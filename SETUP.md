# 📋 Configuração e Setup

## ✅ O Que Foi Instalado

Seu projeto **Mosaic Creator** foi configurado com sucesso! Aqui está o que você tem:

### Arquivos Principais
- **mosaic_creator.py** - Programa principal que cria os mosaicos
- **create_mosaic.sh** - Script shell para facilitar o uso

### Documentação
- **README.md** - Documentação completa
- **QUICKSTART.md** - Guia rápido de início
- **requirements.txt** - Dependências do projeto

### Utilities
- **example_usage.py** - Exemplos de uso
- **.gitignore** - Configuração Git

## 🔧 Ambiente Python

O projeto foi configurado com um ambiente virtual em:
```
/Users/felipedenuzzo/VSCODE/.venv/
```

Python instalado:
- **Versão**: 3.14.0
- **Tipo**: Virtual Environment
- **Pillow**: ✅ Instalado (para manipulação de imagens)

## 🚀 Como Usar

### Método 1: Usar o Script Shell (Recomendado no macOS)

```bash
cd /Users/felipedenuzzo/VSCODE/mosaic_creator
./create_mosaic.sh reference_images/sua_imagem.jpg tiles/
```

### Método 2: Usar Python Diretamente

```bash
/Users/felipedenuzzo/VSCODE/.venv/bin/python mosaic_creator.py \
  --reference sua_imagem.jpg \
  --tiles pasta_tiles/
```

### Método 3: Ativar o Ambiente Virtual

```bash
source /Users/felipedenuzzo/VSCODE/.venv/bin/activate
python mosaic_creator.py --reference sua_imagem.jpg --tiles pasta_tiles/
deactivate
```

## 📁 Próximos Passos

1. **Crie as pastas necessárias:**
```bash
cd /Users/felipedenuzzo/VSCODE/mosaic_creator
mkdir -p reference_images tiles output
```

2. **Adicione suas imagens:**
   - Coloque a imagem base em `reference_images/`
   - Coloque as imagens de tile em `tiles/`

3. **Execute o programa:**
```bash
./create_mosaic.sh reference_images/sua_imagem.jpg tiles/
```

## ✨ Recursos do Programa

✅ Análise inteligente de cores
✅ Seleção automática de tiles
✅ Suporte a PNG, JPG, JPEG
✅ Customização de tamanho de tile
✅ Limite de repetições de tiles
✅ Processamento eficiente

## 🎯 Exemplos de Uso

### Exemplo 1: Básico
```bash
./create_mosaic.sh reference_images/foto.jpg tiles/
```

### Exemplo 2: Com tamanho customizado
```bash
./create_mosaic.sh reference_images/foto.jpg tiles/ --tile-size 20
```

### Exemplo 3: Com limite de uso
```bash
./create_mosaic.sh reference_images/foto.jpg tiles/ --max-uses 2
```

### Exemplo 4: Especificar saída
```bash
./create_mosaic.sh reference_images/foto.jpg tiles/ --output output/meu_mosaico.png
```

## 📞 Suporte

Se encontrar problemas:

1. **Imagens de tile não encontradas**: Certifique-se que estão em `tiles/`
2. **Erro de permissão**: Execute `chmod +x create_mosaic.sh`
3. **PIL não encontrado**: Já está instalado no ambiente virtual

## 💡 Dicas de Performance

- **Tiles pequenas (20-30px)**: Melhor detalhamento
- **Tiles grandes (50+px)**: Processamento mais rápido
- **Máximo de tiles**: Use pelo menos 50-100 imagens diferentes
- **--max-uses**: Defina como 2-3 para melhor distribuição

---

**Divirta-se criando mosaicos artísticos! 🎨**
