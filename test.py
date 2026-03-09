# debug_import.py
import streamlit as st

print("=" * 50)
print("🔍 DEBUG DE IMPORTAÇÃO")
print("=" * 50)

print(f"1. st.session_state antes de qualquer import: {list(st.session_state.keys())}")

print("\n2. Importando módulos...")
from modules.config import *
print("   ✅ config importado")

from modules.database import *
print("   ✅ database importado")

print("   ⚠️ Importando image_handler...")
from modules.image_handler import image_handler
print("   ✅ image_handler importado")

print(f"\n3. st.session_state depois dos imports: {list(st.session_state.keys())}")

print("\n4. Verificando cache_caminhos:")
if 'cache_caminhos' in st.session_state:
    print(f"   ✅ cache_caminhos existe: {type(st.session_state.cache_caminhos)}")
else:
    print("   ❌ cache_caminhos NÃO existe")

print("\n5. Testando acesso direto:")
try:
    test = st.session_state.cache_caminhos
    print("   ✅ Acesso direto OK")
except Exception as e:
    print(f"   ❌ Erro no acesso direto: {e}")

print("=" * 50)