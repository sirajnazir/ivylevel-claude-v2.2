"""
IvyQuest v15.0 Agent Service Configuration
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
    service_version: str = "15.0.0"
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


# =============================================================================
# HYBRID ARCHITECTURE v4.1 FEATURE FLAGS
# =============================================================================
FEATURE_FLAGS = {
    # -------------------------------------------------------------------------
    # v4.0 Core Flags
    # -------------------------------------------------------------------------
    "use_profile_inference": True,      # Enable profile-based spike/archetype inference
    "use_strategic_routing": True,      # Enable strategic routing (BUILD_FRESH/OPTIMIZE/REFRAME/URGENT)
    "enable_guardrails": True,          # Enable output validation against knowledge base

    # -------------------------------------------------------------------------
    # v4.1 Phase 1: Enhanced Guardrails (ENABLED)
    # -------------------------------------------------------------------------
    "guardrails_strict_mode": False,    # If True, fail on any warning (not just errors)
    "guardrails_log_metrics": True,     # Log validation metrics for analysis

    # -------------------------------------------------------------------------
    # v4.1 Phase 2: ReAct Self-Correction (A/B TEST)
    # -------------------------------------------------------------------------
    "enable_react": True,               # Master switch for ReAct framework (ENABLED FOR TESTING)
    "react_max_cycles": 3,              # Maximum correction cycles before accepting output
    "react_min_confidence": 0.70,       # Minimum quality score threshold (0-1)
    "react_enable_for_agents": [        # Which agents get ReAct wrapping
        "Extracurriculars",
        "Awards",
        "Programs",
        "GamePlan",
    ],
    "react_wrap_sub_agents": True,      # v5.0: Wrap EC/Awards/Programs in their own ReAct cycles

    # -------------------------------------------------------------------------
    # v4.1 Phase 3: Voice & Benchmark (FUTURE)
    # -------------------------------------------------------------------------
    "enable_voice_validation": False,   # Enable Jenny voice compliance validation
    "voice_min_score": 70,              # Minimum voice compliance score (0-100)
    "enable_golden_benchmark": False,   # Enable golden example comparison
    "golden_min_similarity": 0.6,       # Minimum similarity to golden example (0-1)

    # -------------------------------------------------------------------------
    # v5.0: EC Generation Engine - Core 4 Pillars + 10 Dimensions (Always On)
    # -------------------------------------------------------------------------
    # NOTE: This is the core EC generation methodology, always enabled.
    # No feature flag needed - this is the foundational framework.
    "ec_engine_max_activities": 3,           # Max activities to generate per analysis
    "ec_engine_require_only_they_pass": True,  # Require "Only They" test validation
    "ec_engine_min_dimensions": 8,           # Minimum dimensions required (out of 10)
    "ec_engine_min_pillars": 2,              # Minimum pillars required per activity

    # -------------------------------------------------------------------------
    # v5.0: Coach Augmentation Settings
    # -------------------------------------------------------------------------
    "coach_augmentations_enabled": True,     # Allow coach-specific methodology layers
    "default_coach_augmentation": None,      # Default coach augmentation to apply (if any)

    # -------------------------------------------------------------------------
    # A/B Testing Configuration
    # -------------------------------------------------------------------------
    "react_ab_test_enabled": False,     # Enable A/B testing for ReAct
    "react_ab_test_percentage": 0.10,   # % of traffic to treatment group (0-1)

    # -------------------------------------------------------------------------
    # Verbose Logging (for testing/debugging)
    # -------------------------------------------------------------------------
    "react_verbose_logging": True,      # Enable detailed console output for ReAct cycles
    "log_react_cycles": True,           # Log each THINK-ACT-OBSERVE-LEARN cycle
    "log_validation_metrics": True,     # Log guardrails validation metrics
}


# =============================================================================
# PHASE CONFIGURATION HELPERS
# =============================================================================

def get_phase_config() -> dict:
    """
    Get current phase configuration based on feature flags.

    Returns dict with:
        - phase: int (1, 2, or 3)
        - name: str
        - description: str
        - features_enabled: list
    """
    if FEATURE_FLAGS.get("enable_golden_benchmark") or FEATURE_FLAGS.get("enable_voice_validation"):
        return {
            "phase": 3,
            "name": "Full ReAct + Voice + Golden",
            "description": "Complete v4.1 with all quality assurance features",
            "features_enabled": [
                "guardrails",
                "react",
                "voice_validation",
                "golden_benchmark",
            ],
        }
    elif FEATURE_FLAGS.get("enable_react"):
        return {
            "phase": 2,
            "name": "ReAct A/B Test",
            "description": "ReAct self-correction with A/B testing",
            "features_enabled": [
                "guardrails",
                "react",
            ],
        }
    else:
        return {
            "phase": 1,
            "name": "Guardrails Only",
            "description": "Output validation without self-correction",
            "features_enabled": [
                "guardrails",
            ],
        }


def is_react_enabled_for_agent(agent_name: str) -> bool:
    """Check if ReAct is enabled for a specific agent."""
    if not FEATURE_FLAGS.get("enable_react", False):
        return False

    enabled_agents = FEATURE_FLAGS.get("react_enable_for_agents", [])
    return agent_name in enabled_agents


def get_react_config() -> dict:
    """Get ReAct configuration."""
    return {
        "enabled": FEATURE_FLAGS.get("enable_react", False),
        "max_cycles": FEATURE_FLAGS.get("react_max_cycles", 3),
        "min_confidence": FEATURE_FLAGS.get("react_min_confidence", 0.70),
        "enabled_agents": FEATURE_FLAGS.get("react_enable_for_agents", []),
        "ab_test_enabled": FEATURE_FLAGS.get("react_ab_test_enabled", False),
        "ab_test_percentage": FEATURE_FLAGS.get("react_ab_test_percentage", 0.10),
    }


def get_quality_thresholds() -> dict:
    """Get quality thresholds for validation."""
    return {
        "min_confidence": FEATURE_FLAGS.get("react_min_confidence", 0.70),
        "min_voice_score": FEATURE_FLAGS.get("voice_min_score", 70),
        "min_golden_similarity": FEATURE_FLAGS.get("golden_min_similarity", 0.6),
    }
