"""
Módulo principal para criação de mosaicos de imagens.
Lê uma imagem base e a recria usando imagens de pixels.
"""

import os
from dataclasses import dataclass
from typing import Tuple, List
import math
from PIL import Image


@dataclass
class TileInfo:
    """Informações sobre uma imagem de pixel."""
    path: str
    average_color: Tuple[int, int, int]
    uses: int = 0


def obter_cor_media(imagem: Image.Image) -> Tuple[int, int, int]:
    """Calcula a cor média de uma imagem."""
    pequena = imagem.convert("RGB").resize((1, 1), Image.Resampling.LANCZOS)
    return pequena.getpixel((0, 0))


def calcular_distancia_cor(cor_a: Tuple[int, int, int], cor_b: Tuple[int, int, int]) -> float:
    """Calcula a distância Euclidiana entre duas cores RGB."""
    return math.sqrt(sum((cor_a[i] - cor_b[i]) ** 2 for i in range(3)))


def carregar_pixels(pasta: str) -> List[TileInfo]:
    """Carrega todas as imagens de uma pasta como pixels."""
    pixels = []
    extensoes = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
    
    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.lower().endswith(extensoes):
            caminho = os.path.join(pasta, nome_arquivo)
            try:
                with Image.open(caminho) as img:
                    cor_media = obter_cor_media(img)
                    pixels.append(TileInfo(path=caminho, average_color=cor_media))
            except Exception as e:
                print(f"Aviso: Não foi possível carregar {nome_arquivo}: {e}")
    
    return pixels


def selecionar_pixel(
    cor_alvo: Tuple[int, int, int],
    pixels: List[TileInfo],
    max_repeticoes: int,
    variacao_cor: int,
    cor_anterior: Tuple[int, int, int] = None
) -> TileInfo:
    """
    Seleciona o melhor pixel para uma célula.
    
    Args:
        cor_alvo: Cor que queremos aproximar
        pixels: Lista de pixels disponíveis
        max_repeticoes: Máximo de vezes que um pixel pode ser usado
        variacao_cor: Variação de cor (0-100), quanto maior mais flexível
        cor_anterior: Cor do pixel anterior (para suavidade)
    
    Returns:
        O pixel mais adequado
    """
    melhor_pixel = None
    melhor_distancia = float("inf")
    
    # Primeira tentativa: respeitar limite de repetições
    for pixel in pixels:
        if max_repeticoes > 0 and pixel.uses >= max_repeticoes:
            continue
        
        distancia = calcular_distancia_cor(cor_alvo, pixel.average_color)
        
        # Aplicar variação de cor (quanto maior, mais flexível)
        # variacao_cor 0 = rígido, 100 = muito flexível
        fator_variacao = 1.0 + (variacao_cor / 100.0)
        distancia = distancia / fator_variacao
        
        # Preferir cores próximas à anterior para suavidade
        if cor_anterior:
            distancia_anterior = calcular_distancia_cor(cor_alvo, cor_anterior)
            distancia -= distancia_anterior * 0.1
        
        if distancia < melhor_distancia:
            melhor_distancia = distancia
            melhor_pixel = pixel
    
    # Se não encontrou com limite, ignorar limite
    if melhor_pixel is None and max_repeticoes > 0:
        for pixel in pixels:
            distancia = calcular_distancia_cor(cor_alvo, pixel.average_color)
            if distancia < melhor_distancia:
                melhor_distancia = distancia
                melhor_pixel = pixel
    
    if melhor_pixel is None:
        raise RuntimeError("Nenhum pixel disponível!")
    
    return melhor_pixel


