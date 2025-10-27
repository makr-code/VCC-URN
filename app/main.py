from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from vcc_urn.service import URNService
from vcc_urn.db import init_db, SessionLocal
from vcc_urn.config import settings
from vcc_urn.api.v1.endpoints import get_router as get_v1_router
from vcc_urn.api.admin.endpoints import get_router as get_admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize DB (creates tables)
    init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(title="VCC URN Resolver (OOP)", version="0.1.0", lifespan=lifespan)

# CORS
origins_cfg = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if origins_cfg == ["*"] else origins_cfg,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_service(db=Depends(get_db)):
    # each request gets a service instance with a per-request db session
    return URNService(db_session=db)


app.include_router(get_v1_router())
app.include_router(get_admin_router())


def run():
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# Info and health endpoints (unversioned)
@app.get("/")
def info():
    return {"service": "VCC URN resolver", "nid": settings.nid}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz(svc: URNService = Depends(get_service)):
    ok = svc.db_health()
    if not ok:
        raise HTTPException(status_code=503, detail="database not ready")
    return {"status": "ready"}