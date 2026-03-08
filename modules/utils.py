"""
Módulo de utilitários - Funções auxiliares
"""
import streamlit as st
import os

def inicializar_session_state():
    """
    Inicializa variáveis do session state
    """
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = 1
    
    if 'filtros_anteriores' not in st.session_state:
        st.session_state.filtros_anteriores = {}
        print("Funcionar")

def reset_paginacao():
    """
    Reseta a paginação para a primeira página
    """
    st.session_state.pagina_atual = 1

def diagnosticar_sistema():
    """
    Diagnóstico do sistema (útil para debug)
    """
    from .config import BASE_DIR, IMAGENS_DIR, DADOS_DIR
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Diagnóstico")
    
    with st.sidebar.expander("Ver diagnóstico"):
        st.write(f"**Diretório base:** {BASE_DIR}")
        
        # Pasta imagens
        st.write(f"**Pasta imagens:** {IMAGENS_DIR}")
        st.write(f"- Existe: {os.path.exists(IMAGENS_DIR)}")
        
        if os.path.exists(IMAGENS_DIR):
            imagens = [f for f in os.listdir(IMAGENS_DIR) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            st.write(f"- Imagens: {len(imagens)}")
        
        # Pasta dados
        st.write(f"**Pasta dados:** {DADOS_DIR}")
        st.write(f"- Existe: {os.path.exists(DADOS_DIR)}")
        
        if os.path.exists(DADOS_DIR):
            planilha = os.path.join(DADOS_DIR, "catalogo.xlsx")
            st.write(f"- Planilha existe: {os.path.exists(planilha)}")