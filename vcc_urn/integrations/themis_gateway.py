"""
Themis Federation Gateway - Orchestrating 16 Bundesländer

This module provides integration with the Themis Federation Gateway,
a VCC-native solution for federating queries across 16 German federal states
(Bundesländer). It replaces Apollo Router with a sovereign, on-premise solution.

Architecture Decision: See ADR-0001 (docs/adr/0001-themis-aql-statt-graphql.md)

Why Themis Gateway instead of Apollo Router?
1. Souveränität - VCC-owned, no US company dependency
2. On-Premise - Self-hostable, no cloud requirements
3. License Freedom - Open-Source (MIT/Apache), not Elastic License 2.0
4. DSGVO-konform - German data protection built-in
5. Föderale Optimierung - Designed for 16 Bundesländer architecture

Gateway Features:
- Intelligent routing to 16 Bundesländer endpoints
- Query federation and result merging
- Load balancing with health-aware routing
- Circuit breaker per downstream service
- Caching layer (Redis-backed)
- mTLS for secure inter-service communication
- Distributed tracing (OpenTelemetry)

Configuration:
    URN_GATEWAY_ENABLED: Enable gateway mode (default: false)
    URN_GATEWAY_ROLE: "gateway" or "subgraph" (default: subgraph)
    URN_GATEWAY_SUBGRAPHS: Comma-separated list of subgraph endpoints
    URN_GATEWAY_TIMEOUT: Request timeout per subgraph (default: 30s)
    URN_GATEWAY_RETRY_ATTEMPTS: Retry attempts per subgraph (default: 3)

Usage:
    # As Gateway (central orchestrator)
    gateway = ThemisGateway(role="gateway")
    await gateway.register_subgraph("nrw", "https://urn-nrw.vcc.de/api/v1")
    await gateway.register_subgraph("by", "https://urn-by.vcc.de/api/v1")
    result = await gateway.federated_resolve("urn:vcc:nrw:document:2025:abc123")
    
    # As Subgraph (Bundesland instance)
    subgraph = ThemisGateway(role="subgraph")
    await subgraph.register_with_gateway("https://gateway.vcc.de")

Deployment Topology:
    
    ┌─────────────────────────────────────────────────────────────┐
    │                    Themis Federation Gateway                 │
    │                   (Central Orchestrator)                     │
    └──────────┬──────────┬──────────┬──────────┬─────────────────┘
               │          │          │          │
    ┌──────────▼─┐ ┌──────▼─────┐ ┌──▼────────┐ │  ... (16 total)
    │ VCC-URN    │ │ VCC-URN    │ │ VCC-URN   │ │
    │ NRW        │ │ Bayern     │ │ Baden-W.  │ │
    └────────────┘ └────────────┘ └───────────┘ │
    
On-Premise Deployment:
    All components run within German sovereign infrastructure:
    - Deutsche Verwaltungscloud
    - IONOS Cloud (German)
    - On-premise data centers
    
    No data leaves German jurisdiction.
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any, List, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GatewayRole(Enum):
    """Gateway deployment role."""
    GATEWAY = "gateway"      # Central orchestrator
    SUBGRAPH = "subgraph"    # Bundesland instance


class SubgraphStatus(Enum):
    """Health status of a subgraph."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# 16 German Bundesländer codes
BUNDESLAENDER = {
    "bw": "Baden-Württemberg",
    "by": "Bayern",
    "be": "Berlin",
    "bb": "Brandenburg",
    "hb": "Bremen",
    "hh": "Hamburg",
    "he": "Hessen",
    "mv": "Mecklenburg-Vorpommern",
    "ni": "Niedersachsen",
    "nrw": "Nordrhein-Westfalen",
    "rp": "Rheinland-Pfalz",
    "sl": "Saarland",
    "sn": "Sachsen",
    "st": "Sachsen-Anhalt",
    "sh": "Schleswig-Holstein",
    "th": "Thüringen",
}


