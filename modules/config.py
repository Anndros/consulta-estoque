"""
Módulo de configurações - Constantes e configurações globais
"""

import os
from pathlib import Path

# Caminhos absolutos
BASE_DIR = Path(__file__).parent.parent.absolute()
IMAGENS_DIR = os.path.join(BASE_DIR, "imagens")
DADOS_DIR = os.path.join(BASE_DIR, "dados")

# Configurações de imagem
SUPPORTED_IMAGES = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
IMAGEM_TAMANHO_PADRAO = (200, 200)  # Aumentado para melhor qualidade
IMAGEM_QUALIDADE = 95  # Qualidade aumentada

# Configurações de cache
CACHE_TTL_DADOS = 600  # 10 minutos
CACHE_TTL_IMAGENS = 3600  # 1 hora
CACHE_MAX_ENTRIES = 100

# Configurações de UI
ITENS_POR_PAGINA = 12
COLUNAS_GRID = 4

# Configurações de filtros
STATUS_OPCOES = ['Todos', 'Em estoque', 'Acabou']

# NOVA: Lista de tipos de peça (será preenchida dinamicamente)
TODAS_PECAS = "Todas as peças"