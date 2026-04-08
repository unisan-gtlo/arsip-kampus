import streamlit as st
from utils.auth import logout
import os
import base64

def show_sidebar():
    with st.sidebar:
        if os.path.exists("logo.png"):
            with open("logo.png", "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
            <div style='text-align:center; margin-bottom:0.5rem'>
                <img src='data:image/png;base64,{logo_base64}'
                     width='90'
                     style='border-radius:50%; border: 3px solid #1976D2'>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align:center'>
            <p style='font-weight:600; font-size:15px; margin:4px 0'>Sistem Arsip Dokumen</p>
            <p style='font-size:12px; color:gray; margin:0'>Universitas Ichsan Gorontalo</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        if "user" in st.session_state and st.session_state.user:
            user = st.session_state.user
            role_label = {
                "admin": "🔴 Administrator",
                "operator": "🟠 Operator",
                "user": "🟢 User"
            }.get(user['role'], user['role'])

            st.markdown(f"""
            <div style='text-align:center'>
                <p style='font-size:14px; font-weight:600; margin:4px 0'>👤 {user['nama']}</p>
                <p style='font-size:12px; color:gray; margin:0'>{role_label}</p>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()