import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from config.settings import CITIES

logger = logging.getLogger(__name__)
BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

def fetch_city_climate(city: dict, years: int = 3) -> pd.DataFrame:
    """Fetch historical climate data for a city from Open-Meteo."""
    end_date   = datetime.now() - timedelta(days=7)
    start_date = end_date - timedelta(days=365 * years)

    params = {
        "latitude":        city["lat"],
        "longitude":       city["lon"],
        "start_date":      start_date.strftime("%Y-%m-%d"),
        "end_date":        end_date.strftime("%Y-%m-%d"),
        "daily":           "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_max",
        "timezone":        "auto",
        "temperature_unit":"celsius",
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame({
            "date":          data["daily"]["time"],
            "temp_max":      data["daily"]["temperature_2m_max"],
            "temp_min":      data["daily"]["temperature_2m_min"],
            "temp_mean":     data["daily"]["temperature_2m_mean"],
            "precipitation": data["daily"]["precipitation_sum"],
            "wind_speed":    data["daily"]["wind_speed_10m_max"],
        })

        df["city"]    = city["name"]
        df["country"] = city["country"]
        df["date"]    = pd.to_datetime(df["date"])
        df = df.dropna(subset=["temp_mean"])

        logger.info(f"Fetched {len(df)} climate records for {city['name']}")
        return df

    except Exception as e:
        logger.error(f"Failed fetching climate for {city['name']}: {e}")
        return pd.DataFrame()

def fetch_all_climate() -> pd.DataFrame:
    """Fetch climate data for all cities."""
    dfs = []
    for city in CITIES:
        df = fetch_city_climate(city)
        if not df.empty:
            dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)