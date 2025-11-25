# VCC-URN Service Discovery
# ===========================
# Kubernetes-native service discovery for federation peers
# On-premise, vendor-free (no Consul/etcd external dependencies)

"""
Service Discovery Module for VCC-URN Federation

Provides Kubernetes-native service discovery using:
- Kubernetes DNS (in-cluster)
- Manual endpoint configuration (fallback)
- Health-aware peer selection

No external service registries required - follows VCC on-premise principles.
"""

import os
import socket
import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import httpx

from vcc_urn.core.logging import logger
from vcc_urn.core.config import settings


@dataclass
class PeerEndpoint:
    """Represents a discovered federation peer."""
    url: str
    nid: str
    health_status: str = "unknown"  # healthy, unhealthy, unknown
    last_health_check: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ServiceDiscovery:
    """
    Kubernetes-native service discovery for VCC-URN federation.
    
    Discovery methods (in order of preference):
    1. Kubernetes DNS (headless services)
    2. Environment variable configuration
    3. Manual configuration file
    
    All methods are on-premise compatible without external dependencies.
    """
    
    def __init__(self):
        self.peers: Dict[str, PeerEndpoint] = {}
        self.discovery_mode = os.getenv("URN_DISCOVERY_MODE", "manual")  # k8s, manual
        self.k8s_namespace = os.getenv("URN_K8S_NAMESPACE", "vcc-urn")
        self.k8s_service_name = os.getenv("URN_K8S_SERVICE_NAME", "vcc-urn-headless")
        self.health_check_interval = int(os.getenv("URN_HEALTH_CHECK_INTERVAL", "30"))
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start service discovery and health checking."""
        await self.discover_peers()
        self._start_health_check_loop()
        logger.info(
            "Service discovery started",
            mode=self.discovery_mode,
            peer_count=len(self.peers)
        )
    
    async def stop(self) -> None:
        """Stop service discovery and cleanup."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("Service discovery stopped")
    
    async def discover_peers(self) -> List[PeerEndpoint]:
        """
        Discover federation peers based on configured discovery mode.
        
        Returns:
            List of discovered peer endpoints
        """
        if self.discovery_mode == "k8s":
            await self._discover_kubernetes_peers()
        else:
            await self._discover_manual_peers()
        
        return list(self.peers.values())
    
    async def _discover_kubernetes_peers(self) -> None:
        """
        Discover peers using Kubernetes DNS (headless service).
        
        This uses DNS A record resolution for headless services,
        which returns individual pod IPs.
        """
        dns_name = f"{self.k8s_service_name}.{self.k8s_namespace}.svc.cluster.local"
        
        try:
            # Resolve DNS to get all pod IPs
            _, _, addrs = await asyncio.get_event_loop().run_in_executor(
                None, socket.gethostbyname_ex, dns_name
            )
            
            logger.info(f"Discovered {len(addrs)} peers via Kubernetes DNS", dns_name=dns_name)
            
            # Query each pod for its NID
            port = os.getenv("URN_SERVICE_PORT", "8000")
            for addr in addrs:
                peer_url = f"http://{addr}:{port}"
                await self._register_peer_from_url(peer_url)
                
        except socket.gaierror as e:
            logger.warning(
                "Kubernetes DNS discovery failed - falling back to manual",
                dns_name=dns_name,
                error=str(e)
            )
            await self._discover_manual_peers()
    
    async def _discover_manual_peers(self) -> None:
        """
        Discover peers from environment configuration.
        
        Expected format: URN_FEDERATION_PEERS=http://peer1:8000,http://peer2:8000
        """
        peers_config = settings.federation_peers
        
        if not peers_config:
            logger.info("No manual peers configured (URN_FEDERATION_PEERS is empty)")
            return
        
        peer_urls = [url.strip() for url in peers_config.split(",") if url.strip()]
        
        logger.info(f"Discovering {len(peer_urls)} manual peers")
        
        for peer_url in peer_urls:
            await self._register_peer_from_url(peer_url)
    
    async def _register_peer_from_url(self, url: str) -> Optional[PeerEndpoint]:
        """Register a peer by querying its info endpoint."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                start_time = datetime.now()
                response = await client.get(f"{url}/")
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    nid = data.get("nid", "unknown")
                    
                    peer = PeerEndpoint(
                        url=url,
                        nid=nid,
                        health_status="healthy",
                        last_health_check=datetime.now(),
                        response_time_ms=response_time,
                        metadata=data
                    )
                    
                    self.peers[url] = peer
                    logger.info(f"Registered peer", url=url, nid=nid, response_time_ms=response_time)
                    return peer
                else:
                    logger.warning(f"Failed to query peer", url=url, status=response.status_code)
                    
        except Exception as e:
            logger.warning(f"Failed to register peer", url=url, error=str(e))
        
        # Register as unhealthy but known
        peer = PeerEndpoint(
            url=url,
            nid="unknown",
            health_status="unhealthy",
            last_health_check=datetime.now()
        )
        self.peers[url] = peer
        return peer
    
    def _start_health_check_loop(self) -> None:
        """Start background health checking for all peers."""
        async def health_check_loop():
            while True:
                await asyncio.sleep(self.health_check_interval)
                await self._check_all_peer_health()
        
        self._health_check_task = asyncio.create_task(health_check_loop())
    
    async def _check_all_peer_health(self) -> None:
        """Check health of all registered peers."""
        for url in list(self.peers.keys()):
            await self._check_peer_health(url)
    
    async def _check_peer_health(self, url: str) -> bool:
        """Check health of a specific peer."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                start_time = datetime.now()
                response = await client.get(f"{url}/healthz")
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if url in self.peers:
                    peer = self.peers[url]
                    peer.health_status = "healthy" if response.status_code == 200 else "unhealthy"
                    peer.last_health_check = datetime.now()
                    peer.response_time_ms = response_time
                    
                return response.status_code == 200
                
        except Exception as e:
            if url in self.peers:
                self.peers[url].health_status = "unhealthy"
                self.peers[url].last_health_check = datetime.now()
            logger.debug(f"Health check failed for peer", url=url, error=str(e))
            return False
    
    def get_healthy_peers(self) -> List[PeerEndpoint]:
        """Get list of healthy peers for federation."""
        return [p for p in self.peers.values() if p.health_status == "healthy"]
    
    def get_peer_by_nid(self, nid: str) -> Optional[PeerEndpoint]:
        """Get a specific peer by its NID."""
        for peer in self.peers.values():
            if peer.nid == nid:
                return peer
        return None
    
    def get_all_peers(self) -> List[PeerEndpoint]:
        """Get all registered peers (healthy and unhealthy)."""
        return list(self.peers.values())
    
    def get_status(self) -> Dict[str, Any]:
        """Get service discovery status for monitoring."""
        healthy_count = len(self.get_healthy_peers())
        total_count = len(self.peers)
        
        return {
            "discovery_mode": self.discovery_mode,
            "total_peers": total_count,
            "healthy_peers": healthy_count,
            "unhealthy_peers": total_count - healthy_count,
            "health_check_interval_seconds": self.health_check_interval,
            "peers": [
                {
                    "url": p.url,
                    "nid": p.nid,
                    "status": p.health_status,
                    "last_check": p.last_health_check.isoformat() if p.last_health_check else None,
                    "response_time_ms": p.response_time_ms
                }
                for p in self.peers.values()
            ]
        }


# Global service discovery instance
service_discovery = ServiceDiscovery()
