from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from vcc_urn.service import URNService
from vcc_urn.db import init_db, SessionLocal
from vcc_urn.config import settings
from vcc_urn.api.v1.endpoints import get_router as get_v1_router
from vcc_urn.api.admin.endpoints import get_router as get_admin_router
from vcc_urn.api.admin.dashboard import get_dashboard_router  # Phase 2b
from vcc_urn.core.logging import logger

# Phase 2: GraphQL (optional - import only if needed)
# GraphQL API available alongside REST and Themis AQL
try:
    from strawberry.fastapi import GraphQLRouter
    from vcc_urn.api.graphql.resolvers import schema as graphql_schema
    GRAPHQL_AVAILABLE = True
except ImportError:
    GRAPHQL_AVAILABLE = False
    logger.warning("GraphQL not available - install with: pip install strawberry-graphql[fastapi]")


# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize DB (creates tables)
    logger.info("Starting VCC-URN Resolver", nid=settings.nid, log_level=settings.log_level)
    init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown: cleanup if needed
    logger.info("Shutting down VCC-URN Resolver")


app = FastAPI(title="VCC URN Resolver (OOP)", version="0.1.0", lifespan=lifespan)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
origins_cfg = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if origins_cfg == ["*"] else origins_cfg,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics (Phase 1)
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

logger.info("Prometheus metrics enabled at /metrics")


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

# Phase 2b: Admin Dashboard for peer monitoring
app.include_router(get_dashboard_router())
logger.info("Admin Dashboard enabled at /admin/dashboard")

# Phase 2: GraphQL endpoint (optional)
# GraphQL API available alongside REST and Themis AQL
if GRAPHQL_AVAILABLE:
    graphql_app = GraphQLRouter(graphql_schema)
    app.include_router(graphql_app, prefix="/graphql")
    logger.info("GraphQL API enabled at /graphql")
else:
    logger.info("GraphQL API disabled (dependency not installed)")


def run():
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


# Info and health endpoints (unversioned)
@app.get("/")
@limiter.limit("100/minute")
async def info(request: Request):
    apis = ["REST /api/v1"]
    if GRAPHQL_AVAILABLE:
        apis.append("GraphQL /graphql")
    return {"service": "VCC URN resolver", "nid": settings.nid, "apis": apis}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz(svc: URNService = Depends(get_service)):
    ok = svc.db_health()
    if not ok:
        logger.error("Database health check failed")
        raise HTTPException(status_code=503, detail="database not ready")
    return {"status": "ready"}