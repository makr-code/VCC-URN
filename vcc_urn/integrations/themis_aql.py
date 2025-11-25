"""
Themis AQL Client - VCC-native Query Language Integration

This module provides integration with Themis AQL, the VCC-native query language
that replaces GraphQL for federated queries. Themis AQL is specifically designed
for German federal administrative structures.

Architecture Decision: See ADR-0001 (docs/adr/0001-themis-aql-statt-graphql.md)

Why Themis AQL instead of GraphQL?
1. VCC-Ökosystem-Integration - Native with Veritas (Graph-DB), Covina, Clara
2. Föderale Verwaltung - Designed for German federal structures
3. Souveränität & Kontrolle - VCC-owned, no Apollo/US dependency
4. On-Premise & Vendor-Freedom - 100% Open-Source, self-hostable
5. DSGVO & BSI-konform - Compliance built-in

Configuration:
    URN_THEMIS_AQL_ENABLED: Enable Themis AQL integration (default: false)
    URN_THEMIS_AQL_ENDPOINT: Themis AQL server endpoint
    URN_THEMIS_AQL_TIMEOUT: Request timeout in seconds (default: 30)
    URN_THEMIS_AQL_API_KEY: API key for Themis authentication

Example AQL Queries:
    # Resolve URN
    RESOLVE urn:vcc:nrw:document:2025:abc123
    
    # Search by domain
    SEARCH urns WHERE domain = "nrw" AND type = "document"
    
    # Federated resolution across multiple Länder
    FEDERATE RESOLVE urn:vcc:*:document:2025:* FROM [nrw, by, bw] LIMIT 100
    
    # Manifest lookup with filter
    MANIFEST FOR urn:vcc:nrw:document:2025:abc123 WHERE version = "latest"

Usage:
    from vcc_urn.integrations.themis_aql import ThemisAQLClient
    
    client = ThemisAQLClient()
    if client.is_available():
        result = await client.execute("RESOLVE urn:vcc:nrw:document:2025:abc123")
        print(result.data)

On-Premise Deployment:
    Themis AQL is part of the ThemisDB project and can be deployed:
    - As a sidecar container
    - As a separate service in Kubernetes
    - With VCC-URN in the same docker-compose stack
    
    See: https://github.com/VCC/ThemisDB (internal repository)
"""

import os
import logging
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AQLQueryType(Enum):
    """AQL Query types supported by Themis."""
    RESOLVE = "resolve"
    SEARCH = "search"
    FEDERATE = "federate"
    MANIFEST = "manifest"
    VALIDATE = "validate"
    GENERATE = "generate"
    STORE = "store"
    BATCH = "batch"


