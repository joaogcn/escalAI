import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Dashboard de Análise",
    page_icon="⚽",
    layout="wide"
)

CONSOLIDATED_OUTPUT_FILE = 'dados_cartola/02_intermediate/dados_consolidados.parquet'
AGGREGATED_OUTPUT_FILE = 'dados_cartola/02_intermediate/dados_agregados_por_atleta.parquet'

@st.cache_data
def load_data():
    if not os.path.exists(CONSOLIDATED_OUTPUT_FILE) or not os.path.exists(AGGREGATED_OUTPUT_FILE):
        st.error("Arquivos de dados não encontrados. Execute o pipeline de dados primeiro.")
        return None, None
    
    df_consolidado = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    df_agregado = pd.read_parquet(AGGREGATED_OUTPUT_FILE)
    return df_consolidado, df_agregado

df_consolidado, df_agregado = load_data()

if df_consolidado is not None and df_agregado is not None:
    st.title("Dashboard Interativo - EscalAI")
    st.markdown("Explore os dados históricos do Cartola FC para tomar as melhores decisões.")

    st.sidebar.header("Filtros")
    
    anos = sorted(df_consolidado['ano'].unique(), reverse=True)
    ano_selecionado = st.sidebar.selectbox("Selecione o Ano", anos)

    posicoes = ['Todas'] + sorted(df_agregado['posicao'].unique())
    posicao_selecionada = st.sidebar.selectbox("Selecione a Posição", posicoes)

    clubes = ['Todos'] + sorted(df_consolidado['clube.nome'].dropna().unique())
    clube_selecionado = st.sidebar.selectbox("Selecione o Clube", clubes)

    df_agregado_filtrado = df_agregado.copy()
    if posicao_selecionada != 'Todas':
        df_agregado_filtrado = df_agregado_filtrado[df_agregado_filtrado['posicao'] == posicao_selecionada]
    if clube_selecionado != 'Todos':
        df_agregado_filtrado = df_agregado_filtrado[df_agregado_filtrado['ultimo_clube'] == clube_selecionado]

    df_consolidado_filtrado = df_consolidado[df_consolidado['ano'] == ano_selecionado]

    atletas_do_ano = df_consolidado_filtrado['atleta_id'].unique()
    df_agregado_filtrado = df_agregado_filtrado[df_agregado_filtrado['atleta_id'].isin(atletas_do_ano)]

    if posicao_selecionada != 'Todas':
        df_consolidado_filtrado = df_consolidado_filtrado[df_consolidado_filtrado['posicao_id'] == posicao_selecionada]
    if clube_selecionado != 'Todos':
        df_consolidado_filtrado = df_consolidado_filtrado[df_consolidado_filtrado['clube.nome'] == clube_selecionado]


    fig_custo_beneficio = px.scatter(
        df_agregado_filtrado,
        x='media_preco',
        y='media_pontos',
        color='posicao',
        hover_name='apelido',
        size='jogos_disputados',
        title='Preço Médio vs. Média de Pontos (Tamanho da bola indica jogos disputados)',
        labels={'media_preco': 'Preço Médio (C$)', 'media_pontos': 'Média de Pontos'}
    )
    st.plotly_chart(fig_custo_beneficio, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        fig_boxplot_posicao = px.box(
            df_consolidado_filtrado[df_consolidado_filtrado['pontos_num'] != 0],
            x='posicao_id',
            y='pontos_num',
            color='posicao_id',
            title=f'Distribuição de Pontos por Posição em {ano_selecionado}',
            labels={'posicao_id': 'Posição', 'pontos_num': 'Pontos na Rodada'}
        )
        st.plotly_chart(fig_boxplot_posicao, use_container_width=True)

    with col2:
        fig_hist_pontos = px.histogram(
            df_consolidado_filtrado,
            x='pontos_num',
            nbins=50,
            title=f'Distribuição de Pontuações em {ano_selecionado}',
            labels={'pontos_num': 'Pontos na Rodada'}
        )
        st.plotly_chart(fig_hist_pontos, use_container_width=True)

else:
    st.info("Aguardando a geração dos arquivos de dados...")
