"""Reusable metrics row component."""
import streamlit as st

def render_metrics(total_users="—", converted_users="—", conversion_rate="—"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Users", value=total_users)
    with col2:
        st.metric(label="Converted Users", value=converted_users)
    with col3:
        st.metric(label="Conversion Rate", value=conversion_rate)