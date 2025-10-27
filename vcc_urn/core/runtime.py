import os
import json
import importlib
from typing import Dict, List, Any


def _parse_global_lists() -> tuple[list[str], list[str]]:
    import vcc_urn.config as config
    gd = [d.strip().lower() for d in config.settings.allowed_domains.split(",") if d.strip()]
    gt = [t.strip().lower() for t in config.settings.allowed_obj_types.split(",") if t.strip()]
    return gd, gt


def _parse_state_catalogs() -> Dict[str, Dict[str, List[str]]]:
    import vcc_urn.config as config
    if not config.settings.catalogs_json:
        return {}
    try:
        data = json.loads(config.settings.catalogs_json)
        if not isinstance(data, dict):
            return {}
        out: Dict[str, Dict[str, List[str]]] = {}
        for st, cfg in data.items():
            if not isinstance(cfg, dict):
                continue
            dom = cfg.get("domains")
            typ = cfg.get("obj_types")
            dom_l = [str(x).strip().lower() for x in dom] if isinstance(dom, list) else []
            typ_l = [str(x).strip().lower() for x in typ] if isinstance(typ, list) else []
            out[str(st).lower()] = {"domains": dom_l, "obj_types": typ_l}
        return out
    except Exception:
        return {}


def effective_catalogs() -> Dict[str, Any]:
    gd, gt = _parse_global_lists()
    sc = _parse_state_catalogs()
    return {
        "global_domains": gd,
        "global_obj_types": gt,
        "state_catalogs": sc,
    }


def reload_settings() -> Dict[str, Any]:
    """Reload configuration and dependent modules that import settings by value."""
    import vcc_urn.config as config
    import vcc_urn.core.config as core_config
    import vcc_urn.urn as urn_mod
    import vcc_urn.federation as fed_mod
    import vcc_urn.security as sec_mod

    importlib.reload(core_config)
    importlib.reload(config)
    importlib.reload(urn_mod)
    importlib.reload(fed_mod)
    importlib.reload(sec_mod)

    return effective_catalogs()


def set_catalogs_runtime(catalogs: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
    os.environ["URN_CATALOGS_JSON"] = json.dumps(catalogs)
    return reload_settings()
