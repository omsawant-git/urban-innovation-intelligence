import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, f1_score, classification_report,
    mean_absolute_percentage_error, mean_squared_error,
    silhouette_score
)
import logging

logger = logging.getLogger(__name__)

def evaluate_classifier(y_true, y_pred, y_proba=None, labels=None):
    """Evaluate classification model."""
    report = classification_report(y_true, y_pred, target_names=labels, output_dict=True)
    result = {
        "classification_report": report,
        "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
    }
    if y_proba is not None:
        try:
            result["roc_auc"] = roc_auc_score(
                y_true, y_proba, multi_class="ovr", average="weighted"
            )
        except Exception as e:
            logger.warning(f"ROC-AUC failed: {e}")
    logger.info(f"Classifier — F1: {result['f1_weighted']:.3f} | ROC-AUC: {result.get('roc_auc', 'N/A')}")
    return result

def evaluate_forecaster(y_true, y_pred):
    """Evaluate forecasting model."""
    mape = mean_absolute_percentage_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    result = {"mape": round(mape, 4), "rmse": round(rmse, 4)}
    logger.info(f"Forecaster — MAPE: {mape:.3f} | RMSE: {rmse:.3f}")
    return result

def evaluate_clustering(X, labels):
    """Evaluate clustering model."""
    score = silhouette_score(X, labels)
    unique, counts = np.unique(labels, return_counts=True)
    result = {
        "silhouette_score": round(score, 4),
        "cluster_distribution": dict(zip(unique.tolist(), counts.tolist()))
    }
    logger.info(f"Clustering — Silhouette: {score:.3f}")
    return result

def evaluate_anomaly(y_true, y_pred):
    """Evaluate anomaly detection."""
    anomaly_rate = y_pred.sum() / len(y_pred)
    result = {
        "anomaly_rate":  round(anomaly_rate, 4),
        "total_anomalies": int(y_pred.sum()),
        "total_records":   len(y_pred),
    }
    logger.info(f"Anomaly — Rate: {anomaly_rate:.3f} | Count: {int(y_pred.sum())}")
    return result