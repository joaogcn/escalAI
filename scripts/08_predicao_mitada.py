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
    Gera dicas de mitada usando uma abordagem híbrida: treina o modelo com dados
    históricos, mas filtra e apresenta os jogadores com base no mercado atual.
    """
    print('--- INICIANDO: Geração de Dicas de Mitada (v7 - Híbrido) ---')

    # --- 1. Carga de Dados ---
    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}")
        return False
    df_historico = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    print(f"  - DataFrame histórico carregado. Shape: {df_historico.shape}")

    # --- 2. Buscar Dados do Mercado Atual ---
    try:
        atletas_mercado = get_current_season_players()
        if not atletas_mercado:
            print("  - AVISO: Não foi possível obter dados do mercado. Abortando.")
            return False
        df_mercado = pd.DataFrame(atletas_mercado)
        # Garantir que apenas jogadores prováveis sejam considerados
        df_mercado = df_mercado[df_mercado['status_id'] == 7].copy()
        print(f"  - Dados do mercado carregados. Jogadores prováveis: {df_mercado.shape[0]}")
    except Exception as e:
        print(f"  - ERRO ao buscar dados do mercado: {e}. Abortando.")
        return False

    # --- 3. Preparar Dados para o Modelo ---
    # Pegar a última partida registrada de CADA jogador no histórico
    df_latest_historico = df_historico.loc[df_historico.groupby('atleta_id')['rodada_id'].idxmax()]

    # Filtrar o histórico para conter apenas jogadores que estão no mercado atual
    jogadores_mercado_ids = df_mercado['atleta_id'].unique()
    df_model_data = df_latest_historico[df_latest_historico['atleta_id'].isin(jogadores_mercado_ids)].copy()
    print(f"  - Jogadores do mercado encontrados no histórico: {df_model_data.shape[0]}")

    if df_model_data.empty:
        print("  - AVISO: Nenhum jogador do mercado atual possui dados históricos para previsão.")
        return False

    # --- 4. Feature Engineering e Treinamento ---
    features = [
        'preco_num', 'variacao_num', 'media_num', 'jogos_num', 'A', 'DS', 'FC', 
        'FD', 'FF', 'FS', 'FT', 'G', 'I', 'PI', 'PP', 'CA', 'DE', 'GS', 
        'PC', 'SG', 'GC', 'CV', 'PS', 'DP', 'V'
    ]
    for col in features:
        if col not in df_model_data.columns:
            df_model_data[col] = 0
    df_model_data[features] = df_model_data[features].fillna(0)

    X = df_model_data[features]
    y = df_model_data['pontos_num']

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    print("  - Modelo treinado com dados históricos de jogadores do mercado atual.")

    # --- 5. Predição e Junção com Dados de Mercado ---
    df_model_data['pontuacao_prevista'] = model.predict(X)
    
    # Usar os dados de mercado como base para as informações atuais
    df_predict = df_mercado[['atleta_id', 'apelido', 'clube.nome', 'posicao_id']].copy()
    df_predict = df_predict.merge(df_model_data[['atleta_id', 'pontuacao_prevista']], on='atleta_id', how='left')
    df_predict['pontuacao_prevista'] = df_predict['pontuacao_prevista'].fillna(0) # Preenche com 0 se não houver previsão
    print("  - Predições geradas e unidas com os dados de mercado atuais.")

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