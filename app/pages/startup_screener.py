import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_session
from database.models import Startup

ACCENT        = "#F5A623"
COLORS        = {"High": "#3B7D4F", "Medium": "#F5A623", "Low": "#D4526E"}
CHART_COLORS  = ["#F5A623", "#E8845A", "#D4526E", "#A23B72", "#6B4C9A",
                 "#3B7D4F", "#2E86AB", "#D4A017", "#1A6B5A", "#E76F51"]
COUNTRY_NAMES = {
    "US": "United States (US)", "GB": "United Kingdom (GB)",
    "ES": "Spain (ES)",         "NL": "Netherlands (NL)",
    "SG": "Singapore (SG)",     "JP": "Japan (JP)",
    "AU": "Australia (AU)",     "CA": "Canada (CA)",
    "AE": "United Arab Emirates (AE)", "BR": "Brazil (BR)",
    "KE": "Kenya (KE)",         "IN": "India (IN)",
}

CHART_LAYOUT = dict(
    paper_bgcolor="#1C1C1C",
    plot_bgcolor="#161616",
    font=dict(color="#888888", family="Inter, sans-serif", size=12),
    xaxis=dict(gridcolor="#2A2A2A", linecolor="#2A2A2A", tickcolor="#555555"),
    yaxis=dict(gridcolor="#2A2A2A", linecolor="#2A2A2A", tickcolor="#555555"),
    margin=dict(t=50, b=40, l=20, r=20),
)

@st.cache_data(ttl=3600)
def load_startups():
    session = get_session()
    rows = session.query(Startup).all()
    session.close()
    df = pd.DataFrame([{
        "id": r.id, "name": r.name, "sector": r.sector,
        "city": r.city, "country": r.country,
        "founding_year": r.founding_year, "team_size": r.team_size,
        "funding_usd": r.funding_usd, "num_pilots": r.num_pilots,
        "cities_deployed": r.cities_deployed,
        "has_government_partner": r.has_government_partner,
        "revenue_stage": r.revenue_stage,
        "sustainability_score": r.sustainability_score,
        "impact_tier": r.impact_tier,
    } for r in rows])
    df["sector"]               = df["sector"].fillna("Unknown")
    df["revenue_stage"]        = df["revenue_stage"].fillna("Unknown")
    df["country"]              = df["country"].fillna("Unknown")
    df["impact_tier"]          = df["impact_tier"].fillna("Low")
    df["sustainability_score"] = df["sustainability_score"].fillna(0)
    return df

def section_header(text):
    st.markdown(f"""
    <div style="font-size:0.68rem;font-weight:700;color:#555555;
                text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.8rem;">
        {text}
    </div>
    """, unsafe_allow_html=True)

