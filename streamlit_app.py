"""
Streamlit Cloud entry point.
Initializes SQLite DB and loads data on first run.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ── Switch to SQLite for cloud deployment ──────────
os.environ.setdefault("USE_SQLITE", "true")

# ── Create artifacts directory ─────────────────────
os.makedirs("artifacts", exist_ok=True)

# ── Auto-initialize DB if empty ────────────────────
from database.connection import get_engine
from database.models import Base
from sqlalchemy.orm import sessionmaker

engine  = get_engine()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

from database.models import City
if session.query(City).count() == 0:
    import logging
    logging.basicConfig(level=logging.INFO)
    from config.settings import CITIES
    from database.models import CityIndicator, CityClimate, Startup
    from etl.worldbank import generate_fallback_indicators
    from etl.openmeteo import fetch_all_climate
    from etl.startups  import generate_startup_dataset
    import pandas as pd

    for c in CITIES:
        session.add(City(
            name=c["name"], country=c["country"],
            country_code=c["wb_code"],
            latitude=c["lat"], longitude=c["lon"]
        ))
    session.commit()

    cities_map = {c.name: c.id for c in session.query(City).all()}
    df_ind = generate_fallback_indicators()
    for _, row in df_ind.iterrows():
        cid = cities_map.get(row["city"])
        if cid:
            session.add(CityIndicator(
                city_id=cid, year=int(row["year"]),
                co2_emissions=row.get("co2_emissions"),
                renewable_energy=row.get("renewable_energy"),
                urban_population=row.get("urban_population"),
                gdp_per_capita=row.get("gdp_per_capita"),
                pm25_exposure=row.get("pm25_exposure"),
                access_electricity=row.get("access_electricity"),
            ))
    session.commit()

    try:
        df_clim = fetch_all_climate()
        for _, row in df_clim.iterrows():
            cid = cities_map.get(row["city"])
            if cid:
                session.add(CityClimate(
                    city_id=cid, date=row["date"],
                    temp_max=row.get("temp_max"),
                    temp_min=row.get("temp_min"),
                    temp_mean=row.get("temp_mean"),
                    precipitation=row.get("precipitation"),
                    wind_speed=row.get("wind_speed"),
                ))
        session.commit()
    except Exception:
        pass

    df_start = generate_startup_dataset(500)
    for _, row in df_start.iterrows():
        session.add(Startup(
            name=row["name"], sector=row["sector"],
            city=row["city"], country=row["country"],
            founding_year=int(row["founding_year"]),
            team_size=int(row["team_size"]),
            funding_usd=float(row["funding_usd"]),
            num_pilots=int(row["num_pilots"]),
            cities_deployed=int(row["cities_deployed"]),
            has_government_partner=bool(row["has_government_partner"]),
            revenue_stage=row["revenue_stage"],
            sustainability_score=float(row["sustainability_score"]),
            impact_tier=row["impact_tier"],
        ))
    session.commit()

session.close()

# ── Train models if artifacts missing ──────────────
import pickle

artifacts = [
    "artifacts/classifier.pkl",
    "artifacts/kmeans.pkl",
    "artifacts/lgbm_forecaster.pkl",
    "artifacts/anomaly.pkl",
]

if not all(os.path.exists(a) for a in artifacts):
    import logging
    logging.basicConfig(level=logging.INFO)
    from scripts.train_models import load_indicators, load_startups
    from models.classifier import train_classifier
    from models.clustering  import train_clustering
    from models.forecasting import train_forecasting
    from models.anomaly     import train_anomaly_detector

    s2   = Session()
    df_i = load_indicators(s2)
    df_s = load_startups(s2)
    s2.close()

    train_classifier(df_s)
    train_clustering(df_i)
    train_forecasting(df_i)
    train_anomaly_detector(df_i)

# ── Launch main app ────────────────────────────────
exec(open("main.py").read())