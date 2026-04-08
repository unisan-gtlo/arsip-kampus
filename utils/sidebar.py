import streamlit as st
from utils.auth import logout
import os
import base64

def show_sidebar():
    # Sembunyikan navigasi default Streamlit
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] { min-width: 260px; max-width: 260px; }
    .menu-item {
        display: flex;
        align-items: center;
        padding: 10px 16px;
        border-radius: 10px;
        margin: 3px 0;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        color: var(--color-text-primary);
        text-decoration: none;
        transition: background 0.2s;
    }
    .menu-item:hover { background: var(--color-background-secondary); }
    .menu-item.active {
        background: #E3F0FC;
        color: #1976D2;
        font-weight: 600;
    }
    .menu-icon { margin-right: 10px; font-size: 16px; }
    .menu-section {
        font-size: 11px;
        font-weight: 600;
        color: gray;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 12px 16px 4px 16px;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Logo dan nama sistem
        if os.path.exists("logo.png"):
            with open("logo.png", "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
            <div style='text-align:center; padding: 8px 0 4px 0'>
                <img src='data:image/png;base64,{logo_b64}'
                     width='72'
                     style='border-radius:50%; border: 2px solid #1976D2'>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align:center; padding: 4px 0 8px 0'>
            <p style='font-weight:700; font-size:14px; margin:4px 0; color:#1976D2'>
                Sistem Arsip Dokumen
            </p>
            <p style='font-size:11px; color:gray; margin:0'>
                Universitas Ichsan Gorontalo
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        if "user" not in st.session_state or not st.session_state.user:
            return

        user = st.session_state.user
        role = user["role"]

        # Info user
        role_warna = {"admin": "#E53935", "operator": "#F57C00", "user": "#2E7D32"}
        role_label = {"admin": "Administrator", "operator": "Operator", "user": "User"}
        warna = role_warna.get(role, "gray")
        label = role_label.get(role, role)

        st.markdown(f"""
        <div style='background: var(--color-background-secondary);
                    border-radius: 10px; padding: 10px 14px; margin-bottom: 8px'>
            <p style='font-size:13px; font-weight:600; margin:0'>👤 {user['nama']}</p>
            <p style='font-size:11px; margin:2px 0 0 0'>
                <span style='background:{warna}; color:white;
                             padding: 2px 8px; border-radius:20px; font-size:10px'>
                    {label}
                </span>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Deteksi halaman aktif
        current = st.query_params.get("page", "")
        try:
            current_page = st.session_state.get("current_page", "")
        except:
            current_page = ""

        # Menu navigasi berdasarkan role
        if role in ["admin", "operator"]:
            st.markdown("<div class='menu-section'>Menu Utama</div>", unsafe_allow_html=True)

            st.page_link("app.py",                        label="🏠  Beranda",           use_container_width=True)
            st.page_link("pages/1_Dashboard_Admin.py",    label="📊  Dashboard Dokumen", use_container_width=True)
            st.page_link("pages/2_Upload_Dokumen.py",     label="📤  Upload Dokumen",    use_container_width=True)
            st.page_link("pages/4_Portal_User.py",        label="🔍  Portal Pencarian",  use_container_width=True)

            if role == "admin":
                st.markdown("<div class='menu-section'>Pengaturan</div>", unsafe_allow_html=True)
                st.page_link("pages/3_Kelola_User.py",       label="👥  Kelola User",       use_container_width=True)
                st.page_link("pages/5_Kelola_Kategori.py",   label="🗂️  Kelola Kategori",   use_container_width=True)

        else:
            st.markdown("<div class='menu-section'>Menu</div>", unsafe_allow_html=True)
            st.page_link("app.py",                 label="🏠  Beranda",          use_container_width=True)
            st.page_link("pages/4_Portal_User.py", label="🔍  Cari Dokumen",     use_container_width=True)

        st.divider()

        if st.button("🚪  Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.user = None
            st.switch_page("app.py")

        # Footer
        st.markdown("""
        <div style='text-align:center; margin-top:8px'>
            <p style='font-size:10px; color:lightgray; margin:0'>© 2025 Unichsan Gorontalo</p>
        </div>
        """, unsafe_allow_html=True)