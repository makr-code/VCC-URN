from fastapi import APIRouter, Depends
from vcc_urn.security import require_role
from vcc_urn import runtime as runtime_tools
from vcc_urn.schemas import AdminCatalogsResponse, AdminCatalogsSetRequest


def get_router() -> APIRouter:
    router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role("admin"))])

    @router.get("/catalogs", response_model=AdminCatalogsResponse)
    def get_catalogs():
        data = runtime_tools.effective_catalogs()
        return AdminCatalogsResponse(**data)

    @router.post("/catalogs/reload", response_model=AdminCatalogsResponse)
    def reload_catalogs():
        data = runtime_tools.reload_settings()
        return AdminCatalogsResponse(**data)

    @router.post("/catalogs/set", response_model=AdminCatalogsResponse)
    def set_catalogs(req: AdminCatalogsSetRequest):
        data = runtime_tools.set_catalogs_runtime(req.catalogs)
        return AdminCatalogsResponse(**data)

    return router
