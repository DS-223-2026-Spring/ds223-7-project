"""Pulse Dashboard — Streamlit frontend."""
import streamlit as st
from components.sidebar import render_sidebar
from components.metrics import render_metrics
from components.campaign_form import render_campaign_form

st.set_page_config(
    page_title="Pulse Dashboard",
    page_icon="💓",
    layout="wide"
)

page = render_sidebar()

# Home page
if page == "🏠 Home":
    st.title("Welcome to Pulse Dashboard")
    st.markdown("### Free-to-Paid Conversion Platform")
    st.divider()
    render_metrics()
    st.divider()
    st.subheader("📈 Conversion Trend")
    st.info("Chart will appear here once data is connected.")
    st.subheader("🗂️ Recent Campaigns")
    st.info("Campaign list will appear here once data is connected.")

# Segment Overview page
elif page == "📊 Segment Overview":
    st.title("Segment Overview")
    st.divider()
    st.subheader("📋 Segment Table")
    st.info("Segment data will appear here once API is connected.")
    st.subheader("📊 Segment Distribution")
    st.info("Chart will appear here once data is connected.")

# Campaign Editor page
elif page == "📣 Campaign Editor":
    st.title("Campaign Editor")
    st.divider()
    st.subheader("📋 Existing Campaigns")
    st.info("Campaign data will appear here once API is connected.")
    st.subheader("➕ Create New Campaign")
    render_campaign_form()