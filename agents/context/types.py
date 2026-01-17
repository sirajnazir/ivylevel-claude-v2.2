"""
Context Type Definitions - Critical 15 Patterns
v5.4 True Autonomous Agents

Defines all context types used across the pattern implementations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# =============================================================================
# C2: USER CONTEXT TYPES
# =============================================================================

class CommunicationStyle(str, Enum):
    """Student communication preference."""
    DETAILED = "detailed"     # Wants thorough explanations
    CONCISE = "concise"       # Prefers brief, actionable info
    BALANCED = "balanced"     # Default middle ground


class MotivationType(str, Enum):
    """What motivates this student."""
    ACHIEVEMENT = "achievement"   # Driven by accomplishments
    MASTERY = "mastery"          # Driven by learning/growth
    SOCIAL = "social"            # Driven by connection/impact


class StudentContext(BaseModel):
    """
    Complete student context - loaded before every interaction.

    Pattern C2: User Context (3P: Supabase + Custom Selection)
    """

    # Core Identity
    profile_id: str
    name: str = ""
    grade: int = 11

    # Identity Synthesis (from EC Agent)
    archetype: Optional[str] = None
    archetype_confidence: Optional[float] = None
    spike: Optional[str] = None
    pillars: Optional[List[str]] = None
    narrative_dna: Optional[str] = None

    # Preferences (USP - coaching personalization)
    communication_style: CommunicationStyle = CommunicationStyle.BALANCED
    motivation_type: MotivationType = MotivationType.ACHIEVEMENT
    stress_indicators: List[str] = Field(default_factory=list)

    # Academic Context
    gpa: Optional[float] = None
    target_schools: List[str] = Field(default_factory=list)
    intended_major: Optional[str] = None

    # Activity Context
    activities: List[Dict[str, Any]] = Field(default_factory=list)
    activity_count: int = 0

    # Constraints (budget, time, location)
    constraints: Dict[str, Any] = Field(default_factory=dict)

    # Current State (USP - coaching awareness)
    energy_level: float = Field(default=0.7, ge=0.0, le=1.0)  # Current capacity
    recent_sentiment: str = "neutral"  # positive/neutral/negative/stressed

    class Config:
        extra = "allow"  # Allow additional fields


class ContextSelection(BaseModel):
    """
    What context to include based on current task.

    USP: Smart context selection - knowing what's relevant.
    """
    include_activities: bool = True
    include_academics: bool = True
    include_goals: bool = True
    include_history: bool = False
    max_history_items: int = 5
    include_constraints: bool = True


# =============================================================================
# C6: TEMPORAL CONTEXT TYPES
# =============================================================================

class DeadlinePriority(str, Enum):
    """Deadline urgency level."""
    CRITICAL = "critical"   # 3 days or less
    HIGH = "high"          # Within 1 week
    MEDIUM = "medium"      # Within 2 weeks
    LOW = "low"            # More than 2 weeks


class DeadlineStatus(str, Enum):
    """Deadline status."""
    UPCOMING = "upcoming"
    IMMINENT = "imminent"   # Within 3 days
    OVERDUE = "overdue"
    COMPLETED = "completed"


class DeadlineCategory(str, Enum):
    """Type of deadline."""
    APPLICATION = "application"
    AWARD = "award"
    PROGRAM = "program"
    ESSAY = "essay"
    RECOMMENDATION = "recommendation"
    TEST = "test"
    OTHER = "other"


class Deadline(BaseModel):
    """A tracked deadline."""
    id: str
    name: str
    due_date: datetime
    category: DeadlineCategory
    priority: DeadlinePriority = DeadlinePriority.MEDIUM
    status: DeadlineStatus = DeadlineStatus.UPCOMING
    days_until: int = 0
    related_task_id: Optional[str] = None
    notes: Optional[str] = None


class AdmissionsPhase(str, Enum):
    """Current phase in admissions calendar."""
    SUMMER_PROGRAMS = "summer_programs"   # Jan-Mar
    ACTIVITIES = "activities"              # Apr-May
    ESSAYS = "essays"                      # Jun-Sep
    APPLICATIONS = "applications"          # Oct-Dec
    DECISIONS = "decisions"                # Jan-Apr


class TemporalContext(BaseModel):
    """
    Time-sensitive context for a student.

    Pattern C6: Temporal Context
    """
    profile_id: str
    current_phase: AdmissionsPhase = AdmissionsPhase.ACTIVITIES
    current_date: datetime = Field(default_factory=datetime.utcnow)

    # Deadlines
    deadlines: List[Deadline] = Field(default_factory=list)
    imminent_deadlines: List[Deadline] = Field(default_factory=list)  # Within 7 days
    overdue_deadlines: List[Deadline] = Field(default_factory=list)

    # Counts
    urgent_count: int = 0
    total_deadlines: int = 0

    # Phase info
    days_until_ed: Optional[int] = None  # Days until Early Decision deadline

    @property
    def has_urgent_items(self) -> bool:
        return self.urgent_count > 0

    @property
    def has_overdue(self) -> bool:
        return len(self.overdue_deadlines) > 0


# =============================================================================
# C4: TASK CONTEXT TYPES
# =============================================================================

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, Enum):
    """Type of task being worked on."""
    ASSESSMENT = "assessment"
    GAMEPLAN = "gameplan"
    EXECUTION = "execution"
    CRISIS = "crisis"
    CHAT = "chat"
    GENERAL = "general"


class TaskContext(BaseModel):
    """
    Current task being worked on.

    Pattern C4: Task Context
    """
    task_id: Optional[str] = None
    task_type: TaskType = TaskType.GENERAL
    objective: str = ""
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None

    # Progress tracking
    steps_completed: int = 0
    steps_total: int = 0
    progress_percentage: float = 0.0

    # Blocking info
    blocker: Optional[str] = None
    blocker_since: Optional[datetime] = None

    # Agent coordination
    current_agent: Optional[str] = None
    agents_completed: List[str] = Field(default_factory=list)

    # Sub-tasks
    sub_tasks: List[Dict[str, Any]] = Field(default_factory=list)

    @property
    def is_blocked(self) -> bool:
        return self.status == TaskStatus.BLOCKED

    @property
    def is_complete(self) -> bool:
        return self.status == TaskStatus.COMPLETED


# =============================================================================
# B1: WORKING MEMORY TYPES
# =============================================================================

class ConversationRole(str, Enum):
    """Role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationTurn(BaseModel):
    """A single conversation turn."""
    role: ConversationRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DetectedSignal(BaseModel):
    """A signal detected from student interaction."""
    signal_type: str  # stress, confusion, excitement, frustration
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str = ""
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class WorkingMemory(BaseModel):
    """
    Working memory for current session.
    Clears when session ends.

    Pattern B1: Working Memory
    """
    session_id: str
    profile_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)

    # Conversation buffer (last N turns)
    conversation_buffer: List[ConversationTurn] = Field(default_factory=list)
    max_buffer_size: int = 20

    # Current state
    current_task: Optional[str] = None
    current_agent: Optional[str] = None

    # Detected signals (USP: Coaching awareness)
    detected_sentiment: str = "neutral"
    engagement_level: float = Field(default=0.5, ge=0.0, le=1.0)
    recent_signals: List[DetectedSignal] = Field(default_factory=list)

    # Pending actions
    pending_actions: List[Dict[str, Any]] = Field(default_factory=list)

    # Scratchpad for agent reasoning
    scratchpad: Dict[str, Any] = Field(default_factory=dict)

    # Facts learned this session
    session_facts: List[str] = Field(default_factory=list)
