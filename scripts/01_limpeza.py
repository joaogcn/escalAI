import pandas as pd
import glob
import os
import sys

# Adiciona o diretório raiz ao path para a importação funcionar tanto em execução direta quanto via orquestrador
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import ROOT_DIR, RAW_DATA_PATH, INTERMEDIATE_DATA_PATH, CONSOLIDATED_OUTPUT_FILE, NUMERIC_COLS, SCOUT_COLS

def run():
    """
    Coleta, consolida e limpa os dados brutos do Cartola FC.
    - Lê arquivos CSV de múltiplos anos.
    - Renomeia colunas.
    - Padroniza nomes de times.
    - Preenche valores numéricos e de scouts ausentes com 0.
    - Mapeia posições e ajusta tipos de dados.
    - Salva o DataFrame limpo em formato parquet.
    """
    print("--- INICIANDO: [1/4] Limpeza de Dados ---")

    all_year_dirs = [d for d in os.listdir(RAW_DATA_PATH) if os.path.isdir(os.path.join(RAW_DATA_PATH, d)) and d.isdigit()]
    if not all_year_dirs:
        print(f"ERRO: Nenhum diretório de ano encontrado em '{RAW_DATA_PATH}'. Abortando.")
        return False

    # Ordena os anos e seleciona apenas os últimos 4
    anos_encontrados = sorted([d for d in all_year_dirs])
    anos_a_processar = anos_encontrados[-4:]
    
    print(f"  - Total de anos encontrados: {len(anos_encontrados)}. Processando os últimos 4: {anos_a_processar}")
    
    df_list = []
    for year in anos_a_processar:
        rodada_files = glob.glob(os.path.join(RAW_DATA_PATH, year, 'rodada-*.csv'))
        rodada_files.extend(glob.glob(os.path.join(RAW_DATA_PATH, year, 'Mercado_*.txt')))

        for file in rodada_files:
            # Imprime o caminho relativo do arquivo para dar feedback ao usuário
            relative_path = os.path.relpath(file, ROOT_DIR)
            # Usa ljust para preencher com espaços e limpar a linha anterior
            print(f"    - Lendo: {relative_path.ljust(80)}", end='\r')
            try:
                df_rodada = pd.read_csv(file, encoding='utf-8', low_memory=False)
            except UnicodeDecodeError:
                df_rodada = pd.read_csv(file, encoding='latin-1', low_memory=False)
            df_rodada['ano'] = int(year)
            df_list.append(df_rodada)
    # Limpa a linha de progresso antes de continuar
    print(" " * 100, end="\r")


    if not df_list:
        print("ERRO: Nenhum arquivo de dado bruto foi encontrado. Abortando.")
        return False

    df = pd.concat(df_list, ignore_index=True)
    print(f"  - Dados brutos consolidados. Shape: {df.shape}")

    print("  - Simplificando nomes de colunas...")
    df.columns = [col.replace('atletas.', '').replace('id.full.name', 'nome') for col in df.columns]

    print("  - Padronizando nomes de times...")
    if 'clube.nome' in df.columns:
        df['clube.nome'] = df['clube.nome'].str.replace('AmÃ©rica-MG', 'América-MG', regex=False)

    print("  - Tratando valores ausentes (NaN -> 0)...")
    all_numeric_cols = NUMERIC_COLS + SCOUT_COLS
    for col in all_numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    print("  - Mapeando posições...")
    if 'posicao_id' in df.columns:
        pos_map = {
            '1': 'gol', 'gol': 'gol',
            '2': 'lat', 'lat': 'lat',
            '3': 'zag', 'zag': 'zag',
            '4': 'mei', 'mei': 'mei',
            '5': 'ata', 'ata': 'ata',
            '6': 'tec', 'tec': 'tec'
        }
        df['posicao_id'] = df['posicao_id'].astype(str).str.lower().map(pos_map).fillna('desconhecida').astype('category')

    print("  - Ajustando tipos de dados...")
    if 'clube_id' in df.columns:
        df['clube_id'] = pd.to_numeric(df['clube_id'], errors='coerce').fillna(0).astype(int)
    if 'status_id' in df.columns:
        df['status_id'] = pd.to_numeric(df['status_id'], errors='coerce').fillna(0).astype('category')

    os.makedirs(INTERMEDIATE_DATA_PATH, exist_ok=True)
    df.to_parquet(CONSOLIDATED_OUTPUT_FILE, index=False)
    print(f"  - Dados limpos salvos em: '{CONSOLIDATED_OUTPUT_FILE}'")
    print("--- SUCESSO: [1/4] Limpeza de Dados Concluída ---")
    return True

if __name__ == "__main__":
    run()
