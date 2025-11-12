import streamlit as st
import json
import os
import sys
import google.generativeai as genai

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import VISUALIZATION_DATA_PATH

st.set_page_config(
    page_title="Bot EscalAI",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Bot EscalAI")
st.caption("Seu assistente pessoal para escalar o time perfeito no Cartola FC.")


if 'GEMINI_API_KEY' in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("A chave `GEMINI_API_KEY` não foi encontrada nos seus Secrets do Streamlit.")
    st.info("Para rodar localmente, crie um arquivo .streamlit/secrets.toml e adicione a chave. Para deploy, configure os Secrets no painel do Streamlit Cloud.")
    st.stop()

try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Erro ao configurar a API do Gemini. Verifique se a chave é válida. Detalhe: {e}")
    st.stop()

@st.cache_data
def load_context():
    """Carrega os dados de dicas para fornecer contexto ao bot."""
    recomendacoes_path = os.path.join(VISUALIZATION_DATA_PATH, 'recomendacoes_por_posicao.json')
    times_path = os.path.join(VISUALIZATION_DATA_PATH, 'times_para_ficar_de_olho.json')
    mitada_path = os.path.join(VISUALIZATION_DATA_PATH, 'recomendacao_mitada.json')
    context_parts = []

    try:
        with open(mitada_path, 'r', encoding='utf-8') as f:
            context_parts.append("## Dicas de Mitada para a Rodada (Previsão de Alto Potencial):\n" + f.read())
    except FileNotFoundError:
        context_parts.append("Arquivo de dicas de mitada não encontrado.")

    try:
        with open(recomendacoes_path, 'r', encoding='utf-8') as f:
            context_parts.append("## Dicas de Jogadores para a Rodada (Índice EscalAI):\n" + f.read())
    except FileNotFoundError:
        context_parts.append("Arquivo de recomendação de jogadores não encontrado.")
    try:
        with open(times_path, 'r', encoding='utf-8') as f:
            context_parts.append("## Dicas de Times para a Rodada:\n" + f.read())
    except FileNotFoundError:
        context_parts.append("Arquivo de times para ficar de olho não encontrado.")
    return "\n".join(context_parts)


if "chat" not in st.session_state:
    model = genai.GenerativeModel('gemini-pro-latest')
    contexto_dicas = load_context()
    system_prompt = (
        f"Você é o EscalAI, um assistente especialista em Cartola FC. "
        f"Sua personalidade é amigável e direta. Use os dados de contexto abaixo para basear suas respostas. "
        f"Diferencie os tipos de dicas: as 'Dicas de Mitada' são previsões de um modelo de machine learning, sendo apostas mais arriscadas e com alto potencial. As 'Dicas de Jogadores (Índice EscalAI)' são baseadas em consistência e desempenho recente, sendo escolhas mais seguras. "
        f"Não mencione os arquivos JSON, apenas use os dados deles.\n\n" 
        f"--- CONTEXTO DA RODADA ---\n{contexto_dicas}"
    )
    st.session_state.chat = model.start_chat(history=[
        {'role': 'user', 'parts': [system_prompt]},
        {'role': 'model', 'parts': ["Olá! Sou o EscalAI. Tenho acesso às últimas dicas de jogadores e times. Como posso te ajudar a escalar seu time hoje?"]}
    ])

for message in st.session_state.chat.history[1:]:
    with st.chat_message(message.role):
        st.markdown(message.parts[0].text)

if prompt := st.chat_input("Me peça uma dica de escalação!"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando as melhores dicas para você..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                response_text = response.text
                st.markdown(response_text)
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar a resposta: {e}")