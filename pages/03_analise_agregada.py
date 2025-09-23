import streamlit as st
from src.dados import load_parquet_data, get_current_season_players

st.set_page_config(page_title="Análise Agregada - EscalAI", layout="wide")

st.header("📊 Análise Agregada (Jogadores Ativos)")

df_agg_historico = load_parquet_data('dados_agregados_por_atleta.parquet')
atletas_atuais = get_current_season_players()

if df_agg_historico is None:
    st.stop()

if not atletas_atuais:
    st.warning("Não foi possível buscar a lista de atletas da temporada atual. A análise pode incluir jogadores inativos.")
    df_agg_filtrado = df_agg_historico
else:    
    apelidos_atuais = {atleta['apelido'] for atleta in atletas_atuais}
    
    df_agg_filtrado = df_agg_historico[df_agg_historico['apelido'].isin(apelidos_atuais)]
    st.info(f"A análise considera o histórico de todos os tempos, mas exibe apenas os **{len(df_agg_filtrado)}** jogadores que estão ativos na temporada atual.")


st.markdown("Use os filtros para encontrar os jogadores mais consistentes e com o melhor custo-benefício ao longo do tempo.")
min_jogos = st.slider("Filtrar por número mínimo de jogos disputados (histórico):", 
                    min_value=1, 
                    max_value=int(df_agg_filtrado['jogos_disputados'].max()), 
                    value=10)

df_final = df_agg_filtrado[df_agg_filtrado['jogos_disputados'] >= min_jogos]

st.markdown("--- ")

st.subheader("🏆 Top 20 Jogadores por Média de Pontos")
st.dataframe(df_final.nlargest(20, 'media_pontos'))

st.subheader("💰 Top 20 Jogadores por Custo-Benefício Médio")
st.dataframe(df_final.nlargest(20, 'custo_beneficio_medio'))