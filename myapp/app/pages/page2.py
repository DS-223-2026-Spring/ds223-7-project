"""Campaign Editor page."""
import streamlit as st
import requests, os

API = os.getenv("API_URL", "http://localhost:8008")

st.title("Campaign Editor")
try:
    data = requests.get(f"{API}/api/campaigns", timeout=5).json()
    for c in data:
        st.subheader(c.get("segment_name", ""))
        st.json(c)
except Exception as e:
    st.warning(f"Could not reach API: {e}")
