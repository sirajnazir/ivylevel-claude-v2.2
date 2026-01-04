"""
IvyQuest v10.0 Agent Service Configuration
==========================================
Loads environment variables and provides typed settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    service_name: str = "ivyquest-agents"
    service_version: str = "10.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = Field(default=8001, alias="AGENT_SERVICE_PORT")

    # Supabase
    supabase_url: str = Field(..., alias="NEXT_PUBLIC_SUPABASE_URL")
    supabase_anon_key: str = Field(..., alias="NEXT_PUBLIC_SUPABASE_ANON_KEY")
    supabase_service_key: str = Field(..., alias="SUPABASE_SERVICE_ROLE_KEY")

    # OpenAI (used by Agno, LangGraph, AutoGen)
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    agent_primary_model: str = Field(default="gpt-4o", alias="AGENT_PRIMARY_MODEL")
    agent_fast_model: str = Field(default="gpt-4o-mini", alias="AGENT_FAST_MODEL")

    # LangChain/LangGraph
    langchain_api_key: Optional[str] = Field(default=None, alias="LANGCHAIN_API_KEY")
    langchain_tracing_v2: bool = Field(default=True, alias="LANGCHAIN_TRACING_V2")
    langchain_project: str = Field(default="ivyquest-v10", alias="LANGCHAIN_PROJECT")

    # Feature Flags
    enable_agents: bool = Field(default=False, alias="ENABLE_AGENTS")
    enable_execution_agent: bool = Field(default=False, alias="ENABLE_EXECUTION_AGENT")
    enable_crisis_alchemy: bool = Field(default=False, alias="ENABLE_CRISIS_ALCHEMY")
    enable_cri_scoring: bool = Field(default=False, alias="ENABLE_CRI_SCORING")
    enable_event_bus: bool = Field(default=False, alias="ENABLE_EVENT_BUS")
    enable_state_versioning: bool = Field(default=False, alias="ENABLE_STATE_VERSIONING")

    # HITL Configuration
    hitl_timeout_hours: float = Field(default=1.0, alias="HITL_TIMEOUT_HOURS")
    hitl_notification_email: Optional[str] = Field(default=None, alias="HITL_NOTIFICATION_EMAIL")

    # Blocker Detection
    blocker_threshold_days: int = 5

    # Strategic Overwhelm
    overwhelm_factor: float = 1.4  # Assign 1.4x tasks
    target_completion_rate: float = 0.73  # Expect 73% completion

    # CRI Configuration
    cri_barrier_boost: float = 1.2  # 20% boost for overcoming barriers
    cri_max_value: float = 3.0

    class Config:
        env_file = "../.env.local"  # Load from parent directory
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience accessor
settings = get_settings()


# Agent autonomy levels
class AutonomyLevel:
    """Agent autonomy levels per v10.0 spec."""
    FULL = "full"      # Deterministic matching/compute (Award fit, CRI calc)
    HIGH = "high"      # Synthesis with context (Narrative DNA, archetype)
    MEDIUM = "medium"  # Reframing/debate (Constraint Forge, micro-edits)
    LOW = "low"        # Crises/human-sensitive (Crisis Alchemy)


# Huda benchmark targets
class HudaBenchmarks:
    """Target metrics validated against Huda case study."""
    SSR_TARGET = 0.85           # >85% Student Success Rate
    CRI_TARGET = 1.2            # >1.2 Context Relativity Index
    PROJECT_COMPLETION = 0.80   # >80% project completion
    CRISIS_RECOVERY_HOURS = 72  # <72 hours recovery time
    TASK_COMPLETION = 0.70      # >70% task completion (Strategic Overwhelm)
    AWARD_WIN_RATE = 0.40       # >40% award win rate
    EDS_MAX = 50                # <50 Execution Debt Score

    # Huda actual results
    HUDA_SSR = 1.0              # 100%
    HUDA_CRI = 1.35
    HUDA_PROJECT_COMPLETION = 1.0
    HUDA_CRISIS_RECOVERY = 2    # <2 hours
    HUDA_TASK_COMPLETION = 0.73
    HUDA_AWARD_WIN_RATE = 0.625  # 5/8
    HUDA_EDS = 12
