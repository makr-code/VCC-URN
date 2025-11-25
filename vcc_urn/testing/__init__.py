# VCC-URN Testing
# Contract Testing and Quality Assurance
#
# This package provides testing utilities including:
# - Contract Testing (Pact) for API contracts
# - Performance Testing utilities
# - Integration test helpers
#
# All testing tools are:
# - 100% Open-Source
# - On-Premise capable
# - Vendor-lock-in free

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .contract_testing import PactContractTest

__all__ = [
    "PactContractTest",
]
