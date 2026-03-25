-- Cities master table
CREATE TABLE IF NOT EXISTS cities (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    country         VARCHAR(100) NOT NULL,
    country_code    VARCHAR(10)  NOT NULL,
    latitude        FLOAT        NOT NULL,
    longitude       FLOAT        NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- World Bank indicators per city per year
CREATE TABLE IF NOT EXISTS city_indicators (
    id                  SERIAL PRIMARY KEY,
    city_id             INT REFERENCES cities(id) ON DELETE CASCADE,
    year                INT NOT NULL,
    co2_emissions       FLOAT,
    renewable_energy    FLOAT,
    urban_population    FLOAT,
    gdp_per_capita      FLOAT,
    pm25_exposure       FLOAT,
    access_electricity  FLOAT,
    data_source         VARCHAR(50) DEFAULT 'WorldBank',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, year)
);

-- Climate data from Open-Meteo
CREATE TABLE IF NOT EXISTS city_climate (
    id                  SERIAL PRIMARY KEY,
    city_id             INT REFERENCES cities(id) ON DELETE CASCADE,
    date                DATE NOT NULL,
    temp_max            FLOAT,
    temp_min            FLOAT,
    temp_mean           FLOAT,
    precipitation       FLOAT,
    wind_speed          FLOAT,
    data_source         VARCHAR(50) DEFAULT 'OpenMeteo',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, date)
);

-- Startups table
CREATE TABLE IF NOT EXISTS startups (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    sector              VARCHAR(100),
    country             VARCHAR(100),
    city                VARCHAR(100),
    founding_year       INT,
    team_size           INT,
    funding_usd         FLOAT,
    num_pilots          INT,
    cities_deployed     INT,
    has_government_partner BOOLEAN,
    revenue_stage       VARCHAR(50),
    impact_tier         VARCHAR(20),
    sustainability_score FLOAT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ML model scores and results
CREATE TABLE IF NOT EXISTS ml_scores (
    id                  SERIAL PRIMARY KEY,
    entity_type         VARCHAR(20) NOT NULL,
    entity_id           INT         NOT NULL,
    model_name          VARCHAR(50) NOT NULL,
    score               FLOAT,
    label               VARCHAR(50),
    confidence          FLOAT,
    cluster_id          INT,
    is_anomaly          BOOLEAN DEFAULT FALSE,
    anomaly_severity    VARCHAR(20),
    calculated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);