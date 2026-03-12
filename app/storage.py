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
