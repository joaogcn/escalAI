import streamlit as st

st.set_page_config(page_title="Início - EscalAI", layout="wide")

st.title("⚽ Bem-vindo ao EscalAI!")
st.markdown("--- ")

st.header("🎯 Sobre o Projeto")
st.markdown("""
O **EscalAI** é uma aplicação web desenvolvida para análise de dados do Cartola FC. O projeto combina dados históricos para estudos de desempenho com a possibilidade de análises detalhadas, fornecendo uma ferramenta completa para auxiliar na escalação de times.

Este projeto foi desenvolvido como parte de uma avaliação acadêmica, com o objetivo de aplicar conceitos de engenharia de software, processamento de dados e visualização de informações em um caso de uso prático e de interesse geral.
""")

st.header("🛠️ Como Navegar")
st.markdown("""
Use o menu na barra lateral para navegar entre as diferentes seções da aplicação:

- **Análise Exploratória (O Processo):** Entenda o passo a passo de como os dados são limpos, processados e analisados.
- **Análise Agregada (Jogadores):** Explore o desempenho consolidado dos jogadores ao longo de todas as temporadas, com filtros interativos.
""")

st.info("Os dados utilizados neste projeto são obtidos do repositório público [caRtola](https://github.com/henriquepgomide/caRtola), que consolida informações históricas do Cartola FC.")