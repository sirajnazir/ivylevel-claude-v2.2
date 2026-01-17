"""
G2: Approval Gates - Type Definitions

Types for the approval gates pattern.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ApprovalCategory(str, Enum):
    """Categories requiring different approval flows."""
    STRATEGIC = "strategic"       # Major plan changes
    CONTENT = "content"           # Essays, applications
    FINANCIAL = "financial"       # Program recommendations with costs
    CRISIS = "crisis"             # Mental health, emergency
    DEADLINE = "deadline"         # Deadline changes


class ApprovalUrgency(str, Enum):
    """How quickly approval is needed."""
    IMMEDIATE = "immediate"       # Block until approved (< 1 hour)
    SAME_DAY = "same_day"         # Need within 24 hours
    STANDARD = "standard"         # 3-5 business days OK
    ADVISORY = "advisory"         # FYI, can proceed if no response


class ApprovalStatus(str, Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


class ApprovalRequest(BaseModel):
    """A request for human approval."""
    request_id: str
    profile_id: str
    agent_name: str

    # What needs approval
    category: ApprovalCategory
    action_type: str
    action_description: str
    action_payload: Dict[str, Any] = Field(default_factory=dict)

    # Context
    urgency: ApprovalUrgency = ApprovalUrgency.STANDARD
    reason: str
    agent_confidence: float = Field(ge=0.0, le=1.0)
    agent_reasoning: str = ""

    # Alternatives considered
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    # Status
    status: ApprovalStatus = ApprovalStatus.PENDING

    class Config:
        extra = "allow"


class ApprovalDecision(BaseModel):
    """Human's decision on an approval request."""
    request_id: str
    status: ApprovalStatus

    # Who decided
    reviewer_id: str
    reviewer_role: str  # "coach", "admin", "parent"

    # Decision details
    decision_reason: Optional[str] = None
    modifications: Optional[Dict[str, Any]] = None  # Changes to original action

    # Timing
    decided_at: datetime = Field(default_factory=datetime.utcnow)


class ApprovalRule(BaseModel):
    """Rule defining what requires approval."""
    rule_id: str
    action_pattern: str  # Regex or action type
    category: ApprovalCategory
    urgency: ApprovalUrgency

    # Conditions
    min_confidence_bypass: float = 1.0  # Confidence above this = auto-approve
    requires_approval_if: Optional[str] = None  # Condition expression

    # Metadata
    description: str
    enabled: bool = True
