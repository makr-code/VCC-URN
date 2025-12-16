from fastapi import APIRouter, Depends, HTTPException, Query, status
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
from vcc_urn.core.validation import validate_batch_size, sanitize_log_value
from vcc_urn.core.logging import logger


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
        except ValueError as e:
            # Client error - return 400 with safe error message
            logger.warning("URN generation validation failed", extra={
                "state": sanitize_log_value(payload.state),
                "domain": sanitize_log_value(payload.domain),
                "error": sanitize_log_value(str(e))
            })
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            # Server error - return 500 without exposing internal details
            logger.error("URN generation failed", extra={
                "state": sanitize_log_value(payload.state),
                "domain": sanitize_log_value(payload.domain),
                "error": sanitize_log_value(str(e))
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during URN generation"
            )

    @router.post("/validate", response_model=ValidateResponse)
    def validate(payload: ValidateRequest, svc: URNService = Depends(get_service)):
        r = svc.validate(payload.urn)
        return r

    @router.post("/store", dependencies=[Depends(require_auth)])
    def store(req: StoreRequest, svc: URNService = Depends(get_service)):
        try:
            svc.store_manifest(req.urn, req.manifest)
            return {"status": "ok", "urn": req.urn}
        except ValueError as e:
            # Client error - return 400 with safe error message
            logger.warning("Manifest store validation failed", extra={
                "urn": sanitize_log_value(req.urn),
                "error": sanitize_log_value(str(e))
            })
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            # Server error - return 500 without exposing internal details
            logger.error("Manifest store failed", extra={
                "urn": sanitize_log_value(req.urn),
                "error": sanitize_log_value(str(e))
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during manifest storage"
            )

    @router.get("/resolve")
    def resolve(urn: str = Query(...), svc: URNService = Depends(get_service)):
        try:
            return svc.resolve(urn)
        except ValueError as e:
            # Client error - return 400 with safe error message
            logger.warning("URN resolution validation failed", extra={
                "urn": sanitize_log_value(urn),
                "error": sanitize_log_value(str(e))
            })
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            # Server error - return 500 without exposing internal details
            logger.error("URN resolution failed", extra={
                "urn": sanitize_log_value(urn),
                "error": sanitize_log_value(str(e))
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during URN resolution"
            )

    # Phase 2: Batch resolution endpoint
    @router.post("/resolve/batch", response_model=BatchResolveResponse)
    def resolve_batch_endpoint(req: BatchResolveRequest, svc: URNService = Depends(get_service)):
        """
        Resolve multiple URNs in a single request (Phase 2: Performance optimization)
        Returns manifest for each URN or None if not found
        """
        try:
            # Validate batch size to prevent DoS
            validate_batch_size(req.urns)
            
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
        except ValueError as e:
            # Client error - return 400 with safe error message
            logger.warning("Batch resolution validation failed", extra={
                "batch_size": len(req.urns),
                "error": sanitize_log_value(str(e))
            })
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            # Server error - return 500 without exposing internal details
            logger.error("Batch resolution failed", extra={
                "batch_size": len(req.urns),
                "error": sanitize_log_value(str(e))
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during batch resolution"
            )

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
        except ValueError as e:
            # Client error - return 400 with safe error message
            logger.warning("Search validation failed", extra={
                "uuid": sanitize_log_value(uuid),
                "error": sanitize_log_value(str(e))
            })
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            # Server error - return 500 without exposing internal details
            logger.error("Search failed", extra={
                "uuid": sanitize_log_value(uuid),
                "error": sanitize_log_value(str(e))
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during search"
            )

    return router
