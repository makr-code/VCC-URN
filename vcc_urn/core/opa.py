# VCC-URN Open Policy Agent (OPA) Integration
# =============================================
# Policy-based authorization for the federal URN resolver
# On-premise, vendor-free policy engine

"""
Open Policy Agent (OPA) Integration Module for VCC-URN

Provides policy-based access control:
- Fine-grained authorization rules
- Data filtering based on policies
- Federation access policies
- RBAC enforcement via Rego policies

OPA is Open-Source (Apache 2.0) and runs fully on-premise.
This module provides OPA integration for Phase 3 when needed.

Configuration:
- URN_OPA_ENABLED: Enable OPA integration (default: false)
- URN_OPA_URL: OPA server URL (default: http://localhost:8181)
- URN_OPA_POLICY_PATH: Policy document path (default: v1/data/vcc/urn/allow)
"""

import os
import json
from typing import Optional, Dict, Any, List
import httpx

from vcc_urn.core.logging import logger


class OPAPolicyEngine:
    """
    OPA Policy Engine for VCC-URN authorization.
    
    Features:
    - REST API integration with OPA server
    - Policy-based access control for URN operations
    - Federation routing policies
    - Audit logging for policy decisions
    
    Runs fully on-premise - no external SaaS dependencies.
    """
    
    def __init__(self):
        self.enabled = os.getenv("URN_OPA_ENABLED", "false").lower() == "true"
        self.opa_url = os.getenv("URN_OPA_URL", "http://localhost:8181")
        self.policy_path = os.getenv("URN_OPA_POLICY_PATH", "v1/data/vcc/urn")
        self._client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self) -> None:
        """Initialize OPA client connection."""
        if not self.enabled:
            logger.info("OPA policy engine disabled")
            return
        
        self._client = httpx.AsyncClient(
            base_url=self.opa_url,
            timeout=5.0
        )
        
        # Test connection to OPA
        try:
            response = await self._client.get("/health")
            if response.status_code == 200:
                logger.info("OPA policy engine connected", url=self.opa_url)
            else:
                logger.warning("OPA health check failed", status=response.status_code)
        except Exception as e:
            logger.warning(f"OPA connection failed: {e}", url=self.opa_url)
    
    async def close(self) -> None:
        """Close OPA client connection."""
        if self._client:
            await self._client.aclose()
    
    async def check_permission(
        self,
        user_id: str,
        action: str,
        resource: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if a user has permission to perform an action on a resource.
        
        Args:
            user_id: User identifier (from auth token)
            action: Action being performed (generate, validate, resolve, store, delete)
            resource: Resource being accessed (urn, manifest, catalog)
            context: Additional context for policy evaluation
        
        Returns:
            True if action is allowed, False otherwise
        """
        if not self.enabled:
            return True  # If OPA disabled, allow all (fallback to RBAC)
        
        input_data = {
            "input": {
                "user": user_id,
                "action": action,
                "resource": resource,
                "context": context or {},
            }
        }
        
        try:
            response = await self._client.post(
                f"/{self.policy_path}/allow",
                json=input_data
            )
            
            if response.status_code == 200:
                result = response.json()
                allowed = result.get("result", False)
                
                logger.debug(
                    "OPA policy decision",
                    user=user_id,
                    action=action,
                    resource=resource,
                    allowed=allowed
                )
                
                return allowed
            else:
                logger.warning(
                    "OPA policy check failed",
                    status=response.status_code,
                    user=user_id,
                    action=action
                )
                return False
                
        except Exception as e:
            logger.error(f"OPA policy evaluation error: {e}")
            return False  # Fail closed on errors
    
    async def get_allowed_operations(
        self,
        user_id: str,
        resource_type: str
    ) -> List[str]:
        """
        Get list of operations a user is allowed to perform on a resource type.
        
        Args:
            user_id: User identifier
            resource_type: Type of resource (urn, manifest, catalog)
        
        Returns:
            List of allowed operation names
        """
        if not self.enabled:
            # Default operations if OPA disabled
            return ["generate", "validate", "resolve", "search"]
        
        input_data = {
            "input": {
                "user": user_id,
                "resource_type": resource_type,
            }
        }
        
        try:
            response = await self._client.post(
                f"/{self.policy_path}/allowed_operations",
                json=input_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("result", [])
            
        except Exception as e:
            logger.error(f"OPA allowed_operations error: {e}")
        
        return []
    
    async def check_federation_access(
        self,
        source_nid: str,
        target_nid: str,
        operation: str
    ) -> bool:
        """
        Check if federation access is allowed between two instances.
        
        Args:
            source_nid: NID of requesting instance
            target_nid: NID of target instance
            operation: Federation operation (resolve, replicate, sync)
        
        Returns:
            True if federation access is allowed
        """
        if not self.enabled:
            return True
        
        input_data = {
            "input": {
                "source_nid": source_nid,
                "target_nid": target_nid,
                "operation": operation,
            }
        }
        
        try:
            response = await self._client.post(
                f"/{self.policy_path}/federation/allow",
                json=input_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("result", False)
                
        except Exception as e:
            logger.error(f"OPA federation policy error: {e}")
        
        return False
    
    async def filter_results(
        self,
        user_id: str,
        results: List[Dict[str, Any]],
        operation: str
    ) -> List[Dict[str, Any]]:
        """
        Filter results based on user's data access policies.
        
        Args:
            user_id: User identifier
            results: List of result objects to filter
            operation: Operation being performed
        
        Returns:
            Filtered list of results user is allowed to see
        """
        if not self.enabled:
            return results
        
        input_data = {
            "input": {
                "user": user_id,
                "operation": operation,
                "results": results,
            }
        }
        
        try:
            response = await self._client.post(
                f"/{self.policy_path}/filter_results",
                json=input_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("result", results)
                
        except Exception as e:
            logger.error(f"OPA filter_results error: {e}")
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get OPA integration status for monitoring."""
        return {
            "enabled": self.enabled,
            "url": self.opa_url if self.enabled else None,
            "policy_path": self.policy_path if self.enabled else None,
        }


# Sample Rego policy for VCC-URN (to be deployed to OPA server)
SAMPLE_REGO_POLICY = '''
# VCC-URN Authorization Policy
# Deploy to OPA server at: /v1/policies/vcc/urn

package vcc.urn

default allow = false

# Allow all operations for admin role
allow {
    input.context.role == "admin"
}

# Allow read operations for reader role
allow {
    input.context.role == "reader"
    input.action == "resolve"
}

allow {
    input.context.role == "reader"
    input.action == "validate"
}

allow {
    input.context.role == "reader"
    input.action == "search"
}

# Allow write operations for writer role
allow {
    input.context.role == "writer"
}

# Federation access policy
federation.allow {
    # Allow all federation between registered instances
    input.source_nid != input.target_nid
}

# Define allowed operations per role
allowed_operations[op] {
    input.context.role == "admin"
    op := ["generate", "validate", "resolve", "store", "delete", "search"][_]
}

allowed_operations[op] {
    input.context.role == "writer"
    op := ["generate", "validate", "resolve", "store", "search"][_]
}

allowed_operations[op] {
    input.context.role == "reader"
    op := ["validate", "resolve", "search"][_]
}
'''


# Global OPA policy engine instance
opa_engine = OPAPolicyEngine()
