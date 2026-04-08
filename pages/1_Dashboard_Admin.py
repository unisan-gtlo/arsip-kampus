import streamlit as st
from utils.auth import require_role
from utils.sheets import get_all_documents, delete_document, get_sheet, get_all_kategori
from utils.drive import get_drive_ids_from_link
from utils.sidebar import show_sidebar
import pandas as pd
import math

st.set_page_config(page_title="Dashboard Admin", page_icon="📊", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None
if "halaman" not in st.session_state:
    st.session_state.halaman = 1

require_role(["admin", "operator"])
show_sidebar()

st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none; }
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

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Dokumen", len(df))
    with col2:
        kategori_terbanyak = df["kategori"].value_counts().idxmax() if len(df) > 0 else "-"
        st.metric("Kategori Terbanyak", kategori_terbanyak)
    with col3:
        st.metric("Jumlah Kategori", df["kategori"].nunique())

    st.divider()

    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 3, 2, 1])
    with col_f1:
        kategori_filter = st.selectbox(
            "Filter Kategori",
            options=["Semua"] + sorted(df["kategori"].unique().tolist()),
            key="filter_kategori_dash"
        )
    with col_f2:
        cari = st.text_input("Cari judul atau nomor dokumen...", key="cari_dash")
    with col_f3:
        sortir = st.selectbox(
            "Urutkan",
            options=["Terbaru", "Terlama", "Nomor A-Z", "Nomor Z-A"],
            key="sortir_dash"
        )
    with col_f4:
        per_halaman = st.selectbox(
            "Per halaman",
            options=[5, 10, 25, 50],
            index=1,
            key="per_halaman_dash"
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

    if sortir == "Terbaru":
        filtered = filtered.sort_values("tgl_upload", ascending=False)
    elif sortir == "Terlama":
        filtered = filtered.sort_values("tgl_upload", ascending=True)
    elif sortir == "Nomor A-Z":
        filtered = filtered.sort_values("nomor_dokumen", ascending=True)
    elif sortir == "Nomor Z-A":
        filtered = filtered.sort_values("nomor_dokumen", ascending=False)

    filtered = filtered.reset_index(drop=True)

    total_data = len(filtered)
    total_halaman = max(1, math.ceil(total_data / per_halaman))

    if st.session_state.halaman > total_halaman:
        st.session_state.halaman = 1

    col_info, col_nav = st.columns([3, 2])
    with col_info:
        start_idx = (st.session_state.halaman - 1) * per_halaman + 1
        end_idx = min(st.session_state.halaman * per_halaman, total_data)
        st.markdown(
            f"Menampilkan **{start_idx}–{end_idx}** dari **{total_data}** dokumen | "
            f"Halaman **{st.session_state.halaman}/{total_halaman}**"
        )
    with col_nav:
        col_prev, col_page, col_next = st.columns([1, 3, 1])
        with col_prev:
            if st.button("◀", key="prev_dash", disabled=st.session_state.halaman <= 1, use_container_width=True):
                st.session_state.halaman -= 1
                st.rerun()
        with col_page:
            halaman_input = st.number_input(
                "Hal", min_value=1, max_value=total_halaman,
                value=st.session_state.halaman, step=1,
                label_visibility="collapsed", key="hal_input_dash"
            )
            if halaman_input != st.session_state.halaman:
                st.session_state.halaman = halaman_input
                st.rerun()
        with col_next:
            if st.button("▶", key="next_dash", disabled=st.session_state.halaman >= total_halaman, use_container_width=True):
                st.session_state.halaman += 1
                st.rerun()

    st.divider()

    start = (st.session_state.halaman - 1) * per_halaman
    end = start + per_halaman
    data_halaman = filtered.iloc[start:end]

    if data_halaman.empty:
        st.warning("Tidak ada dokumen yang sesuai pencarian.")
    else:
        for i, row in data_halaman.iterrows():
            nomor_label = f"[{row['nomor_dokumen']}] " if str(row.get('nomor_dokumen', '')).strip() else ""
            sifat_val = str(row.get('sifat', 'Umum')).strip()
            sifat_badge = "🔴 Rahasia" if sifat_val == "Rahasia" else "🟢 Umum"

            with st.expander(f"📄 {nomor_label}{row['judul']} — {row['kategori']} | {sifat_badge}"):

                edit_key = f"edit_mode_{row['id']}"
                konfirm_key = f"konfirm_{row['id']}"

                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False
                if konfirm_key not in st.session_state:
                    st.session_state[konfirm_key] = False

                if st.session_state[edit_key]:
                    st.markdown("### ✏️ Edit Dokumen")
                    with st.form(key=f"form_edit_{row['id']}"):
                        nomor_baru = st.text_input("Nomor Dokumen", value=str(row.get("nomor_dokumen", "")), key=f"nomor_{row['id']}")
                        judul_baru = st.text_input("Judul", value=row["judul"], key=f"judul_{row['id']}")
                        kategori_baru = st.selectbox(
                            "Kategori", KATEGORI,
                            index=KATEGORI.index(row["kategori"]) if row["kategori"] in KATEGORI else 0,
                            key=f"kat_{row['id']}"
                        )
                        deskripsi_baru = st.text_area("Deskripsi", value=row["deskripsi"], key=f"desk_{row['id']}")
                        sifat_options = ["Umum", "Rahasia"]
                        sifat_index = sifat_options.index(sifat_val) if sifat_val in sifat_options else 0
                        sifat_baru = st.radio(
                            "Sifat Dokumen", sifat_options,
                            index=sifat_index, horizontal=True,
                            key=f"sifat_{row['id']}"
                        )
                        link_baru = st.text_input(
                            "Link Google Drive (kosongkan jika tidak diganti)",
                            placeholder="https://drive.google.com/file/d/xxxx/view",
                            key=f"link_{row['id']}"
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
                                        sheet.update(f"A{idx+2}:I{idx+2}", [[
                                            row["id"],
                                            nomor_baru.strip(),
                                            judul_baru,
                                            kategori_baru,
                                            deskripsi_baru,
                                            file_id_baru,
                                            link_view_baru,
                                            row["tgl_upload"],
                                            sifat_baru
                                        ]])
                                        st.cache_data.clear()
                                        st.success("✅ Dokumen berhasil diperbarui!")
                                        st.session_state[edit_key] = False
                                        st.rerun()

                        if batal:
                            st.session_state[edit_key] = False
                            st.rerun()

                else:
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.markdown(f"**Nomor:** {row.get('nomor_dokumen', '-') or '-'}")
                        st.markdown(f"**Kategori:** {row['kategori']}")
                        st.markdown(f"**Sifat:** {sifat_badge}")
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
                                                st.cache_data.clear()
                                                st.session_state[konfirm_key] = False
                                                st.success("Dokumen berhasil dihapus.")
                                                st.rerun()
                                with col_tidak:
                                    if st.button("❌ Tidak", key=f"tidak_{row['id']}", use_container_width=True):
                                        st.session_state[konfirm_key] = False
                                        st.rerun()

    st.divider()
    col_prev2, col_info2, col_next2 = st.columns([1, 3, 1])
    with col_prev2:
        if st.button("◀ Sebelumnya", key="prev2_dash", disabled=st.session_state.halaman <= 1, use_container_width=True):
            st.session_state.halaman -= 1
            st.rerun()
    with col_info2:
        st.markdown(
            f"<div style='text-align:center; padding-top:8px'>"
            f"Halaman <b>{st.session_state.halaman}</b> dari <b>{total_halaman}</b>"
            f"</div>", unsafe_allow_html=True
        )
    with col_next2:
        if st.button("Berikutnya ▶", key="next2_dash", disabled=st.session_state.halaman >= total_halaman, use_container_width=True):
            st.session_state.halaman += 1
            st.rerun()