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
    Treina um modelo de ML e recomenda os melhores jogadores da temporada atual.
    """
    print('--- INICIANDO: Geração de Dicas de Mitada (v6 - Foco na Temporada) ---')

    # --- 1. Carga e Preparação dos Dados ---
    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}")
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    print(f"  - DataFrame histórico carregado. Shape: {df.shape}")

    # --- 2. Filtrar para a Temporada Atual ---
    ano_atual = df['ano'].max()
    df_temporada = df[df['ano'] == ano_atual].copy()
    print(f"  - Filtrado para a temporada atual ({ano_atual}). Shape: {df_temporada.shape}")

    if df_temporada.empty:
        print("  - AVISO: Nenhum dado encontrado para a temporada atual. Abortando.")
        return False

    # --- 3. Feature Engineering ---
    features = [
        'preco_num', 'variacao_num', 'media_num', 'jogos_num', 'A', 'DS', 'FC', 
        'FD', 'FF', 'FS', 'FT', 'G', 'I', 'PI', 'PP', 'CA', 'DE', 'GS', 
        'PC', 'SG', 'GC', 'CV', 'PS', 'DP', 'V'
    ]
    for col in features:
        if col not in df_temporada.columns:
            df_temporada[col] = 0

    df_temporada[features] = df_temporada[features].fillna(0)

    # Usar a última rodada de cada jogador na temporada como feature
    df_latest = df_temporada.loc[df_temporada.groupby('atleta_id')['rodada_id'].idxmax()]
    df_model = df_latest.copy()
    print(f"  - Features criadas. Shape do DataFrame de modelo: {df_model.shape}")

    # --- 4. Treinamento do Modelo ---
    X = df_model[features].fillna(0)
    y = df_model['pontos_num']

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    print("  - Modelo RandomForestRegressor treinado.")

    # --- 5. Predição para jogadores da temporada ---
    df_predict = df_model[['atleta_id', 'apelido', 'clube.nome', 'posicao_id']].copy()
    df_predict['pontuacao_prevista'] = model.predict(X)
    print("  - Predições de pontuação geradas.")

    # --- 6. Recomendação Final ---
    recomendacoes = {}
    posicoes = {
        "Goleiro": "gol", "Lateral": "lat", "Zagueiro": "zag",
        "Meia": "mei", "Atacante": "ata", "Técnico": "tec"
    }

    for pos_nome, pos_id in posicoes.items():
        df_pos = df_predict[df_predict['posicao_id'] == pos_id]
        if not df_pos.empty:
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