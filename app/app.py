"""Pulse Dashboard — Streamlit frontend."""
import streamlit as st

st.set_page_config(
    page_title="Pulse Dashboard",
    page_icon="💓",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("💓 Pulse")
st.sidebar.markdown("Free-to-Paid Conversion Platform")
st.sidebar.divider()
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📊 Segment Overview", "📣 Campaign Editor"]
)

# Home page
if page == "🏠 Home":
    st.title("Welcome to Pulse Dashboard")
    st.markdown("### Free-to-Paid Conversion Platform")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Users", value="—")
    with col2:
        st.metric(label="Converted Users", value="—")
    with col3:
        st.metric(label="Conversion Rate", value="—")

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
    with st.form("new_campaign"):
        st.text_input("Campaign Name")
        st.selectbox("Target Segment", ["—"])
        st.text_area("Message")
        st.form_submit_button("Create Campaign")