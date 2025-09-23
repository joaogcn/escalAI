import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, AGGREGATED_OUTPUT_FILE

def run():
    """
    Realiza a agregação de dados por atleta.
    - Carrega os dados limpos.
    - Agrupa por jogador e calcula métricas de desempenho (média de pontos, etc.).
    - Salva o DataFrame agregado em formato parquet.
    """
    print("\n--- INICIANDO: [5/5] Agregação de Dados por Atleta ---")

    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em '{CONSOLIDATED_OUTPUT_FILE}'.")
        print("Execute os scripts anteriores (01, 02, 03) primeiro.")
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    print(f"  - Dados limpos carregados. Shape: {df.shape}")

    print("  - Agregando dados por jogador...")
    df_jogadores = df[df['posicao_id'] != 'tec']

    player_agg = df_jogadores.groupby(['atleta_id', 'apelido']).agg(
        total_pontos=('pontos_num', 'sum'),
        media_pontos=('pontos_num', 'mean'),
        std_pontos=('pontos_num', 'std'),
        jogos_disputados=('pontos_num', lambda x: (x != 0).sum()),
        media_preco=('preco_num', 'mean'),
        ultimo_clube=('clube.nome', 'last'),
        posicao=('posicao_id', 'last')
    ).reset_index()

    player_agg['std_pontos'] = player_agg['std_pontos'].fillna(0)
    
    player_agg['custo_beneficio_medio'] = (player_agg['media_pontos'] / player_agg['media_preco']).replace([np.inf, -np.inf], 0).fillna(0)
    
    player_agg_sorted = player_agg.sort_values(by='media_pontos', ascending=False)
    
    os.makedirs(os.path.dirname(AGGREGATED_OUTPUT_FILE), exist_ok=True)
    player_agg_sorted.to_parquet(AGGREGATED_OUTPUT_FILE, index=False)
    
    print(f"  - Análise agregada por atleta salva em '{AGGREGATED_OUTPUT_FILE}'")
    print("--- SUCESSO: [5/5] Agregação de Dados Concluída ---")
    return True

if __name__ == "__main__":
    if not run():
        sys.exit(1)
