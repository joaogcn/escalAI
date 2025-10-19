import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Top 10 Jogadores",
    page_icon="🏆",
    layout="wide"
)

# Caminhos para os arquivos de dados
CONSOLIDATED_OUTPUT_FILE = 'dados_cartola/02_intermediate/dados_consolidados.parquet'
AGGREGATED_OUTPUT_FILE = 'dados_cartola/02_intermediate/dados_agregados_por_atleta.parquet'

# Função para carregar os dados com cache
@st.cache_data
def load_data():
    df_consolidado = pd.read_parquet(CONSOLIDATED_OUTPUT_FILE)
    df_agregado = pd.read_parquet(AGGREGATED_OUTPUT_FILE)
    return df_consolidado, df_agregado

# Carregar os dados
df_consolidado, df_agregado = load_data()

st.title("🏆 Top 10 Jogadores")
st.markdown("Explore os jogadores com melhores desempenhos e custo-benefício.")

# --- Filtros na barra lateral ---
st.sidebar.header("Filtros")

# Filtro de Ano
anos = sorted(df_consolidado['ano'].unique(), reverse=True)
ano_selecionado = st.sidebar.selectbox("Selecione o Ano", anos)

# Filtro de Posição
posicoes = ['Todas'] + sorted(df_agregado['posicao'].unique())
posicao_selecionada = st.sidebar.selectbox("Selecione a Posição", posicoes)

# Filtro de Clube
clubes = ['Todos'] + sorted(df_consolidado['clube.nome'].dropna().unique())
clube_selecionado = st.sidebar.selectbox("Selecione o Clube", clubes)

# Filtrar dados com base nas seleções
df_agregado_filtrado = df_agregado.copy()
if posicao_selecionada != 'Todas':
    df_agregado_filtrado = df_agregado_filtrado[df_agregado_filtrado['posicao'] == posicao_selecionada]
if clube_selecionado != 'Todos':
    df_agregado_filtrado = df_agregado_filtrado[df_agregado_filtrado['ultimo_clube'] == clube_selecionado]

df_consolidado_filtrado = df_consolidado[df_consolidado['ano'] == ano_selecionado]

# Filtra o df_agregado para incluir apenas atletas que jogaram no ano selecionado
atletas_do_ano = df_consolidado_filtrado['atleta_id'].unique()
df_agregado_filtrado = df_agregado_filtrado[df_agregado_filtrado['atleta_id'].isin(atletas_do_ano)]

# Filtro para número mínimo de jogos
min_jogos = st.slider("Número Mínimo de Jogos Disputados", min_value=1, max_value=int(df_agregado_filtrado['jogos_disputados'].max()), value=10)
df_agregado_filtrado = df_agregado_filtrado[df_agregado_filtrado['jogos_disputados'] >= min_jogos]



# --- Tabelas ---
st.header("Jogadores por Média de Pontos")

# Tabela com Top 10 jogadores por média de pontos
top_10_media = df_agregado_filtrado.nlargest(10, 'media_pontos')[['apelido', 'posicao', 'ultimo_clube', 'media_pontos', 'media_preco', 'jogos_disputados']]
st.dataframe(top_10_media.style.format({'media_pontos': '{:.2f}', 'media_preco': '{:.2f}'}), use_container_width=True)

st.header("Jogadores por Custo-Benefício")

df_custo_beneficio = df_agregado_filtrado

# Selecionar colunas de scouts
scout_cols = [col for col in df_custo_beneficio.columns if col.startswith('total_')]

# Colunas para exibir
cols_to_show = ['apelido', 'posicao', 'ultimo_clube', 'custo_beneficio_medio', 'media_pontos', 'media_preco', 'jogos_disputados'] + scout_cols

format_dict = {
    'custo_beneficio_medio': '{:.2f}',
    'media_pontos': '{:.2f}',
    'media_preco': '{:.2f}'
}
for col in scout_cols:
    format_dict[col] = '{:.0f}'

st.dataframe(df_custo_beneficio[cols_to_show].sort_values(by='custo_beneficio_medio', ascending=False).style.format(format_dict), use_container_width=True)
