

import os
from PIL import Image
from glob import glob
from tqdm import tqdm
# Adiciona suporte a seleção gráfica de arquivos/pastas
import tkinter as tk
from tkinter import filedialog

def perguntar(msg, tipo=str, padrao=None):
    while True:
        valor = input(f"{msg} " + (f"[Padrão: {padrao}] " if padrao else ""))
        if not valor and padrao is not None:
            return tipo(padrao)
        try:
            return tipo(valor)
        except Exception:
            print("Valor inválido. Tente novamente.")

def main():

    print("\n=== Criador de Mosaico - Terminal Interativo ===\n")

    # Caminhos padrão para as pastas (ajuste conforme necessário)
    PASTA_PIXEL = "/Volumes/2024 TRAB/2025/ART/Mosaico"
    PASTA_BASE = "/Volumes/2024 TRAB/2025/ART/Mosaico"

    # Inicializa Tkinter para dialogs (sem janela principal)
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    # Seleção gráfica da imagem base
    print("Selecione a imagem base na janela que irá abrir...")
    base = filedialog.askopenfilename(
        title="Selecione a imagem base",
        filetypes=[("Imagens", "*.jpg *.jpeg *.png")],
        initialdir=PASTA_BASE
    )
    while not base or not os.path.isfile(base):
        print("Arquivo não encontrado! Tente novamente.")
        base = filedialog.askopenfilename(
            title="Selecione a imagem base",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png")],
            initialdir=PASTA_BASE
        )

    # Seleção gráfica da pasta de pixels
    print("Selecione a pasta com imagens de pixel na janela que irá abrir...")
    pixels = filedialog.askdirectory(
        title="Selecione a pasta de pixels",
        initialdir=PASTA_PIXEL
    )
    while not (pixels and os.path.isdir(pixels) and (glob(os.path.join(pixels, '*.jpg')) + glob(os.path.join(pixels, '*.jpeg')) + glob(os.path.join(pixels, '*.png')))):
        print("Pasta não encontrada ou sem imagens! Tente novamente.")
        pixels = filedialog.askdirectory(
            title="Selecione a pasta de pixels",
            initialdir=PASTA_PIXEL
        )

    root.destroy()

    tam = perguntar("Tamanho do pixel (px):", int, 25)
    cor = perguntar("Variação de cor (0-100):", int, 0)
    rep = perguntar("Repetições máximas por pixel (0, 2, 4):", int, 0)
    saida = perguntar("Nome do arquivo de saída:", str, "mosaico_final.jpg")
    destino = perguntar("Pasta de destino:", str, ".")

    # Carregar imagem base
    base_img = Image.open(base).convert('RGB')
    base_w, base_h = base_img.size

    # Carregar imagens de pixel e calcular cor média de cada tile
    pixel_files = glob(os.path.join(pixels, '*.jpg')) + glob(os.path.join(pixels, '*.jpeg')) + glob(os.path.join(pixels, '*.png'))
    tiles_data = []  # (imagem, cor média, caminho)
    for f in pixel_files:
        img = Image.open(f).resize((tam, tam)).convert('RGB')
        stat = img.resize((1, 1), resample=Image.LANCZOS)
        avg_color = stat.getpixel((0, 0))
        tiles_data.append((img, avg_color, f))
    if not tiles_data:
        print('Nenhuma imagem de pixel encontrada!')
        return

    # Calcular grid
    tiles_x = base_w // tam
    tiles_y = base_h // tam
    if tiles_x < 1 or tiles_y < 1:
        print('Imagem base muito pequena para o tamanho de pixel escolhido!')
        return

    # Criar imagem final
    final_img = Image.new('RGB', (tiles_x * tam, tiles_y * tam), 'white')

    print(f'Criando mosaico {tiles_x}x{tiles_y}...')
    import random
    # Define o limite de variação de cor (0-100): 0 = só o mais próximo, 100 = qualquer tile
    cor_limite = int(cor)
    max_dist = 442  # Distância máxima RGB (sqrt(3*255^2))
    for y in tqdm(range(tiles_y), desc='Linhas'):
        for x in range(tiles_x):
            box = (x * tam, y * tam, (x + 1) * tam, (y + 1) * tam)
            region = base_img.crop(box)
            # Calcular cor média do bloco da base
            region_stat = region.resize((1, 1), resample=Image.LANCZOS)
            region_color = region_stat.getpixel((0, 0))
            # Calcula distância de cor para cada tile
            dists = [(t, sum((region_color[i] - t[1][i]) ** 2 for i in range(3)) ** 0.5) for t in tiles_data]
            min_dist = min(d[1] for d in dists)
            # Limite de aceitação: linear entre 0 (apenas o melhor) e 100 (aceita todos)
            lim = min_dist + (max_dist - min_dist) * (cor_limite / 100)
            candidatos = [t for t, d in dists if d <= lim]
            if candidatos:
                tile = random.choice(candidatos)
            else:
                tile = min(dists, key=lambda d: d[1])[0]
            final_img.paste(tile[0], (x * tam, y * tam))
    out_path = os.path.join(destino, saida)
    final_img.save(out_path)
    print(f'Mosaico salvo em: {out_path}')

if __name__ == '__main__':
    main()
