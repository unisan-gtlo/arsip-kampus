import streamlit as st
import bcrypt
from utils.sheets import get_sheet

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def get_all_users():
    sheet = get_sheet("users")
    records = sheet.get_all_records()
    return records

def login(username: str, password: str):
    users = get_all_users()
    for user in users:
        if user["username"] == username:
            if verify_password(password, str(user["password_hash"])):
                return {
                    "username": user["username"],
                    "nama": user["nama"],
                    "role": user["role"]
                }
    return None

def is_logged_in():
    return "user" in st.session_state and st.session_state.user is not None

def require_login():
    if not is_logged_in():
        st.warning("Silakan login terlebih dahulu.")
        st.stop()

def require_role(allowed_roles: list):
    require_login()
    role = st.session_state.user["role"]
    if role not in allowed_roles:
        st.error("Anda tidak memiliki akses ke halaman ini.")
        st.stop()

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.user = None