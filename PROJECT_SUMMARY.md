# Mosaic Creator - Estrutura do Projeto

## 📂 Arquivos Criados

```
mosaic_creator/
├── mosaic_creator.py          # ⭐ Programa principal
├── create_mosaic.sh            # 🚀 Script de conveniência
├── example_usage.py            # 📚 Exemplos de uso
│
├── README.md                   # 📖 Documentação completa
├── QUICKSTART.md               # ⚡ Guia rápido
├── SETUP.md                    # 🔧 Instruções de setup
│
├── requirements.txt            # 📦 Dependências
└── .gitignore                  # 📝 Git ignore
```

## 🎯 O Que o Programa Faz

1. **Recebe uma imagem base** - Aquela que você quer recriar
2. **Analisa cores** - Calcula a cor média de cada região
3. **Compara com tiles** - Encontra a imagem de tile com cor mais próxima
4. **Monta o mosaico** - Combina todas as tiles para criar a imagem final

## 🚀 Comando Mais Rápido para Usar

```bash
./create_mosaic.sh reference_images/sua_imagem.jpg tiles/
```

## 📊 Funcionalidades

| Feature | Descrição |
|---------|-----------|
| **--reference** | Imagem base a recriar (obrigatório) |
| **--tiles** | Pasta com imagens de tile (obrigatório) |
| **--tile-size** | Tamanho do tile em pixels (padrão: 30) |
| **--max-uses** | Limite de repetições por tile (padrão: ilimitado) |
| **--output** | Arquivo de saída (padrão: mosaico_final.png) |

## ✅ Setup Concluído

- ✅ Python 3.14.0 configurado
- ✅ Pillow instalado (processamento de imagens)
- ✅ Ambiente virtual criado
- ✅ Todos os arquivos criados
- ✅ Pronto para usar!

## 📋 Estrutura Recomendada para Seus Arquivos

```
mosaic_creator/
├── reference_images/           # Suas imagens base
│   └── foto.jpg
├── tiles/                       # Suas imagens de tile
│   ├── tile1.png
│   ├── tile2.png
│   └── ...
└── output/                      # Mosaicos gerados
    └── mosaico_final.png
```

---

**Tudo pronto! Comece a criar mosaicos! 🎨**
