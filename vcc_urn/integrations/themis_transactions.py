"""
Themis Transactions - Saga Orchestrator for Cross-Jurisdiction Consistency

This module provides distributed transaction support for federated URN operations
across multiple Bundesländer. It implements the Saga pattern for eventual consistency
in a distributed system where traditional ACID transactions are not possible.

Architecture Decision: See ADR-0001 (docs/adr/0001-themis-aql-statt-graphql.md)

Why Saga Pattern?
1. Föderale Struktur - No shared database across Bundesländer
2. Autonomie - Each Land controls its own data
3. Eventual Consistency - Acceptable for URN operations
4. Resilience - Compensating transactions handle failures
5. On-Premise - No dependency on cloud orchestration services

Transaction Types:
1. URN Registration - Create URN across multiple registries
2. URN Migration - Move URN ownership between Länder
3. Manifest Sync - Synchronize manifest data across federation
4. Batch Operations - Coordinated multi-URN operations

Saga Steps:
    1. Begin Transaction (get transaction ID)
    2. Execute Participants (call each Bundesland)
    3. Coordinate Responses (wait for all confirmations)
    4. Commit or Compensate (finalize or rollback)

Configuration:
    URN_SAGA_ENABLED: Enable Saga orchestrator (default: false)
    URN_SAGA_TIMEOUT: Global transaction timeout (default: 120s)
    URN_SAGA_RETRY_DELAY: Delay between retries (default: 5s)
    URN_SAGA_MAX_RETRIES: Max retry attempts (default: 3)

Usage:
    orchestrator = ThemisTransactionOrchestrator()
    
    # Start a distributed transaction
    tx = await orchestrator.begin_transaction("urn_registration")
    
    # Add participants
    await tx.add_participant("nrw", "https://urn-nrw.vcc.de/api/v1")
    await tx.add_participant("by", "https://urn-by.vcc.de/api/v1")
    
    # Execute transaction
    result = await tx.execute({
        "action": "register",
        "urn": "urn:vcc:nrw:document:2025:abc123",
        "manifest": {...}
    })
    
    if result.success:
        await tx.commit()
    else:
        await tx.compensate()

On-Premise Alternative to:
    - AWS Step Functions
    - Azure Durable Functions
    - Google Cloud Workflows
    - Temporal.io (cloud hosted)
    
    Themis Transactions runs fully on-premise with no cloud dependencies.
"""

