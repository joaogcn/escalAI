import pandas as pd
import os
import sys
import json
import re
from sklearn.ensemble import RandomForestRegressor
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, VISUALIZATION_DATA_PATH
from src.dados import get_current_season_players, get_confrontos_rodada

def run():
    """
    Treina um modelo de ML simples e aplica um filtro inteligente de confronto 
    para gerar as dicas de "mitada" para a rodada.
    """
    print('--- INICIANDO: Geração de Dicas de Mitada (v4 - Final) ---')

    # --- 1. Carga e Preparação dos Dados Históricos ---
    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}")
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    df = df.sort_values(by=['atleta_id', 'ano', 'rodada_id'])
    print(f"  - DataFrame histórico carregado. Shape: {df.shape}")

    # --- 2. Feature Engineering (Sem Contexto de Confronto) ---
    features = [
        'preco_num', 'variacao_num', 'media_num', 'jogos_num', 'A', 'DS', 'FC', 
        'FD', 'FF', 'FS', 'FT', 'G', 'I', 'PI', 'PP', 'CA', 'DE', 'GS', 
        'PC', 'SG', 'GC', 'CV', 'PS', 'DP', 'V'
    ]
    for col in features:
        if col not in df.columns:
            df[col] = 0

    df[features] = df[features].fillna(0)

    lagged_features = df.groupby('atleta_id')[features].shift(1)
    lagged_features.columns = [f'{col}_lag1' for col in features]
    
    df_model = pd.concat([df[['atleta_id', 'posicao_id', 'pontos_num']], lagged_features], axis=1)
    df_model = df_model.dropna(subset=['pontos_num'] + list(lagged_features.columns))
    print(f"  - Features criadas. Shape do DataFrame de modelo: {df_model.shape}")

    # --- 3. Treinamento do Modelo Único ---
    X = df_model[lagged_features.columns]
    y = df_model['pontos_num']

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    print("  - Modelo RandomForestRegressor treinado.")

    # --- 4. Predição Base para a Rodada Atual ---
    print("  - Gerando previsões base para a rodada atual...")
    atletas_mercado = get_current_season_players()
    if not atletas_mercado:
        print("  - AVISO: Não foi possível obter dados do mercado.")
        return False
    df_mercado = pd.DataFrame(atletas_mercado)
    provaveis_ids = set(df_mercado[df_mercado['status_id'] == 7]['atleta_id'])
    
    df_latest = df[df['atleta_id'].isin(provaveis_ids)].copy()
    if df_latest.empty:
        print("  - AVISO: Nenhum jogador provável com histórico encontrado.")
        return False
    df_latest = df_latest.loc[df_latest.groupby('atleta_id')['rodada_id'].idxmax()]

    X_pred = df_latest[features].fillna(0)
    X_pred.columns = [f'{col}_lag1' for col in features]
    X_pred = X_pred[lagged_features.columns]

    df_predict = df_latest[['atleta_id', 'apelido', 'clube.nome', 'clube_id', 'posicao_id', 'media_num']].copy()
    df_predict['pontuacao_prevista'] = model.predict(X_pred)
    print("  - Predições de pontuação geradas.")

    # --- 5. Filtro Inteligente de Confronto ---
    print("  - Aplicando filtro inteligente de confronto...")
    confrontos = get_confrontos_rodada()
    if not confrontos:
        print("  - AVISO: Não foi possível obter confrontos da rodada. O filtro inteligente não será aplicado.")
        df_predict['pontuacao_ajustada'] = df_predict['pontuacao_prevista']
    else:
        # Criar mapeamento de nome de time para ID
        club_name_to_id = df_mercado.drop_duplicates('clube_id').set_index('clube.nome')['clube_id'].to_dict()

        def get_matchup_info(clube_id):
            confronto_str = confrontos.get(clube_id, '')
            match = re.search(r'vs (.*) \((.*)\)', confronto_str)
            if not match:
                return None, None, None
            
            opponent_name = match.group(1)
            local = match.group(2)
            opponent_id = club_name_to_id.get(opponent_name)
            casa = 1 if local == 'Casa' else 0
            return opponent_id, casa, opponent_name

        df_predict[['adversario_id', 'casa', 'adversario_nome']] = df_predict['clube_id'].apply(lambda x: pd.Series(get_matchup_info(x)))

        ano_atual = df['ano'].max()
        df_ano_atual = df[df['ano'] == ano_atual]
        team_strength_season = df_ano_atual.groupby('clube_id')['pontos_num'].mean().to_dict()
        avg_strength_season = np.mean(list(team_strength_season.values()))

        df_predict['forca_adversario'] = df_predict['adversario_id'].map(team_strength_season).fillna(avg_strength_season)

        bonus = pd.Series(1.0, index=df_predict.index)
        cond_def = (df_predict['posicao_id'].isin(['gol', 'lat', 'zag'])) & (df_predict['casa'] == 1) & (df_predict['forca_adversario'] < avg_strength_season)
        bonus[cond_def] *= 1.2 # Bônus mais conservador
        cond_ata = (df_predict['posicao_id'].isin(['mei', 'ata'])) & (df_predict['forca_adversario'] < avg_strength_season)
        bonus[cond_ata] *= 1.1
        df_predict['pontuacao_ajustada'] = df_predict['pontuacao_prevista'] * bonus
        print("  - Filtro inteligente de confronto aplicado.")

    # --- 6. Recomendação Final ---
    recomendacoes = {}
    market_positions = df_mercado[['atleta_id', 'posicao_id']].rename(columns={'posicao_id': 'posicao_id_atual'})
    df_predict = pd.merge(df_predict, market_positions, on='atleta_id', how='left')
    df_predict['posicao_id'] = df_predict['posicao_id_atual'].fillna(df_predict['posicao_id'])

    # Lógica para Técnicos
    df_tec = df_mercado[(df_mercado['posicao_id'] == 'tec') & (df_mercado['atleta_id'].isin(provaveis_ids))].copy()
    if not confrontos or df_tec.empty:
        best_coach = df_predict[df_predict['posicao_id'] == 'tec'].sort_values(by='media_num', ascending=False).head(1)
        if not best_coach.empty:
            recomendacoes['Técnico'] = best_coach[['apelido', 'clube.nome']].iloc[0].to_dict()
    else:
        df_tec[['adversario_id', 'casa', 'adversario_nome']] = df_tec['clube_id'].apply(lambda x: pd.Series(get_matchup_info(x)))
        df_tec['forca_time'] = df_tec['clube_id'].map(team_strength_season).fillna(avg_strength_season)
        df_tec['forca_adversario'] = df_tec['adversario_id'].map(team_strength_season).fillna(avg_strength_season)
        df_tec['matchup_score'] = (df_tec['forca_time'] / df_tec['forca_adversario']) * np.where(df_tec['casa'] == 1, 1.2, 0.8)
        best_coach = df_tec.sort_values(by='matchup_score', ascending=False).iloc[0]
        recomendacoes['Técnico'] = {'apelido': best_coach['apelido'], 'clube.nome': best_coach['clube.nome']}

    # Lógica para Jogadores
    posicoes_jogadores = {'Goleiro': 'gol', 'Lateral': 'lat', 'Zagueiro': 'zag', 'Meia': 'mei', 'Atacante': 'ata'}
    for pos_nome, pos_id in posicoes_jogadores.items():
        best_player = df_predict[df_predict['posicao_id'] == pos_id].sort_values(by='pontuacao_ajustada', ascending=False).head(1)
        if not best_player.empty:
            recomendacoes[pos_nome] = best_player[['apelido', 'clube.nome']].iloc[0].to_dict()

    output_path = os.path.join(VISUALIZATION_DATA_PATH, 'recomendacao_mitada.json')
    os.makedirs(VISUALIZATION_DATA_PATH, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recomendacoes, f, ensure_ascii=False, indent=4)

    print(f"  - Recomendações salvas em: {output_path}")
    print('--- SUCESSO: Geração de Dicas de Mitada Concluída ---')
    return True

if __name__ == "__main__":
    run()