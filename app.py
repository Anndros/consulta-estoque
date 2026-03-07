import streamlit as st
import pandas as pd
from PIL import Image
import os
import sys
from datetime import datetime

# Configuração da página - DEVE SER O PRIMEIRO COMANDO STREAMLIT
st.set_page_config(
    page_title="Consulta de Produtos",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar versões das bibliotecas (útil para debug)
st.sidebar.write("📦 Versões:")
st.sidebar.write(f"Python: {sys.version.split()[0]}")
st.sidebar.write(f"Streamlit: {st.__version__}")
st.sidebar.write(f"Pandas: {pd.__version__}")


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

# Função para carregar dados com cache
@st.cache_data(ttl=60)  # Atualiza a cada 60 segundos
def carregar_dados():
    """Carrega os dados da planilha Excel"""
    caminho_planilha = os.path.join("dados", "catalogo.xlsx")
    
    if os.path.exists(caminho_planilha):
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
        
        # Converter preço para float
        df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0)
        
        # Converter quantidade para int
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype(int)
        
        return df
    else:
        st.error("Arquivo de dados não encontrado em: " + caminho_planilha)
        return pd.DataFrame()

def encontrar_imagem(caminho_imagem, codigo_produto):
    """
    Tenta encontrar a imagem em diferentes locais
    """
    if pd.isna(caminho_imagem) or not caminho_imagem:
        caminho_imagem = ""
    
    # Lista de possíveis caminhos para tentar
    possiveis_caminhos = []
    
    # 1. Caminho original como está
    if caminho_imagem and isinstance(caminho_imagem, str):
        possiveis_caminhos.append(caminho_imagem)
        
        # 2. Apenas o nome do arquivo na pasta imagens
        nome_arquivo = os.path.basename(caminho_imagem)
        possiveis_caminhos.append(os.path.join(IMAGENS_DIR, nome_arquivo))
    
    # 3. Nome baseado no código do produto (formatos comuns)
    extensoes = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    for ext in extensoes:
        possiveis_caminhos.append(os.path.join(IMAGENS_DIR, f"{codigo_produto}{ext}"))
        possiveis_caminhos.append(os.path.join(IMAGENS_DIR, f"{codigo_produto.lower()}{ext}"))
        possiveis_caminhos.append(os.path.join(IMAGENS_DIR, f"img_{codigo_produto}{ext}"))
    
    # 4. Procurar em subpastas
    if os.path.exists(IMAGENS_DIR):
        for root, dirs, files in os.walk(IMAGENS_DIR):
            for file in files:
                if codigo_produto.lower() in file.lower():
                    possiveis_caminhos.append(os.path.join(root, file))
    
    # Tentar cada caminho
    for caminho in possiveis_caminhos:
        try:
            if os.path.exists(caminho):
                # Verificar se é um arquivo de imagem válido
                ext = os.path.splitext(caminho)[1].lower()
                if ext in SUPPORTED_IMAGES:
                    return Image.open(caminho)
        except:
            continue
    
    return None