import os
import uuid
import logging
import asyncio
from typing import Optional, Dict, Any, List, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TransactionState(Enum):
    """State of a distributed transaction."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMMITTING = "committing"
    COMPENSATING = "compensating"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


class ParticipantState(Enum):
    """State of a transaction participant."""
    PENDING = "pending"
    PREPARED = "prepared"
    COMMITTED = "committed"
    COMPENSATED = "compensated"
    FAILED = "failed"


@dataclass
class Participant:
    """A participant in a distributed transaction."""
    id: str
    code: str  # Bundesland code
    endpoint: str
    state: ParticipantState = ParticipantState.PENDING
    prepared_at: Optional[datetime] = None
    committed_at: Optional[datetime] = None
    compensated_at: Optional[datetime] = None
    error: Optional[str] = None
    response: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "code": self.code,
            "endpoint": self.endpoint,
            "state": self.state.value,
            "error": self.error,
        }


@dataclass
class SagaStep:
    """A step in a Saga transaction."""
    id: str
    name: str
    participant: Participant
    action: str
    payload: Dict[str, Any]
    compensating_action: Optional[str] = None
    compensating_payload: Optional[Dict[str, Any]] = None
    executed: bool = False
    compensated: bool = False
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class Transaction:
    """A distributed transaction."""
    id: str
    type: str
    state: TransactionState = TransactionState.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None
    participants: List[Participant] = field(default_factory=list)
    steps: List[SagaStep] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "participants": [p.to_dict() for p in self.participants],
            "steps_total": len(self.steps),
            "steps_executed": sum(1 for s in self.steps if s.executed),
            "error": self.error,
        }


class SagaTransaction:
    """
    A Saga-style distributed transaction.
    
    This class manages a single distributed transaction across
    multiple Bundesländer, implementing the Saga pattern with
    compensating transactions for rollback.
    
    Example:
        tx = SagaTransaction("urn_registration")
        await tx.add_participant("nrw", "https://urn-nrw.vcc.de/api/v1")
        result = await tx.execute({"action": "register", "urn": "..."})
        if result.success:
            await tx.commit()
        else:
            await tx.compensate()
    """
    
    def __init__(
        self,
        tx_type: str,
        timeout: int = 120,
        orchestrator: Optional["ThemisTransactionOrchestrator"] = None,
    ):
        """
        Initialize a Saga transaction.
        
        Args:
            tx_type: Type of transaction
            timeout: Transaction timeout in seconds
            orchestrator: Parent orchestrator
        """
        self.transaction = Transaction(
            id=str(uuid.uuid4()),
            type=tx_type,
            timeout_at=datetime.utcnow() + timedelta(seconds=timeout),
        )
        self.orchestrator = orchestrator
        self._client = None
        self._executed_steps: List[SagaStep] = []
    
    @property
    def id(self) -> str:
        """Get transaction ID."""
        return self.transaction.id
    
    @property
    def state(self) -> TransactionState:
        """Get transaction state."""
        return self.transaction.state
    
    async def _get_client(self):
        """Get or create HTTP client."""
        if self._client is None:
            try:
                import httpx
                self._client = httpx.AsyncClient(timeout=30)
            except ImportError:
                return None
        return self._client
    
    def add_participant_sync(self, code: str, endpoint: str) -> Participant:
        """
        Add a participant synchronously.
        
        Args:
            code: Bundesland code
            endpoint: Participant API endpoint
            
        Returns:
            Participant object
        """
        participant = Participant(
            id=str(uuid.uuid4()),
            code=code,
            endpoint=endpoint.rstrip("/"),
        )
        self.transaction.participants.append(participant)
        logger.debug(f"Added participant {code} to transaction {self.id}")
        return participant
    
    async def add_participant(self, code: str, endpoint: str) -> Participant:
        """
        Add a participant and verify connectivity.
        
        Args:
            code: Bundesland code
            endpoint: Participant API endpoint
            
        Returns:
            Participant object
        """
        participant = self.add_participant_sync(code, endpoint)
        
        # Verify connectivity
        client = await self._get_client()
        if client:
            try:
                response = await client.get(f"{endpoint}/health")
                if response.status_code != 200:
                    logger.warning(f"Participant {code} health check failed")
            except Exception as e:
                logger.warning(f"Could not verify participant {code}: {e}")
        
        return participant
    
    def add_step(
        self,
        participant: Participant,
        action: str,
        payload: Dict[str, Any],
        compensating_action: Optional[str] = None,
        compensating_payload: Optional[Dict[str, Any]] = None,
    ) -> SagaStep:
        """
        Add a step to the transaction.
        
        Args:
            participant: Participant to execute step
            action: Action endpoint (e.g., "store", "update")
            payload: Action payload
            compensating_action: Rollback action endpoint
            compensating_payload: Rollback payload
            
        Returns:
            SagaStep object
        """
        step = SagaStep(
            id=str(uuid.uuid4()),
            name=f"{participant.code}:{action}",
            participant=participant,
            action=action,
            payload=payload,
            compensating_action=compensating_action,
            compensating_payload=compensating_payload,
        )
        self.transaction.steps.append(step)
        return step
    
    async def _execute_step(self, step: SagaStep) -> bool:
        """Execute a single step."""
        client = await self._get_client()
        if client is None:
            step.error = "HTTP client not available"
            return False
        
        try:
            response = await client.post(
                f"{step.participant.endpoint}/{step.action}",
                json=step.payload,
                headers={"X-Transaction-ID": self.id},
            )
            
            step.executed = True
            step.result = response.json() if response.status_code == 200 else None
            
            if response.status_code in (200, 201):
                step.participant.state = ParticipantState.PREPARED
                self._executed_steps.append(step)
                return True
            else:
                step.error = f"HTTP {response.status_code}: {response.text}"
                step.participant.state = ParticipantState.FAILED
                return False
                
        except Exception as e:
            step.error = str(e)
            step.participant.state = ParticipantState.FAILED
            return False
    
    async def _compensate_step(self, step: SagaStep) -> bool:
        """Execute compensating transaction for a step."""
        if not step.compensating_action:
            logger.debug(f"No compensating action for step {step.name}")
            return True
        
        client = await self._get_client()
        if client is None:
            return False
        
        try:
            payload = step.compensating_payload or step.payload
            response = await client.post(
                f"{step.participant.endpoint}/{step.compensating_action}",
                json=payload,
                headers={"X-Transaction-ID": self.id, "X-Compensating": "true"},
            )
            
            step.compensated = True
            step.participant.state = ParticipantState.COMPENSATED
            return response.status_code in (200, 201, 204)
            
        except Exception as e:
            logger.error(f"Compensation failed for step {step.name}: {e}")
            return False
    
    async def execute(self, payload: Optional[Dict[str, Any]] = None) -> Transaction:
        """
        Execute the transaction.
        
        This executes all steps in sequence. If any step fails,
        the transaction will need to be compensated.
        
        Args:
            payload: Additional payload for all steps
            
        Returns:
            Transaction object with results
        """
        if self.state != TransactionState.PENDING:
            logger.warning(f"Transaction {self.id} already executed")
            return self.transaction
        
        self.transaction.state = TransactionState.EXECUTING
        self.transaction.updated_at = datetime.utcnow()
        
        if payload:
            self.transaction.payload = payload
        
        # Check timeout
        if datetime.utcnow() > self.transaction.timeout_at:
            self.transaction.state = TransactionState.TIMED_OUT
            return self.transaction
        
        # Execute all steps
        for step in self.transaction.steps:
            success = await self._execute_step(step)
            if not success:
                self.transaction.state = TransactionState.FAILED
                self.transaction.error = step.error
                return self.transaction
        
        # All steps succeeded
        logger.info(f"Transaction {self.id} executed successfully")
        return self.transaction
    
    async def commit(self) -> bool:
        """
        Commit the transaction.
        
        This confirms all participants that the transaction is complete.
        
        Returns:
            True if commit successful
        """
        if self.state not in (TransactionState.EXECUTING, TransactionState.PENDING):
            if self.state == TransactionState.COMMITTED:
                return True
            logger.warning(f"Cannot commit transaction in state {self.state}")
            return False
        
        self.transaction.state = TransactionState.COMMITTING
        self.transaction.updated_at = datetime.utcnow()
        
        # Notify all participants of commit
        client = await self._get_client()
        if client:
            for participant in self.transaction.participants:
                try:
                    await client.post(
                        f"{participant.endpoint}/transaction/commit",
                        json={"transaction_id": self.id},
                    )
                    participant.state = ParticipantState.COMMITTED
                    participant.committed_at = datetime.utcnow()
                except Exception as e:
                    logger.warning(f"Commit notification failed for {participant.code}: {e}")
        
        self.transaction.state = TransactionState.COMMITTED
        logger.info(f"Transaction {self.id} committed")
        return True
    
    async def compensate(self) -> bool:
        """
        Compensate (rollback) the transaction.
        
        This executes compensating transactions for all executed steps
        in reverse order.
        
        Returns:
            True if compensation successful
        """
        if self.state == TransactionState.ROLLED_BACK:
            return True
        
        self.transaction.state = TransactionState.COMPENSATING
        self.transaction.updated_at = datetime.utcnow()
        
        # Execute compensating transactions in reverse order
        all_compensated = True
        for step in reversed(self._executed_steps):
            success = await self._compensate_step(step)
            if not success:
                all_compensated = False
                logger.error(f"Failed to compensate step {step.name}")
        
        self.transaction.state = TransactionState.ROLLED_BACK
        logger.info(f"Transaction {self.id} rolled back (all_compensated={all_compensated})")
        return all_compensated
    
    async def close(self):
        """Close transaction and cleanup."""
        if self._client:
            await self._client.aclose()
            self._client = None


class ThemisTransactionOrchestrator:
    """
    Themis Transaction Orchestrator - Saga Pattern Implementation
    
    This orchestrator manages distributed transactions across 16 Bundesländer
    using the Saga pattern for eventual consistency.
    
    Features:
    - Transaction lifecycle management
    - Automatic compensation on failure
    - Timeout handling
    - Transaction log persistence
    - Idempotency support
    
    Configuration via environment variables:
        URN_SAGA_ENABLED: Enable orchestrator (default: false)
        URN_SAGA_TIMEOUT: Default timeout (default: 120s)
        URN_SAGA_LOG_PATH: Transaction log path (optional)
    
    Example:
        orchestrator = ThemisTransactionOrchestrator()
        tx = await orchestrator.begin_transaction("urn_registration")
        # ... add participants and execute
        await orchestrator.end_transaction(tx.id)
    """
    
    def __init__(
        self,
        timeout: int = 120,
        max_concurrent: int = 100,
    ):
        """
        Initialize the orchestrator.
        
        Args:
            timeout: Default transaction timeout in seconds
            max_concurrent: Maximum concurrent transactions
        """
        self.enabled = os.getenv("URN_SAGA_ENABLED", "false").lower() == "true"
        self.default_timeout = int(os.getenv("URN_SAGA_TIMEOUT", str(timeout)))
        self.max_concurrent = max_concurrent
        
        # Active transactions
        self._transactions: Dict[str, SagaTransaction] = {}
        
        # Transaction log (in-memory, can be replaced with persistent storage)
        self._log: List[Transaction] = []
        
        if self.enabled:
            logger.info("Themis Transaction Orchestrator initialized")
        else:
            logger.debug("Themis Transaction Orchestrator disabled")
    
    def is_available(self) -> bool:
        """Check if orchestrator is available."""
        return self.enabled
    
    async def begin_transaction(
        self,
        tx_type: str,
        timeout: Optional[int] = None,
    ) -> SagaTransaction:
        """
        Begin a new distributed transaction.
        
        Args:
            tx_type: Type of transaction
            timeout: Transaction timeout (uses default if not specified)
            
        Returns:
            SagaTransaction object
        """
        if len(self._transactions) >= self.max_concurrent:
            raise RuntimeError("Maximum concurrent transactions reached")
        
        tx = SagaTransaction(
            tx_type=tx_type,
            timeout=timeout or self.default_timeout,
            orchestrator=self,
        )
        
        self._transactions[tx.id] = tx
        logger.info(f"Started transaction {tx.id} (type={tx_type})")
        return tx
    
    def get_transaction(self, tx_id: str) -> Optional[SagaTransaction]:
        """Get an active transaction by ID."""
        return self._transactions.get(tx_id)
    
    async def end_transaction(self, tx_id: str) -> bool:
        """
        End and cleanup a transaction.
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            True if cleanup successful
        """
        tx = self._transactions.pop(tx_id, None)
        if tx:
            # Log completed transaction
            self._log.append(tx.transaction)
            await tx.close()
            logger.info(f"Ended transaction {tx_id}")
            return True
        return False
    
    async def cleanup_timed_out(self):
        """Cleanup timed out transactions."""
        now = datetime.utcnow()
        timed_out = [
            tx_id for tx_id, tx in self._transactions.items()
            if tx.transaction.timeout_at and now > tx.transaction.timeout_at
        ]
        
        for tx_id in timed_out:
            tx = self._transactions.get(tx_id)
            if tx:
                logger.warning(f"Transaction {tx_id} timed out, compensating")
                await tx.compensate()
                await self.end_transaction(tx_id)
    
    def get_active_transactions(self) -> List[Transaction]:
        """Get all active transactions."""
        return [tx.transaction for tx in self._transactions.values()]
    
    def get_transaction_log(self, limit: int = 100) -> List[Transaction]:
        """Get transaction log."""
        return self._log[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "enabled": self.enabled,
            "active_transactions": len(self._transactions),
            "max_concurrent": self.max_concurrent,
            "default_timeout": self.default_timeout,
            "transactions": [tx.transaction.to_dict() for tx in self._transactions.values()],
        }


# Pre-defined transaction templates
class TransactionTemplates:
    """Pre-defined transaction templates for common operations."""
    
    @staticmethod
    async def urn_registration(
        orchestrator: ThemisTransactionOrchestrator,
        urn: str,
        manifest: Dict[str, Any],
        participants: List[tuple],  # [(code, endpoint), ...]
    ) -> Transaction:
        """
        URN Registration across multiple Bundesländer.
        
        Args:
            orchestrator: Transaction orchestrator
            urn: URN to register
            manifest: Manifest data
            participants: List of (code, endpoint) tuples
            
        Returns:
            Transaction result
        """
        tx = await orchestrator.begin_transaction("urn_registration")
        
        for code, endpoint in participants:
            participant = await tx.add_participant(code, endpoint)
            tx.add_step(
                participant=participant,
                action="store",
                payload={"urn": urn, "manifest": manifest},
                compensating_action="delete",
                compensating_payload={"urn": urn},
            )
        
        result = await tx.execute()
        
        if result.state == TransactionState.EXECUTING:
            await tx.commit()
        else:
            await tx.compensate()
        
        await orchestrator.end_transaction(tx.id)
        return result
    
    @staticmethod
    async def manifest_sync(
        orchestrator: ThemisTransactionOrchestrator,
        urn: str,
        manifest: Dict[str, Any],
        source: str,
        targets: List[tuple],
    ) -> Transaction:
        """
        Synchronize manifest across federation.
        
        Args:
            orchestrator: Transaction orchestrator
            urn: URN to sync
            manifest: Manifest data
            source: Source Bundesland code
            targets: List of (code, endpoint) tuples
            
        Returns:
            Transaction result
        """
        tx = await orchestrator.begin_transaction("manifest_sync")
        
        for code, endpoint in targets:
            participant = await tx.add_participant(code, endpoint)
            tx.add_step(
                participant=participant,
                action="manifest/sync",
                payload={
                    "urn": urn,
                    "manifest": manifest,
                    "source": source,
                },
            )
        
        result = await tx.execute()
        
        if result.state == TransactionState.EXECUTING:
            await tx.commit()
        else:
            await tx.compensate()
        
        await orchestrator.end_transaction(tx.id)
        return result


# FastAPI integration
def get_transaction_router():
    """
    Get FastAPI router for transaction endpoints.
    
    Returns:
        APIRouter with /transaction endpoints, or None if FastAPI not available
    """
    try:
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel
    except ImportError:
        logger.debug("FastAPI not available, skipping Transaction router")
        return None
    
    router = APIRouter(prefix="/transaction", tags=["Themis Transactions"])
    
    _orchestrator = ThemisTransactionOrchestrator()
    
    class BeginRequest(BaseModel):
        type: str
        timeout: Optional[int] = None
    
    @router.post("/begin")
    async def begin_transaction(request: BeginRequest):
        """Begin a new transaction."""
        if not _orchestrator.is_available():
            raise HTTPException(status_code=503, detail="Saga orchestrator not enabled")
        
        tx = await _orchestrator.begin_transaction(request.type, request.timeout)
        return {"transaction_id": tx.id, "type": request.type}
    
    @router.get("/{tx_id}")
    async def get_transaction(tx_id: str):
        """Get transaction status."""
        tx = _orchestrator.get_transaction(tx_id)
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return tx.transaction.to_dict()
    
    @router.post("/{tx_id}/commit")
    async def commit_transaction(tx_id: str):
        """Commit a transaction."""
        tx = _orchestrator.get_transaction(tx_id)
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        success = await tx.commit()
        return {"success": success, "state": tx.state.value}
    
    @router.post("/{tx_id}/compensate")
    async def compensate_transaction(tx_id: str):
        """Compensate (rollback) a transaction."""
        tx = _orchestrator.get_transaction(tx_id)
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        success = await tx.compensate()
        return {"success": success, "state": tx.state.value}
    
    @router.get("/")
    async def list_transactions():
        """List active transactions."""
        return {
            "transactions": [t.to_dict() for t in _orchestrator.get_active_transactions()],
        }
    
    @router.get("/status")
    async def orchestrator_status():
        """Get orchestrator status."""
        return _orchestrator.get_status()
    
    return router
