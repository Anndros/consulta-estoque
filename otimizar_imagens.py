from PIL import Image
import os

def compactar_imagens():
    """Compacta todas as imagens para carregar mais rápido"""
    imagens_dir = "imagens"
    
    if not os.path.exists(imagens_dir):
        return
    
    for arquivo in os.listdir(imagens_dir):
        if arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
            caminho = os.path.join(imagens_dir, arquivo)
            
            try:
                img = Image.open(caminho)
                
                # Redimensionar se for muito grande
                if img.width > 800 or img.height > 800:
                    img.thumbnail((800, 800))
                
                # Salvar com compressão
                if arquivo.lower().endswith('.png'):
                    img.save(caminho, optimize=True, compress_level=9)
                else:
                    img.save(caminho, optimize=True, quality=85)
                
                print(f"✅ Compactado: {arquivo}")
            except:
                print(f"❌ Erro: {arquivo}")

if __name__ == "__main__":
    compactar_imagens()