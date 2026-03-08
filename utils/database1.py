import pandas as pd
import os
from datetime import datetime

CAMINHO_PLANILHA = "dados/catalogo.xlsx"


def carregar_dados():
    """Carrega os dados da planilha Excel"""
    if os.path.exists(CAMINHO_PLANILHA):
        df = pd.read_excel(CAMINHO_PLANILHA)
        # Garantir que as colunas existam
        colunas_necessarias = ['loja','codigo', 'imagem', 'preco', 'status', 'qtd']
        for col in colunas_necessarias:
            if col not in df.columns:
                df[col] = ''
        return df
    else:
        # Criar planilha vazia se não existir
        df = pd.DataFrame(columns=['loja','codigo', 'imagem', 'preco', 'status', 'qtd'])
        salvar_dados(df)
        return df

def salvar_dados(df):
    """Salva os dados na planilha Excel"""
    # Criar pasta dados se não existir
    os.makedirs("dados", exist_ok=True)
    df.to_excel(CAMINHO_PLANILHA, index=False)


def adicionar_produto(codigo, imagem_path, preco):
    """Adiciona um novo produto"""
    df = carregar_dados()
    
    novo_produto = {
        'codigo': codigo,
        'imagem': imagem_path,
        'preco': preco,
        'status': 'em_estoque',
        'cliente': ''
    }
    
    df = pd.concat([df, pd.DataFrame([novo_produto])], ignore_index=True)
    salvar_dados(df)
    return df

def marcar_vendido(codigo, nome_cliente):
    """Marca um produto como vendido"""
    df = carregar_dados()
    df.loc[df['codigo'] == codigo, 'status'] = 'vendido'
    df.loc[df['codigo'] == codigo, 'cliente'] = nome_cliente
    salvar_dados(df)
    return df

def atualizar_produto(codigo, **kwargs):
    """Atualiza informações de um produto"""
    df = carregar_dados()
    for key, value in kwargs.items():
        df.loc[df['codigo'] == codigo, key] = value
    salvar_dados(df)
    return df

def remover_produto(codigo):
    """Remove um produto do catálogo"""
    df = carregar_dados()
    df = df[df['codigo'] != codigo]
    salvar_dados(df)
    return df