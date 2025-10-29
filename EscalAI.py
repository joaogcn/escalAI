import streamlit as st

st.set_page_config(
    page_title="EscalAI - Início",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ EscalAI - Análise de Dados do Cartola FC")

st.header("Inteligência artificial para sua escalação no Cartola FC")
st.markdown("""
O **EscalAI** é uma aplicação web que une análise de dados e inteligência artificial para te ajudar a escalar seu time no **Cartola FC** com mais estratégia e confiança.
Explore nossas páginas na barra lateral para ter acesso a dashboards, dicas e um bot assistente!
""")

st.markdown("---")

st.header("✨ Funcionalidades")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Dashboard Interativo")
    st.write("Analise o desempenho dos jogadores na temporada através de gráficos e estatísticas descritivas.")

with col2:
    st.subheader("🎯 Dicas da Rodada")
    st.write("Receba recomendações dos melhores jogadores por posição e dos times que estão em melhor fase no campeonato, tudo baseado em nossos índices de desempenho.")

with col3:
    st.subheader("🤖 Bot EscalAI")
    st.write("Converse com nosso assistente com IA (Google Gemini) e peça dicas personalizadas. Ele tem acesso aos dados da rodada para te ajudar a montar o time ideal.")


st.markdown("---")

st.header("⚙️ Tecnologias Utilizadas")
st.markdown("""
-   **Python** -- Base de toda a aplicação
-   **Streamlit** -- Interface web interativa
-   **Pandas** -- Processamento e análise de dados
-   **Plotly** -- Visualizações dinâmicas
-   **Google Gemini** -- Inteligência artificial para o Bot assistente
-   **GitHub Actions** -- Automação e atualização contínua dos dados
""")

st.markdown("---")

st.info("💡 **Navegue pelas páginas na barra lateral e descubra insights que vão transformar sua escalação!**")
