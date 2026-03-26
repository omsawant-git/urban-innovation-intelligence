import os
import pandas as pd
import numpy as np
import pickle
import logging
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from models.evaluator import evaluate_classifier
from config.settings import RANDOM_STATE

logger = logging.getLogger(__name__)

FEATURE_COLS = [
    "founding_year", "team_size", "funding_usd",
    "num_pilots", "cities_deployed", "has_government_partner",
    "sustainability_score"
]
REVENUE_MAP = {"Pre-Revenue": 0, "Early Revenue": 1, "Growth": 2, "Scaling": 3}
TIER_MAP    = {"Low": 0, "Medium": 1, "High": 2}

def prepare_features(df: pd.DataFrame):
    X = df[FEATURE_COLS].copy()
    X["has_government_partner"] = X["has_government_partner"].astype(int)
    X["revenue_stage"] = df["revenue_stage"].map(REVENUE_MAP).fillna(0)
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    y        = df["impact_tier"].map(TIER_MAP).values
    return X_scaled, y, scaler

def train_classifier(df: pd.DataFrame) -> dict:
    """Train XGBoost classifier on startup impact tier."""
    logger.info("Training XGBoost classifier...")

    df = df.dropna(subset=["impact_tier"]).copy()
    df = df[df["impact_tier"].isin(["Low", "Medium", "High"])].copy()

    X, y, scaler = prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    model = XGBClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        use_label_encoder=False, eval_metric="mlogloss",
        random_state=RANDOM_STATE, verbosity=0,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    labels  = ["Low", "Medium", "High"]
    metrics = evaluate_classifier(y_test, y_pred, y_proba, labels)

    try:
        import shap
        explainer   = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        feature_names = FEATURE_COLS + ["revenue_stage"]
        importance = dict(zip(
            feature_names,
            np.abs(shap_values).mean(axis=(0, 2)).tolist()
            if shap_values.ndim == 3
            else np.abs(shap_values).mean(axis=0).tolist()
        ))
        metrics["shap_importance"] = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)
        )
    except Exception as e:
        logger.warning(f"SHAP failed: {e}")

    # Save artifacts
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/classifier.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("artifacts/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    logger.info("✅ Classifier trained and saved.")
    return {"model": model, "scaler": scaler, "metrics": metrics}

def predict_impact_tier(startup_features: dict) -> dict:
    """Predict impact tier for a single startup."""
    with open("artifacts/classifier.pkl", "rb") as f:
        model = pickle.load(f)
    with open("artifacts/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    df  = pd.DataFrame([startup_features])
    X   = df[FEATURE_COLS].copy()
    X["has_government_partner"] = X["has_government_partner"].astype(int)
    X["revenue_stage"] = df["revenue_stage"].map(REVENUE_MAP).fillna(0)
    X_scaled = scaler.transform(X)

    pred     = model.predict(X_scaled)[0]
    proba    = model.predict_proba(X_scaled)[0]
    tier_inv = {0: "Low", 1: "Medium", 2: "High"}

    return {
        "impact_tier":   tier_inv[pred],
        "confidence":    round(float(proba.max()), 3),
        "probabilities": {"Low": round(proba[0],3), "Medium": round(proba[1],3), "High": round(proba[2],3)}
    }