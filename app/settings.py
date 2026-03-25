import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

TILES_DIR = Path(os.getenv("MOSAIC_TILES_DIR", DATA_DIR / "tiles"))
INPUT_DIR = Path(os.getenv("MOSAIC_INPUT_DIR", "/tmp/mosaic_input"))
OUTPUT_DIR = Path(os.getenv("MOSAIC_OUTPUT_DIR", "/tmp/mosaic_output"))

DEFAULT_DPI = int(os.getenv("MOSAIC_DPI", "240"))
DEFAULT_QUALITY = int(os.getenv("MOSAIC_QUALITY", "85"))
MAX_UPLOAD_MB = int(os.getenv("MOSAIC_MAX_UPLOAD_MB", "20"))

def drive_is_configured() -> bool:
    return False  # Google Drive removido


for folder in (INPUT_DIR, OUTPUT_DIR):
    folder.mkdir(parents=True, exist_ok=True)
