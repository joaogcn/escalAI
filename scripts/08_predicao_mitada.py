import pandas as pd
import os
import sys
import json
from sklearn.ensemble import RandomForestRegressor
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONSOLIDATED_OUTPUT_FILE, VISUALIZATION_DATA_PATH
from src.dados import get_mercado_data

def run():
    """
    Gera dicas de mitada usando uma abordagem híbrida: treina o modelo com dados
    históricos, mas filtra e apresenta os jogadores com base no mercado atual.
    """
    print('--- INICIANDO: Geração de Dicas de Mitada (v9 - Corrigido) ---')

    # --- 1. Carga de Dados Históricos ---
    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE):
        print(f"ERRO: Arquivo de dados consolidados não encontrado em {CONSOLIDATED_OUTPUT_FILE}")
        return False
    df_historico = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    print(f"  - DataFrame histórico carregado. Shape: {df_historico.shape}")

    # --- 2. Buscar e Preparar Dados do Mercado Atual ---
    try:
        mercado_data = get_mercado_data()
        if not mercado_data or 'atletas' not in mercado_data:
            print("  - AVISO: Não foi possível obter dados do mercado. Abortando.")
            return False
        
        atletas_mercado = mercado_data['atletas']
        clubes_mercado = mercado_data['clubes']
        posicoes_mercado = mercado_data['posicoes']
        
        df_mercado = pd.DataFrame(atletas_mercado)
        
        clubes_map = {clube['id']: clube['nome'] for clube in clubes_mercado.values()}
        df_mercado['clube_nome'] = df_mercado['clube_id'].map(clubes_map)

        posicoes_map = {pos['id']: pos['abreviacao'] for pos in posicoes_mercado.values()}
        df_mercado['posicao_id'] = df_mercado['posicao_id'].map(posicoes_map)

        df_mercado = df_mercado[df_mercado['status_id'] == 7].copy()
        print(f"  - Dados do mercado carregados e processados. Jogadores prováveis: {df_mercado.shape[0]}")

    except Exception as e:
        print(f"  - ERRO ao buscar ou processar dados do mercado: {e}. Abortando.")
        return False

    if df_mercado.empty:
        print("  - AVISO: Nenhum jogador provável encontrado no mercado. Abortando.")
        return False

    # --- 3. Preparar Dados para o Modelo ---
    df_latest_historico = df_historico.loc[df_historico.groupby('atleta_id')['rodada_id'].idxmax()]
    
    jogadores_mercado_ids = df_mercado['atleta_id'].unique()
    df_model_data = df_latest_historico[df_latest_historico['atleta_id'].isin(jogadores_mercado_ids)].copy()
    print(f"  - Jogadores do mercado encontrados no histórico: {df_model_data.shape[0]}")

    if df_model_data.empty:
        print("  - AVISO: Nenhum jogador do mercado atual possui dados históricos para previsão. O arquivo de recomendação não será gerado.")
        return False

    # --- 4. Feature Engineering e Treinamento ---
    features = [
        'preco_num', 'variacao_num', 'media_num', 'jogos_num', 'A', 'DS', 'FC', 
        'FD', 'FF', 'FS', 'FT', 'G', 'I', 'PI', 'PP', 'CA', 'DE', 'GS', 
        'PC', 'SG', 'GC', 'CV', 'PS', 'DP', 'V'
    ]
    
    X = df_model_data.reindex(columns=features, fill_value=0)
    y = df_model_data['pontos_num'].fillna(0)

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    print("  - Modelo treinado com dados históricos de jogadores do mercado atual.")

    # --- 5. Predição e Junção com Dados de Mercado ---
    df_model_data['pontuacao_prevista'] = model.predict(X)
    
    df_predict = df_mercado[['atleta_id', 'apelido', 'clube_nome', 'posicao_id']].copy()
    df_predict = df_predict.merge(df_model_data[['atleta_id', 'pontuacao_prevista']], on='atleta_id', how='left')
    df_predict['pontuacao_prevista'] = df_predict['pontuacao_prevista'].fillna(0)
    print("  - Predições geradas e unidas com os dados de mercado atuais.")

    # --- 6. Recomendação Final ---
    recomendacoes = {}
    posicoes_nomes = {
        "gol": "Goleiro", "lat": "Lateral", "zag": "Zagueiro",
        "mei": "Meia", "ata": "Atacante", "tec": "Técnico"
    }

    for pos_abbr, pos_nome in posicoes_nomes.items():
        df_pos = df_predict[df_predict['posicao_id'] == pos_abbr]
        if not df_pos.empty:
            best_player = df_pos.sort_values(by='pontuacao_prevista', ascending=False).iloc[0]
            recomendacoes[pos_nome] = best_player[['apelido', 'clube_nome']].to_dict()
            print(f"    - Melhor jogador para '{pos_nome}': {best_player['apelido']}")
        else:
            print(f"    - AVISO: Nenhum jogador encontrado para a posição: {pos_nome}")

    output_path = os.path.join(VISUALIZATION_DATA_PATH, 'recomendacao_mitada.json')
    os.makedirs(VISUALIZATION_DATA_PATH, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recomendacoes, f, ensure_ascii=False, indent=4)

    if not recomendacoes:
        print("  - AVISO FINAL: Nenhuma recomendação foi gerada. O arquivo JSON está vazio.")
    else:
        print(f"  - Recomendações salvas em: {output_path}")

    print('--- SUCESSO: Geração de Dicas de Mitada Concluída ---')
    return True

if __name__ == "__main__":
    run()
