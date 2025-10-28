import pandas as pd
import os
import sys
import json

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, VISUALIZATION_DATA_PATH

def run():
    """
    Gera recomendações de jogadores com base no desempenho recente e geral.
    """
    print('--- INICIANDO: Geração de Recomendações ---')

    # Verifica se o arquivo de dados consolidados existe
    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}")
        return False

    # Carrega os dados
    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    print(f"  - DataFrame carregado. Shape inicial: {df.shape}")

    # --- Filtra para a Temporada Mais Recente ---
    ano_atual = df['ano'].max()
    df = df[df['ano'] == ano_atual].copy()
    print(f"  - Filtrando para a temporada mais recente: {ano_atual}. Shape: {df.shape}")

    # Filtra apenas por jogadores que pontuaram (exclui rodadas que não jogaram)
    df_jogadores_validos = df[df['pontos_num'].notna() & (df['pontos_num'] != 0)].copy()
    print(f"  - DataFrame após remover jogos não pontuados. Shape: {df_jogadores_validos.shape}")
    
    # Garante que os dados estão ordenados por atleta e rodada
    df_jogadores_validos = df_jogadores_validos.sort_values(by=['atleta_id', 'rodada_id'])

    # --- Lógica de Recomendação ---
    
    # 1. Média de pontos nas últimas 5 partidas jogadas
    df_jogadores_validos['media_ultimas_5'] = df_jogadores_validos.groupby('atleta_id')['pontos_num'].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean()
    )

    # 2. Média geral de pontos (agora apenas da temporada atual)
    df_jogadores_validos['media_geral'] = df_jogadores_validos.groupby('atleta_id')['pontos_num'].transform('mean')

    # 3. Número de jogos disputados (apenas da temporada atual)
    df_jogadores_validos['jogos_disputados'] = df_jogadores_validos.groupby('atleta_id')['atleta_id'].transform('count')

    # Pega os dados mais recentes de cada jogador
    df_latest = df_jogadores_validos.loc[df_jogadores_validos.groupby('atleta_id')['rodada_id'].idxmax()]
    print(f"  - DataFrame com dados mais recentes dos jogadores. Shape: {df_latest.shape}")

    # Filtra jogadores com poucos jogos para ter uma base mais sólida
    df_latest = df_latest[df_latest['jogos_disputados'] >= 3]
    print(f"  - DataFrame após filtrar jogadores com >= 3 jogos. Shape: {df_latest.shape}")


    # 4. Calcula o "Índice EscalAI"
    df_latest['indice_escalai'] = (df_latest['media_ultimas_5'] * 0.7) + (df_latest['media_geral'] * 0.3)
    
    # --- Geração do JSON ---
    
    recomendacoes = {}
    posicoes = {
        'gol': 'Goleiro', 'lat': 'Lateral', 'zag': 'Zagueiro', 
        'mei': 'Meia', 'ata': 'Atacante', 'tec': 'Técnico'
    }
    print(f"  - Posições a serem processadas: {list(posicoes.keys())}")

    for pos_id, pos_nome in posicoes.items():
        # Filtra por posição e ordena pelo índice
        top_5 = df_latest[df_latest['posicao_id'] == pos_id].sort_values(by='indice_escalai', ascending=False).head(5)
        
        if not top_5.empty:
            print(f"    - Encontrados {len(top_5)} jogadores para a posição: {pos_nome}")
        else:
            print(f"    - AVISO: Nenhum jogador encontrado para a posição: {pos_nome}")

        # Formata os dados para o JSON
        recomendacoes[pos_nome] = top_5[[
            'apelido', 'clube.nome', 'posicao_id', 'preco_num', 
            'media_ultimas_5', 'media_geral', 'indice_escalai'
        ]].to_dict(orient='records')

    # Verifica se o dicionário de recomendações não está vazio
    if not any(recomendacoes.values()):
        print("  - AVISO FINAL: Nenhuma recomendação foi gerada para nenhuma posição. O arquivo JSON estará vazio.")

    # Salva o arquivo JSON
    output_path = os.path.join(VISUALIZATION_DATA_PATH, 'recomendacoes_por_posicao.json')
    os.makedirs(VISUALIZATION_DATA_PATH, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recomendacoes, f, ensure_ascii=False, indent=4)

    print(f'  - Recomendações salvas em: {output_path}')
    print('--- SUCESSO: Geração de Recomendações Concluída ---')
    return True

if __name__ == "__main__":
    run()
