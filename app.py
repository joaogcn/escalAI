import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from supabase import create_client, Client
import os
from typing import Dict, List, Optional
import time
from dotenv import load_dotenv

load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="EscalAI - Cartola FC",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações do Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Inicializar cliente Supabase
@st.cache_resource
def init_supabase():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"Erro ao conectar com Supabase: {e}")
        return None

# APIs do Cartola - FOCO NO MERCADO
CARTOLA_BASE_URL = "https://api.cartolafc.globo.com"

# Funções para coletar dados das APIs - FOCO NO MERCADO
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_mercado_status():
    """Status do mercado - ESTRUTURA REAL VERIFICADA"""
    try:
        response = requests.get(f"{CARTOLA_BASE_URL}/mercado/status")
        if response.status_code == 200:
            data = response.json()
            return data
        return None
    except:
        return None

@st.cache_data(ttl=300)
def get_destaques():
    """Jogadores mais escalados do mercado"""
    try:
        response = requests.get(f"{CARTOLA_BASE_URL}/mercado/destaques")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=300)
def get_jogadores_mercado():
    """Todos os jogadores do mercado - ESTRUTURA REAL VERIFICADA"""
    try:
        response = requests.get(f"{CARTOLA_BASE_URL}/atletas/mercado")
        if response.status_code == 200:
            data = response.json()
            return data  # Dict com 'atletas', 'clubes', 'posicoes', 'status'
        return None
    except:
        return None

@st.cache_data(ttl=60)  # Cache por 1 minuto
def get_pontuacao_rodada():
    """Pontuação da rodada em andamento"""
    try:
        response = requests.get(f"{CARTOLA_BASE_URL}/atletas/pontuados")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=3600)
def get_destaques_pos_rodada():
    """Destaques da rodada anterior"""
    try:
        response = requests.get(f"{CARTOLA_BASE_URL}/pos-rodada/destaques")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Funções para salvar dados no Supabase - FOCO NO MERCADO (ESTRUTURA SIMPLIFICADA)
def save_clubes_mercado(supabase, jogadores_data):
    """Salva apenas os clubes que estão no mercado (ESTRUTURA LIMPA)"""
    if not supabase:
        return False
    
    try:
        clubes_mercado = jogadores_data.get('clubes', {})
        clubes_list = []
        
        for clube_id, clube_info in clubes_mercado.items():
            clubes_list.append({
                'id': int(clube_id),
                'nome': clube_info.get('nome_fantasia', clube_info.get('nome', '')),  # Nome fantasia como principal
                'abreviacao': clube_info.get('abreviacao', ''),
                'escudo_url': clube_info.get('escudos', {}).get('60x60', '') if clube_info.get('escudos') else '',
                'apelido': clube_info.get('apelido', ''),
                'no_mercado': True
            })
        
        # Upsert para evitar duplicatas
        result = supabase.table('clubes').upsert(clubes_list).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar clubes do mercado: {e}")
        return False

def save_jogadores_mercado(supabase, jogadores_data):
    """Salva dados dos jogadores do mercado (ESTRUTURA LIMPA)"""
    if not supabase:
        return False
    
    try:
        atletas = jogadores_data.get('atletas', [])
        clubes_mercado = jogadores_data.get('clubes', {})
        posicoes = jogadores_data.get('posicoes', {})
        status = jogadores_data.get('status', {})
        
        jogadores_list = []
        for jogador_info in atletas:
            # Obter informações do clube
            clube_id = jogador_info.get('clube_id', 0)
            
            # Obter nome da posição diretamente
            posicao_id = str(jogador_info.get('posicao_id', ''))
            posicao_nome = posicoes.get(posicao_id, {}).get('nome', 'N/A')
            
            # Obter nome do status diretamente
            status_id = str(jogador_info.get('status_id', ''))
            status_nome = status.get(status_id, {}).get('nome', 'N/A')
            
            jogadores_list.append({
                'id': int(jogador_info.get('atleta_id', 0)),
                'nome': jogador_info.get('nome', ''),
                'apelido': jogador_info.get('apelido', ''),
                'clube_id': int(clube_id),
                'posicao': posicao_nome,  # Apenas posição (sem duplicação)
                'status': status_nome,     # Apenas status (sem duplicação)
                'preco': float(jogador_info.get('preco_num', 0)),
                'media': float(jogador_info.get('media_num', 0)),
                'variacao': float(jogador_info.get('variacao_num', 0)),
                'no_mercado': True
            })
        
        result = supabase.table('jogadores').upsert(jogadores_list).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar jogadores do mercado: {e}")
        return False

