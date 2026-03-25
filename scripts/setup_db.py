"""
Run once to initialize the database, create tables, and load all data.
Usage: python scripts/setup_db.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

from database.connection import get_engine, test_connection
from database.models import Base, City, CityIndicator, CityClimate, Startup
from config.settings import CITIES
from etl.worldbank import fetch_all_city_indicators
from etl.openmeteo import fetch_all_climate
from etl.startups import generate_startup_dataset
from sqlalchemy.orm import sessionmaker

def create_tables(engine):
    logger.info("Creating database tables...")
    Base.metadata.create_all(engine)
    logger.info("✅ Tables created.")

def load_cities(session):
    logger.info("Loading cities...")
    for c in CITIES:
        exists = session.query(City).filter_by(name=c["name"]).first()
        if not exists:
            session.add(City(
                name=c["name"], country=c["country"],
                country_code=c["wb_code"],
                latitude=c["lat"], longitude=c["lon"]
            ))
    session.commit()
    logger.info(f"✅ {len(CITIES)} cities loaded.")

def load_indicators(session):
    logger.info("Fetching World Bank indicators (this may take 1-2 min)...")
    df = fetch_all_city_indicators()
    if df.empty:
        logger.warning("No indicator data fetched.")
        return

    cities = {c.name: c.id for c in session.query(City).all()}
    count  = 0
    for _, row in df.iterrows():
        city_id = cities.get(row["city"])
        if not city_id:
            continue
        exists = session.query(CityIndicator).filter_by(
            city_id=city_id, year=int(row["year"])
        ).first()
        if not exists:
            session.add(CityIndicator(
                city_id            = city_id,
                year               = int(row["year"]),
                co2_emissions      = row.get("co2_emissions"),
                renewable_energy   = row.get("renewable_energy"),
                urban_population   = row.get("urban_population"),
                gdp_per_capita     = row.get("gdp_per_capita"),
                pm25_exposure      = row.get("pm25_exposure"),
                access_electricity = row.get("access_electricity"),
            ))
            count += 1
    session.commit()
    logger.info(f"✅ {count} indicator records loaded.")

def load_climate(session):
    logger.info("Fetching climate data from Open-Meteo (this may take 2-3 min)...")
    df = fetch_all_climate()
    if df.empty:
        logger.warning("No climate data fetched.")
        return

    cities = {c.name: c.id for c in session.query(City).all()}
    count  = 0
    for _, row in df.iterrows():
        city_id = cities.get(row["city"])
        if not city_id:
            continue
        exists = session.query(CityClimate).filter_by(
            city_id=city_id, date=row["date"]
        ).first()
        if not exists:
            session.add(CityClimate(
                city_id       = city_id,
                date          = row["date"],
                temp_max      = row.get("temp_max"),
                temp_min      = row.get("temp_min"),
                temp_mean     = row.get("temp_mean"),
                precipitation = row.get("precipitation"),
                wind_speed    = row.get("wind_speed"),
            ))
            count += 1
    session.commit()
    logger.info(f"✅ {count} climate records loaded.")

def load_startups(session):
    logger.info("Generating startup dataset...")
    df = generate_startup_dataset(500)
    for _, row in df.iterrows():
        session.add(Startup(
            name                   = row["name"],
            sector                 = row["sector"],
            city                   = row["city"],
            country                = row["country"],
            founding_year          = int(row["founding_year"]),
            team_size              = int(row["team_size"]),
            funding_usd            = float(row["funding_usd"]),
            num_pilots             = int(row["num_pilots"]),
            cities_deployed        = int(row["cities_deployed"]),
            has_government_partner = bool(row["has_government_partner"]),
            revenue_stage          = row["revenue_stage"],
            sustainability_score   = float(row["sustainability_score"]),
            impact_tier            = row["impact_tier"],
        ))
    session.commit()
    logger.info(f"✅ {len(df)} startups loaded.")

if __name__ == "__main__":
    if not test_connection():
        logger.error("Cannot connect to database. Check your .env file.")
        sys.exit(1)

    engine  = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    create_tables(engine)
    load_cities(session)
    load_indicators(session)
    load_climate(session)
    load_startups(session)

    session.close()
    logger.info("🎉 Database setup complete!")