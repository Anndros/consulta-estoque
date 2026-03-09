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
    """Gerenciador de imagens com cache e preservação de qualidade"""
    
    def __init__(self):
        # Garantir que session_state está pronto para uso
        self._inicializar_session_state()
    
    def _inicializar_session_state(self):
        """Inicializa as variáveis no session_state de forma segura"""
        if 'cache_imagens' not in st.session_state:
            st.session_state.cache_imagens = {}
        
        if 'cache_caminhos' not in st.session_state:
            st.session_state.cache_caminhos = {}
    
    def _get_cache_caminhos(self):
        """Retorna o cache de caminhos de forma segura"""
        self._inicializar_session_state()
        return st.session_state.cache_caminhos
    
    def _get_cache_imagens(self):
        """Retorna o cache de imagens de forma segura"""
        self._inicializar_session_state()
        return st.session_state.cache_imagens
    
    @st.cache_data(ttl=CACHE_TTL_IMAGENS, show_spinner=False)
    def _load_image_from_path(_self, caminho):
        """Carrega imagem do disco com cache - mantém qualidade original"""
        try:
            if os.path.exists(caminho):
                img = Image.open(caminho)
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    return rgb_img
                return img
        except Exception as e:
            print(f"Erro ao carregar imagem {caminho}: {e}")
        return None
    
    def _to_base64(self, caminho):
        """Converte imagem para base64 mantendo qualidade"""
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
        cache_caminhos = self._get_cache_caminhos()
        cache_key = f"{codigo}_{caminho_planilha}"
        
        # Verificar cache
        if cache_key in cache_caminhos:
            cached = cache_caminhos[cache_key]
            if cached and cached.get('caminho') and os.path.exists(cached['caminho']):
                return (
                    cached['caminho'], 
                    cached.get('imagem'), 
                    cached.get('base64'), 
                    cached.get('estrategia', 'Cache')
                )
        
        # Tratar caminho vazio
        if pd.isna(caminho_planilha) or not caminho_planilha:
            caminho_planilha = ""
        else:
            caminho_planilha = str(caminho_planilha)
        
        # Lista de estratégias em ordem de prioridade
        estrategias = self._gerar_estrategias(caminho_planilha, codigo)
        
        # Tentar cada estratégia
        for nome_estrategia, caminho in estrategias:
            if caminho and os.path.exists(caminho):
                imagem = self._load_image_from_path(caminho)
                base64_str = self._to_base64(caminho)
                
                # Salvar no cache
                cache_caminhos[cache_key] = {
                    'caminho': caminho,
                    'imagem': imagem,
                    'base64': base64_str,
                    'estrategia': nome_estrategia
                }
                
                return caminho, imagem, base64_str, nome_estrategia
        
        return None, None, None, "Não encontrada"
    
    def _gerar_estrategias(self, caminho_planilha, codigo):
        """Gera todas as possíveis estratégias de busca em ordem de prioridade"""
        estrategias = []
        codigo = str(codigo)
        
        # Estratégia 1: Caminho direto
        if caminho_planilha and os.path.exists(caminho_planilha):
            estrategias.append(("Direto", caminho_planilha))
        
        # Estratégia 2: Nome do arquivo na pasta imagens
        if caminho_planilha:
            nome_arquivo = os.path.basename(caminho_planilha)
            caminho_test = os.path.join(IMAGENS_DIR, nome_arquivo)
            if os.path.exists(caminho_test):
                estrategias.append(("Nome planilha", caminho_test))
        
        # Estratégia 3: Código + extensões
        for ext in ['.jpg', '.jpeg', '.png']:
            caminho_test = os.path.join(IMAGENS_DIR, f"{codigo}{ext}")
            if os.path.exists(caminho_test):
                estrategias.append((f"Código{ext}", caminho_test))
            
            caminho_test = os.path.join(IMAGENS_DIR, f"{codigo.lower()}{ext}")
            if os.path.exists(caminho_test):
                estrategias.append((f"Código lower{ext}", caminho_test))
        
        # Estratégia 4: Código sem caracteres especiais
        codigo_limpo = ''.join(e for e in codigo if e.isalnum())
        if codigo_limpo and codigo_limpo != codigo:
            for ext in ['.jpg', '.jpeg', '.png']:
                caminho_test = os.path.join(IMAGENS_DIR, f"{codigo_limpo}{ext}")
                if os.path.exists(caminho_test):
                    estrategias.append((f"Código limpo{ext}", caminho_test))
        
        # Estratégia 5: Busca por similaridade
        if os.path.exists(IMAGENS_DIR):
            for arquivo in os.listdir(IMAGENS_DIR):
                if arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                    if codigo.lower() in arquivo.lower() or arquivo.lower() in codigo.lower():
                        caminho_test = os.path.join(IMAGENS_DIR, arquivo)
                        if os.path.exists(caminho_test):
                            estrategias.append(("Similar", caminho_test))
                            break
        
        # Remover duplicatas
        seen = set()
        estrategias_unicas = []
        for nome, caminho in estrategias:
            if caminho not in seen:
                seen.add(caminho)
                estrategias_unicas.append((nome, caminho))
        
        return estrategias_unicas
    
    def redimensionar_imagem(self, imagem, tamanho=(200, 200)):
        """Redimensiona imagem mantendo proporção e qualidade"""
        if imagem:
            try:
                img_copy = imagem.copy()
                img_copy.thumbnail(tamanho, Image.Resampling.LANCZOS)
                return img_copy
            except Exception as e:
                print(f"Erro ao redimensionar imagem: {e}")
                return imagem
        return None

# Instância global do gerenciador
image_handler = ImageHandler()