import secrets
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from settings import TILES_DIR, DEFAULT_QUALITY, MAX_UPLOAD_MB
from build_mosaic import build_mosaic
import os

app = FastAPI(title="mosaicoonlineV2", version="2.0.0")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
    quality: int = Form(DEFAULT_QUALITY),
):
    content = await base_image.read()
    max_bytes = MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File too large. Max is {MAX_UPLOAD_MB}MB.")

    extension = ".jpg"
    if base_image.filename and base_image.filename.lower().endswith(".png"):
        extension = ".png"

    # Salvar temporariamente em /tmp
    tmp_file = open(f"/tmp/{secrets.token_hex(8)}{extension}", "wb")
    tmp_file.write(content)
    tmp_file.close()
    input_path = Path(tmp_file.name)

    # Redimensionar para 2K (2048px de largura)
    from PIL import Image
    resized_path = Path(f"/tmp/resized_{input_path.name}")
    img = Image.open(input_path)
    img = img.convert("RGB")
    img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
    img.save(resized_path, "JPEG", quality=90)

    # Usar tiles locais
    if not TILES_DIR.exists() or not any(TILES_DIR.glob("*.jpg")) and not any(TILES_DIR.glob("*.jpeg")) and not any(TILES_DIR.glob("*.png")):
        raise HTTPException(status_code=400, detail="Tiles folder is empty. Adicione imagens em data/tiles.")

    output_name = _safe_output_name(base_image.filename or "mosaic")
    output_path = Path(f"/tmp/{output_name}")

    try:
        build_mosaic(
            reference_path=resized_path,
            tiles_folder=TILES_DIR,
            tile_size_mm=pixel_size_mm,
            max_uses=max_uses,
            output_path=output_path,
            similarity=similarity,
            quality=quality,
            dpi=DEFAULT_QUALITY,
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

@app.get("/api/output/{filename}")
def get_output_file(filename: str):
    file_path = Path(f"/tmp/{filename}")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path=file_path, media_type="image/jpeg", filename=file_path.name)
