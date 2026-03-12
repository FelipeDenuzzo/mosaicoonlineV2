import io
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import settings


@dataclass
class ExportResult:
    local_path: Path
    drive_file_id: str
    drive_web_link: str


def _get_drive_client():
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build

    service_info = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
    scopes = ["https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(service_info, scopes=scopes)
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def _upload_to_drive(file_path: Path, folder_id: Optional[str] = None) -> tuple[str, str]:
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not configured.")

    target_folder = folder_id or settings.GOOGLE_DRIVE_FOLDER_ID
    if not target_folder:
        raise RuntimeError("GOOGLE_DRIVE_FOLDER_ID is not configured.")

    from googleapiclient.http import MediaFileUpload

    drive = _get_drive_client()

    # Detect mimetype
    suffix = file_path.suffix.lower()
    if suffix == ".png":
        mimetype = "image/png"
    else:
        mimetype = "image/jpeg"

    metadata = {
        "name": file_path.name,
        "parents": [target_folder],
    }
    media = MediaFileUpload(str(file_path), mimetype=mimetype, resumable=False)
    created = (
        drive.files()
        .create(
            body=metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True,
        )
        .execute()
    )

    file_id = created.get("id", "")
    web_link = created.get("webViewLink", "")

    # Transfer ownership to the Drive owner if configured
    owner_email = getattr(settings, "GOOGLE_DRIVE_OWNER_EMAIL", "") or ""
    if owner_email and file_id:
        try:
            drive.permissions().create(
                fileId=file_id,
                body={"role": "owner", "type": "user", "emailAddress": owner_email},
                transferOwnership=True,
                supportsAllDrives=True,
            ).execute()
        except Exception:
            # Transfer may fail on Shared Drives or cross-domain — ignore
            pass

    return file_id, web_link


def export_result(file_path: Path, folder_id: Optional[str] = None) -> ExportResult:
    drive_id, web_link = _upload_to_drive(file_path, folder_id=folder_id)
    if not drive_id:
        raise RuntimeError("Google Drive upload succeeded without file id.")
    if not web_link:
        raise RuntimeError("Google Drive upload succeeded without web link.")
    return ExportResult(
        local_path=file_path,
        drive_file_id=drive_id,
        drive_web_link=web_link,
    )


def download_tiles_from_drive(tiles_folder_id: str) -> Path:
    """
    Baixa todas as imagens da pasta 'tiles' do Google Drive para uma pasta temporaria local.
    Retorna o caminho da pasta temporaria.
    """
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not configured.")
    if not tiles_folder_id:
        raise RuntimeError("Tiles folder ID is not configured.")

    from googleapiclient.http import MediaIoBaseDownload

    drive = _get_drive_client()
    query = (
        f"'{tiles_folder_id}' in parents and "
        "(mimeType='image/jpeg' or mimeType='image/png' or mimeType='image/jpg') "
        "and trashed=false"
    )
    results = drive.files().list(
        q=query,
        fields="files(id, name)",
        pageSize=1000,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = results.get("files", [])

    temp_dir = Path(tempfile.mkdtemp(prefix="tiles_"))
    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        request = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
        file_path = temp_dir / file_name
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        file_path.write_bytes(fh.getvalue())

    return temp_dir