def criar_mosaico(
    caminho_base: str,
    pasta_pixels: str,
    tamanho_pixel: int,  # em pixels
    redimensionar: bool,
    max_repeticoes: int,
    variacao_cor: int,
    caminho_saida: str,
    qualidade: int = 85,
    callback_progresso = None
) -> Tuple[int, int]:
    """
    Cria um mosaico a partir de uma imagem base.
    
    Args:
        caminho_base: Caminho da imagem base
        pasta_pixels: Pasta com imagens de pixels
        tamanho_pixel: Tamanho dos pixels em pixels (ex: 50, 100, 200)
        redimensionar: Se True, redimensiona pixels para tamanho_pixel
        max_repeticoes: Máximo de repetições (0, 2, 4)
        variacao_cor: Variação de cor (0-100)
        caminho_saida: Onde salvar o arquivo final
        qualidade: Qualidade JPEG (1-100)
        callback_progresso: Função para reportar progresso
    
    Returns:
        Tupla (largura_final, altura_final) do mosaico
    """
    
    # Carregar imagem base
    with Image.open(caminho_base) as img_base:
        img_base = img_base.convert("RGB")
        largura_base = img_base.width
        altura_base = img_base.height
    
    # Calcular grid
    colunas = largura_base // tamanho_pixel
    linhas = altura_base // tamanho_pixel
    
    if colunas == 0 or linhas == 0:
        raise ValueError("Imagem base é muito pequena para o tamanho de pixel escolhido!")
    
    # Carregar pixels
    pixels = carregar_pixels(pasta_pixels)
    if not pixels:
        raise ValueError("Nenhuma imagem de pixel encontrada na pasta!")
    
    # Redimensionar imagem base para análise
    with Image.open(caminho_base) as img_base:
        img_base = img_base.convert("RGB")
        img_redimensionada = img_base.resize(
            (colunas * tamanho_pixel, linhas * tamanho_pixel),
            Image.Resampling.LANCZOS
        )
    
    # Descobrir tamanho nativo do primeiro pixel
    with Image.open(pixels[0].path) as sample:
        tamanho_pixel_nativo = sample.width
    
    # Se redimensionar, usar tamanho_pixel, senão usar tamanho nativo
    tamanho_final_pixel = tamanho_pixel if redimensionar else tamanho_pixel_nativo
    
    # Criar imagem final
    largura_final = colunas * tamanho_final_pixel
    altura_final = linhas * tamanho_final_pixel
    mosaico = Image.new("RGB", (largura_final, altura_final), "white")
    
    cor_anterior = None
    total_celulas = colunas * linhas
    
    # Processar cada célula
    for linha in range(linhas):
        for coluna in range(colunas):
            celula_atual = linha * colunas + coluna + 1
            
            if callback_progresso:
                callback_progresso(celula_atual, total_celulas)
            
            # Coordenadas na análise
            x1_analise = coluna * tamanho_pixel
            y1_analise = linha * tamanho_pixel
            x2_analise = x1_analise + tamanho_pixel
            y2_analise = y1_analise + tamanho_pixel
            
            # Extrair célula
            celula = img_redimensionada.crop((x1_analise, y1_analise, x2_analise, y2_analise))
            cor_celula = obter_cor_media(celula)
            
            # Selecionar pixel
            pixel_selecionado = selecionar_pixel(
                cor_celula,
                pixels,
                max_repeticoes,
                variacao_cor,
                cor_anterior
            )
            pixel_selecionado.uses += 1
            cor_anterior = cor_celula
            
            # Carregar e processar imagem de pixel
            with Image.open(pixel_selecionado.path) as img_pixel:
                img_pixel = img_pixel.convert("RGB")
                
                # Redimensionar se necessário
                if redimensionar:
                    img_pixel = img_pixel.resize(
                        (tamanho_final_pixel, tamanho_final_pixel),
                        Image.Resampling.LANCZOS
                    )
                
                # Colar na posição correta
                x_final = coluna * tamanho_final_pixel
                y_final = linha * tamanho_final_pixel
                mosaico.paste(img_pixel, (x_final, y_final))
    
    # Salvar
    mosaico.save(caminho_saida, "JPEG", quality=qualidade)
    
    return largura_final, altura_final


def calcular_tamanho_final(
    caminho_base: str,
    pasta_pixels: str,
    tamanho_pixel: int,
    redimensionar: bool
) -> Tuple[int, int, str]:
    """
    Calcula o tamanho final do mosaico sem criar a imagem.
    
    Returns:
        Tupla (largura, altura, descricao)
    """
    # Imagem base
    with Image.open(caminho_base) as img:
        largura_base = img.width
        altura_base = img.height
    
    colunas = largura_base // tamanho_pixel
    linhas = altura_base // tamanho_pixel
    
    if colunas == 0 or linhas == 0:
        return 0, 0, "Erro: imagem base muito pequena!"
    
    # Descobrir tamanho nativo do pixel
    extensoes = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
    tamanho_nativo = 100  # padrão
    
    for nome_arquivo in os.listdir(pasta_pixels):
        if nome_arquivo.lower().endswith(extensoes):
            caminho = os.path.join(pasta_pixels, nome_arquivo)
            try:
                with Image.open(caminho) as img:
                    tamanho_nativo = img.width
                    break
            except:
                pass
    
    # Calcular tamanho final
    tamanho_final = tamanho_pixel if redimensionar else tamanho_nativo
    largura_final = colunas * tamanho_final
    altura_final = linhas * tamanho_final
    
    # Descrição
    modo_texto = f"redimensionado para {tamanho_pixel}px" if redimensionar else f"tamanho nativo ({tamanho_nativo}px)"
    desc = f"Grid: {colunas}×{linhas} | Pixels: {modo_texto} | Resultado: {largura_final}×{altura_final}px"
    
    return largura_final, altura_final, desc
