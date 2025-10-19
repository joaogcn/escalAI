import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, NUMERIC_COLS, SCOUT_COLS

def run():
    print('  --- INICIANDO: Verificação de Dados ---')
    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f'ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}.')
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    print(f'  - Arquivo {CONSOLIDATED_OUTPUT_FILE} carregado. Shape: {df.shape}')

    check_cols = NUMERIC_COLS + SCOUT_COLS
    cols_with_nan = [col for col in check_cols if col in df.columns and df[col].isnull().any()]
    if cols_with_nan:
        print(f'ERRO: As seguintes colunas contêm valores nulos (NaN): {cols_with_nan}')
        return False
    print('    - OK: Nenhuma coluna numérica com valores nulos.')

    if 'posicao_id' in df.columns:
        expected_positions = {'gol', 'lat', 'zag', 'mei', 'ata', 'tec'}
        actual_positions = set(df['posicao_id'].unique())
        if not actual_positions.issubset(expected_positions.union({'desconhecida'})):
            print(f'ERRO: Posições inesperadas encontradas: {actual_positions - expected_positions}')
            return False
        print('    - OK: Categorias de posição validadas.')

    print('--- SUCESSO: Verificação de Dados Concluída ---')
    return True

if __name__ == "__main__":
    run()