def exibir_produto_com_imagem(row):
    """
    Função para exibir produto com imagem em formato de card
    """
    # Criar card com borda
    st.markdown("""
    <style>
    .product-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-estoque {
        color: green;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 3px;
        background-color: #e8f5e8;
        display: inline-block;
    }
    .status-acabou {
        color: red;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 3px;
        background-color: #ffe8e8;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Layout do card
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Tentar encontrar a imagem
        imagem = encontrar_imagem(row['imagem'], row['codigo'])
        
        if imagem:
            # Redimensionar imagem para tamanho padrão
            imagem.thumbnail((500, 500))
            st.image(imagem, use_column_width=True)
        else:
            # Placeholder com ícone
            st.markdown("""
            <div style="width:100%; height:150px; background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius:10px; display:flex; align-items:center; justify-content:center; color:white;
                        font-size:48px;">
                📸
            </div>
            <p style="text-align:center; color:#666; font-size:12px; margin-top:5px;">
                Imagem não disponível
            </p>
            """, unsafe_allow_html=True)
            
            # Debug: mostrar caminhos tentados (opcional - comentar em produção)
            # with st.expander("Debug"):
            #     st.write(f"Código: {row['codigo']}")
            #     st.write(f"Caminho na planilha: {row['imagem']}")
    
    with col2:
        # Informações do produto
        st.markdown(f"### 📦 {row['codigo']}")
        
        # Loja com ícone
        st.markdown(f"🏪 **Loja:** {row['loja']}")
        
        # Preço em destaque
        st.markdown(f"### 💰 R$ {row['preco']:.2f}")
        
        # Status com estilo
        if row['status'].lower() == 'estoque':
            st.markdown(f'<span class="status-estoque">✅ EM ESTOQUE</span>', unsafe_allow_html=True)
            st.markdown(f"📊 **Quantidade:** {row['quantidade']} unidades")
        else:
            st.markdown(f'<span class="status-acabou">❌ ACABOU</span>', unsafe_allow_html=True)
            st.markdown(f"📊 **Quantidade:** 0 unidades")
        
        # Linha separadora
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

# Carregar dados
df = carregar_dados()

# Sidebar para filtros
with st.sidebar:
    st.header("🔎 Filtros")
    
    # Informações do sistema (opcional - pode remover depois)
    with st.expander("ℹ️ Info"):
        st.write(f"Pasta imagens: {IMAGENS_DIR}")
        if os.path.exists(IMAGENS_DIR):
            qtd_imagens = len([f for f in os.listdir(IMAGENS_DIR) if f.lower().endswith(tuple(SUPPORTED_IMAGES))])
            st.write(f"Imagens encontradas: {qtd_imagens}")
    
    # Filtro por Loja
    if not df.empty and 'loja' in df.columns:
        lojas = ['Todas'] + sorted(df['loja'].dropna().unique().tolist())
        loja_selecionada = st.selectbox("Selecione a Loja:", lojas)
    else:
        loja_selecionada = "Todas"
        st.warning("Nenhuma loja encontrada")
    
    # Filtro por Status
    status_opcoes = ['Todos', 'Em estoque', 'Acabou']
    status_selecionado = st.radio("Status:", status_opcoes)
    
    # Filtro por Preço
    st.subheader("💰 Faixa de Preço")
    if not df.empty and 'preco' in df.columns and len(df) > 0:
        preco_min = float(df['preco'].min())
        preco_max = float(df['preco'].max())
        
        col1, col2 = st.columns(2)
        with col1:
            preco_inicial = st.number_input("Mínimo (R$)", 
                                           min_value=0.0, 
                                           value=preco_min,
                                           step=10.0)
        with col2:
            preco_final = st.number_input("Máximo (R$)", 
                                         min_value=0.0, 
                                         value=preco_max,
                                         step=10.0)
    else:
        preco_inicial = 0
        preco_final = 1000
    
    # Busca por código
    st.markdown("---")
    st.subheader("🔍 Busca Rápida")
    busca_codigo = st.text_input("Digite o código do produto:")
    
    # Informações de atualização
    st.markdown("---")
    st.caption(f"🕐 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    if st.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()

# Área principal
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
        # Métricas em cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Produtos", len(df_filtrado))
        
        with col2:
            em_estoque = len(df_filtrado[df_filtrado['status'].str.lower() == 'estoque'])
            st.metric("Em Estoque", em_estoque)
        
        with col3:
            acabou = len(df_filtrado[df_filtrado['status'].str.lower() == 'acabou'])
            st.metric("Acabou", acabou)
        
        with col4:
            quantidade_total = df_filtrado['quantidade'].sum()
            st.metric("Quantidade Total", int(quantidade_total))
        
        st.markdown("---")
        
        # Exibir produtos
        st.subheader(f"📸 Produtos da {loja_selecionada if loja_selecionada != 'Todas' else 'Todas as Lojas'}")
        
        # Criar linhas com 2 colunas para melhor visualização
        for i in range(0, len(df_filtrado), 2):
            cols = st.columns(2)
            
            # Primeiro produto da linha
            if i < len(df_filtrado):
                with cols[0]:
                    exibir_produto_com_imagem(df_filtrado.iloc[i])
            
            # Segundo produto da linha
            if i + 1 < len(df_filtrado):
                with cols[1]:
                    exibir_produto_com_imagem(df_filtrado.iloc[i + 1])
            
            # Linha separadora entre grupos
            st.markdown("---")
        
        # Mostrar quantidade de resultados
        st.info(f"🔍 Encontrados {len(df_filtrado)} produtos")
        
    else:
        st.warning("❌ Nenhum produto encontrado com os filtros selecionados.")
        
        # Sugestões
        with st.expander("💡 Dicas para encontrar produtos"):
            st.write("- Aumente a faixa de preço")
            st.write("- Selecione 'Todos' no status")
            st.write("- Tente outra loja")
            st.write("- Verifique se o código foi digitado corretamente")
else:
    st.error("""
    ❌ Não foi possível carregar os dados.
    
    Verifique:
    1. Se a pasta 'dados' existe
    2. Se o arquivo 'catalogo.xlsx' está na pasta dados
    3. Se o arquivo tem as colunas: loja, codigo, imagem, preco, status, quantidade
    """)

# Rodapé
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🏪 Sistema de Consulta de Produtos")
with col2:
    st.caption(f"📊 {len(df)} produtos cadastrados" if not df.empty else "📊 Nenhum produto")
with col3:
    st.caption("🔄 Dados atualizados em tempo real")

# Script de diagnóstico (opcional - pode remover em produção)
if st.checkbox("🔧 Mostrar diagnóstico"):
    st.header("Diagnóstico do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pastas")
        st.write(f"Diretório base: {BASE_DIR}")
        st.write(f"Pasta imagens: {IMAGENS_DIR}")
        st.write(f"Pasta imagens existe: {os.path.exists(IMAGENS_DIR)}")
        
        if os.path.exists(IMAGENS_DIR):
            arquivos = os.listdir(IMAGENS_DIR)
            st.write(f"Arquivos na pasta imagens: {len(arquivos)}")
            if arquivos:
                st.write("Primeiros 5 arquivos:")
                for arquivo in arquivos[:5]:
                    st.write(f"- {arquivo}")
    
    with col2:
        st.subheader("Planilha")
        if not df.empty:
            st.write(f"Total de linhas: {len(df)}")
            st.write(f"Colunas: {list(df.columns)}")
            st.write(f"Lojas: {df['loja'].unique().tolist()}")
            
            st.subheader("Primeiros 5 produtos")
            for idx, row in df.head().iterrows():
                st.write(f"**{row['codigo']}**")
                st.write(f"- Loja: {row['loja']}")
                st.write(f"- Imagem: {row['imagem']}")
                st.write(f"- Existe: {os.path.exists(row['imagem']) if pd.notna(row['imagem']) else False}")
                st.write("---")