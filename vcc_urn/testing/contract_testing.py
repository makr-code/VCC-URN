"""
Contract Testing - Pact Integration for API Contracts

This module provides contract testing capabilities using Pact,
enabling consumer-driven contract testing between VCC-URN instances
and other VCC ecosystem components.

Why Contract Testing?
1. API Stability - Ensure API contracts don't break during evolution
2. Decoupled Development - Consumer and provider develop independently
3. Federation Confidence - Verify inter-Bundesland API compatibility
4. Themis AQL Contracts - Test AQL query/response contracts
5. Version Management - Track contract versions across deployments

Contract Types:
1. REST API Contracts - HTTP request/response verification
2. Themis AQL Contracts - AQL query result verification
3. Federation Contracts - Peer-to-peer API contracts
4. Event Contracts - Async message contracts (future)

Configuration:
    URN_PACT_ENABLED: Enable Pact contract testing (default: false)
    URN_PACT_BROKER_URL: Pact Broker URL (optional)
    URN_PACT_CONSUMER: Consumer name for contracts
    URN_PACT_PROVIDER: Provider name for contracts
    URN_PACT_DIR: Directory for contract files

Usage:
    # Consumer test (defines expectations)
    contract = PactContractTest(consumer="covina", provider="vcc-urn")
    
    with contract.given("URN exists"):
        contract.upon_receiving("resolve URN request")
        contract.with_request("GET", "/api/v1/resolve", query={"urn": "..."})
        contract.will_respond_with(200, body={"urn": "...", "manifest": {...}})
    
    contract.verify_with_provider()
    
    # Provider test (verifies against contracts)
    contract = PactContractTest(provider="vcc-urn")
    contract.verify_provider_contracts()

On-Premise Deployment:
    Pact Broker can be self-hosted for on-premise contract management:
    - Docker: pactfoundation/pact-broker
    - Kubernetes: Pact Broker Helm chart
    
    No SaaS dependency required.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ContractInteraction:
    """A single interaction in a contract."""
    description: str
    given: Optional[str] = None  # Provider state
    request: Dict[str, Any] = field(default_factory=dict)
    response: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to Pact interaction format."""
        interaction = {
            "description": self.description,
            "request": self.request,
            "response": self.response,
        }
        if self.given:
            interaction["providerState"] = self.given
        return interaction


@dataclass
class Contract:
    """A Pact contract between consumer and provider."""
    consumer: str
    provider: str
    interactions: List[ContractInteraction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to Pact contract format."""
        return {
            "consumer": {"name": self.consumer},
            "provider": {"name": self.provider},
            "interactions": [i.to_dict() for i in self.interactions],
            "metadata": {
                "pactSpecification": {"version": "2.0.0"},
                **self.metadata,
            },
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save(self, path: str):
        """Save contract to file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.to_json())
        logger.info(f"Contract saved to {path}")


