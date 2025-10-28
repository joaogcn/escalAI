import streamlit as st
import json
import os
import pandas as pd
import sys

# Adiciona o diretório raiz ao sys.path para encontrar o módulo src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import VISUALIZATION_DATA_PATH

st.set_page_config(
    page_title="Recomendações de Jogadores",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Melhores Jogadores para Escalar")

st.markdown("""
Esta página apresenta os jogadores com maior potencial de pontuação para a próxima rodada, com base no **Índice EscalAI**.

O índice combina o **desempenho recente (últimas 5 partidas)** com a **média geral** do jogador na temporada, 
fornecendo uma visão equilibrada entre o momento atual e a consistência.
""")

# Carrega os dados de recomendações
recomendacoes_path = os.path.join(VISUALIZATION_DATA_PATH, 'recomendacoes_por_posicao.json')

if not os.path.exists(recomendacoes_path):
    st.error("Arquivo de recomendações não encontrado. Execute o pipeline de dados primeiro.")
    st.stop()

with open(recomendacoes_path, 'r', encoding='utf-8') as f:
    recomendacoes = json.load(f)

# --- Storytelling dos Jogadores ---

for posicao, jogadores in recomendacoes.items():
    if not jogadores:
        continue

    st.header(f"{posicao}s")
    
    cols = st.columns(5)
    
    for i, jogador in enumerate(jogadores):
        with cols[i]:
            st.subheader(jogador['apelido'])
            st.caption(f"{jogador['clube.nome']}")
            
            st.metric(
                label="Índice EscalAI",
                value=f"{jogador['indice_escalai']:.2f}"
            )
            
            st.metric(
                label="Média (Últimas 5 Partidas)",
                value=f"{jogador['media_ultimas_5']:.2f}"
            )

            st.metric(
                label="Preço (C$)",
                value=f"{jogador['preco_num']:.2f}"
            )

            # Pequena narrativa
            if jogador['media_ultimas_5'] > jogador['media_geral'] + 1:
                st.info("🔥 Em grande fase!", icon="📈")
            elif jogador['preco_num'] < 8:
                st.success("💰 Ótimo custo-benefício!", icon="👍")
            else:
                st.write("Regularidade e confiança.")

    st.markdown("---")
