from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from vcc_urn.config import settings

# SQLAlchemy setup
engine = create_engine(settings.db_url, connect_args={"check_same_thread": False} if settings.db_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    # create tables (simple approach for a reference implementation)
    from vcc_urn import models  # ensure models are imported so they are registered on Base
    Base.metadata.create_all(bind=engine)
