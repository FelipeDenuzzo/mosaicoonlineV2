import json
from dataclasses import dataclass
from pathlib import Path

from . import settings


@dataclass
class ExportResult:
    local_path: Path
    drive_file_id: str
    drive_web_link: str


def _upload_to_drive(file_path: Path) -> tuple[str, str]:
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not configured.")
    if not settings.GOOGLE_DRIVE_FOLDER_ID:
        raise RuntimeError("GOOGLE_DRIVE_FOLDER_ID is not configured.")

    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    service_info = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
    scopes = ["https://www.googleapis.com/auth/drive.file"]
    credentials = Credentials.from_service_account_info(service_info, scopes=scopes)

    drive = build("drive", "v3", credentials=credentials, cache_discovery=False)

    metadata = {
        "name": file_path.name,
        "parents": [settings.GOOGLE_DRIVE_FOLDER_ID],
    }
    media = MediaFileUpload(str(file_path), mimetype="image/jpeg", resumable=False)

    created = (
        drive.files()
        .create(body=metadata, media_body=media, fields="id, webViewLink")
        .execute()
    )

    return created.get("id", ""), created.get("webViewLink", "")


def export_result(file_path: Path) -> ExportResult:
    drive_id, web_link = _upload_to_drive(file_path)
    if not drive_id:
        raise RuntimeError("Google Drive upload succeeded without file id.")
    if not web_link:
        raise RuntimeError("Google Drive upload succeeded without web link.")

    return ExportResult(
        local_path=file_path,
        drive_file_id=drive_id,
        drive_web_link=web_link,
    )


# NOVO: Função para baixar todos os tiles da pasta 'tiles' do Google Drive para uma pasta temporária local
import tempfile
import shutil
from typing import List

def download_tiles_from_drive(tiles_folder_id: str) -> Path:
    """
    Baixa todas as imagens da pasta 'tiles' do Google Drive para uma pasta temporária local.
    Retorna o caminho da pasta temporária.
    """
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not configured.")
    if not tiles_folder_id:
        raise RuntimeError("Tiles folder ID is not configured.")

    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    import requests

    service_info = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    credentials = Credentials.from_service_account_info(service_info, scopes=scopes)
    drive = build("drive", "v3", credentials=credentials, cache_discovery=False)

    # Buscar arquivos de imagem na pasta
    query = f"'{tiles_folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png' or mimeType='image/jpg') and trashed=false"
    results = drive.files().list(q=query, fields="files(id, name, mimeType)", pageSize=1000).execute()
    files = results.get("files", [])

    temp_dir = Path(tempfile.mkdtemp(prefix="tiles_"))

    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        request = drive.files().get_media(fileId=file_id)
        file_path = temp_dir / file_name
        # Baixar arquivo
        with open(file_path, "wb") as f:
            downloader = build("drive", "v3", credentials=credentials, cache_discovery=False).files().get_media(fileId=file_id)
            from googleapiclient.http import MediaIoBaseDownload
            import io
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            f.write(fh.getvalue())

    return temp_dir
