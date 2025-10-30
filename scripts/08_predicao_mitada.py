
import pandas as pd
import os
import sys
import json
from sklearn.ensemble import GradientBoostingRegressor
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

    # Feature Engineering
    df = df.sort_values(by=['atleta_id', 'ano', 'rodada_id'])
    
    scout_features = ['A', 'DS', 'FC', 'FD', 'FF', 'FS', 'FT', 'G', 'I', 'PI', 'PP', 
                      'CA', 'DE', 'GS', 'PC', 'SG', 'GC', 'CV', 'PS', 'DP', 'V']
    player_stats_features = ['preco_num', 'variacao_num', 'media_num', 'jogos_num']

    features = player_stats_features + scout_features
    df[features] = df[features].fillna(0)

    # Calculate rolling average for scout features
    rolling_scouts = df.groupby('atleta_id')[scout_features].rolling(window=3, min_periods=1).mean()
    rolling_scouts = rolling_scouts.reset_index(level=0, drop=True)
    
    # Lag all features
    lagged_rolling_scouts = rolling_scouts.groupby('atleta_id').shift(1)
    lagged_player_stats = df.groupby('atleta_id')[player_stats_features].shift(1)

    # Rename columns
    lagged_rolling_scouts.columns = [f'{col}_rolling3_lag1' for col in scout_features]
    lagged_player_stats.columns = [f'{col}_lag1' for col in player_stats_features]

    # Combine features
    lagged_features = pd.concat([lagged_player_stats, lagged_rolling_scouts], axis=1)
    
    df_model = pd.concat([df[['atleta_id', 'rodada_id', 'ano', 'posicao_id', 'pontos_num', 'apelido', 'clube.nome']], lagged_features], axis=1)
    df_model = df_model.dropna(subset=['pontos_num'] + list(lagged_features.columns))
    
    print(f"  - DataFrame para o modelo criado. Shape: {df_model.shape}")

    X = df_model[lagged_features.columns]
    y = df_model['pontos_num']

    # Train model to predict the 90th percentile (high potential scores)
    model = GradientBoostingRegressor(loss='quantile', alpha=0.9, n_estimators=250, max_depth=3, random_state=42)
    model.fit(X, y)
    print("  - Modelo GradientBoostingRegressor (Quantile) treinado.")

    # Prepare data for prediction
    atletas_mercado = get_current_season_players()
    if not atletas_mercado:
        print("  - AVISO: Não foi possível obter dados do mercado de atletas. As predições não serão geradas.")
        return False

    df_mercado = pd.DataFrame(atletas_mercado)
    provaveis_ids = set(df_mercado[df_mercado['status_id'] == 7]['atleta_id'])
    print(f"  - Encontrados {len(provaveis_ids)} jogadores prováveis no mercado.")

    # Get all data for probable players
    df_provaveis = df[df['atleta_id'].isin(provaveis_ids)].copy()

    # Get the latest stats for each player
    latest_player_data = df_provaveis.loc[df_provaveis.groupby('atleta_id')['rodada_id'].idxmax()]
    latest_player_data = latest_player_data.set_index('atleta_id')

    # Calculate rolling average of scouts for each probable player
    rolling_scouts_pred = df_provaveis.groupby('atleta_id')[scout_features].rolling(window=3, min_periods=1).mean()
    
    # Get the last rolling average for each player
    last_rolling_scouts = rolling_scouts_pred.groupby('atleta_id').last()

    # Prepare the final prediction dataframe
    df_predict = latest_player_data.copy()
    
    # Create the feature matrix X_pred
    X_pred_player_stats = df_predict[player_stats_features]
    X_pred_scouts = last_rolling_scouts.reindex(df_predict.index).fillna(0)

    # Rename columns to match model's expectation
    X_pred_player_stats.columns = [f'{col}_lag1' for col in player_stats_features]
    X_pred_scouts.columns = [f'{col}_rolling3_lag1' for col in scout_features]

    X_pred = pd.concat([X_pred_player_stats, X_pred_scouts], axis=1)
    
    # Ensure column order is the same as in training
    X_pred = X_pred[df_model.drop(columns=['atleta_id', 'rodada_id', 'ano', 'posicao_id', 'pontos_num', 'apelido', 'clube.nome']).columns]

    df_predict['pontuacao_prevista'] = model.predict(X_pred)
    print("  - Predições de pontuação geradas.")
    
    df_predict = df_predict.reset_index()

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
