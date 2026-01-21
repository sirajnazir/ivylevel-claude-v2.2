"""
Letta Configuration
===================

Configuration constants and feature flags for Letta integration.

All feature flags default to False (disabled) for safe rollout.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AgentType(str, Enum):
    """Letta agent types."""
    ORCHESTRATOR = "orchestrator"
    GAMEPLAN = "gameplan"
    EXECUTION = "execution"
    AWARDS = "awards"
    ESSAY = "essay"
    ASSESSMENT = "assessment"  # DORMANT


class AgentStatus(str, Enum):
    """Agent operational status."""
    ACTIVE = "active"
    DORMANT = "dormant"
    DISABLED = "disabled"


@dataclass
class AgentConfig:
    """Configuration for a single Letta agent."""
    name: str
    agent_type: AgentType
    status: AgentStatus
    env_flag: str
    model: str = "gpt-4o"
    description: str = ""
    tags: list = field(default_factory=list)

    def is_enabled(self) -> bool:
        """Check if this agent is enabled via environment variable."""
        if self.status == AgentStatus.DORMANT:
            return False
        return os.getenv(self.env_flag, "false").lower() == "true"


@dataclass
class LettaConfig:
    """Master configuration for Letta integration."""

    # API Configuration
    api_key: str = field(default_factory=lambda: os.getenv("LETTA_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.getenv("LETTA_BASE_URL", "https://api.letta.com"))
    org_id: Optional[str] = field(default_factory=lambda: os.getenv("LETTA_ORG_ID"))

    # Master Feature Flag
    enabled: bool = field(default_factory=lambda: os.getenv("LETTA_ENABLED", "false").lower() == "true")

    # Memory Configuration
    memory_block_limit: int = 5000  # Letta default
    memory_sync_interval_seconds: int = 300  # 5 minutes

    # Agent Configurations
    agents: Dict[AgentType, AgentConfig] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize agent configurations."""
        self.agents = {
            AgentType.ORCHESTRATOR: AgentConfig(
                name="Orchestrator",
                agent_type=AgentType.ORCHESTRATOR,
                status=AgentStatus.ACTIVE,
                env_flag="LETTA_ORCHESTRATOR_ENABLED",
                description="Routes conversations to appropriate specialist agents",
                tags=["supervisor", "router"],
            ),
            AgentType.GAMEPLAN: AgentConfig(
                name="GamePlan Specialist",
                agent_type=AgentType.GAMEPLAN,
                status=AgentStatus.ACTIVE,
                env_flag="LETTA_GAMEPLAN_ENABLED",
                description="Strategic planning, goal setting, milestone tracking",
                tags=["specialist", "strategy"],
            ),
            AgentType.EXECUTION: AgentConfig(
                name="Execution Specialist",
                agent_type=AgentType.EXECUTION,
                status=AgentStatus.ACTIVE,
                env_flag="LETTA_EXECUTION_ENABLED",
                description="Task tracking, nudges, deadline management",
                tags=["specialist", "execution"],
            ),
            AgentType.AWARDS: AgentConfig(
                name="Awards Specialist",
                agent_type=AgentType.AWARDS,
                status=AgentStatus.ACTIVE,
                env_flag="LETTA_AWARDS_ENABLED",
                description="Award recommendations, scholarship tracking",
                tags=["specialist", "awards"],
            ),
            AgentType.ESSAY: AgentConfig(
                name="Essay Specialist",
                agent_type=AgentType.ESSAY,
                status=AgentStatus.ACTIVE,
                env_flag="LETTA_ESSAY_ENABLED",
                description="Narrative coaching, essay feedback, story development",
                tags=["specialist", "essay"],
            ),
            AgentType.ASSESSMENT: AgentConfig(
                name="Assessment Specialist",
                agent_type=AgentType.ASSESSMENT,
                status=AgentStatus.DORMANT,  # DORMANT - Phase 2
                env_flag="LETTA_ASSESSMENT_ENABLED",
                description="DORMANT - Phase 2: Quarterly reassessment, pattern analysis",
                tags=["specialist", "assessment", "dormant"],
            ),
        }

    def is_enabled(self) -> bool:
        """Check if Letta is enabled globally."""
        return self.enabled and bool(self.api_key)

    def get_agent_config(self, agent_type: AgentType) -> AgentConfig:
        """Get configuration for a specific agent type."""
        return self.agents.get(agent_type)

    def get_active_agents(self) -> Dict[AgentType, AgentConfig]:
        """Get all agents that are not dormant."""
        return {
            k: v for k, v in self.agents.items()
            if v.status != AgentStatus.DORMANT
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        return {
            "enabled": self.enabled,
            "base_url": self.base_url,
            "has_api_key": bool(self.api_key),
            "org_id": self.org_id,
            "memory_block_limit": self.memory_block_limit,
            "agents": {
                k.value: {
                    "name": v.name,
                    "status": v.status.value,
                    "enabled": v.is_enabled(),
                }
                for k, v in self.agents.items()
            }
        }


# Global configuration singleton
LETTA_CONFIG = LettaConfig()


def is_letta_enabled() -> bool:
    """Check if Letta integration is enabled globally.

    Returns:
        True if LETTA_ENABLED=true and LETTA_API_KEY is set
    """
    return LETTA_CONFIG.is_enabled()


def is_agent_enabled(agent_type: AgentType) -> bool:
    """Check if a specific agent type is enabled.

    Args:
        agent_type: The type of agent to check

    Returns:
        True if the agent is enabled (not dormant and flag is true)
    """
    if not is_letta_enabled():
        return False

    config = LETTA_CONFIG.get_agent_config(agent_type)
    if config is None:
        return False

    return config.is_enabled()


# Memory block names (constants for consistency)
MEMORY_BLOCK_NAMES = {
    "student_profile": "student_profile",
    "coaching_history": "coaching_history",
    "active_gameplan": "active_gameplan",
    "outcome_tracker": "outcome_tracker",
    "deadline_state": "deadline_state",
}


# Database table names (all prefixed with letta_)
LETTA_TABLES = {
    "agent_registry": "letta_agent_registry",
    "memory_snapshots": "letta_memory_snapshots",
    "approval_queue": "letta_approval_queue",
    "transition_log": "letta_transition_log",
}


# API endpoint prefix
LETTA_API_PREFIX = "/api/letta"
