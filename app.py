import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
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
CONSOLIDATED_DATA_PATH = "dados_cartola/02_intermediate/dados_consolidados.parquet"
AGGREGATED_DATA_PATH = "dados_cartola/02_intermediate/dados_agregados_por_atleta.parquet" # Novo

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

@st.cache_data
def load_data():
    """Carrega os dados consolidados a partir do arquivo Parquet."""
    if os.path.exists(CONSOLIDATED_DATA_PATH):
        return pd.read_parquet(CONSOLIDATED_DATA_PATH)
    return None

@st.cache_data
def load_aggregated_data():
    """Carrega os dados agregados por atleta."""
    if os.path.exists(AGGREGATED_DATA_PATH):
        return pd.read_parquet(AGGREGATED_DATA_PATH)
    return None

def get_available_rounds(df):
    """Gera a lista de rodadas disponíveis a partir do DataFrame consolidado."""
    if df is None or 'ano' not in df or 'rodada_id' not in df:
        return []
    
    rounds = df[['ano', 'rodada_id']].drop_duplicates().sort_values(
        by=['ano', 'rodada_id'], ascending=[False, False]
    )
    return [f"{int(ano)} - Rodada {int(rodada_id)}" for ano, rodada_id in rounds.itertuples(index=False)]


# --- Interface Principal ---

def main():
    st.title("⚽ EscalAI - Análise de Dados do Cartola FC")
    st.markdown("---")

    df_consolidado = load_data()

    with st.sidebar:
        st.header("🎛️ Navegação")
        page = st.selectbox(
            "Selecione a página:",
            ["🏠 Dashboard (Ao Vivo)", "📊 Análise Agregada", "👥 Análise de Jogadores (Histórico)", "🏆 Análise de Clubes (Histórico)"]
        )

        st.header("🔍 Filtro de Dados Históricos")
        
        year = None
        rodada = None
        df_historical = pd.DataFrame()

        if df_consolidado is None:
            st.warning("Arquivo de dados consolidados não encontrado. Execute o script de limpeza primeiro.")
        else:
            available_rounds = get_available_rounds(df_consolidado)
            if not available_rounds:
                st.warning("Nenhuma rodada encontrada nos dados consolidados.")
            else:
                selected_round_str = st.selectbox("Temporada e Rodada:", available_rounds)
                if selected_round_str:
                    year_str, rodada_str = selected_round_str.split(" - Rodada ")
                    year = int(year_str)
                    rodada = int(rodada_str)
                    
                    df_historical = df_consolidado[(df_consolidado['ano'] == year) & (df_consolidado['rodada_id'] == rodada)].copy()

    if page == "🏠 Dashboard (Ao Vivo)":
        show_dashboard()
    elif page == "📊 Análise Agregada":
        show_aggregated_analysis_page(df_consolidado) # Passa o df original para o boxplot
    elif page == "👥 Análise de Jogadores (Histórico)":
        if not df_historical.empty:
            show_jogadores_page(df_historical)
        else:
            st.info("Selecione uma temporada e rodada para ver a análise dos jogadores.")
    elif page == "🏆 Análise de Clubes (Histórico)":
        if not df_historical.empty:
            show_clubes_page(df_historical)
        else:
            st.info("Selecione uma temporada e rodada para ver a análise dos clubes.")


# --- Páginas da Aplicação ---

def show_dashboard():
    """Página inicial com dados ao vivo do mercado."""
    st.header("🏠 Dashboard do Mercado (Dados ao Vivo)")
    # ... (código existente sem alteração)
    mercado_status = get_mercado_status()
    if mercado_status:
        col1, col2, col3, col4 = st.columns(4)
        status_map = {1: "Aberto", 2: "Fechado", 3: "Em atualização", 4: "Manutenção"}
        status_mercado_id = mercado_status.get('status_mercado', 0)
        col1.metric("Status", status_map.get(status_mercado_id, "N/A"))
        col2.metric("Rodada Atual", mercado_status.get('rodada_atual', 'N/A'))
        col3.metric("Times Escalados", f"{mercado_status.get('times_escalados', 0):,}")
        
        fechamento_ts = mercado_status.get('fechamento', {}).get('timestamp', 0)
        if fechamento_ts > 0:
            fechamento_str = datetime.fromtimestamp(fechamento_ts).strftime('%d/%m %H:%M')
        else:
            fechamento_str = "N/A"
        col4.metric("Fechamento", fechamento_str)
    else:
        st.warning("Não foi possível carregar o status do mercado.")


