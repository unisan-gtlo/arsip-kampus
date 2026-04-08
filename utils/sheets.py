import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def get_sheet(sheet_name: str):
    client = get_gspread_client()
    spreadsheet_id = st.secrets["SPREADSHEET_ID"]
    spreadsheet = client.open_by_key(spreadsheet_id)
    return spreadsheet.worksheet(sheet_name)

def get_all_documents():
    sheet = get_sheet("dokumen")
    records = sheet.get_all_records()
    return records

def add_document(data: dict):
    sheet = get_sheet("dokumen")
    row = [
        data["id"],
        data["judul"],
        data["kategori"],
        data["deskripsi"],
        data["file_id"],
        data["link_view"],
        data["tgl_upload"]
    ]
    sheet.append_row(row)

def update_document(row_index: int, data: dict):
    sheet = get_sheet("dokumen")
    sheet.update(f"A{row_index}:G{row_index}", [[
        data["id"],
        data["judul"],
        data["kategori"],
        data["deskripsi"],
        data["file_id"],
        data["link_view"],
        data["tgl_upload"]
    ]])

def delete_document(row_index: int):
    sheet = get_sheet("dokumen")
    sheet.delete_rows(row_index)

def get_all_users_sheet():
    sheet = get_sheet("users")
    return sheet.get_all_records()

def add_user(data: dict):
    sheet = get_sheet("users")
    sheet.append_row([
        data["username"],
        data["password_hash"],
        data["nama"],
        data["role"]
    ])

def delete_user(row_index: int):
    sheet = get_sheet("users")
    sheet.delete_rows(row_index)

@st.cache_data(ttl=10)
def get_all_kategori():
    sheet = get_sheet("kategori")
    records = sheet.get_all_records()
    return [r["nama_kategori"] for r in records if r["nama_kategori"]]

def add_kategori(nama: str):
    sheet = get_sheet("kategori")
    sheet.append_row([nama])

def delete_kategori(row_index: int):
    sheet = get_sheet("kategori")
    sheet.delete_rows(row_index)

@st.cache_data(ttl=10)
def get_all_documents():
    sheet = get_sheet("dokumen")
    records = sheet.get_all_records()
    return records

@st.cache_data(ttl=10)
def get_all_users_sheet():
    sheet = get_sheet("users")
    return sheet.get_all_records()    