"""
CoachingAsset - Universal Primitive for Coaching IP

This is the atomic unit of coaching intelligence. Every technique, template,
and reference is stored as a CoachingAsset with effectiveness tracking.

Pattern: Outcome-Driven Asset with Archetype-Specific Effectiveness
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class AssetType(str, Enum):
    """Types of coaching assets."""
    TECHNIQUE = "technique"
    TEMPLATE = "template"
    REFERENCE = "reference"
    FRAMEWORK = "framework"
    CHECKLIST = "checklist"
    PROMPT = "prompt"
    EXAMPLE = "example"


class AssetDomain(str, Enum):
    """Primary domains for coaching assets."""
    ASSESSMENT = "assessment"
    EXECUTION = "execution"
    AWARDS = "awards"
    PROGRAMS = "programs"
    ESSAYS = "essays"
    ACTIVITIES = "activities"
    EMOTIONAL = "emotional"
    STRATEGY = "strategy"
    GENERAL = "general"


class TriggerCondition(BaseModel):
    """Conditions that trigger asset selection."""
    event_types: List[str] = Field(default_factory=list)
    lifecycle_stages: List[str] = Field(default_factory=list)
    emotional_states: List[str] = Field(default_factory=list)
    score_thresholds: Dict[str, float] = Field(default_factory=dict)
    custom_conditions: Dict[str, Any] = Field(default_factory=dict)


class Applicability(BaseModel):
    """When and for whom this asset applies."""
    grade_levels: List[int] = Field(default_factory=lambda: [9, 10, 11, 12])
    archetypes: List[str] = Field(default_factory=list)
    school_tiers: List[str] = Field(default_factory=list)
    min_iv_score: float = 0.0
    max_iv_score: float = 1.0
    exclude_conditions: List[str] = Field(default_factory=list)


class Provenance(BaseModel):
    """Where this asset came from."""
    source: str = "system"
    author: Optional[str] = None
    created_from_student_id: Optional[str] = None
    derived_from_asset_id: Optional[UUID] = None
    version_notes: Optional[str] = None


class ArchetypeEffectiveness(BaseModel):
    """Effectiveness metrics for a specific archetype."""
    times_used: int = 0
    success_count: int = 0
    success_rate: float = 0.0


class Effectiveness(BaseModel):
    """Tracks how well this asset performs over time."""
    times_used: int = 0
    success_count: int = 0
    global_success_rate: float = 0.0
    by_archetype: Dict[str, ArchetypeEffectiveness] = Field(default_factory=dict)
    confidence_level: float = 0.0  # 0-1, increases with usage


class CoachingAsset(BaseModel):
    """
    Universal primitive for all coaching IP.

    Key principle: Assets learn their effectiveness over time,
    especially segmented by student archetype.
    """
    id: UUID = Field(default_factory=uuid4)

    # Identity
    name: str
    version: int = 1

    # Classification
    asset_type: AssetType
    domain: AssetDomain
    secondary_domains: List[AssetDomain] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    # Content (flexible JSONB structure)
    content: Dict[str, Any]

    # Trigger conditions
    trigger_config: TriggerCondition = Field(default_factory=TriggerCondition)

    # Applicability
    applicability: Applicability = Field(default_factory=Applicability)

    # Provenance
    provenance: Provenance = Field(default_factory=Provenance)

    # Effectiveness (learned over time)
    effectiveness: Effectiveness = Field(default_factory=Effectiveness)

    # Embedding for vector search (set externally)
    embedding: Optional[List[float]] = None

    # Metadata
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    def get_effectiveness_for_archetype(self, archetype: str) -> float:
        """Get success rate for a specific archetype."""
        if archetype in self.effectiveness.by_archetype:
            arch_data = self.effectiveness.by_archetype[archetype]
            if arch_data.times_used >= 3:  # Minimum sample size
                return arch_data.success_rate
        # Fall back to global rate
        return self.effectiveness.global_success_rate

    def matches_trigger(self, context: Dict[str, Any]) -> bool:
        """Check if this asset should be triggered by the given context."""
        trigger = self.trigger_config

        # Check event type
        if trigger.event_types:
            event_type = context.get("event_type")
            if event_type and event_type not in trigger.event_types:
                return False

        # Check lifecycle stage
        if trigger.lifecycle_stages:
            stage = context.get("lifecycle_stage")
            if stage and stage not in trigger.lifecycle_stages:
                return False

        # Check emotional state
        if trigger.emotional_states:
            emotional = context.get("emotional_state")
            if emotional and emotional not in trigger.emotional_states:
                return False

        # Check score thresholds
        for score_key, threshold in trigger.score_thresholds.items():
            score_value = context.get(score_key, 0)
            if score_value < threshold:
                return False

        return True

    def applies_to_student(self, student_context: Dict[str, Any]) -> bool:
        """Check if this asset applies to a given student."""
        app = self.applicability

        # Check grade level
        grade = student_context.get("grade_level")
        if grade and grade not in app.grade_levels:
            return False

        # Check archetype
        archetype = student_context.get("archetype")
        if app.archetypes and archetype and archetype not in app.archetypes:
            return False

        # Check school tier
        tier = student_context.get("school_tier")
        if app.school_tiers and tier and tier not in app.school_tiers:
            return False

        # Check IV score range
        iv_score = student_context.get("iv_score", 0.5)
        if not (app.min_iv_score <= iv_score <= app.max_iv_score):
            return False

        # Check exclusions
        for condition in app.exclude_conditions:
            if student_context.get(condition):
                return False

        return True

    def to_db_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion."""
        return {
            "id": str(self.id),
            "name": self.name,
            "version": self.version,
            "asset_type": self.asset_type,
            "domain": self.domain,
            "secondary_domains": self.secondary_domains,
            "tags": self.tags,
            "content": self.content,
            "trigger_config": self.trigger_config.model_dump(),
            "applicability": self.applicability.model_dump(),
            "provenance": self.provenance.model_dump(),
            "effectiveness": self.effectiveness.model_dump(),
            "embedding": self.embedding,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "CoachingAsset":
        """Create from database row."""
        return cls(
            id=UUID(row["id"]) if isinstance(row["id"], str) else row["id"],
            name=row["name"],
            version=row.get("version", 1),
            asset_type=row["asset_type"],
            domain=row["domain"],
            secondary_domains=row.get("secondary_domains", []),
            tags=row.get("tags", []),
            content=row["content"],
            trigger_config=TriggerCondition(**row.get("trigger_config", {})),
            applicability=Applicability(**row.get("applicability", {})),
            provenance=Provenance(**row.get("provenance", {})),
            effectiveness=Effectiveness(**row.get("effectiveness", {})),
            embedding=row.get("embedding"),
            is_active=row.get("is_active", True),
            created_at=row.get("created_at", datetime.utcnow()),
            updated_at=row.get("updated_at", datetime.utcnow()),
        )
