import os
import pathlib
import importlib
import shutil
import pytest

# Ensure a clean SQLite file DB per test session
@pytest.fixture(scope="session", autouse=True)
def test_db_env():
    db_path = pathlib.Path.cwd() / "test_urn.db"
    if db_path.exists():
        try:
            db_path.unlink()
        except Exception:
            # fallback remove via shutil on Windows lock
            shutil.rmtree(str(db_path), ignore_errors=True)
    os.environ["URN_DB_URL"] = f"sqlite:///{db_path}"
    # Clear catalog ENV to avoid cross-test pollution
    os.environ.pop("URN_ALLOWED_DOMAINS", None)
    os.environ.pop("URN_ALLOWED_OBJ_TYPES", None)
    os.environ.pop("URN_CATALOGS_JSON", None)
    # Reload settings and db after setting env
    import vcc_urn.config as config
    importlib.reload(config)
    import vcc_urn.db as db
    importlib.reload(db)
    import vcc_urn.urn as urn_mod
    importlib.reload(urn_mod)
    # Initialize schema
    db.init_db()
    yield
    # teardown not strictly necessary
