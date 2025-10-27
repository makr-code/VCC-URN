from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from vcc_urn.config import settings

# SQLAlchemy setup
engine = create_engine(settings.db_url, connect_args={"check_same_thread": False} if settings.db_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    # create tables (simple approach for a reference implementation)
    # Ensure models are imported and bound to the current Base instance.
    # If models was previously imported against an older db.Base, reload it so
    # model classes pick up the current Base created in this module.
    import importlib
    try:
        from vcc_urn import models as models_mod
        importlib.reload(models_mod)
    except Exception:
        # fallback: import normally
        from vcc_urn import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
