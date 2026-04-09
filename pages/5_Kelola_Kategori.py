import streamlit as st
from utils.auth import require_role
from utils.sheets import get_all_kategori, add_kategori, delete_kategori, get_sheet

st.set_page_config(page_title="Kelola Kategori", page_icon="🗂️", layout="centered")

if "user" not in st.session_state:
    st.session_state.user = None

require_role(["admin"])
from utils.sidebar import show_sidebar
show_sidebar()

user = st.session_state.user
st.title("🗂️ Kelola Kategori Dokumen")
st.markdown(f"Login sebagai: **{user['nama']}** | Role: `{user['role']}`")
st.divider()

kategori_list = get_all_kategori()

if kategori_list:
    st.subheader(f"Daftar Kategori ({len(kategori_list)})")

    # Header tabel
    col_no, col_nama, col_edit, col_hapus = st.columns([1, 5, 2, 2])
    with col_no:
        st.markdown("**No**")
    with col_nama:
        st.markdown("**Nama Kategori**")
    with col_edit:
        st.markdown("**Edit**")
    with col_hapus:
        st.markdown("**Hapus**")

    st.markdown("<hr style='margin: 4px 0 8px 0'>", unsafe_allow_html=True)

    for idx, nama in enumerate(kategori_list):
        edit_key = f"edit_kat_{idx}"
        konfirm_key = f"konfirm_kat_{idx}"

        if edit_key not in st.session_state:
            st.session_state[edit_key] = False
        if konfirm_key not in st.session_state:
            st.session_state[konfirm_key] = False

        # Baris normal
        if not st.session_state[edit_key] and not st.session_state[konfirm_key]:
            col_no, col_nama_val, col_edit_btn, col_hapus_btn = st.columns([1, 5, 2, 2])
            with col_no:
                st.markdown(f"{idx + 1}")
            with col_nama_val:
                st.markdown(f"🏷️ {nama}")
            with col_edit_btn:
                if st.button("🟠 Edit", key=f"btn_edit_kat_{idx}", use_container_width=True):
                    st.session_state[edit_key] = True
                    st.rerun()
            with col_hapus_btn:
                if st.button("🔴 Hapus", key=f"btn_del_kat_{idx}", use_container_width=True):
                    st.session_state[konfirm_key] = True
                    st.rerun()

        # Baris mode edit
        elif st.session_state[edit_key]:
            with st.form(key=f"form_edit_kat_{idx}"):
                col_no, col_input, col_simpan, col_batal = st.columns([1, 5, 2, 2])
                with col_no:
                    st.markdown(f"{idx + 1}")
                with col_input:
                    nama_baru = st.text_input(
                        "Nama baru",
                        value=nama,
                        label_visibility="collapsed"
                    )
                with col_simpan:
                    simpan = st.form_submit_button(
                        "💾 Simpan",
                        use_container_width=True,
                        type="primary"
                    )
                with col_batal:
                    batal = st.form_submit_button(
                        "✖ Batal",
                        use_container_width=True
                    )

                if simpan:
                    if not nama_baru.strip():
                        st.error("Nama kategori tidak boleh kosong.")
                    elif nama_baru.strip() in kategori_list and nama_baru.strip() != nama:
                        st.error(f"Kategori '{nama_baru}' sudah ada.")
                    else:
                        sheet = get_sheet("kategori")
                        sheet.update(f"A{idx + 2}", [[nama_baru.strip()]])
                        st.cache_data.clear()
                        st.session_state[edit_key] = False
                        st.success(f"Kategori berhasil diubah menjadi '{nama_baru}'!")
                        st.rerun()

                if batal:
                    st.session_state[edit_key] = False
                    st.rerun()

        # Baris mode konfirmasi hapus
        elif st.session_state[konfirm_key]:
            col_no, col_nama_val, col_ya, col_tidak = st.columns([1, 5, 2, 2])
            with col_no:
                st.markdown(f"{idx + 1}")
            with col_nama_val:
                st.warning(f"Hapus kategori **{nama}**?")
            with col_ya:
                if st.button("✅ Ya, Hapus", key=f"ya_kat_{idx}", use_container_width=True):
                    delete_kategori(idx + 2)
                    st.cache_data.clear()
                    st.session_state[konfirm_key] = False
                    st.success(f"Kategori '{nama}' berhasil dihapus.")
                    st.rerun()
            with col_tidak:
                if st.button("❌ Tidak", key=f"tidak_kat_{idx}", use_container_width=True):
                    st.session_state[konfirm_key] = False
                    st.rerun()

        st.markdown("<hr style='margin: 4px 0'>", unsafe_allow_html=True)

else:
    st.info("Belum ada kategori. Tambahkan kategori baru di bawah.")

st.divider()
st.subheader("➕ Tambah Kategori Baru")

with st.form("form_tambah_kategori"):
    nama_baru = st.text_input(
        "Nama Kategori *",
        placeholder="contoh: Peraturan, MOU, Berita Acara"
    )
    submit = st.form_submit_button("Tambah Kategori", use_container_width=True, type="primary")

    if submit:
        if not nama_baru.strip():
            st.error("Nama kategori tidak boleh kosong.")
        elif nama_baru.strip() in kategori_list:
            st.error(f"Kategori '{nama_baru}' sudah ada.")
        else:
            add_kategori(nama_baru.strip())
            st.cache_data.clear()
            st.success(f"Kategori '{nama_baru}' berhasil ditambahkan!")
            st.rerun()