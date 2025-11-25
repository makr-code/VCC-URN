# VCC-URN Integrations
# Phase 3: VCC Ecosystem Integration
#
# This package provides integration with other VCC components:
# - Themis AQL: VCC-native query language (replaces GraphQL)
# - Themis Gateway: Federation gateway for 16 Bundesländer
# - Themis Transactions: Saga orchestrator for distributed consistency
# - Veritas: Graph-DB integration for URN storage
#
# All integrations are:
# - 100% Open-Source
# - On-Premise deployable
# - Vendor-lock-in free
# - DSGVO & BSI compliant

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .themis_aql import ThemisAQLClient
    from .themis_gateway import ThemisGateway
    from .themis_transactions import ThemisTransactionOrchestrator
    from .veritas import VeritasClient

__all__ = [
    "ThemisAQLClient",
    "ThemisGateway",
    "ThemisTransactionOrchestrator",
    "VeritasClient",
]
