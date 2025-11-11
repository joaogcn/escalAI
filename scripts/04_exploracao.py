import pandas as pd
import os
import sys
import plotly.express as px
import plotly.io as pio

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

    print("  - Gerando Boxplot de Pontos por Posição...")
    fig_box_pos = px.box(df, x='posicao_id', y='pontos_num', color='posicao_id',
                         title='Distribuição de Pontos por Posição',
                         labels={'posicao_id': 'Posição', 'pontos_num': 'Pontos na Rodada'})
    pio.write_json(fig_box_pos, os.path.join(VISUALIZATION_DATA_PATH, 'boxplot_pontos_posicao.json'))

    print("  - Gerando Histograma da Distribuição de Pontos...")
    fig_hist_pontos = px.histogram(df, x='pontos_num', nbins=100, title='Distribuição de Pontuações dos Jogadores')
    pio.write_json(fig_hist_pontos, os.path.join(VISUALIZATION_DATA_PATH, 'histograma_pontos.json'))

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

    print("  - Gerando Gráfico de Média de Pontos por Time e Posição...")
    current_year = df['ano'].max()
    df_filtered_for_chart = df[df['ano'] == current_year]
    team_pos_performance = df_filtered_for_chart.groupby(['clube_nome', 'posicao_id'], observed=True)['pontos_num'].mean().reset_index()
    fig_bar_team_pos = px.bar(team_pos_performance, x='clube_nome', y='pontos_num', color='posicao_id',
                              title=f'Média de Pontos por Time e Posição ({current_year})',
                              labels={'clube_nome': 'Time', 'pontos_num': 'Média de Pontos', 'posicao_id': 'Posição'})
    pio.write_json(fig_bar_team_pos, os.path.join(VISUALIZATION_DATA_PATH, 'bar_pontos_time_posicao.json'))

    print("--- SUCESSO: [4/5] Geração de Gráficos Concluída ---")
    return True

if __name__ == "__main__":
    if not run():
        sys.exit(1)