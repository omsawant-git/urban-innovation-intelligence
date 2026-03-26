import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Urban Innovation Intelligence",
    page_icon="🌆",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }

/* ── Base ── */
.main { background-color: #111111 !important; }
.block-container { padding: 2rem 2.5rem !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #161616 !important;
    border-right: 1px solid #2A2A2A !important;
}
div[data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebar"] * { visibility: visible !important; }

/* ── Navigation blocks ── */
div[role="radiogroup"] { gap: 0 !important; }
div[role="radiogroup"] > label {
    display: flex !important;
    align-items: center !important;
    background: #1C1C1C !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 8px !important;
    padding: 0.65rem 1rem !important;
    margin-bottom: 0.4rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
div[role="radiogroup"] > label:hover {
    background: #242424 !important;
    border-color: #F5A623 !important;
}
div[role="radiogroup"] > label:has(input:checked) {
    background: #2A1F00 !important;
    border-color: #F5A623 !important;
    border-left: 3px solid #F5A623 !important;
}
div[role="radiogroup"] > label > div:first-child { display: none !important; }
div[role="radiogroup"] > label p {
    color: #888888 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    margin: 0 !important;
}
div[role="radiogroup"] > label:hover p { color: #E8E8E8 !important; }
div[role="radiogroup"] > label:has(input:checked) p {
    color: #F5A623 !important;
    font-weight: 600 !important;
}

/* ── Headings ── */
h1 {
    color: #F0F0F0 !important;
    font-weight: 800 !important;
    font-size: 1.9rem !important;
    letter-spacing: -0.02em !important;
}
h2 { color: #CCCCCC !important; font-weight: 600 !important; }
h3 { color: #F5A623 !important; font-weight: 600 !important; }
p  { color: #888888 !important; }
li { color: #666666 !important; }

/* ── Metrics ── */
div[data-testid="metric-container"] {
    background: #1C1C1C !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 10px !important;
    padding: 1.2rem 1rem !important;
    transition: all 0.2s ease !important;
}
div[data-testid="metric-container"]:hover {
    border-color: #F5A623 !important;
    box-shadow: 0 0 16px rgba(245,166,35,0.1) !important;
}
div[data-testid="metric-container"] label {
    color: #555555 !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
div[data-testid="stMetricValue"] > div {
    color: #F0F0F0 !important;
    font-weight: 700 !important;
    font-size: 1.7rem !important;
}
div[data-testid="stMetricDelta"] {
    color: #F5A623 !important;
    font-size: 0.72rem !important;
}

/* ── Select / Multiselect ── */
div[data-baseweb="select"] > div {
    background: #1C1C1C !important;
    border: 1px solid #333333 !important;
    border-radius: 8px !important;
    color: #E8E8E8 !important;
}
div[data-baseweb="select"] > div:hover,
div[data-baseweb="select"] > div:focus-within {
    border-color: #F5A623 !important;
    box-shadow: 0 0 0 2px rgba(245,166,35,0.15) !important;
}
div[data-baseweb="select"] input { color: #E8E8E8 !important; }
div[data-baseweb="tag"] {
    background: #2A1F00 !important;
    border: 1px solid #F5A623 !important;
    border-radius: 5px !important;
}
div[data-baseweb="tag"] span {
    color: #F5A623 !important;
    font-size: 0.75rem !important;
}
ul[data-baseweb="menu"] {
    background: #1C1C1C !important;
    border: 1px solid #2A2A2A !important;
}
li[role="option"] {
    background: #1C1C1C !important;
    color: #888888 !important;
}
li[role="option"]:hover {
    background: #242424 !important;
    color: #E8E8E8 !important;
}

/* ── Expander ── */
div[data-testid="stExpander"] {
    background: #1C1C1C !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 10px !important;
}
details summary {
    color: #888888 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
details summary:hover { color: #E8E8E8 !important; }

/* ── Tabs ── */
button[data-baseweb="tab"] {
    color: #555555 !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}
button[data-baseweb="tab"]:hover { color: #AAAAAA !important; }
button[data-baseweb="tab"][aria-selected="true"] {
    color: #F5A623 !important;
    border-bottom: 2px solid #F5A623 !important;
}

/* ── Divider ── */
hr { border-color: #2A2A2A !important; margin: 1.2rem 0 !important; }

/* ── Buttons ── */
div[data-testid="stDownloadButton"] button {
    background: #2A1F00 !important;
    border: 1px solid #F5A623 !important;
    color: #F5A623 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stDownloadButton"] button:hover {
    background: #F5A623 !important;
    color: #111111 !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border: 1px solid #2A2A2A !important;
    border-radius: 10px !important;
}

/* ── Alerts ── */
div[data-testid="stAlert"] {
    background: #1C1C1C !important;
    border-radius: 8px !important;
    color: #888888 !important;
}

/* ── Slider ── */
div[data-testid="stSlider"] { padding: 0.5rem 0 !important; }

/* ── Caption ── */
div[data-testid="stCaptionContainer"] p {
    color: #555555 !important;
    font-size: 0.75rem !important;
}

/* ── Copyright ── */
.copyright {
    background: #1C1C1C;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    padding: 0.6rem;
    font-size: 0.65rem;
    color: #444444;
    text-align: center;
    line-height: 1.6;
    margin-top: 1rem;
}
.copyright span { color: #F5A623; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.5rem 0;">
        <div style="font-size:1rem;font-weight:800;color:#F0F0F0;letter-spacing:0.05em;">
            URBAN INNOVATION
        </div>
        <div style="font-size:0.68rem;color:#F5A623;font-weight:600;
                    text-transform:uppercase;letter-spacing:0.12em;margin-top:2px;">
            Intelligence Platform
        </div>
        <div style="font-size:0.63rem;color:#444444;margin-top:4px;">
            Powered by Leading Cities
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.65rem;font-weight:700;color:#444444;
                text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;">
        Navigation
    </div>
    """, unsafe_allow_html=True)

    PAGES = {
        "Home":               "home",
        "City Map & KPIs":    "city_map",
        "Startup Screener":   "startup_screener",
        "City-Startup Match": "match_engine",
        "Forecasting":        "forecasting",
        "Model Performance":  "model_performance",
    }

    selection = st.radio("nav", list(PAGES.keys()), label_visibility="collapsed")
    page      = PAGES[selection]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.63rem;color:#444444;line-height:2.2;">
        <div style="color:#555555;font-weight:700;font-size:0.63rem;
                    text-transform:uppercase;letter-spacing:0.1em;">
            Data Sources
        </div>
        Open-Meteo API · World Bank · AcceliCITY
        <div style="color:#555555;font-weight:700;font-size:0.63rem;
                    text-transform:uppercase;letter-spacing:0.1em;margin-top:0.6rem;">
            ML Stack
        </div>
        XGBoost · K-Means · LightGBM · Isolation Forest
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="copyright">
        <span>© 2026 Om Sawant</span> · All Rights Reserved<br>
        Patent Pending — Urban Innovation Intelligence
    </div>
    """, unsafe_allow_html=True)

# ── Accent color for all pages ─────────────────────────
ACCENT      = "#F5A623"
BG_CARD     = "#1C1C1C"
BG_PAGE     = "#111111"
BORDER      = "#2A2A2A"
TEXT_PRIMARY= "#F0F0F0"
TEXT_MUTED  = "#888888"
TEXT_DIM    = "#555555"

# ── Pages ──────────────────────────────────────────────
if page == "home":

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1C1400 0%,#1C1C1C 60%,#1A1A1A 100%);
                border:1px solid #2A2A2A;border-radius:16px;padding:2.5rem;
                margin-bottom:2rem;overflow:hidden;position:relative;">
        <div style="position:absolute;top:-80px;right:-80px;width:350px;height:350px;
                    background:radial-gradient(circle,rgba(245,166,35,0.07) 0%,transparent 70%);
                    border-radius:50%;pointer-events:none;"></div>
        <div style="font-size:0.68rem;font-weight:700;color:{ACCENT};
                    text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">
            AI-POWERED &nbsp;·&nbsp; LEADING CITIES &nbsp;·&nbsp; ACCELICITY PROGRAM
        </div>
        <div style="font-size:2rem;font-weight:800;color:{TEXT_PRIMARY};
                    letter-spacing:-0.03em;line-height:1.2;margin-bottom:0.8rem;">
            Urban Innovation<br>Intelligence Platform
        </div>
        <div style="font-size:0.9rem;color:#666666;max-width:580px;line-height:1.7;">
            Identify, score, and match urban sustainability startups to the cities
            that need them most — powered by 4 production ML models and real-world data.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Cities Tracked",   "15",     "Global Network")
    c2.metric("Startups Scored",  "500",    "AI-Evaluated")
    c3.metric("Climate Records",  "16,440", "Open-Meteo")
    c4.metric("ML Models",        "4",      "Production")
    c5.metric("Indicators",       "6",      "Per City")

    st.divider()

    st.markdown(f"""
    <div style="font-size:0.68rem;font-weight:700;color:{TEXT_DIM};
                text-transform:uppercase;letter-spacing:0.12em;margin-bottom:1rem;">
        Platform Capabilities
    </div>
    """, unsafe_allow_html=True)

    cols  = st.columns(4)
    cards = [
        ("Startup Screening", [
            "XGBoost impact classification",
            "SHAP explainability layer",
            "ROC-AUC: 1.0 · F1: 0.99",
            "500 startups evaluated"
        ]),
        ("City Profiling", [
            "K-Means sustainability clusters",
            "5 city archetypes identified",
            "Real Open-Meteo climate data",
            "15 global cities profiled"
        ]),
        ("Forecasting", [
            "LightGBM multi-year forecasts",
            "Lag feature engineering",
            "TimeSeriesSplit CV",
            "95% confidence intervals"
        ]),
        ("Anomaly Detection", [
            "Isolation Forest detection",
            "High / Medium / Low severity",
            "Early warning system",
            "Per-city anomaly scoring"
        ]),
    ]

    for col, (title, items) in zip(cols, cards):
        items_html = "".join([
            f'<div style="font-size:0.78rem;color:#666666;padding:3px 0;line-height:1.5;">'
            f'<span style="color:{ACCENT};margin-right:6px;">›</span>{item}</div>'
            for item in items
        ])
        col.markdown(f"""
        <div style="background:{BG_CARD};border:1px solid {BORDER};
                    border-radius:12px;padding:1.3rem;height:100%;">
            <div style="font-size:0.9rem;font-weight:700;color:{TEXT_PRIMARY};
                        margin-bottom:0.8rem;padding-bottom:0.6rem;
                        border-bottom:1px solid {BORDER};">{title}</div>
            {items_html}
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown(f"""
    <div style="font-size:0.68rem;font-weight:700;color:{TEXT_DIM};
                text-transform:uppercase;letter-spacing:0.12em;margin-bottom:1rem;">
        How It Works
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("01", "Data Ingestion",      "Climate + World Bank indicators via API"),
        ("02", "Feature Engineering", "Lag features, rolling stats, scoring"),
        ("03", "ML Modeling",         "4 models trained with cross-validation"),
        ("04", "City Matching",       "Clusters cities, matches startup sectors"),
        ("05", "Insights Delivered",  "Rankings, forecasts, anomaly alerts"),
    ]

    step_cols = st.columns(5)
    for col, (num, title, desc) in zip(step_cols, steps):
        col.markdown(f"""
        <div style="text-align:center;background:{BG_CARD};border:1px solid {BORDER};
                    border-radius:12px;padding:1.2rem 0.8rem;">
            <div style="font-size:1.4rem;font-weight:800;color:{ACCENT};
                        margin-bottom:0.5rem;">{num}</div>
            <div style="font-size:0.8rem;font-weight:700;color:{TEXT_PRIMARY};
                        margin-bottom:0.4rem;">{title}</div>
            <div style="font-size:0.72rem;color:#555555;line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown(f"""
    <div style="text-align:center;background:{BG_CARD};border:1px solid {BORDER};
                border-radius:12px;padding:1.5rem;">
        <div style="font-size:0.78rem;color:#555555;line-height:2.2;">
            Built for
            <span style="color:{ACCENT};font-weight:600;">Leading Cities' AcceliCITY Program</span>
            &nbsp;·&nbsp;
            Data from
            <span style="color:{ACCENT};font-weight:600;">Open-Meteo & World Bank</span>
            &nbsp;·&nbsp;
            <span style="color:{ACCENT};font-weight:600;">4 Production ML Models</span>
        </div>
        <div style="font-size:0.65rem;color:#333333;margin-top:0.4rem;">
            © 2026 Om Sawant · Patent Pending · Urban Innovation Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "city_map":
    from app.pages.city_map import show
    show()
elif page == "startup_screener":
    from app.pages.startup_screener import show
    show()
elif page == "match_engine":
    from app.pages.match_engine import show
    show()
elif page == "forecasting":
    from app.pages.forecasting import show
    show()
elif page == "model_performance":
    from app.pages.model_performance import show
    show()