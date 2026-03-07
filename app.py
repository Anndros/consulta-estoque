import streamlit as st
import pandas as pd
from PIL import Image
import os
from datetime import datetime

# ===== CONFIGURAÇÃO DA PÁGINA - PRIMEIRO COMANDO STREAMLIT =====
st.set_page_config(
    page_title="Consulta de Produtos",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)
# =================================================================

# Inicializar session state para cache
if 'filtros_anteriores' not in st.session_state:
    st.session_state.filtros_anteriores = {}
if 'resultados_cache' not in st.session_state:
    st.session_state.resultados_cache = None
if 'cache_caminhos' not in st.session_state:
    st.session_state.cache_caminhos = {}
if 'css_carregado' not in st.session_state:
    st.session_state.css_carregado = False

# Configurar caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGENS_DIR = os.path.join(BASE_DIR, "imagens")

# Criar pasta de imagens se não existir
os.makedirs(IMAGENS_DIR, exist_ok=True)

# Formatos de imagem suportados
SUPPORTED_IMAGES = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

# Título principal
st.title("🔍 Consulta de Produtos por Loja")
st.markdown("---")

# ===== FUNÇÕES OTIMIZADAS COM CACHE =====

@st.cache_data(ttl=300, max_entries=10, show_spinner=False)
def carregar_dados():
    """Carrega os dados da planilha Excel com cache otimizado"""
    caminho_planilha = os.path.join("dados", "catalogo.xlsx")
    
    if os.path.exists(caminho_planilha):
        # Carregar apenas as colunas necessárias
        df = pd.read_excel(caminho_planilha)
        
        # Garantir que as colunas existam
        colunas_necessarias = ['loja', 'codigo', 'imagem', 'preco', 'status', 'quantidade']
        for col in colunas_necessarias:
            if col not in df.columns:
                if col == 'quantidade':
                    df[col] = 0
                elif col == 'preco':
                    df[col] = 0.0
                else:
                    df[col] = ''
        
        # Otimizar tipos de dados para economizar memória
        df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0).astype('float32')
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype('int16')
        df['status'] = df['status'].astype('category')
        df['loja'] = df['loja'].astype('category')
        
        return df
    else:
        return pd.DataFrame()

@st.cache_data(ttl=3600, max_entries=50, show_spinner=False)
def carregar_imagem_caminho(caminho):
    """Carrega imagem com cache para evitar leituras repetidas"""
    if os.path.exists(caminho):
        try:
            return Image.open(caminho)
        except:
            return None
    return None

def encontrar_imagem(caminho_imagem, codigo_produto):
    """Versão otimizada com cache de caminhos"""
    if pd.isna(caminho_imagem) or not caminho_imagem:
        caminho_imagem = ""
    
    # Verificar se já encontramos esse caminho antes
    cache_key = f"{codigo_produto}_{caminho_imagem}"
    if cache_key in st.session_state.cache_caminhos:
        caminho_encontrado = st.session_state.cache_caminhos[cache_key]
        if caminho_encontrado and os.path.exists(caminho_encontrado):
            return carregar_imagem_caminho(caminho_encontrado)
        return None
    
    # Lista prioritária de caminhos (mais prováveis primeiro)
    possiveis_caminhos = []
    
    # 1. Caminho direto na pasta imagens com nome do código
    extensoes = ['.jpg', '.jpeg', '.png']
    for ext in extensoes:
        possiveis_caminhos.append(os.path.join(IMAGENS_DIR, f"{codigo_produto}{ext}"))
        possiveis_caminhos.append(os.path.join(IMAGENS_DIR, f"{codigo_produto.lower()}{ext}"))
    
    # 2. Caminho da planilha
    if caminho_imagem and isinstance(caminho_imagem, str):
        possiveis_caminhos.append(caminho_imagem)
        nome_arquivo = os.path.basename(caminho_imagem)
        possiveis_caminhos.append(os.path.join(IMAGENS_DIR, nome_arquivo))
    
    # 3. Variações comuns
    if codigo_produto:
        codigo_limpo = codigo_produto.replace('-', '').replace('_', '')
        for ext in extensoes:
            possiveis_caminhos.append(os.path.join(IMAGENS_DIR, f"{codigo_limpo}{ext}"))
    
    # Tentar cada caminho (limitado para economizar)
    for caminho in possiveis_caminhos[:8]:  # Limitar tentativas
        try:
            if os.path.exists(caminho):
                st.session_state.cache_caminhos[cache_key] = caminho
                return carregar_imagem_caminho(caminho)
        except:
            continue
    
    st.session_state.cache_caminhos[cache_key] = None
    return None

