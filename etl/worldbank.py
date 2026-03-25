import pandas as pd
import numpy as np
import logging
from config.settings import CITIES, RANDOM_STATE

logger = logging.getLogger(__name__)


def generate_fallback_indicators() -> pd.DataFrame:
    """
    Generate realistic city indicator data based on
    real-world country baselines with year-over-year trends.
    """
    rng = np.random.default_rng(RANDOM_STATE)

    baselines = {
        "USA": {"co2": 14.2, "renewable": 12.0, "urban": 82.0, "gdp": 65000, "pm25": 7.4,  "elec": 100.0},
        "GBR": {"co2": 5.5,  "renewable": 42.0, "urban": 83.0, "gdp": 46000, "pm25": 10.0, "elec": 100.0},
        "ESP": {"co2": 5.8,  "renewable": 38.0, "urban": 80.0, "gdp": 30000, "pm25": 9.5,  "elec": 100.0},
        "NLD": {"co2": 8.2,  "renewable": 27.0, "urban": 91.0, "gdp": 57000, "pm25": 11.0, "elec": 100.0},
        "SGP": {"co2": 7.9,  "renewable": 3.0,  "urban": 100.0,"gdp": 65000, "pm25": 17.0, "elec": 100.0},
        "JPN": {"co2": 8.7,  "renewable": 19.0, "urban": 91.0, "gdp": 40000, "pm25": 11.5, "elec": 100.0},
        "AUS": {"co2": 14.8, "renewable": 24.0, "urban": 86.0, "gdp": 55000, "pm25": 7.0,  "elec": 100.0},
        "CAN": {"co2": 14.2, "renewable": 66.0, "urban": 81.0, "gdp": 52000, "pm25": 6.5,  "elec": 100.0},
        "ARE": {"co2": 20.5, "renewable": 4.0,  "urban": 87.0, "gdp": 43000, "pm25": 38.0, "elec": 100.0},
        "BRA": {"co2": 2.2,  "renewable": 83.0, "urban": 87.0, "gdp": 8900,  "pm25": 14.0, "elec": 99.0},
        "KEN": {"co2": 0.4,  "renewable": 74.0, "urban": 27.0, "gdp": 1900,  "pm25": 25.0, "elec": 75.0},
        "IND": {"co2": 1.9,  "renewable": 38.0, "urban": 34.0, "gdp": 2400,  "pm25": 55.0, "elec": 95.0},
    }

    records = []
    for city in CITIES:
        code = city["wb_code"]
        base = baselines.get(code, baselines["USA"])
        for year in range(2013, 2024):
            yr = year - 2013
            records.append({
                "city":               city["name"],
                "country":            city["country"],
                "country_code":       code,
                "year":               year,
                "co2_emissions":      round(max(0,   base["co2"]       - yr * 0.15 + rng.normal(0, 0.3)), 2),
                "renewable_energy":   round(min(100, base["renewable"] + yr * 1.2  + rng.normal(0, 1.5)), 2),
                "urban_population":   round(min(100, base["urban"]     + yr * 0.2  + rng.normal(0, 0.3)), 2),
                "gdp_per_capita":     round(base["gdp"] * (1 + yr * 0.02) + rng.normal(0, 500),           2),
                "pm25_exposure":      round(max(0,   base["pm25"]      - yr * 0.3  + rng.normal(0, 1.0)), 2),
                "access_electricity": round(min(100, base["elec"]      + rng.normal(0, 0.1)),              2),
            })

    df = pd.DataFrame(records)
    logger.info(f"✅ Generated {len(df)} indicator records.")
    return df


def fetch_all_city_indicators() -> pd.DataFrame:
    """Main entry point — returns city indicators DataFrame."""
    logger.info("Loading city indicators from generated data...")
    return generate_fallback_indicators()