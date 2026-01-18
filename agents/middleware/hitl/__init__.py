"""
HITL (Human-in-the-Loop) Module - Phase 2B

NEW MODULE - Does not modify existing v7.0 code.
"""

from .atomic_operations_v8 import (
    AtomicOperation,
    AtomicOperationStatus,
    AtomicOperationResult,
    AtomicOperationExecutor,
)

__all__ = [
    "AtomicOperation",
    "AtomicOperationStatus",
    "AtomicOperationResult",
    "AtomicOperationExecutor",
]
