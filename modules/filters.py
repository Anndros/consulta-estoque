"""
Módulo de filtros - Aplicação de filtros aos dados
"""
import pandas as pd

def aplicar_filtros(df, filtros):
    """
    Aplica todos os filtros ao DataFrame
    """
    if df.empty:
        return df
    
    df_filtrado = df.copy()
    
    # Filtro por loja
    if filtros['loja'] != "Todas":
        df_filtrado = df_filtrado[df_filtrado['loja'] == filtros['loja']]
    
    # Filtro por status
    if filtros['status'] == "Em estoque":
        df_filtrado = df_filtrado[df_filtrado['status'].str.lower() == 'estoque']
    elif filtros['status'] == "Acabou":
        df_filtrado = df_filtrado[df_filtrado['status'].str.lower() == 'acabou']
    
    # Filtro por preço
    df_filtrado = df_filtrado[
        (df_filtrado['preco'] >= filtros['preco_min']) & 
        (df_filtrado['preco'] <= filtros['preco_max'])
    ]
    
    # Filtro por busca
    if filtros['busca']:
        df_filtrado = df_filtrado[
            df_filtrado['codigo'].str.contains(filtros['busca'], case=False, na=False)
        ]
    
    return df_filtrado

def paginar_dados(df, pagina, itens_por_pagina):
    """
    Retorna apenas os dados da página solicitada
    """
    inicio = (pagina - 1) * itens_por_pagina
    fim = min(inicio + itens_por_pagina, len(df))
    
    return df.iloc[inicio:fim], inicio, fim