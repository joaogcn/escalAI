import pandas as pd
import os
import sys
import plotly.express as px
import plotly.io as pio

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, VISUALIZATION_DATA_PATH

def run():
    """
    Gera as visualizações para a análise exploratória.
    - Carrega os dados limpos.
    - Gera e salva o boxplot de pontos por posição.
    - Gera e salva o scatter plot de preço vs. pontos.
    """
    print("\n--- INICIANDO: [4/5] Geração de Gráficos de Exploração ---")

    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em '{CONSOLIDATED_OUTPUT_FILE}'.")
        print("Execute os scripts anteriores primeiro.")
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    os.makedirs(VISUALIZATION_DATA_PATH, exist_ok=True)
    print(f"  - Dados limpos carregados. Shape: {df.shape}")

    # 1. Boxplot de Pontos por Posição
    print("  - Gerando Boxplot de Pontos por Posição...")
    fig_box_pos = px.box(df, x='posicao_id', y='pontos_num', color='posicao_id',
                         title='Distribuição de Pontos por Posição',
                         labels={'posicao_id': 'Posição', 'pontos_num': 'Pontos na Rodada'})
    pio.write_json(fig_box_pos, os.path.join(VISUALIZATION_DATA_PATH, 'boxplot_pontos_posicao.json'))

    # 2. Scatter Plot de Preço vs. Pontos
    print("  - Gerando Scatter Plot de Preço vs. Pontos...")
    df_com_pontos = df[df['pontos_num'] > 0]
    if not df_com_pontos.empty:
        df_sample = df_com_pontos.sample(min(20000, len(df_com_pontos)))
        fig_scatter_preco_pontos = px.scatter(
            df_sample,
            x='preco_num',
            y='pontos_num',
            color='posicao_id',
            trendline="ols",
            trendline_scope="overall",
            title='Relação Preço vs. Pontos (Amostra com Linha de Tendência)',
            labels={'preco_num': 'Preço (C$)', 'pontos_num': 'Pontos na Rodada'}
        )
        pio.write_json(fig_scatter_preco_pontos, os.path.join(VISUALIZATION_DATA_PATH, 'scatter_preco_pontos.json'))
    else:
        print("  - AVISO: Nenhum dado com pontos > 0 encontrado. Gráfico de dispersão não foi gerado.")

    print("--- SUCESSO: [4/5] Geração de Gráficos Concluída ---")
    return True

if __name__ == "__main__":
    if not run():
        sys.exit(1)