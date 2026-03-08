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
    Renderiza um card de produto com tamanho fixo
    """
    # Encontrar imagem
    caminho, imagem, base64_str, estrategia = image_handler.encontrar_imagem(
        row['imagem'], row['codigo']
    )
    
    # CSS específico para cards
    st.markdown("""
    <style>
                
    .product-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        display: none;
        flex-direction: column;
        margin-bottom: 20px;
                
    }
                
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .product-image-container {
        width: 100%;
        height: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin-bottom: 12px;
    }
    .product-image {
        width: 100%;
        height: 400px;
        object-fit: cover;
        diplay: block; /* inclusão feita por mim - teste */
        transition: transform 0.3s;
    }
    .product-image:hover {
        transform: scale(1.05);
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
    }
    .product-price {
        font-size: 1.4em;
        font-weight: 700;
        color: #2c3e50;
        margin: 8px 0;
    }
    .status-estoque {
        color: #2e7d32;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        background-color: #e8f5e9;
        display: inline-block;
        font-size: 0.85em;
        border: 1px solid #a5d6a7;
    }
    .status-acabou {
        color: #c62828;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        background-color: #ffebee;
        display: inline-block;
        font-size: 0.85em;
        border: 1px solid #ef9a9a;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Card do produto
    with st.container():
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        
        # Container da imagem
        st.markdown('<div class="product-image-container">', unsafe_allow_html=True)
        
        if base64_str:
            ext = os.path.splitext(caminho)[1][1:] if caminho else 'jpg'
            st.markdown(
                f'<img src="data:image/{ext};base64,{base64_str}" class="product-image">',
                unsafe_allow_html=True
            )
        elif imagem:
            img_redimensionada = image_handler.redimensionar_imagem(imagem)
            st.image(img_redimensionada, use_column_width=True)
        else:
            st.markdown("""
            <div style="width:100%; height:100%; display:flex; align-items:center; 
                        justify-content:center; color:white; font-size:32px;">
                📸
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Informações
        st.markdown(f'<div class="product-code">📦 {row["codigo"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="product-store">🏪 {row["loja"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="product-price">R$ {row["preco"]:.2f}</div>', unsafe_allow_html=True)
        
        if row['status'].lower() == 'estoque':
            st.markdown(f'<span class="status-estoque">✅ {int(row["quantidade"])} em estoque</span>', 
                       unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-acabou">❌ Acabou</span>', 
                       unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_product_grid(df_paginado):
    """
    Renderiza grid de produtos
    """
    num_colunas = 4
    
    for i in range(0, len(df_paginado), num_colunas):
        cols = st.columns(num_colunas)
        
        for j in range(num_colunas):
            idx = i + j
            if idx < len(df_paginado):
                with cols[j]:
                    render_product_card(df_paginado.iloc[idx], j)