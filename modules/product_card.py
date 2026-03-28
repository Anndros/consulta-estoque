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
    Renderiza um card de produto com tamanho fixo - AGORA COM CAMPO PEÇA
    """
    # Encontrar imagem
    caminho, imagem, base64_str, estrategia = image_handler.encontrar_imagem(
        row['imagem'], row['codigo']
    )
    
    # CSS atualizado
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
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .product-image-container {
        width: 100%;
        height: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 8px;
        background: #f8f9fa;
        margin-bottom: 12px;
    }
    .product-image {
        max-width: 100%;
        max-height: 100%;
        width: auto;
        height: auto;
        object-fit: contain;
        transition: transform 0.3s;
        display: block;
    }
    .product-image:hover {
        transform: scale(1.02);
    }
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
    .product-type {
        font-size: 0.9em;
        color: #7f8c8d;
        margin: 2px 0;
        display: flex;
        align-items: center;
        gap: 4px;
        background: #f1f3f4;
        padding: 2px 8px;
        border-radius: 16px;
        width: fit-content;
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
    .status-estoque {
        color: #2e7d32;
        font-weight: 600;
        padding: 8px 16px;
        border-radius: 30px;
        background-color: #e8f5e9;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.95em;
        border: 1px solid #a5d6a7;
        width: fit-content;
        margin-top: 5px;
    }
    .status-acabou {
        color: #c62828;
        font-weight: 600;
        padding: 8px 16px;
        border-radius: 30px;
        background-color: #ffebee;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.95em;
        border: 1px solid #ef9a9a;
        width: fit-content;
        margin-top: 5px;
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
                f'<img src="data:image/{ext};base64,{base64_str}" class="product-image" alt="{row["codigo"]}">',
                unsafe_allow_html=True
            )
        elif imagem:
            try:
                img_copy = imagem.copy()
                img_copy.thumbnail((180, 180), Image.Resampling.LANCZOS)
                st.image(img_copy, use_column_width=True, output_format="PNG")
            except:
                st.markdown('<div class="product-image-placeholder">📸</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="product-image-placeholder">📸</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Informações do produto
        st.markdown('<div class="product-info">', unsafe_allow_html=True)
        
        # Código
        st.markdown(f'<div class="product-code">📦 {row["codigo"]}</div>', unsafe_allow_html=True)
        
        # NOVO: Tipo de Peça
        peca = str(row["peca"]) if pd.notna(row["peca"]) and row["peca"] else "Não especificado"
        st.markdown(f'<div class="product-type">👕 {peca}</div>', unsafe_allow_html=True)
        
        # Loja
        st.markdown(f'<div class="product-store">🏪 {row["loja"]}</div>', unsafe_allow_html=True)
        
        # Preço
        try:
            preco = float(row["preco"])
            st.markdown(f'<div class="product-price">R$ {preco:.2f}</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div class="product-price">R$ 0,00</div>', unsafe_allow_html=True)
        
        # Status com quantidade
        status = str(row["status"]).lower().strip()
        
        try:
            quantidade = int(float(row["quantidade"])) if pd.notna(row["quantidade"]) else 0
        except:
            quantidade = 0
        
        if status == 'estoque':
            if quantidade > 0:
                st.markdown(
                    f'<span class="status-estoque">'
                    f'✅ {quantidade} unidade{"s" if quantidade != 1 else ""}'
                    f'</span>', 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<span class="status-estoque">'
                    f'⚠️ Estoque zerado'
                    f'</span>', 
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                '<span class="status-acabou">'
                '❌ Esgotado'
                '</span>', 
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_product_grid(df_paginado):
    """
    Renderiza grid de produtos
    """
    if df_paginado.empty:
        st.info("Nenhum produto para exibir")
        return
    
    num_colunas = 4
    
    for i in range(0, len(df_paginado), num_colunas):
        cols = st.columns(num_colunas, gap="medium")
        
        for j in range(num_colunas):
            idx = i + j
            if idx < len(df_paginado):
                with cols[j]:
                    render_product_card(df_paginado.iloc[idx], j)