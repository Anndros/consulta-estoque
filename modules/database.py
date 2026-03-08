"""
Módulo de banco de dados - Carregamento e cache da planilha
"""
import streamlit as st
import pandas as pd
import os
import numpy as np
from .config import DADOS_DIR, CACHE_TTL_DADOS

@st.cache_data(ttl=CACHE_TTL_DADOS, show_spinner="Carregando dados...")
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
        # Carregar planilha mantendo os tipos originais
        df = pd.read_excel(caminho_planilha, dtype={
            'loja': str,
            'codigo': str,
            'imagem': str,
            'preco': float,
            'status': str,
            'quantidade': int  # Forçar tipo inteiro
        })
        
        # Verificar se as colunas necessárias existem
        colunas_necessarias = ['loja', 'codigo', 'imagem', 'preco', 'status', 'quantidade']
        colunas_existentes = df.columns.tolist()
        
        for col in colunas_necessarias:
            if col not in colunas_existentes:
                if col == 'quantidade':
                    df[col] = 0
                elif col == 'preco':
                    df[col] = 0.0
                else:
                    df[col] = ''
        
        # CONVERSÕES CORRIGIDAS
        # Preço
        if 'preco' in df.columns:
            df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0).astype(float)
        
        # QUANTIDADE - CORREÇÃO PRINCIPAL
        if 'quantidade' in df.columns:
            # Primeiro, converter para numérico, tratando erros
            df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce')
            # Depois, preencher NaN com 0
            df['quantidade'] = df['quantidade'].fillna(0)
            # Por fim, converter para inteiro
            df['quantidade'] = df['quantidade'].astype(int)
        else:
            df['quantidade'] = 0
        
        # Status - garantir string e lower case
        if 'status' in df.columns:
            df['status'] = df['status'].fillna('').astype(str).str.lower().str.strip()
            # Mapear variações comuns
            df['status'] = df['status'].replace({
                'em estoque': 'estoque',
                'em_estoque': 'estoque',
                'disponivel': 'estoque',
                'disponível': 'estoque',
                'acabou': 'acabou',
                'esgotado': 'acabou',
                'vendido': 'acabou'
            })
            # Se vazio, definir como 'acabou'
            df.loc[df['status'] == '', 'status'] = 'acabou'
        
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
        'loja': ['Loja Centro', 'Loja Shopping', 'Loja Centro', 'Loja Norte', 'Loja Sul', 'Loja Centro'],
        'codigo': ['PROD-001', 'PROD-002', 'PROD-003', 'PROD-004', 'PROD-005', 'PROD-006'],
        'imagem': ['', '', '', '', '', ''],
        'preco': [49.90, 89.90, 129.90, 59.90, 199.90, 34.90],
        'status': ['estoque', 'estoque', 'acabou', 'estoque', 'acabou', 'estoque'],
        'quantidade': [15, 8, 0, 3, 0, 1]  # Diferentes quantidades
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