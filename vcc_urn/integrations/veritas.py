"""
Veritas Graph-DB Integration - URN Storage in Graph Database

This module provides integration with Veritas, the VCC Graph-DB component,
for storing and retrieving URNs as graph nodes and relationships.

VCC Ecosystem Integration:
    VCC-URN ←→ Veritas (Graph-DB)
    
    URNs are stored as:
    - Node properties on document/entity nodes
    - Dedicated URN nodes for cross-references
    - Proxy nodes for external federation references

Why Veritas (not Neo4j Cloud/Aura)?
1. On-Premise - Self-hostable, no cloud dependencies
2. Souveränität - VCC-owned and operated
3. DSGVO-konform - German data protection compliance
4. Integration - Native VCC ecosystem integration
5. License Freedom - Open-Source (MIT/Apache)

Graph Model:
    
    (:Document {urn: "urn:vcc:nrw:document:2025:abc123"})
        -[:HAS_MANIFEST]->
    (:Manifest {version: "1.0", created_at: "..."})
        -[:REFERENCES]->
    (:ExternalURN {urn: "urn:vcc:by:document:2024:xyz789", federated: true})

Configuration:
    URN_VERITAS_ENABLED: Enable Veritas integration (default: false)
    URN_VERITAS_ENDPOINT: Veritas API endpoint
    URN_VERITAS_API_KEY: API key for authentication
    URN_VERITAS_DATABASE: Database name (default: vcc_urn)

Usage:
    client = VeritasClient()
    if client.is_available():
        # Store URN as node
        await client.store_urn_node("urn:vcc:nrw:document:2025:abc123", {
            "title": "Dokument XYZ",
            "type": "document",
        })
        
        # Query URNs
        results = await client.query_urns(domain="nrw", type="document")
        
        # Create cross-reference
        await client.create_reference(
            source="urn:vcc:nrw:document:2025:abc123",
            target="urn:vcc:by:document:2024:xyz789",
            relation="REFERENCES"
        )

On-Premise Deployment:
    Veritas runs alongside VCC-URN in the same infrastructure:
    - Kubernetes: Separate deployment in same namespace
    - Docker Compose: Additional service
    - Manual: Separate process on same host
    
    No data leaves German jurisdiction.
"""

