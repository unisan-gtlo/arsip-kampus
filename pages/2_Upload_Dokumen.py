import streamlit as st
from utils.auth import require_role
from utils.drive import get_drive_ids_from_link
from utils.sheets import add_document, get_all_kategori, get_all_documents
import pandas as pd
import uuid
from datetime import datetime

st.set_page_config(page_title="Upload Dokumen", page_icon="📤", layout="centered")

if "user" not in st.session_state:
    st.session_state.user = None
if "kategori_dipilih" not in st.session_state:
    st.session_state.kategori_dipilih = None
# Selalu reset form_submitted saat halaman dimuat ulang dari sidebar
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "judul_tersimpan" not in st.session_state:
    st.session_state.judul_tersimpan = ""

# Reset otomatis jika masuk dari halaman lain
if "upload_page_active" not in st.session_state:
    st.session_state.upload_page_active = False

if not st.session_state.upload_page_active:
    st.session_state.form_submitted = False
    st.session_state.judul_tersimpan = ""
    st.session_state.upload_page_active = True

require_role(["admin", "operator"])
from utils.sidebar import show_sidebar
show_sidebar()

user = st.session_state.user
st.title("📤 Tambah Dokumen Baru")
st.markdown(f"Login sebagai: **{user['nama']}** | Role: `{user['role']}`")
st.divider()

KATEGORI = get_all_kategori()
if not KATEGORI:
    st.warning("Belum ada kategori. Minta admin menambahkan kategori terlebih dahulu.")
    st.stop()

# Ambil data dokumen untuk referensi nomor terakhir
docs = get_all_documents()
df_docs = pd.DataFrame(docs) if docs else pd.DataFrame()

# Buat dictionary nomor terakhir per kategori
nomor_per_kategori = {}
if not df_docs.empty and "nomor_dokumen" in df_docs.columns:
    df_valid = df_docs[df_docs["nomor_dokumen"].astype(str).str.strip() != ""]
    if not df_valid.empty:
        for kat in df_valid["kategori"].unique():
            df_kat = df_valid[df_valid["kategori"] == kat]
            nomor_per_kategori[kat] = df_kat.iloc[-1]["nomor_dokumen"]

# Tampilkan pesan sukses dan tombol pilihan setelah berhasil simpan
if st.session_state.form_submitted:
    st.success(f"✅ Dokumen **'{st.session_state.judul_tersimpan}'** berhasil disimpan!")
    st.markdown(" ")
    col_baru, col_dashboard = st.columns(2)
    with col_baru:
        if st.button(
            "➕ Tambah Dokumen Baru",
            use_container_width=True,
            type="primary"
        ):
            st.session_state.form_submitted = False
            st.session_state.judul_tersimpan = ""
            st.session_state.upload_page_active = True
            st.rerun()
    with col_dashboard:
        st.page_link(
            "pages/1_Dashboard_Admin.py",
            label="📊 Kembali ke Dashboard",
            use_container_width=True
        )
    st.stop()

# Pilih kategori di luar form agar reaktif
kategori_dipilih = st.selectbox(
    "Kategori *",
    KATEGORI,
    key="kategori_select"
)

# Tampilkan nomor terakhir berdasarkan kategori yang dipilih
if kategori_dipilih in nomor_per_kategori:
    st.info(f"📋 Nomor terakhir **{kategori_dipilih}**: **{nomor_per_kategori[kategori_dipilih]}**")
else:
    st.warning(f"📋 Belum ada dokumen untuk kategori **{kategori_dipilih}**")

st.divider()

st.info("""
**Cara menambah dokumen:**
1. Upload file PDF ke Google Drive Anda seperti biasa
2. Klik kanan file → **"Get link"** → ubah akses ke **"Anyone with the link"** → klik **"Copy link"**
3. Paste link tersebut di form di bawah
""")

with st.form("form_upload"):
    nomor_dokumen = st.text_input(
        "Nomor Dokumen",
        placeholder="contoh: 003/SK-UNISAN/V/2025"
    )
    judul = st.text_input("Judul Dokumen *")
    deskripsi = st.text_area("Deskripsi Dokumen")
    deskripsi = st.text_area("Deskripsi Dokumen")
    sifat = st.radio(
        "Sifat Dokumen *",
        options=["Umum", "Rahasia"],
        horizontal=True,
        help="Umum = bisa diakses publik tanpa login | Rahasia = hanya untuk user yang login"
    )
    drive_link = st.text_input(...)
    drive_link = st.text_input(
        "Link Google Drive *",
        placeholder="https://drive.google.com/file/d/xxxx/view?usp=sharing"
    )

    submit = st.form_submit_button(
        "💾 Simpan Dokumen",
        use_container_width=True,
        type="primary"
    )

    if submit:
        if not judul:
            st.error("Judul tidak boleh kosong.")
        elif not drive_link:
            st.error("Link Google Drive wajib diisi.")
        else:
            file_id, link_view = get_drive_ids_from_link(drive_link)
            if not file_id:
                st.error("Format link Google Drive tidak valid. Pastikan link sudah benar.")
            else:
                with st.spinner("Menyimpan dokumen..."):
                    doc_id = str(uuid.uuid4())[:8].upper()
                    tgl = datetime.now().strftime("%Y-%m-%d %H:%M")
                    add_document({
                    "id": doc_id,
                    "nomor_dokumen": nomor_dokumen.strip(),
                    "judul": judul,
                    "kategori": kategori_dipilih,
                    "deskripsi": deskripsi,
                    "file_id": file_id,
                    "link_view": link_view,
                    "tgl_upload": tgl,
                    "sifat": sifat
                })
                st.session_state.form_submitted = True
                st.session_state.judul_tersimpan = judul
                st.rerun()

st.divider()
st.subheader("🔍 Preview PDF")
st.markdown("Paste link Drive di bawah untuk test preview sebelum disimpan:")
test_link = st.text_input(
    "Test link preview",
    placeholder="https://drive.google.com/file/d/xxxx/view"
)
if test_link:
    file_id_test, link_view_test = get_drive_ids_from_link(test_link)
    if link_view_test:
        st.components.v1.iframe(link_view_test, height=500, scrolling=True)
    else:
        st.error("Link tidak valid.")