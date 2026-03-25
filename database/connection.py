from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import DATABASE_URL
import logging

logger = logging.getLogger(__name__)
Base   = declarative_base()

def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

def get_session():
    engine  = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def test_connection():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ PostgreSQL connection successful")
        print("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        print(f"❌ Connection failed: {e}")
        return False