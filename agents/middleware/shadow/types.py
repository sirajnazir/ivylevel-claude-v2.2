"""
G5: Human Shadow Mode - Type Definitions

Types for the human shadow mode pattern.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ShadowMode(str, Enum):
    """Shadow mode levels."""
    OFF = "off"                    # No shadow, agent acts autonomously
    ADVISORY = "advisory"          # Coach sees proposals, agent proceeds anyway
    REVIEW = "review"              # Coach must review, can modify
    APPROVAL = "approval"          # Coach must explicitly approve


class ShadowProposal(BaseModel):
    """An agent proposal for coach review."""
    proposal_id: str
    profile_id: str
    agent_name: str

    # What the agent wants to do/say
    proposal_type: str  # "message", "action", "plan_change"
    proposed_content: str
    proposed_payload: Dict[str, Any] = Field(default_factory=dict)

    # Context for reviewer
    student_message: Optional[str] = None
    relevant_context: Dict[str, Any] = Field(default_factory=dict)
    agent_reasoning: str = ""
    confidence_score: float = Field(default=0.7, ge=0.0, le=1.0)

    # Alternatives
    alternative_responses: List[Dict[str, Any]] = Field(default_factory=list)

    # Status
    shadow_mode: ShadowMode
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[str] = None

    # Outcome
    final_content: Optional[str] = None
    modifications_made: List[str] = Field(default_factory=list)
    coach_notes: Optional[str] = None


class ShadowReview(BaseModel):
    """Coach's review of a proposal."""
    proposal_id: str
    reviewer_id: str

    # Decision
    action: str  # "approve", "modify", "reject", "escalate"

    # Modifications
    modified_content: Optional[str] = None
    modifications_description: List[str] = Field(default_factory=list)

    # Feedback for agent learning
    quality_rating: Optional[int] = None  # 1-5
    feedback_for_agent: Optional[str] = None

    # Timing
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)


class ShadowConfig(BaseModel):
    """Configuration for shadow mode per student/agent."""
    profile_id: Optional[str] = None  # None = global default
    agent_name: Optional[str] = None  # None = all agents

    shadow_mode: ShadowMode = ShadowMode.ADVISORY

    # Conditions to upgrade shadow level
    upgrade_to_review_if: List[str] = Field(default_factory=list)
    upgrade_to_approval_if: List[str] = Field(default_factory=list)

    # Timeouts
    review_timeout_minutes: int = 60
    auto_proceed_on_timeout: bool = True
