import re
import uuid
from urllib.parse import quote, unquote
from typing import Optional, Dict
from dataclasses import dataclass

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
    # note: practical validator; a full RFC parser would be more involved
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
        self.components = URNComponents(
            nid=g["nid"],
            state=g["state"],
            domain=g["domain"],
            obj_type=g["obj_type"],
            local_aktenzeichen=unquote(g["local"]),
            uuid=g["uuid"],
            version=g.get("version")
        )

    @classmethod
    def generate(cls, state: str, domain: str, obj_type: str, local_aktenzeichen: str, uuid_str: Optional[str] = None, version: Optional[str] = None, nid: str = "de") -> "URN":
        # normalizations
        state_n = state.strip().lower()
        domain_n = domain.strip().lower()
        obj_type_n = obj_type.strip().lower()
        local_enc = quote(local_aktenzeichen, safe="A-Za-z0-9-_~.!*'();:@&=+$,/")
        if uuid_str:
            u = str(uuid.UUID(uuid_str))
        else:
            u = str(uuid.uuid4())
        urn_str = f"urn:{nid}:{state_n}:{domain_n}:{obj_type_n}:{local_enc}:{u}"
        if version:
            urn_str = f"{urn_str}:{version}"
        return cls(urn_str)

    def as_string(self) -> str:
        return self.raw

    def to_dict(self) -> Dict[str, str]:
        if not self.components:
            raise ValueError("URN not parsed")
        return self.components.__dict__