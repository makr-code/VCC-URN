from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from vcc_urn import models
from vcc_urn.urn import URN
import json

class ManifestRepository:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_schema(self):
        # Attempt to (re)create tables if missing
        try:
            from vcc_urn import db as db_mod
            db_mod.init_db()
            try:
                if hasattr(self.db, "close"):
                    try:
                        self.db.close()
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                self.db = db_mod.SessionLocal()
            except Exception:
                pass
        except Exception:
            pass

    def get_by_urn(self, urn: str) -> Optional[Dict[str, Any]]:
        try:
            obj = self.db.query(models.Manifest).filter(models.Manifest.urn == urn).one_or_none()
        except Exception as e:
            if "no such table" in str(e).lower():
                self._ensure_schema()
                obj = self.db.query(models.Manifest).filter(models.Manifest.urn == urn).one_or_none()
            else:
                raise
        if not obj:
            return None
        return {"urn": obj.urn, "manifest": json.loads(obj.manifest_json)}

    def get_by_uuid(self, uuid_str: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        q = self.db.query(models.Manifest).filter(models.Manifest.uuid == uuid_str).order_by(models.Manifest.created_at.desc())
        if limit is not None:
            q = q.limit(limit)
        if offset:
            q = q.offset(offset)
        rows = q.all()
        return [{"urn": r.urn, "manifest": json.loads(r.manifest_json)} for r in rows]

    def upsert(self, urn: str, manifest: Dict[str, Any]):
        m_json = json.dumps(manifest, ensure_ascii=False)
        urn_obj = URN(urn)
        c = urn_obj.components
        try:
            existing = (
                self.db.query(models.Manifest)
                .filter(models.Manifest.urn == urn)
                .one_or_none()
            )
            if existing:
                existing.manifest_json = m_json
                existing.nid = c.nid
                existing.state = manifest.get("country", c.state)
                existing.domain = manifest.get("domain", c.domain)
                existing.obj_type = manifest.get("type", c.obj_type)
                existing.local_aktenzeichen = manifest.get("local_aktenzeichen", c.local_aktenzeichen)
                existing.uuid = manifest.get("uuid", c.uuid)
                existing.version = c.version
            else:
                new = models.Manifest(
                    urn=urn,
                    nid=c.nid,
                    state=manifest.get("country", c.state),
                    domain=manifest.get("domain", c.domain),
                    obj_type=manifest.get("type", c.obj_type),
                    local_aktenzeichen=manifest.get("local_aktenzeichen", c.local_aktenzeichen),
                    uuid=manifest.get("uuid", c.uuid),
                    version=c.version,
                    manifest_json=m_json,
                )
                self.db.add(new)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            if "no such table" in str(e).lower():
                self._ensure_schema()
                existing = (
                    self.db.query(models.Manifest)
                    .filter(models.Manifest.urn == urn)
                    .one_or_none()
                )
                if existing:
                    existing.manifest_json = m_json
                    existing.nid = c.nid
                    existing.state = manifest.get("country", c.state)
                    existing.domain = manifest.get("domain", c.domain)
                    existing.obj_type = manifest.get("type", c.obj_type)
                    existing.local_aktenzeichen = manifest.get("local_aktenzeichen", c.local_aktenzeichen)
                    existing.uuid = manifest.get("uuid", c.uuid)
                    existing.version = c.version
                else:
                    new = models.Manifest(
                        urn=urn,
                        nid=c.nid,
                        state=manifest.get("country", c.state),
                        domain=manifest.get("domain", c.domain),
                        obj_type=manifest.get("type", c.obj_type),
                        local_aktenzeichen=manifest.get("local_aktenzeichen", c.local_aktenzeichen),
                        uuid=manifest.get("uuid", c.uuid),
                        version=c.version,
                        manifest_json=m_json,
                    )
                    self.db.add(new)
                self.db.commit()
            else:
                raise

    def health_check(self) -> bool:
        try:
            self.db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
