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
        
        # Garantir colunas necessárias - ADICIONADO 'peca'
        colunas_necessarias = ['loja', 'peca', 'codigo', 'imagem', 'preco', 'status', 'quantidade']
        
        for col in colunas_necessarias:
            if col not in df.columns:
                if col == 'quantidade':
                    df[col] = 0
                elif col == 'preco':
                    df[col] = 0.0
                else:
                    df[col] = ''
        
        # CONVERSÕES
        # Quantidade
        if 'quantidade' in df.columns:
            df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype('int32')
        
        # Preço
        if 'preco' in df.columns:
            df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0).astype(float)
        
        # Status
        if 'status' in df.columns:
            df['status'] = df['status'].fillna('').astype(str).str.lower().str.strip()
        
        # NOVO: Peça
        if 'peca' in df.columns:
            df['peca'] = df['peca'].fillna('').astype(str).str.strip()
            # Se vazio, colocar "Não especificado"
            df.loc[df['peca'] == '', 'peca'] = 'Não especificado'
        
        # Loja
        if 'loja' in df.columns:
            df['loja'] = df['loja'].fillna('').astype(str)
        
        # Código
        if 'codigo' in df.columns:
            df['codigo'] = df['codigo'].fillna('').astype(str)
        
        # Imagem
        if 'imagem' in df.columns:
            df['imagem'] = df['imagem'].fillna('').astype(str)
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return pd.DataFrame()

def criar_dados_exemplo():
    """
    Cria dados de exemplo para teste com o novo campo 'peca'
    """
    from PIL import Image, ImageDraw
    import os
    
    # Dados com o novo campo 'peca'
    dados_exemplo = {
        'loja': ['Loja Centro', 'Loja Shopping', 'Loja Centro', 'Loja Norte', 'Loja Sul'],
        'peca': ['Camiseta', 'Calça', 'Tênis', 'Camiseta', 'Boné'],  # NOVO CAMPO
        'codigo': ['PROD-001', 'PROD-002', 'PROD-003', 'PROD-004', 'PROD-005'],
        'imagem': ['', '', '', '', ''],
        'preco': [49.90, 89.90, 129.90, 59.90, 34.90],
        'status': ['estoque', 'estoque', 'acabou', 'estoque', 'estoque'],
        'quantidade': [15, 8, 0, 3, 10]
    }
    
    df_exemplo = pd.DataFrame(dados_exemplo)
    
    # Garantir que a pasta existe
    os.makedirs(DADOS_DIR, exist_ok=True)
    df_exemplo.to_excel(os.path.join(DADOS_DIR, "catalogo.xlsx"), index=False)
    
    # Criar imagens exemplo
    from .config import IMAGENS_DIR
    os.makedirs(IMAGENS_DIR, exist_ok=True)

    return True

@st.cache_data(ttl=CACHE_TTL_DADOS)
def get_tipos_peca(df):
    """Retorna lista única de tipos de peça"""
    if df.empty or 'peca' not in df.columns:
        return []
    return sorted(df['peca'].unique().tolist())