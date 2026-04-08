import re
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]

@st.cache_resource
def get_drive_service():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)
    return service

def get_drive_ids_from_link(drive_link: str):
    """
    Ekstrak file_id dari berbagai format link Google Drive.
    """
    patterns = [
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"id=([a-zA-Z0-9_-]+)",
        r"/d/([a-zA-Z0-9_-]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, drive_link)
        if match:
            file_id = match.group(1)
            link_view = f"https://drive.google.com/file/d/{file_id}/preview"
            return file_id, link_view
    return None, None

def delete_file_from_drive(file_id: str):
    service = get_drive_service()
    service.files().delete(fileId=file_id).execute()