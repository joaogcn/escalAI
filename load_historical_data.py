import os
import pandas as pd
import glob
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
import numpy as np

load_dotenv()

# --- Configurações do Supabase (carregadas do .env) ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# --- Mapeamentos ---
POSICOES = {
    # IDs numéricos e abreviações
    '1': 'Goleiro', 'gol': 'Goleiro',
    '2': 'Lateral', 'lat': 'Lateral',
    '3': 'Zagueiro', 'zag': 'Zagueiro',
    '4': 'Meia', 'mei': 'Meia',
    '5': 'Atacante', 'ata': 'Atacante',
    '6': 'Técnico', 'tec': 'Técnico'
}

STATUS = {
    2: 'Dúvida',
    3: 'Suspenso',
    5: 'Contundido',
    6: 'Nulo',
    7: 'Provável'
}

def get_files_for_years(base_path, years):
    all_files = []
    for year in years:
        pattern = os.path.join(base_path, str(year), 'rodada-*.csv')
        all_files.extend(glob.glob(pattern))
    return all_files

def populate_clubes_from_api(supabase: Client):
    """Busca dados de clubes da API do Cartola e popula a tabela 'clubes'."""
    try:
        print("Buscando dados de clubes da API do Cartola...")
        response = requests.get("https://api.cartola.globo.com/clubes")
        response.raise_for_status()  # Lança um erro para status HTTP ruins (4xx ou 5xx) 
        
        clubes_data = response.json()
        
        # O endpoint retorna um dicionário, onde a chave é o ID do clube
        clubes_list = []
        for clube_id, clube_info in clubes_data.items():
            clubes_list.append({
                'id': clube_info['id'],
                'nome': clube_info['nome_fantasia'],
                'abreviacao': clube_info['abreviacao']
            })
        
        if clubes_list:
            print(f"Encontrados {len(clubes_list)} clubes. Inserindo/atualizando no Supabase...")
            supabase.table('clubes').upsert(clubes_list).execute()
            print("Dados dos clubes inseridos/atualizados com sucesso.")
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da API de clubes: {e}")
    except Exception as e:
        print(f"Um erro inesperado ocorreu ao popular os clubes: {e}")


def load_historical_data(supabase: Client, base_path: str, years: list):
    """Carrega os dados históricos de jogadores do Cartola FC para o Supabase."""
    
    # Lembrete de que o schema deve ser executado manualmente.
    print("Lembre-se: o schema em 'historical_schema.sql' deve ser executado manualmente no Supabase se ainda não foi feito.")

    # 1. Popular a tabela de clubes a partir da API
    populate_clubes_from_api(supabase)

    # 2. Coletar todos os arquivos CSV de jogadores
    files_to_process = get_files_for_years(base_path, years)
    
    if not files_to_process:
        print("Nenhum arquivo CSV encontrado para os anos especificados.")
        return

    print(f"{len(files_to_process)} arquivos encontrados para processar.")

    # 3. Processar cada arquivo
    for file_path in files_to_process:
        try:
            print(f"Processando arquivo: {file_path}")
            
            # Extrair ano e rodada do caminho do arquivo
            parts = file_path.replace('\\', '/').split('/')
            year = int(parts[-2])
            rodada = int(parts[-1].replace('rodada-', '').replace('.csv', ''))

            df = pd.read_csv(file_path)

            # Renomear colunas para corresponder ao schema
            df.rename(columns={
                'atletas.atleta_id': 'atleta_id',
                'atletas.rodada_id': 'rodada_id',
                'atletas.clube_id': 'clube_id',
                'atletas.posicao_id': 'posicao_id',
                'atletas.status_id': 'status_id',
                'atletas.pontos_num': 'pontos_num',
                'atletas.preco_num': 'preco_num',
                'atletas.variacao_num': 'variacao_num',
                'atletas.media_num': 'media_num',
                'atletas.jogos_num': 'jogos_num',
                'atletas.apelido': 'apelido',
                'atletas.nome': 'nome'
            }, inplace=True)

            # Mapear IDs para nomes
            # Garante que a coluna de posição seja string e minúscula para o mapeamento
            df['posicao'] = df['posicao_id'].astype(str).str.lower().map(POSICOES)
            df['status'] = df['status_id'].map(STATUS)
            df['temporada'] = year

            # Substituir NaN por None para compatibilidade com JSON
            df.replace({np.nan: None}, inplace=True)

            # Preparar dados dos jogadores para inserção
            cols_to_insert = [
                'atleta_id', 'rodada_id', 'temporada', 'clube_id', 'posicao', 'status',
                'pontos_num', 'preco_num', 'variacao_num', 'media_num', 'jogos_num',
                'apelido', 'nome'
            ] 
            
            existing_cols = [col for col in cols_to_insert if col in df.columns]
            jogadores_data = df[existing_cols].to_dict(orient='records')

            # Inserir dados dos jogadores
            if jogadores_data:
                supabase.table('jogadores').insert(jogadores_data).execute()

            print(f"Dados de {file_path} inseridos com sucesso.")

        except Exception as e:
            print(f"Erro ao processar o arquivo {file_path}: {e}")

if __name__ == '__main__':
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY precisam ser definidas.")
    else:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        base_data_path = 'caRtola-master/data/01_raw'
        years_to_load = [2022, 2023, 2024, 2025]
        load_historical_data(supabase_client, base_data_path, years_to_load)