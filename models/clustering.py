import pandas as pd
import numpy as np
import pickle
import logging
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from models.evaluator import evaluate_clustering
from config.settings import RANDOM_STATE

logger = logging.getLogger(__name__)

CLUSTER_FEATURES = [
    "co2_emissions", "renewable_energy", "urban_population",
    "gdp_per_capita", "pm25_exposure", "access_electricity"
]

CLUSTER_LABELS = {
    0: "Climate Leaders",
    1: "Emerging Sustainers",
    2: "Energy Dependent",
    3: "High Growth Cities",
    4: "Developing Hubs"
}

def prepare_city_features(df: pd.DataFrame):
    """Aggregate indicators per city and scale."""
    city_avg = df.groupby("city")[CLUSTER_FEATURES].mean().reset_index()
    city_avg = city_avg.dropna()
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(city_avg[CLUSTER_FEATURES])
    return city_avg, X_scaled, scaler

def train_clustering(df: pd.DataFrame, n_clusters: int = 5) -> dict:
    """Train K-Means clustering on city sustainability profiles."""
    logger.info("Training K-Means clustering...")

    city_avg, X_scaled, scaler = prepare_city_features(df)

    # Elbow method
    inertias = []
    k_range  = range(2, 9)
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)

    # Final model
    model = KMeans(n_clusters=n_clusters, random_state=RANDOM_STATE, n_init=10)
    model.fit(X_scaled)

    city_avg["cluster_id"]    = model.labels_
    city_avg["cluster_label"] = city_avg["cluster_id"].map(CLUSTER_LABELS)

    metrics = evaluate_clustering(X_scaled, model.labels_)
    metrics["elbow_data"] = {"k": list(k_range), "inertia": inertias}

    # PCA for 2D visualization
    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X_scaled)
    city_avg["pca_x"] = X_2d[:, 0]
    city_avg["pca_y"] = X_2d[:, 1]

    # Save artifacts
    with open("artifacts/kmeans.pkl", "wb") as f:
        pickle.dump({"model": model, "scaler": scaler, "pca": pca}, f)

    logger.info("✅ Clustering trained and saved.")
    return {"model": model, "city_clusters": city_avg, "metrics": metrics}