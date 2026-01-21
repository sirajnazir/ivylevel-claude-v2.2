"""
IvyQuest Proactive Autonomy Module v10.0
========================================

This module adds proactive coaching capabilities to the existing agent system.
All features are feature-flagged and disabled by default for safe rollout.

Components:
- config.py: Feature flags and configuration
- opportunity_matcher.py: Hourly opportunity matching job
- scheduler.py: Registration of proactive scheduler jobs

Usage:
    from proactive import is_proactive_enabled, register_proactive_jobs

    if is_proactive_enabled():
        register_proactive_jobs(scheduler, supabase_client)

Feature Flags (all default to FALSE):
- PROACTIVE_ENABLED: Master switch for proactive features
- PROACTIVE_OPPORTUNITY_MATCH: Enable hourly opportunity matching
- PROACTIVE_DEADLINE_ALERTS: Enable deadline proximity alerts
- PROACTIVE_STALL_DETECTION: Enable project stall detection

IMPORTANT: This module is ADDITIVE ONLY. It does not modify any existing code.
"""

from .config import (
    PROACTIVE_CONFIG,
    is_proactive_enabled,
    is_feature_enabled,
)
from .scheduler import register_proactive_jobs

__all__ = [
    "PROACTIVE_CONFIG",
    "is_proactive_enabled",
    "is_feature_enabled",
    "register_proactive_jobs",
]
