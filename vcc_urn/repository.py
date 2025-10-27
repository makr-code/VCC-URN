from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from vcc_urn import models
import json

class ManifestRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_urn(self, urn: str) -> Optional[Dict[str, Any]]:
        obj = self.db.query(models.Manifest).filter(models.Manifest.urn == urn).one_or_none()
        if not obj:
            return None
        return {"urn": obj.urn, "manifest": json.loads(obj.manifest_json)}

    def get_by_uuid(self, uuid_str: str) -> List[Dict[str, Any]]:
        rows = self.db.query(models.Manifest).filter(models.Manifest.uuid == uuid_str).all()
        return [{"urn": r.urn, "manifest": json.loads(r.manifest_json)} for r in rows]

    def upsert(self, urn: str, manifest: Dict[str, Any]):
        m_json = json.dumps(manifest, ensure_ascii=False)
        existing = self.db.query(models.Manifest).filter(models.Manifest.urn == urn).one_or_none()
        if existing:
            existing.manifest_json = m_json
            existing.updated_at = manifest.get("updated_at")
        else:
            # extract basic fields defensively
            parts = urn.split(":")
            version = None
            if len(parts) >= 8:
                version = parts[7]
            new = models.Manifest(
                urn=urn,
                nid=manifest.get("nid", "de"),
                state=manifest.get("country", parts[2] if len(parts) > 2 else ""),
                domain=manifest.get("domain", parts[3] if len(parts) > 3 else ""),
                obj_type=manifest.get("type", parts[4] if len(parts) > 4 else ""),
                local_aktenzeichen=manifest.get("local_aktenzeichen", ""),
                uuid=manifest.get("uuid", parts[5] if len(parts) > 5 else ""),
                version=version,
                manifest_json=m_json
            )
            self.db.add(new)
        self.db.commit()