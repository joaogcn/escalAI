import streamlit as st

st.set_page_config(
    page_title="EscalAI - Início",
    page_icon="⚽",
    layout="wide"  
)

st.title("⚽ EscalAI - Análise de Dados do Cartola FC")

st.header("Inteligência para sua escalação no Cartola FC")
st.markdown("""
O **EscalAI** é uma aplicação web desenvolvida em **Streamlit** que combina tecnologia e análise de dados para ajudar você a montar seu time do **Cartola FC** com mais estratégia e confiança.
Com base em dados históricos e informações de mercado em tempo real, o EscalAI oferece uma visão completa do desempenho dos jogadores e das tendências da rodada.
""")

st.markdown("---")

st.header("🔍 Como Funciona")
st.markdown("""
1.  **Dados Históricos**
    O EscalAI utiliza informações de temporadas anteriores obtidas do projeto [caRtola](https://github.com/henriquepgomide/caRtola), permitindo análises detalhadas de desempenho e evolução dos atletas.

2.  **Atualização Automática**
    Sem necessidade de intervenção manual, uma rotina automatizada mantém os dados sempre atualizados, garantindo que as análises estejam alinhadas com as informações mais recentes.

3.  **Análises em Tempo Real**
    O sistema também consome **APIs oficiais do Cartola FC**, trazendo status de mercado, jogadores mais escalados e outras informações em tempo real para decisões mais assertivas.
""")

st.markdown("---")

st.header("⚙️ Tecnologias")
st.markdown("""
-   **Python** -- Base de toda a aplicação
-   **Streamlit** -- Interface simples, interativa e intuitiva
-   **Pandas** -- Processamento e análise de dados
-   **Plotly** -- Visualizações dinâmicas e interativas
-   **GitHub Actions** -- Automação e atualização contínua dos dados
""")

st.markdown("---")

st.markdown("""
🤖 **Em breve:** o EscalAI contará com um **bot inteligente** que vai te ajudar a montar a melhor escalação possível, sugerindo jogadores e estratégias personalizadas para cada rodada!
""")

st.markdown("---")

st.info("💡 **Acesse o Dashboard na barra lateral e descubra insights que vão transformar sua escalação!**")