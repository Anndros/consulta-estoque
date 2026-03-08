"""
Inicializador dos módulos
"""
from .config import *
from .database import carregar_dados, criar_dados_exemplo
from .image_handler import image_handler
from .ui_components import sidebar_filtros, metricas_produtos, rodape
from .filters import aplicar_filtros, paginar_dados
from .product_card import render_product_grid
from .utils import inicializar_session_state, reset_paginacao, diagnosticar_sistema