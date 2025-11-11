import streamlit as st
import pandas as pd
import json
import os
import glob

VISUALIZATION_DATA_PATH = "dados_cartola/03_visualizacoes"

st.set_page_config(
    page_title="Backtest do Modelo",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Backtest do Modelo de Machine Learning")
st.markdown("""
Nesta página, analisamos o desempenho real das recomendações do nosso modelo de "mitada" nas últimas rodadas. 
O processo de backtest treina o modelo com os dados disponíveis *antes* de cada rodada e, em seguida, compara a previsão com o resultado real.
""")

@st.cache_data
def carregar_resultados_backtest():
    """Carrega os resultados dos arquivos de backtest gerados pelo script."""
    resultados = []
    padrao_arquivo = os.path.join(VISUALIZATION_DATA_PATH, "backtest_rodada_*.json")
    arquivos_backtest = sorted(glob.glob(padrao_arquivo), reverse=True)
    
    if not arquivos_backtest:
        st.warning("Nenhum arquivo de resultado de backtest foi encontrado. Execute o pipeline de dados, incluindo o script de backtest.")
        return []

    for arquivo in arquivos_backtest:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                resultados.append(dados)
        except (json.JSONDecodeError, FileNotFoundError):
            st.error(f"Erro ao ler o arquivo de backtest: {arquivo}")
            continue
            
    return resultados

resultados_backtest = carregar_resultados_backtest()

if not resultados_backtest:
    st.info("Execute o script `scripts/09_backtest.py` para gerar os dados de análise.")
else:
    st.header("Análise de Desempenho por Rodada")

    resultados_backtest.sort(key=lambda x: x['rodada_id'], reverse=True)

    for resultado in resultados_backtest:
        rodada_id = resultado['rodada_id']
        recomendacoes = resultado.get('recomendacoes', [])
        
        st.subheader(f"🔍 Rodada {rodada_id}")

        if not recomendacoes:
            st.write("Nenhuma recomendação foi gerada para esta rodada.")
            continue

        df_recomendacoes = pd.DataFrame(recomendacoes)
        
        pos_map = {'ata': 'Atacante', 'mei': 'Meia', 'lat': 'Lateral', 'zag': 'Zagueiro', 'gol': 'Goleiro', 'tec': 'Técnico'}
        df_recomendacoes['posicao_id'] = df_recomendacoes['posicao_id'].map(pos_map)

        colunas_exibicao = {
            'apelido': 'Apelido',
            'clube.nome': 'Clube',
            'posicao_id': 'Posição',
            'pontuacao_prevista': 'Pontuação Prevista',
            'pontuacao_real': 'Pontuação Real'
        }
        
        df_display = df_recomendacoes[colunas_exibicao.keys()].rename(columns=colunas_exibicao)
        
        st.dataframe(
            df_display.sort_values(by='Pontuação Real', ascending=False).reset_index(drop=True),
            use_container_width=True
        )

        pontuacao_total_real = df_display['Pontuação Real'].sum()
        pontuacao_total_prevista = df_display['Pontuação Prevista'].sum()
        
        col1, col2 = st.columns(2)
        col1.metric(label="Pontuação Total Real dos Recomendados", value=f"{pontuacao_total_real:.2f}")
        col2.metric(label="Pontuação Total Prevista", value=f"{pontuacao_total_prevista:.2f}")
        st.markdown("---")

st.info("""
**Como ler esta página:** Cada tabela mostra as recomendações que o modelo *teria feito* para aquela rodada, com base nos dados disponíveis na época. 
A "Pontuação Prevista" é o que o modelo esperava, e a "Pontuação Real" é o resultado que o jogador de fato alcançou.
""")
