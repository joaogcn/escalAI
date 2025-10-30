import pandas as pd
import os
import sys
import json
from sklearn.ensemble import RandomForestRegressor
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, VISUALIZATION_DATA_PATH
from src.dados import get_current_season_players

def run():
    """
    Treina um modelo de ML simples para prever a pontuação dos jogadores, 
    validando status e posição com a API antes de recomendar.
    """
    print('--- INICIANDO: Geração de Dicas de Mitada (Versão Simplificada) ---')

    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}")
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    df = df.sort_values(by=['atleta_id', 'ano', 'rodada_id'])
    print(f"  - DataFrame histórico carregado. Shape: {df.shape}")

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
    
    df_model = pd.concat([df[['atleta_id', 'rodada_id', 'ano', 'posicao_id', 'pontos_num', 'apelido', 'clube.nome']], lagged_features], axis=1)
    df_model = df_model.dropna(subset=['pontos_num'] + list(lagged_features.columns))
    print(f"  - Features criadas. Shape do DataFrame de modelo: {df_model.shape}")

    X = df_model[lagged_features.columns]
    y = df_model['pontos_num']

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    print("  - Modelo RandomForestRegressor treinado.")

    print("  - Gerando previsões para a rodada atual...")
    
    atletas_mercado = get_current_season_players()
    if not atletas_mercado:
        print("  - AVISO: Não foi possível obter dados do mercado. Recomendações não serão geradas.")
        return False
    df_mercado = pd.DataFrame(atletas_mercado)
    provaveis_ids = set(df_mercado[df_mercado['status_id'] == 7]['atleta_id'])
    print(f"  - Encontrados {len(provaveis_ids)} jogadores prováveis no mercado.")

    df_latest = df[df['atleta_id'].isin(provaveis_ids)].copy()
    df_latest = df_latest.loc[df_latest.groupby('atleta_id')['rodada_id'].idxmax()]

    if df_latest.empty:
        print("  - AVISO: Nenhum jogador provável com histórico encontrado para fazer predições.")
        return False

    X_pred = df_latest[features].fillna(0)
    X_pred.columns = [f'{col}_lag1' for col in features]
    X_pred = X_pred[lagged_features.columns] 

    df_predict = df_latest.copy()
    df_predict['pontuacao_prevista'] = model.predict(X_pred)
    print("  - Predições de pontuação geradas.")

    market_positions = df_mercado[['atleta_id', 'posicao_id']].rename(columns={'posicao_id': 'posicao_id_atual'})
    df_predict = pd.merge(df_predict, market_positions, on='atleta_id', how='left')
    df_predict['posicao_id'] = df_predict['posicao_id_atual'].fillna(df_predict['posicao_id'])
    print("  - Posições dos jogadores validadas com a API.")

    recomendacoes = {}
    posicoes = {'Goleiro': 'gol', 'Lateral': 'lat', 'Zagueiro': 'zag', 'Meia': 'mei', 'Atacante': 'ata', 'Técnico': 'tec'}

    for pos_nome, pos_id in posicoes.items():
        if pos_id == 'tec':
            best_player = df_predict[df_predict['posicao_id'] == pos_id].sort_values(by='media_num', ascending=False).head(1)
        else:
            best_player = df_predict[df_predict['posicao_id'] == pos_id].sort_values(by='pontuacao_prevista', ascending=False).head(1)
        
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