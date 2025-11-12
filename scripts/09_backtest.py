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
TARGET_SCORES = {
    'ata': 10, 'mei': 8, 'lat': 6, 'zag': 6, 'gol': 8, 'tec': 8
}
POSICOES = {
    'Goleiro': 'gol', 'Lateral': 'lat', 'Zagueiro': 'zag', 
    'Meia': 'mei', 'Atacante': 'ata', 'Técnico': 'tec'
}

def get_signal(actual_score, target_score):
    """Retorna um sinal de trânsito com base na pontuação real vs. alvo."""
    if actual_score >= target_score:
        return "Verde"
    elif actual_score >= target_score * 0.7:
        return "Amarelo"
    else:
        return "Vermelho"

def train_and_predict_for_round(rodada_alvo, df_historico_temporada):
    """
    Treina um modelo com dados até a rodada anterior à 'rodada_alvo'
    e gera previsões para ela, dentro de uma mesma temporada.
    """
    print(f"\n--- Processando Backtest para Rodada {rodada_alvo} ---")

    df_mercado_simulado = df_historico_temporada[df_historico_temporada['rodada_id'] == rodada_alvo].copy()
    if df_mercado_simulado.empty:
        print(f"  - AVISO: Sem dados para a rodada {rodada_alvo}. Pulando.")
        return None
    
    jogadores_mercado_ids = df_mercado_simulado['atleta_id'].unique()
    
    df_treinamento = df_historico_temporada[df_historico_temporada['rodada_id'] < rodada_alvo].copy()
    print(f"  - Shape do df_treinamento (rodadas < {rodada_alvo}): {df_treinamento.shape}")
    
    if df_treinamento.empty:
        print(f"  - AVISO: Sem dados de treinamento para rodadas anteriores a {rodada_alvo}. Pulando.")
        return None

    df_latest_historico = df_treinamento.loc[df_treinamento.groupby('atleta_id')['rodada_id'].idxmax()]
    print(f"  - Shape do df_latest_historico (último jogo de cada atleta no treino): {df_latest_historico.shape}")
    
    latest_historico_ids = set(df_latest_historico['atleta_id'].unique())
    mercado_simulado_ids = set(jogadores_mercado_ids)
    common_ids = latest_historico_ids.intersection(mercado_simulado_ids)
    print(f"  - Atletas únicos no histórico de treino: {len(latest_historico_ids)}")
    print(f"  - Atletas únicos no 'mercado' da rodada alvo: {len(mercado_simulado_ids)}")
    print(f"  - Atletas em comum para modelagem: {len(common_ids)}")

    df_model_data = df_latest_historico[df_latest_historico['atleta_id'].isin(jogadores_mercado_ids)].copy()

    if df_model_data.empty:
        print("  - AVISO: Nenhum jogador do 'mercado' da rodada alvo foi encontrado no histórico de treinamento. Não é possível treinar o modelo para esta rodada.")
        return None

    X = df_model_data.reindex(columns=FEATURES, fill_value=0)
    y = df_model_data['pontos_num'].fillna(0)

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    print("  - Modelo treinado com dados até a rodada anterior.")

    df_model_data['pontuacao_prevista'] = model.predict(X)
    
    df_predict = df_mercado_simulado[['atleta_id', 'apelido', 'clube_nome', 'posicao_id', 'pontos_num']].copy()
    df_predict = df_predict.merge(df_model_data[['atleta_id', 'pontuacao_prevista']], on='atleta_id', how='left')
    df_predict['pontuacao_prevista'] = df_predict['pontuacao_prevista'].fillna(0)
    
    df_predict = df_predict.rename(columns={'pontos_num': 'pontuacao_real'})
    
    print("  - Predições geradas e unidas com os resultados reais da rodada.")
    return df_predict

def run():
    """
    Orquestra o processo de backtest para as últimas N rodadas da temporada mais recente.
    """
    print("==================================================")
    print("INICIANDO SCRIPT DE BACKTEST DO MODELO...")
    print("==================================================")

    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}")
        return False
    df_historico_total = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    print(f"  - Dados históricos carregados. Shape total: {df_historico_total.shape}")

    # Filtra para a temporada mais recente
    ano_atual = df_historico_total['ano'].max()
    df_historico_temporada = df_historico_total[df_historico_total['ano'] == ano_atual].copy()
    print(f"  - Filtrando dados para a temporada mais recente: {int(ano_atual)}. Shape: {df_historico_temporada.shape}")

    # Identifica as rodadas que foram de fato jogadas (têm pontuação) na temporada atual
    df_com_pontos = df_historico_temporada[df_historico_temporada['pontos_num'].notna()]
    rodadas_completas = sorted(df_com_pontos['rodada_id'].unique(), reverse=True)

    if len(rodadas_completas) < 2:
        print("AVISO: Não há rodadas completas suficientes na temporada atual para o backtest. É necessária pelo menos 1 rodada para treinar e 1 para testar.")
        return True

    # As rodadas para testar são as N mais recentes que têm dados de pontuação
    rodadas_para_backtest = rodadas_completas[:BACKTEST_ROUNDS]
    
    ultima_rodada_completa = rodadas_completas[0]

    print(f"  - Última rodada com pontuação encontrada na temporada {int(ano_atual)}: {ultima_rodada_completa}")
    print(f"  - Rodadas a serem testadas (as {BACKTEST_ROUNDS} mais recentes com dados): {rodadas_para_backtest}")

    for rodada in rodadas_para_backtest:
        resultado_rodada_df = train_and_predict_for_round(rodada, df_historico_temporada)
        
        if resultado_rodada_df is not None:
            backtest_results = {}
            for pos_nome, pos_id in POSICOES.items():
                df_pos = resultado_rodada_df[resultado_rodada_df['posicao_id'] == pos_id]
                if not df_pos.empty:
                    melhor_jogador = df_pos.sort_values(by='pontuacao_prevista', ascending=False).iloc[0]
                    
                    pontuacao_real = melhor_jogador['pontuacao_real']
                    target_score = TARGET_SCORES.get(pos_id, 0)
                    sinal = get_signal(pontuacao_real, target_score)
                    
                    backtest_results[pos_nome] = {
                        'apelido': melhor_jogador['apelido'],
                        'pontuacao_real': pontuacao_real,
                        'sinal': sinal
                    }
            
            if not backtest_results:
                print(f"  - AVISO: Nenhuma recomendação pôde ser gerada para a rodada {rodada} após a predição.")
                continue

            output_filename = os.path.join(VISUALIZATION_DATA_PATH, f'backtest_rodada_{rodada}.json')
            os.makedirs(VISUALIZATION_DATA_PATH, exist_ok=True)
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(backtest_results, f, ensure_ascii=False, indent=4)
            
            print(f"  - Resultado do backtest para a rodada {rodada} salvo em {output_filename}")

    print("\n==================================================")
    print("SCRIPT DE BACKTEST CONCLUÍDO COM SUCESSO!")
    print("==================================================")
    return True

if __name__ == "__main__":
    run()
