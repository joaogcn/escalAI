import streamlit as st

st.set_page_config(
    page_title="Sobre o Projeto",
    page_icon="ℹ️",
    layout="wide"
)

st.title("ℹ️ Sobre o Projeto")

st.header("Inteligência artificial para sua escalação no Cartola FC")
st.markdown("""
O **EscalAI** é uma aplicação web que une análise de dados e inteligência artificial para te ajudar a escalar seu time no **Cartola FC** com mais estratégia e confiança.
Explore nossas páginas na barra lateral para ter acesso a dashboards, dicas e um bot assistente!
""")

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

st.header("🛠️ Como o Projeto é Feito?")
st.markdown("""
O EscalAI é construído sobre um pipeline de dados robusto e automatizado, que transforma dados brutos em insights valiosos. O processo pode ser dividido em três etapas principais:

**1. Coleta e Limpeza de Dados:**
-   Os dados históricos das últimas temporadas são coletados de um repositório público no GitHub (`henriquepgomide/caRtola`).
-   Dados em tempo real, como o status dos jogadores (provável, dúvida, etc.) e os confrontos da rodada, são buscados diretamente da API oficial do Cartola FC.
-   Um script de limpeza (`01_limpeza.py`) unifica esses dados, padroniza nomes, trata valores ausentes e salva o resultado em um formato eficiente (Parquet).

**2. Análise e Geração de Insights:**
-   Com os dados limpos, uma sequência de scripts de análise é executada:
    -   **Índice EscalAI:** Calculamos um índice de desempenho que pondera a média de pontos recente (últimas 5 partidas) e a consistência do jogador na temporada.
    -   **Previsão de "Mitada":** Um modelo de *Machine Learning* (Random Forest) é treinado com dados históricos para prever quais jogadores têm o maior potencial de pontuação na rodada.
    -   **Análise de Times:** Avaliamos o desempenho recente das equipes (últimas 5 rodadas) com base em vitórias, gols e saldo de gols para identificar times em boa fase.

**3. Visualização e Interação:**
-   Todos os dados e insights gerados são salvos em arquivos JSON e Parquet.
-   A aplicação **Streamlit** lê esses arquivos para alimentar os dashboards, as tabelas e as páginas de dicas.
-   O **Bot EscalAI** utiliza os arquivos de dicas como contexto para que a Inteligência Artificial (Google Gemini) possa fornecer respostas personalizadas e precisas.

Todo esse pipeline é orquestrado pelo script `scripts/run_pipeline.py` e é executado automaticamente por meio do **GitHub Actions**, garantindo que os dados estejam sempre atualizados com as informações mais recentes do Cartola FC.
""")

st.markdown("---")

st.header("👥 Equipe do Projeto")
st.markdown("""
- [João Guilherme Carvalho Neto](https://www.linkedin.com/in/joaogcneto/)
- [Felipe Domingos Vital](https://www.linkedin.com/in/felipe-vital-392820181/)
- [Felipe Moraes](https://www.linkedin.com/in/felipe-moraes-6b58441b9/)
- [Laudemir Duarte da Silva Júnior](https://www.linkedin.com/in/laudemirjr/)
- Luiz Lobato
- [Victorino Bezerra](https://www.linkedin.com/in/victorino-bezerra-6527b3353/)
- [Filipe Novaes Maia Correia](https://www.linkedin.com/in/fnmc/)
""")

st.markdown("---")

st.info("💡 **Navegue pelas páginas na barra lateral e descubra insights que vão transformar sua escalação!**")
