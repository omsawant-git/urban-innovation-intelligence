import pandas as pd
import numpy as np
from config.settings import CITIES, STARTUP_SECTORS, RANDOM_STATE

def generate_startup_dataset(n: int = 500) -> pd.DataFrame:
    """
    Generate a realistic startup dataset simulating
    AcceliCITY-style applications.
    """
    rng = np.random.default_rng(RANDOM_STATE)
    city_names    = [c["name"]    for c in CITIES]
    city_countries= [c["country"] for c in CITIES]

    city_idx = rng.integers(0, len(city_names), n)

    prefixes = ["Green", "Smart", "Urban", "Eco", "Climate", "City", "Clean", "Nexus", "Terra", "Volt"]
    suffixes = ["Tech", "Labs", "AI", "Works", "Systems", "Hub", "Solutions", "Dynamics", "Ventures", "Innovations"]
    names = [
        f"{rng.choice(prefixes)}{rng.choice(suffixes)} {i+1}"
        for i in range(n)
    ]

    sectors       = rng.choice(STARTUP_SECTORS, n)
    founding_year = rng.integers(2010, 2024, n)
    team_size     = rng.integers(2, 200, n)
    funding_usd   = rng.exponential(500_000, n).round(-3)
    num_pilots    = rng.integers(0, 20, n)
    cities_deployed = rng.integers(1, 30, n)
    has_gov_partner = rng.choice([True, False], n, p=[0.4, 0.6])
    revenue_stage = rng.choice(
        ["Pre-Revenue", "Early Revenue", "Growth", "Scaling"], n,
        p=[0.3, 0.3, 0.25, 0.15]
    )

    # Sustainability score — composite of features
    sustainability_score = (
        (num_pilots * 2) +
        (cities_deployed * 1.5) +
        (has_gov_partner.astype(int) * 10) +
        (np.log1p(funding_usd) * 2) +
        rng.normal(0, 5, n)
    )
    sustainability_score = (
        (sustainability_score - sustainability_score.min()) /
        (sustainability_score.max() - sustainability_score.min()) * 100
    ).round(2)

    # Impact tier derived from score
    impact_tier = pd.cut(
        sustainability_score,
        bins=[0, 33, 66, 100],
        labels=["Low", "Medium", "High"]
    ).astype(str)

    df = pd.DataFrame({
        "name":                  names,
        "sector":                sectors,
        "city":                  [city_names[i]     for i in city_idx],
        "country":               [city_countries[i] for i in city_idx],
        "founding_year":         founding_year,
        "team_size":             team_size,
        "funding_usd":           funding_usd,
        "num_pilots":            num_pilots,
        "cities_deployed":       cities_deployed,
        "has_government_partner":has_gov_partner,
        "revenue_stage":         revenue_stage,
        "sustainability_score":  sustainability_score,
        "impact_tier":           impact_tier,
    })

    return df