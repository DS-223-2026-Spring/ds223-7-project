"""Segment Overview page."""
import streamlit as st
import requests, os

API = os.getenv("API_URL", "http://localhost:8008")

st.title("Segment Overview")
try:
    data = requests.get(f"{API}/api/segments", timeout=5).json()
    st.dataframe(data)
except Exception as e:
    st.warning(f"Could not reach API: {e}")
