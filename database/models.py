from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from database.connection import Base

class City(Base):
    __tablename__ = "cities"
    id           = Column(Integer, primary_key=True)
    name         = Column(String(100), nullable=False)
    country      = Column(String(100), nullable=False)
    country_code = Column(String(10),  nullable=False)
    latitude     = Column(Float,       nullable=False)
    longitude    = Column(Float,       nullable=False)
    created_at   = Column(DateTime,    server_default=func.now())

class CityIndicator(Base):
    __tablename__ = "city_indicators"
    __table_args__ = (UniqueConstraint("city_id", "year"),)
    id                 = Column(Integer, primary_key=True)
    city_id            = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"))
    year               = Column(Integer, nullable=False)
    co2_emissions      = Column(Float)
    renewable_energy   = Column(Float)
    urban_population   = Column(Float)
    gdp_per_capita     = Column(Float)
    pm25_exposure      = Column(Float)
    access_electricity = Column(Float)
    data_source        = Column(String(50), default="WorldBank")
    created_at         = Column(DateTime, server_default=func.now())

class CityClimate(Base):
    __tablename__ = "city_climate"
    __table_args__ = (UniqueConstraint("city_id", "date"),)
    id            = Column(Integer, primary_key=True)
    city_id       = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"))
    date          = Column(Date,    nullable=False)
    temp_max      = Column(Float)
    temp_min      = Column(Float)
    temp_mean     = Column(Float)
    precipitation = Column(Float)
    wind_speed    = Column(Float)
    data_source   = Column(String(50), default="OpenMeteo")
    created_at    = Column(DateTime, server_default=func.now())

class Startup(Base):
    __tablename__ = "startups"
    id                     = Column(Integer, primary_key=True)
    name                   = Column(String(200), nullable=False)
    sector                 = Column(String(100))
    country                = Column(String(100))
    city                   = Column(String(100))
    founding_year          = Column(Integer)
    team_size              = Column(Integer)
    funding_usd            = Column(Float)
    num_pilots             = Column(Integer)
    cities_deployed        = Column(Integer)
    has_government_partner = Column(Boolean)
    revenue_stage          = Column(String(50))
    impact_tier            = Column(String(20))
    sustainability_score   = Column(Float)
    created_at             = Column(DateTime, server_default=func.now())

class MLScore(Base):
    __tablename__ = "ml_scores"
    id               = Column(Integer, primary_key=True)
    entity_type      = Column(String(20), nullable=False)
    entity_id        = Column(Integer,    nullable=False)
    model_name       = Column(String(50), nullable=False)
    score            = Column(Float)
    label            = Column(String(50))
    confidence       = Column(Float)
    cluster_id       = Column(Integer)
    is_anomaly       = Column(Boolean, default=False)
    anomaly_severity = Column(String(20))
    calculated_at    = Column(DateTime, server_default=func.now())