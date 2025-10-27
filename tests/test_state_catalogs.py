import os
import importlib
import json


def test_state_specific_catalogs_override_globals():
    # Save original ENV
    orig_domains = os.environ.get("URN_ALLOWED_DOMAINS")
    orig_types = os.environ.get("URN_ALLOWED_OBJ_TYPES")
    orig_catalogs = os.environ.get("URN_CATALOGS_JSON")
    
    try:
        # Global catalogs (should be overridden where state-specific exist)
        os.environ["URN_ALLOWED_DOMAINS"] = "bau"
        os.environ["URN_ALLOWED_OBJ_TYPES"] = "bescheid"

        # State-specific catalogs
        catalogs = {
            "nrw": {"domains": ["bimschg"], "obj_types": ["anlage"]},
            "by": {"domains": ["bau"], "obj_types": ["bescheid"]},
        }
        os.environ["URN_CATALOGS_JSON"] = json.dumps(catalogs)

        import vcc_urn.config as config
        importlib.reload(config)

        import vcc_urn.urn as urn_mod
        importlib.reload(urn_mod)

        # NRW: only bimschg/anlage allowed
        u_ok_nrw = urn_mod.URN.generate(state="nrw", domain="bimschg", obj_type="anlage", local_aktenzeichen="4711")
        assert urn_mod.URN(u_ok_nrw.as_string())

        import pytest
        with pytest.raises(ValueError):
            urn_mod.URN.generate(state="nrw", domain="bau", obj_type="anlage", local_aktenzeichen="1")

        with pytest.raises(ValueError):
            urn_mod.URN.generate(state="nrw", domain="bimschg", obj_type="bescheid", local_aktenzeichen="1")

        # BY: bau/bescheid allowed
        u_ok_by = urn_mod.URN.generate(state="by", domain="bau", obj_type="bescheid", local_aktenzeichen="99")
        assert urn_mod.URN(u_ok_by.as_string())

        # State without specific mapping should fall back to globals
        u_ok_hh = urn_mod.URN.generate(state="hh", domain="bau", obj_type="bescheid", local_aktenzeichen="X")
        assert urn_mod.URN(u_ok_hh.as_string())

        with pytest.raises(ValueError):
            urn_mod.URN.generate(state="hh", domain="foo", obj_type="bar", local_aktenzeichen="X")
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
        importlib.reload(config)
        importlib.reload(urn_mod)
