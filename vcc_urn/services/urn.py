import re
import uuid
from urllib.parse import quote, unquote
from typing import Optional, Dict
from dataclasses import dataclass
from vcc_urn.config import settings
import json
from vcc_urn import runtime as runtime_mod

# Encapsulate URN logic in OOP
@dataclass
class URNComponents:
    nid: str
    state: str
    domain: str
    obj_type: str
    local_aktenzeichen: str
    uuid: str
    version: Optional[str] = None

class URN:
    """
    URN utility / value object for scheme:
    urn:de:<state>:<domain>:<objtype>:<localAktenzeichen>:<uuid>[:<version>]
    """
    _pattern = re.compile(
        r"^urn:(?P<nid>[a-z0-9\-]{1,32}):(?P<state>[a-z]{2,3}):(?P<domain>[a-z0-9\-]+):"
        r"(?P<obj_type>[a-z0-9\-]+):(?P<local>[A-Za-z0-9%\-._~!*'();:@&=+$,\/]+):"
        r"(?P<uuid>[0-9a-fA-F\-]{36})(?::(?P<version>v[0-9A-Za-z\-.]+))?$"
    )

    def __init__(self, raw: str):
        self.raw = raw
        self.components: Optional[URNComponents] = None
        self._parse()

    def _parse(self):
        m = self._pattern.match(self.raw)
        if not m:
            raise ValueError(f"URN does not match expected pattern: {self.raw}")
        g = m.groupdict()
        if settings.nid and g["nid"] != settings.nid:
            raise ValueError(f"Unexpected NID '{g['nid']}', expected '{settings.nid}'")
        if settings.state_pattern and not re.match(settings.state_pattern, g["state"]):
            raise ValueError(f"State '{g['state']}' does not match pattern {settings.state_pattern}")
        try:
            cats = runtime_mod.effective_catalogs()
            state_l = g["state"].lower()
            state_catalogs = cats.get("state_catalogs", {}) or {}
            state_cfg = state_catalogs.get(state_l, {})
            state_domains = state_cfg.get("domains") if isinstance(state_cfg.get("domains"), list) else None
            state_types = state_cfg.get("obj_types") if isinstance(state_cfg.get("obj_types"), list) else None
            global_domains = cats.get("global_domains") or []
            global_types = cats.get("global_obj_types") or []
            eff_domains = state_domains if state_domains is not None else (global_domains if global_domains else None)
            eff_types = state_types if state_types is not None else (global_types if global_types else None)
        except Exception:
            state_l = g["state"].lower()
            state_domains = None
            state_types = None
            try:
                if settings.catalogs_json:
                    cfgs = json.loads(settings.catalogs_json)
                    st_cfg = cfgs.get(state_l) if isinstance(cfgs, dict) else None
                    if isinstance(st_cfg, dict):
                        d = st_cfg.get("domains")
                        t = st_cfg.get("obj_types")
                        if isinstance(d, list):
                            state_domains = [str(x).strip().lower() for x in d if str(x).strip()]
                        if isinstance(t, list):
                            state_types = [str(x).strip().lower() for x in t if str(x).strip()]
            except Exception:
                pass
            global_domains = [d.strip().lower() for d in settings.allowed_domains.split(",") if d.strip()]
            global_types = [t.strip().lower() for t in settings.allowed_obj_types.split(",") if t.strip()]
            eff_domains = state_domains if state_domains else (global_domains if global_domains else None)
            eff_types = state_types if state_types else (global_types if global_types else None)

        if eff_domains is not None and g["domain"].lower() not in eff_domains:
            raise ValueError(f"Domain '{g['domain']}' not in allowed catalog")
        if eff_types is not None and g["obj_type"].lower() not in eff_types:
            raise ValueError(f"Object type '{g['obj_type']}' not in allowed catalog")
        self.components = URNComponents(
            nid=g["nid"],
            state=g["state"],
            domain=g["domain"],
            obj_type=g["obj_type"],
            local_aktenzeichen=unquote(g["local"]),
            uuid=g["uuid"],
            version=g.get("version"),
        )

    @classmethod
    def generate(
        cls,
        state: str,
        domain: str,
        obj_type: str,
        local_aktenzeichen: str,
        uuid_str: Optional[str] = None,
        version: Optional[str] = None,
        nid: Optional[str] = None,
    ) -> "URN":
        state_n = state.strip().lower()
        domain_n = domain.strip().lower()
        obj_type_n = obj_type.strip().lower()
        local_enc = quote(local_aktenzeichen, safe="A-Za-z0-9-_~.!*'();:@&=+$,/")
        nid_eff = (nid or settings.nid or "de").strip().lower()
        try:
            cats = runtime_mod.effective_catalogs()
            state_catalogs = cats.get("state_catalogs", {}) or {}
            state_cfg = state_catalogs.get(state_n, {})
            state_domains = state_cfg.get("domains") if isinstance(state_cfg.get("domains"), list) else None
            state_types = state_cfg.get("obj_types") if isinstance(state_cfg.get("obj_types"), list) else None
            global_domains = cats.get("global_domains") or []
            global_types = cats.get("global_obj_types") or []
            eff_domains = state_domains if state_domains is not None else (global_domains if global_domains else None)
            eff_types = state_types if state_types is not None else (global_types if global_types else None)
        except Exception:
            eff_domains = [d.strip().lower() for d in settings.allowed_domains.split(",") if d.strip()] or None
            eff_types = [t.strip().lower() for t in settings.allowed_obj_types.split(",") if t.strip()] or None

        if eff_domains is not None and domain_n not in eff_domains:
            raise ValueError(f"Domain '{domain}' not allowed for state '{state}'")
        if eff_types is not None and obj_type_n not in eff_types:
            raise ValueError(f"Object type '{obj_type}' not allowed for state '{state}'")

        if uuid_str:
            u = str(uuid.UUID(uuid_str))
        else:
            u = str(uuid.uuid4())
        urn_str = f"urn:{nid_eff}:{state_n}:{domain_n}:{obj_type_n}:{local_enc}:{u}"
        if version:
            urn_str = f"{urn_str}:{version}"
        return cls(urn_str)

    def as_string(self) -> str:
        return self.raw

    def to_dict(self) -> Dict[str, str]:
        if not self.components:
            raise ValueError("URN not parsed")
        return self.components.__dict__
