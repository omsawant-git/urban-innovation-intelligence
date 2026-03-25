import pandas as pd
import numpy as np
import pickle
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from models.evaluator import evaluate_anomaly
from config.settings import RANDOM_STATE, ANOMALY_THRESHOLD

logger = logging.getLogger(__name__)

ANOMALY_FEATURES = [
    "co2_emissions", "renewable_energy",
    "pm25_exposure", "gdp_per_capita"
]

def train_anomaly_detector(df: pd.DataFrame) -> dict:
    """Train Isolation Forest on city indicators."""
    logger.info("Training Isolation Forest anomaly detector...")

    city_avg = df.groupby("city")[ANOMALY_FEATURES].mean().reset_index().dropna()
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(city_avg[ANOMALY_FEATURES])

    model = IsolationForest(
        contamination=ANOMALY_THRESHOLD,
        random_state=RANDOM_STATE,
        n_estimators=100
    )
    model.fit(X_scaled)

    city_avg["anomaly_score"] = model.decision_function(X_scaled)
    city_avg["is_anomaly"]    = model.predict(X_scaled) == -1
    city_avg["severity"]      = city_avg["anomaly_score"].apply(
        lambda s: "High" if s < -0.1 else ("Medium" if s < 0 else "Low")
    )

    metrics = evaluate_anomaly(
        np.zeros(len(city_avg)),
        city_avg["is_anomaly"].values
    )

    with open("artifacts/anomaly.pkl", "wb") as f:
        pickle.dump({"model": model, "scaler": scaler}, f)

    logger.info("✅ Anomaly detector trained and saved.")
    return {"model": model, "city_anomalies": city_avg, "metrics": metrics}