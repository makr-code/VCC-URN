import os
import importlib
import json
from fastapi.testclient import TestClient
from app.main import app


def test_admin_catalogs_reload_and_set():
    # Save original ENV
    orig_domains = os.environ.get("URN_ALLOWED_DOMAINS")
    orig_types = os.environ.get("URN_ALLOWED_OBJ_TYPES")
    orig_catalogs = os.environ.get("URN_CATALOGS_JSON")
    
    try:
        # Prepare environment
        os.environ["URN_ALLOWED_DOMAINS"] = "bau"
        os.environ["URN_ALLOWED_OBJ_TYPES"] = "bescheid"
        os.environ["URN_CATALOGS_JSON"] = json.dumps({"nrw": {"domains": ["bimschg"], "obj_types": ["anlage"]}})

        # Reload settings via admin endpoint
        client = TestClient(app)

        r_reload = client.post("/admin/catalogs/reload")
        assert r_reload.status_code == 200
        body = r_reload.json()
        assert body["state_catalogs"]["nrw"]["domains"] == ["bimschg"]
        assert body["state_catalogs"]["nrw"]["obj_types"] == ["anlage"]

        # Check GET reflects same data
        r_get = client.get("/admin/catalogs")
        assert r_get.status_code == 200
        assert r_get.json()["state_catalogs"]["nrw"]["domains"] == ["bimschg"]

        # Change catalogs at runtime
        new_catalogs = {"nrw": {"domains": ["bau"], "obj_types": ["bescheid"]}}
        r_set = client.post("/admin/catalogs/set", json={"catalogs": new_catalogs})
        assert r_set.status_code == 200
        data = r_set.json()
        assert data["state_catalogs"]["nrw"]["domains"] == ["bau"]
        assert data["state_catalogs"]["nrw"]["obj_types"] == ["bescheid"]

        # After change, a NRW URN with bau/bescheid should be valid
        import vcc_urn.urn as urn_mod
        urn_obj = urn_mod.URN.generate(state="nrw", domain="bau", obj_type="bescheid", local_aktenzeichen="A")
        # Parsing should not raise
        urn_mod.URN(urn_obj.as_string())
    finally:
        # Restore original ENV
        if orig_domains is None:
            os.environ.pop("URN_ALLOWED_DOMAINS", None)
        else:
            os.environ["URN_ALLOWED_DOMAINS"] = orig_domains
        if orig_types is None:
            os.environ.pop("URN_ALLOWED_OBJ_TYPES", None)
        else:
            os.environ["URN_ALLOWED_OBJ_TYPES"] = orig_types
        if orig_catalogs is None:
            os.environ.pop("URN_CATALOGS_JSON", None)
        else:
            os.environ["URN_CATALOGS_JSON"] = orig_catalogs
        # Reload to clear test settings
        import vcc_urn.config as config
        importlib.reload(config)
        import vcc_urn.urn as urn_mod
        importlib.reload(urn_mod)
