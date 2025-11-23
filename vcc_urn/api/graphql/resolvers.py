"""
GraphQL resolvers for VCC-URN

⚠️ EXPERIMENTAL / DEPRECATED ⚠️

This GraphQL implementation is EXPERIMENTAL and will be DEPRECATED in favor of Themis AQL.
See: docs/adr/0001-themis-aql-statt-graphql.md

Themis AQL is the VCC-native query language and should be used for all new development.
This GraphQL API is provided for backward compatibility only and may be removed in future versions.

Phase 2: Federation Evolution
"""
import strawberry
from typing import Optional, List
from datetime import datetime

from vcc_urn.service import URNService
from vcc_urn.db import SessionLocal
from vcc_urn.services.federation import resolve_batch as federation_resolve_batch
from vcc_urn.api.graphql.schema import (
    URN,
    URNComponents,
    Manifest,
    ValidationResult,
    GenerateURNInput,
)


def get_service() -> URNService:
    """Get URN service with DB session"""
    db = SessionLocal()
    return URNService(db_session=db)


@strawberry.type
class Query:
    @strawberry.field
    def resolve_urn(self, urn: str) -> Optional[Manifest]:
        """Resolve a URN to its manifest"""
        svc = get_service()
        try:
            result = svc.resolve(urn)
            if result:
                return Manifest(
                    urn=result["urn"],
                    manifest_json=result.get("manifest_json", {}),
                    created_at=datetime.fromisoformat(result["created_at"]) if result.get("created_at") else datetime.now(),
                    updated_at=datetime.fromisoformat(result["updated_at"]) if result.get("updated_at") else datetime.now()
                )
        except Exception:
            return None
        finally:
            svc.db_session.close()
        return None
    
    @strawberry.field
    def validate_urn(self, urn: str) -> ValidationResult:
        """Validate a URN and return components"""
        svc = get_service()
        try:
            result = svc.validate(urn)
            components = None
            if result.components:
                components = URNComponents(
                    nid=result.components.get("nid", ""),
                    state=result.components.get("state", ""),
                    domain=result.components.get("domain", ""),
                    obj_type=result.components.get("obj_type", ""),
                    local_aktenzeichen=result.components.get("local_aktenzeichen", ""),
                    uuid=result.components.get("uuid", ""),
                    version=result.components.get("version")
                )
            return ValidationResult(
                valid=result.valid,
                reason=result.reason,
                components=components
            )
        finally:
            svc.db_session.close()
    
    @strawberry.field
    def search_by_uuid(
        self,
        uuid: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Manifest]:
        """Search manifests by UUID"""
        svc = get_service()
        try:
            results = svc.search_by_uuid(uuid, limit=limit, offset=offset)
            manifests = []
            for item in results:
                manifests.append(Manifest(
                    urn=item["urn"],
                    manifest_json=item["manifest"],
                    created_at=datetime.now(),  # Would need to add to search results
                    updated_at=datetime.now()
                ))
            return manifests
        finally:
            svc.db_session.close()
    
    @strawberry.field
    def resolve_batch(self, urns: List[str]) -> List[Optional[Manifest]]:
        """Batch resolve multiple URNs (Phase 2: Performance)"""
        results_dict = federation_resolve_batch(urns)
        manifests = []
        for urn in urns:
            result = results_dict.get(urn)
            if result:
                manifests.append(Manifest(
                    urn=result["urn"],
                    manifest_json=result.get("manifest_json", {}),
                    created_at=datetime.fromisoformat(result["created_at"]) if result.get("created_at") else datetime.now(),
                    updated_at=datetime.fromisoformat(result["updated_at"]) if result.get("updated_at") else datetime.now()
                ))
            else:
                manifests.append(None)
        return manifests


@strawberry.type
class Mutation:
    @strawberry.mutation
    def generate_urn(self, input: GenerateURNInput) -> URN:
        """Generate a new URN"""
        svc = get_service()
        try:
            urn_str = svc.generate(
                state=input.state,
                domain=input.domain,
                obj_type=input.obj_type,
                local=input.local_aktenzeichen,
                uuid=input.uuid,
                version=input.version,
                store=input.store
            )
            # Parse to get components
            validation = svc.validate(urn_str)
            components = URNComponents(
                nid=validation.components.get("nid", ""),
                state=validation.components.get("state", ""),
                domain=validation.components.get("domain", ""),
                obj_type=validation.components.get("obj_type", ""),
                local_aktenzeichen=validation.components.get("local_aktenzeichen", ""),
                uuid=validation.components.get("uuid", ""),
                version=validation.components.get("version")
            )
            return URN(urn=urn_str, components=components)
        finally:
            svc.db_session.close()
    
    @strawberry.mutation
    def store_manifest(
        self,
        urn: str,
        manifest: strawberry.scalars.JSON
    ) -> Manifest:
        """Store or update a manifest"""
        svc = get_service()
        try:
            svc.store_manifest(urn, manifest)
            result = svc.resolve(urn)
            if result:
                return Manifest(
                    urn=result["urn"],
                    manifest_json=result.get("manifest_json", {}),
                    created_at=datetime.fromisoformat(result["created_at"]) if result.get("created_at") else datetime.now(),
                    updated_at=datetime.fromisoformat(result["updated_at"]) if result.get("updated_at") else datetime.now()
                )
            raise Exception("Failed to store manifest")
        finally:
            svc.db_session.close()


# Create schema with resolvers
schema = strawberry.Schema(query=Query, mutation=Mutation)
