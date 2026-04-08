import streamlit as st
from utils.auth import require_login
from utils.sheets import get_all_documents, get_all_kategori
import pandas as pd

st.set_page_config(page_title="Portal Dokumen", page_icon="🔍", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

require_login()

user = st.session_state.user
st.title("🔍 Portal Pencarian Dokumen")
st.markdown(f"Login sebagai: **{user['nama']}** | Role: `{user['role']}`")
st.divider()

docs = get_all_documents()

if not docs:
    st.info("Belum ada dokumen tersedia.")
else:
    df = pd.DataFrame(docs)
    kategori_list = get_all_kategori()

    col1, col2 = st.columns([3, 1])
    with col1:
        cari = st.text_input(
            "Cari dokumen...",
            placeholder="ketik judul atau deskripsi"
        )
    with col2:
        kategori_filter = st.selectbox(
            "Kategori",
            options=["Semua"] + kategori_list
        )

    filtered = df.copy()
    if kategori_filter != "Semua":
        filtered = filtered[filtered["kategori"] == kategori_filter]
    if cari:
        mask = (
            filtered["judul"].str.contains(cari, case=False, na=False) |
            filtered["deskripsi"].str.contains(cari, case=False, na=False)
        )
        filtered = filtered[mask]

    st.markdown(f"Ditemukan **{len(filtered)}** dokumen")
    st.divider()

    if filtered.empty:
        st.warning("Tidak ada dokumen yang sesuai pencarian.")
    else:
        for _, row in filtered.iterrows():
            with st.expander(f"📄 {row['judul']} — {row['kategori']}"):
                st.markdown(f"**Deskripsi:** {row['deskripsi']}")
                st.markdown(f"**Tanggal Upload:** {row['tgl_upload']}")
                st.markdown("**Preview PDF:**")
                st.components.v1.iframe(row["link_view"], height=500, scrolling=True)
                st.divider()
                col_a, col_b = st.columns(2)
                with col_a:
                    st.link_button(
                        "🔵 Buka di Tab Baru",
                        row["link_view"],
                        use_container_width=True
                    )
                with col_b:
                    download_url = f"https://drive.google.com/uc?export=download&id={row['file_id']}"
                    st.link_button(
                        "🟢 Download PDF",
                        download_url,
                        use_container_width=True
                    )