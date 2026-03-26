import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_session
from database.models import City, CityIndicator, Startup
from models.classifier import train_classifier
from models.clustering import train_clustering
from models.anomaly import train_anomaly_detector

ACCENT        = "#F5A623"
CHART_COLORS  = ["#F5A623", "#E8845A", "#D4526E", "#A23B72", "#6B4C9A"]

CHART_LAYOUT = dict(
    paper_bgcolor="#1C1C1C",
    plot_bgcolor="#161616",
    font=dict(color="#888888", family="Inter, sans-serif", size=12),
    xaxis=dict(gridcolor="#2A2A2A", linecolor="#2A2A2A", tickcolor="#555555"),
    yaxis=dict(gridcolor="#2A2A2A", linecolor="#2A2A2A", tickcolor="#555555"),
    margin=dict(t=50, b=40, l=20, r=20),
)

DEFAULT_LEGEND = dict(bgcolor="#1C1C1C", bordercolor="#2A2A2A", borderwidth=1)

@st.cache_data(ttl=7200)
def get_classifier_metrics():
    session = get_session()
    rows = session.query(Startup).all()
    session.close()
    df = pd.DataFrame([{
        "founding_year": r.founding_year, "team_size": r.team_size,
        "funding_usd": r.funding_usd, "num_pilots": r.num_pilots,
        "cities_deployed": r.cities_deployed,
        "has_government_partner": r.has_government_partner,
        "revenue_stage": r.revenue_stage,
        "sustainability_score": r.sustainability_score,
        "impact_tier": r.impact_tier,
    } for r in rows])
    df = df.dropna(subset=["impact_tier"])
    df = df[df["impact_tier"].isin(["Low","Medium","High"])]
    return train_classifier(df)["metrics"]

@st.cache_data(ttl=7200)
def get_cluster_metrics():
    session = get_session()
    rows = session.query(
        City.name.label("city"),
        CityIndicator.co2_emissions, CityIndicator.renewable_energy,
        CityIndicator.urban_population, CityIndicator.gdp_per_capita,
        CityIndicator.pm25_exposure, CityIndicator.access_electricity,
    ).join(City, City.id == CityIndicator.city_id).all()
    session.close()
    result = train_clustering(pd.DataFrame(rows))
    return result["metrics"], result["city_clusters"]