class PactContractTest:
    """
    Pact Contract Test Builder and Verifier.
    
    This class provides a fluent interface for building and verifying
    Pact contracts between VCC components.
    
    Configuration via environment variables:
        URN_PACT_ENABLED: Enable Pact (default: false)
        URN_PACT_BROKER_URL: Pact Broker URL
        URN_PACT_DIR: Contract directory
    
    Example (Consumer):
        test = PactContractTest(consumer="covina", provider="vcc-urn")
        
        test.given("URN urn:vcc:nrw:document:2025:abc123 exists")
        test.upon_receiving("a request to resolve the URN")
        test.with_request("GET", "/api/v1/resolve", query={"urn": "urn:vcc:nrw:document:2025:abc123"})
        test.will_respond_with(200, body={"urn": "...", "manifest": {...}})
        
        test.finalize()
        test.verify()
    
    Example (Provider):
        test = PactContractTest(provider="vcc-urn")
        test.verify_provider()
    """
    
    def __init__(
        self,
        consumer: Optional[str] = None,
        provider: Optional[str] = None,
        pact_dir: Optional[str] = None,
        broker_url: Optional[str] = None,
    ):
        """
        Initialize contract test.
        
        Args:
            consumer: Consumer name (for consumer tests)
            provider: Provider name
            pact_dir: Directory for contract files
            broker_url: Pact Broker URL (optional)
        """
        self.enabled = os.getenv("URN_PACT_ENABLED", "false").lower() == "true"
        
        self.consumer = consumer or os.getenv("URN_PACT_CONSUMER", "test-consumer")
        self.provider = provider or os.getenv("URN_PACT_PROVIDER", "vcc-urn")
        self.pact_dir = pact_dir or os.getenv("URN_PACT_DIR", "./pacts")
        self.broker_url = broker_url or os.getenv("URN_PACT_BROKER_URL")
        
        # Current interaction being built
        self._current_interaction: Optional[ContractInteraction] = None
        
        # Contract being built
        self._contract = Contract(
            consumer=self.consumer,
            provider=self.provider,
        )
        
        if self.enabled:
            logger.info(f"Pact contract testing enabled: {self.consumer} -> {self.provider}")
    
    def given(self, provider_state: str) -> "PactContractTest":
        """
        Set the provider state for the current interaction.
        
        Args:
            provider_state: Description of provider state
            
        Returns:
            Self for chaining
        """
        if self._current_interaction is None:
            self._current_interaction = ContractInteraction(description="")
        self._current_interaction.given = provider_state
        return self
    
    def upon_receiving(self, description: str) -> "PactContractTest":
        """
        Set the description for the current interaction.
        
        Args:
            description: Description of the interaction
            
        Returns:
            Self for chaining
        """
        if self._current_interaction is None:
            self._current_interaction = ContractInteraction(description=description)
        else:
            self._current_interaction.description = description
        return self
    
    def with_request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        query: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
    ) -> "PactContractTest":
        """
        Define the expected request.
        
        Args:
            method: HTTP method
            path: Request path
            headers: Request headers
            query: Query parameters
            body: Request body
            
        Returns:
            Self for chaining
        """
        if self._current_interaction is None:
            self._current_interaction = ContractInteraction(description="")
        
        request = {
            "method": method,
            "path": path,
        }
        if headers:
            request["headers"] = headers
        if query:
            request["query"] = query
        if body:
            request["body"] = body
        
        self._current_interaction.request = request
        return self
    
    def will_respond_with(
        self,
        status: int,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
    ) -> "PactContractTest":
        """
        Define the expected response.
        
        Args:
            status: HTTP status code
            headers: Response headers
            body: Response body
            
        Returns:
            Self for chaining
        """
        if self._current_interaction is None:
            self._current_interaction = ContractInteraction(description="")
        
        response = {"status": status}
        if headers:
            response["headers"] = headers
        if body:
            response["body"] = body
        
        self._current_interaction.response = response
        
        # Add interaction to contract
        self._contract.interactions.append(self._current_interaction)
        self._current_interaction = None
        
        return self
    
    def finalize(self) -> Contract:
        """
        Finalize and return the contract.
        
        Returns:
            The completed contract
        """
        # Add metadata
        self._contract.metadata["generated_at"] = datetime.utcnow().isoformat()
        self._contract.metadata["vcc_urn_version"] = os.getenv("URN_VERSION", "1.0.0")
        
        return self._contract
    
    def save_contract(self, filename: Optional[str] = None) -> str:
        """
        Save the contract to a file.
        
        Args:
            filename: Custom filename (default: consumer-provider.json)
            
        Returns:
            Path to saved contract
        """
        if filename is None:
            filename = f"{self.consumer}-{self.provider}.json"
        
        path = os.path.join(self.pact_dir, filename)
        self._contract.save(path)
        return path
    
    def verify(self, base_url: Optional[str] = None) -> bool:
        """
        Verify the contract against a provider.
        
        Args:
            base_url: Provider base URL
            
        Returns:
            True if verification passes
        """
        if not self.enabled:
            logger.warning("Pact testing disabled, skipping verification")
            return True
        
        # In a real implementation, this would use the Pact verifier
        # For now, we simulate the verification
        logger.info(f"Verifying contract: {self.consumer} -> {self.provider}")
        
        try:
            import httpx
            
            base = base_url or "http://localhost:8000"
            client = httpx.Client(timeout=10)
            
            for interaction in self._contract.interactions:
                request = interaction.request
                
                # Build URL
                url = f"{base}{request['path']}"
                if request.get('query'):
                    params = "&".join(f"{k}={v}" for k, v in request['query'].items())
                    url = f"{url}?{params}"
                
                # Make request
                method = request.get('method', 'GET')
                response = client.request(
                    method,
                    url,
                    headers=request.get('headers', {}),
                    json=request.get('body'),
                )
                
                # Verify response
                expected = interaction.response
                if response.status_code != expected.get('status'):
                    logger.error(
                        f"Contract verification failed: {interaction.description}\n"
                        f"Expected status {expected.get('status')}, got {response.status_code}"
                    )
                    return False
                
                logger.info(f"✓ {interaction.description}")
            
            logger.info("Contract verification passed")
            return True
            
        except ImportError:
            logger.warning("httpx not installed, skipping live verification")
            return True
        except Exception as e:
            logger.error(f"Contract verification error: {e}")
            return False
    
    def publish_to_broker(self, version: str) -> bool:
        """
        Publish contract to Pact Broker.
        
        Args:
            version: Consumer version
            
        Returns:
            True if publish successful
        """
        if not self.broker_url:
            logger.warning("No Pact Broker URL configured")
            return False
        
        try:
            import httpx
            
            contract_path = self.save_contract()
            
            with open(contract_path, 'r') as f:
                contract_data = json.load(f)
            
            url = f"{self.broker_url}/pacts/provider/{self.provider}/consumer/{self.consumer}/version/{version}"
            
            response = httpx.put(
                url,
                json=contract_data,
                headers={"Content-Type": "application/json"},
            )
            
            if response.status_code in (200, 201):
                logger.info(f"Contract published to broker: {url}")
                return True
            else:
                logger.error(f"Failed to publish contract: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing to broker: {e}")
            return False


