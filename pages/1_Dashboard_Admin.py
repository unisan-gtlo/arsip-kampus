import streamlit as st
from utils.auth import require_role
from utils.sheets import get_all_documents, delete_document, get_sheet, get_all_kategori
from utils.drive import get_drive_ids_from_link
import pandas as pd

st.set_page_config(page_title="Dashboard Admin", page_icon="📊", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

require_role(["admin", "operator"])

st.markdown("""
<style>
div[data-testid="column"]:nth-child(1) .stLinkButton a {
    background-color: #1976D2; color: white; border: none; border-radius: 8px;
}
div[data-testid="column"]:nth-child(2) .stLinkButton a {
    background-color: #2E7D32; color: white; border: none; border-radius: 8px;
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
        st.metric("Jumlah Kategori", df["kategori"].nunique())

    st.divider()

    # Filter, pencarian, dan sortir
    col_f1, col_f2, col_f3 = st.columns([2, 3, 2])
    with col_f1:
        kategori_filter = st.selectbox(
            "Filter Kategori",
            options=["Semua"] + sorted(df["kategori"].unique().tolist())
        )
    with col_f2:
        cari = st.text_input("Cari judul atau nomor dokumen...")
    with col_f3:
        sortir = st.selectbox(
            "Urutkan berdasarkan",
            options=["Terbaru", "Terlama", "Nomor Dokumen A-Z", "Nomor Dokumen Z-A"]
        )

    filtered = df.copy()
    if kategori_filter != "Semua":
        filtered = filtered[filtered["kategori"] == kategori_filter]
    if cari:
        mask = (
            filtered["judul"].str.contains(cari, case=False, na=False) |
            filtered["nomor_dokumen"].astype(str).str.contains(cari, case=False, na=False)
        )
        filtered = filtered[mask]

    # Sortir
    if sortir == "Terbaru":
        filtered = filtered.sort_values("tgl_upload", ascending=False)
    elif sortir == "Terlama":
        filtered = filtered.sort_values("tgl_upload", ascending=True)
    elif sortir == "Nomor Dokumen A-Z":
        filtered = filtered.sort_values("nomor_dokumen", ascending=True)
    elif sortir == "Nomor Dokumen Z-A":
        filtered = filtered.sort_values("nomor_dokumen", ascending=False)

    st.markdown(f"Menampilkan **{len(filtered)}** dokumen")
    st.divider()

    for i, row in filtered.iterrows():
        nomor_label = f"[{row['nomor_dokumen']}] " if str(row.get('nomor_dokumen', '')).strip() else ""
        with st.expander(f"📄 {nomor_label}{row['judul']} — {row['kategori']}"):

            edit_key = f"edit_mode_{row['id']}"
            konfirm_key = f"konfirm_{row['id']}"

            if edit_key not in st.session_state:
                st.session_state[edit_key] = False
            if konfirm_key not in st.session_state:
                st.session_state[konfirm_key] = False

            # MODE EDIT
            if st.session_state[edit_key]:
                st.markdown("### ✏️ Edit Dokumen")
                with st.form(key=f"form_edit_{row['id']}"):
                    nomor_baru = st.text_input(
                        "Nomor Dokumen",
                        value=str(row.get("nomor_dokumen", ""))
                    )
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
                        simpan = st.form_submit_button("💾 Simpan", use_container_width=True, type="primary")
                    with col_cancel:
                        batal = st.form_submit_button("✖ Batal", use_container_width=True)

                    if simpan:
                        if not judul_baru:
                            st.error("Judul tidak boleh kosong.")
                        else:
                            if link_baru.strip():
                                file_id_baru, link_view_baru = get_drive_ids_from_link(link_baru)
                                if not file_id_baru:
                                    st.error("Format link tidak valid.")
                                    st.stop()
                            else:
                                file_id_baru = row["file_id"]
                                link_view_baru = row["link_view"]

                            all_docs = get_all_documents()
                            for idx, doc in enumerate(all_docs):
                                if doc["id"] == row["id"]:
                                    sheet = get_sheet("dokumen")
                                    sheet.update(f"A{idx+2}:H{idx+2}", [[
                                        row["id"],
                                        nomor_baru.strip(),
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

            # MODE TAMPIL NORMAL
            else:
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.markdown(f"**Nomor:** {row.get('nomor_dokumen', '-') or '-'}")
                    st.markdown(f"**Kategori:** {row['kategori']}")
                with col_info2:
                    st.markdown(f"**Tanggal Upload:** {row['tgl_upload']}")
                    st.markdown(f"**Deskripsi:** {row['deskripsi']}")

                col_a, col_b, col_c, col_d = st.columns([2, 2, 1, 1])
                with col_a:
                    st.link_button("🔵 Buka PDF", row["link_view"], use_container_width=True)
                with col_b:
                    download_url = f"https://drive.google.com/uc?export=download&id={row['file_id']}"
                    st.link_button("🟢 Download", download_url, use_container_width=True)
                with col_c:
                    if st.button("🟠 Edit", key=f"edit_{row['id']}", use_container_width=True):
                        st.session_state[edit_key] = True
                        st.session_state[konfirm_key] = False
                        st.rerun()
                with col_d:
                    if user["role"] == "admin":
                        if not st.session_state[konfirm_key]:
                            if st.button("🔴 Hapus", key=f"del_{row['id']}", use_container_width=True):
                                st.session_state[konfirm_key] = True
                                st.rerun()
                        else:
                            st.warning("Yakin hapus?")
                            col_ya, col_tidak = st.columns(2)
                            with col_ya:
                                if st.button("✅ Ya", key=f"ya_{row['id']}", use_container_width=True):
                                    all_docs = get_all_documents()
                                    for idx, doc in enumerate(all_docs):
                                        if doc["id"] == row["id"]:
                                            delete_document(idx + 2)
                                            st.session_state[konfirm_key] = False
                                            st.success("Dokumen berhasil dihapus.")
                                            st.rerun()
                            with col_tidak:
                                if st.button("❌ Tidak", key=f"tidak_{row['id']}", use_container_width=True):
                                    st.session_state[konfirm_key] = False
                                    st.rerun()