from fastapi import APIRouter, Depends, HTTPException, Query
from vcc_urn.schemas import (
    GenerateRequest,
    GenerateResponse,
    ValidateRequest,
    ValidateResponse,
    StoreRequest,
    SearchResponse,
    BatchResolveRequest,
    BatchResolveResponse,
    BatchResolveResult,
)
from vcc_urn.service import URNService
from vcc_urn.db import SessionLocal
from vcc_urn.security import require_auth
from vcc_urn.services.federation import resolve_batch


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_service(db=Depends(get_db)):
    return URNService(db_session=db)


def get_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["urn"])

    @router.post("/generate", response_model=GenerateResponse, dependencies=[Depends(require_auth)])
    def generate(payload: GenerateRequest, svc: URNService = Depends(get_service)):
        try:
            urn = svc.generate(
                state=payload.state,
                domain=payload.domain,
                obj_type=payload.obj_type,
                local=payload.local_aktenzeichen,
                uuid=payload.uuid,
                version=payload.version,
                store=payload.store,
            )
            return GenerateResponse(urn=urn)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/validate", response_model=ValidateResponse)
    def validate(payload: ValidateRequest, svc: URNService = Depends(get_service)):
        r = svc.validate(payload.urn)
        return r

    @router.post("/store", dependencies=[Depends(require_auth)])
    def store(req: StoreRequest, svc: URNService = Depends(get_service)):
        try:
            svc.store_manifest(req.urn, req.manifest)
            return {"status": "ok", "urn": req.urn}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/resolve")
    def resolve(urn: str = Query(...), svc: URNService = Depends(get_service)):
        try:
            return svc.resolve(urn)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Phase 2: Batch resolution endpoint
    @router.post("/resolve/batch", response_model=BatchResolveResponse)
    def resolve_batch_endpoint(req: BatchResolveRequest, svc: URNService = Depends(get_service)):
        """
        Resolve multiple URNs in a single request (Phase 2: Performance optimization)
        Returns manifest for each URN or None if not found
        """
        try:
            results_dict = resolve_batch(req.urns)
            results = []
            found_count = 0
            
            for urn in req.urns:
                manifest = results_dict.get(urn)
                is_found = manifest is not None
                if is_found:
                    found_count += 1
                results.append(BatchResolveResult(
                    urn=urn,
                    manifest=manifest,
                    found=is_found
                ))
            
            return BatchResolveResponse(
                results=results,
                total=len(req.urns),
                found=found_count
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/search", response_model=SearchResponse)
    def search(
        uuid: str = Query(...),
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        svc: URNService = Depends(get_service),
    ):
        try:
            results = svc.search_by_uuid(uuid, limit=limit, offset=offset)
            return {"count": len(results), "results": results}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router