def save_status_mercado(supabase, mercado_status):
    """Salva status do mercado (sempre 1 registro)"""
    if not supabase:
        return False
    
    try:
        # Sempre atualizar o registro existente (ID 1)
        mercado_data = {
            'id': 1,
            'rodada_atual': mercado_status.get('rodada_atual'),
            'status_mercado': mercado_status.get('status_mercado'),
            'times_escalados': mercado_status.get('times_escalados'),
            'temporada': mercado_status.get('temporada'),
            'cartoleta_inicial': mercado_status.get('cartoleta_inicial'),
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('mercado').upsert(mercado_data).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar status do mercado: {e}")
        return False

# Interface principal
def main():
    st.title("⚽ EscalAI - Cartola FC")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Navegação")
        page = st.selectbox(
            "Selecione a página:",
            ["🏠 Dashboard", "👥 Jogadores do Mercado", "🏆 Clubes do Mercado", "📊 Análises", "🔄 Coletar Dados do Mercado"]
        )
        
        st.header("🔍 Filtros")
        rodada_atual = st.number_input("Rodada:", min_value=1, max_value=38, value=1)
        
        st.header("⚙️ Configurações")
        auto_refresh = st.checkbox("Atualização automática", value=False)
        if auto_refresh:
            st.info("Atualizando a cada 5 minutos...")
            time.sleep(300)
            st.rerun()
    
    # Navegação das páginas
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👥 Jogadores do Mercado":
        show_jogadores_mercado()
    elif page == "🏆 Clubes do Mercado":
        show_clubes_mercado()
    elif page == "📊 Análises":
        show_analises()
    elif page == "🔄 Coletar Dados do Mercado":
        show_coletar_dados_mercado()

def show_dashboard():
    """Página inicial do dashboard - FOCO NO MERCADO"""
    st.header("🏠 Dashboard do Mercado")
    
    # Status do mercado
    st.subheader("📊 Status do Mercado")
    mercado_status = get_mercado_status()
    
    if mercado_status:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_text = "Ativo" if mercado_status.get('status_mercado') == 1 else "Fechado"
            st.metric(
                "Status",
                status_text,
                delta="Ativo" if mercado_status.get('status_mercado') == 1 else "Fechado"
            )
        
        with col2:
            st.metric(
                "Rodada Atual",
                mercado_status.get('rodada_atual', 'N/A')
            )
        
        with col3:
            st.metric(
                "Times Escalados",
                f"{mercado_status.get('times_escalados', 0):,}"
            )
        
        with col4:
            st.metric(
                "Cartoleta Inicial",
                f"R$ {mercado_status.get('cartoleta_inicial', 0):.2f}"
            )
    else:
        st.warning("Não foi possível carregar o status do mercado")
    
    # Destaques do mercado
    st.subheader("🌟 Destaques do Mercado")
    destaques = get_destaques()
    
    if destaques:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👑 Jogadores Mais Escalados")
            if 'atletas' in destaques:
                atletas_destaque = destaques['atletas']
                for atleta in atletas_destaque[:5]:  # Top 5
                    st.write(f"• {atleta.get('apelido', 'N/A')} - {atleta.get('clube', {}).get('nome', 'N/A')}")
        
        with col2:
            st.subheader("📈 Estatísticas do Mercado")
            if 'posicoes' in destaques:
                posicoes_destaque = destaques['posicoes']
                for posicao in posicoes_destaque[:3]:  # Top 3 posições
                    st.write(f"• {posicao.get('nome', 'N/A')}: {posicao.get('escalacoes', 0)} escalações")
    else:
        st.info("Nenhum destaque disponível do mercado")
    
    # Resumo do mercado
    st.subheader("📋 Resumo do Mercado")
    jogadores = get_jogadores_mercado()
    
    if jogadores:
        atletas = jogadores.get('atletas', [])
        clubes_mercado = jogadores.get('clubes', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Jogadores", len(atletas))
        
        with col2:
            st.metric("Clubes no Mercado", len(clubes_mercado))
        
        with col3:
            # Contar posições únicas dos jogadores
            posicoes_unicas = set()
            for jogador_info in atletas:
                posicao_id = str(jogador_info.get('posicao_id', ''))
                if posicao_id in jogadores.get('posicoes', {}):
                    posicoes_unicas.add(jogadores['posicoes'][posicao_id].get('nome', ''))
            st.metric("Posições Disponíveis", len(posicoes_unicas))

def show_jogadores_mercado():
    """Página de jogadores do mercado"""
    st.header("👥 Jogadores do Mercado")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        posicao = st.selectbox(
            "Posição:",
            ["Todas", "Goleiro", "Lateral", "Zagueiro", "Meia", "Atacante", "Técnico"]
        )
    
    with col2:
        clube = st.selectbox(
            "Clube:",
            ["Todos"]
        )
    
    with col3:
        status = st.selectbox(
            "Status:",
            ["Todos", "Provável", "Dúvida", "Suspenso", "Lesionado", "Nulo"]
        )
    
    # Buscar jogadores do mercado
    if st.button("🔍 Buscar Jogadores do Mercado"):
        jogadores = get_jogadores_mercado()
        
        if jogadores and 'atletas' in jogadores:
            atletas = jogadores['atletas']
            clubes_mercado = jogadores.get('clubes', {})
            posicoes = jogadores.get('posicoes', {})
            status_types = jogadores.get('status', {})
            
            # Filtrar jogadores
            jogadores_list = []
            for jogador_info in atletas:
                clube_id = str(jogador_info.get('clube_id', ''))
                clube_nome = clubes_mercado.get(clube_id, {}).get('nome_fantasia', clubes_mercado.get(clube_id, {}).get('nome', 'N/A'))
                
                posicao_id = str(jogador_info.get('posicao_id', ''))
                posicao_nome = posicoes.get(posicao_id, {}).get('nome', 'N/A')
                
                status_id = str(jogador_info.get('status_id', ''))
                status_nome = status_types.get(status_id, {}).get('nome', 'N/A')
                
                jogadores_list.append({
                    'ID': jogador_info.get('atleta_id', 'N/A'),
                    'Nome': jogador_info.get('nome', ''),
                    'Apelido': jogador_info.get('apelido', ''),
                    'Clube': clube_nome,
                    'Posição': posicao_nome,
                    'Preço': f"R$ {jogador_info.get('preco_num', 0):.2f}",
                    'Média': f"{jogador_info.get('media_num', 0):.1f}",
                    'Variação': f"{jogador_info.get('variacao_num', 0):.2f}",
                    'Status': status_nome
                })
            
            df = pd.DataFrame(jogadores_list)
            st.dataframe(df, use_container_width=True)
            
            # Gráficos do mercado
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Distribuição por Posição")
                pos_counts = df['Posição'].value_counts()
                fig = px.pie(values=pos_counts.values, names=pos_counts.index, title="Jogadores por Posição")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 Distribuição por Clube")
                clube_counts = df['Clube'].value_counts().head(10)
                fig = px.bar(x=clube_counts.values, y=clube_counts.index, orientation='h', title="Top 10 Clubes")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Erro ao carregar dados dos jogadores do mercado")

def show_clubes_mercado():
    """Página de clubes do mercado"""
    st.header("🏆 Clubes do Mercado")
    
    jogadores = get_jogadores_mercado()
    
    if jogadores and 'clubes' in jogadores:
        clubes_mercado = jogadores['clubes']
        
        # Listar clubes do mercado
        st.subheader("📋 Clubes Ativos no Mercado")
        clubes_list = []
        
        for clube_id, clube_info in clubes_mercado.items():
            clubes_list.append({
                'ID': clube_id,
                'Nome': clube_info.get('nome_fantasia', clube_info.get('nome', '')),
                'Abreviação': clube_info.get('abreviacao', ''),
                'Apelido': clube_info.get('apelido', '')
            })
        
        df = pd.DataFrame(clubes_list)
        st.dataframe(df, use_container_width=True)
        
        # Estatísticas dos clubes
        st.subheader("📊 Estatísticas dos Clubes")
        
        # Contar jogadores por clube
        jogadores_por_clube = {}
        atletas = jogadores.get('atletas', [])
        
        for jogador_info in atletas:
            clube_id = str(jogador_info.get('clube_id', ''))
            if clube_id in clubes_mercado:
                clube_nome = clubes_mercado[clube_id].get('nome_fantasia', clubes_mercado[clube_id].get('nome', 'N/A'))
                if clube_nome not in jogadores_por_clube:
                    jogadores_por_clube[clube_nome] = 0
                jogadores_por_clube[clube_nome] += 1
        
        # Gráfico de jogadores por clube
        if jogadores_por_clube:
            clube_names = list(jogadores_por_clube.keys())
            clube_counts = list(jogadores_por_clube.values())
            
            fig = px.bar(x=clube_names, y=clube_counts, title="Jogadores por Clube no Mercado")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Erro ao carregar dados dos clubes do mercado")

def show_analises():
    """Página de análises do mercado"""
    st.header("📊 Análises do Mercado")
    
    jogadores = get_jogadores_mercado()
    
    if jogadores and 'atletas' in jogadores:
        atletas = jogadores['atletas']
        
        # Análise de preços
        st.subheader("💰 Análise de Preços")
        
        precos = []
        for jogador_info in atletas:
            preco = jogador_info.get('preco_num', 0)
            if preco > 0:
                precos.append(preco)
        
        if precos:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Preço Médio", f"R$ {sum(precos)/len(precos):.2f}")
            
            with col2:
                st.metric("Preço Mínimo", f"R$ {min(precos):.2f}")
            
            with col3:
                st.metric("Preço Máximo", f"R$ {max(precos):.2f}")
            
            with col4:
                st.metric("Total de Jogadores", len(precos))
            
            # Histograma de preços
            fig = px.histogram(x=precos, nbins=20, title="Distribuição de Preços no Mercado")
            st.plotly_chart(fig, use_container_width=True)
        
        # Análise de médias
        st.subheader("📈 Análise de Médias")
        
        medias = []
        for jogador_info in atletas:
            media = jogador_info.get('media_num', 0)
            if media > 0:
                medias.append(media)
        
        if medias:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Média Geral", f"{sum(medias)/len(medias):.2f}")
            
            with col2:
                st.metric("Média Mínima", f"{min(medias):.2f}")
            
            with col3:
                st.metric("Média Máxima", f"{max(medias):.2f}")
            
            with col4:
                st.metric("Jogadores com Média", len(medias))
            
            # Gráfico de médias
            fig = px.histogram(x=medias, nbins=20, title="Distribuição de Médias no Mercado")
            st.plotly_chart(fig, use_container_width=True)

def show_coletar_dados_mercado():
    """Página para coletar dados do mercado"""
    st.header("🔄 Coletar Dados do Mercado")
    
    supabase = init_supabase()
    
    if not supabase:
        st.error("❌ Não foi possível conectar ao Supabase")
        st.info("Configure as variáveis de ambiente SUPABASE_URL e SUPABASE_KEY")
        return
    
    st.success("✅ Conectado ao Supabase")
    
    # Botões para coletar dados do mercado
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏆 Coletar Clubes do Mercado"):
            with st.spinner("Coletando dados dos clubes do mercado..."):
                jogadores = get_jogadores_mercado()
                if jogadores:
                    if save_clubes_mercado(supabase, jogadores):
                        st.success("✅ Clubes do mercado salvos com sucesso!")
                    else:
                        st.error("❌ Erro ao salvar clubes do mercado")
                else:
                    st.error("❌ Erro ao coletar dados dos clubes do mercado")
        
        if st.button("👥 Coletar Jogadores do Mercado"):
            with st.spinner("Coletando dados dos jogadores do mercado..."):
                jogadores = get_jogadores_mercado()
                if jogadores:
                    if save_jogadores_mercado(supabase, jogadores):
                        st.success("✅ Jogadores do mercado salvos com sucesso!")
                    else:
                        st.error("❌ Erro ao salvar jogadores do mercado")
                else:
                    st.error("❌ Erro ao coletar dados dos jogadores do mercado")
    
    with col2:
        if st.button("📊 Coletar Posições e Status"):
            with st.spinner("Coletando posições e status..."):
                jogadores = get_jogadores_mercado()
                if jogadores:
                    # A estrutura simplificada não salva posições e status separadamente
                    # A função save_status_mercado salva o status geral
                    if save_status_mercado(supabase, jogadores): # Passa o próprio jogadores_data
                        st.success("✅ Status do mercado salvos com sucesso!")
                    else:
                        st.error("❌ Erro ao salvar status do mercado")
                else:
                    st.error("❌ Erro ao coletar dados")
        
        if st.button("📈 Coletar Status do Mercado"):
            with st.spinner("Coletando status do mercado..."):
                mercado_status = get_mercado_status()
                if mercado_status:
                    st.success("✅ Status do mercado coletado com sucesso!")
                    st.json(mercado_status)
                else:
                    st.error("❌ Erro ao coletar status do mercado")
    
    # Status das tabelas
    st.subheader("📋 Status das Tabelas do Mercado")
    
    try:
        # Verificar dados nas tabelas
        clubes_count = supabase.table('clubes').select('*', count='exact').execute()
        jogadores_count = supabase.table('jogadores').select('*', count='exact').execute()
        mercado_count = supabase.table('mercado').select('*', count='exact').execute()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Clubes no Mercado", clubes_count.count if hasattr(clubes_count, 'count') else 'N/A')
        
        with col2:
            st.metric("Jogadores no Mercado", jogadores_count.count if hasattr(jogadores_count, 'count') else 'N/A')
        
        with col3:
            st.metric("Status do Mercado", mercado_count.count if hasattr(mercado_count, 'count') else 'N/A')
    
    except Exception as e:
        st.warning(f"⚠️ Erro ao verificar status das tabelas: {e}")

if __name__ == "__main__":
    main()
