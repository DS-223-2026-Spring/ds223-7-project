"""Reusable sidebar navigation component."""
import streamlit as st

def render_sidebar():
    st.sidebar.title("💓 Pulse")
    st.sidebar.markdown("Free-to-Paid Conversion Platform")
    st.sidebar.divider()
    page = st.sidebar.radio(
        "Navigate",
        ["🏠 Home", "📊 Segment Overview", "📣 Campaign Editor"]
    )
    return page