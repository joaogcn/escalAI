import streamlit as st
from src.dados import load_plot
import pandas as pd
import json
import os

st.set_page_config(page_title="Análise Exploratória - EscalAI", layout="wide")

# Função para carregar os novos JSONs de dados
@st.cache_data
def load_json_data(file_name):
    path = os.path.join("dados_cartola", "03_visualizacoes", file_name)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

st.header("🔎 Análise Exploratória: O Processo")
st.markdown("Esta seção detalha o processo de análise de dados, desde a limpeza até a identificação de padrões e outliers.")

# ETAPAS 1 E 2
st.subheader("Etapas 1 e 2: Limpeza e Verificação dos Dados")
st.markdown("""
O processo inicial, executado pelos scripts `01_limpeza.py` e `02_verificacao.py`, consiste em:
- **Consolidar** dados de múltiplos anos em um único dataset.
- **Limpar** os dados, o que inclui renomear colunas, padronizar nomes e preencher valores ausentes (`NaN`) com `0`.
- **Verificar** a qualidade dos dados para garantir que a limpeza foi bem-sucedida.

O exemplo abaixo, usando o jogador David Braz (ID 50317), ilustra a transformação de `NaN` para `0` nas colunas de scout.
""")

try:
    path_raw_sample = os.path.join("dados_cartola", "raw", "2025", "rodada-11.csv")
    df_raw = pd.read_csv(path_raw_sample)
    jogador_raw = df_raw[df_raw['atletas.atleta_id'] == 50317]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Antes da Limpeza**")
        st.dataframe(jogador_raw[['atletas.apelido', 'CA', 'FC', 'FS']])
    with col2:
        st.markdown("**Depois da Limpeza**")
        data = {'apelido': ['David Braz'], 'CA': [0.0], 'FC': [0.0], 'FS': [0.0]}
        st.dataframe(pd.DataFrame(data).set_index('apelido'))

except Exception:
    st.warning("Arquivo de exemplo (`2025/rodada-11.csv`) não encontrado. Execute o pipeline para ver o exemplo.")

st.markdown("<hr>", unsafe_allow_html=True)

# ETAPA 3
st.subheader("Etapa 3: Análise Descritiva e Outliers")
st.markdown("Executada pelo `03_analise_descritiva.py`, esta etapa calcula as principais métricas estatísticas e identifica performances excepcionais (outliers).")

st.markdown("##### Estatísticas Descritivas")
stats_path = os.path.join("dados_cartola", "03_visualizacoes", 'estatisticas_descritivas.json')
if os.path.exists(stats_path):
    try:
        # O arquivo foi salvo com orient='table', o pandas pode lê-lo diretamente.
        df_stats = pd.read_json(stats_path, orient='table')
        st.dataframe(df_stats.style.format("{:.2f}"))
    except Exception as e:
        st.error(f"Erro ao ler o arquivo de estatísticas: {e}")
else:
    st.warning("Arquivo `estatisticas_descritivas.json` não encontrado. Execute o pipeline.")

outliers_data = load_json_data('outliers_pontuacao.json')
if outliers_data:
    st.markdown("##### Detecção de Outliers de Pontuação (Método IQR)")
    st.markdown("Jogadores com pontuações muito acima (positivos) ou abaixo (negativos) da média para sua posição em uma determinada rodada.")
    df_outliers = pd.DataFrame(outliers_data)
    
    if not df_outliers.empty:
        df_outliers_sorted = df_outliers.sort_values(by='pontos', ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top 5 Outliers Positivos**")
            st.dataframe(df_outliers_sorted.head(5))
        with col2:
            st.markdown("**Top 5 Outliers Negativos**")
            st.dataframe(df_outliers_sorted.tail(5).sort_values(by='pontos', ascending=True))
    else:
        st.info("Nenhum outlier de pontuação foi identificado nos dados processados.")
else:
    st.warning("Arquivo `outliers_pontuacao.json` não encontrado. Execute o pipeline.")

st.markdown("<hr>", unsafe_allow_html=True)

# ETAPA 4
st.subheader("Etapa 4: Análise Visual Exploratória")
st.markdown("Executada pelo `04_exploracao.py`, esta etapa gera os gráficos principais para entendermos as relações nos dados.")

fig_box_pos = load_plot('boxplot_pontos_posicao.json')
if fig_box_pos:
    st.plotly_chart(fig_box_pos, use_container_width=True)
else:
    st.warning("Gráfico `boxplot_pontos_posicao.json` não encontrado.")

fig_scatter_preco_pontos = load_plot('scatter_preco_pontos.json')
if fig_scatter_preco_pontos:
    st.plotly_chart(fig_scatter_preco_pontos, use_container_width=True)
else:
    st.warning("Gráfico `scatter_preco_pontos.json` não encontrado.")