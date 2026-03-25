import pandas as pd
import numpy as np
import pickle
import logging
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_percentage_error
import lightgbm as lgb
from models.evaluator import evaluate_forecaster
from config.settings import RANDOM_STATE, FORECAST_HORIZON

logger = logging.getLogger(__name__)

FORECAST_TARGETS = ["co2_emissions", "renewable_energy", "pm25_exposure", "gdp_per_capita"]
LAGS = [1, 2, 3, 6]

def create_lag_features(df: pd.DataFrame, target: str) -> pd.DataFrame:
    """Create lag, rolling, and calendar features."""
    df = df.copy().sort_values("year")
    for lag in LAGS:
        df[f"lag_{lag}"] = df[target].shift(lag)
    df["rolling_mean_3"] = df[target].shift(1).rolling(3).mean()
    df["rolling_std_3"]  = df[target].shift(1).rolling(3).std()
    df["trend"]          = range(len(df))
    return df.dropna()

def train_forecasting(df: pd.DataFrame) -> dict:
    """Train LightGBM forecaster for each target indicator."""
    logger.info("Training LightGBM forecaster...")
    models  = {}
    metrics = {}

    for target in FORECAST_TARGETS:
        city_models = {}
        city_metrics= {}

        for city in df["city"].unique():
            city_df = df[df["city"] == city][["year", target]].copy()
            if len(city_df) < 6:
                continue

            featured = create_lag_features(city_df, target)
            feat_cols = [c for c in featured.columns if c not in ["year", target]]
            X = featured[feat_cols].values
            y = featured[target].values

            tscv = TimeSeriesSplit(n_splits=3)
            mape_scores = []

            for train_idx, test_idx in tscv.split(X):
                if len(test_idx) == 0:
                    continue
                m = lgb.LGBMRegressor(
                    n_estimators=200, learning_rate=0.05,
                    num_leaves=15, random_state=RANDOM_STATE, verbose=-1
                )
                m.fit(X[train_idx], y[train_idx])
                preds = m.predict(X[test_idx])
                mape_scores.append(mean_absolute_percentage_error(y[test_idx], preds))

            # Final model
            final = lgb.LGBMRegressor(
                n_estimators=200, learning_rate=0.05,
                num_leaves=15, random_state=RANDOM_STATE, verbose=-1
            )
            final.fit(X, y)
            city_models[city]  = {"model": final, "last_data": city_df}
            city_metrics[city] = {"mape": round(np.mean(mape_scores), 4)}

        models[target]  = city_models
        metrics[target] = city_metrics

    with open("artifacts/lgbm_forecaster.pkl", "wb") as f:
        pickle.dump(models, f)

    logger.info("✅ Forecaster trained and saved.")
    return {"models": models, "metrics": metrics}

def forecast_city(city: str, target: str, periods: int = FORECAST_HORIZON) -> pd.DataFrame:
    """Generate forecast for a city and target indicator."""
    with open("artifacts/lgbm_forecaster.pkl", "rb") as f:
        all_models = pickle.load(f)

    if target not in all_models or city not in all_models[target]:
        return pd.DataFrame()

    model_data = all_models[target][city]
    model      = model_data["model"]
    history    = model_data["last_data"].copy()
    forecasts  = []

    for step in range(periods):
        featured   = create_lag_features(history, target)
        if featured.empty:
            break
        feat_cols  = [c for c in featured.columns if c not in ["year", target]]
        last_feats = featured[feat_cols].iloc[[-1]].values
        pred       = float(model.predict(last_feats)[0])
        next_year  = int(history["year"].max()) + 1
        uncertainty= abs(pred) * 0.05 * (1 + step * 0.1)

        forecasts.append({
            "year":        next_year,
            "forecast":    round(pred, 2),
            "lower_bound": round(pred - 1.96 * uncertainty, 2),
            "upper_bound": round(pred + 1.96 * uncertainty, 2),
        })
        history = pd.concat(
            [history, pd.DataFrame({"year": [next_year], target: [pred]})],
            ignore_index=True
        )

    return pd.DataFrame(forecasts)