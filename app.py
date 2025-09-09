import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
import glob
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="EscalAI - Cartola FC",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constantes ---
CARTOLA_BASE_URL = "https://api.cartolafc.globo.com"
DATA_PATH = "dados_cartola/raw"

# --- Funções de Carregamento de Dados ---

@st.cache_data(ttl=300)  # Cache de 5 minutos para dados ao vivo
def get_mercado_status():
    """Busca o status atual do mercado na API do Cartola."""
    try:
        response = requests.get(f"{CARTOLA_BASE_URL}/mercado/status")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=300)
def get_destaques():
    """Busca os jogadores mais escalados na API do Cartola."""
    try:
        response = requests.get(f"{CARTOLA_BASE_URL}/mercado/destaques")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

@st.cache_data
def load_historical_data(year, rodada):
    """Carrega os dados históricos de uma rodada específica a partir de um arquivo CSV local."""
    file_path = os.path.join(DATA_PATH, str(year), f"rodada-{rodada}.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

@st.cache_data
def get_available_years_and_rounds():
    """Verifica as pastas de dados para encontrar anos e rodadas disponíveis."""
    years = [d for d in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, d))]
    return sorted([int(y) for y in years if y.isdigit()], reverse=True)

# --- Interface Principal ---

def main():
    st.title("⚽ EscalAI - Análise de Dados do Cartola FC")
    st.markdown("---")

    # --- Sidebar ---
    with st.sidebar:
        st.header("🎛️ Navegação")
        page = st.selectbox(
            "Selecione a página:",
            ["🏠 Dashboard (Ao Vivo)", "👥 Análise de Jogadores (Histórico)", "🏆 Análise de Clubes (Histórico)"]
        )

        st.header("🔍 Filtros de Dados Históricos")
        available_years = get_available_years_and_rounds()
        if not available_years:
            st.warning("Nenhum dado histórico encontrado. Execute a Action para sincronizar.")
            year = 2024
            rodada = 1
        else:
            year = st.selectbox("Temporada:", available_years)
            rodada = st.number_input("Rodada:", min_value=1, max_value=38, value=1)

    # Carregar dados históricos com base na seleção da sidebar
    df_historical = load_historical_data(year, rodada)

    # --- Navegação das Páginas ---
    if page == "🏠 Dashboard (Ao Vivo)":
        show_dashboard()
    elif page == "👥 Análise de Jogadores (Histórico)":
        show_jogadores_page(df_historical)
    elif page == "🏆 Análise de Clubes (Histórico)":
        show_clubes_page(df_historical)

# --- Páginas da Aplicação ---

def show_dashboard():
    """Página inicial com dados ao vivo do mercado."""
    st.header("🏠 Dashboard do Mercado (Dados ao Vivo)")

    st.subheader("📊 Status do Mercado")
    mercado_status = get_mercado_status()
    if mercado_status:
        col1, col2, col3, col4 = st.columns(4)
        status_map = {1: "Aberto", 2: "Fechado", 3: "Em atualização", 4: "Manutenção"}
        status_mercado_id = mercado_status.get('status_mercado', 0)
        col1.metric("Status", status_map.get(status_mercado_id, "N/A"))
        col2.metric("Rodada Atual", mercado_status.get('rodada_atual', 'N/A'))
        col3.metric("Times Escalados", f"{mercado_status.get('times_escalados', 0):,}")
        col4.metric("Fechamento", datetime.fromtimestamp(mercado_status.get('fechamento', {}).get('timestamp', 0)).strftime('%d/%m %H:%M'))
    else:
        st.warning("Não foi possível carregar o status do mercado.")

    st.subheader("🌟 Destaques do Mercado")
    destaques = get_destaques()
    if destaques and 'atletas' in destaques:
        for atleta in destaques['atletas']:
            st.write(f"- **{atleta['Atleta']['apelido']}** ({atleta['clube']}): {atleta['escalacoes']:,} escalações")
    else:
        st.info("Nenhum destaque disponível.")

def show_jogadores_page(df):
    """Página para análise de jogadores com base em dados históricos."""
    st.header("👥 Análise de Jogadores (Dados Históricos)")

    if df is None:
        st.error("Dados para a temporada e rodada selecionadas não encontrados. Verifique a pasta `dados_cartola/raw`.")
        return

    st.dataframe(df)

    st.subheader("Filtros Avançados")
    col1, col2, col3 = st.columns(3)
    posicoes = ["Todas"] + df['atletas.posicao_id'].unique().tolist()
    clubes = ["Todos"] + df['atletas.clube.id.full.name'].unique().tolist()

    posicao_filtro = col1.selectbox("Posição:", posicoes)
    clube_filtro = col2.selectbox("Clube:", clubes)
    min_preco = col3.slider("Preço Mínimo:", float(df['atletas.preco_num'].min()), float(df['atletas.preco_num'].max()))

    df_filtrado = df[df['atletas.preco_num'] >= min_preco]
    if posicao_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado['atletas.posicao_id'] == posicao_filtro]
    if clube_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['atletas.clube.id.full.name'] == clube_filtro]

    st.write(f"**Mostrando {len(df_filtrado)} de {len(df)} jogadores.**")
    st.dataframe(df_filtrado)

    st.subheader("Visualizações")
    col1, col2 = st.columns(2)
    fig_preco = px.histogram(df_filtrado, x="atletas.preco_num", title="Distribuição de Preços")
    col1.plotly_chart(fig_preco, use_container_width=True)

    fig_pontos = px.histogram(df_filtrado, x="atletas.pontos_num", title="Distribuição de Pontos")
    col2.plotly_chart(fig_pontos, use_container_width=True)

def show_clubes_page(df):
    """Página para análise de clubes com base em dados históricos."""
    st.header("🏆 Análise de Clubes (Dados Históricos)")

    if df is None:
        st.error("Dados para a temporada e rodada selecionadas não encontrados.")
        return

    st.subheader("Jogadores por Clube")
    clubes_count = df['atletas.clube.id.full.name'].value_counts()
    fig = px.bar(clubes_count, x=clubes_count.index, y=clubes_count.values, title="Número de Jogadores por Clube")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Média de Pontos por Clube")
    media_pontos_clube = df.groupby('atletas.clube.id.full.name')['atletas.pontos_num'].mean().sort_values(ascending=False)
    st.dataframe(media_pontos_clube)

if __name__ == "__main__":
    main()