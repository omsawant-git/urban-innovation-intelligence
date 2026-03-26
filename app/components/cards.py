import streamlit as st

def kpi_card(col, label: str, value, delta=None, help_text: str = ""):
    col.metric(label=label, value=value, delta=delta, help=help_text)

def impact_badge(tier: str) -> str:
    colors = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
    return f"{colors.get(tier, '⚪')} {tier}"

def anomaly_badge(severity: str) -> str:
    colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
    return f"{colors.get(severity, '⚪')} {severity}"