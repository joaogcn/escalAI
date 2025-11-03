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
    Treina um modelo de ML simples e usa a predição de maior pontuação para
    recomendar os jogadores (sem filtro de confronto, mais robusto).
    """
    print('--- INICIANDO: Geração de Dicas de Mitada (v5 - Robusto) ---')

    # --- 1. Carga e Preparação dos Dados Históricos ---
    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}")
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    df = df.sort_values(by=['atleta_id', 'ano', 'rodada_id'])
    print(f"  - DataFrame histórico carregado. Shape: {df.shape}")

    # --- 2. Feature Engineering ---
    features = [
        'preco_num', 'variacao_num', 'media_num', 'jogos_num', 'A', 'DS', 'FC', 
        'FD', 'FF', 'FS', 'FT', 'G', 'I', 'PI', 'PP', 'CA', 'DE', 'GS', 
        'PC', 'SG', 'GC', 'CV', 'PS', 'DP', 'V'
    ]
    for col in features:
        if col not in df.columns:
            df[col] = 0

    df[features] = df[features].fillna(0)

    # Usar a última rodada de cada jogador como feature
    df_latest = df.loc[df.groupby('atleta_id')['rodada_id'].idxmax()]
    
    df_model = df_latest.copy()
    print(f"  - Features criadas. Shape do DataFrame de modelo: {df_model.shape}")

    # --- 3. Treinamento do Modelo ---
    X = df_model[features].fillna(0)
    y = df_model['pontos_num']

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    print("  - Modelo RandomForestRegressor treinado.")

    # --- 4. Predição para todos os jogadores com dados ---
    df_predict = df_model[['atleta_id', 'apelido', 'clube.nome', 'posicao_id']].copy()
    df_predict['pontuacao_prevista'] = model.predict(X)
    print("  - Predições de pontuação geradas para todos os jogadores.")

    # --- 5. Recomendação Final (baseado na maior pontuação prevista) ---
    recomendacoes = {}
    
    # Mapeamento de posições
    posicoes = {
        "Goleiro": "gol", "Lateral": "lat", "Zagueiro": "zag",
        "Meia": "mei", "Atacante": "ata", "Técnico": "tec"
    }

    for pos_nome, pos_id in posicoes.items():
        # Filtra jogadores da posição
        df_pos = df_predict[df_predict['posicao_id'] == pos_id]
        
        if not df_pos.empty:
            # Ordena pela pontuação prevista e pega o melhor
            best_player = df_pos.sort_values(by='pontuacao_prevista', ascending=False).iloc[0]
            recomendacoes[pos_nome] = best_player[['apelido', 'clube.nome']].to_dict()

    output_path = os.path.join(VISUALIZATION_DATA_PATH, 'recomendacao_mitada.json')
    os.makedirs(VISUALIZATION_DATA_PATH, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recomendacoes, f, ensure_ascii=False, indent=4)

    print(f"  - Recomendações salvas em: {output_path}")
    print('--- SUCESSO: Geração de Dicas de Mitada Concluída ---')
    return True

if __name__ == "__main__":
    run()