# Vercel Environment Variables

Configure todas as variaveis abaixo no projeto Vercel.

## Obrigatorias

- MOSAIC_TILES_DIR=./data/tiles
- MOSAIC_INPUT_DIR=./data/input
- MOSAIC_OUTPUT_DIR=./data/output
- MOSAIC_DPI=240
- MOSAIC_QUALITY=85
- MOSAIC_MAX_UPLOAD_MB=20
- GOOGLE_DRIVE_FOLDER_ID=<id_da_pasta_no_google_drive>
- GOOGLE_SERVICE_ACCOUNT_JSON=<json_completo_da_service_account_em_linha_unica>

## Como obter o GOOGLE_DRIVE_FOLDER_ID

1. Abra a pasta do Google Drive no navegador.
2. Copie o trecho final da URL apos `/folders/`.

## Como preparar o GOOGLE_SERVICE_ACCOUNT_JSON

1. Baixe o JSON da service account no Google Cloud.
2. Converta para linha unica:

```bash
python -c "import json; print(json.dumps(json.load(open('service-account.json'))))"
```

3. Cole a saida inteira em GOOGLE_SERVICE_ACCOUNT_JSON.

## Importante

- Compartilhe a pasta do Drive com o email da service account.
- Sem essas variaveis, a API bloqueia a geracao do mosaico.
