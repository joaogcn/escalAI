import pandas as pd
import os
import sys
import json

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, VISUALIZATION_DATA_PATH, NUMERIC_COLS

def run():
    """
    Calcula estatísticas descritivas e identifica outliers.
    - Carrega os dados limpos.
    - Calcula e salva estatísticas descritivas.
    - Identifica e salva outliers de pontuação usando o método IQR.
    """
    print("\n--- INICIANDO: [3/5] Análise Descritiva e Outliers ---")

    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em '{CONSOLIDATED_OUTPUT_FILE}'.")
        print("Execute os scripts de limpeza (01) e verificação (02) primeiro.")
        return False

    df = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    os.makedirs(VISUALIZATION_DATA_PATH, exist_ok=True)
    print(f"  - Dados limpos carregados. Shape: {df.shape}")

    # 1. Estatísticas Descritivas
    print("  - Gerando estatísticas descritivas...")
    desc_stats = df[NUMERIC_COLS].describe()
    desc_stats_path = os.path.join(VISUALIZATION_DATA_PATH, 'estatisticas_descritivas.json')
    desc_stats.to_json(desc_stats_path, orient='table', indent=4)
    print(f"    - Estatísticas salvas em: {desc_stats_path}")

    # 2. Detecção de Outliers com IQR
    print("  - Identificando outliers de pontuação por posição...")
    outliers_list = []
    # Focar em posições de linha, onde a análise de pontos é mais comparável
    posicoes_analise = ['lat', 'zag', 'mei', 'ata']
    
    for pos in posicoes_analise:
        df_pos = df[df['posicao_id'] == pos]
        
        Q1 = df_pos['pontos_num'].quantile(0.25)
        Q3 = df_pos['pontos_num'].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        pos_outliers = df_pos[(df_pos['pontos_num'] < lower_bound) | (df_pos['pontos_num'] > upper_bound)]
        
        for _, row in pos_outliers.iterrows():
            outliers_list.append({
                'apelido': row['apelido'],
                'posicao': pos,
                'pontos': row['pontos_num'],
                'media_pontos_pos': df_pos['pontos_num'].mean(),
                'limite_superior': upper_bound,
                'limite_inferior': lower_bound,
                'ano': row['ano'],
                'rodada_id': row['rodada_id']
            })

    print(f"    - Total de outliers de pontuação identificados: {len(outliers_list)}")
    
    outliers_path = os.path.join(VISUALIZATION_DATA_PATH, 'outliers_pontuacao.json')
    with open(outliers_path, 'w', encoding='utf-8') as f:
        json.dump(outliers_list, f, ensure_ascii=False, indent=4)
    print(f"    - Outliers salvos em: {outliers_path}")

    print("--- SUCESSO: [3/5] Análise Descritiva Concluída ---")
    return True

if __name__ == "__main__":
    if not run():
        sys.exit(1)