def show():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div style="font-size:0.68rem;font-weight:700;color:#555555;
                    text-transform:uppercase;letter-spacing:0.12em;">AI Screening</div>
        <div style="font-size:1.8rem;font-weight:800;color:#F0F0F0;
                    letter-spacing:-0.02em;">Startup Impact Screener</div>
        <div style="font-size:0.85rem;color:#666666;margin-top:0.3rem;">
            XGBoost-powered scoring of urban innovation startups with SHAP explainability.
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = load_startups()
    if df.empty:
        st.error("No startup data found.")
        return

    st.markdown("""
    <div style="background:#1C1C1C;border:1px solid #333333;border-radius:10px;
                padding:1.2rem 1.5rem;margin-bottom:1rem;">
        <div style="font-size:0.68rem;font-weight:700;color:#F5A623;
                    text-transform:uppercase;letter-spacing:0.12em;margin-bottom:1rem;">
            Filters
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    all_sectors        = sorted(df["sector"].unique().tolist())
    sel_sectors        = col1.multiselect("Sector", all_sectors, default=all_sectors)
    sel_tiers          = col2.multiselect("Impact Tier", ["High","Medium","Low"], default=["High","Medium","Low"])
    all_stages         = sorted(df["revenue_stage"].unique().tolist())
    sel_stages         = col3.multiselect("Revenue Stage", all_stages, default=all_stages)
    all_countries      = sorted(df["country"].unique().tolist())
    country_options    = [COUNTRY_NAMES.get(c, c) for c in all_countries]
    reverse_map        = {v: k for k, v in COUNTRY_NAMES.items()}
    sel_country_labels = col4.multiselect("Country", country_options, default=country_options)
    sel_countries      = [reverse_map.get(c, c) for c in sel_country_labels]
    min_score          = st.slider("Minimum Sustainability Score", 0, 100, 0)
    st.markdown("</div>", unsafe_allow_html=True)

    filtered = df.copy()
    if sel_sectors:    filtered = filtered[filtered["sector"].isin(sel_sectors)]
    if sel_tiers:      filtered = filtered[filtered["impact_tier"].isin(sel_tiers)]
    if sel_stages:     filtered = filtered[filtered["revenue_stage"].isin(sel_stages)]
    if sel_countries:  filtered = filtered[filtered["country"].isin(sel_countries)]
    filtered = filtered[filtered["sustainability_score"] >= min_score]

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Startups", len(filtered))
    c2.metric("High Impact",    len(filtered[filtered["impact_tier"]=="High"]))
    c3.metric("Medium Impact",  len(filtered[filtered["impact_tier"]=="Medium"]))
    c4.metric("Low Impact",     len(filtered[filtered["impact_tier"]=="Low"]))

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        section_header("Impact Tier Distribution")
        tier_counts = filtered["impact_tier"].value_counts().reset_index()
        tier_counts.columns = ["tier", "count"]
        fig = px.pie(
            tier_counts, names="tier", values="count",
            color="tier", color_discrete_map=COLORS, hole=0.5
        )
        fig.update_layout(**CHART_LAYOUT, height=320)
        fig.update_layout(legend=dict(bgcolor="#1C1C1C", bordercolor="#2A2A2A",
                                      orientation="h", yanchor="bottom", y=-0.2))
        fig.update_traces(
            textinfo="percent+label",
            textfont=dict(color="#E8E8E8", size=12),
            marker=dict(line=dict(color="#111111", width=2))
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Average Score by Sector")
        sector_avg = filtered.groupby("sector")["sustainability_score"].mean().reset_index()
        sector_avg = sector_avg.sort_values("sustainability_score")
        fig2 = px.bar(
            sector_avg, x="sustainability_score", y="sector",
            orientation="h", color="sector",
            color_discrete_sequence=CHART_COLORS
        )
        fig2.update_layout(**CHART_LAYOUT, height=320, showlegend=False,
                           xaxis_title="Average Score", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("Startups by Revenue Stage")
        stage_counts = filtered["revenue_stage"].value_counts().reset_index()
        stage_counts.columns = ["stage", "count"]
        fig3 = px.bar(
            stage_counts, x="stage", y="count",
            color="stage", color_discrete_sequence=CHART_COLORS
        )
        fig3.update_layout(**CHART_LAYOUT, height=300, showlegend=False,
                           xaxis_title="Revenue Stage", yaxis_title="Count")
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        section_header("Startups by Country")
        fd = filtered.copy()
        fd["country_name"] = fd["country"].map(lambda x: COUNTRY_NAMES.get(x, x))
        country_counts = fd["country_name"].value_counts().reset_index()
        country_counts.columns = ["country", "count"]
        fig4 = px.bar(
            country_counts, x="country", y="count",
            color="country", color_discrete_sequence=CHART_COLORS
        )
        fig4.update_layout(**CHART_LAYOUT, height=300, showlegend=False,
                           xaxis_title="Country", yaxis_title="Count",
                           xaxis_tickangle=-30)
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    section_header("Funding vs Sustainability Score")
    fig5 = px.scatter(
        filtered, x="funding_usd", y="sustainability_score",
        color="impact_tier", hover_name="name",
        size="team_size", log_x=True,
        color_discrete_map=COLORS,
        labels={
            "funding_usd":          "Funding (USD, log scale)",
            "sustainability_score": "Sustainability Score",
            "impact_tier":          "Impact Tier"
        }
    )
    fig5.update_layout(**CHART_LAYOUT, height=420)
    fig5.update_layout(legend=dict(bgcolor="#1C1C1C", bordercolor="#2A2A2A",
                                   orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig5, use_container_width=True)

    st.divider()
    section_header("Ranked Startups")
    top = filtered.sort_values("sustainability_score", ascending=False).copy()
    top["country"] = top["country"].map(lambda x: COUNTRY_NAMES.get(x, x))
    st.dataframe(
        top[["name","sector","city","country","impact_tier",
             "sustainability_score","funding_usd","num_pilots","revenue_stage"]].round(2),
        use_container_width=True, height=420
    )
    st.download_button("Download Screened Startups",
                       filtered.to_csv(index=False), "screened_startups.csv")