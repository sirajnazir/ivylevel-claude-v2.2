"""
G2: Approval Gates Pattern - Phase 2A

Human-in-the-loop approval for high-stakes agent actions.
Pause agent execution for human approval before risky actions.

Usage:
    from middleware.approval import ApprovalGateManager, ApprovalCategory

    manager = ApprovalGateManager(supabase_client)
    rule = manager.check_requires_approval("change_college_list")
    if rule:
        request = await manager.request_approval(...)
        decision = await manager.await_approval(request)
"""

from .types import (
    ApprovalCategory,
    ApprovalUrgency,
    ApprovalStatus,
    ApprovalRequest,
    ApprovalDecision,
    ApprovalRule,
)
from .gates import (
    ApprovalGateManager,
    DEFAULT_APPROVAL_RULES,
    requires_approval,
)

__all__ = [
    # Types
    "ApprovalCategory",
    "ApprovalUrgency",
    "ApprovalStatus",
    "ApprovalRequest",
    "ApprovalDecision",
    "ApprovalRule",
    # Manager
    "ApprovalGateManager",
    "DEFAULT_APPROVAL_RULES",
    "requires_approval",
]
