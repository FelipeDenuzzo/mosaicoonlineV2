import secrets
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import settings
from .mosaic_engine import build_mosaic
from .storage import export_result

app = FastAPI(title="mosaicoonline", version="1.0.0")

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).resolve().parent.parent / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "tiles_dir": str(settings.TILES_DIR),
        "output_dir": str(settings.OUTPUT_DIR),
        "drive_required": True,
        "drive_configured": settings.drive_is_configured(),
    }


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
    print("[DEBUG] Início do endpoint /api/mosaic")
    print(f"[DEBUG] Tiles DIR: {settings.TILES_DIR}")
    print(f"[DEBUG] Output DIR: /tmp")
    import os
    if not settings.TILES_DIR.exists():
        print("[ERRO] Pasta de tiles não existe!")
        raise HTTPException(status_code=500, detail="Pasta de tiles (data/tiles) não existe no deploy. Adicione imagens e faça novo deploy.")
    print(f"[DEBUG] Arquivos em tiles: {os.listdir(settings.TILES_DIR)}")
    if not settings.drive_is_configured():
        raise HTTPException(
            status_code=500,
            detail=(
                "Google Drive configuration is required. "
                "Set GOOGLE_DRIVE_FOLDER_ID and GOOGLE_SERVICE_ACCOUNT_JSON."
            ),
        )

    if base_image.content_type not in {"image/jpeg", "image/jpg", "image/png"}:
        raise HTTPException(status_code=400, detail="Only JPG and PNG files are allowed.")

    if pixel_size_mm <= 0:
        raise HTTPException(status_code=400, detail="pixel_size_mm must be greater than zero.")
    if max_uses not in {0, 2, 4}:
        raise HTTPException(status_code=400, detail="max_uses must be one of: 0, 2, 4.")
    if not (0.0 <= similarity <= 100.0):
        raise HTTPException(status_code=400, detail="similarity must be between 0 and 100.")


    import tempfile
    from PIL import Image
    from . import settings

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

    # Enviar para pasta de bases no Google Drive
    base_drive_id, base_drive_link = _upload_to_drive(resized_path, folder_id=settings.GOOGLE_DRIVE_BASES_FOLDER_ID)

    # Copiar para pasta de pixel (tiles) para integrar ao banco
    tile_drive_id, tile_drive_link = _upload_to_drive(resized_path, folder_id=settings.GOOGLE_DRIVE_TILES_FOLDER_ID)

    # Baixar tiles do Drive para pasta temporária
    tiles_temp_dir = download_tiles_from_drive(settings.GOOGLE_DRIVE_TILES_FOLDER_ID)

    if not any(tiles_temp_dir.glob("*.jpg")) and not any(tiles_temp_dir.glob("*.jpeg")) and not any(tiles_temp_dir.glob("*.png")):
        raise HTTPException(status_code=400, detail="Tiles folder is empty. Add images to Google Drive tiles folder.")

    output_name = _safe_output_name(base_image.filename or "mosaic")
    output_path = Path(f"/tmp/{output_name}")

    try:
        build_mosaic(
            reference_path=resized_path,
            tiles_folder=tiles_temp_dir,
            tile_size_mm=pixel_size_mm,
            max_uses=max_uses,
            output_path=output_path,
            similarity=similarity,
            quality=quality,
            dpi=settings.DEFAULT_DPI,
        )
        export_info = export_result(output_path, folder_id=settings.GOOGLE_DRIVE_OUTPUT_FOLDER_ID)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create mosaic: {exc}") from exc

    return JSONResponse(
        {
            "ok": True,
            "output_file": output_name,
            "download_url": f"/api/output/{output_name}",
            "drive_file_id": export_info.drive_file_id,
            "drive_web_link": export_info.drive_web_link,
            "base_drive_id": base_drive_id,
            "base_drive_link": base_drive_link,
            "tile_drive_id": tile_drive_id
        }
    )
