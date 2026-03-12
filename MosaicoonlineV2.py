Leitura [](file:///Users/felipedenuzzo/VSCODE/Mosaico%20Programas/mosaic_creator/mosaicoonline/app/main.py#1-1), linhas 1 para 80

Leitura [](file:///Users/felipedenuzzo/VSCODE/Mosaico%20Programas/mosaic_creator/mosaicoonline/app/main.py#81-81), linhas 81 para 180

Leitura [](file:///Users/felipedenuzzo/VSCODE/Mosaico%20Programas/mosaic_creator/mosaicoonline/app/main.py#181-181), linhas 181 para 221

Aqui está a lógica essencial do mosaico para criar a imagem, já adaptada para fluxo 100% local (sem Google Drive):

```python
import secrets
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from . import settings
from .mosaic_engine import build_mosaic

app = FastAPI(title="mosaicoonline", version="1.0.0")

def _safe_output_name(original_name: str) -> str:
    stem = Path(original_name).stem or "mosaic"
    safe_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
    if not safe_stem:
        safe_stem = "mosaic"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    token = secrets.token_hex(3)
    return f"{safe_stem}_{stamp}_{token}.jpg"

@app.post("/api/mosaic")
async def create_mosaic(
    base_image: UploadFile = File(...),
    pixel_size_mm: int = Form(25),
    max_uses: int = Form(2),
    similarity: float = Form(0.0),
    quality: int = Form(settings.DEFAULT_QUALITY),
):
    import tempfile
    from PIL import Image

    content = await base_image.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File too large. Max is {settings.MAX_UPLOAD_MB}MB.")

    extension = ".jpg"
    if base_image.filename and base_image.filename.lower().endswith(".png"):
        extension = ".png"

    # Salvar temporariamente em /tmp
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension, dir="/tmp")
    tmp_file.write(content)
    tmp_file.close()
    input_path = Path(tmp_file.name)

    # Redimensionar para 2K (2048px de largura)
    resized_path = Path(f"/tmp/resized_{input_path.name}")
    img = Image.open(input_path)
    img = img.convert("RGB")
    img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
    img.save(resized_path, "JPEG", quality=90)

    # Usar tiles locais
    if not any(settings.TILES_DIR.glob("*.jpg")) and not any(settings.TILES_DIR.glob("*.jpeg")) and not any(settings.TILES_DIR.glob("*.png")):
        raise HTTPException(status_code=400, detail="Tiles folder is empty. Adicione imagens em data/tiles.")

    output_name = _safe_output_name(base_image.filename or "mosaic")
    output_path = Path(f"/tmp/{output_name}")

    try:
        build_mosaic(
            reference_path=resized_path,
            tiles_folder=settings.TILES_DIR,
            tile_size_mm=pixel_size_mm,
            max_uses=max_uses,
            output_path=output_path,
            similarity=similarity,
            quality=quality,
            dpi=settings.DEFAULT_DPI,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create mosaic: {exc}") from exc

    return JSONResponse(
        {
            "ok": True,
            "output_file": output_name,
            "download_url": f"/api/output/{output_name}",
        }
    )
```

Se quiser recomeçar do zero, basta usar esse bloco como base para o endpoint de criação do mosaico! Se precisar do código do build_mosaic ou de outro trecho, me avise.