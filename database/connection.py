from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging

logger = logging.getLogger(__name__)
Base   = declarative_base()

def get_database_url():
    use_sqlite = os.getenv("USE_SQLITE", "false").lower() == "true"
    if use_sqlite:
        return "sqlite:///./sustainability.db"
    from config.settings import DATABASE_URL
    return DATABASE_URL

def get_engine():
    url = get_database_url()
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url, pool_pre_ping=True, echo=False)

def get_session():
    engine  = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def test_connection():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        print(f"❌ Connection failed: {e}")
        return False