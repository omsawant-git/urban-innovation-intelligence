import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_session
from database.models import City, CityIndicator

INDICATOR_LABELS = {
    "co2_emissions":      "CO2 Emissions (per capita)",
    "renewable_energy":   "Renewable Energy (%)",
    "pm25_exposure":      "PM2.5 Exposure (ug/m3)",
    "gdp_per_capita":     "GDP per Capita (USD)",
    "access_electricity": "Electricity Access (%)",
    "urban_population":   "Urban Population (%)",
}

COUNTRY_NAMES = {
    "US": "United States (US)", "GB": "United Kingdom (GB)",
    "ES": "Spain (ES)",         "NL": "Netherlands (NL)",
    "SG": "Singapore (SG)",     "JP": "Japan (JP)",
    "AU": "Australia (AU)",     "CA": "Canada (CA)",
    "AE": "United Arab Emirates (AE)", "BR": "Brazil (BR)",
    "KE": "Kenya (KE)",         "IN": "India (IN)",
}

ACCENT       = "#F5A623"
CHART_COLORS = ["#F5A623", "#E8845A", "#D4526E", "#A23B72", "#6B4C9A", "#3B7D4F"]

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
def load_city_data():
    session = get_session()
    rows = session.query(
        City.name.label("city"),
        City.latitude, City.longitude, City.country,
        CityIndicator.year,
        CityIndicator.co2_emissions,
        CityIndicator.renewable_energy,
        CityIndicator.pm25_exposure,
        CityIndicator.gdp_per_capita,
        CityIndicator.access_electricity,
        CityIndicator.urban_population,
    ).join(City, City.id == CityIndicator.city_id).all()
    session.close()
    return pd.DataFrame(rows)

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
                    text-transform:uppercase;letter-spacing:0.12em;">City Analytics</div>
        <div style="font-size:1.8rem;font-weight:800;color:#F0F0F0;
                    letter-spacing:-0.02em;">Global City Sustainability Map</div>
        <div style="font-size:0.85rem;color:#666666;margin-top:0.3rem;">
            Explore sustainability indicators across Leading Cities' global network of 15 cities.
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = load_city_data()
    if df.empty:
        st.error("No data found. Run setup_db.py first.")
        return

    st.markdown("""
    <div style="background:#1C1C1C;border:1px solid #333333;border-radius:10px;
                padding:1.2rem 1.5rem;margin-bottom:1rem;">
        <div style="font-size:0.68rem;font-weight:700;color:#F5A623;
                    text-transform:uppercase;letter-spacing:0.12em;margin-bottom:1rem;">
            Filters
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    years     = sorted(df["year"].unique(), reverse=True)
    sel_year  = col1.selectbox("Reference Year", years)
    indicator = col2.selectbox(
        "Indicator", list(INDICATOR_LABELS.keys()),
        format_func=lambda x: INDICATOR_LABELS[x]
    )
    all_countries      = sorted(df["country"].unique().tolist())
    country_options    = [COUNTRY_NAMES.get(c, c) for c in all_countries]
    reverse_map        = {v: k for k, v in COUNTRY_NAMES.items()}
    sel_country_labels = col3.multiselect("Countries", country_options, default=country_options)
    sel_countries      = [reverse_map.get(c, c) for c in sel_country_labels]
    st.markdown("</div>", unsafe_allow_html=True)

    filtered = df[df["year"] == sel_year]
    if sel_countries:
        filtered = filtered[filtered["country"].isin(sel_countries)]
    city_avg = filtered.groupby(
        ["city", "latitude", "longitude", "country"]
    )[indicator].mean().reset_index()

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cities Selected", len(city_avg))
    c2.metric("Reference Year",  sel_year)
    c3.metric("Global Average",  round(city_avg[indicator].mean(), 2))
    best = city_avg.loc[city_avg[indicator].idxmin(), "city"]
    c4.metric("Best Performing", best)

    st.divider()
    section_header(f"Geographic Distribution — {sel_year}")
    fig = px.scatter_geo(
        city_avg, lat="latitude", lon="longitude",
        color=indicator, hover_name="city",
        hover_data={"latitude": False, "longitude": False, indicator: ":.2f"},
        size_max=25, projection="natural earth",
        color_continuous_scale=["#D4526E", "#F5A623", "#3B7D4F"],
    )
    fig.update_layout(
        **CHART_LAYOUT,
        legend=DEFAULT_LEGEND,
        height=500,
        geo=dict(
            bgcolor="#161616", showframe=False,
            showcoastlines=True, coastlinecolor="#2A2A2A",
            showland=True, landcolor="#1C1C1C",
            showocean=True, oceancolor="#111111",
            showlakes=False, showcountries=True, countrycolor="#2A2A2A",
        ),
        coloraxis_colorbar=dict(
            bgcolor="#1C1C1C", bordercolor="#2A2A2A",
            tickcolor="#555555",
            title=dict(font=dict(color="#888888")),
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    section_header("Indicator Trends Over Time")
    all_cities = sorted(df["city"].unique())
    sel_cities = st.multiselect(
        "Select Cities to Compare", all_cities,
        default=["Boston", "London", "Tokyo", "Nairobi", "Amsterdam"]
    )
    if sel_cities:
        trend_df  = df[df["city"].isin(sel_cities)]
        city_year = trend_df.groupby(["city","year"])[indicator].mean().reset_index()
        fig2 = px.line(
            city_year, x="year", y=indicator, color="city",
            markers=True, color_discrete_sequence=CHART_COLORS,
            labels={"year": "Year", indicator: INDICATOR_LABELS[indicator], "city": "City"}
        )
        fig2.update_traces(line=dict(width=2.5), marker=dict(size=7))
        fig2.update_layout(
            **CHART_LAYOUT,
            legend=DEFAULT_LEGEND,
            height=420,
            title=dict(text=INDICATOR_LABELS[indicator], font=dict(color="#CCCCCC", size=14))
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    section_header(f"City Comparison — {sel_year}")
    city_sorted = city_avg.sort_values(indicator, ascending=True)
    fig3 = px.bar(
        city_sorted, x="city", y=indicator,
        color=indicator,
        color_continuous_scale=["#3B7D4F", "#F5A623", "#D4526E"],
        labels={"city": "City", indicator: INDICATOR_LABELS[indicator]}
    )
    fig3.update_layout(
        **CHART_LAYOUT,
        legend=DEFAULT_LEGEND,
        height=400,
        title=dict(text=f"{INDICATOR_LABELS[indicator]} by City", font=dict(color="#CCCCCC", size=14)),
        showlegend=False, xaxis_tickangle=-30
    )
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("View Raw Data"):
        st.dataframe(city_avg.sort_values(indicator).round(2), use_container_width=True)
        st.download_button("Download CSV", city_avg.to_csv(index=False), "city_indicators.csv")