"""Reusable campaign creation form component."""
import streamlit as st

def render_campaign_form(segments=None):
    if segments is None:
        segments = ["—"]
    with st.form("new_campaign"):
        st.text_input("Campaign Name")
        st.selectbox("Target Segment", segments)
        st.text_area("Message")
        submitted = st.form_submit_button("Create Campaign")
    return submitted