from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class GenerateRequest(BaseModel):
    state: str = Field(..., example="nrw")
    domain: str = Field(..., example="bimschg")
    obj_type: str = Field(..., example="anlage")
    local_aktenzeichen: str = Field(..., example="4711-0815-K1")
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