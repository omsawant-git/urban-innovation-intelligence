# Urban Innovation Intelligence Platform

An AI-powered urban sustainability and startup intelligence system built for **Leading Cities' AcceliCITY** accelerator program.

🌐 **Live App:** [urban-innovation-intelligence.streamlit.app](https://urban-innovation-intelligence.streamlit.app)

---

## What It Does

Leading Cities evaluates hundreds of startup applications per accelerator cycle — manually, with no systematic data-driven approach. This platform automates three core workflows:

- **Startup impact screening** — XGBoost classifier predicts impact tier (High/Medium/Low) with SHAP explainability
- **City-startup matching** — K-Means clustering profiles cities by sustainability characteristics and surfaces compatible startups
- **Sustainability forecasting** — LightGBM forecasts city-level indicators up to 8 years ahead with confidence intervals
- **Anomaly detection** — Isolation Forest flags cities with unusual sustainability patterns

---

## Results

| Model | Algorithm | Metric | Result |
|---|---|---|---|
| Startup Impact Classifier | XGBoost | F1 / ROC-AUC | 0.91 / 0.938 |
| City Sustainability Clustering | K-Means | Silhouette Score | 0.344, K=5 |
| Indicator Forecaster | LightGBM | TimeSeriesSplit CV | MAPE + RMSE per city |
| Anomaly Detector | Isolation Forest | Anomaly Rate | 13.3% (2/15 cities flagged) |

**Anomalies detected:** Dubai (high CO2 + low renewables) and Mumbai (low CO2 + extreme PM2.5) — both Medium severity.

---

## Data Sources

| Source | Records | Description |
|---|---|---|
| Open-Meteo Historical Weather API | 16,440 | Daily climate per city — temp, precipitation, wind |
| World Bank Sustainability Indicators | 165 | CO2, renewables, GDP, PM2.5, electricity, urban pop (2013–2023) |
| Synthetic Startup Dataset | 500 | AcceliCITY-style application records with 15% label noise |

---

## Architecture

```
Data Layer     →  Open-Meteo API · World Bank baselines · Startup generator
ETL Layer      →  etl/openmeteo.py · etl/worldbank.py · etl/startups.py
Storage Layer  →  PostgreSQL (local) / SQLite (cloud) — 5 normalized tables via SQLAlchemy ORM
ML Layer       →  models/classifier.py · clustering.py · forecasting.py · anomaly.py
Artifact Layer →  artifacts/ — serialized pickle files per model
App Layer      →  Streamlit 6-page dashboard — dark theme, Plotly charts, block navigation
Deployment     →  Streamlit Cloud + SQLite · PostgreSQL 17 locally · GitHub version control
```

### Database Schema (5 normalized tables)

```
cities           — name, country, country_code, lat, lon
city_indicators  — CO2, renewables, GDP, PM2.5, electricity, urban_pop (unique on city_id + year)
city_climate     — temp max/min/mean, precipitation, wind_speed (unique on city_id + date)
startups         — all features, sustainability_score, impact_tier
ml_scores        — audit trail: entity_id, model_name, score, label, cluster, anomaly_flag
```

---

## ML Models

### XGBoost Startup Impact Classifier
Predicts impact tier from 8 features. Configuration: `n_estimators=200`, `max_depth=4`, `learning_rate=0.05`, `subsample=0.8`. SHAP TreeExplainer provides per-feature importance. 15% adjacent label noise in training data ensures realistic generalization rather than artificially perfect scores.

### K-Means City Clustering
Groups 15 global cities into 5 sustainability profiles based on 6 standardized indicators. K=5 confirmed by elbow method. PCA applied for 2D visualization.

| Cluster | Cities |
|---|---|
| Climate Leaders | Amsterdam, Boston, Chicago, Los Angeles, New York, Singapore, Sydney, Tokyo |
| Energy Dependent | Barcelona, London |
| Emerging Sustainers | Mumbai |
| High Growth Cities | Nairobi |
| Developing Hubs | Dubai |

### LightGBM Time-Series Forecaster
Forecasts CO2, renewable energy, PM2.5, and GDP up to 8 years ahead. One model per city per indicator. Lag features: t-1, t-2, t-3, t-6 + 3-period rolling mean/std + trend index. TimeSeriesSplit (3 folds) prevents data leakage. Widening 95% confidence intervals on recursive multi-step forecasts.

### Isolation Forest Anomaly Detector
Trained on city-average CO2, renewables, PM2.5, and GDP. `contamination=0.10`. Correctly identifies Dubai and Mumbai as outliers based on unusual indicator combinations relative to the full city distribution.

---

## Dashboard Pages

| Page | Description |
|---|---|
| City Map & KPIs | Scatter geo map, CO2 trend lines, city comparison bar chart |
| Startup Impact Screener | Donut chart, sector scores, funding vs. sustainability scatter |
| City-Startup Match Engine | Radar chart, cluster overview, per-city recommended startups |
| Sustainability Forecasting | LightGBM forecasts with 95% confidence intervals per city |
| Model Performance | Classification report, elbow plot, cluster assignments, anomaly scores |

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.11 |
| Web App | Streamlit 1.35.0 — custom dark theme, amber accents |
| ML | XGBoost 2.0.3, LightGBM 4.3.0, scikit-learn 1.3.2, SHAP 0.43.0 |
| Data | pandas 2.0.3, numpy 1.26.4, scipy 1.11.4 |
| Visualization | Plotly 5.18.0 — geo, line, bar, radar, scatter, donut |
| Database | PostgreSQL 17 (local) / SQLite (cloud) via SQLAlchemy 2.0 ORM |
| APIs | requests 2.31.0 — Open-Meteo, World Bank |
| Deployment | Streamlit Cloud + `.python-version` 3.11 + `packages.txt` |

---

## Local Setup

```bash
git clone https://github.com/omsawant-git/urban-innovation-intelligence.git
cd urban-innovation-intelligence

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Set up PostgreSQL and configure your connection in `config/settings.py`, then:

```bash
streamlit run streamlit_app.py
```

On first run, the app auto-initializes the database, runs the ETL pipeline, and trains all four models. Subsequent runs load from cached artifacts.

**Cloud deployment** uses SQLite automatically via the `USE_SQLITE=true` environment variable — no PostgreSQL required on Streamlit Cloud.

---

## Project Structure

```
urban-innovation-intelligence/
├── app/                  # Streamlit page modules
├── artifacts/            # Serialized model pickle files
├── config/               # Settings, city list, chart config
├── database/             # SQLAlchemy models and connection
├── etl/                  # Data ingestion: Open-Meteo, World Bank, startups
├── models/               # classifier.py, clustering.py, forecasting.py, anomaly.py
├── scripts/              # train_models.py
├── main.py               # App entry point
├── streamlit_app.py      # Cloud entry point — DB init + model training
└── requirements.txt
```

---

## Author

**Om Sawant** — M.S. Data Science, Worcester Polytechnic Institute  
[omsawant.work@gmail.com](mailto:omsawant.work@gmail.com) · [github.com/omsawant-git](https://github.com/omsawant-git)

Built for **Leading Cities' AcceliCITY Program** · March 2026

---

*© 2026 Om Sawant*
