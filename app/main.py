from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from vcc_urn.schemas import GenerateRequest, GenerateResponse, ValidateRequest, ValidateResponse, StoreRequest
from vcc_urn.service import URNService
from vcc_urn.db import init_db
from vcc_urn.config import settings

app = FastAPI(title="VCC URN Resolver (OOP)", version="0.1.0")

@app.on_event("startup")
def on_startup():
    # initialize DB (creates tables)
    init_db()

def get_service():
    # each request gets a service instance (manages session internally)
    return URNService()

@app.get("/")
def info():
    return {"service": "VCC URN resolver", "nid": settings.nid}

@app.post("/generate", response_model=GenerateResponse)
def generate(payload: GenerateRequest, svc: URNService = Depends(get_service)):
    try:
        urn = svc.generate(state=payload.state, domain=payload.domain, obj_type=payload.obj_type, local=payload.local_aktenzeichen, uuid=payload.uuid, version=payload.version, store=payload.store)
        return GenerateResponse(urn=urn)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/validate", response_model=ValidateResponse)
def validate(payload: ValidateRequest, svc: URNService = Depends(get_service)):
    r = svc.validate(payload.urn)
    return JSONResponse(content=r)

@app.post("/store")
def store(req: StoreRequest, svc: URNService = Depends(get_service)):
    try:
        svc.store_manifest(req.urn, req.manifest)
        return {"status": "ok", "urn": req.urn}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/resolve")
def resolve(urn: str = Query(...), svc: URNService = Depends(get_service)):
    try:
        return svc.resolve(urn)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/search")
def search(uuid: str = Query(...), svc: URNService = Depends(get_service)):
    try:
        return {"count": len(svc.search_by_uuid(uuid)), "results": svc.search_by_uuid(uuid)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def run():
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)