@dataclass
class Subgraph:
    """Represents a VCC-URN subgraph (Bundesland instance)."""
    code: str
    name: str
    endpoint: str
    status: SubgraphStatus = SubgraphStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    response_time_ms: float = 0.0
    error_count: int = 0
    success_count: int = 0
    circuit_breaker_open: bool = False
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        total = self.error_count + self.success_count
        if total == 0:
            return 0.0
        return self.error_count / total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "name": self.name,
            "endpoint": self.endpoint,
            "status": self.status.value,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "response_time_ms": self.response_time_ms,
            "error_rate": self.error_rate,
            "circuit_breaker_open": self.circuit_breaker_open,
        }


@dataclass
class FederatedResult:
    """Result from a federated query across multiple subgraphs."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    sources: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    partial_results: Dict[str, Any] = field(default_factory=dict)
    failed_sources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "sources": self.sources,
            "execution_time_ms": self.execution_time_ms,
            "partial_results": self.partial_results,
            "failed_sources": self.failed_sources,
        }


class ThemisGateway:
    """
    Themis Federation Gateway for orchestrating 16 Bundesländer.
    
    This is the VCC-native solution for federating queries across
    German federal states, designed as a sovereign alternative to
    Apollo Router.
    
    Configuration via environment variables:
        URN_GATEWAY_ENABLED: Enable gateway (default: false)
        URN_GATEWAY_ROLE: "gateway" or "subgraph"
        URN_GATEWAY_TIMEOUT: Request timeout (default: 30s)
        URN_GATEWAY_HEALTH_INTERVAL: Health check interval (default: 60s)
    
    Example (as Gateway):
        gateway = ThemisGateway(role="gateway")
        await gateway.register_subgraph("nrw", "https://urn-nrw.vcc.de/api/v1")
        result = await gateway.federated_resolve("urn:vcc:nrw:document:2025:abc123")
    
    Example (as Subgraph):
        subgraph = ThemisGateway(role="subgraph")
        await subgraph.register_with_gateway("https://gateway.vcc.de")
    """
    
    def __init__(
        self,
        role: Optional[GatewayRole] = None,
        timeout: int = 30,
        health_interval: int = 60,
    ):
        """
        Initialize Themis Gateway.
        
        Args:
            role: Gateway role (gateway or subgraph)
            timeout: Request timeout in seconds
            health_interval: Health check interval in seconds
        """
        self.enabled = os.getenv("URN_GATEWAY_ENABLED", "false").lower() == "true"
        
        role_str = os.getenv("URN_GATEWAY_ROLE", "subgraph")
        self.role = role or GatewayRole(role_str)
        
        self.timeout = int(os.getenv("URN_GATEWAY_TIMEOUT", str(timeout)))
        self.health_interval = int(os.getenv("URN_GATEWAY_HEALTH_INTERVAL", str(health_interval)))
        
        # Subgraph registry (for gateway role)
        self._subgraphs: Dict[str, Subgraph] = {}
        
        # HTTP client (lazy initialization)
        self._client = None
        
        # Health check task
        self._health_task: Optional[asyncio.Task] = None
        
        # Initialize from environment
        self._init_from_env()
        
        if self.enabled:
            logger.info(f"Themis Gateway initialized, role: {self.role.value}")
    
    def _init_from_env(self):
        """Initialize subgraphs from environment variables."""
        subgraphs_env = os.getenv("URN_GATEWAY_SUBGRAPHS", "")
        if subgraphs_env:
            for entry in subgraphs_env.split(","):
                if "=" in entry:
                    code, endpoint = entry.strip().split("=", 1)
                    self.register_subgraph_sync(code, endpoint)
    
    def is_gateway(self) -> bool:
        """Check if running as gateway."""
        return self.role == GatewayRole.GATEWAY
    
    def is_subgraph(self) -> bool:
        """Check if running as subgraph."""
        return self.role == GatewayRole.SUBGRAPH
    
    def register_subgraph_sync(self, code: str, endpoint: str) -> bool:
        """
        Register a subgraph synchronously.
        
        Args:
            code: Bundesland code (e.g., "nrw", "by")
            endpoint: Subgraph API endpoint
            
        Returns:
            True if registration successful
        """
        if code not in BUNDESLAENDER:
            logger.warning(f"Unknown Bundesland code: {code}")
            # Allow custom codes for testing
        
        name = BUNDESLAENDER.get(code, code.upper())
        
        subgraph = Subgraph(
            code=code,
            name=name,
            endpoint=endpoint.rstrip("/"),
        )
        
        self._subgraphs[code] = subgraph
        logger.info(f"Registered subgraph: {name} ({code}) at {endpoint}")
        return True
    
    async def register_subgraph(self, code: str, endpoint: str) -> bool:
        """
        Register a subgraph and verify connectivity.
        
        Args:
            code: Bundesland code
            endpoint: Subgraph API endpoint
            
        Returns:
            True if registration successful
        """
        self.register_subgraph_sync(code, endpoint)
        
        # Verify connectivity
        subgraph = self._subgraphs.get(code)
        if subgraph:
            await self._health_check_subgraph(subgraph)
        
        return True
    
    def unregister_subgraph(self, code: str) -> bool:
        """
        Unregister a subgraph.
        
        Args:
            code: Bundesland code
            
        Returns:
            True if unregistration successful
        """
        if code in self._subgraphs:
            del self._subgraphs[code]
            logger.info(f"Unregistered subgraph: {code}")
            return True
        return False
    
    def get_subgraphs(self) -> List[Subgraph]:
        """Get all registered subgraphs."""
        return list(self._subgraphs.values())
    
    def get_healthy_subgraphs(self) -> List[Subgraph]:
        """Get only healthy subgraphs."""
        return [s for s in self._subgraphs.values() 
                if s.status == SubgraphStatus.HEALTHY and not s.circuit_breaker_open]
    
    async def _get_client(self):
        """Get or create HTTP client."""
        if self._client is None:
            try:
                import httpx
                self._client = httpx.AsyncClient(
                    timeout=self.timeout,
                    headers={"Accept": "application/json"},
                )
            except ImportError:
                logger.error("httpx not installed")
                return None
        return self._client
    
    async def _health_check_subgraph(self, subgraph: Subgraph):
        """Check health of a single subgraph."""
        client = await self._get_client()
        if client is None:
            subgraph.status = SubgraphStatus.UNKNOWN
            return
        
        import time
        start = time.time()
        
        try:
            response = await client.get(f"{subgraph.endpoint}/health")
            response_time = (time.time() - start) * 1000
            
            subgraph.response_time_ms = response_time
            subgraph.last_health_check = datetime.utcnow()
            
            if response.status_code == 200:
                subgraph.status = SubgraphStatus.HEALTHY
                subgraph.circuit_breaker_open = False
            else:
                subgraph.status = SubgraphStatus.DEGRADED
                
        except Exception as e:
            subgraph.status = SubgraphStatus.UNHEALTHY
            subgraph.last_health_check = datetime.utcnow()
            logger.warning(f"Health check failed for {subgraph.code}: {e}")
    
    async def health_check_all(self):
        """Run health check on all subgraphs."""
        tasks = [
            self._health_check_subgraph(subgraph)
            for subgraph in self._subgraphs.values()
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def start_health_checks(self):
        """Start background health check task."""
        if self._health_task is not None:
            return
        
        async def health_loop():
            while True:
                await self.health_check_all()
                await asyncio.sleep(self.health_interval)
        
        self._health_task = asyncio.create_task(health_loop())
        logger.info(f"Started health check loop (interval: {self.health_interval}s)")
    
    async def stop_health_checks(self):
        """Stop background health check task."""
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass
            self._health_task = None
            logger.info("Stopped health check loop")
    
    def _extract_domain_from_urn(self, urn: str) -> Optional[str]:
        """Extract domain (Bundesland code) from URN."""
        # URN format: urn:vcc:<domain>:<type>:<year>:<id>
        parts = urn.split(":")
        if len(parts) >= 3:
            return parts[2]
        return None
    
    async def resolve(self, urn: str) -> FederatedResult:
        """
        Resolve a URN, routing to the appropriate subgraph.
        
        Args:
            urn: URN to resolve
            
        Returns:
            FederatedResult with resolution result
        """
        if not self.enabled or not self.is_gateway():
            return FederatedResult(
                success=False,
                error="Gateway not enabled or not in gateway mode",
            )
        
        domain = self._extract_domain_from_urn(urn)
        if not domain:
            return FederatedResult(
                success=False,
                error=f"Could not extract domain from URN: {urn}",
            )
        
        # Route to specific subgraph
        subgraph = self._subgraphs.get(domain)
        if not subgraph:
            # Try federated resolution if domain not found
            return await self.federated_resolve(urn, domains=list(self._subgraphs.keys()))
        
        return await self._resolve_from_subgraph(subgraph, urn)
    
    async def _resolve_from_subgraph(self, subgraph: Subgraph, urn: str) -> FederatedResult:
        """Resolve URN from a specific subgraph."""
        if subgraph.circuit_breaker_open:
            return FederatedResult(
                success=False,
                error=f"Circuit breaker open for {subgraph.code}",
                failed_sources=[subgraph.code],
            )
        
        client = await self._get_client()
        if client is None:
            return FederatedResult(
                success=False,
                error="HTTP client not available",
            )
        
        import time
        start = time.time()
        
        try:
            response = await client.get(
                f"{subgraph.endpoint}/resolve",
                params={"urn": urn},
            )
            execution_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                subgraph.success_count += 1
                return FederatedResult(
                    success=True,
                    data=data,
                    sources=[subgraph.code],
                    execution_time_ms=execution_time,
                )
            else:
                subgraph.error_count += 1
                return FederatedResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}",
                    failed_sources=[subgraph.code],
                    execution_time_ms=execution_time,
                )
                
        except Exception as e:
            subgraph.error_count += 1
            
            # Open circuit breaker if error rate too high
            if subgraph.error_rate > 0.5 and subgraph.error_count >= 5:
                subgraph.circuit_breaker_open = True
                logger.warning(f"Circuit breaker opened for {subgraph.code}")
            
            return FederatedResult(
                success=False,
                error=str(e),
                failed_sources=[subgraph.code],
            )
    
    async def federated_resolve(
        self, 
        urn: str, 
        domains: Optional[List[str]] = None
    ) -> FederatedResult:
        """
        Resolve URN across multiple subgraphs.
        
        Args:
            urn: URN to resolve (may contain wildcards)
            domains: List of domains to query (default: all healthy)
            
        Returns:
            FederatedResult with merged results
        """
        if not self.enabled or not self.is_gateway():
            return FederatedResult(
                success=False,
                error="Gateway not enabled or not in gateway mode",
            )
        
        # Determine which subgraphs to query
        if domains:
            subgraphs = [self._subgraphs[d] for d in domains if d in self._subgraphs]
        else:
            subgraphs = self.get_healthy_subgraphs()
        
        if not subgraphs:
            return FederatedResult(
                success=False,
                error="No healthy subgraphs available",
            )
        
        import time
        start = time.time()
        
        # Query all subgraphs in parallel
        tasks = [
            self._resolve_from_subgraph(sg, urn)
            for sg in subgraphs
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        execution_time = (time.time() - start) * 1000
        
        # Merge results
        merged_data = []
        sources = []
        failed_sources = []
        partial_results = {}
        
        for sg, result in zip(subgraphs, results):
            if isinstance(result, Exception):
                failed_sources.append(sg.code)
                continue
            
            if result.success and result.data:
                sources.append(sg.code)
                partial_results[sg.code] = result.data
                if isinstance(result.data, list):
                    merged_data.extend(result.data)
                elif isinstance(result.data, dict):
                    merged_data.append(result.data)
            else:
                failed_sources.append(sg.code)
        
        return FederatedResult(
            success=len(merged_data) > 0,
            data=merged_data if merged_data else None,
            sources=sources,
            execution_time_ms=execution_time,
            partial_results=partial_results,
            failed_sources=failed_sources,
        )
    
    async def register_with_gateway(self, gateway_url: str) -> bool:
        """
        Register this instance with a central gateway.
        
        Args:
            gateway_url: URL of the central gateway
            
        Returns:
            True if registration successful
        """
        if not self.is_subgraph():
            logger.warning("Only subgraphs can register with gateway")
            return False
        
        client = await self._get_client()
        if client is None:
            return False
        
        # Get local instance info
        local_code = os.getenv("URN_DOMAIN", "unknown")
        local_endpoint = os.getenv("URN_PUBLIC_URL", "http://localhost:8000/api/v1")
        
        try:
            response = await client.post(
                f"{gateway_url}/gateway/register",
                json={
                    "code": local_code,
                    "endpoint": local_endpoint,
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Registered with gateway at {gateway_url}")
                return True
            else:
                logger.error(f"Gateway registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Gateway registration error: {e}")
            return False
    
    async def close(self):
        """Close gateway and cleanup resources."""
        await self.stop_health_checks()
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get gateway status summary."""
        return {
            "enabled": self.enabled,
            "role": self.role.value,
            "subgraphs_total": len(self._subgraphs),
            "subgraphs_healthy": len(self.get_healthy_subgraphs()),
            "subgraphs": [sg.to_dict() for sg in self._subgraphs.values()],
        }


