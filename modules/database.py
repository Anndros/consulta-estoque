"""
Módulo de banco de dados - Carregamento e cache da planilha
"""

import streamlit as st
import pandas as pd
import os
from .config import DADOS_DIR, CACHE_TTL_DADOS

@st.cache_data(ttl=CACHE_TTL_DADOS, show_spinner="Carregando dados...")
def carregar_dados():
    """
    Carrega os dados da planilha Excel com cache
    Retorna: DataFrame com os dados
    """
    caminho_planilha = os.path.join(DADOS_DIR, "catalogo.xlsx")
    
    if not os.path.exists(caminho_planilha):
        return pd.DataFrame()
    
    try:
        df = pd.read_excel(caminho_planilha)
        
        # Garantir colunas necessárias
        colunas_necessarias = ['loja', 'codigo', 'imagem', 'preco', 'status', 'quantidade']
        for col in colunas_necessarias:
            if col not in df.columns:
                if col == 'quantidade':
                    df[col] = 0
                elif col == 'preco':
                    df[col] = 0.0
                else:
                    df[col] = ''
        
        # Converter tipos
        df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0)
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype(int)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return pd.DataFrame()

def criar_dados_exemplo():
    """
    Cria dados de exemplo para teste
    """
    from PIL import Image, ImageDraw
    
    dados_exemplo = {
        'loja': ['Loja Centro', 'Loja Shopping', 'Loja Centro', 'Loja Norte', 'Loja Sul'],
        'codigo': ['PROD-001', 'PROD-002', 'PROD-003', 'PROD-004', 'PROD-005'],
        'imagem': ['', '', '', '', ''],
        'preco': [49.90, 89.90, 129.90, 59.90, 199.90],
        'status': ['estoque', 'estoque', 'acabou', 'estoque', 'acabou'],
        'quantidade': [10, 8, 0, 5, 0]
    }
    
    df_exemplo = pd.DataFrame(dados_exemplo)
    df_exemplo.to_excel(os.path.join(DADOS_DIR, "catalogo.xlsx"), index=False)
    
    # Criar imagens exemplo
    from .config import IMAGENS_DIR
    for codigo in ['PROD-001', 'PROD-002', 'PROD-003']:
        img = Image.new('RGB', (300, 300), color=(100, 150, 200))
        d = ImageDraw.Draw(img)
        d.text((100, 150), codigo, fill=(255, 255, 255))
        img.save(os.path.join(IMAGENS_DIR, f"{codigo}.jpg"))
    
    return True