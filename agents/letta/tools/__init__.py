"""
Letta Tools Module
==================

Custom tools for Letta agents that bridge to existing IvyLevel infrastructure.

Tools:
- techniques.py: Bridge to AssetSelector for 139 coaching techniques
- hitl.py: Human-in-the-loop approval workflow
- monitoring.py: Deadline checking and opportunity matching
- database.py: Supabase read operations for student data
"""

from .techniques import (
    search_techniques,
    get_technique_by_id,
    get_top_techniques_for_domain,
)
from .hitl import (
    request_approval,
    check_approval_status,
    list_pending_approvals,
)
from .monitoring import (
    check_upcoming_deadlines,
    match_opportunities,
    get_execution_state,
)
from .database import (
    get_student_profile,
    get_active_gameplan,
    get_recent_interactions,
    get_goal_progress,
)

__all__ = [
    # Techniques
    "search_techniques",
    "get_technique_by_id",
    "get_top_techniques_for_domain",
    # HITL
    "request_approval",
    "check_approval_status",
    "list_pending_approvals",
    # Monitoring
    "check_upcoming_deadlines",
    "match_opportunities",
    "get_execution_state",
    # Database
    "get_student_profile",
    "get_active_gameplan",
    "get_recent_interactions",
    "get_goal_progress",
]
