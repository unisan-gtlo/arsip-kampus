import streamlit as st
from utils.sheets import get_all_documents, get_all_kategori
from utils.sidebar import show_public_sidebar
import pandas as pd
import math

st.set_page_config(
    page_title="Pencarian Dokumen - Unichsan",
    page_icon="🔍",
    layout="wide"
)

if "user" not in st.session_state:
    st.session_state.user = None

# CSS
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

show_public_sidebar()

# Header publik
st.markdown("""
<div style='text-align:center; padding: 1rem 0'>
    <h2 style='color:#1976D2; margin:0'>🔍 Portal Dokumen Publik</h2>
    <p style='color:gray; margin:4px 0'>Universitas Ichsan Gorontalo</p>
</div>
""", unsafe_allow_html=True)
st.divider()

if "halaman_publik" not in st.session_state:
    st.session_state.halaman_publik = 1

docs = get_all_documents()
kategori_list = get_all_kategori()

if not docs:
    st.info("Belum ada dokumen tersedia.")
else:
    df = pd.DataFrame(docs)

    # Filter hanya dokumen Umum
    if "sifat" in df.columns:
        df = df[df["sifat"].astype(str).str.strip().str.lower() != "rahasia"]

    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    with col1:
        cari = st.text_input("Cari dokumen...", placeholder="ketik judul, nomor, atau deskripsi")
    with col2:
        kategori_filter = st.selectbox("Kategori", ["Semua"] + kategori_list)
    with col3:
        sortir = st.selectbox("Urutkan", ["Terbaru", "Terlama", "Nomor A-Z", "Nomor Z-A"])
    with col4:
        per_halaman = st.selectbox("Per halaman", [5, 10, 25, 50], index=1)

    filtered = df.copy()
    if kategori_filter != "Semua":
        filtered = filtered[filtered["kategori"] == kategori_filter]
    if cari:
        mask = (
            filtered["judul"].str.contains(cari, case=False, na=False) |
            filtered["deskripsi"].str.contains(cari, case=False, na=False) |
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

    if st.session_state.halaman_publik > total_halaman:
        st.session_state.halaman_publik = 1

    col_info, col_nav = st.columns([3, 2])
    with col_info:
        if total_data == 0:
            st.warning("Tidak ada dokumen ditemukan.")
        else:
            start_idx = (st.session_state.halaman_publik - 1) * per_halaman + 1
            end_idx = min(st.session_state.halaman_publik * per_halaman, total_data)
            st.markdown(
                f"Ditemukan **{total_data}** dokumen | "
                f"Menampilkan **{start_idx}–{end_idx}** | "
                f"Halaman **{st.session_state.halaman_publik}/{total_halaman}**"
            )
    with col_nav:
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("◀", disabled=st.session_state.halaman_publik <= 1, use_container_width=True):
                st.session_state.halaman_publik -= 1
                st.rerun()
        with col_page:
            halaman_input = st.number_input(
                "Hal", min_value=1, max_value=total_halaman,
                value=st.session_state.halaman_publik, step=1,
                label_visibility="collapsed"
            )
            if halaman_input != st.session_state.halaman_publik:
                st.session_state.halaman_publik = halaman_input
                st.rerun()
        with col_next:
            if st.button("▶", disabled=st.session_state.halaman_publik >= total_halaman, use_container_width=True):
                st.session_state.halaman_publik += 1
                st.rerun()

    st.divider()

    start = (st.session_state.halaman_publik - 1) * per_halaman
    end = start + per_halaman
    data_halaman = filtered.iloc[start:end]

    if data_halaman.empty:
        st.warning("Tidak ada dokumen yang sesuai.")
    else:
        for _, row in data_halaman.iterrows():
            nomor_label = f"[{row['nomor_dokumen']}] " if str(row.get('nomor_dokumen', '')).strip() else ""
            with st.expander(f"📄 {nomor_label}{row['judul']} — {row['kategori']}"):
                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    st.markdown(f"**Nomor:** {row.get('nomor_dokumen', '-') or '-'}")
                    st.markdown(f"**Kategori:** {row['kategori']}")
                with col_i2:
                    st.markdown(f"**Tanggal:** {row['tgl_upload']}")
                    st.markdown(f"**Deskripsi:** {row['deskripsi']}")
                st.markdown("**Preview PDF:**")
                st.components.v1.iframe(row["link_view"], height=500, scrolling=True)
                st.divider()
                col_a, col_b = st.columns(2)
                with col_a:
                    st.link_button("🔵 Buka di Tab Baru", row["link_view"], use_container_width=True)
                with col_b:
                    download_url = f"https://drive.google.com/uc?export=download&id={row['file_id']}"
                    st.link_button("🟢 Download PDF", download_url, use_container_width=True)

    st.divider()
    col_prev2, col_info2, col_next2 = st.columns([1, 3, 1])
    with col_prev2:
        if st.button("◀ Sebelumnya", disabled=st.session_state.halaman_publik <= 1, use_container_width=True):
            st.session_state.halaman_publik -= 1
            st.rerun()
    with col_info2:
        st.markdown(
            f"<div style='text-align:center; padding-top:8px'>"
            f"Halaman <b>{st.session_state.halaman_publik}</b> dari <b>{total_halaman}</b>"
            f"</div>", unsafe_allow_html=True
        )
    with col_next2:
        if st.button("Berikutnya ▶", disabled=st.session_state.halaman_publik >= total_halaman, use_container_width=True):
            st.session_state.halaman_publik += 1
            st.rerun()

# Tombol login di bawah
st.divider()
st.markdown("""
<div style='text-align:center; color:gray; font-size:13px'>
    Dokumen rahasia hanya dapat diakses oleh pengguna yang login.
</div>
""", unsafe_allow_html=True)
col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
with col_l2:
    st.page_link("app.py", label="🔐 Login ->akses penuh", use_container_width=True)