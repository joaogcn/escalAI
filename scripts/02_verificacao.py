import pandas as pd
import os
import sys

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, NUMERIC_COLS, SCOUT_COLS

def run():
    """
    Verifica a qualidade do conjunto de dados limpo.
    - Checa se o arquivo existe.
    - Valida se não há NaNs em colunas numéricas/scouts.
    - Valida as categorias da coluna de posição.
    - Retorna True se todas as verificações passarem, senão False.
    """
    print("\n--- INICIANDO: [2/4] Verificação de Dados ---")

    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em '{CONSOLIDATED_OUTPUT_FILE}'.")
        print("Execute o script de limpeza (01_limpeza.py) primeiro.")
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    print(f"  - Arquivo '{CONSOLIDATED_OUTPUT_FILE}' carregado. Shape: {df.shape}")

    # 1. Verificação de Nulos
    print("  - Verificando valores nulos em colunas numéricas e de scouts...")
    check_cols = NUMERIC_COLS + SCOUT_COLS
    cols_with_nan = [col for col in check_cols if col in df.columns and df[col].isnull().any()]
    
    if cols_with_nan:
        print(f"ERRO: As seguintes colunas contêm valores nulos (NaN): {cols_with_nan}")
        return False
    print("    - OK: Nenhuma coluna numérica com valores nulos.")

    # 2. Verificação de Categorias de Posição
    print("  - Verificando categorias da coluna 'posicao_id'...")
    if 'posicao_id' in df.columns:
        expected_positions = {'gol', 'lat', 'zag', 'mei', 'ata', 'tec', 'desconhecida'}
        actual_positions = set(df['posicao_id'].unique())
        
        if not actual_positions.issubset(expected_positions):
            print(f"ERRO: Posições inesperadas encontradas: {actual_positions - expected_positions}")
            return False
        print("    - OK: Categorias de posição validadas.")

    print("--- SUCESSO: [2/4] Verificação de Dados Concluída ---")
    return True

if __name__ == "__main__":
    if not run():
        sys.exit(1)
