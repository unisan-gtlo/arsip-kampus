import streamlit as st
from utils.auth import require_role, hash_password
from utils.sheets import get_all_users_sheet, add_user, delete_user, get_sheet
import pandas as pd

st.set_page_config(page_title="Kelola User", page_icon="👥", layout="centered")

if "user" not in st.session_state:
    st.session_state.user = None

require_role(["admin"])
from utils.sidebar import show_sidebar
show_sidebar()

user = st.session_state.user
st.title("👥 Kelola Pengguna")
st.markdown(f"Login sebagai: **{user['nama']}** | Role: `{user['role']}`")
st.divider()

users = get_all_users_sheet()

if users:
    st.subheader(f"Daftar Pengguna ({len(users)})")

    # Header tabel
    col_no, col_user, col_nama, col_role, col_aksi = st.columns([1, 3, 3, 2, 2])
    with col_no:
        st.markdown("**No**")
    with col_user:
        st.markdown("**Username**")
    with col_nama:
        st.markdown("**Nama**")
    with col_role:
        st.markdown("**Role**")
    with col_aksi:
        st.markdown("**Hapus**")

    st.markdown("<hr style='margin: 4px 0 8px 0'>", unsafe_allow_html=True)

    for idx, u in enumerate(users):
        konfirm_key = f"konfirm_user_{idx}"
        if konfirm_key not in st.session_state:
            st.session_state[konfirm_key] = False

        if not st.session_state[konfirm_key]:
            col_no, col_user, col_nama, col_role, col_aksi = st.columns([1, 3, 3, 2, 2])
            with col_no:
                st.markdown(f"{idx + 1}")
            with col_user:
                st.markdown(f"`{u['username']}`")
            with col_nama:
                st.markdown(f"{u['nama']}")
            with col_role:
                role = u['role']
                if role == "admin":
                    st.markdown("🔴 admin")
                elif role == "operator":
                    st.markdown("🟠 operator")
                else:
                    st.markdown("🟢 user")
            with col_aksi:
                if u['username'] == user['username']:
                    st.markdown("_(akun aktif)_")
                else:
                    if st.button("🔴 Hapus", key=f"del_user_{idx}", use_container_width=True):
                        st.session_state[konfirm_key] = True
                        st.rerun()
        else:
            col_no, col_info, col_ya, col_tidak = st.columns([1, 5, 2, 2])
            with col_no:
                st.markdown(f"{idx + 1}")
            with col_info:
                st.warning(f"Hapus user **{u['username']}**?")
            with col_ya:
                if st.button("✅ Ya", key=f"ya_user_{idx}", use_container_width=True):
                    delete_user(idx + 2)
                    st.session_state[konfirm_key] = False
                    st.success(f"User '{u['username']}' berhasil dihapus.")
                    st.rerun()
            with col_tidak:
                if st.button("❌ Tidak", key=f"tidak_user_{idx}", use_container_width=True):
                    st.session_state[konfirm_key] = False
                    st.rerun()

        st.markdown("<hr style='margin: 4px 0'>", unsafe_allow_html=True)

else:
    st.info("Belum ada pengguna.")

st.divider()
st.subheader("➕ Tambah Pengguna Baru")

with st.form("form_tambah_user"):
    col_a, col_b = st.columns(2)
    with col_a:
        username_baru = st.text_input("Username *")
        password_baru = st.text_input("Password *", type="password")
    with col_b:
        nama_baru = st.text_input("Nama Lengkap *")
        role_baru = st.selectbox("Role *", ["user", "operator", "admin"])

    submit = st.form_submit_button("Tambah User", use_container_width=True, type="primary")

    if submit:
        if not username_baru or not nama_baru or not password_baru:
            st.error("Semua field wajib diisi.")
        else:
            existing = [u["username"] for u in users]
            if username_baru in existing:
                st.error("Username sudah digunakan.")
            else:
                hashed = hash_password(password_baru)
                add_user({
                    "username": username_baru,
                    "password_hash": hashed,
                    "nama": nama_baru,
                    "role": role_baru
                })
                st.success(f"User '{username_baru}' berhasil ditambahkan.")
                st.rerun()