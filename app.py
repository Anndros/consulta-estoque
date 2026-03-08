"""
Arquivo principal do aplicativo - Orquestra todos os módulos
"""

import streamlit as st
from modules import config, database, image_handler, ui_components, filters, product_card, utils
from modules.config import ITENS_POR_PAGINA
from modules.database import carregar_dados, criar_dados_exemplo
from modules.image_handler import image_handler
from modules.ui_components import sidebar_filtros, metricas_produtos, rodape
from modules.filters import aplicar_filtros, paginar_dados
from modules.product_card import render_product_grid
from modules.utils import inicializar_session_state, reset_paginacao, diagnosticar_sistema




# ===== CONFIGURAÇÃO INICIAL =====
st.set_page_config(
    page_title="Consulta de Produtos",
    page_icon="🔍",
    layout="wide"
)

# Inicializar session state
inicializar_session_state()

# Título
st.title("🔍 Consulta de Produtos")
st.markdown("---")

# ===== CARREGAR DADOS =====
df = carregar_dados()

# ===== SIDEBAR COM FILTROS =====
if not df.empty:
    filtros = sidebar_filtros(df)
    
    # Aplicar filtros
    df_filtrado = aplicar_filtros(df, filtros)
    
    # ===== ÁREA PRINCIPAL =====
    if not df_filtrado.empty:
        st.subheader(f"📊 {len(df_filtrado)} produtos encontrados")
        
        # Métricas
        metricas_produtos(df_filtrado)
        
        # Paginação
        total_paginas = (len(df_filtrado) + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA
        
        # Controles de página
        if total_paginas > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.session_state.pagina_atual = st.number_input(
                    "Página", 
                    min_value=1, 
                    max_value=total_paginas, 
                    value=st.session_state.pagina_atual
                )
        
        # Pegar dados da página atual
        df_paginado, inicio, fim = paginar_dados(
            df_filtrado, 
            st.session_state.pagina_atual, 
            ITENS_POR_PAGINA
        )
        
        # Mostrar produtos
        st.subheader(f"📸 Mostrando {inicio+1}-{fim} de {len(df_filtrado)}")
        render_product_grid(df_paginado)
        
    else:
        st.warning("Nenhum produto encontrado com os filtros selecionados")
        
        with st.expander("💡 Dicas"):
            st.write("- Aumente a faixa de preço")
            st.write("- Selecione 'Todos' no status")
            st.write("- Tente outra loja")
else:
    # Dados não carregados
    st.error("""
    ❌ Nenhum dado encontrado
    
    **Para começar:**
    1. Coloque sua planilha 'catalogo.xlsx' na pasta 'dados/'
    2. Ou clique no botão abaixo para criar dados de exemplo
    """)
    
    if st.button("📝 Criar dados exemplo"):
        if criar_dados_exemplo():
            st.success("Dados exemplo criados!")
            st.rerun()
    
    # Diagnóstico
    diagnosticar_sistema()

# ===== RODAPÉ =====
rodape(df)