def exibir_produto_com_imagem(row):
    """Versão otimizada com lazy loading e cache"""
    
    # CSS único (carregar apenas uma vez)
    if not st.session_state.css_carregado:
        st.markdown("""
        <style>
        .product-card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 15px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            height: 100%;
        }
        .product-card:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .status-estoque {
            color: #2e7d32;
            font-weight: bold;
            padding: 4px 10px;
            border-radius: 20px;
            background-color: #e8f5e9;
            display: inline-block;
            font-size: 0.85em;
            border: 1px solid #a5d6a7;
        }
        .status-acabou {
            color: #c62828;
            font-weight: bold;
            padding: 4px 10px;
            border-radius: 20px;
            background-color: #ffebee;
            display: inline-block;
            font-size: 0.85em;
            border: 1px solid #ef9a9a;
        }
        .product-image-container {
            width: 100%;
            height: 140px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            border-radius: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin-bottom: 10px;
        }
        .product-code {
            font-size: 1.1em;
            font-weight: bold;
            color: #333;
            margin: 5px 0;
        }
        .product-price {
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            margin: 5px 0;
        }
        .product-store {
            color: #666;
            font-size: 0.9em;
            margin: 5px 0;
        }
        .product-info {
            padding: 5px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.css_carregado = True
    
    # Usar session_state para cache de imagens carregadas
    imagem_key = f"img_{row['codigo']}"
    if imagem_key not in st.session_state:
        with st.spinner(''):  # Spinner vazio para não mostrar loading
            st.session_state[imagem_key] = encontrar_imagem(row['imagem'], row['codigo'])
    
    imagem = st.session_state[imagem_key]
    
    # Layout em card único
    with st.container():
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        
        # Container da imagem
        st.markdown('<div class="product-image-container">', unsafe_allow_html=True)
        if imagem:
            # Redimensionar para tamanho fixo
            img_copy = imagem.copy()
            img_copy.thumbnail((140, 140))
            st.image(img_copy, use_column_width=True)
        else:
            st.markdown("""
            <div style="width:100%; height:140px; display:flex; align-items:center; 
                        justify-content:center; color:white; font-size:32px;">
                📸
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Informações do produto
        st.markdown(f'<div class="product-code">📦 {row["codigo"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="product-store">🏪 {row["loja"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="product-price">R$ {row["preco"]:.2f}</div>', unsafe_allow_html=True)
        
        # Status
        if row['status'].lower() == 'estoque':
            st.markdown(f'<span class="status-estoque">✅ {row["quantidade"]} em estoque</span>', 
                       unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-acabou">❌ Acabou</span>', 
                       unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ===== CARREGAR DADOS =====
df = carregar_dados()

# ===== SIDEBAR COM FILTROS =====
with st.sidebar:
    st.header("🔎 Filtros")
    
    # Status do cache (informação útil)
    st.caption(f"📦 {len(df)} produtos cadastrados" if not df.empty else "📦 Nenhum produto")
    
    # Filtro por Loja
    if not df.empty and 'loja' in df.columns:
        lojas = ['Todas'] + sorted(df['loja'].cat.categories.tolist())
        loja_selecionada = st.selectbox("Selecione a Loja:", lojas, key='filtro_loja')
    else:
        loja_selecionada = "Todas"
        st.warning("Nenhuma loja encontrada")
    
    # Filtro por Status
    status_opcoes = ['Todos', 'Em estoque', 'Acabou']
    status_selecionado = st.radio("Status:", status_opcoes, key='filtro_status')
    
    # Filtro por Preço
    st.subheader("💰 Faixa de Preço")
    if not df.empty and 'preco' in df.columns and len(df) > 0:
        preco_min = float(df['preco'].min())
        preco_max = float(df['preco'].max())
        
        col1, col2 = st.columns(2)
        with col1:
            preco_inicial = st.number_input("Mínimo", 
                                           min_value=0.0, 
                                           value=preco_min,
                                           step=10.0,
                                           format="%.0f",
                                           key='preco_min')
        with col2:
            preco_final = st.number_input("Máximo", 
                                         min_value=0.0, 
                                         value=preco_max,
                                         step=10.0,
                                         format="%.0f",
                                         key='preco_max')
    else:
        preco_inicial = 0
        preco_final = 1000
    
    # Busca por código
    st.markdown("---")
    st.subheader("🔍 Busca Rápida")
    busca_codigo = st.text_input("Digite o código:", key='busca_codigo')
    
    # Informações de atualização
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"🕐 {datetime.now().strftime('%H:%M')}")
    with col2:
        if st.button("🔄", help="Atualizar dados"):
            st.cache_data.clear()
            st.session_state.cache_caminhos = {}
            st.rerun()

# ===== ÁREA PRINCIPAL =====
st.header("📦 Produtos Encontrados")

# Aplicar filtros
if not df.empty:
    df_filtrado = df.copy()
    
    # Filtrar por loja
    if loja_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['loja'] == loja_selecionada]
    
    # Filtrar por status
    if status_selecionado == "Em estoque":
        df_filtrado = df_filtrado[df_filtrado['status'].str.lower() == 'estoque']
    elif status_selecionado == "Acabou":
        df_filtrado = df_filtrado[df_filtrado['status'].str.lower() == 'acabou']
    
    # Filtrar por preço
    df_filtrado = df_filtrado[
        (df_filtrado['preco'] >= preco_inicial) & 
        (df_filtrado['preco'] <= preco_final)
    ]
    
    # Filtrar por código
    if busca_codigo:
        df_filtrado = df_filtrado[
            df_filtrado['codigo'].str.contains(busca_codigo, case=False, na=False)
        ]
    
    # Estatísticas rápidas
    if not df_filtrado.empty:
        # Métricas em linha
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", len(df_filtrado))
        
        with col2:
            em_estoque = len(df_filtrado[df_filtrado['status'].str.lower() == 'estoque'])
            st.metric("Em Estoque", em_estoque)
        
        with col3:
            acabou = len(df_filtrado[df_filtrado['status'].str.lower() == 'acabou'])
            st.metric("Acabou", acabou)
        
        with col4:
            quantidade_total = df_filtrado['quantidade'].sum()
            st.metric("Qtd Total", int(quantidade_total))
        
        st.markdown("---")
        
        # ===== PAGINAÇÃO =====
        ITENS_POR_PAGINA = 12  # 3 linhas de 4 colunas
        
        # Calcular número de páginas
        total_paginas = (len(df_filtrado) + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA
        
        # Controles de página
        if total_paginas > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Inicializar página atual no session state
                if 'pagina_atual' not in st.session_state:
                    st.session_state.pagina_atual = 1
                
                # Seletor de página
                pagina = st.number_input(
                    f"Página", 
                    min_value=1, 
                    max_value=total_paginas, 
                    value=st.session_state.pagina_atual,
                    key='seletor_pagina'
                )
                st.session_state.pagina_atual = pagina
        else:
            pagina = 1
        
        # Calcular índices
        inicio = (pagina - 1) * ITENS_POR_PAGINA
        fim = min(inicio + ITENS_POR_PAGINA, len(df_filtrado))
        
        # Mostrar apenas os itens da página atual
        df_paginado = df_filtrado.iloc[inicio:fim]
        
        # Título com informação de paginação
        st.subheader(f"📸 Mostrando {inicio+1}-{fim} de {len(df_filtrado)} produtos")
        
        # Exibir produtos em grid de 4 colunas
        cols = st.columns(4)
        
        for idx, (_, row) in enumerate(df_paginado.iterrows()):
            with cols[idx % 4]:
                exibir_produto_com_imagem(row)
        
        # Navegação rápida (botões)
        if total_paginas > 1:
            st.markdown("---")
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if pagina > 1 and st.button("⏮️ Primeira"):
                    st.session_state.pagina_atual = 1
                    st.rerun()
            
            with col2:
                if pagina > 1 and st.button("◀ Anterior"):
                    st.session_state.pagina_atual = pagina - 1
                    st.rerun()
            
            with col3:
                st.write(f"Página {pagina} de {total_paginas}")
            
            with col4:
                if pagina < total_paginas and st.button("Próxima ▶"):
                    st.session_state.pagina_atual = pagina + 1
                    st.rerun()
            
            with col5:
                if pagina < total_paginas and st.button("⏭️ Última"):
                    st.session_state.pagina_atual = total_paginas
                    st.rerun()
        
    else:
        # Mensagem quando não encontra produtos
        st.warning("❌ Nenhum produto encontrado")
        
        with st.expander("💡 Dicas"):
            st.write("""
            - Aumente a faixa de preço
            - Selecione 'Todos' no status
            - Tente outra loja
            - Verifique o código digitado
            """)
else:
    # Mensagem de erro quando não carrega dados
    st.error("""
    ❌ Dados não encontrados
    
    **Verifique:**
    1. A pasta 'dados' existe
    2. O arquivo 'catalogo.xlsx' está na pasta
    3. As colunas: loja, codigo, imagem, preco, status, quantidade
    """)
    
    # Mostrar estrutura para debug
    with st.expander("🔧 Debug - Estrutura de pastas"):
        st.write("Arquivos no diretório:")
        for item in os.listdir('.'):
            st.write(f"- {item}")
        
        if os.path.exists('dados'):
            st.write("\nArquivos em 'dados':")
            for item in os.listdir('dados'):
                st.write(f"- {item}")

# ===== RODAPÉ =====
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🏪 Consulta de Produtos")
with col2:
    if not df.empty:
        total_estoque = df[df['status'].str.lower() == 'estoque']['quantidade'].sum()
        st.caption(f"📦 Total em estoque: {int(total_estoque)} unidades")
with col3:
    st.caption(f"🔄 Cache: 5min")

# Botão invisível para atualizar (atalho)
if st.button("🎯", key="hidden_refresh", help="Atalho para atualizar"):
    st.cache_data.clear()
    st.session_state.cache_caminhos = {}
    st.rerun()