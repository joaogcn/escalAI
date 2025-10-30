
import pandas as pd
import os
import sys
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, VISUALIZATION_DATA_PATH
from src.dados import get_current_season_players

def run():
    """
    Treina um modelo de RandomForest para prever a pontuação dos jogadores e gera recomendações.
    """
    print('--- INICIANDO: Geração de Dicas de Mitada com ML ---')

    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}")
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    print(f"  - DataFrame carregado. Shape inicial: {df.shape}")

    df = df.sort_values(by=['atleta_id', 'ano', 'rodada_id'])
    
    features = ['preco_num', 'variacao_num', 'media_num', 'jogos_num', 
                'A', 'DS', 'FC', 'FD', 'FF', 'FS', 'FT', 'G', 'I', 'PI', 'PP', 
                'CA', 'DE', 'GS', 'PC', 'SG', 'GC', 'CV', 'PS', 'DP', 'V']
    
    df[features] = df[features].fillna(0)

    lagged_features = df.groupby('atleta_id')[features].shift(1)
    lagged_features.columns = [f'{col}_lag1' for col in features]
    
    df_model = pd.concat([df[['atleta_id', 'rodada_id', 'ano', 'posicao_id', 'pontos_num', 'apelido', 'clube.nome']], lagged_features], axis=1)
    df_model = df_model.dropna(subset=['pontos_num'] + list(lagged_features.columns))
    
    print(f"  - DataFrame para o modelo criado. Shape: {df_model.shape}")

    X = df_model[lagged_features.columns]
    y = df_model['pontos_num']

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    print("  - Modelo RandomForestRegressor treinado.")

    df_latest = df.loc[df.groupby('atleta_id')['rodada_id'].idxmax()]
    
    atletas_mercado = get_current_season_players()
    if not atletas_mercado:
        print("  - AVISO: Não foi possível obter dados do mercado de atletas. As predições não serão geradas.")
        return False

    df_mercado = pd.DataFrame(atletas_mercado)
    provaveis_ids = set(df_mercado[df_mercado['status_id'] == 7]['atleta_id'])
    print(f"  - Encontrados {len(provaveis_ids)} jogadores prováveis no mercado.")

    df_predict = df_latest[df_latest['atleta_id'].isin(provaveis_ids)].copy()
    print(f"  - DataFrame para predição criado. Shape: {df_predict.shape}")

    X_pred = df_predict[features].fillna(0)
    X_pred.columns = [f'{col}_lag1' for col in features]

    df_predict['pontuacao_prevista'] = model.predict(X_pred)
    print("  - Predições de pontuação geradas.")

    recomendacoes = {}
    posicoes = {'gol': 'Goleiro', 'lat': 'Lateral', 'zag': 'Zagueiro', 'mei': 'Meia', 'ata': 'Atacante', 'tec': 'Técnico'}

    for pos_id, pos_nome in posicoes.items():
        best_player = df_predict[df_predict['posicao_id'] == pos_id].sort_values(by='pontuacao_prevista', ascending=False).head(1)
        if not best_player.empty:
            recomendacoes[pos_nome] = best_player[['apelido', 'clube.nome', 'pontuacao_prevista']].to_dict(orient='records')[0]
            print(f"    - Melhor jogador para '{pos_nome}': {recomendacoes[pos_nome]['apelido']}")

    output_path = os.path.join(VISUALIZATION_DATA_PATH, 'recomendacao_mitada.json')
    os.makedirs(VISUALIZATION_DATA_PATH, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recomendacoes, f, ensure_ascii=False, indent=4)

    print(f"  - Recomendações de mitada salvas em: {output_path}")
    print('--- SUCESSO: Geração de Dicas de Mitada Concluída ---')
    return True

if __name__ == "__main__":
    run()
