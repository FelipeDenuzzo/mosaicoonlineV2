from PIL import Image
import numpy as np

def build_mosaic(reference_path, tiles_folder, tile_size_mm, max_uses, output_path, similarity, quality, dpi):
    # Exemplo: apenas copia a imagem base para o output
    img = Image.open(reference_path)
    img.save(output_path, "JPEG", quality=quality, dpi=(dpi, dpi))
