import pandas as pd
import os
import sys
import json
from sklearn.ensemble import RandomForestRegressor
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, VISUALIZATION_DATA_PATH

FEATURES = [
    'preco_num', 'variacao_num', 'media_num', 'jogos_num', 'A', 'DS', 'FC', 
    'FD', 'FF', 'FS', 'FT', 'G', 'I', 'PI', 'PP', 'CA', 'DE', 'GS', 
    'PC', 'SG', 'GC', 'CV', 'PS', 'DP', 'V'
]
BACKTEST_ROUNDS = 3

def train_and_predict_for_round(rodada_alvo, df_historico_completo):
    """
    Treina um modelo com dados até a rodada anterior à 'rodada_alvo'
    e gera previsões para ela.
    """
    print(f"\n--- Processando Backtest para Rodada {rodada_alvo} ---")

    df_mercado_simulado = df_historico_completo[df_historico_completo['rodada_id'] == rodada_alvo].copy()
    if df_mercado_simulado.empty:
        print(f"  - AVISO: Sem dados para a rodada {rodada_alvo}. Pulando.")
        return None
    
    jogadores_mercado_ids = df_mercado_simulado['atleta_id'].unique()
    print(f"  - Jogadores no 'mercado' da rodada {rodada_alvo}: {len(jogadores_mercado_ids)}")

    df_treinamento = df_historico_completo[df_historico_completo['rodada_id'] < rodada_alvo].copy()
    
    df_latest_historico = df_treinamento.loc[df_treinamento.groupby('atleta_id')['rodada_id'].idxmax()]
    
    df_model_data = df_latest_historico[df_latest_historico['atleta_id'].isin(jogadores_mercado_ids)].copy()
    print(f"  - Jogadores do 'mercado' encontrados no histórico de treinamento: {df_model_data.shape[0]}")

    if df_model_data.empty:
        print("  - AVISO: Nenhum jogador do mercado possui dados históricos para esta rodada.")
        return None

    for col in FEATURES:
        if col not in df_model_data.columns:
            df_model_data[col] = 0
    df_model_data[FEATURES] = df_model_data[FEATURES].fillna(0)

    X = df_model_data[FEATURES]
    y = df_model_data['pontos_num']

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    print("  - Modelo treinado com dados até a rodada anterior.")

    df_model_data['pontuacao_prevista'] = model.predict(X)
    
    df_predict = df_mercado_simulado[['atleta_id', 'apelido', 'clube.nome', 'posicao_id', 'pontuacao']].copy()
    df_predict = df_predict.merge(df_model_data[['atleta_id', 'pontuacao_prevista']], on='atleta_id', how='left')
    df_predict['pontuacao_prevista'] = df_predict['pontuacao_prevista'].fillna(0)
    
    df_predict = df_predict.rename(columns={'pontuacao': 'pontuacao_real'})
    
    print("  - Predições geradas e unidas com os resultados reais da rodada.")
    return df_predict

def run():
    """
    Orquestra o processo de backtest para as últimas N rodadas.
    """
    print("==================================================")
    print("INICIANDO SCRIPT DE BACKTEST DO MODELO...")
    print("==================================================")

    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}")
        return False
    df_historico = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    print(f"  - Dados históricos carregados. Shape: {df_historico.shape}")

    rodadas_disponiveis = sorted(df_historico['rodada_id'].unique(), reverse=True)
    rodada_atual = rodadas_disponiveis[0] if rodadas_disponiveis else 0
    rodadas_para_backtest = [r for r in rodadas_disponiveis if r < rodada_atual][:BACKTEST_ROUNDS]

    if not rodadas_para_backtest:
        print("AVISO: Não há rodadas anteriores suficientes para o backtest.")
        return True

    print(f"  - Rodadas a serem testadas: {rodadas_para_backtest}")

    for rodada in rodadas_para_backtest:
        resultado_rodada = train_and_predict_for_round(rodada, df_historico)
        
        if resultado_rodada is not None:
            recomendacoes = []
            posicoes = resultado_rodada['posicao_id'].unique()
            for pos in posicoes:
                df_pos = resultado_rodada[resultado_rodada['posicao_id'] == pos]
                if not df_pos.empty:
                    melhor_jogador = df_pos.sort_values(by='pontuacao_prevista', ascending=False).iloc[0]
                    recomendacoes.append(melhor_jogador.to_dict())
            
            output_data = {
                'rodada_id': int(rodada),
                'recomendacoes': recomendacoes
            }
            
            output_filename = os.path.join(VISUALIZATION_DATA_PATH, f'backtest_rodada_{rodada}.json')
            os.makedirs(VISUALIZATION_DATA_PATH, exist_ok=True)
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)
            
            print(f"  - Resultado do backtest para a rodada {rodada} salvo em {output_filename}")

    print("\n==================================================")
    print("SCRIPT DE BACKTEST CONCLUÍDO COM SUCESSO!")
    print("==================================================")
    return True

if __name__ == "__main__":
    run()
