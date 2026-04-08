import streamlit as st
from utils.auth import login, logout, is_logged_in
from utils.sidebar import show_sidebar
import os
import base64

st.set_page_config(
    page_title="Arsip Dokumen",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "user" not in st.session_state:
    st.session_state.user = None

# CSS global
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none; }
h1, h2, h3 { color: #1976D2; }
.stButton > button[kind="primary"] {
    background-color: #1976D2;
    color: white;
    border: none;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---- HALAMAN LOGIN ----
def show_login():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"):
            with open("logo.png", "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
            <div style='text-align:center; margin-bottom:0.5rem'>
                <img src='data:image/png;base64,{logo_base64}'
                     width='100'
                     style='border-radius:50%; border: 3px solid #1976D2'>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align:center; padding: 0.5rem 0'>
            <p style='font-size:22px; font-weight:700; color:#1976D2; margin:4px 0'>
                Sistem Arsip Dokumen
            </p>
            <p style='font-size:13px; color:gray; margin:0'>
                Universitas Ichsan Gorontalo
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("#### 🔐 Login")
            with st.form("form_login"):
                username = st.text_input("Username", placeholder="masukkan username")
                password = st.text_input("Password", type="password", placeholder="masukkan password")
                submit = st.form_submit_button("Login", use_container_width=True, type="primary")

                if submit:
                    if not username or not password:
                        st.error("Username dan password tidak boleh kosong.")
                    else:
                        user = login(username, password)
                        if user:
                            st.session_state.user = user
                            st.rerun()
                        else:
                            st.error("Username atau password salah.")

        st.markdown("""
        <div style='text-align:center; margin-top:1rem; font-size:12px; color:#999'>
            © 2025 Universitas Ichsan Gorontalo
        </div>
        """, unsafe_allow_html=True)

# ---- HALAMAN BERANDA SETELAH LOGIN ----
def show_beranda():
    show_sidebar()

    user = st.session_state.user
    role = user["role"]

    st.title("🏠 Beranda")
    st.markdown(f"Selamat datang, **{user['nama']}**!")
    st.divider()

    if role == "admin":
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.markdown("### 📊")
                st.markdown("**Dashboard Dokumen**")
                st.markdown("Lihat & kelola semua dokumen arsip")
                st.page_link("pages/1_Dashboard_Admin.py", label="Buka Dashboard →")
        with col2:
            with st.container(border=True):
                st.markdown("### 📤")
                st.markdown("**Upload Dokumen**")
                st.markdown("Tambahkan dokumen arsip baru")
                st.page_link("pages/2_Upload_Dokumen.py", label="Upload Sekarang →")
        with col3:
            with st.container(border=True):
                st.markdown("### 🔍")
                st.markdown("**Portal Pencarian**")
                st.markdown("Cari dan preview dokumen")
                st.page_link("pages/4_Portal_User.py", label="Cari Dokumen →")

        col4, col5 = st.columns(2)
        with col4:
            with st.container(border=True):
                st.markdown("### 👥")
                st.markdown("**Kelola User**")
                st.markdown("Tambah & hapus pengguna sistem")
                st.page_link("pages/3_Kelola_User.py", label="Kelola User →")
        with col5:
            with st.container(border=True):
                st.markdown("### 🗂️")
                st.markdown("**Kelola Kategori**")
                st.markdown("Atur master kategori dokumen")
                st.page_link("pages/5_Kelola_Kategori.py", label="Kelola Kategori →")

    elif role == "operator":
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.markdown("### 📊")
                st.markdown("**Dashboard Dokumen**")
                st.markdown("Lihat semua dokumen arsip")
                st.page_link("pages/1_Dashboard_Admin.py", label="Buka Dashboard →")
        with col2:
            with st.container(border=True):
                st.markdown("### 📤")
                st.markdown("**Upload Dokumen**")
                st.markdown("Tambahkan dokumen arsip baru")
                st.page_link("pages/2_Upload_Dokumen.py", label="Upload Sekarang →")
        with col3:
            with st.container(border=True):
                st.markdown("### 🔍")
                st.markdown("**Portal Pencarian**")
                st.markdown("Cari dan preview dokumen")
                st.page_link("pages/4_Portal_User.py", label="Cari Dokumen →")

    else:
        with st.container(border=True):
            st.markdown("### 🔍")
            st.markdown("**Portal Pencarian Dokumen**")
            st.markdown("Cari, preview, dan download dokumen kampus")
            st.page_link("pages/4_Portal_User.py", label="Cari Dokumen →")

# ---- MAIN ----
if is_logged_in():
    show_beranda()
else:
    show_login()