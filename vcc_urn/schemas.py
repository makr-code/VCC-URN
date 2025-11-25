from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class GenerateRequest(BaseModel):
    state: str = Field(..., json_schema_extra={"example": "nrw"})
    domain: str = Field(..., json_schema_extra={"example": "bimschg"})
    obj_type: str = Field(..., json_schema_extra={"example": "anlage"})
    local_aktenzeichen: str = Field(..., json_schema_extra={"example": "4711-0815-K1"})
    uuid: Optional[str] = None
    version: Optional[str] = None
    store: Optional[bool] = True

class GenerateResponse(BaseModel):
    urn: str

class ValidateRequest(BaseModel):
    urn: str

class ValidateResponse(BaseModel):
    valid: bool
    reason: Optional[str] = None
    components: Optional[Dict[str, Any]] = None

class StoreRequest(BaseModel):
    urn: str
    manifest: Dict[str, Any]

class SearchItem(BaseModel):
    urn: str
    manifest: Dict[str, Any]

class SearchResponse(BaseModel):
    count: int
    results: List[SearchItem]

# Phase 2: Batch Resolution
class BatchResolveRequest(BaseModel):
    urns: List[str] = Field(..., json_schema_extra={"example": ["urn:de:nrw:bimschg:anlage:4711:..."]})

class BatchResolveResult(BaseModel):
    urn: str
    manifest: Optional[Dict[str, Any]] = None
    found: bool

class BatchResolveResponse(BaseModel):
    results: List[BatchResolveResult]
    total: int
    found: int


class AdminCatalogsSetRequest(BaseModel):
    catalogs: Dict[str, Dict[str, List[str]]]


class AdminCatalogsResponse(BaseModel):
    global_domains: List[str]
    global_obj_types: List[str]
    state_catalogs: Dict[str, Dict[str, List[str]]]