import streamlit as st
from utils.auth import require_role
from utils.sheets import get_all_documents, delete_document, get_sheet, get_all_kategori
from utils.drive import get_drive_ids_from_link
import pandas as pd

st.set_page_config(page_title="Dashboard Admin", page_icon="📊", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

require_role(["admin", "operator"])

# Custom CSS warna tombol
st.markdown("""
<style>
div[data-testid="column"]:nth-child(1) .stLinkButton a {
    background-color: #1976D2;
    color: white;
    border: none;
    border-radius: 8px;
}
div[data-testid="column"]:nth-child(1) .stLinkButton a:hover {
    background-color: #1565C0;
    color: white;
}
div[data-testid="column"]:nth-child(2) .stLinkButton a {
    background-color: #2E7D32;
    color: white;
    border: none;
    border-radius: 8px;
}
div[data-testid="column"]:nth-child(2) .stLinkButton a:hover {
    background-color: #1B5E20;
    color: white;
}
</style>
""", unsafe_allow_html=True)

user = st.session_state.user
st.title("📊 Dashboard Dokumen")
st.markdown(f"Login sebagai: **{user['nama']}** | Role: `{user['role']}`")
st.divider()

docs = get_all_documents()
KATEGORI = get_all_kategori()

if not docs:
    st.info("Belum ada dokumen yang tersimpan.")
else:
    df = pd.DataFrame(docs)

    # Metric cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Dokumen", len(df))
    with col2:
        kategori_terbanyak = df["kategori"].value_counts().idxmax() if len(df) > 0 else "-"
        st.metric("Kategori Terbanyak", kategori_terbanyak)
    with col3:
        jumlah_kategori = df["kategori"].nunique()
        st.metric("Jumlah Kategori", jumlah_kategori)

    st.divider()

    # Filter dan pencarian
    col_filter, col_cari = st.columns([2, 3])
    with col_filter:
        kategori_filter = st.selectbox(
            "Filter Kategori",
            options=["Semua"] + sorted(df["kategori"].unique().tolist())
        )
    with col_cari:
        cari = st.text_input("Cari judul dokumen...")

    filtered = df.copy()
    if kategori_filter != "Semua":
        filtered = filtered[filtered["kategori"] == kategori_filter]
    if cari:
        filtered = filtered[filtered["judul"].str.contains(cari, case=False, na=False)]

    st.markdown(f"Menampilkan **{len(filtered)}** dokumen")
    st.divider()

    for i, row in filtered.iterrows():
        with st.expander(f"📄 {row['judul']} — {row['kategori']}"):

            edit_key = f"edit_mode_{row['id']}"
            konfirm_key = f"konfirm_{row['id']}"

            if edit_key not in st.session_state:
                st.session_state[edit_key] = False
            if konfirm_key not in st.session_state:
                st.session_state[konfirm_key] = False

            # ---- MODE EDIT ----
            if st.session_state[edit_key]:
                st.markdown("### ✏️ Edit Dokumen")
                with st.form(key=f"form_edit_{row['id']}"):
                    judul_baru = st.text_input("Judul", value=row["judul"])
                    kategori_baru = st.selectbox(
                        "Kategori",
                        KATEGORI,
                        index=KATEGORI.index(row["kategori"]) if row["kategori"] in KATEGORI else 0
                    )
                    deskripsi_baru = st.text_area("Deskripsi", value=row["deskripsi"])
                    link_baru = st.text_input(
                        "Link Google Drive (kosongkan jika tidak diganti)",
                        placeholder="https://drive.google.com/file/d/xxxx/view"
                    )

                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        simpan = st.form_submit_button(
                            "💾 Simpan Perubahan",
                            use_container_width=True,
                            type="primary"
                        )
                    with col_cancel:
                        batal = st.form_submit_button(
                            "✖ Batal",
                            use_container_width=True
                        )

                    if simpan:
                        if not judul_baru:
                            st.error("Judul tidak boleh kosong.")
                        else:
                            if link_baru.strip():
                                file_id_baru, link_view_baru = get_drive_ids_from_link(link_baru)
                                if not file_id_baru:
                                    st.error("Format link Google Drive tidak valid.")
                                    st.stop()
                            else:
                                file_id_baru = row["file_id"]
                                link_view_baru = row["link_view"]

                            all_docs = get_all_documents()
                            row_index = None
                            for idx, doc in enumerate(all_docs):
                                if doc["id"] == row["id"]:
                                    row_index = idx + 2
                                    break

                            if row_index:
                                sheet = get_sheet("dokumen")
                                sheet.update(f"A{row_index}:G{row_index}", [[
                                    row["id"],
                                    judul_baru,
                                    kategori_baru,
                                    deskripsi_baru,
                                    file_id_baru,
                                    link_view_baru,
                                    row["tgl_upload"]
                                ]])
                                st.success("✅ Dokumen berhasil diperbarui!")
                                st.session_state[edit_key] = False
                                st.rerun()

                    if batal:
                        st.session_state[edit_key] = False
                        st.rerun()

            # ---- MODE TAMPIL NORMAL ----
            else:
                st.markdown(f"**Deskripsi:** {row['deskripsi']}")
                st.markdown(f"**Tanggal Upload:** {row['tgl_upload']}")

                # Tombol aksi
                col_a, col_b, col_c, col_d = st.columns([2, 2, 1, 1])
                with col_a:
                    st.link_button(
                        "🔵 Buka PDF",
                        row["link_view"],
                        use_container_width=True
                    )
                with col_b:
                    download_url = f"https://drive.google.com/uc?export=download&id={row['file_id']}"
                    st.link_button(
                        "🟢 Download",
                        download_url,
                        use_container_width=True
                    )
                with col_c:
                    if st.button(
                        "🟠 Edit",
                        key=f"edit_{row['id']}",
                        use_container_width=True
                    ):
                        st.session_state[edit_key] = True
                        st.session_state[konfirm_key] = False
                        st.rerun()
                with col_d:
                    if user["role"] == "admin":
                        if not st.session_state[konfirm_key]:
                            if st.button(
                                "🔴 Hapus",
                                key=f"del_{row['id']}",
                                use_container_width=True
                            ):
                                st.session_state[konfirm_key] = True
                                st.rerun()
                        else:
                            st.warning(f"Yakin hapus dokumen ini?")
                            col_ya, col_tidak = st.columns(2)
                            with col_ya:
                                if st.button(
                                    "✅ Ya",
                                    key=f"ya_{row['id']}",
                                    use_container_width=True
                                ):
                                    all_docs = get_all_documents()
                                    for idx, doc in enumerate(all_docs):
                                        if doc["id"] == row["id"]:
                                            delete_document(idx + 2)
                                            st.session_state[konfirm_key] = False
                                            st.success("Dokumen berhasil dihapus.")
                                            st.rerun()
                            with col_tidak:
                                if st.button(
                                    "❌ Tidak",
                                    key=f"tidak_{row['id']}",
                                    use_container_width=True
                                ):
                                    st.session_state[konfirm_key] = False
                                    st.rerun()