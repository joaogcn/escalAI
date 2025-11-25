import streamlit as st
import pandas as pd
import json
import os
import glob
import re

# Constrói um caminho absoluto para o diretório de visualizações, tornando o script mais robusto.
# O script está em /pages, então a raiz do projeto é um nível acima.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VISUALIZATION_DATA_PATH = os.path.join(PROJECT_ROOT, "dados_cartola", "03_visualizacoes")

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
    """Carrega e processa os resultados dos arquivos de backtest gerados pelo pipeline."""
    resultados = []
    padrao_arquivo = os.path.join(VISUALIZATION_DATA_PATH, "backtest_rodada_*.json")
    arquivos_backtest = sorted(glob.glob(padrao_arquivo), reverse=True)
    
    # Garante que apenas as 3 rodadas mais recentes sejam consideradas
    arquivos_backtest = arquivos_backtest[:3]
    
    if not arquivos_backtest:
        st.warning(f"Nenhum arquivo de resultado de backtest foi encontrado no padrão: {padrao_arquivo}. Execute o pipeline de dados, incluindo o script de backtest.")
        return []

    for arquivo in arquivos_backtest:
        try:
            match = re.search(r'backtest_rodada_(\d+)\.json', os.path.basename(arquivo))
            if not match:
                continue
            rodada_id = int(match.group(1))

            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                if dados:
                    resultados.append({'rodada_id': rodada_id, 'data': dados})
        except (json.JSONDecodeError, FileNotFoundError):
            st.error(f"Erro ao ler o arquivo de backtest: {arquivo}")
            continue
            
    resultados.sort(key=lambda x: x['rodada_id'], reverse=True)
    return resultados

def display_signal(sinal):
    """Exibe o sinal de trânsito com cor e ícone."""
    if sinal == "Verde":
        st.success("✅ Verde")
    elif sinal == "Amarelo":
        st.warning("⚠️ Amarelo")
    else:
        st.error("❌ Vermelho")

# --- Início da Exibição ---
resultados_backtest = carregar_resultados_backtest()

if not resultados_backtest:
    st.info("Execute o script `scripts/09_backtest.py` para gerar os dados de análise.")
else:
    st.header("Análise de Desempenho por Rodada")

    for resultado in resultados_backtest:
        rodada_id = resultado['rodada_id']
        recomendacoes = resultado.get('data', {})
        
        st.subheader(f"🔍 Rodada {rodada_id}")

        if not recomendacoes:
            st.write("Nenhuma recomendação foi gerada para esta rodada.")
            continue

        ordered_pos = ["Goleiro", "Lateral", "Zagueiro", "Meia", "Atacante", "Técnico"]
        cols = st.columns(len(ordered_pos))

        for i, pos_nome in enumerate(ordered_pos):
            if pos_nome in recomendacoes:
                jogador = recomendacoes[pos_nome]
                with cols[i]:
                    with st.container(border=True):
                        st.subheader(pos_nome)
                        st.markdown(f"**{jogador['apelido']}**")
                        
                        st.metric(
                            label="Pontuação Real",
                            value=f"{jogador['pontuacao_real']:.2f}"
                        )
                        
                        display_signal(jogador['sinal'])
        
        st.markdown("---")

st.info("""
**Como ler esta página:** Para cada rodada passada, mostramos o jogador que o modelo teria recomendado para cada posição. 
A "Pontuação Real" é o resultado que o jogador de fato alcançou. O sinal indica se a pontuação atingiu a meta definida para a posição.
""")
