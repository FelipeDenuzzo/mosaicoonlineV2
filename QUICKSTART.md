# 🚀 Guia de Início Rápido

## Instalação (Primeira Vez)

```bash
cd /Users/felipedenuzzo/VSCODE/mosaic_creator
pip install -r requirements.txt
```

## Estrutura de Pastas Recomendada

```
mosaic_creator/
├── reference_images/     # Suas imagens base
│   └── foto.jpg
├── tiles/                # Suas imagens de tile
│   ├── tile1.png
│   ├── tile2.png
│   └── tile3.png
└── output/               # Mosaicos gerados
    └── mosaico_final.png
```

## Executar o Programa

### Opção 1: Usar o Python do ambiente virtual

```bash
/Users/felipedenuzzo/VSCODE/.venv/bin/python mosaic_creator.py \
  --reference reference_images/sua_imagem.jpg \
  --tiles tiles/ \
  --output output/meu_mosaico.png
```

### Opção 2: Usar python diretamente (se o ambiente estiver ativo)

```bash
python mosaic_creator.py \
  --reference reference_images/sua_imagem.jpg \
  --tiles tiles/ \
  --output output/meu_mosaico.png
```

## Exemplo Prático

1. Crie as pastas:
```bash
mkdir -p reference_images tiles output
```

2. Coloque sua imagem base em `reference_images/`

3. Coloque suas imagens de tile em `tiles/`

4. Execute:
```bash
/Users/felipedenuzzo/VSCODE/.venv/bin/python mosaic_creator.py \
  --reference reference_images/foto.jpg \
  --tiles tiles/ \
  --tile-size 30 \
  --output output/mosaico.png
```

5. Encontre o resultado em `output/mosaico.png`

## Dicas de Performance

- **Imagens pequenas de tile**: Use tiles de 20-30px
- **Muitas imagens de tile**: Reduz o tempo de processamento
- **--max-uses**: Limitar a 2-3 para evitar repetições
- **Imagem base pequena**: Más rápido processar

## Troubleshooting

### Erro: "PIL não encontrado"
```bash
pip install Pillow
```

### Erro: "Nenhuma imagem encontrada na pasta de tiles"
- Certifique-se que há imagens (.png, .jpg, .jpeg) em `tiles/`

### Mosaic muito grande
- Reduza `--tile-size` ou a resolução da imagem base

### Mosaic demorando muito
- Aumente `--tile-size` ou reduza o número de tiles
