import streamlit as st
import subprocess
import os
st.set_page_config(page_title="EscalAI", layout="wide", initial_sidebar_state="expanded")

pages = [
    st.Page("pages/01_dashboard.py", title="Início", icon="🏠"),
    st.Page("pages/02_analise_exploratoria.py", title="Análise Exploratória", icon="🔎"),
    st.Page("pages/03_analise_agregada.py", title="Análise Agregada", icon="📊"),
]

pg = st.navigation(pages)

pg.run()