@st.cache_data(ttl=7200)
def get_anomaly_metrics():
    session = get_session()
    rows = session.query(
        City.name.label("city"),
        CityIndicator.co2_emissions, CityIndicator.renewable_energy,
        CityIndicator.pm25_exposure, CityIndicator.gdp_per_capita,
    ).join(City, City.id == CityIndicator.city_id).all()
    session.close()
    result = train_anomaly_detector(pd.DataFrame(rows))
    return result["metrics"], result["city_anomalies"]

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
                    text-transform:uppercase;letter-spacing:0.12em;">Evaluation</div>
        <div style="font-size:1.8rem;font-weight:800;color:#F0F0F0;
                    letter-spacing:-0.02em;">Model Performance Dashboard</div>
        <div style="font-size:0.85rem;color:#666666;margin-top:0.3rem;">
            Evaluation metrics and diagnostics for all 4 production ML models.
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "XGBoost Classifier",
        "K-Means Clustering",
        "LightGBM Forecaster",
        "Isolation Forest"
    ])

    with tab1:
        section_header("XGBoost Startup Impact Classifier")
        st.caption("Classifies startups into High, Medium, or Low impact tiers.")
        with st.spinner("Computing metrics..."):
            metrics = get_classifier_metrics()

        c1, c2, c3 = st.columns(3)
        c1.metric("F1 Score (Weighted)", round(metrics["f1_weighted"], 3))
        c2.metric("ROC-AUC Score",       round(metrics.get("roc_auc", 0), 3))
        c3.metric("Algorithm",           "XGBoost")

        st.divider()
        section_header("Classification Report")
        report_df = pd.DataFrame(metrics["classification_report"]).transpose().round(3)
        st.dataframe(report_df, use_container_width=True)

        if "shap_importance" in metrics:
            st.divider()
            section_header("SHAP Feature Importance")
            shap_df = pd.DataFrame(
                list(metrics["shap_importance"].items()),
                columns=["Feature", "Importance"]
            ).sort_values("Importance")
            fig = px.bar(
                shap_df, x="Importance", y="Feature",
                orientation="h", color="Importance",
                color_continuous_scale=["#2A1F00", "#F5A623"]
            )
            fig.update_layout(
                **CHART_LAYOUT, height=320,
                legend=DEFAULT_LEGEND,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        section_header("K-Means City Sustainability Clustering")
        st.caption("Groups 15 cities into 5 sustainability profiles based on key indicators.")
        with st.spinner("Computing metrics..."):
            clu_metrics, city_clusters = get_cluster_metrics()

        c1, c2 = st.columns(2)
        c1.metric("Silhouette Score",    round(clu_metrics["silhouette_score"], 3))
        c2.metric("Number of Clusters",  "5")

        st.divider()
        section_header("Elbow Plot — Optimal K Selection")
        elbow    = clu_metrics["elbow_data"]
        elbow_df = pd.DataFrame({"K": elbow["k"], "Inertia": elbow["inertia"]})
        fig = px.line(elbow_df, x="K", y="Inertia", markers=True,
                      color_discrete_sequence=[ACCENT])
        fig.update_traces(line=dict(width=2.5), marker=dict(size=8, color="#E8845A"))
        fig.update_layout(**CHART_LAYOUT, height=320, legend=DEFAULT_LEGEND)
        st.plotly_chart(fig, use_container_width=True)

        section_header("City Cluster Assignments")
        st.dataframe(
            city_clusters[["city","cluster_label","co2_emissions",
                           "renewable_energy","pm25_exposure"]].round(2),
            use_container_width=True
        )

    with tab3:
        section_header("LightGBM Time-Series Forecaster")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background:#1C1C1C;border:1px solid #2A2A2A;
                        border-radius:10px;padding:1.2rem;">
                <div style="font-size:0.82rem;font-weight:700;color:#CCCCCC;
                            margin-bottom:0.8rem;">Model Architecture</div>
                <div style="font-size:0.78rem;color:#666666;line-height:2.2;">
                    Algorithm: LightGBM Regressor<br>
                    Lag Features: 1, 2, 3, 6 years<br>
                    Rolling Stats: Mean + Std (window=3)<br>
                    Validation: TimeSeriesSplit (3 folds)<br>
                    Forecasting: Recursive multi-step
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style="background:#1C1C1C;border:1px solid #2A2A2A;
                        border-radius:10px;padding:1.2rem;">
                <div style="font-size:0.82rem;font-weight:700;color:#CCCCCC;
                            margin-bottom:0.8rem;">Target Indicators</div>
                <div style="font-size:0.78rem;color:#666666;line-height:2.2;">
                    CO2 Emissions per capita<br>
                    Renewable Energy (%)<br>
                    PM2.5 Exposure<br>
                    GDP per Capita<br>
                    Evaluation: MAPE + RMSE
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.info("Per-city forecast accuracy is visible on the Forecasting page.")

    with tab4:
        section_header("Isolation Forest Anomaly Detector")
        st.caption("Identifies cities with unusual sustainability profiles.")
        with st.spinner("Computing metrics..."):
            ano_metrics, city_anomalies = get_anomaly_metrics()

        c1, c2, c3 = st.columns(3)
        c1.metric("Cities Analyzed",    ano_metrics["total_records"])
        c2.metric("Anomalies Detected", ano_metrics["total_anomalies"])
        c3.metric("Anomaly Rate",       f"{ano_metrics['anomaly_rate']*100:.1f}%")

        st.divider()
        section_header("Anomaly Score by City")
        st.caption("Lower scores indicate more anomalous behavior.")
        fig = px.bar(
            city_anomalies.sort_values("anomaly_score"),
            x="city", y="anomaly_score",
            color="severity",
            color_discrete_map={
                "High": "#D4526E", "Medium": "#F5A623", "Low": "#3B7D4F"
            },
            labels={"anomaly_score": "Anomaly Score", "severity": "Severity"}
        )
        fig.update_layout(
            **CHART_LAYOUT, height=400,
            legend=DEFAULT_LEGEND,
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig, use_container_width=True)

        anomalies = city_anomalies[city_anomalies["is_anomaly"]]
        if not anomalies.empty:
            section_header("Flagged Cities")
            st.dataframe(
                anomalies[["city","anomaly_score","severity",
                           "co2_emissions","renewable_energy"]].round(3),
                use_container_width=True
            )