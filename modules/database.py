"""
Módulo de banco de dados - Carregamento e cache da planilha
"""
import streamlit as st
import pandas as pd
import os
from .config import DADOS_DIR, CACHE_TTL_DADOS
import numpy as np

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
        
        # Converter tipos com tratamento de NaN
        df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0).astype(float)
        
        # Converter quantidade garantindo que seja int e não NaN
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype(int)
        
        # Converter status para string e tratar NaN
        df['status'] = df['status'].fillna('').astype(str).str.lower()
        
        # Converter loja para string
        df['loja'] = df['loja'].fillna('').astype(str)
        
        # Converter codigo para string
        df['codigo'] = df['codigo'].fillna('').astype(str)
        
        # Converter imagem para string
        df['imagem'] = df['imagem'].fillna('').astype(str)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return pd.DataFrame()

def criar_dados_exemplo():
    """
    Cria dados de exemplo para teste
    """
    from PIL import Image, ImageDraw, ImageFont
    
    dados_exemplo = {
        'loja': ['Loja Centro', 'Loja Shopping', 'Loja Centro', 'Loja Norte', 'Loja Sul'],
        'codigo': ['PROD-001', 'PROD-002', 'PROD-003', 'PROD-004', 'PROD-005'],
        'imagem': ['', '', '', '', ''],
        'preco': [49.90, 89.90, 129.90, 59.90, 199.90],
        'status': ['estoque', 'estoque', 'acabou', 'estoque', 'acabou'],
        'quantidade': [10, 8, 0, 5, 0]
    }
    
    df_exemplo = pd.DataFrame(dados_exemplo)
    
    # Garantir que a pasta existe
    os.makedirs(DADOS_DIR, exist_ok=True)
    df_exemplo.to_excel(os.path.join(DADOS_DIR, "catalogo.xlsx"), index=False)
    
    # Criar imagens exemplo com melhor qualidade
    from .config import IMAGENS_DIR
    os.makedirs(IMAGENS_DIR, exist_ok=True)
    
    for i, codigo in enumerate(['PROD-001', 'PROD-002', 'PROD-003']):
        # Criar imagem com fundo gradiente
        img = Image.new('RGB', (300, 300), color=(100 + i*30, 150, 200))
        d = ImageDraw.Draw(img)
        
        # Desenhar um retângulo decorativo
        d.rectangle([50, 50, 250, 250], outline=(255, 255, 255), width=3)
        
        # Adicionar texto
        d.text((80, 140), codigo, fill=(255, 255, 255))
        
        # Salvar com qualidade
        img.save(os.path.join(IMAGENS_DIR, f"{codigo}.jpg"), quality=95)
    
    return True