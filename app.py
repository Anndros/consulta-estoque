import streamlit as st
import pandas as pd
from PIL import Image
import os
import base64
from datetime import datetime

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Consulta de Produtos",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGENS_DIR = os.path.join(BASE_DIR, "imagens")
DADOS_DIR = os.path.join(BASE_DIR, "dados")

# Criar pastas se não existirem
os.makedirs(IMAGENS_DIR, exist_ok=True)
os.makedirs(DADOS_DIR, exist_ok=True)

# Inicializar session state
if 'css_carregado' not in st.session_state:
    st.session_state.css_carregado = False

# ===== CSS FIXO PARA FORMATAÇÃO CONSISTENTE =====
def carregar_css():
    """Carrega CSS uma única vez"""
    if not st.session_state.css_carregado:
        st.markdown("""
        <style>
        /* Container principal */
        .main {
            padding: 0rem 1rem;
        }
        
        /* Grid de produtos */
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            padding: 20px 0;
        }
        
        /* Card do produto */
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
        }
        
        .product-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Container da imagem - TAMANHO FIXO */
        .product-image-container {
            width: 100%;
            height: 180px;  /* Altura fixa */
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            border-radius: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin-bottom: 12px;
        }
        
        /* Imagem - TAMANHO FIXO */
        .product-image {
            width: 100%;
            height: 100%;
            object-fit: cover;  /* Cobre todo o container sem distorcer */
            transition: transform 0.3s;
        }
        
        .product-image:hover {
            transform: scale(1.05);
        }
        
        /* Informações do produto */
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
        
        /* Status */
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
        
        /* Métricas */
        .metric-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .product-grid {
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 10px;
            }
            
            .product-image-container {
                height: 120px;
            }
            
            .product-price {
                font-size: 1.2em;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.css_carregado = True

# Carregar CSS
carregar_css()

# Título
st.title("🔍 Consulta de Produtos")
st.markdown("---")

# ===== FUNÇÕES DE CARREGAMENTO =====
@st.cache_data(ttl=300)
def carregar_dados():
    """Carrega os dados da planilha"""
    caminho_planilha = os.path.join(DADOS_DIR, "catalogo.xlsx")
    
    if os.path.exists(caminho_planilha):
        df = pd.read_excel(caminho_planilha)
        
        # Garantir colunas
        colunas_necessarias = ['loja', 'codigo', 'imagem', 'preco', 'status', 'quantidade']
        for col in colunas_necessarias:
            if col not in df.columns:
                if col == 'quantidade':
                    df[col] = 0
                elif col == 'preco':
                    df[col] = 0.0
                else:
                    df[col] = ''
        
        # Converter tipos
        df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0)
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype(int)
        
        return df
    return pd.DataFrame()

def encontrar_imagem(caminho_planilha, codigo):
    """Encontra imagem em múltiplos locais"""
    
    if pd.isna(caminho_planilha) or not caminho_planilha:
        caminho_planilha = ""
    
    # Lista de possíveis caminhos
    possiveis_caminhos = []
    
    # 1. Caminho direto
    if caminho_planilha and os.path.exists(caminho_planilha):
        possiveis_caminhos.append(caminho_planilha)
    
    # 2. Na pasta imagens com nome da planilha
    if caminho_planilha:
        nome_arquivo = os.path.basename(caminho_planilha)
        possiveis_caminhos.append(os.path.join(IMAGENS_DIR, nome_arquivo))
    
    # 3. Código + extensões
    for ext in ['.jpg', '.jpeg', '.png']:
        caminho = os.path.join(IMAGENS_DIR, f"{codigo}{ext}")
        possiveis_caminhos.append(caminho)
        
        caminho = os.path.join(IMAGENS_DIR, f"{codigo.lower()}{ext}")
        possiveis_caminhos.append(caminho)
    
    # 4. Procurar qualquer arquivo com o código
    if os.path.exists(IMAGENS_DIR):
        for arquivo in os.listdir(IMAGENS_DIR):
            if codigo.lower() in arquivo.lower() and arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                possiveis_caminhos.append(os.path.join(IMAGENS_DIR, arquivo))
                break
    
    # Tentar cada caminho
    for caminho in possiveis_caminhos:
        if os.path.exists(caminho):
            try:
                return Image.open(caminho)
            except:
                continue
    
    return None

def imagem_para_base64(caminho):
    """Converte imagem para base64"""
    try:
        with open(caminho, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# ===== FUNÇÃO PARA EXIBIR PRODUTO COM TAMANHO FIXO =====
def exibir_produto_card(row):
    """Exibe produto em card com tamanho fixo"""
    
    # Encontrar imagem
    imagem = encontrar_imagem(row['imagem'], row['codigo'])
    caminho = None
    
    # Se encontrou imagem, tentar obter caminho
    if imagem:
        for ext in ['.jpg', '.jpeg', '.png']:
            caminho_teste = os.path.join(IMAGENS_DIR, f"{row['codigo']}{ext}")
            if os.path.exists(caminho_teste):
                caminho = caminho_teste
                break
    
    # Converter para base64 se tiver caminho
    base64_str = imagem_para_base64(caminho) if caminho else None
    
    # Card do produto
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    
    # Container da imagem com tamanho fixo
    st.markdown('<div class="product-image-container">', unsafe_allow_html=True)
    
    if base64_str:
        # Exibir imagem via base64 (tamanho controlado pelo CSS)
        ext = os.path.splitext(caminho)[1][1:] if caminho else 'jpg'
        st.markdown(
            f'<img src="data:image/{ext};base64,{base64_str}" class="product-image">',
            unsafe_allow_html=True
        )
    elif imagem:
        # Usar PIL com redimensionamento forçado
        try:
            img_copy = imagem.copy()
            img_copy.thumbnail((180, 180))  # Redimensionar para tamanho fixo
            st.image(img_copy, use_column_width=True)
        except:
            st.markdown("""
            <div style="width:100%; height:100%; display:flex; align-items:center; 
                        justify-content:center; color:white; font-size:32px;">
                📸
            </div>
            """, unsafe_allow_html=True)
    else:
        # Placeholder
        st.markdown("""
        <div style="width:100%; height:100%; display:flex; align-items:center; 
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
        st.markdown(f'<span class="status-estoque">✅ {int(row["quantidade"])} em estoque</span>', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-acabou">❌ Acabou</span>', 
                   unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.header("🔎 Filtros")
    
    # Carregar dados
    df = carregar_dados()
    
    if not df.empty:
        # Filtro por Loja
        lojas = ['Todas'] + sorted(df['loja'].unique().tolist())
        loja_selecionada = st.selectbox("Selecione a Loja:", lojas)
        
        # Filtro por Status
        status_opcoes = ['Todos', 'Em estoque', 'Acabou']
        status_selecionado = st.radio("Status:", status_opcoes)
        
        # Filtro por Preço
        st.subheader("💰 Faixa de Preço")
        preco_min = float(df['preco'].min())
        preco_max = float(df['preco'].max())
        
        col1, col2 = st.columns(2)
        with col1:
            preco_inicial = st.number_input("Mínimo", value=preco_min, step=10.0)
        with col2:
            preco_final = st.number_input("Máximo", value=preco_max, step=10.0)
        
        # Busca
        busca_codigo = st.text_input("🔍 Buscar código")
        
        # Informações
        st.markdown("---")
        st.caption(f"Total de produtos: {len(df)}")
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
        
        if st.button("🔄 Atualizar"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.error("Nenhum dado encontrado")
        
        # Botão para criar exemplo
        if st.button("📝 Criar dados exemplo"):
            dados_exemplo = {
                'loja': ['Loja Centro', 'Loja Shopping', 'Loja Centro', 'Loja Norte', 'Loja Sul'],
                'codigo': ['PROD-001', 'PROD-002', 'PROD-003', 'PROD-004', 'PROD-005'],
                'imagem': ['', '', '', '', ''],
                'preco': [49.90, 89.90, 129.90, 59.90, 199.90],
                'status': ['estoque', 'estoque', 'acabou', 'estoque', 'acabou'],
                'quantidade': [10, 8, 0, 5, 0]
            }
            df_exemplo = pd.DataFrame(dados_exemplo)
            df_exemplo.to_excel(os.path.join(DADOS_DIR, "catalogo.xlsx"), index=False)
            
            # Criar imagens exemplo
            from PIL import Image, ImageDraw
            for codigo in ['PROD-001', 'PROD-002', 'PROD-003']:
                img = Image.new('RGB', (300, 300), color=(100, 150, 200))
                d = ImageDraw.Draw(img)
                d.text((100, 150), codigo, fill=(255, 255, 255))
                img.save(os.path.join(IMAGENS_DIR, f"{codigo}.jpg"))
            
            st.success("Dados exemplo criados!")
            st.rerun()

# ===== ÁREA PRINCIPAL =====
if not df.empty:
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if loja_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['loja'] == loja_selecionada]
    
    if status_selecionado == "Em estoque":
        df_filtrado = df_filtrado[df_filtrado['status'].str.lower() == 'estoque']
    elif status_selecionado == "Acabou":
        df_filtrado = df_filtrado[df_filtrado['status'].str.lower() == 'acabou']
    
    df_filtrado = df_filtrado[
        (df_filtrado['preco'] >= preco_inicial) & 
        (df_filtrado['preco'] <= preco_final)
    ]
    
    if busca_codigo:
        df_filtrado = df_filtrado[
            df_filtrado['codigo'].str.contains(busca_codigo, case=False, na=False)
        ]
    
    # Métricas
    if not df_filtrado.empty:
        st.subheader(f"📊 {len(df_filtrado)} produtos encontrados")
        
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
            qtd_total = df_filtrado['quantidade'].sum()
            st.metric("Unidades", int(qtd_total))
        
        st.markdown("---")
        
        # ===== GRID DE PRODUTOS COM TAMANHO FIXO =====
        # Calcular número de colunas baseado na largura da tela
        num_colunas = 4  # Fixo em 4 colunas para desktop
        
        # Criar linhas
        for i in range(0, len(df_filtrado), num_colunas):
            cols = st.columns(num_colunas)
            
            for j in range(num_colunas):
                idx = i + j
                if idx < len(df_filtrado):
                    with cols[j]:
                        exibir_produto_card(df_filtrado.iloc[idx])
        
        # Paginação se necessário
        if len(df_filtrado) > 20:
            st.markdown("---")
            st.info(f"Mostrando todos os {len(df_filtrado)} produtos")
            
    else:
        st.warning("Nenhum produto encontrado com os filtros selecionados")
        
        with st.expander("💡 Dicas"):
            st.write("- Aumente a faixa de preço")
            st.write("- Selecione 'Todos' no status")
            st.write("- Tente outra loja")

# ===== RODAPÉ =====
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🏪 Consulta de Produtos")
with col2:
    if not df.empty:
        st.caption(f"📦 Total em estoque: {int(df[df['status'].str.lower() == 'estoque']['quantidade'].sum())} unidades")
with col3:
    st.caption("🎨 Imagens redimensionadas automaticamente")