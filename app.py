import streamlit as st
from utils.auth import login, logout, is_logged_in
import os

st.set_page_config(
    page_title="Arsip Dokumen",
    page_icon="🗂️",
    layout="centered",
    initial_sidebar_state="expanded"
)

if "user" not in st.session_state:
    st.session_state.user = None

# ---- SIDEBAR BRANDING ----
with st.sidebar:
    # Logo kampus
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.markdown("## 🏛️")

    st.markdown("### Sistem Arsip Dokumen")
    st.markdown("**Universitas Ichsan Gorontalo**")
    st.markdown("---")

    if is_logged_in():
        user = st.session_state.user
        st.markdown(f"👤 **{user['nama']}**")
        role_label = {
            "admin": "🔴 Administrator",
            "operator": "🟠 Operator",
            "user": "🟢 User"
        }.get(user['role'], user['role'])
        st.markdown(f"{role_label}")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

# ---- CSS GLOBAL ----
st.markdown("""
<style>
/* Sidebar navigation label */
[data-testid="stSidebarNav"] {
    padding-top: 0rem;
}
/* Sembunyikan nama file mentah, tampilkan nama bersih */
[data-testid="stSidebarNavLink"] span {
    font-size: 14px;
}
/* Warna header */
h1, h2, h3 {
    color: #1976D2;
}
/* Tombol primary */
.stButton > button[kind="primary"] {
    background-color: #1976D2;
    color: white;
    border: none;
    border-radius: 8px;
}
.stButton > button[kind="primary"]:hover {
    background-color: #1565C0;
}
</style>
""", unsafe_allow_html=True)

# ---- HALAMAN LOGIN ----
def show_login():
    # CSS khusus halaman login
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        text-align: center;
    }
    .login-title {
        font-size: 24px;
        font-weight: 600;
        color: #1976D2;
        margin: 0.5rem 0 0.2rem 0;
    }
    .login-subtitle {
        font-size: 14px;
        color: #666;
        margin-bottom: 1.5rem;
    }
    /* Sembunyikan sidebar di halaman login */
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Logo center menggunakan base64
        if os.path.exists("logo.png"):
            import base64
            with open("logo.png", "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
            <div style='text-align:center; margin-bottom:0.5rem'>
                <img src='data:image/png;base64,{logo_base64}' 
                     width='100' 
                     style='border-radius:50%; border: 3px solid #1976D2'>
            </div>
            """, unsafe_allow_html=True)

        # Judul
        st.markdown("""
        <div style='text-align:center; padding: 0.5rem 0'>
            <p class='login-title'>Sistem Arsip Dokumen</p>
            <p class='login-subtitle'>Universitas Ichsan Gorontalo</p>
        </div>
        """, unsafe_allow_html=True)

        # Form login dalam card
        with st.container(border=True):
            st.markdown("#### 🔐 Login")
            with st.form("form_login"):
                username = st.text_input(
                    "Username",
                    placeholder="masukkan username"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="masukkan password"
                )
                submit = st.form_submit_button(
                    "Login",
                    use_container_width=True,
                    type="primary"
                )

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

        # Footer
        st.markdown("""
        <div style='text-align:center; margin-top:1rem; font-size:12px; color:#999'>
            © 2025 Universitas Ichsan Gorontalo
        </div>
        """, unsafe_allow_html=True)

# ---- HALAMAN DASHBOARD SETELAH LOGIN ----
def show_dashboard():
    user = st.session_state.user
    role = user["role"]

    st.markdown(f"## Selamat datang, {user['nama']}! 👋")
    st.markdown(f"Silakan pilih menu di sidebar untuk memulai.")
    st.divider()

    if role == "admin":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("📊 **Dashboard Admin**\n\nLihat & kelola semua dokumen")
            st.page_link("pages/1_Dashboard_Admin.py", label="Buka Dashboard", icon="📊")
        with col2:
            st.info("📤 **Upload Dokumen**\n\nTambah dokumen baru")
            st.page_link("pages/2_Upload_Dokumen.py", label="Upload Dokumen", icon="📤")
        with col3:
            st.info("👥 **Kelola User**\n\nTambah & hapus pengguna")
            st.page_link("pages/3_Kelola_User.py", label="Kelola User", icon="👥")

        col4, col5 = st.columns([1, 2])
        with col4:
            st.info("🗂️ **Kelola Kategori**\n\nAtur master kategori")
            st.page_link("pages/5_Kelola_Kategori.py", label="Kelola Kategori", icon="🗂️")
        with col5:
            st.info("🔍 **Portal User**\n\nCari & preview dokumen")
            st.page_link("pages/4_Portal_User.py", label="Portal Dokumen", icon="🔍")

    elif role == "operator":
        col1, col2 = st.columns(2)
        with col1:
            st.info("📊 **Dashboard**\n\nLihat semua dokumen")
            st.page_link("pages/1_Dashboard_Admin.py", label="Buka Dashboard", icon="📊")
        with col2:
            st.info("📤 **Upload Dokumen**\n\nTambah dokumen baru")
            st.page_link("pages/2_Upload_Dokumen.py", label="Upload Dokumen", icon="📤")

    else:
        st.info("🔍 **Portal Dokumen**\n\nCari, preview, dan download dokumen kampus")
        st.page_link("pages/4_Portal_User.py", label="Cari Dokumen", icon="🔍")

# ---- MAIN ----
if is_logged_in():
    show_dashboard()
else:
    show_login()