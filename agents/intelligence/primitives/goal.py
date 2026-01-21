"""
OutcomeDrivenGoal - Goal Primitive Focused on WINS, Not Just Progress

Key distinction from existing GoalMonitor:
- GoalMonitor tracks PROGRESS (% complete, milestones)
- OutcomeDrivenGoal tracks OUTCOMES (wins, acceptances, achievements)

Pattern: The goal knows what success looks like AND what it's NOT about.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class GoalType(str, Enum):
    """Types of outcome-driven goals."""
    WIN = "win"          # Win an award, competition
    COMPLETE = "complete"  # Complete a project, application
    ACHIEVE = "achieve"   # Achieve a score, milestone
    PREVENT = "prevent"   # Prevent a negative outcome (dropout, burnout)
    IMPROVE = "improve"   # Improve a metric over time


class GoalStatus(str, Enum):
    """Status of an outcome-driven goal."""
    ACTIVE = "active"
    ACHIEVED = "achieved"
    FAILED = "failed"
    PAUSED = "paused"
    SUPERSEDED = "superseded"  # Replaced by a better goal


class SecondaryMetric(BaseModel):
    """A secondary metric that contributes to goal achievement."""
    name: str
    target_value: float
    current_value: float = 0.0
    weight: float = 1.0  # Relative importance


class OutcomeDrivenGoal(BaseModel):
    """
    A goal focused on OUTCOMES (wins) rather than just PROGRESS.

    Key innovation: The `not_goal` field explicitly states what this goal
    is NOT about, preventing scope creep and maintaining focus.

    Example:
        primary_outcome: "Win Regeneron STS"
        not_goal: ["Get participation certificate", "Just complete the application"]

    This forces clarity: we're not just trying to complete something,
    we're trying to WIN.
    """
    id: UUID = Field(default_factory=uuid4)
    profile_id: UUID
    agent_name: str  # Which agent owns this goal

    # Goal definition
    primary_outcome: str  # The WIN we're pursuing
    goal_type: GoalType
    not_goal: List[str] = Field(default_factory=list)  # What this is NOT about

    # Primary metric
    primary_metric: Optional[str] = None
    target_value: float = 1.0  # Default: binary (0 = not achieved, 1 = achieved)
    current_value: float = 0.0

    # Secondary metrics (contributing factors)
    secondary_metrics: Dict[str, SecondaryMetric] = Field(default_factory=dict)

    # Status
    status: GoalStatus = GoalStatus.ACTIVE

    # Timing
    target_date: Optional[datetime] = None
    achieved_at: Optional[datetime] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    @property
    def is_active(self) -> bool:
        """Check if goal is still being pursued."""
        return self.status == GoalStatus.ACTIVE

    @property
    def is_achieved(self) -> bool:
        """Check if goal has been achieved."""
        return self.status == GoalStatus.ACHIEVED

    @property
    def progress_percentage(self) -> float:
        """Calculate overall progress toward goal."""
        if self.target_value == 0:
            return 100.0 if self.current_value >= 0 else 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)

    @property
    def days_until_deadline(self) -> Optional[int]:
        """Days remaining until target date."""
        if not self.target_date:
            return None
        delta = self.target_date - datetime.utcnow()
        return delta.days

    @property
    def is_at_risk(self) -> bool:
        """Check if goal is at risk based on progress vs timeline."""
        if not self.target_date:
            return False

        days_left = self.days_until_deadline
        if days_left is None or days_left < 0:
            return True  # Past deadline

        # At risk if behind expected pace
        total_days = (self.target_date - self.created_at).days
        if total_days <= 0:
            return False

        expected_progress = ((total_days - days_left) / total_days) * 100
        return self.progress_percentage < (expected_progress * 0.7)  # 30% buffer

    def update_progress(self, new_value: float) -> None:
        """Update the current value toward the goal."""
        self.current_value = new_value
        self.updated_at = datetime.utcnow()

        # Check for achievement
        if self.current_value >= self.target_value:
            self.mark_achieved()

    def update_secondary_metric(self, metric_name: str, new_value: float) -> None:
        """Update a secondary metric."""
        if metric_name in self.secondary_metrics:
            self.secondary_metrics[metric_name].current_value = new_value
            self.updated_at = datetime.utcnow()

    def mark_achieved(self) -> None:
        """Mark the goal as achieved."""
        self.status = GoalStatus.ACHIEVED
        self.achieved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_failed(self) -> None:
        """Mark the goal as failed."""
        self.status = GoalStatus.FAILED
        self.updated_at = datetime.utcnow()

    def pause(self) -> None:
        """Pause the goal."""
        self.status = GoalStatus.PAUSED
        self.updated_at = datetime.utcnow()

    def resume(self) -> None:
        """Resume a paused goal."""
        if self.status == GoalStatus.PAUSED:
            self.status = GoalStatus.ACTIVE
            self.updated_at = datetime.utcnow()

    def get_weighted_progress(self) -> float:
        """Calculate weighted progress including secondary metrics."""
        if not self.secondary_metrics:
            return self.progress_percentage

        # Primary metric gets 60% weight
        total_weight = 0.6
        weighted_sum = (self.progress_percentage / 100) * 0.6

        # Secondary metrics split remaining 40%
        secondary_weight = 0.4 / len(self.secondary_metrics) if self.secondary_metrics else 0

        for metric in self.secondary_metrics.values():
            if metric.target_value > 0:
                metric_progress = min(1.0, metric.current_value / metric.target_value)
                weighted_sum += metric_progress * secondary_weight * metric.weight
                total_weight += secondary_weight * metric.weight

        return (weighted_sum / total_weight * 100) if total_weight > 0 else 0

    def to_db_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion."""
        return {
            "id": str(self.id),
            "profile_id": str(self.profile_id),
            "agent_name": self.agent_name,
            "primary_outcome": self.primary_outcome,
            "goal_type": self.goal_type,
            "not_goal": self.not_goal,
            "primary_metric": self.primary_metric,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "secondary_metrics": {
                k: v.model_dump() for k, v in self.secondary_metrics.items()
            },
            "status": self.status,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "achieved_at": self.achieved_at.isoformat() if self.achieved_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "OutcomeDrivenGoal":
        """Create from database row."""
        secondary_metrics = {}
        if row.get("secondary_metrics"):
            for k, v in row["secondary_metrics"].items():
                secondary_metrics[k] = SecondaryMetric(**v)

        return cls(
            id=UUID(row["id"]) if isinstance(row["id"], str) else row["id"],
            profile_id=UUID(row["profile_id"]) if isinstance(row["profile_id"], str) else row["profile_id"],
            agent_name=row["agent_name"],
            primary_outcome=row["primary_outcome"],
            goal_type=row["goal_type"],
            not_goal=row.get("not_goal", []),
            primary_metric=row.get("primary_metric"),
            target_value=row.get("target_value", 1.0),
            current_value=row.get("current_value", 0.0),
            secondary_metrics=secondary_metrics,
            status=row.get("status", GoalStatus.ACTIVE),
            target_date=row.get("target_date"),
            achieved_at=row.get("achieved_at"),
            created_at=row.get("created_at", datetime.utcnow()),
            updated_at=row.get("updated_at", datetime.utcnow()),
        )


# Pre-built goal templates for common outcomes
GOAL_TEMPLATES = {
    "regeneron_sts": OutcomeDrivenGoal(
        id=uuid4(),
        profile_id=uuid4(),  # Placeholder, set on creation
        agent_name="awards",
        primary_outcome="Win Regeneron Science Talent Search",
        goal_type=GoalType.WIN,
        not_goal=[
            "Just submit an application",
            "Get participation recognition",
            "Complete the paperwork",
        ],
        primary_metric="award_status",
        target_value=1.0,  # Binary: won or not
        secondary_metrics={
            "research_quality": SecondaryMetric(
                name="Research Quality Score",
                target_value=0.95,
                weight=1.5,  # Higher weight
            ),
            "essay_quality": SecondaryMetric(
                name="Essay Quality Score",
                target_value=0.90,
                weight=1.0,
            ),
            "mentor_feedback": SecondaryMetric(
                name="Mentor Feedback Score",
                target_value=0.85,
                weight=0.8,
            ),
        },
    ),
    "ivy_admission": OutcomeDrivenGoal(
        id=uuid4(),
        profile_id=uuid4(),
        agent_name="gameplan",
        primary_outcome="Get accepted to target Ivy League school",
        goal_type=GoalType.ACHIEVE,
        not_goal=[
            "Just apply to many schools",
            "Complete applications on time",
            "Get deferred to regular decision",
        ],
        primary_metric="admission_status",
        target_value=1.0,
        secondary_metrics={
            "iv_score": SecondaryMetric(
                name="IV+ Ready Score",
                target_value=0.90,
                weight=1.2,
            ),
            "spike_strength": SecondaryMetric(
                name="Spike Strength",
                target_value=0.85,
                weight=1.5,
            ),
            "essay_quality": SecondaryMetric(
                name="Essay Quality",
                target_value=0.90,
                weight=1.0,
            ),
        },
    ),
}
