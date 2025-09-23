import os

# --- Configurações da API ---
CARTOLA_BASE_URL = 'https://api.cartolafc.globo.com'

# --- Caminho Raiz do Projeto ---
# Pega o caminho do diretório do arquivo (src) e sobe um nível para a raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Paths para os Dados ---
RAW_DATA_PATH = os.path.join(ROOT_DIR, 'dados_cartola/raw')
INTERMEDIATE_DATA_PATH = os.path.join(ROOT_DIR, 'dados_cartola/02_intermediate')
VISUALIZATION_DATA_PATH = os.path.join(ROOT_DIR, 'dados_cartola/03_visualizacoes')

# --- Nomes de Arquivos de Saída ---
CONSOLIDATED_OUTPUT_FILE = os.path.join(INTERMEDIATE_DATA_PATH, 'dados_consolidados.parquet')
AGGREGATED_OUTPUT_FILE = os.path.join(INTERMEDIATE_DATA_PATH, 'dados_agregados_por_atleta.parquet')

# --- Listas de Colunas para Limpeza ---
NUMERIC_COLS = ['pontos_num', 'preco_num', 'variacao_num', 'media_num', 'jogos_num']
SCOUT_COLS = [
    'A', 'CA', 'CV', 'DD', 'DP', 'DS', 'FC', 'FD', 'FF', 'FS', 
    'FT', 'G', 'GC', 'GS', 'I', 'PC', 'PE', 'PP', 'PS', 'RB', 'SG', 'V'
]
