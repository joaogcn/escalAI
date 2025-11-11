import pandas as pd
import numpy as np
import os
import requests
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import INTERMEDIATE_DATA_PATH, CONSOLIDATED_OUTPUT_FILE, NUMERIC_COLS, SCOUT_COLS

def run():
    print('--- INICIANDO: Carga e Limpeza de Dados ---')

    API_URL = 'https://api.github.com/repos/henriquepgomide/caRtola/contents/data/01_raw'

    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        all_content = response.json()
        all_year_dirs = [item['name'] for item in all_content if item['type'] == 'dir' and item['name'].isdigit()]
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha ao buscar lista de anos do GitHub: {e}")
        return False

    if not all_year_dirs:
        print(f'ERRO: Nenhum diretório de ano encontrado em {API_URL}.')
        return False

    anos_encontrados = sorted(all_year_dirs)
    anos_a_processar = anos_encontrados[-4:]
    print(f'  - Processando os anos: {anos_a_processar}')
    df_list = []

    for year in anos_a_processar:
        year_url = f'{API_URL}/{year}'
        try:
            response = requests.get(year_url)
            response.raise_for_status()
            year_files = response.json()
        except requests.exceptions.RequestException as e:
            print(f"ERRO: Falha ao buscar arquivos para o ano {year}: {e}")
            continue

        rodada_files_urls = [f['download_url'] for f in year_files if 'name' in f and f['name'].startswith('rodada-') and f['name'].endswith('.csv')]

        for file_url in rodada_files_urls:
            try:
                df_rodada = pd.read_csv(file_url, encoding='utf-8', low_memory=False)
                df_rodada['ano'] = int(year)
                df_list.append(df_rodada)
            except UnicodeDecodeError:
                df_rodada = pd.read_csv(file_url, encoding='latin-1', low_memory=False)
                df_rodada['ano'] = int(year)
                df_list.append(df_rodada)
            except Exception as e:
                print(f"  - AVISO: Falha ao ler o arquivo {file_url}. Erro: {e}")


    if not df_list:
        print('ERRO: Nenhum arquivo de dado bruto foi lido do GitHub.')
        return False

    df = pd.concat(df_list, ignore_index=True)

    df.columns = [col.replace('atletas.', '').replace('id.full.name', 'nome') for col in df.columns]

    club_col_candidates = ['clube.nome', 'clube_nome']
    club_col = next((col for col in club_col_candidates if col in df.columns), None)
    
    if club_col:
        df.rename(columns={club_col: 'clube_nome'}, inplace=True)
        df.dropna(subset=['clube_nome'], inplace=True)
        team_name_map = {
            'AmÃ©rica-MG': 'América-MG',
            'AthlÃ©tico-PR': 'Athlético-PR',
            'AtlÃ©tico-MG': 'Atlético-MG',
            'CuiabÃ¡': 'Cuiabá',
            'GoiÃ¡s': 'Goiás',
            'GrÃªmio': 'Grêmio',
            'SÃ£o Paulo': 'São Paulo',
            'JUV': 'Juventude',
            'MIR': 'Mirassol',
            'PAL': 'Palmeiras',
            'FLA': 'Flamengo',
            'FLU': 'Fluminense',
            'RBB': 'Bragantino',
            'SAN': 'Santos',
            'SAO': 'São Paulo',
            'SPT': 'Sport Recife',
            'BAH': 'Bahia',
            'BOT': 'Botafogo',
            'CAM': 'Atlético-MG',
            'CEA': 'Ceará',
            'COR': 'Corinthians',
            'CRU': 'Cruzeiro',
            'GRE': 'Grêmio',
            'INT': 'Internacional',
            'VAS': 'Vasco',
            'VIT': 'Vitória',
            'FOR': 'Fortaleza',
            'Athletico-PR': 'Athlético-PR'
        }
        df['clube_nome'] = df['clube_nome'].replace(team_name_map)
    else:
        print("  - AVISO: Coluna com nome do clube não encontrada. Alguns dados podem ficar incompletos.")

    for col in SCOUT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    initial_rows = len(df)
    df.dropna(subset=['preco_num'], inplace=True)
    print(f'  - Registros com preço ausente removidos: {initial_rows - len(df)}')

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(0)

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

    if 'clube_id' in df.columns:
        df['clube_id'] = pd.to_numeric(df['clube_id'], errors='coerce').fillna(0).astype(int)
    if 'status_id' in df.columns:
        df['status_id'] = pd.to_numeric(df['status_id'], errors='coerce').fillna(0).astype('category')

    os.makedirs(INTERMEDIATE_DATA_PATH, exist_ok=True)
    df.to_parquet(CONSOLIDATED_OUTPUT_FILE, index=False)
    print(f'\n  - Dados limpos e consolidados salvos em: {CONSOLIDATED_OUTPUT_FILE}')
    print(f'  - Shape do DataFrame final: {df.shape}')
    print('--- SUCESSO: Carga e Limpeza de Dados Concluída ---')
    return True

if __name__ == "__main__":
    run()