"""
Proactive Autonomy Configuration v10.0
======================================

Feature flags and configuration for proactive coaching capabilities.
All features are DISABLED by default for safe rollout.

Environment Variables:
- PROACTIVE_ENABLED: Master switch (default: false)
- PROACTIVE_OPPORTUNITY_MATCH: Hourly opportunity matching (default: false)
- PROACTIVE_DEADLINE_ALERTS: Deadline proximity alerts (default: false)
- PROACTIVE_STALL_DETECTION: Project stall detection (default: false)
- PROACTIVE_INACTIVITY_CHECK: Student inactivity check-ins (default: false)
- PROACTIVE_OUTCOME_TRACKING: Track wins/losses for learning (default: false)
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any
import structlog

logger = structlog.get_logger()


@dataclass
class ProactiveConfig:
    """Configuration for proactive autonomy features."""

    # Master switch - ALL features require this to be true
    enabled: bool = field(
        default_factory=lambda: os.getenv("PROACTIVE_ENABLED", "false").lower() == "true"
    )

    # Individual feature flags
    opportunity_match: bool = field(
        default_factory=lambda: os.getenv("PROACTIVE_OPPORTUNITY_MATCH", "false").lower() == "true"
    )

    deadline_alerts: bool = field(
        default_factory=lambda: os.getenv("PROACTIVE_DEADLINE_ALERTS", "false").lower() == "true"
    )

    stall_detection: bool = field(
        default_factory=lambda: os.getenv("PROACTIVE_STALL_DETECTION", "false").lower() == "true"
    )

    inactivity_check: bool = field(
        default_factory=lambda: os.getenv("PROACTIVE_INACTIVITY_CHECK", "false").lower() == "true"
    )

    outcome_tracking: bool = field(
        default_factory=lambda: os.getenv("PROACTIVE_OUTCOME_TRACKING", "false").lower() == "true"
    )

    # Scheduling configuration
    opportunity_match_interval_hours: int = field(
        default_factory=lambda: int(os.getenv("PROACTIVE_OPPORTUNITY_INTERVAL", "1"))
    )

    deadline_check_interval_hours: int = field(
        default_factory=lambda: int(os.getenv("PROACTIVE_DEADLINE_INTERVAL", "6"))
    )

    stall_check_daily_hour: int = field(
        default_factory=lambda: int(os.getenv("PROACTIVE_STALL_HOUR", "9"))  # 9 AM
    )

    def is_enabled(self) -> bool:
        """Check if proactive features are enabled globally."""
        return self.enabled

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled."""
        if not self.enabled:
            return False

        feature_map = {
            "opportunity_match": self.opportunity_match,
            "deadline_alerts": self.deadline_alerts,
            "stall_detection": self.stall_detection,
            "inactivity_check": self.inactivity_check,
            "outcome_tracking": self.outcome_tracking,
        }

        return feature_map.get(feature, False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for logging/debugging."""
        return {
            "enabled": self.enabled,
            "features": {
                "opportunity_match": self.opportunity_match,
                "deadline_alerts": self.deadline_alerts,
                "stall_detection": self.stall_detection,
                "inactivity_check": self.inactivity_check,
                "outcome_tracking": self.outcome_tracking,
            },
            "intervals": {
                "opportunity_match_hours": self.opportunity_match_interval_hours,
                "deadline_check_hours": self.deadline_check_interval_hours,
                "stall_check_hour": self.stall_check_daily_hour,
            },
        }


# Global configuration singleton
PROACTIVE_CONFIG = ProactiveConfig()


def is_proactive_enabled() -> bool:
    """
    Check if proactive features are enabled globally.

    Returns:
        True if PROACTIVE_ENABLED=true
    """
    return PROACTIVE_CONFIG.is_enabled()


def is_feature_enabled(feature: str) -> bool:
    """
    Check if a specific proactive feature is enabled.

    Args:
        feature: Feature name (opportunity_match, deadline_alerts, etc.)

    Returns:
        True if the feature is enabled (requires PROACTIVE_ENABLED=true)
    """
    return PROACTIVE_CONFIG.is_feature_enabled(feature)


# Log configuration on module load
logger.info(
    "proactive_config_loaded",
    enabled=PROACTIVE_CONFIG.enabled,
    features=PROACTIVE_CONFIG.to_dict()["features"],
)
