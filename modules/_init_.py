"""
Inicializador dos módulos
"""

import streamlit as st

# Inicializar session state
if 'cache_imagens' not in st.session_state:
    st.session_state.cache_imagens = {}
if 'cache_caminhos' not in st.session_state:
    st.session_state.cache_caminhos = {}

from .config import *
from .database import carregar_dados, criar_dados_exemplo, get_tipos_peca  # NOVA função
from .image_handler import image_handler
from .ui_components import sidebar_filtros, metricas_produtos, rodape
from .filters import aplicar_filtros, paginar_dados
from .product_card import render_product_grid, render_product_card
from .utils import inicializar_session_state, reset_paginacao, diagnosticar_sistema