@dataclass
class AQLResult:
    """Result from Themis AQL query execution."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    query_type: Optional[AQLQueryType] = None
    execution_time_ms: float = 0.0
    federated_sources: List[str] = field(default_factory=list)
    cache_hit: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "query_type": self.query_type.value if self.query_type else None,
            "execution_time_ms": self.execution_time_ms,
            "federated_sources": self.federated_sources,
            "cache_hit": self.cache_hit,
        }


@dataclass
class AQLQuery:
    """Themis AQL Query representation."""
    raw_query: str
    query_type: AQLQueryType
    target_urn: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    federated_sources: List[str] = field(default_factory=list)
    limit: Optional[int] = None
    timeout_ms: Optional[int] = None
    
    @classmethod
    def resolve(cls, urn: str, federated: bool = False, sources: Optional[List[str]] = None) -> "AQLQuery":
        """Create a RESOLVE query."""
        if federated and sources:
            raw = f"FEDERATE RESOLVE {urn} FROM [{', '.join(sources)}]"
            return cls(
                raw_query=raw,
                query_type=AQLQueryType.FEDERATE,
                target_urn=urn,
                federated_sources=sources,
            )
        return cls(
            raw_query=f"RESOLVE {urn}",
            query_type=AQLQueryType.RESOLVE,
            target_urn=urn,
        )
    
    @classmethod
    def search(cls, domain: Optional[str] = None, obj_type: Optional[str] = None, 
               year: Optional[int] = None, limit: int = 100) -> "AQLQuery":
        """Create a SEARCH query."""
        filters = []
        if domain:
            filters.append(f'domain = "{domain}"')
        if obj_type:
            filters.append(f'type = "{obj_type}"')
        if year:
            filters.append(f'year = {year}')
        
        where_clause = " AND ".join(filters) if filters else "1=1"
        raw = f"SEARCH urns WHERE {where_clause} LIMIT {limit}"
        
        return cls(
            raw_query=raw,
            query_type=AQLQueryType.SEARCH,
            filters={"domain": domain, "type": obj_type, "year": year},
            limit=limit,
        )
    
    @classmethod
    def manifest(cls, urn: str, version: str = "latest") -> "AQLQuery":
        """Create a MANIFEST query."""
        return cls(
            raw_query=f'MANIFEST FOR {urn} WHERE version = "{version}"',
            query_type=AQLQueryType.MANIFEST,
            target_urn=urn,
            filters={"version": version},
        )
    
    @classmethod
    def batch_resolve(cls, urns: List[str]) -> "AQLQuery":
        """Create a BATCH RESOLVE query."""
        urn_list = ", ".join([f'"{u}"' for u in urns])
        return cls(
            raw_query=f"BATCH RESOLVE [{urn_list}]",
            query_type=AQLQueryType.BATCH,
        )


class ThemisAQLClient:
    """
    Client for Themis AQL queries.
    
    Themis AQL is the VCC-native query language, designed as a vendor-free,
    on-premise alternative to GraphQL specifically for German federal
    administrative structures.
    
    Configuration via environment variables:
        URN_THEMIS_AQL_ENABLED: Enable Themis AQL (default: false)
        URN_THEMIS_AQL_ENDPOINT: Themis server URL
        URN_THEMIS_AQL_TIMEOUT: Request timeout in seconds
        URN_THEMIS_AQL_API_KEY: API key for authentication
    
    Example:
        client = ThemisAQLClient()
        if client.is_available():
            result = await client.resolve("urn:vcc:nrw:document:2025:abc123")
            print(result.data)
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize Themis AQL client.
        
        Args:
            endpoint: Themis AQL server endpoint (or URN_THEMIS_AQL_ENDPOINT)
            api_key: API key for authentication (or URN_THEMIS_AQL_API_KEY)
            timeout: Request timeout in seconds
        """
        self.enabled = os.getenv("URN_THEMIS_AQL_ENABLED", "false").lower() == "true"
        self.endpoint = endpoint or os.getenv("URN_THEMIS_AQL_ENDPOINT", "http://localhost:8081/aql")
        self.api_key = api_key or os.getenv("URN_THEMIS_AQL_API_KEY")
        self.timeout = int(os.getenv("URN_THEMIS_AQL_TIMEOUT", str(timeout)))
        
        # HTTP client (lazy initialization)
        self._client = None
        
        if self.enabled:
            logger.info(f"Themis AQL client initialized, endpoint: {self.endpoint}")
        else:
            logger.debug("Themis AQL client disabled (URN_THEMIS_AQL_ENABLED=false)")
    
    def is_available(self) -> bool:
        """Check if Themis AQL is enabled and configured."""
        return self.enabled and bool(self.endpoint)
    
    async def _get_client(self):
        """Get or create HTTP client."""
        if self._client is None:
            try:
                import httpx
                self._client = httpx.AsyncClient(
                    timeout=self.timeout,
                    headers={
                        "Content-Type": "application/aql",
                        "Accept": "application/json",
                    }
                )
                if self.api_key:
                    self._client.headers["X-API-Key"] = self.api_key
            except ImportError:
                logger.error("httpx not installed, cannot create Themis AQL client")
                return None
        return self._client
    
    async def execute(self, query: Union[str, AQLQuery]) -> AQLResult:
        """
        Execute a Themis AQL query.
        
        Args:
            query: AQL query string or AQLQuery object
            
        Returns:
            AQLResult with query results
        """
        if not self.is_available():
            return AQLResult(
                success=False,
                error="Themis AQL not enabled or configured",
            )
        
        # Convert string to AQLQuery if needed
        if isinstance(query, str):
            raw_query = query
            query_type = self._detect_query_type(query)
        else:
            raw_query = query.raw_query
            query_type = query.query_type
        
        client = await self._get_client()
        if client is None:
            return AQLResult(
                success=False,
                error="HTTP client not available",
            )
        
        import time
        start_time = time.time()
        
        try:
            response = await client.post(
                self.endpoint,
                content=raw_query,
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                return AQLResult(
                    success=True,
                    data=data.get("result"),
                    query_type=query_type,
                    execution_time_ms=execution_time,
                    federated_sources=data.get("sources", []),
                    cache_hit=data.get("cache_hit", False),
                )
            else:
                return AQLResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}",
                    query_type=query_type,
                    execution_time_ms=execution_time,
                )
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Themis AQL query failed: {e}")
            return AQLResult(
                success=False,
                error=str(e),
                query_type=query_type,
                execution_time_ms=execution_time,
            )
    
    def _detect_query_type(self, query: str) -> AQLQueryType:
        """Detect query type from raw AQL string."""
        query_upper = query.strip().upper()
        if query_upper.startswith("FEDERATE"):
            return AQLQueryType.FEDERATE
        elif query_upper.startswith("RESOLVE"):
            return AQLQueryType.RESOLVE
        elif query_upper.startswith("SEARCH"):
            return AQLQueryType.SEARCH
        elif query_upper.startswith("MANIFEST"):
            return AQLQueryType.MANIFEST
        elif query_upper.startswith("VALIDATE"):
            return AQLQueryType.VALIDATE
        elif query_upper.startswith("GENERATE"):
            return AQLQueryType.GENERATE
        elif query_upper.startswith("STORE"):
            return AQLQueryType.STORE
        elif query_upper.startswith("BATCH"):
            return AQLQueryType.BATCH
        else:
            return AQLQueryType.RESOLVE  # Default
    
    # Convenience methods
    async def resolve(self, urn: str) -> AQLResult:
        """Resolve a single URN."""
        query = AQLQuery.resolve(urn)
        return await self.execute(query)
    
    async def federated_resolve(self, urn: str, sources: List[str]) -> AQLResult:
        """Resolve URN across multiple federation sources."""
        query = AQLQuery.resolve(urn, federated=True, sources=sources)
        return await self.execute(query)
    
    async def search(self, domain: Optional[str] = None, obj_type: Optional[str] = None,
                     year: Optional[int] = None, limit: int = 100) -> AQLResult:
        """Search URNs with filters."""
        query = AQLQuery.search(domain=domain, obj_type=obj_type, year=year, limit=limit)
        return await self.execute(query)
    
    async def get_manifest(self, urn: str, version: str = "latest") -> AQLResult:
        """Get manifest for a URN."""
        query = AQLQuery.manifest(urn, version)
        return await self.execute(query)
    
    async def batch_resolve(self, urns: List[str]) -> AQLResult:
        """Resolve multiple URNs in a single query."""
        query = AQLQuery.batch_resolve(urns)
        return await self.execute(query)
    
    async def health_check(self) -> bool:
        """Check if Themis AQL server is healthy."""
        if not self.is_available():
            return False
        
        client = await self._get_client()
        if client is None:
            return False
        
        try:
            response = await client.get(f"{self.endpoint.rstrip('/aql')}/health")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Themis AQL health check failed: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# FastAPI integration
def get_themis_aql_router():
    """
    Get FastAPI router for Themis AQL endpoints.
    
    This provides a REST wrapper around Themis AQL for clients
    that don't support the native AQL protocol.
    
    Returns:
        APIRouter with /aql endpoints, or None if FastAPI not available
    """
    try:
        from fastapi import APIRouter, HTTPException, Depends
        from pydantic import BaseModel
    except ImportError:
        logger.debug("FastAPI not available, skipping Themis AQL router")
        return None
    
    router = APIRouter(prefix="/aql", tags=["Themis AQL"])
    
    class AQLRequest(BaseModel):
        query: str
        timeout_ms: Optional[int] = None
    
    class AQLResponse(BaseModel):
        success: bool
        data: Optional[Any] = None
        error: Optional[str] = None
        execution_time_ms: float = 0.0
        federated_sources: List[str] = []
        cache_hit: bool = False
    
    _client = ThemisAQLClient()
    
    @router.post("/execute", response_model=AQLResponse)
    async def execute_aql(request: AQLRequest):
        """Execute a Themis AQL query."""
        if not _client.is_available():
            raise HTTPException(
                status_code=503,
                detail="Themis AQL not enabled or configured"
            )
        
        result = await _client.execute(request.query)
        return AQLResponse(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time_ms=result.execution_time_ms,
            federated_sources=result.federated_sources,
            cache_hit=result.cache_hit,
        )
    
    @router.get("/health")
    async def aql_health():
        """Check Themis AQL health."""
        is_healthy = await _client.health_check()
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "enabled": _client.is_available(),
        }
    
    return router
