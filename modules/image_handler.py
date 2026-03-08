"""
Módulo de gerenciamento de imagens - Busca, cache e processamento
"""

import streamlit as st
import os
import pandas as pd
from PIL import Image
import base64
from .config import IMAGENS_DIR, SUPPORTED_IMAGES, CACHE_TTL_IMAGENS, IMAGEM_TAMANHO_PADRAO

class ImageHandler:
    """Gerenciador de imagens com cache"""
    
    def __init__(self):
        if 'cache_imagens' not in st.session_state:
            st.session_state.cache_imagens = {}
        if 'cache_caminhos' not in st.session_state:
            st.session_state.cache_caminhos = {}
    
    @st.cache_data(ttl=CACHE_TTL_IMAGENS, show_spinner=False)
    def _load_image_from_path(_self, caminho):
        """Carrega imagem do disco com cache"""
        try:
            if os.path.exists(caminho):
                return Image.open(caminho)
        except:
            pass
        return None
    
    def _to_base64(self, caminho):
        """Converte imagem para base64"""
        try:
            with open(caminho, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None
    
    def encontrar_imagem(self, caminho_planilha, codigo):
        """
        Encontra imagem em múltiplos locais com cache
        Retorna: (caminho, imagem, base64, estrategia)
        """
        cache_key = f"{codigo}_{caminho_planilha}"
        
        # Verificar cache
        if cache_key in st.session_state.cache_caminhos:
            cached = st.session_state.cache_caminhos[cache_key]
            if cached and os.path.exists(cached['caminho']):
                return cached['caminho'], cached['imagem'], cached['base64'], cached['estrategia']
        
        if pd.isna(caminho_planilha) or not caminho_planilha:
            caminho_planilha = ""
        
        # Lista de estratégias
        estrategias = self._gerar_estrategias(caminho_planilha, codigo)
        
        # Tentar cada estratégia
        for nome_estrategia, caminho in estrategias:
            if os.path.exists(caminho):
                imagem = self._load_image_from_path(caminho)
                base64_str = self._to_base64(caminho)
                
                # Salvar no cache
                st.session_state.cache_caminhos[cache_key] = {
                    'caminho': caminho,
                    'imagem': imagem,
                    'base64': base64_str,
                    'estrategia': nome_estrategia
                }
                
                return caminho, imagem, base64_str, nome_estrategia
        
        return None, None, None, "Não encontrada"
    
    def _gerar_estrategias(self, caminho_planilha, codigo):
        """Gera todas as possíveis estratégias de busca"""
        estrategias = []
        
        # Estratégia 1: Caminho direto
        if caminho_planilha and os.path.exists(caminho_planilha):
            estrategias.append(("Direto", caminho_planilha))
        
        # Estratégia 2: Nome do arquivo na pasta imagens
        if caminho_planilha:
            nome_arquivo = os.path.basename(caminho_planilha)
            estrategias.append(("Nome planilha", os.path.join(IMAGENS_DIR, nome_arquivo)))
        
        # Estratégia 3: Código + extensões
        for ext in ['.jpg', '.jpeg', '.png']:
            estrategias.append((f"Código{ext}", os.path.join(IMAGENS_DIR, f"{codigo}{ext}")))
            estrategias.append((f"Código lower{ext}", os.path.join(IMAGENS_DIR, f"{codigo.lower()}{ext}")))
        
        # Estratégia 4: Busca por similaridade
        if os.path.exists(IMAGENS_DIR):
            for arquivo in os.listdir(IMAGENS_DIR):
                if codigo.lower() in arquivo.lower() and arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                    estrategias.append(("Similar", os.path.join(IMAGENS_DIR, arquivo)))
                    break
        
        return estrategias
    
    def redimensionar_imagem(self, imagem, tamanho=IMAGEM_TAMANHO_PADRAO):
        """Redimensiona imagem mantendo proporção"""
        if imagem:
            img_copy = imagem.copy()
            img_copy.thumbnail(tamanho)
            return img_copy
        return None

# Instância global do gerenciador
image_handler = ImageHandler()