import os
import importlib

def test_catalogs_enforced_when_configured():
    # Save original ENV
    orig_domains = os.environ.get("URN_ALLOWED_DOMAINS")
    orig_types = os.environ.get("URN_ALLOWED_OBJ_TYPES")
    
    try:
        # Configure catalogs
        os.environ["URN_ALLOWED_DOMAINS"] = "bimschg,bau"
        os.environ["URN_ALLOWED_OBJ_TYPES"] = "anlage,bescheid"

        import vcc_urn.config as config
        importlib.reload(config)

        import vcc_urn.urn as urn_mod
        importlib.reload(urn_mod)

        # Allowed
        u = urn_mod.URN.generate(state="nrw", domain="bimschg", obj_type="anlage", local_aktenzeichen="4711")
        assert urn_mod.URN(u.as_string())  # should parse

        # Not allowed domain
        import pytest
        with pytest.raises(ValueError):
            urn_mod.URN.generate(state="nrw", domain="xyz", obj_type="anlage", local_aktenzeichen="1")

        # Not allowed type
        with pytest.raises(ValueError):
            urn_mod.URN.generate(state="nrw", domain="bimschg", obj_type="unbekannt", local_aktenzeichen="1")
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
        # Reload to clear test settings
        importlib.reload(config)
        importlib.reload(urn_mod)
