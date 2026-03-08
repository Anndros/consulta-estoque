"""
Módulo do card de produto - Exibição individual de cada produto
"""
import os
from PIL import Image
import pandas as pd
import streamlit as st
from .image_handler import image_handler
from .config import COLUNAS_GRID

def render_product_card(row, col_index):
    """
    Renderiza um card de produto com tamanho fixo e qualidade preservada
    """
    # Encontrar imagem
    caminho, imagem, base64_str, estrategia = image_handler.encontrar_imagem(
        row['imagem'], row['codigo']
    )
    
    # CSS específico para cards - CORRIGIDO
    st.markdown("""
    <style>
    /* Container principal do card */
    .product-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Container da imagem - TAMANHO FIXO E CENTRALIZADO */
    .product-image-container {
        width: 100%;
        height: 200px;  /* Altura fixa */
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 8px;
        background: #f8f9fa;  /* Fundo neutro */
        margin-bottom: 12px;
        position: relative;
    }
    
    /* Imagem - MANTÉM NITIDEZ E PROPORÇÃO */
    .product-image {
        max-width: 100%;
        max-height: 100%;
        width: auto;
        height: auto;
        object-fit: contain;  /* Mantém proporção sem cortar */
        transition: transform 0.3s;
        display: block;
    }
    
    .product-image:hover {
        transform: scale(1.02);
    }
    
    /* Placeholder quando não há imagem */
    .product-image-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 48px;
        border-radius: 8px;
    }
    
    /* Informações do produto */
    .product-info {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    
    .product-code {
        font-size: 1.1em;
        font-weight: 600;
        color: #2c3e50;
        margin: 8px 0 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .product-store {
        color: #7f8c8d;
        font-size: 0.9em;
        margin: 4px 0;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .product-price {
        font-size: 1.4em;
        font-weight: 700;
        color: #2c3e50;
        margin: 8px 0;
    }
    
    /* Status - CORRIGIDO PARA MOSTRAR QUANTIDADE */
    .status-estoque {
        color: #2e7d32;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 20px;
        background-color: #e8f5e9;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.9em;
        border: 1px solid #a5d6a7;
        width: fit-content;
    }
    
    .status-acabou {
        color: #c62828;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 20px;
        background-color: #ffebee;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.9em;
        border: 1px solid #ef9a9a;
        width: fit-content;
    }
    
    /* Ícone de quantidade */
    .quantity-icon {
        font-size: 1em;
        margin-right: 2px;
    }
    
    /* Remover qualquer elemento estranho */
    .product-card::before,
    .product-card::after {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Card do produto
    with st.container():
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        
        # Container da imagem
        st.markdown('<div class="product-image-container">', unsafe_allow_html=True)
        
        # Exibir imagem com qualidade preservada
        if base64_str:
            # Usar base64 para garantir qualidade
            ext = os.path.splitext(caminho)[1][1:] if caminho else 'jpg'
            st.markdown(
                f'<img src="data:image/{ext};base64,{base64_str}" class="product-image" alt="{row["codigo"]}">',
                unsafe_allow_html=True
            )
        elif imagem:
            # Redimensionar mantendo proporção e qualidade
            try:
                # Calcular proporção para manter qualidade
                img_copy = imagem.copy()
                
                # Usar LANCZOS para melhor qualidade no redimensionamento
                img_copy.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                # Salvar temporariamente para exibir com qualidade
                st.image(img_copy, use_column_width=True, output_format="PNG")
            except Exception as e:
                st.markdown("""
                <div class="product-image-placeholder">
                    📸
                </div>
                """, unsafe_allow_html=True)
        else:
            # Placeholder
            st.markdown("""
            <div class="product-image-placeholder">
                📸
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Informações do produto
        st.markdown('<div class="product-info">', unsafe_allow_html=True)
        
        # Código e loja
        st.markdown(f'<div class="product-code">📦 {row["codigo"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="product-store">🏪 {row["loja"]}</div>', unsafe_allow_html=True)
        
        # Preço
        st.markdown(f'<div class="product-price">R$ {row["preco"]:.2f}</div>', unsafe_allow_html=True)
        
        # Status com quantidade - CORRIGIDO
        if str(row['status']).lower() == 'estoque':
            quantidade = int(row['quantidade']) if pd.notna(row['quantidade']) else 0
            st.markdown(
                f'<span class="status-estoque">'
                f'<span class="quantity-icon">✅</span> '
                f'{quantidade} unidade{"s" if quantidade != 1 else ""} em estoque'
                f'</span>', 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<span class="status-acabou">'
                '<span class="quantity-icon">❌</span> '
                'Acabou'
                '</span>', 
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_product_grid(df_paginado):
    """
    Renderiza grid de produtos com espaçamento consistente
    """
    if df_paginado.empty:
        return
    
    num_colunas = 4
    
    # Container do grid
    st.markdown('<div class="product-grid">', unsafe_allow_html=True)
    
    for i in range(0, len(df_paginado), num_colunas):
        cols = st.columns(num_colunas, gap="medium")
        
        for j in range(num_colunas):
            idx = i + j
            if idx < len(df_paginado):
                with cols[j]:
                    render_product_card(df_paginado.iloc[idx], j)
    
    st.markdown('</div>', unsafe_allow_html=True)