"""
Letta Multi-Agent Integration for IvyLevel
==========================================

This module provides Letta-based autonomous agent capabilities for IvyLevel's
college admissions coaching platform.

Architecture:
- Orchestrator: Routes conversations to specialist agents
- GamePlan Agent: Strategic planning and goal setting
- Execution Agent: Task tracking, nudges, deadline management
- Awards Agent: Award recommendations and tracking
- Essay Agent: Narrative coaching and essay feedback
- Assessment Agent: DORMANT - Future Phase 2 (quarterly reassessment)

Key Principles:
- ADDITIVE ONLY: This module does NOT modify any existing code
- FEATURE FLAGS: All functionality gated by LETTA_ENABLED and per-agent flags
- BRIDGE PATTERN: Reuses existing AssetSelector, APScheduler, AutonomousMonitorService
- ISOLATED DATA: All tables prefixed with letta_*, all endpoints under /api/letta/*

Usage:
    from letta import LettaClient, is_letta_enabled

    if is_letta_enabled():
        client = LettaClient()
        response = await client.chat(profile_id, message)
"""

from .config import (
    LETTA_CONFIG,
    is_letta_enabled,
    is_agent_enabled,
)
from .client import LettaClientWrapper

__all__ = [
    "LETTA_CONFIG",
    "is_letta_enabled",
    "is_agent_enabled",
    "LettaClientWrapper",
]

__version__ = "1.0.0"
