"""
Módulo de componentes UI - Elementos reutilizáveis da interface
"""

import streamlit as st
from datetime import datetime
from .config import TODAS_PECAS
from .database import get_tipos_peca

def sidebar_filtros(df, on_filter_change=None):
    """
    Cria a sidebar com todos os filtros
    Retorna: dicionário com valores dos filtros
    """
    with st.sidebar:
        st.header("🔎 Filtros")
        
        if df.empty:
            st.error("Nenhum dado carregado")
            return None
        
        # NOVO: Filtro por Tipo de Peça
        st.subheader("👕 Tipo de Peça")
        tipos_peca = get_tipos_peca(df)
        opcoes_peca = [TODAS_PECAS] + tipos_peca
        peca_sel = st.selectbox("Selecione o tipo:", opcoes_peca, key='filtro_peca')


        # Filtro por Loja
        lojas = ['Todas'] + sorted(df['loja'].unique().tolist())
        loja_sel = st.selectbox("Selecione a Loja:", lojas, key='filtro_loja')
        
        # Filtro por Status
        status_opcoes = ['Todos', 'Em estoque', 'Acabou']
        status_sel = st.radio("Status:", status_opcoes, key='filtro_status')
        
        # Filtro por Preço
        st.subheader("💰 Faixa de Preço")
        preco_min = float(df['preco'].min())
        preco_max = float(df['preco'].max())
        
        col1, col2 = st.columns(2)
        with col1:
            preco_inicial = st.number_input("Mínimo", value=preco_min, step=10.0, key='preco_min')
        with col2:
            preco_final = st.number_input("Máximo", value=preco_max, step=10.0, key='preco_max')
        
        # Busca
        busca = st.text_input("🔍 Buscar código", key='busca_codigo')
        
        # Informações
        st.markdown("---")
        st.caption(f"Total de produtos: {len(df)}")
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
        
        if st.button("🔄 Atualizar", key='btn_atualizar'):
            st.cache_data.clear()
            st.rerun()
        
        return {
            'peca': peca_sel,  # NOVO
            'loja': loja_sel,
            'status': status_sel,
            'preco_min': preco_inicial,
            'preco_max': preco_final,
            'busca': busca
        }

def metricas_produtos(df_filtrado):
    """
    Exibe métricas dos produtos filtrados
    """
    if df_filtrado.empty:
        return
    
    col1, col2, col3, col4, col5 = st.columns(5) # Aumentado para 5 colunas
    
    with col1:
        st.metric("Total", len(df_filtrado))
    
    with col2:
        em_estoque = len(df_filtrado[df_filtrado['status'].str.lower() == 'estoque'])
        st.metric("Em Estoque", em_estoque)
    
    with col3:
        acabou = len(df_filtrado[df_filtrado['status'].str.lower() == 'acabou'])
        st.metric("Acabou", acabou)
    
    with col4:
        qtd_total = df_filtrado['quantidade'].sum()
        st.metric("Unidades", int(qtd_total))

    with col5:
        # NOVO: Mostrar variedade de peças
        variedade = df_filtrado['peca'].nunique() if 'peca' in df_filtrado.columns else 0
        st.metric("Tipos de Peça", variedade)
    
    st.markdown("---")

def rodape(df):
    """
    Exibe rodapé com informações
    """
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption("🏪 Consulta de Produtos")
    
    with col2:
        if not df.empty:
            total_estoque = df[df['status'].str.lower() == 'estoque']['quantidade'].sum()
            st.caption(f"📦 Total em estoque: {int(total_estoque)} unidades")
    
    with col3:
        versao = "v2.0.0"
        st.caption(f"🔄 {versao}")