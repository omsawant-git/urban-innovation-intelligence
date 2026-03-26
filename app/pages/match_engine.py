import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pickle, sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_session
from database.models import City, CityIndicator, Startup

ACCENT        = "#F5A623"
CHART_COLORS  = ["#F5A623", "#E8845A", "#D4526E", "#A23B72", "#6B4C9A"]
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

DEFAULT_LEGEND = dict(bgcolor="#1C1C1C", bordercolor="#2A2A2A", borderwidth=1)

@st.cache_data(ttl=3600)
def load_data():
    session = get_session()
    city_rows = session.query(
        City.name.label("city"), City.country,
        CityIndicator.co2_emissions, CityIndicator.renewable_energy,
        CityIndicator.urban_population, CityIndicator.gdp_per_capita,
        CityIndicator.pm25_exposure, CityIndicator.access_electricity,
    ).join(City, City.id == CityIndicator.city_id).all()
    startup_rows = session.query(Startup).all()
    session.close()
    cities_df   = pd.DataFrame(city_rows).groupby(["city","country"]).mean().reset_index()
    startups_df = pd.DataFrame([{
        "name": r.name, "sector": r.sector,
        "sustainability_score": r.sustainability_score,
        "impact_tier": r.impact_tier,
        "num_pilots": r.num_pilots,
        "funding_usd": r.funding_usd,
        "revenue_stage": r.revenue_stage,
    } for r in startup_rows])
    return cities_df, startups_df

