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

    # Metrics placeholders
    render_metrics()
    st.divider()

    # Filter placeholder
    st.subheader("🔍 Filters")
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Time Period", ["Last 7 days", "Last 30 days", "Last 90 days"], disabled=True)
    with col2:
        st.selectbox("Segment", ["All Segments"], disabled=True)
    st.caption("Filters will be enabled once data is connected.")
    st.divider()

    # Chart placeholders
    st.subheader("📈 Conversion Trend")
    st.info("Chart will appear here once data is connected.")

    st.subheader("🗂️ Recent Campaigns")
    st.info("Campaign list will appear here once data is connected.")

    # Model output placeholder
    st.divider()
    st.subheader("🤖 Model Predictions")
    st.info("Model output will appear here once the DS model is connected.")

# Segment Overview page
elif page == "📊 Segment Overview":
    st.title("Segment Overview")
    st.divider()

    # Filter placeholders
    st.subheader("🔍 Filters")
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Segment Type", ["All"], disabled=True)
    with col2:
        st.selectbox("Status", ["All"], disabled=True)
    st.caption("Filters will be enabled once data is connected.")
    st.divider()

    # Table placeholder
    st.subheader("📋 Segment Table")
    st.info("Segment data will appear here once API is connected.")

    # Chart placeholder
    st.subheader("📊 Segment Distribution")
    st.info("Chart will appear here once data is connected.")

    # Model output placeholder
    st.divider()
    st.subheader("🤖 Segment Model Output")
    st.info("Predicted segment scores will appear here once model is connected.")

# Campaign Editor page
elif page == "📣 Campaign Editor":
    st.title("Campaign Editor")
    st.divider()

    # Filter placeholders
    st.subheader("🔍 Filters")
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Filter by Segment", ["All"], disabled=True)
    with col2:
        st.selectbox("Filter by Status", ["All"], disabled=True)
    st.caption("Filters will be enabled once data is connected.")
    st.divider()

    # Existing campaigns placeholder
    st.subheader("📋 Existing Campaigns")
    st.info("Campaign data will appear here once API is connected.")

    # Model output placeholder
    st.subheader("🤖 Campaign Performance Predictions")
    st.info("Model predictions for campaign performance will appear here.")
    st.divider()

    # Form placeholder
    st.subheader("➕ Create New Campaign")
    render_campaign_form()