from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool, StaticPool
from vcc_urn.config import settings

# SQLAlchemy setup with connection pooling and security improvements
# Security: Configure connection pool limits to prevent resource exhaustion

# Determine pool configuration based on database type
is_sqlite = settings.db_url.startswith("sqlite")

if is_sqlite:
    # SQLite: Use StaticPool for in-memory/single-threaded access
    # or NullPool for file-based to avoid locking issues
    engine = create_engine(
        settings.db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Disable SQL echo in production
    )
else:
    # PostgreSQL/MySQL: Use QueuePool with reasonable limits
    engine = create_engine(
        settings.db_url,
        poolclass=QueuePool,
        pool_size=10,           # Maximum number of connections to keep persistently
        max_overflow=20,        # Maximum number of connections that can be created beyond pool_size
        pool_timeout=30,        # Timeout for getting a connection from the pool
        pool_recycle=3600,      # Recycle connections after 1 hour to prevent stale connections
        pool_pre_ping=True,     # Test connections before using them
        echo=False,             # Disable SQL echo in production
    )
    
    # Security: Set statement timeout for PostgreSQL to prevent long-running queries
    if "postgresql" in settings.db_url:
        @event.listens_for(engine, "connect")
        def set_postgresql_timeout(dbapi_conn, connection_record):
            """Set statement timeout to 30 seconds for PostgreSQL"""
            cursor = dbapi_conn.cursor()
            cursor.execute("SET statement_timeout = 30000")  # 30 seconds in milliseconds
            cursor.close()

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
