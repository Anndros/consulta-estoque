import streamlit as st
import pandas as pd
from PIL import Image
import os
import base64
from datetime import datetime
import glob

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
DADOS_DIR = os.path.join(BASE_DIR, "dados")

# Criar pastas se não existirem
os.makedirs(IMAGENS_DIR, exist_ok=True)
os.makedirs(DADOS_DIR, exist_ok=True)

# Formatos de imagem suportados
SUPPORTED_IMAGES = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

# Título principal
st.title("🔍 Consulta de Produtos por Loja")
st.markdown("---")

# ===== FUNÇÃO DE DIAGNÓSTICO =====
def diagnosticar_imagens():
    """Função para diagnosticar problemas com imagens"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Diagnóstico")
    
    with st.sidebar.expander("Ver diagnóstico completo", expanded=False):
        st.write("**Pastas:**")
        st.write(f"- Diretório base: {BASE_DIR}")
        st.write(f"- Pasta imagens existe: {os.path.exists(IMAGENS_DIR)}")
        st.write(f"- Pasta dados existe: {os.path.exists(DADOS_DIR)}")
        
        if os.path.exists(IMAGENS_DIR):
            imagens = [f for f in os.listdir(IMAGENS_DIR) 
                      if f.lower().endswith(tuple(SUPPORTED_IMAGES))]
            st.write(f"- Imagens encontradas: {len(imagens)}")
            if len(imagens) > 0:
                st.write("**Primeiras 10 imagens:**")
                for img in imagens[:10]:
                    st.write(f"  • {img}")
            else:
                st.warning("Nenhuma imagem encontrada na pasta!")
        
        st.write("\n**Planilha:**")
        planilha_path = os.path.join(DADOS_DIR, "catalogo.xlsx")
        st.write(f"- Planilha existe: {os.path.exists(planilha_path)}")
        
        if os.path.exists(planilha_path):
            try:
                df_teste = pd.read_excel(planilha_path)
                st.write(f"- Linhas: {len(df_teste)}")
                st.write(f"- Colunas: {list(df_teste.columns)}")
            except Exception as e:
                st.error(f"Erro ao ler planilha: {e}")

# ===== FUNÇÕES DE CARREGAMENTO =====
@st.cache_data(ttl=300, max_entries=10, show_spinner=False)
def carregar_dados():
    """Carrega os dados da planilha Excel com cache otimizado"""
    caminho_planilha = os.path.join(DADOS_DIR, "catalogo.xlsx")
    
    if os.path.exists(caminho_planilha):
        try:
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
            
            # Otimizar tipos de dados
            df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0).astype('float32')
            df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype('int16')
            df['status'] = df['status'].astype('category')
            df['loja'] = df['loja'].astype('category')
            
            return df
        except Exception as e:
            st.error(f"Erro ao carregar planilha: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

@st.cache_data(ttl=3600, max_entries=100, show_spinner=False)
def carregar_imagem_caminho(caminho):
    """Carrega imagem com cache para evitar leituras repetidas"""
    try:
        if os.path.exists(caminho):
            return Image.open(caminho)
    except:
        pass
    return None

def imagem_para_base64(caminho_imagem):
    """Converte imagem para base64 (100% garantido de exibição)"""
    try:
        with open(caminho_imagem, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def encontrar_imagem_ultra(caminho_planilha, codigo):
    """
    Estratégia SUPER otimizada para encontrar imagens
    Retorna: (caminho_encontrado, imagem_object, estrategia_usada, base64_string)
    """
    
    # Verificar cache primeiro
    cache_key = f"{codigo}_{caminho_planilha}"
    if cache_key in st.session_state.cache_caminhos:
        caminho_cache = st.session_state.cache_caminhos[cache_key]
        if caminho_cache and os.path.exists(caminho_cache):
            img = carregar_imagem_caminho(caminho_cache)
            base64_str = imagem_para_base64(caminho_cache)
            return caminho_cache, img, "Cache", base64_str
    
    # Se o caminho da planilha é NaN ou vazio
    if pd.isna(caminho_planilha) or not caminho_planilha:
        caminho_planilha = ""
    
    # Lista de todas as estratégias
    estrategias = []
    
    # ESTRATÉGIA 1: Caminho direto da planilha
    if caminho_planilha and isinstance(caminho_planilha, str):
        if os.path.exists(caminho_planilha):
            estrategias.append(("Direto da planilha (absoluto)", caminho_planilha))
        
        # Tentar com caminho relativo à pasta imagens
        nome_arquivo = os.path.basename(caminho_planilha)
        caminho_relativo = os.path.join(IMAGENS_DIR, nome_arquivo)
        if os.path.exists(caminho_relativo):
            estrategias.append(("Nome da planilha", caminho_relativo))
    
    # ESTRATÉGIA 2: Código do produto + extensões comuns
    extensoes = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    for ext in extensoes:
        # Código original
        caminho = os.path.join(IMAGENS_DIR, f"{codigo}{ext}")
        if os.path.exists(caminho):
            estrategias.append((f"Código original{ext}", caminho))
        
        # Código em minúsculas
        caminho = os.path.join(IMAGENS_DIR, f"{codigo.lower()}{ext}")
        if os.path.exists(caminho):
            estrategias.append((f"Código minúsculo{ext}", caminho))
        
        # Código em maiúsculas
        caminho = os.path.join(IMAGENS_DIR, f"{codigo.upper()}{ext}")
        if os.path.exists(caminho):
            estrategias.append((f"Código maiúsculo{ext}", caminho))
    
    # ESTRATÉGIA 3: Código sem caracteres especiais
    codigo_limpo = ''.join(e for e in codigo if e.isalnum())
    for ext in extensoes:
        caminho = os.path.join(IMAGENS_DIR, f"{codigo_limpo}{ext}")
        if os.path.exists(caminho):
            estrategias.append((f"Código limpo{ext}", caminho))
        
        caminho = os.path.join(IMAGENS_DIR, f"{codigo_limpo.lower()}{ext}")
        if os.path.exists(caminho):
            estrategias.append((f"Código limpo min{ext}", caminho))
    
    # ESTRATÉGIA 4: Procurar qualquer arquivo que contenha o código
    if os.path.exists(IMAGENS_DIR):
        for arquivo in os.listdir(IMAGENS_DIR):
            if arquivo.lower().endswith(tuple(extensoes)):
                # Se o código está no nome do arquivo
                if codigo.lower() in arquivo.lower():
                    caminho = os.path.join(IMAGENS_DIR, arquivo)
                    estrategias.append(("Contém código", caminho))
                    break
                # Se o nome do arquivo (sem extensão) está no código
                nome_sem_ext = os.path.splitext(arquivo)[0].lower()
                if nome_sem_ext in codigo.lower():
                    caminho = os.path.join(IMAGENS_DIR, arquivo)
                    estrategias.append(("Código contém nome", caminho))
                    break
    
    # Pegar a primeira estratégia que funcionou
    if estrategias:
        nome_estrategia, caminho = estrategias[0]
        img = carregar_imagem_caminho(caminho)
        base64_str = imagem_para_base64(caminho)
        # Salvar no cache
        st.session_state.cache_caminhos[cache_key] = caminho
        return caminho, img, nome_estrategia, base64_str
    
    return None, None, "Nenhuma", None

def exibir_produto_com_imagem(row):
    """Exibe produto com imagem usando múltiplas estratégias"""
    
    # Encontrar imagem
    caminho, imagem, estrategia, base64_str = encontrar_imagem_ultra(row['imagem'], row['codigo'])
    
    # CSS único (carregar apenas uma vez)
    if not st.session_state.css_carregado:
        st.markdown("""
        <style>
        .product-card {
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
            height: 100%;
        }
        .product-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
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
        .product-image-container {
            width: 100%;
            height: 160px;
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
            height: 100%;
            object-fit: cover;
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
        }
        .product-price {
            font-size: 1.4em;
            font-weight: 700;
            color: #2c3e50;
            margin: 8px 0;
        }
        .product-store {
            color: #7f8c8d;
            font-size: 0.9em;
            margin: 4px 0;
        }
        .diagnostico {
            font-size: 10px;
            color: #7f8c8d;
            margin-top: 8px;
            padding: 4px 8px;
            background: #f8f9fa;
            border-radius: 4px;
            border-left: 3px solid #3498db;
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.css_carregado = True
    
    # Card do produto
    with st.container():
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        
        # Container da imagem
        st.markdown('<div class="product-image-container">', unsafe_allow_html=True)
        
        # Tentar exibir imagem de diferentes formas
        imagem_exibida = False
        
        # Método 1: Base64 (mais garantido)
        if base64_str:
            ext = os.path.splitext(caminho)[1][1:] if caminho else 'jpg'
            st.markdown(
                f'<img src="data:image/{ext};base64,{base64_str}" class="product-image">',
                unsafe_allow_html=True
            )
            imagem_exibida = True
        
        # Método 2: PIL Image
        elif imagem:
            try:
                img_copy = imagem.copy()
                img_copy.thumbnail((160, 160))
                st.image(img_copy, use_column_width=True)
                imagem_exibida = True
            except:
                pass
        
        # Método 3: Caminho direto
        elif caminho and os.path.exists(caminho):
            try:
                st.image(caminho, use_column_width=True)
                imagem_exibida = True
            except:
                pass
        
        # Se nenhum método funcionou, mostrar placeholder
        if not imagem_exibida:
            st.markdown("""
            <div style="width:100%; height:160px; background:linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%); 
                        display:flex; align-items:center; justify-content:center; color:white; 
                        font-size:48px; border-radius:8px;">
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
        
        # Diagnóstico (opcional - pode remover depois)
        if st.session_state.get('mostrar_diagnostico', False):
            st.markdown(f"""
            <div class="diagnostico">
                <b>Estratégia:</b> {estrategia}<br>
                <b>Caminho:</b> {caminho if caminho else 'não encontrado'}<br>
                <b>Planilha:</b> {row['imagem'] if pd.notna(row['imagem']) else 'vazio'}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ===== EXECUTAR DIAGNÓSTICO =====
diagnosticar_imagens()

# ===== CARREGAR DADOS =====
df = carregar_dados()

# ===== SIDEBAR COM FILTROS =====
with st.sidebar:
    st.header("🔎 Filtros")
    
    # Checkbox para mostrar diagnóstico
    st.session_state.mostrar_diagnostico = st.checkbox("📋 Mostrar diagnóstico", value=False)
    
    if not df.empty:
        st.success(f"✅ {len(df)} produtos carregados")
        
        # Filtro por Loja
        lojas = ['Todas'] + sorted(df['loja'].unique().tolist())
        loja_selecionada = st.selectbox("Selecione a Loja:", lojas, key='filtro_loja')
        
        # Filtro por Status
        status_opcoes = ['Todos', 'Em estoque', 'Acabou']
        status_selecionado = st.radio("Status:", status_opcoes, key='filtro_status')
        
        # Filtro por Preço
        st.subheader("💰 Faixa de Preço")
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
        
        # Busca por código
        st.markdown("---")
        st.subheader("🔍 Busca Rápida")
        busca_codigo = st.text_input("Digite o código:", key='busca_codigo')
        
        # Botão para listar imagens
        if st.button("📸 Listar todas imagens"):
            with st.expander("Imagens disponíveis", expanded=True):
                if os.path.exists(IMAGENS_DIR):
                    imagens = [f for f in os.listdir(IMAGENS_DIR) 
                              if f.lower().endswith(tuple(SUPPORTED_IMAGES))]
                    if imagens:
                        for f in sorted(imagens):
                            st.write(f"- {f}")
                    else:
                        st.warning("Nenhuma imagem encontrada")
                else:
                    st.error("Pasta imagens não encontrada")
        
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
    else:
        st.error("❌ Nenhum dado carregado")
        
        # Botão para criar planilha de exemplo
        if st.button("📝 Criar planilha exemplo"):
            dados_exemplo = {
                'loja': ['Loja A', 'Loja A', 'Loja B', 'Loja B', 'Loja C'],
                'codigo': ['PROD-001', 'PROD-002', 'PROD-003', 'PROD-004', 'PROD-005'],
                'imagem': ['', 'imagem2.jpg', 'foto3.png', 'prod4.jpg', ''],
                'preco': [49.90, 89.90, 129.90, 59.90, 199.90],
                'status': ['estoque', 'acabou', 'estoque', 'estoque', 'acabou'],
                'quantidade': [10, 0, 5, 3, 0]
            }
            df_exemplo = pd.DataFrame(dados_exemplo)
            os.makedirs(DADOS_DIR, exist_ok=True)
            df_exemplo.to_excel(os.path.join(DADOS_DIR, "catalogo.xlsx"), index=False)
            
            # Criar uma imagem de exemplo
            try:
                img = Image.new('RGB', (200, 200), color='red')
                img.save(os.path.join(IMAGENS_DIR, "PROD-001.jpg"))
                img.save(os.path.join(IMAGENS_DIR, "imagem2.jpg"))
                st.success("✅ Planilha e imagens exemplo criadas!")
            except:
                st.success("✅ Planilha exemplo criada!")
            
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
        
        # Estatísticas das imagens
        with st.expander("📊 Estatísticas das Imagens"):
            total = len(df_filtrado)
            com_imagem = 0
            sem_imagem = []
            
            for _, row in df_filtrado.iterrows():
                caminho, _, _, _ = encontrar_imagem_ultra(row['imagem'], row['codigo'])
                if caminho:
                    com_imagem += 1
                else:
                    sem_imagem.append(row['codigo'])
            
            st.write(f"✅ Produtos com imagem: {com_imagem}/{total} ({com_imagem/total*100:.1f}%)")
            st.write(f"❌ Produtos sem imagem: {total-com_imagem}/{total} ({(total-com_imagem)/total*100:.1f}%)")
            
            if sem_imagem:
                st.write("**Produtos sem imagem:**")
                for cod in sem_imagem[:10]:  # Mostrar apenas 10
                    st.write(f"- {cod}")
                if len(sem_imagem) > 10:
                    st.write(f"... e mais {len(sem_imagem)-10}")
        
        # ===== PAGINAÇÃO =====
        ITENS_POR_PAGINA = 8  # 2 linhas de 4 colunas
        
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
        
        # Navegação rápida
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