import os
import logging
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in the graph."""
    URN = "URN"
    DOCUMENT = "Document"
    MANIFEST = "Manifest"
    EXTERNAL_URN = "ExternalURN"
    CATALOG = "Catalog"
    DOMAIN = "Domain"


class RelationType(Enum):
    """Types of relationships in the graph."""
    HAS_MANIFEST = "HAS_MANIFEST"
    REFERENCES = "REFERENCES"
    BELONGS_TO = "BELONGS_TO"
    FEDERATED_FROM = "FEDERATED_FROM"
    SUPERSEDES = "SUPERSEDES"
    RELATED_TO = "RELATED_TO"


@dataclass
class GraphNode:
    """A node in the graph database."""
    id: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "labels": self.labels,
            "properties": self.properties,
        }


@dataclass
class GraphRelationship:
    """A relationship in the graph database."""
    id: Optional[str] = None
    type: str = ""
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "properties": self.properties,
        }


@dataclass
class QueryResult:
    """Result from a graph query."""
    success: bool
    nodes: List[GraphNode] = field(default_factory=list)
    relationships: List[GraphRelationship] = field(default_factory=list)
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "nodes": [n.to_dict() for n in self.nodes],
            "relationships": [r.to_dict() for r in self.relationships],
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
        }


class VeritasClient:
    """
    Client for Veritas Graph-DB integration.
    
    Veritas is the VCC Graph-DB component that stores URNs as graph nodes
    and relationships, enabling graph-based queries and traversals.
    
    Configuration via environment variables:
        URN_VERITAS_ENABLED: Enable Veritas (default: false)
        URN_VERITAS_ENDPOINT: Veritas API endpoint
        URN_VERITAS_API_KEY: API key for authentication
        URN_VERITAS_DATABASE: Database name
    
    Example:
        client = VeritasClient()
        await client.store_urn_node("urn:vcc:nrw:document:2025:abc123", {...})
        results = await client.query_urns(domain="nrw")
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        database: str = "vcc_urn",
    ):
        """
        Initialize Veritas client.
        
        Args:
            endpoint: Veritas API endpoint (or URN_VERITAS_ENDPOINT)
            api_key: API key (or URN_VERITAS_API_KEY)
            database: Database name
        """
        self.enabled = os.getenv("URN_VERITAS_ENABLED", "false").lower() == "true"
        self.endpoint = endpoint or os.getenv("URN_VERITAS_ENDPOINT", "http://localhost:7474")
        self.api_key = api_key or os.getenv("URN_VERITAS_API_KEY")
        self.database = os.getenv("URN_VERITAS_DATABASE", database)
        
        self._client = None
        
        if self.enabled:
            logger.info(f"Veritas client initialized, endpoint: {self.endpoint}")
        else:
            logger.debug("Veritas client disabled")
    
    def is_available(self) -> bool:
        """Check if Veritas is enabled and configured."""
        return self.enabled and bool(self.endpoint)
    
    async def _get_client(self):
        """Get or create HTTP client."""
        if self._client is None:
            try:
                import httpx
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
                if self.api_key:
                    headers["X-API-Key"] = self.api_key
                
                self._client = httpx.AsyncClient(
                    timeout=30,
                    headers=headers,
                )
            except ImportError:
                logger.error("httpx not installed")
                return None
        return self._client
    
    def _parse_urn(self, urn: str) -> Dict[str, str]:
        """Parse URN into components."""
        # URN format: urn:vcc:<domain>:<type>:<year>:<id>
        parts = urn.split(":")
        if len(parts) >= 6:
            return {
                "urn": urn,
                "namespace": parts[1],
                "domain": parts[2],
                "type": parts[3],
                "year": parts[4],
                "id": ":".join(parts[5:]),
            }
        return {"urn": urn}
    
    async def store_urn_node(
        self,
        urn: str,
        properties: Optional[Dict[str, Any]] = None,
        labels: Optional[List[str]] = None,
    ) -> QueryResult:
        """
        Store a URN as a node in the graph.
        
        Args:
            urn: URN to store
            properties: Additional node properties
            labels: Additional node labels
            
        Returns:
            QueryResult with created node
        """
        if not self.is_available():
            return QueryResult(success=False, error="Veritas not enabled")
        
        # Parse URN and merge with properties
        urn_props = self._parse_urn(urn)
        node_props = {**urn_props, **(properties or {})}
        
        # Determine labels
        node_labels = [NodeType.URN.value]
        if labels:
            node_labels.extend(labels)
        
        # Build Cypher query
        cypher = f"""
        MERGE (n:{':'.join(node_labels)} {{urn: $urn}})
        SET n += $properties
        RETURN n
        """
        
        return await self._execute_cypher(cypher, {
            "urn": urn,
            "properties": node_props,
        })
    
    async def get_urn_node(self, urn: str) -> QueryResult:
        """
        Get a URN node from the graph.
        
        Args:
            urn: URN to retrieve
            
        Returns:
            QueryResult with node
        """
        if not self.is_available():
            return QueryResult(success=False, error="Veritas not enabled")
        
        cypher = """
        MATCH (n:URN {urn: $urn})
        RETURN n
        """
        
        return await self._execute_cypher(cypher, {"urn": urn})
    
    async def query_urns(
        self,
        domain: Optional[str] = None,
        type: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 100,
    ) -> QueryResult:
        """
        Query URN nodes with filters.
        
        Args:
            domain: Filter by domain (Bundesland)
            type: Filter by type
            year: Filter by year
            limit: Maximum results
            
        Returns:
            QueryResult with matching nodes
        """
        if not self.is_available():
            return QueryResult(success=False, error="Veritas not enabled")
        
        # Build filter conditions
        conditions = []
        params = {"limit": limit}
        
        if domain:
            conditions.append("n.domain = $domain")
            params["domain"] = domain
        if type:
            conditions.append("n.type = $type")
            params["type"] = type
        if year:
            conditions.append("n.year = $year")
            params["year"] = str(year)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cypher = f"""
        MATCH (n:URN)
        WHERE {where_clause}
        RETURN n
        LIMIT $limit
        """
        
        return await self._execute_cypher(cypher, params)
    
    async def create_reference(
        self,
        source_urn: str,
        target_urn: str,
        relation: str = "REFERENCES",
        properties: Optional[Dict[str, Any]] = None,
    ) -> QueryResult:
        """
        Create a reference (relationship) between two URNs.
        
        Args:
            source_urn: Source URN
            target_urn: Target URN
            relation: Relationship type
            properties: Relationship properties
            
        Returns:
            QueryResult with relationship
        """
        if not self.is_available():
            return QueryResult(success=False, error="Veritas not enabled")
        
        cypher = f"""
        MATCH (s:URN {{urn: $source_urn}})
        MATCH (t:URN {{urn: $target_urn}})
        MERGE (s)-[r:{relation}]->(t)
        SET r += $properties
        RETURN s, r, t
        """
        
        return await self._execute_cypher(cypher, {
            "source_urn": source_urn,
            "target_urn": target_urn,
            "properties": properties or {},
        })
    
    async def create_external_reference(
        self,
        source_urn: str,
        external_urn: str,
        federated_from: str,
    ) -> QueryResult:
        """
        Create a reference to an external (federated) URN.
        
        This creates a proxy node for URNs that exist in other Bundesländer.
        
        Args:
            source_urn: Local source URN
            external_urn: External URN (from another Bundesland)
            federated_from: Source Bundesland code
            
        Returns:
            QueryResult with relationship
        """
        if not self.is_available():
            return QueryResult(success=False, error="Veritas not enabled")
        
        cypher = """
        MATCH (s:URN {urn: $source_urn})
        MERGE (e:ExternalURN {urn: $external_urn})
        ON CREATE SET e.federated = true, e.federated_from = $federated_from
        MERGE (s)-[r:FEDERATED_FROM]->(e)
        SET r.created_at = datetime()
        RETURN s, r, e
        """
        
        return await self._execute_cypher(cypher, {
            "source_urn": source_urn,
            "external_urn": external_urn,
            "federated_from": federated_from,
        })
    
    async def store_manifest(
        self,
        urn: str,
        manifest: Dict[str, Any],
        version: str = "1.0",
    ) -> QueryResult:
        """
        Store a manifest for a URN.
        
        Args:
            urn: URN to attach manifest to
            manifest: Manifest data
            version: Manifest version
            
        Returns:
            QueryResult with manifest node
        """
        if not self.is_available():
            return QueryResult(success=False, error="Veritas not enabled")
        
        cypher = """
        MATCH (u:URN {urn: $urn})
        MERGE (m:Manifest {urn: $urn, version: $version})
        SET m.data = $manifest, m.updated_at = datetime()
        MERGE (u)-[r:HAS_MANIFEST]->(m)
        RETURN u, r, m
        """
        
        return await self._execute_cypher(cypher, {
            "urn": urn,
            "manifest": manifest,
            "version": version,
        })
    
    async def get_manifest(
        self,
        urn: str,
        version: Optional[str] = None,
    ) -> QueryResult:
        """
        Get manifest for a URN.
        
        Args:
            urn: URN to get manifest for
            version: Specific version (default: latest)
            
        Returns:
            QueryResult with manifest
        """
        if not self.is_available():
            return QueryResult(success=False, error="Veritas not enabled")
        
        if version:
            cypher = """
            MATCH (u:URN {urn: $urn})-[:HAS_MANIFEST]->(m:Manifest {version: $version})
            RETURN m
            """
            params = {"urn": urn, "version": version}
        else:
            cypher = """
            MATCH (u:URN {urn: $urn})-[:HAS_MANIFEST]->(m:Manifest)
            RETURN m
            ORDER BY m.updated_at DESC
            LIMIT 1
            """
            params = {"urn": urn}
        
        return await self._execute_cypher(cypher, params)
    
    async def get_related_urns(
        self,
        urn: str,
        relation: Optional[str] = None,
        direction: str = "both",
        depth: int = 1,
    ) -> QueryResult:
        """
        Get URNs related to a given URN.
        
        Args:
            urn: Source URN
            relation: Filter by relationship type
            direction: "in", "out", or "both"
            depth: Traversal depth
            
        Returns:
            QueryResult with related URNs
        """
        if not self.is_available():
            return QueryResult(success=False, error="Veritas not enabled")
        
        rel_pattern = f"[:{relation}]" if relation else "[r]"
        
        if direction == "out":
            cypher = f"""
            MATCH (s:URN {{urn: $urn}})-{rel_pattern}*1..{depth}->(t:URN)
            RETURN DISTINCT t
            """
        elif direction == "in":
            cypher = f"""
            MATCH (s:URN {{urn: $urn}})<-{rel_pattern}*1..{depth}-(t:URN)
            RETURN DISTINCT t
            """
        else:
            cypher = f"""
            MATCH (s:URN {{urn: $urn}})-{rel_pattern}*1..{depth}-(t:URN)
            RETURN DISTINCT t
            """
        
        return await self._execute_cypher(cypher, {"urn": urn})
    
    async def _execute_cypher(
        self,
        cypher: str,
        parameters: Dict[str, Any],
    ) -> QueryResult:
        """Execute a Cypher query."""
        client = await self._get_client()
        if client is None:
            return QueryResult(success=False, error="HTTP client not available")
        
        import time
        start = time.time()
        
        try:
            response = await client.post(
                f"{self.endpoint}/db/{self.database}/tx/commit",
                json={
                    "statements": [{
                        "statement": cypher,
                        "parameters": parameters,
                    }]
                }
            )
            
            execution_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse results
                nodes = []
                relationships = []
                
                for result in data.get("results", []):
                    for record in result.get("data", []):
                        for item in record.get("row", []):
                            if isinstance(item, dict):
                                if "labels" in item or "urn" in item:
                                    nodes.append(GraphNode(
                                        properties=item,
                                    ))
                
                return QueryResult(
                    success=True,
                    nodes=nodes,
                    relationships=relationships,
                    execution_time_ms=execution_time,
                )
            else:
                return QueryResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}",
                    execution_time_ms=execution_time,
                )
                
        except Exception as e:
            logger.error(f"Veritas query failed: {e}")
            return QueryResult(
                success=False,
                error=str(e),
            )
    
    async def health_check(self) -> bool:
        """Check if Veritas is healthy."""
        if not self.is_available():
            return False
        
        client = await self._get_client()
        if client is None:
            return False
        
        try:
            response = await client.get(f"{self.endpoint}/")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Veritas health check failed: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# FastAPI integration