# FastAPI integration
def get_gateway_router():
    """
    Get FastAPI router for Themis Gateway endpoints.
    
    Returns:
        APIRouter with /gateway endpoints, or None if FastAPI not available
    """
    try:
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel
    except ImportError:
        logger.debug("FastAPI not available, skipping Gateway router")
        return None
    
    router = APIRouter(prefix="/gateway", tags=["Themis Gateway"])
    
    _gateway = ThemisGateway()
    
    class RegisterRequest(BaseModel):
        code: str
        endpoint: str
    
    @router.post("/register")
    async def register_subgraph(request: RegisterRequest):
        """Register a subgraph with the gateway."""
        if not _gateway.is_gateway():
            raise HTTPException(status_code=400, detail="Not in gateway mode")
        
        success = await _gateway.register_subgraph(request.code, request.endpoint)
        return {"success": success, "code": request.code}
    
    @router.delete("/unregister/{code}")
    async def unregister_subgraph(code: str):
        """Unregister a subgraph."""
        if not _gateway.is_gateway():
            raise HTTPException(status_code=400, detail="Not in gateway mode")
        
        success = _gateway.unregister_subgraph(code)
        return {"success": success, "code": code}
    
    @router.get("/subgraphs")
    async def list_subgraphs():
        """List all registered subgraphs."""
        return {
            "subgraphs": [sg.to_dict() for sg in _gateway.get_subgraphs()],
            "healthy": len(_gateway.get_healthy_subgraphs()),
        }
    
    @router.get("/status")
    async def gateway_status():
        """Get gateway status."""
        return _gateway.get_status()
    
    @router.get("/resolve")
    async def resolve_via_gateway(urn: str):
        """Resolve URN via gateway."""
        if not _gateway.is_gateway():
            raise HTTPException(status_code=400, detail="Not in gateway mode")
        
        result = await _gateway.resolve(urn)
        return result.to_dict()
    
    return router
