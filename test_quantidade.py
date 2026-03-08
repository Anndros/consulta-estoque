# diagnostico.py
import streamlit as st
from modules.database import carregar_dados, verificar_dados, criar_dados_exemplo
import pandas as pd

st.set_page_config(page_title="Diagnóstico", page_icon="🔧")
st.title("🔧 Diagnóstico do Banco de Dados")

# Botão para recriar dados
if st.button("🔄 Recriar dados de exemplo"):
    if criar_dados_exemplo():
        st.success("Dados de exemplo recriados!")
        st.cache_data.clear()
        st.rerun()

# Carregar e mostrar dados
df = carregar_dados()

if not df.empty:
    st.success(f"✅ Dados carregados: {len(df)} linhas")
    
    # Mostrar dados brutos
    with st.expander("📊 Ver dados brutos", expanded=True):
        st.dataframe(df, use_container_width=True)
    
    # Análise por status
    st.subheader("📦 Análise por Status")
    
    for status in df['status'].unique():
        df_status = df[df['status'] == status]
        st.write(f"**{status.upper()}:** {len(df_status)} produtos")
        
        if status == 'estoque':
            st.write(f"- Total em estoque: {df_status['quantidade'].sum()} unidades")
            st.write(f"- Média por produto: {df_status['quantidade'].mean():.1f} unidades")
            st.write(f"- Mínimo: {df_status['quantidade'].min()}")
            st.write(f"- Máximo: {df_status['quantidade'].max()}")
    
    # Verificar tipos
    st.subheader("🔤 Tipos das Colunas")
    tipos = pd.DataFrame({
        'Coluna': df.columns,
        'Tipo': df.dtypes.values,
        'Exemplo': [df[col].iloc[0] if len(df) > 0 else '' for col in df.columns]
    })
    st.dataframe(tipos)
    
    # Botão para testar card
    if st.button("🃏 Testar Card do Produto"):
        st.subheader("Preview do Primeiro Produto")
        from modules.product_card import render_product_card
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            render_product_card(df.iloc[0], 0)
    
else:
    st.error("❌ Nenhum dado carregado")
    
    if st.button("📝 Criar dados de exemplo agora"):
        if criar_dados_exemplo():
            st.success("Dados criados!")
            st.rerun()