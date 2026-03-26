import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_session
from database.models import City, CityIndicator
from models.forecasting import forecast_city

INDICATOR_LABELS = {
    "co2_emissions":    "CO2 Emissions (per capita)",
    "renewable_energy": "Renewable Energy (%)",
    "pm25_exposure":    "PM2.5 Exposure (ug/m3)",
    "gdp_per_capita":   "GDP per Capita (USD)",
}

ACCENT = "#F5A623"

CHART_LAYOUT = dict(
    paper_bgcolor="#1C1C1C",
    plot_bgcolor="#161616",
    font=dict(color="#888888", family="Inter, sans-serif", size=12),
    xaxis=dict(gridcolor="#2A2A2A", linecolor="#2A2A2A", tickcolor="#555555"),
    yaxis=dict(gridcolor="#2A2A2A", linecolor="#2A2A2A", tickcolor="#555555"),
    margin=dict(t=50, b=40, l=20, r=20),
)

@st.cache_data(ttl=3600)
def load_indicators():
    session = get_session()
    rows = session.query(
        City.name.label("city"),
        CityIndicator.year,
        CityIndicator.co2_emissions,
        CityIndicator.renewable_energy,
        CityIndicator.pm25_exposure,
        CityIndicator.gdp_per_capita,
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
                    text-transform:uppercase;letter-spacing:0.12em;">Predictive Analytics</div>
        <div style="font-size:1.8rem;font-weight:800;color:#F0F0F0;
                    letter-spacing:-0.02em;">Sustainability Forecasting</div>
        <div style="font-size:0.85rem;color:#666666;margin-top:0.3rem;">
            LightGBM multi-year forecasts with lag features and TimeSeriesSplit cross-validation.
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = load_indicators()

    st.markdown("""
    <div style="background:#1C1C1C;border:1px solid #333333;border-radius:10px;
                padding:1.2rem 1.5rem;margin-bottom:1rem;">
        <div style="font-size:0.68rem;font-weight:700;color:#F5A623;
                    text-transform:uppercase;letter-spacing:0.12em;margin-bottom:1rem;">
            Filters
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    all_cities = sorted(df["city"].unique())
    sel_cities = col1.multiselect("Cities", all_cities,
                                  default=["Amsterdam","Boston","Nairobi"])
    sel_target = col2.selectbox(
        "Indicator", list(INDICATOR_LABELS.keys()),
        format_func=lambda x: INDICATOR_LABELS[x]
    )
    sel_years = col3.slider("Forecast Horizon (Years)", 1, 8, 5)
    st.markdown("</div>", unsafe_allow_html=True)

    if not sel_cities:
        st.info("Select at least one city.")
        return

    for sel_city in sel_cities:
        city_df = df[df["city"] == sel_city][["year", sel_target]].dropna()
        if len(city_df) < 4:
            st.warning(f"Not enough data for {sel_city}.")
            continue

        with st.spinner(f"Generating forecast for {sel_city}..."):
            forecast_df = forecast_city(sel_city, sel_target, periods=sel_years)

        if forecast_df.empty:
            st.warning(f"Forecast unavailable for {sel_city}.")
            continue

        last_val     = city_df[sel_target].iloc[-1]
        forecast_val = forecast_df["forecast"].iloc[-1]
        delta        = round(forecast_val - last_val, 2)
        trend        = "Increasing" if delta > 0 else "Decreasing"
        trend_color  = "#D4526E" if delta > 0 else "#3B7D4F"

        st.divider()
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.8rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#F0F0F0;">{sel_city}</div>
            <div style="background:#1C1C1C;border:1px solid {trend_color};
                        border-radius:12px;padding:0.2rem 0.7rem;
                        font-size:0.72rem;color:{trend_color};font-weight:600;">{trend}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Current Value",              round(last_val, 2))
        c2.metric(f"{sel_years}-Year Forecast", round(forecast_val, 2), delta=str(delta))
        c3.metric("Projected Change",           f"{round((delta/last_val)*100, 1)}%")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=city_df["year"], y=city_df[sel_target],
            name="Historical",
            line=dict(color="#CCCCCC", width=2.5),
            mode="lines+markers",
            marker=dict(size=6, color="#CCCCCC")
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df["year"], y=forecast_df["forecast"],
            name="Forecast",
            line=dict(color=ACCENT, width=2.5, dash="dash"),
            mode="lines+markers",
            marker=dict(size=6, color=ACCENT)
        ))
        fig.add_trace(go.Scatter(
            x=pd.concat([forecast_df["year"], forecast_df["year"][::-1]]),
            y=pd.concat([forecast_df["upper_bound"], forecast_df["lower_bound"][::-1]]),
            fill="toself",
            fillcolor="rgba(245,166,35,0.08)",
            line=dict(color="rgba(255,255,255,0)"),
            name="95% Confidence Interval"
        ))
        fig.update_layout(
            **CHART_LAYOUT,
            height=420,
            title=dict(
                text=f"{sel_city} — {INDICATOR_LABELS[sel_target]}",
                font=dict(color="#CCCCCC", size=14)
            ),
            xaxis_title="Year",
            yaxis_title=INDICATOR_LABELS[sel_target],
        )
        fig.update_layout(legend=dict(bgcolor="#1C1C1C", bordercolor="#2A2A2A",
                                      orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

        with st.expander(f"Forecast Data — {sel_city}"):
            st.dataframe(forecast_df.round(3), use_container_width=True)
            st.download_button(
                f"Download Forecast — {sel_city}",
                forecast_df.to_csv(index=False),
                f"forecast_{sel_city}_{sel_target}.csv"
            )