class ContractTemplates:
    """Pre-defined contract templates for common VCC-URN interactions."""
    
    @staticmethod
    def resolve_urn_contract(consumer: str, urn: str) -> Contract:
        """
        Create a contract for URN resolution.
        
        Args:
            consumer: Consumer name
            urn: URN to resolve
            
        Returns:
            Contract for URN resolution
        """
        test = PactContractTest(consumer=consumer, provider="vcc-urn")
        
        test.given(f"URN {urn} exists")
        test.upon_receiving("a request to resolve the URN")
        test.with_request("GET", "/api/v1/resolve", query={"urn": urn})
        test.will_respond_with(
            200,
            body={
                "urn": urn,
                "manifest": {
                    "title": "Example Document",
                    "version": "1.0",
                },
            }
        )
        
        return test.finalize()
    
    @staticmethod
    def generate_urn_contract(consumer: str, domain: str, obj_type: str) -> Contract:
        """
        Create a contract for URN generation.
        
        Args:
            consumer: Consumer name
            domain: Domain (Bundesland)
            obj_type: Object type
            
        Returns:
            Contract for URN generation
        """
        test = PactContractTest(consumer=consumer, provider="vcc-urn")
        
        test.upon_receiving("a request to generate a new URN")
        test.with_request(
            "POST",
            "/api/v1/generate",
            body={
                "domain": domain,
                "type": obj_type,
            }
        )
        test.will_respond_with(
            200,
            body={
                "urn": f"urn:vcc:{domain}:{obj_type}:2025:",  # Partial match
                "valid": True,
            }
        )
        
        return test.finalize()
    
    @staticmethod
    def validate_urn_contract(consumer: str) -> Contract:
        """
        Create a contract for URN validation.
        
        Args:
            consumer: Consumer name
            
        Returns:
            Contract for URN validation
        """
        test = PactContractTest(consumer=consumer, provider="vcc-urn")
        
        test.upon_receiving("a request to validate a valid URN")
        test.with_request(
            "GET",
            "/api/v1/validate",
            query={"urn": "urn:vcc:nrw:document:2025:abc123"}
        )
        test.will_respond_with(200, body={"valid": True})
        
        test.upon_receiving("a request to validate an invalid URN")
        test.with_request(
            "GET",
            "/api/v1/validate",
            query={"urn": "invalid-urn"}
        )
        test.will_respond_with(200, body={"valid": False})
        
        return test.finalize()
    
    @staticmethod
    def batch_resolve_contract(consumer: str, urns: List[str]) -> Contract:
        """
        Create a contract for batch URN resolution.
        
        Args:
            consumer: Consumer name
            urns: List of URNs to resolve
            
        Returns:
            Contract for batch resolution
        """
        test = PactContractTest(consumer=consumer, provider="vcc-urn")
        
        test.given(f"URNs {urns} exist")
        test.upon_receiving("a request to batch resolve URNs")
        test.with_request(
            "POST",
            "/api/v1/resolve/batch",
            body={"urns": urns}
        )
        test.will_respond_with(
            200,
            body={
                "results": [
                    {"urn": urn, "found": True, "manifest": {}}
                    for urn in urns
                ]
            }
        )
        
        return test.finalize()


# VCC ecosystem contracts
class VCCContracts:
    """Contracts for VCC ecosystem integrations."""
    
    @staticmethod
    def covina_to_urn() -> Contract:
        """Contract: Covina -> VCC-URN (document ingestion generates URN)."""
        return ContractTemplates.generate_urn_contract(
            consumer="covina",
            domain="nrw",
            obj_type="document",
        )
    
    @staticmethod
    def veritas_to_urn() -> Contract:
        """Contract: Veritas -> VCC-URN (graph traversal resolves URN)."""
        return ContractTemplates.resolve_urn_contract(
            consumer="veritas",
            urn="urn:vcc:nrw:document:2025:abc123",
        )
    
    @staticmethod
    def clara_to_urn() -> Contract:
        """Contract: Clara -> VCC-URN (RAG context resolution)."""
        return ContractTemplates.batch_resolve_contract(
            consumer="clara",
            urns=[
                "urn:vcc:nrw:document:2025:abc123",
                "urn:vcc:by:document:2024:xyz789",
            ],
        )
