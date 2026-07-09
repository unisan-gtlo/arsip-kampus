from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from django.conf import settings

SCOPES = ["https://www.googleapis.com/auth/drive"]

_service = None


def get_drive_service():
    global _service
    if _service is None:
        creds = Credentials.from_service_account_info(
            settings.GCP_SERVICE_ACCOUNT, scopes=SCOPES
        )
        _service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return _service


def upload_file(django_file, filename: str) -> tuple[str, str]:
    """Upload a Django UploadedFile to DRIVE_FOLDER_ID, return (file_id, link_view).

    DRIVE_FOLDER_ID must live inside a Shared Drive (not a personal "My Drive"
    folder) with the service account added as a member/editor. Google Drive
    rejects uploads from service accounts into regular My Drive storage with
    a storageQuotaExceeded error, since service accounts have no personal
    storage quota of their own. supportsAllDrives=True is required on every
    call below for Shared Drive items to work at all.
    """
    service = get_drive_service()
    media = MediaIoBaseUpload(
        django_file,
        mimetype=getattr(django_file, "content_type", None) or "application/pdf",
        resumable=True,
    )
    metadata = {"name": filename, "parents": [settings.DRIVE_FOLDER_ID]}
    created = (
        service.files()
        .create(body=metadata, media_body=media, fields="id", supportsAllDrives=True)
        .execute()
    )
    file_id = created["id"]
    # Files uploaded by the service account are private by default;
    # make them viewable via the preview link.
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        supportsAllDrives=True,
    ).execute()
    return file_id, f"https://drive.google.com/file/d/{file_id}/preview"


def delete_file(file_id: str) -> None:
    if not file_id:
        return
    service = get_drive_service()
    try:
        service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
    except Exception:
        pass


def replace_file(old_file_id: str, django_file, filename: str) -> tuple[str, str]:
    delete_file(old_file_id)
    return upload_file(django_file, filename)
