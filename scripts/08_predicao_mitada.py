import pandas as pd
import os
import sys
import json
from sklearn.ensemble import GradientBoostingRegressor
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, VISUALIZATION_DATA_PATH
from src.dados import get_current_season_players, get_partidas_rodada

def run():
    """
    Treina modelos de ML (sem contexto de confronto) e depois aplica um filtro 
    inteligente com base nos confrontos da rodada atual para gerar as dicas.
    """
    print('--- INICIANDO: Geração de Dicas de Mitada com ML (v3 - Correção) ---')

    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}")
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    df = df.sort_values(by=['atleta_id', 'ano', 'rodada_id'])
    print(f"  - DataFrame histórico carregado. Shape inicial: {df.shape}")

    gk_scout_features = ['SG', 'DE', 'GS', 'DP'] 
    field_scout_features = ['G', 'A', 'DS', 'FC', 'FD', 'FF', 'FS', 'FT'] 
    all_scouts_needed = list(set(gk_scout_features + field_scout_features))
    for col in all_scouts_needed:
        if col not in df.columns:
            df[col] = 0
            print(f"  - AVISO: Coluna de scout ''{col}'' não encontrada. Adicionada com valor 0.")

    def create_features_sem_contexto(data, scout_features, other_features):
        data.loc[:, scout_features + other_features] = data[scout_features + other_features].fillna(0)
        
        rolling_scouts = data.groupby('atleta_id')[scout_features].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        lagged_rolling_scouts = rolling_scouts.groupby('atleta_id').shift(1)
        lagged_rolling_scouts.columns = [f'{col}_rolling3_lag1' for col in scout_features]

        lagged_other_features = data.groupby('atleta_id')[other_features].shift(1)
        lagged_other_features.columns = [f'{col}_lag1' for col in other_features]

        lagged_features = pd.concat([lagged_other_features, lagged_rolling_scouts], axis=1)
        
        df_model_features = pd.concat([data[['atleta_id', 'rodada_id', 'ano', 'posicao_id', 'pontos_num']], lagged_features], axis=1)
        return df_model_features.dropna(subset=['pontos_num'] + list(lagged_features.columns))

    other_features = ['preco_num', 'media_num']
    df_model_gk = create_features_sem_contexto(df[df['posicao_id'] == 'gol'].copy(), gk_scout_features, other_features)
    df_model_field = create_features_sem_contexto(df[df['posicao_id'].isin(['lat', 'zag', 'mei', 'ata'])].copy(), field_scout_features, other_features)
    print(f"  - Features (sem contexto) criadas. Shape Goleiros: {df_model_gk.shape}, Shape Linha: {df_model_field.shape}")

    print("  - Treinando modelos (sem contexto de confronto)...")
    X_gk = df_model_gk.drop(columns=['atleta_id', 'rodada_id', 'ano', 'posicao_id', 'pontos_num'])
    y_gk = df_model_gk['pontos_num']
    model_gk = GradientBoostingRegressor(loss='quantile', alpha=0.9, n_estimators=100, max_depth=3, random_state=42)
    model_gk.fit(X_gk, y_gk)
    print("    - Modelo para Goleiros treinado.")

    X_field = df_model_field.drop(columns=['atleta_id', 'rodada_id', 'ano', 'posicao_id', 'pontos_num'])
    y_field = df_model_field['pontos_num']
    model_field = GradientBoostingRegressor(loss='quantile', alpha=0.9, n_estimators=250, max_depth=3, random_state=42)
    model_field.fit(X_field, y_field)
    print("    - Modelo para Jogadores de Linha treinado.")

    print("  - Gerando previsões base (sem contexto)...")
    atletas_mercado = get_current_season_players()
    if not atletas_mercado:
        print("  - AVISO: Não foi possível obter dados do mercado.")
        return False
    df_mercado = pd.DataFrame(atletas_mercado)
    provaveis_ids = set(df_mercado[df_mercado['status_id'] == 7]['atleta_id'])
    df_provaveis = df[df['atleta_id'].isin(provaveis_ids)].copy()

    # DEBUG: Verificar colunas
    print("Colunas em df_provaveis:", df_provaveis.columns)

    def create_prediction_features(data, scout_features, other_features):
        latest = data.loc[data.groupby('atleta_id')['rodada_id'].idxmax()].set_index('atleta_id')
        rolling = data.groupby('atleta_id')[scout_features].rolling(window=3, min_periods=1).mean().groupby('atleta_id').last()
        stats_lag1 = latest[other_features]
        scouts_rolling3_lag1 = rolling.reindex(latest.index).fillna(0)
        stats_lag1.columns = [f'{col}_lag1' for col in other_features]
        scouts_rolling3_lag1.columns = [f'{col}_rolling3_lag1' for col in scout_features]
        return pd.concat([stats_lag1, scouts_rolling3_lag1], axis=1), latest.reset_index()

    df_provaveis_field = df_provaveis[df_provaveis['posicao_id'].isin(['lat', 'zag', 'mei', 'ata'])]
    X_pred_field, df_predict_field = create_prediction_features(df_provaveis_field, field_scout_features, other_features)

    df_provaveis_gk = df_provaveis[df_provaveis['posicao_id'] == 'gol']
    X_pred_gk, df_predict_gk = create_prediction_features(df_provaveis_gk, gk_scout_features, other_features)

    df_predict_field['pontuacao_prevista'] = model_field.predict(X_pred_field[X_field.columns])
    df_predict_gk['pontuacao_prevista'] = model_gk.predict(X_pred_gk[X_gk.columns])
    df_predict = pd.concat([df_predict_field, df_predict_gk], ignore_index=True)

    print("  - Aplicando filtro inteligente de confronto...")
    partidas_rodada = get_partidas_rodada()
    if not partidas_rodada:
        print("  - AVISO: Não foi possível obter partidas da rodada. O filtro inteligente não será aplicado.")
        df_predict['pontuacao_ajustada'] = df_predict['pontuacao_prevista']
    else:
        ano_atual = df['ano'].max()
        df_ano_atual = df[df['ano'] == ano_atual]
        team_strength_season = df_ano_atual.groupby('clube_id')['pontos_num'].mean().to_dict()
        avg_strength_season = np.mean(list(team_strength_season.values()))

        matchup_info = {p['clube_casa_id']: {'adversario_id': p['clube_visitante_id'], 'casa': 1} for p in partidas_rodada}
        matchup_info.update({p['clube_visitante_id']: {'adversario_id': p['clube_casa_id'], 'casa': 0} for p in partidas_rodada})

        df_predict['adversario_id'] = df_predict['clube_id'].map(lambda x: matchup_info.get(x, {}).get('adversario_id'))
        df_predict['casa'] = df_predict['clube_id'].map(lambda x: matchup_info.get(x, {}).get('casa', 0))
        df_predict['forca_adversario'] = df_predict['adversario_id'].map(team_strength_season).fillna(avg_strength_season)

        bonus = pd.Series(1.0, index=df_predict.index)
        cond_def = (df_predict['posicao_id'].isin(['gol', 'lat', 'zag'])) & (df_predict['casa'] == 1) & (df_predict['forca_adversario'] < avg_strength_season)
        bonus[cond_def] *= 1.4
        cond_ata = (df_predict['posicao_id'].isin(['mei', 'ata'])) & (df_predict['forca_adversario'] < avg_strength_season)
        bonus[cond_ata] *= 1.2
        df_predict['pontuacao_ajustada'] = df_predict['pontuacao_prevista'] * bonus
        print("  - Filtro inteligente de confronto aplicado.")

    recomendacoes = {}
    df_tec = df_mercado[(df_mercado['posicao_id'] == 'tec') & (df_mercado['atleta_id'].isin(provaveis_ids))].copy()
    if partidas_rodada and not df_tec.empty:
        df_tec['adversario_id'] = df_tec['clube_id'].map(lambda x: matchup_info.get(x, {}).get('adversario_id'))
        df_tec['casa'] = df_tec['clube_id'].map(lambda x: matchup_info.get(x, {}).get('casa', 0))
        df_tec['forca_time'] = df_tec['clube_id'].map(team_strength_season).fillna(avg_strength_season)
        df_tec['forca_adversario'] = df_tec['adversario_id'].map(team_strength_season).fillna(avg_strength_season)
        df_tec['matchup_score'] = (df_tec['forca_time'] / df_tec['forca_adversario']) * np.where(df_tec['casa'] == 1, 1.2, 0.8)
        best_coach = df_tec.sort_values(by='matchup_score', ascending=False).iloc[0]
        club_name = df_mercado.loc[df_mercado['clube_id'] == best_coach['clube_id'], 'clube.nome'].iloc[0]
        recomendacoes['Técnico'] = {'apelido': best_coach['apelido'], 'clube.nome': club_name}

    posicoes_jogadores = {'Goleiro': 'gol', 'Lateral': 'lat', 'Zagueiro': 'zag', 'Meia': 'mei', 'Atacante': 'ata'}
    market_positions = df_mercado[['atleta_id', 'posicao_id']].rename(columns={'posicao_id': 'posicao_id_atual'})
    df_predict = pd.merge(df_predict, market_positions, on='atleta_id', how='left')
    df_predict['posicao_id'] = df_predict['posicao_id_atual'].fillna(df_predict['posicao_id'])

    for pos_nome, pos_id in posicoes_jogadores.items():
        best_player = df_predict[df_predict['posicao_id'] == pos_id].sort_values(by='pontuacao_ajustada', ascending=False).head(1)
        if not best_player.empty:
            recomendacoes[pos_nome] = best_player[['apelido', 'clube.nome']].iloc[0].to_dict()

    output_path = os.path.join(VISUALIZATION_DATA_PATH, 'recomendacao_mitada.json')
    os.makedirs(VISUALIZATION_DATA_PATH, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recomendacoes, f, ensure_ascii=False, indent=4)

    print(f"  - Recomendações de mitada salvas em: {output_path}")
    print('--- SUCESSO: Geração de Dicas de Mitada Concluída ---')
    return True

if __name__ == "__main__":
    run()
