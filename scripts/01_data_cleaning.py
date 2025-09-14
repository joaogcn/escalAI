import pandas as pd
import glob
import os
import json

# --- Configurações ---
RAW_DATA_PATH = 'dados_cartola/raw'
INTERMEDIATE_DATA_PATH = 'dados_cartola/02_intermediate'
OUTPUT_FILE = os.path.join(INTERMEDIATE_DATA_PATH, 'dados_consolidados.parquet')

def clean_data():
    """
    Uma função completa para carregar, limpar e consolidar os dados históricos do Cartola FC.
    """
    print("Iniciando a Lição 1: Limpeza e Pré-processamento de Dados.")

    # --- 1. Carga e Consolidação ---
    print(f"Analisando diretórios de anos em '{RAW_DATA_PATH}'...")
    
    try:
        all_year_dirs = [d for d in os.listdir(RAW_DATA_PATH) if os.path.isdir(os.path.join(RAW_DATA_PATH, d)) and d.isdigit()]
        sorted_years = sorted(all_year_dirs, key=int, reverse=True)
        year_dirs = sorted_years[:4]
        print(f"Processando os últimos {len(year_dirs)} anos de dados: {year_dirs}")
    except FileNotFoundError:
        year_dirs = []

    if not year_dirs:
        print("="*50)
        print(f"AVISO: Nenhum diretório de ano encontrado em '{RAW_DATA_PATH}'.")
        print("Execute a automação do GitHub Actions para popular a pasta.")
        print("="*50)
        return
        
    print(f"Anos encontrados: {sorted([int(y) for y in year_dirs])}")

    df_list = []
    print("Carregando e processando arquivos 'rodada-*.csv'...")

    for year in year_dirs:
        rodada_files = glob.glob(os.path.join(RAW_DATA_PATH, year, 'rodada-*.csv'))
        print(f"  - Ano {year}: Encontrados {len(rodada_files)} arquivos de rodada.")
        
        for file in rodada_files:
            try:
                try:
                    df_rodada = pd.read_csv(file, encoding='utf-8')
                except UnicodeDecodeError:
                    df_rodada = pd.read_csv(file, encoding='latin-1')
                
                df_rodada['ano'] = int(year)
                df_list.append(df_rodada)
            except Exception as e:
                print(f"AVISO: Erro ao processar o arquivo {file}. Erro: {e}")

    if not df_list:
        print("="*50)
        print("AVISO: Nenhum arquivo de dado bruto foi encontrado.")
        print(f"Verifique se a pasta '{RAW_DATA_PATH}' contém os dados.")
        print("="*50)
        return

    print("Consolidando todos os dados em um único DataFrame...")
    df = pd.concat(df_list, ignore_index=True)
    print("Dados consolidados.")

    # --- 2. Padronização dos Nomes dos Times ---
    print("\nPadronizando nomes de times...")
    if 'atletas.clube.id.full.name' in df.columns:
        # Corrigir problemas de encoding primeiro
        encoding_fixes = {
            'AmÃ©rica-MG': 'América-MG',
            'AthlÃ©tico-PR': 'Athlético-PR',
            'AtlÃ©tico-MG': 'Atlético-MG',
            'CuiabÃ¡': 'Cuiabá',
            'GoiÃ¡s': 'Goiás',
            'GrÃªmio': 'Grêmio',
            'SÃ£o Paulo': 'São Paulo',
        }
        for bad_name, good_name in encoding_fixes.items():
            df['atletas.clube.id.full.name'] = df['atletas.clube.id.full.name'].str.replace(bad_name, good_name, regex=False)

        # Padronizar abreviações
        abbreviation_fixes = {
            'BAH': 'Bahia',
            'BOT': 'Botafogo',
            'CAM': 'Atlético-MG',
            'CEA': 'Ceará',
            'COR': 'Corinthians',
            'CRU': 'Cruzeiro',
            'FLA': 'Flamengo',
            'FLU': 'Fluminense',
            'FOR': 'Fortaleza',
            'GRE': 'Grêmio',
            'INT': 'Internacional',
            'JUV': 'Juventude',
            'PAL': 'Palmeiras',
            'SAN': 'Santos',
            'SAO': 'São Paulo',
            'VAS': 'Vasco',
            'VIT': 'Vitória',
            'RBB': 'Bragantino',
            'MIR': 'Mirassol',
            'SPT': 'Sport',
        }
        df['atletas.clube.id.full.name'] = df['atletas.clube.id.full.name'].replace(abbreviation_fixes)
        
        print("Nomes de times padronizados.")
    else:
        print("AVISO: Coluna 'atletas.clube.id.full.name' não encontrada para padronização.")


    # --- 3. Diagnóstico Inicial ---
    print("\n--- Diagnóstico Inicial do DataFrame ---")
    print("Formato do DataFrame (Linhas, Colunas):", df.shape)
    print("Verificando valores nulos por coluna:")
    print(df.isnull().sum())
    print("---" * 35)

    # --- 4. Limpeza e Transformação ---
    print("\nSimplificando nomes de colunas...")
    df.columns = [col.replace('atletas.', '').replace('id.full.name', 'nome') for col in df.columns]
    print("Nomes de colunas simplificados.")

    print("Tratando valores ausentes...")
    numeric_cols_to_fill = ['pontos_num', 'preco_num', 'variacao_num', 'media_num', 'jogos_num']
    for col in numeric_cols_to_fill:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    print("Valores numéricos ausentes preenchidos com 0.")

    if 'posicao_id' in df.columns:
        df['posicao_id'] = df['posicao_id'].fillna('Desconhecida')

    print("Ajustando tipos de dados...")
    if 'clube_id' in df.columns:
        df['clube_id'] = pd.to_numeric(df['clube_id'], errors='coerce').fillna(0).astype(int)
    if 'clube.nome' in df.columns:
        df['clube.nome'] = df['clube.nome'].astype('category')
    
    if 'posicao_id' in df.columns:
        pos_map = {
            '1': 'gol', '2': 'lat', '3': 'zag', '4': 'mei', '5': 'ata', '6': 'tec',
            'gol': 'gol', 'lat': 'lat', 'zag': 'zag', 'mei': 'mei', 'ata': 'ata', 'tec': 'tec'
        }
        df['posicao_id'] = df['posicao_id'].astype(str).str.lower().map(pos_map).astype('category')

    if 'status_id' in df.columns:
        df['status_id'] = pd.to_numeric(df['status_id'], errors='coerce').fillna(0).astype('category')

    print("Tipos de dados ajustados para melhor performance.")

    # --- 5. Salvando o Resultado ---
    print(f"\nSalvando o DataFrame limpo em '{OUTPUT_FILE}'...")
    os.makedirs(INTERMEDIATE_DATA_PATH, exist_ok=True)
    
    print("\nColunas finais do DataFrame antes de salvar:")
    print(df.columns.tolist())
    
    df.to_parquet(OUTPUT_FILE, index=False)
    print("="*50)
    print("Lição 1 Concluída! Seus dados estão limpos, consolidados e prontos para a análise.")
    print(f"Arquivo salvo em: {OUTPUT_FILE}")
    print("="*50)

if __name__ == '__main__':
    clean_data()