def get_veritas_router():
    """
    Get FastAPI router for Veritas integration endpoints.
    
    Returns:
        APIRouter with /graph endpoints, or None if FastAPI not available
    """
    try:
        from fastapi import APIRouter, HTTPException, Query
        from pydantic import BaseModel
    except ImportError:
        logger.debug("FastAPI not available, skipping Veritas router")
        return None
    
    router = APIRouter(prefix="/graph", tags=["Veritas Graph-DB"])
    
    _client = VeritasClient()
    
    class StoreNodeRequest(BaseModel):
        urn: str
        properties: Optional[Dict[str, Any]] = None
        labels: Optional[List[str]] = None
    
    class CreateReferenceRequest(BaseModel):
        source_urn: str
        target_urn: str
        relation: str = "REFERENCES"
        properties: Optional[Dict[str, Any]] = None
    
    @router.post("/nodes")
    async def store_node(request: StoreNodeRequest):
        """Store a URN as a graph node."""
        if not _client.is_available():
            raise HTTPException(status_code=503, detail="Veritas not enabled")
        
        result = await _client.store_urn_node(
            request.urn,
            request.properties,
            request.labels,
        )
        return result.to_dict()
    
    @router.get("/nodes/{urn:path}")
    async def get_node(urn: str):
        """Get a URN node."""
        if not _client.is_available():
            raise HTTPException(status_code=503, detail="Veritas not enabled")
        
        result = await _client.get_urn_node(urn)
        if not result.success:
            raise HTTPException(status_code=404, detail="Node not found")
        return result.to_dict()
    
    @router.get("/query")
    async def query_urns(
        domain: Optional[str] = Query(None),
        type: Optional[str] = Query(None),
        year: Optional[int] = Query(None),
        limit: int = Query(100),
    ):
        """Query URN nodes."""
        if not _client.is_available():
            raise HTTPException(status_code=503, detail="Veritas not enabled")
        
        result = await _client.query_urns(domain, type, year, limit)
        return result.to_dict()
    
    @router.post("/references")
    async def create_reference(request: CreateReferenceRequest):
        """Create a reference between URNs."""
        if not _client.is_available():
            raise HTTPException(status_code=503, detail="Veritas not enabled")
        
        result = await _client.create_reference(
            request.source_urn,
            request.target_urn,
            request.relation,
            request.properties,
        )
        return result.to_dict()
    
    @router.get("/related/{urn:path}")
    async def get_related(
        urn: str,
        relation: Optional[str] = Query(None),
        direction: str = Query("both"),
        depth: int = Query(1),
    ):
        """Get URNs related to a given URN."""
        if not _client.is_available():
            raise HTTPException(status_code=503, detail="Veritas not enabled")
        
        result = await _client.get_related_urns(urn, relation, direction, depth)
        return result.to_dict()
    
    @router.get("/health")
    async def graph_health():
        """Check Veritas health."""
        is_healthy = await _client.health_check()
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "enabled": _client.is_available(),
        }
    
    return router
