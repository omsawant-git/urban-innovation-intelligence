import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     os.getenv("DB_PORT", 5432),
    "database": os.getenv("DB_NAME", "acceliscout"),
    "user":     os.getenv("DB_USER", "acceliscout_user"),
    "password": os.getenv("DB_PASSWORD", "acceliscout123"),
}

DATABASE_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

CITIES = [
    {"name": "Boston",         "country": "US", "lat": 42.36,  "lon": -71.06,  "wb_code": "USA"},
    {"name": "New York",       "country": "US", "lat": 40.71,  "lon": -74.01,  "wb_code": "USA"},
    {"name": "Los Angeles",    "country": "US", "lat": 34.05,  "lon": -118.24, "wb_code": "USA"},
    {"name": "Chicago",        "country": "US", "lat": 41.88,  "lon": -87.63,  "wb_code": "USA"},
    {"name": "London",         "country": "GB", "lat": 51.51,  "lon": -0.13,   "wb_code": "GBR"},
    {"name": "Barcelona",      "country": "ES", "lat": 41.39,  "lon": 2.15,    "wb_code": "ESP"},
    {"name": "Amsterdam",      "country": "NL", "lat": 52.37,  "lon": 4.90,    "wb_code": "NLD"},
    {"name": "Singapore",      "country": "SG", "lat": 1.35,   "lon": 103.82,  "wb_code": "SGP"},
    {"name": "Tokyo",          "country": "JP", "lat": 35.68,  "lon": 139.69,  "wb_code": "JPN"},
    {"name": "Sydney",         "country": "AU", "lat": -33.87, "lon": 151.21,  "wb_code": "AUS"},
    {"name": "Toronto",        "country": "CA", "lat": 43.65,  "lon": -79.38,  "wb_code": "CAN"},
    {"name": "Dubai",          "country": "AE", "lat": 25.20,  "lon": 55.27,   "wb_code": "ARE"},
    {"name": "Rio de Janeiro", "country": "BR", "lat": -22.91, "lon": -43.17,  "wb_code": "BRA"},
    {"name": "Nairobi",        "country": "KE", "lat": -1.29,  "lon": 36.82,   "wb_code": "KEN"},
    {"name": "Mumbai",         "country": "IN", "lat": 19.08,  "lon": 72.88,   "wb_code": "IND"},
]

WB_INDICATORS = {
    "co2_emissions":      "EN.ATM.CO2E.PC",
    "renewable_energy":   "EG.FEC.RNEW.ZS",
    "urban_population":   "SP.URB.TOTL.IN.ZS",
    "gdp_per_capita":     "NY.GDP.PCAP.CD",
    "pm25_exposure":      "EN.ATM.PM25.MC.M3",
    "access_electricity": "EG.ELC.ACCS.ZS",
}

STARTUP_SECTORS = [
    "Clean Energy", "Smart Mobility", "Waste Management",
    "Water Technology", "Urban Agriculture", "Climate Tech",
    "Smart Infrastructure", "Green Building", "Air Quality",
    "Circular Economy"
]

IMPACT_TIERS  = ["High", "Medium", "Low"]
FORECAST_HORIZON  = 12
ANOMALY_THRESHOLD = 0.1
RANDOM_STATE      = 42