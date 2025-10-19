import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, AGGREGATED_OUTPUT_FILE, SCOUT_COLS

def run():
    print('  --- INICIANDO: Agregação de Dados por Atleta ---')
    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print('ERRO: Arquivo de dados consolidados não encontrado.')
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    df_jogadores = df[df['posicao_id'] != 'tec'].copy()

    df_jogadores['rodada_id'] = pd.to_numeric(df_jogadores['rodada_id'], errors='coerce')

    agg_per_round = df_jogadores.groupby('atleta_id').agg(
        media_pontos=('pontos_num', 'mean'),
        std_pontos=('pontos_num', 'std'),
        jogos_disputados=('pontos_num', lambda x: (x != 0).sum()),
        anos_disputados=('ano', 'nunique'),
        media_preco=('preco_num', 'mean'),
        apelido=('apelido', 'last'),
        ultimo_clube=('clube.nome', 'last'),
        posicao=('posicao_id', 'last')
    ).reset_index()

    df_last_rounds = df_jogadores.loc[df_jogadores.groupby(['atleta_id', 'ano'])['rodada_id'].idxmax()]

    scout_cols_to_sum = [scout for scout in SCOUT_COLS if scout in df_last_rounds.columns]
    agg_scouts = df_last_rounds.groupby('atleta_id')[scout_cols_to_sum].sum().reset_index()
    agg_scouts.columns = ['atleta_id'] + [f'total_{scout}' for scout in scout_cols_to_sum]

    player_agg = pd.merge(agg_per_round, agg_scouts, on='atleta_id', how='left')

    for scout in scout_cols_to_sum:
        if f'total_{scout}' in player_agg.columns:
            player_agg[f'total_{scout}'] = player_agg[f'total_{scout}'].fillna(0)

    player_agg['std_pontos'] = player_agg['std_pontos'].fillna(0)
    player_agg['custo_beneficio_medio'] = (player_agg['media_pontos'] / player_agg['media_preco']).replace([np.inf, -np.inf], 0).fillna(0)

    player_agg_sorted = player_agg.sort_values(by='custo_beneficio_medio', ascending=False)

    os.makedirs(os.path.dirname(AGGREGATED_OUTPUT_FILE), exist_ok=True)
    player_agg_sorted.to_parquet(AGGREGATED_OUTPUT_FILE, index=False)

    print(f'  - Análise agregada por atleta salva em {AGGREGATED_OUTPUT_FILE}')
    print('--- SUCESSO: Agregação de Dados Concluída ---')
    return True

if __name__ == "__main__":
    run()