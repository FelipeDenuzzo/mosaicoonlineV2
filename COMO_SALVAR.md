# 💾 Como Salvar seu Projeto

## 1️⃣ SALVAR A IMAGEM DO MOSAICO

A imagem é salva automaticamente em:
- **Padrão:** `/Users/felipedenuzzo/VSCODE/mosaic_creator/mosaico_final.png`
- **Ou em:** `/Users/felipedenuzzo/VSCODE/mosaic_creator/output/`

Você pode mudar o local na interface gráfica antes de clicar em "CRIAR MOSAICO"

---

## 2️⃣ SALVAR O PROJETO COMPLETO (Git)

### Opção A: Fazer Backup Manual
```bash
# Copiar todo o projeto para um local seguro
cp -r /Users/felipedenuzzo/VSCODE/mosaic_creator ~/Documentos/mosaic_backup_$(date +%Y%m%d)
```

### Opção B: Inicializar Git
```bash
cd /Users/felipedenuzzo/VSCODE/mosaic_creator
git init
git add .
git commit -m "Mosaic Creator - Projeto Inicial"
```

### Opção C: Enviar para GitHub
```bash
cd /Users/felipedenuzzo/VSCODE/mosaic_creator
git remote add origin https://github.com/seu-usuario/mosaic-creator.git
git push -u origin main
```

---

## 3️⃣ SALVAR CONFIGURAÇÕES PADRÃO

Crie um arquivo `config.json`:

```bash
cat > /Users/felipedenuzzo/VSCODE/mosaic_creator/config.json << 'EOF'
{
  "tile_size": 40,
  "max_uses": 3,
  "similarity": 0.2,
  "output_folder": "output"
}
EOF
```

---

## 4️⃣ LOCALIZAR ARQUIVOS IMPORTANTES

```bash
# Ver todos os mosaicos criados
ls -lh /Users/felipedenuzzo/VSCODE/mosaic_creator/mosaico*.png

# Ver arquivos de output
ls -lh /Users/felipedenuzzo/VSCODE/mosaic_creator/output/

# Ver tamanho do projeto
du -sh /Users/felipedenuzzo/VSCODE/mosaic_creator/
```

---

## ✨ RESUMO DOS ARQUIVOS PRINCIPAIS

```
mosaic_creator/
├── mosaic_creator.py        ⭐ Programa principal
├── gui_v2.py                🎨 Interface gráfica
├── reference_images/        📷 Imagens base
├── tiles/                   🧩 265 imagens de pixel
├── output/                  💾 Mosaicos gerados
└── mosaico_final.png       📸 Última criação
```

---

## 🔧 ABRIR IMAGEM NO MAC

```bash
open /Users/felipedenuzzo/VSCODE/mosaic_creator/mosaico_final.png
```

Qual desses você precisa? 💾
