# teste_direto.py
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Teste Direto", page_icon="🔴")
st.title("🔴 TESTE DIRETO - SEM MÓDULOS")

# CARREGAR DIRETAMENTE
caminho = "dados/catalogo.xlsx"

if os.path.exists(caminho):
    st.success(f"Arquivo encontrado: {caminho}")
    
    # Ler direto
    df = pd.read_excel(caminho)
    
    st.write("### Dados brutos da planilha:")
    st.dataframe(df)
    
    st.write("### Tipos dos dados:")
    st.write(df.dtypes)
    
    st.write("### Valores de quantidade:")
    for idx, row in df.iterrows():
        st.write(f"**{row['codigo']}**")
        st.write(f"- Valor: {row['quantidade']}")
        st.write(f"- Tipo: {type(row['quantidade'])}")
        st.write(f"- Int convertido: {int(row['quantidade'])}")
        st.write("---")
    
    # Teste com st.metric
    st.write("### Teste com st.metric:")
    for idx, row in df.iterrows():
        st.metric(
            label=f"{row['codigo']}",
            value=f"{row['quantidade']} unidades",
            delta=None
        )
else:
    st.error("Arquivo não encontrado")
    
    # Criar arquivo de teste
    if st.button("Criar arquivo de teste"):
        dados = {
            'loja': ['Loja A', 'Loja B'],
            'codigo': ['TESTE-01', 'TESTE-02'],
            'imagem': ['', ''],
            'preco': [100.0, 200.0],
            'status': ['estoque', 'acabou'],
            'quantidade': [42, 0]
        }
        df_teste = pd.DataFrame(dados)
        os.makedirs("dados", exist_ok=True)
        df_teste.to_excel("dados/catalogo.xlsx", index=False)
        st.success("Arquivo criado! Atualize a página.")