def show_aggregated_analysis_page(df_original):
    """Nova página para mostrar as análises agregadas por jogador."""
    st.header("📊 Análise Agregada por Jogador")
    
    df_agg = load_aggregated_data()

    if df_agg is None:
        st.error("Arquivo de dados agregados não encontrado! Por favor, execute o script 'scripts/02_analise_exploratoria.py' primeiro.")
        return

    st.markdown("""
    Esta página analisa o desempenho consolidado dos jogadores ao longo de todas as temporadas e rodadas disponíveis nos dados. 
    Use os filtros para encontrar os jogadores mais consistentes e com o melhor custo-benefício.
    """)

    min_jogos = st.slider("Filtrar por número mínimo de jogos disputados:", 1, int(df_agg['jogos_disputados'].max()), 10)
    df_filtrado = df_agg[df_agg['jogos_disputados'] >= min_jogos]

    st.markdown("---")

    # Gráficos
    st.subheader("🏆 Top 20 Jogadores por Média de Pontos")
    top_20_media = df_filtrado.nlargest(20, 'media_pontos')
    fig1 = px.bar(top_20_media, x='apelido', y='media_pontos', title="Top 20 Jogadores por Média de Pontos",
                  hover_data=['posicao', 'ultimo_clube', 'jogos_disputados'], labels={'apelido': 'Jogador', 'media_pontos': 'Média de Pontos'})
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("💰 Top 20 Jogadores por Custo-Benefício Médio")
    top_20_custo_beneficio = df_filtrado.nlargest(20, 'custo_beneficio_medio')
    fig2 = px.bar(top_20_custo_beneficio, x='apelido', y='custo_beneficio_medio', title="Top 20 Jogadores por Custo-Benefício Médio",
                  hover_data=['posicao', 'ultimo_clube', 'media_pontos', 'media_preco'], labels={'apelido': 'Jogador', 'custo_beneficio_medio': 'Custo-Benefício (Média Pontos / Média Preço)'})
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🔍 Preço Médio vs. Média de Pontos")
    fig3 = px.scatter(df_filtrado, x='media_preco', y='media_pontos', color='posicao',
                      title="Preço Médio vs. Média de Pontos por Posição",
                      hover_data=['apelido'], labels={'media_preco': 'Preço Médio (C$)', 'media_pontos': 'Média de Pontos'})
    st.plotly_chart(fig3, use_container_width=True)
    
    st.subheader("📊 Distribuição de Pontos por Posição (Dados não agregados)")
    if df_original is not None:
        fig4 = px.box(df_original, x='posicao_id', y='pontos_num', color='posicao_id',
                      title="Distribuição de Pontos por Posição",
                      labels={'posicao_id': 'Posição', 'pontos_num': 'Pontos na Rodada'})
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("Não foi possível carregar os dados originais para o Box Plot.")


def show_jogadores_page(df):
    """Página para análise de jogadores com base em dados históricos."""
    st.header("👥 Análise de Jogadores (Dados Históricos)")
    # ... (código existente sem alteração)
    if df.empty:
        st.error("Dados para a temporada e rodada selecionadas não encontrados.")
        return

    st.subheader("Filtros Avançados")
    col1, col2, col3 = st.columns(3)
    
    posicoes = ["Todas"] + df['posicao_id'].unique().tolist()
    clubes = ["Todos"] + df['clube.nome'].unique().tolist()

    posicao_filtro = col1.selectbox("Posição:", posicoes)
    clube_filtro = col2.selectbox("Clube:", clubes)
    min_preco = col3.slider("Preço Mínimo:", float(df['preco_num'].min()), float(df['preco_num'].max()))

    df_filtrado = df[df['preco_num'] >= min_preco]
    if posicao_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado['posicao_id'] == posicao_filtro]
    if clube_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['clube.nome'] == clube_filtro]

    st.write(f"**Mostrando {len(df_filtrado)} de {len(df)} jogadores.**")
    
    cols_to_hide = [
        'Unnamed: 0', 'foto', 'slug', 'atleta_id', 'clube_id', 
        'minimo_para_valorizar', 'apelido_abreviado', 'temporada_id', 'PI',
        'gato_mestre.media_pontos_mandante', 'gato_mestre.media_pontos_visitante',
        'gato_mestre.media_minutos_jogados', 'gato_mestre.minutos_jogados'
    ]
    cols_to_hide_existing = [col for col in cols_to_hide if col in df_filtrado.columns]
    
    st.dataframe(df_filtrado.drop(columns=cols_to_hide_existing))

    st.subheader("Visualizações")
    col1, col2 = st.columns(2)
    fig_preco = px.histogram(df_filtrado, x="preco_num", title="Distribuição de Preços")
    col1.plotly_chart(fig_preco, use_container_width=True)

    fig_pontos = px.histogram(df_filtrado, x="pontos_num", title="Distribuição de Pontos")
    col2.plotly_chart(fig_pontos, use_container_width=True)


def show_clubes_page(df):
    """Página para análise de clubes com base em dados históricos."""
    st.header("🏆 Análise de Clubes (Dados Históricos)")
    # ... (código existente sem alteração)
    if df.empty:
        st.error("Dados para a temporada e rodada selecionadas não encontrados.")
        return

    st.subheader("Jogadores por Clube")
    clubes_count = df['clube.nome'].value_counts()
    fig = px.bar(clubes_count, x=clubes_count.index, y=clubes_count.values, title="Número de Jogadores por Clube")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Média de Pontos por Clube")
    media_pontos_clube = df.groupby('clube.nome')['pontos_num'].mean().sort_values(ascending=False)
    st.dataframe(media_pontos_clube)

if __name__ == "__main__":
    main()
