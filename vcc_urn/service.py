from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from vcc_urn.repository import ManifestRepository
from vcc_urn.urn import URN
from vcc_urn.db import SessionLocal

class URNService:
    def __init__(self, db_session: Optional[Session] = None):
        self._external_session = db_session
        self._managed_session = None

    def _get_session(self):
        if self._external_session:
            return self._external_session
        if not self._managed_session:
            self._managed_session = SessionLocal()
        return self._managed_session

    def generate(self, state: str, domain: str, obj_type: str, local: str, uuid: Optional[str] = None, version: Optional[str] = None, store: bool = True) -> str:
        urn_obj = URN.generate(state=state, domain=domain, obj_type=obj_type, local_aktenzeichen=local, uuid_str=uuid, version=version)
        urn_str = urn_obj.as_string()
        if store:
            repo = ManifestRepository(self._get_session())
            manifest = {
                "@id": urn_str,
                "urn": urn_str,
                "type": obj_type,
                "domain": domain,
                "country": state,
                "local_aktenzeichen": local,
                "uuid": urn_obj.components.uuid,
                "label": f"{obj_type} {local} ({state.upper()})"
            }
            repo.upsert(urn_str, manifest)
        return urn_str

    def resolve(self, urn: str) -> Dict[str, Any]:
        # validate / parse
        urn_obj = URN(urn)
        repo = ManifestRepository(self._get_session())
        manifest = repo.get_by_urn(urn)
        if manifest:
            return manifest["manifest"]
        # fallback: generate minimal manifest
        c = urn_obj.to_dict()
        return {
            "@id": urn,
            "urn": urn,
            "type": c["obj_type"],
            "domain": c["domain"],
            "country": c["state"],
            "local_aktenzeichen": c["local_aktenzeichen"],
                "uuid": c["uuid"],
                "label": f"{c['obj_type']} {c['local_aktenzeichen']} ({c['state'].upper()})"
        }

    def validate(self, urn: str) -> Dict[str, Any]:
        try:
            urn_obj = URN(urn)
            return {"valid": True, "components": urn_obj.to_dict()}
        except Exception as e:
            return {"valid": False, "reason": str(e)}

    def store_manifest(self, urn: str, manifest: Dict[str, Any]):
        # ensure urn parses
        URN(urn)
        repo = ManifestRepository(self._get_session())
        repo.upsert(urn, manifest)

    def search_by_uuid(self, uuid_str: str) -> List[Dict[str, Any]]:
        repo = ManifestRepository(self._get_session())
        return repo.get_by_uuid(uuid_str)
