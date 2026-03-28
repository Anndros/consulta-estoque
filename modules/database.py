"""
Módulo de banco de dados - Carregamento e cache da planilha
"""
import streamlit as st
import pandas as pd
import os
import numpy as np
from .config import DADOS_DIR, CACHE_TTL_DADOS

@st.cache_data(ttl=300, show_spinner="Carregando dados...")
def carregar_dados():
    """
    Carrega os dados da planilha Excel com cache
    Retorna: DataFrame com os dados
    """
    caminho_planilha = os.path.join(DADOS_DIR, "catalogo.xlsx")
    
    if not os.path.exists(caminho_planilha):
        st.warning("Planilha não encontrada. Use o botão 'Criar dados exemplo'.")
        return pd.DataFrame()
    
    try:
          # Carregar SEM modificações
        df = pd.read_excel(caminho_planilha)
        
        # APENAS garantir que as colunas existem
        colunas_necessarias = ['loja','peca' ,'codigo', 'imagem', 'preco', 'status', 'quantidade']

        for col in colunas_necessarias:
            if col not in df.columns:
                df[col] = 0 if col in ['preco', 'quantidade'] else ''
        
        # CONVERSÃO MÍNIMA
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
    Cria dados de exemplo para teste com quantidades variadas
    """
    from PIL import Image, ImageDraw
    import os
    
    # Dados com quantidades variadas para teste
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
    
    # Salvar explicitamente como inteiros
    with pd.ExcelWriter(os.path.join(DADOS_DIR, "catalogo.xlsx"), engine='openpyxl') as writer:
        df_exemplo.to_excel(writer, index=False)
    
    # Criar imagens exemplo
    from .config import IMAGENS_DIR
    os.makedirs(IMAGENS_DIR, exist_ok=True)
    
    cores = [(100, 150, 200), (150, 100, 200), (200, 150, 100)]
    
    for i, codigo in enumerate(['PROD-001', 'PROD-002', 'PROD-003']):
        try:
            cor = cores[i % len(cores)]
            img = Image.new('RGB', (300, 300), color=cor)
            d = ImageDraw.Draw(img)
            
            # Desenhar borda
            d.rectangle([10, 10, 290, 290], outline=(255, 255, 255), width=3)
            
            # Adicionar texto
            d.text((80, 140), codigo, fill=(255, 255, 255))
            
            # Salvar
            img.save(os.path.join(IMAGENS_DIR, f"{codigo}.jpg"), quality=95)
        except Exception as e:
            print(f"Erro ao criar imagem {codigo}: {e}")
    
    return True

def verificar_dados():
    """
    Função de diagnóstico para verificar os dados carregados
    """
    df = carregar_dados()
    
    if df.empty:
        st.error("DataFrame vazio")
        return
    
    st.write("### Diagnóstico dos Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Primeiras linhas:**")
        st.dataframe(df[['codigo', 'status', 'quantidade']].head())
        
        st.write("**Tipos dos dados:**")
        st.write(df[['quantidade']].dtypes)
    
    with col2:
        st.write("**Estatísticas da quantidade:**")
        st.write(f"- Mínimo: {df['quantidade'].min()}")
        st.write(f"- Máximo: {df['quantidade'].max()}")
        st.write(f"- Média: {df['quantidade'].mean():.2f}")
        st.write(f"- Total: {df['quantidade'].sum()}")
        
        st.write("**Distribuição por status:**")
        st.write(df['status'].value_counts())