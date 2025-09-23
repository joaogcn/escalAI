import streamlit as st
import pandas as pd
import plotly.io as pio
import requests
import os
from src.config import CARTOLA_BASE_URL, INTERMEDIATE_DATA_PATH, VISUALIZATION_DATA_PATH

@st.cache_data(ttl=300)
def get_mercado_status():
    """Busca o status atual do mercado na API do Cartola."""
    try:
        response = requests.get(f"{CARTOLA_BASE_URL}/mercado/status")
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException:
        return None

@st.cache_data
def load_parquet_data(file_name):
    """Carrega um arquivo Parquet do diretório intermediário."""
    path = os.path.join(INTERMEDIATE_DATA_PATH, file_name)
    if not os.path.exists(path):
        st.error(f"Arquivo de dados não encontrado: {path}. Execute o pipeline de processamento.")
        return None
    return pd.read_parquet(path)

@st.cache_data
def load_plot(file_name):
    """Carrega uma figura Plotly a partir de um arquivo JSON."""
    path = os.path.join(VISUALIZATION_DATA_PATH, file_name)
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return pio.from_json(f.read())


@st.cache_data(ttl=3600)
def get_current_season_players():
    """Busca os atletas do mercado da temporada atual na API do Cartola."""
    try:
        response = requests.get(f"{CARTOLA_BASE_URL}/atletas/mercado")
        if response.status_code == 200:
            return response.json().get('atletas', [])
        return []
    except (requests.exceptions.RequestException, KeyError):
        return []
