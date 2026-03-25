# mosaicoonline

Aplicacao web para gerar mosaicos a partir de upload de foto base, reaproveitando a mesma logica de analise de cor e reconstrucao por tiles.

## O que este projeto faz

- Recebe uma imagem base via interface web.
- Usa um banco fixo de imagens na pasta `data/tiles`.
- Gera o mosaico e salva na pasta `data/output`.
- Sempre envia o resultado para Google Drive (obrigatorio para persistencia no Vercel).

## Estrutura

```
mosaicoonline/
├── app/
│   ├── main.py
│   ├── mosaic_engine.py
│   ├── settings.py
│   └── storage.py
├── data/
│   ├── input/
│   ├── output/
│   └── tiles/
├── static/
│   └── style.css
├── templates/
│   └── index.html
├── .env.example
├── requirements.txt
└── vercel.json
```

## Requisitos

- Python 3.10+
- Dependencias em `requirements.txt`

## Rodar localmente

1. Entre na pasta do projeto:

```bash
cd mosaicoonline
```

2. Instale dependencias:

```bash
pip install -r requirements.txt
```

3. Copie variaveis de ambiente:

```bash
cp .env.example .env
```

4. Coloque imagens de banco em `data/tiles`.

5. Suba o servidor:

```bash
uvicorn app.main:app --reload
```

6. Abra:

- http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/api/health

## API

### POST /api/mosaic

Form-data:

- `base_image`: arquivo jpg/png
- `pixel_size_mm`: inteiro > 0
- `max_uses`: 0, 2 ou 4
- `similarity`: 0 a 100
- `quality`: 1 a 100

Resposta:

```json
{
  "ok": true,
  "output_file": "nome_arquivo.jpg",
  "download_url": "/api/output/nome_arquivo.jpg",
  "drive_file_id": null,
  "drive_web_link": null
}
```

## Google Drive (obrigatorio)

Para persistencia em ambiente serverless:

1. Crie uma service account no Google Cloud.
2. Habilite API do Google Drive.
3. Compartilhe a pasta de destino com o email da service account.
4. Configure:

- `GOOGLE_DRIVE_FOLDER_ID=<id_da_pasta>`
- `GOOGLE_SERVICE_ACCOUNT_JSON=<json_em_linha_unica>`

## Deploy no Vercel

1. Suba o codigo no GitHub.
2. Importe o repositorio no Vercel.
3. Configure as variaveis de ambiente do `.env.example`.
4. Deploy.

### Secrets no Vercel

Configure estes Environment Variables no projeto:

- `MOSAIC_TILES_DIR=./data/tiles`
- `MOSAIC_INPUT_DIR=./data/input`
- `MOSAIC_OUTPUT_DIR=./data/output`
- `MOSAIC_DPI=240`
- `MOSAIC_QUALITY=85`
- `MOSAIC_MAX_UPLOAD_MB=20`
- `GOOGLE_DRIVE_FOLDER_ID=<id_da_pasta_no_drive>`
- `GOOGLE_SERVICE_ACCOUNT_JSON=<json_da_service_account_em_linha_unica>`

Observacao importante:

- O filesystem do Vercel e efemero.
- O resultado deve ser enviado para Google Drive para persistir.

## Checklist de validacao

- Upload de imagem funciona na tela inicial.
- Pasta `data/tiles` com imagens gera mosaico.
- Arquivo aparece em `data/output` localmente.
- Endpoint `/api/output/{filename}` baixa o arquivo.
- Se Drive nao estiver configurado, API retorna erro e nao conclui o processo.
- Retorno inclui `drive_file_id` e `drive_web_link` em caso de sucesso.
# Mosaic Creator 🎨

Um programa Python que cria mosaicos artísticos recriando uma imagem base usando outras imagens como "pixels".

## Como Funciona

1. Você fornece uma **imagem base** que deseja recriar
2. O programa analisa a cor média de cada região da imagem base
3. Para cada região, seleciona a imagem de tile cuja cor média mais se aproxima
4. Monta o mosaico final combinando todas as imagens selecionadas

## Requisitos

- Python 3.8+
- Pillow (PIL)

## Instalação

```bash
pip install Pillow
```

## Uso

### Comando Básico

```bash
python mosaic_creator.py --reference imagem_base.jpg --tiles pasta_com_tiles/
```

### Opções Disponíveis

| Opção | Padrão | Descrição |
|-------|--------|-----------|
| `--reference` | **Obrigatório** | Caminho da imagem base a ser recriada |
| `--tiles` | **Obrigatório** | Pasta contendo as imagens para usar como pixels |
| `--tile-size` | 30 | Tamanho em pixels de cada tile no mosaico final |
| `--max-uses` | 0 (ilimitado) | Número máximo de vezes que cada imagem pode ser usada |
| `--output` | mosaico_final.png | Arquivo de saída do mosaico |

### Exemplos

**Exemplo 1: Básico**
```bash
python mosaic_creator.py --reference foto.jpg --tiles meus_tiles/
```

**Exemplo 2: Customizado**
```bash
python mosaic_creator.py \
  --reference mona_lisa.jpg \
  --tiles emojis/ \
  --tile-size 20 \
  --max-uses 3 \
  --output mosaico_colorido.png
```

**Exemplo 3: Tiles grandes**
```bash
python mosaic_creator.py \
  --reference paisagem.jpg \
  --tiles fotos_pequenas/ \
  --tile-size 50 \
  --output paisagem_mosaico.png
```

## Estrutura do Projeto

```
mosaic_creator/
├── mosaic_creator.py   # Programa principal
├── README.md           # Este arquivo
├── imagem_base/        # (Opcional) Pasta com imagens base de exemplo
└── tiles/              # (Opcional) Pasta com imagens para usar como tiles
```

## Dicas para Melhores Resultados

1. **Qualidade de Tiles**: Use imagens de boa qualidade e com cores bem definidas
2. **Tamanho do Tile**: 
   - `20-30px`: Melhor detalhamento
   - `40-50px`: Mosaiços mais rápidos
   - `60+px`: Mosaiços abstratos

3. **Variedade de Cores**: Quanto mais variedade de cores nas tiles, melhor o resultado

4. **Resolução da Imagem Base**: Use imagens com resolução adequada (não muito pequenas)

5. **Limite de Uso**: Aumentar `--max-uses` evita repetições excessivas

## Processo Passo a Passo

1. **Carregamento**: O programa carrega todos os tiles e calcula sua cor média
2. **Divisão**: A imagem base é dividida em células de `tile-size × tile-size`
3. **Análise**: Para cada célula, calcula a cor média
4. **Seleção**: Encontra o tile cuja cor média é mais próxima
5. **Composição**: Monta o mosaico final combinando os tiles selecionados

## Formatos Suportados

- Entrada: PNG, JPG, JPEG
- Saída: PNG (com suporte a transparência)

## Performance

O tempo de processamento depende de:
- Tamanho da imagem base
- Número de tiles disponíveis
- Tamanho do tile (menor = mais rápido)
