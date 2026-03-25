"""
Train all 4 ML models and save artifacts.
Usage: python scripts/train_models.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import pandas as pd
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

from database.connection import get_session
from database.models import CityIndicator, Startup, City
from models.classifier import train_classifier
from models.clustering import train_clustering
from models.forecasting import train_forecasting
from models.anomaly import train_anomaly_detector

def load_indicators(session) -> pd.DataFrame:
    rows = session.query(
        City.name.label("city"),
        CityIndicator.year,
        CityIndicator.co2_emissions,
        CityIndicator.renewable_energy,
        CityIndicator.urban_population,
        CityIndicator.gdp_per_capita,
        CityIndicator.pm25_exposure,
        CityIndicator.access_electricity,
    ).join(City, City.id == CityIndicator.city_id).all()
    return pd.DataFrame(rows)

def load_startups(session) -> pd.DataFrame:
    rows = session.query(Startup).all()
    return pd.DataFrame([{
        "name": r.name, "sector": r.sector, "city": r.city,
        "founding_year": r.founding_year, "team_size": r.team_size,
        "funding_usd": r.funding_usd, "num_pilots": r.num_pilots,
        "cities_deployed": r.cities_deployed,
        "has_government_partner": r.has_government_partner,
        "revenue_stage": r.revenue_stage,
        "sustainability_score": r.sustainability_score,
        "impact_tier": r.impact_tier,
    } for r in rows])

if __name__ == "__main__":
    session = get_session()

    logger.info("Loading data from PostgreSQL...")
    indicators_df = load_indicators(session)
    startups_df   = load_startups(session)
    session.close()

    logger.info(f"Indicators: {len(indicators_df)} rows | Startups: {len(startups_df)} rows")

    logger.info("=" * 50)
    logger.info("Training Classifier...")
    clf_results = train_classifier(startups_df)
    logger.info(f"F1: {clf_results['metrics']['f1_weighted']:.3f}")

    logger.info("=" * 50)
    logger.info("Training Clustering...")
    clu_results = train_clustering(indicators_df)
    logger.info(f"Silhouette: {clu_results['metrics']['silhouette_score']:.3f}")

    logger.info("=" * 50)
    logger.info("Training Forecaster...")
    fct_results = train_forecasting(indicators_df)

    logger.info("=" * 50)
    logger.info("Training Anomaly Detector...")
    ano_results = train_anomaly_detector(indicators_df)
    logger.info(f"Anomalies: {ano_results['metrics']['total_anomalies']}")

    logger.info("=" * 50)
    logger.info("🎉 All models trained and saved to artifacts/")