@st.cache_data(ttl=3600)
def load_clusters():
    with open("artifacts/kmeans.pkl", "rb") as f:
        return pickle.load(f)

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
                    text-transform:uppercase;letter-spacing:0.12em;">ML Matching</div>
        <div style="font-size:1.8rem;font-weight:800;color:#F0F0F0;
                    letter-spacing:-0.02em;">City-Startup Match Engine</div>
        <div style="font-size:0.85rem;color:#666666;margin-top:0.3rem;">
            K-Means cluster profiles matched to startup sectors based on city sustainability gaps.
        </div>
    </div>
    """, unsafe_allow_html=True)

    cities_df, startups_df = load_data()
    cluster_data = load_clusters()
    model  = cluster_data["model"]
    scaler = cluster_data["scaler"]

    CLUSTER_LABELS = {
        0: "Climate Leaders",    1: "Emerging Sustainers",
        2: "Energy Dependent",   3: "High Growth Cities",
        4: "Developing Hubs"
    }
    CLUSTER_NEEDS = {
        "Climate Leaders":     ["Clean Energy", "Smart Infrastructure", "Circular Economy"],
        "Emerging Sustainers": ["Climate Tech", "Air Quality", "Green Building"],
        "Energy Dependent":    ["Clean Energy", "Smart Mobility", "Water Technology"],
        "High Growth Cities":  ["Smart Infrastructure", "Waste Management", "Urban Agriculture"],
        "Developing Hubs":     ["Water Technology", "Air Quality", "Smart Mobility"],
    }

    features   = ["co2_emissions","renewable_energy","urban_population",
                  "gdp_per_capita","pm25_exposure","access_electricity"]
    city_clean = cities_df.dropna(subset=features).copy()
    X          = scaler.transform(city_clean[features])
    city_clean["cluster_id"]    = model.predict(X)
    city_clean["cluster_label"] = city_clean["cluster_id"].map(CLUSTER_LABELS)

    # ── Filters ───────────────────────────────────────
    st.markdown("""
    <div style="background:#1C1C1C;border:1px solid #333333;border-radius:10px;
                padding:1.2rem 1.5rem;margin-bottom:1rem;">
        <div style="font-size:0.68rem;font-weight:700;color:#F5A623;
                    text-transform:uppercase;letter-spacing:0.12em;margin-bottom:1rem;">
            Filters
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    sel_cities = col1.multiselect(
        "Select Cities", sorted(city_clean["city"].unique()),
        default=["Amsterdam", "Nairobi", "Boston"]
    )
    sel_tier = col2.multiselect(
        "Startup Impact Tier", ["High","Medium","Low"], default=["High"]
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if not sel_cities:
        st.info("Select at least one city to begin matching.")
        return

    # ── Global Cluster Overview ────────────────────────
    st.divider()
    section_header("City Cluster Overview")

    col1, col2, col3 = st.columns(3)
    with col1:
        fig_scatter = px.scatter(
            city_clean, x="co2_emissions", y="renewable_energy",
            color="cluster_label", hover_name="city",
            size="gdp_per_capita", color_discrete_sequence=CHART_COLORS,
            labels={"co2_emissions": "CO2 Emissions",
                    "renewable_energy": "Renewable Energy (%)",
                    "cluster_label": "Cluster"}
        )
        fig_scatter.update_layout(
            **CHART_LAYOUT, height=350,
            title=dict(text="CO2 vs Renewable Energy",
                      font=dict(color="#CCCCCC", size=13))
        )
        fig_scatter.update_layout(legend=DEFAULT_LEGEND)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        fig_pm = px.bar(
            city_clean.sort_values("pm25_exposure", ascending=False),
            x="city", y="pm25_exposure",
            color="cluster_label", color_discrete_sequence=CHART_COLORS,
            labels={"pm25_exposure": "PM2.5", "cluster_label": "Cluster"}
        )
        fig_pm.update_layout(
            **CHART_LAYOUT, height=350,
            title=dict(text="PM2.5 Exposure by City",
                      font=dict(color="#CCCCCC", size=13)),
            xaxis_tickangle=-45, showlegend=False
        )
        st.plotly_chart(fig_pm, use_container_width=True)

    with col3:
        cluster_counts = city_clean["cluster_label"].value_counts().reset_index()
        cluster_counts.columns = ["cluster", "count"]
        fig_pie = px.pie(
            cluster_counts, names="cluster", values="count",
            color_discrete_sequence=CHART_COLORS, hole=0.5
        )
        fig_pie.update_layout(
            **CHART_LAYOUT, height=350,
            title=dict(text="Cities by Cluster",
                      font=dict(color="#CCCCCC", size=13))
        )
        fig_pie.update_layout(legend=dict(bgcolor="#1C1C1C", bordercolor="#2A2A2A",
                                          orientation="v", x=0.6))
        fig_pie.update_traces(textinfo="percent", textfont=dict(color="#E8E8E8"))
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Radar Chart ───────────────────────────────────
    st.divider()
    section_header("City Sustainability Radar — Selected Cities")

    radar_cols   = ["co2_emissions","renewable_energy","pm25_exposure",
                    "gdp_per_capita","access_electricity","urban_population"]
    radar_labels = ["CO2","Renewables","PM2.5","GDP","Electricity","Urban Pop"]
    col_mins     = city_clean[radar_cols].min()
    col_maxs     = city_clean[radar_cols].max()

    fig_radar = go.Figure()
    for i, city in enumerate(sel_cities[:5]):
        row = city_clean[city_clean["city"] == city]
        if row.empty:
            continue
        vals      = row[radar_cols].values[0].tolist()
        norm_vals = [(v - col_mins[c]) / (col_maxs[c] - col_mins[c] + 1e-9)
                     for v, c in zip(vals, radar_cols)]
        norm_vals += [norm_vals[0]]
        color = CHART_COLORS[i % len(CHART_COLORS)]
        r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        fig_radar.add_trace(go.Scatterpolar(
            r=norm_vals,
            theta=radar_labels + [radar_labels[0]],
            fill="toself",
            name=city,
            line=dict(color=color, width=2),
            fillcolor=f"rgba({r},{g},{b},0.1)"
        ))

    fig_radar.update_layout(
        paper_bgcolor="#1C1C1C",
        font=dict(color="#888888", family="Inter", size=12),
        polar=dict(
            bgcolor="#161616",
            radialaxis=dict(visible=True, range=[0,1],
                           color="#444444", gridcolor="#2A2A2A"),
            angularaxis=dict(color="#666666", gridcolor="#2A2A2A")
        ),
        height=420,
        legend=dict(bgcolor="#1C1C1C", bordercolor="#2A2A2A", borderwidth=1),
        margin=dict(t=50, b=40, l=60, r=60),
        title=dict(text="Normalized Sustainability Profile Comparison",
                  font=dict(color="#CCCCCC", size=14))
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Per City Matching ─────────────────────────────
    for sel_city in sel_cities:
        city_row = city_clean[city_clean["city"] == sel_city].iloc[0]
        cluster  = city_row["cluster_label"]
        needs    = CLUSTER_NEEDS.get(cluster, [])

        st.divider()
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
            <div style="font-size:1.2rem;font-weight:800;color:#F0F0F0;">{sel_city}</div>
            <div style="background:#2A1F00;border:1px solid #F5A623;border-radius:20px;
                        padding:0.2rem 0.8rem;font-size:0.72rem;
                        color:#F5A623;font-weight:600;">{cluster}</div>
            <div style="font-size:0.72rem;color:#555555;">
                {COUNTRY_NAMES.get(city_row['country'], city_row['country'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("CO2 Emissions",        round(city_row["co2_emissions"], 2))
        c2.metric("Renewable Energy (%)", round(city_row["renewable_energy"], 2))
        c3.metric("PM2.5 Exposure",       round(city_row["pm25_exposure"], 2))
        c4.metric("GDP per Capita",       f"${round(city_row['gdp_per_capita']):,}")

        section_header("Recommended Innovation Sectors")
        need_cols = st.columns(len(needs))
        for i, need in enumerate(needs):
            need_cols[i].markdown(f"""
            <div style="background:#2A1F00;border:1px solid #F5A623;
                        border-radius:8px;padding:0.6rem;text-align:center;
                        font-size:0.8rem;color:#F5A623;font-weight:600;">{need}</div>
            """, unsafe_allow_html=True)

        matched = startups_df[
            (startups_df["sector"].isin(needs)) &
            (startups_df["impact_tier"].isin(sel_tier))
        ].sort_values("sustainability_score", ascending=False).head(10)

        if matched.empty:
            matched = startups_df[
                startups_df["sector"].isin(needs)
            ].sort_values("sustainability_score", ascending=False).head(10)

        col1, col2 = st.columns(2)
        with col1:
            section_header(f"Top Matched Startups — {sel_city}")
            fig_bar = px.bar(
                matched.head(8).sort_values("sustainability_score"),
                x="sustainability_score", y="name",
                orientation="h", color="impact_tier",
                color_discrete_map={
                    "High": "#3B7D4F", "Medium": "#F5A623", "Low": "#D4526E"
                },
                labels={"sustainability_score": "Score", "name": "",
                        "impact_tier": "Impact Tier"}
            )
            fig_bar.update_layout(**CHART_LAYOUT, height=320)
            fig_bar.update_layout(legend=DEFAULT_LEGEND)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            section_header("Score Distribution by Sector")
            fig_box = px.box(
                startups_df[startups_df["sector"].isin(needs)],
                x="sector", y="sustainability_score",
                color="sector", color_discrete_sequence=CHART_COLORS,
                labels={"sustainability_score": "Score", "sector": ""}
            )
            fig_box.update_layout(**CHART_LAYOUT, height=320,
                                  showlegend=False, xaxis_tickangle=-20)
            st.plotly_chart(fig_box, use_container_width=True)

        with st.expander(f"View All Matched Startups — {sel_city}"):
            st.dataframe(matched.round(2), use_container_width=True)
            st.download_button(
                f"Download Matches — {sel_city}",
                matched.to_csv(index=False),
                f"matches_{sel_city}.csv"
            )

    # ── All Cities Table ──────────────────────────────
    st.divider()
    section_header("All Cities — Cluster Assignments")
    display_df = city_clean.copy()
    display_df["country"] = display_df["country"].map(
        lambda x: COUNTRY_NAMES.get(x, x)
    )
    st.dataframe(
        display_df[["city","country","cluster_label","co2_emissions",
                    "renewable_energy","pm25_exposure","gdp_per_capita"]
                   ].sort_values("cluster_label").round(2),
        use_container_width=True
    )