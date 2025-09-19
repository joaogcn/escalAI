import pandas as pd
import numpy as np

# --- Configurações ---
CONSOLIDATED_DATA_PATH = 'dados_cartola/02_intermediate/dados_consolidados.parquet'

def exploratory_analysis():
    """
    Realiza uma análise exploratória focada no desempenho agregado dos atletas.
    """
    print("Iniciando a Análise Exploratória...")

    # --- 1. Carga de Dados ---
    try:
        df = pd.read_parquet(CONSOLIDATED_DATA_PATH)
        print(f"Dados carregados com sucesso. Formato: {df.shape}")
    except FileNotFoundError:
        print(f"ERRO: Arquivo de dados consolidados não encontrado em '{CONSOLIDATED_DATA_PATH}'.")
        print("Por favor, execute o script '01_data_cleaning.py' primeiro.")
        return

    # --- 2. Análise Agregada por Atleta ---
    # Garantir que as colunas necessárias existem
    required_cols = ['apelido', 'posicao_id', 'clube.nome', 'pontos_num', 'preco_num', 'variacao_num']
    if not all(col in df.columns for col in required_cols):
        print(f"ERRO: Colunas necessárias para análise não encontradas. Colunas existentes: {df.columns.tolist()}")
        return
        
    print("\nAgregando estatísticas por atleta...")

    # Agrupa por atleta e calcula as métricas agregadas
    # Usamos 'last' para 'posicao_id' e 'clube.nome' para pegar a informação mais recente
    player_agg = df.groupby('apelido').agg(
        total_pontos=('pontos_num', 'sum'),
        media_pontos=('pontos_num', 'mean'),
        std_pontos=('pontos_num', 'std'),
        max_pontos=('pontos_num', 'max'),
        jogos_disputados=('apelido', 'size'),
        media_preco=('preco_num', 'mean'),
        ultimo_clube=('clube.nome', 'last'),
        posicao=('posicao_id', 'last')
    ).reset_index()

    # Preencher NaNs na Desvio Padrão (para jogadores com 1 jogo) com 0
    player_agg['std_pontos'] = player_agg['std_pontos'].fillna(0)

    # --- 3. Métrica de Custo-Benefício ---
    # Evitar divisão por zero para jogadores com preço médio 0
    player_agg['custo_beneficio_medio'] = (player_agg['media_pontos'] / player_agg['media_preco']).replace([np.inf, -np.inf], 0).fillna(0)
    
    # Ordenar por média de pontos para ver os melhores
    player_agg_sorted = player_agg.sort_values(by='media_pontos', ascending=False)

    # --- 4. Exibição dos Resultados Iniciais ---
    print("\n--- Análise Descritiva Agregada por Atleta ---")
    print("Shape do DataFrame Agregado:", player_agg_sorted.shape)
    
    print("\n--- Top 10 Jogadores por Média de Pontos (com mais de 10 jogos) ---")
    print(player_agg_sorted[player_agg_sorted['jogos_disputados'] > 10].head(10))

    print("\n--- Top 10 Jogadores por Custo-Benefício Médio (com mais de 10 jogos) ---")
    top_custo_beneficio = player_agg_sorted[player_agg_sorted['jogos_disputados'] > 10].sort_values(by='custo_beneficio_medio', ascending=False)
    print(top_custo_beneficio.head(10))
    
    print("\n--- Estatísticas Descritivas Gerais (Jogadores Agregados) ---")
    print(player_agg_sorted.describe())

    # --- 5. Salvando o Resultado Agregado ---
    AGGREGATED_OUTPUT_FILE = 'dados_cartola/02_intermediate/dados_agregados_por_atleta.parquet'
    print(f"\nSalvando dados agregados em '{AGGREGATED_OUTPUT_FILE}'...")
    player_agg_sorted.to_parquet(AGGREGATED_OUTPUT_FILE, index=False)
    print("Dados agregados salvos com sucesso.")


if __name__ == '__main__':
    exploratory_analysis()
