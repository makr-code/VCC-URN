from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime, timezone
from vcc_urn.db import Base

class Manifest(Base):
    __tablename__ = "manifests"

    urn = Column(String(512), primary_key=True, index=True, nullable=False)
    nid = Column(String(32), nullable=False, default="de")
    state = Column(String(10), index=True, nullable=False)
    domain = Column(String(64), nullable=False)
    obj_type = Column(String(64), nullable=False)
    local_aktenzeichen = Column(String(512), nullable=True)
    uuid = Column(String(36), index=True, nullable=False)
    version = Column(String(64), nullable=True)
    manifest_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
