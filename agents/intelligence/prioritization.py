"""
Pattern A12: Prioritization Logic
v5.4 True Autonomous Agents

USP: This is OUR competitive advantage.
BUILD, not buy - custom prioritization intelligence.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class PriorityLevel(str, Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"     # Must do ASAP
    HIGH = "high"            # Important, do soon
    MEDIUM = "medium"        # Should do
    LOW = "low"              # Nice to have
    DEFERRED = "deferred"    # Consider later


class RecommendationType(str, Enum):
    """Types of recommendations we prioritize."""
    AWARD = "award"
    PROGRAM = "program"
    ACTIVITY = "activity"
    ESSAY = "essay"
    DEADLINE = "deadline"
    TASK = "task"


class PrioritizedItem(BaseModel):
    """A prioritized recommendation."""
    id: str
    type: RecommendationType
    name: str
    priority: PriorityLevel
    score: float = Field(ge=0.0, le=100.0)
    reasoning: str = ""
    deadline: Optional[datetime] = None
    effort_hours: Optional[float] = None
    impact_score: Optional[float] = None
    alignment_score: Optional[float] = None


# Weighting factors for prioritization (USP)
PRIORITY_WEIGHTS = {
    "deadline_urgency": 0.25,      # How soon is the deadline
    "profile_alignment": 0.25,     # How well does it fit the student
    "impact_potential": 0.20,      # How much will it help admission
    "effort_required": 0.15,       # Feasibility given constraints
    "selectivity_match": 0.15,     # Match to target school selectivity
}

# Time urgency multipliers
URGENCY_MULTIPLIERS = {
    7: 2.0,    # Within 1 week: 2x multiplier
    14: 1.5,   # Within 2 weeks: 1.5x
    30: 1.2,   # Within 1 month: 1.2x
    60: 1.0,   # Within 2 months: normal
    90: 0.8,   # Within 3 months: slightly reduced
}


class Prioritizer:
    """
    Prioritizes recommendations for students.

    USP: This is our secret sauce for personalized guidance.

    Key factors:
    1. Deadline urgency - what's coming up soonest
    2. Profile alignment - what fits the student's identity
    3. Impact potential - what will help most
    4. Effort required - what's achievable
    5. Selectivity match - appropriate for target schools
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize prioritizer with optional custom weights.

        Args:
            weights: Custom weighting factors (defaults to PRIORITY_WEIGHTS)
        """
        self.weights = weights or PRIORITY_WEIGHTS
        self._validate_weights()

    def _validate_weights(self) -> None:
        """Ensure weights sum to 1.0."""
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total}, normalizing...")
            for key in self.weights:
                self.weights[key] /= total

    def prioritize(
        self,
        items: List[Dict[str, Any]],
        student_context: Dict[str, Any],
        temporal_context: Optional[Dict[str, Any]] = None,
        max_items: int = 10,
    ) -> List[PrioritizedItem]:
        """
        Prioritize a list of recommendations.

        Args:
            items: List of raw recommendations (awards, programs, etc.)
            student_context: Student's profile, identity, constraints
            temporal_context: Deadlines, current phase, etc.
            max_items: Maximum items to return

        Returns:
            List of PrioritizedItems sorted by priority
        """
        scored_items = []

        for item in items:
            score, reasoning = self._calculate_priority_score(
                item,
                student_context,
                temporal_context or {},
            )

            priority_level = self._score_to_priority(score)

            scored_items.append(PrioritizedItem(
                id=item.get("id", ""),
                type=self._detect_item_type(item),
                name=item.get("name", item.get("title", "Unknown")),
                priority=priority_level,
                score=score,
                reasoning=reasoning,
                deadline=self._parse_deadline(item.get("deadline")),
                effort_hours=item.get("effort_hours"),
                impact_score=item.get("impact_score"),
                alignment_score=item.get("alignment_score"),
            ))

        # Sort by score descending
        scored_items.sort(key=lambda x: x.score, reverse=True)

        return scored_items[:max_items]

    def _calculate_priority_score(
        self,
        item: Dict[str, Any],
        student_context: Dict[str, Any],
        temporal_context: Dict[str, Any],
    ) -> tuple[float, str]:
        """
        Calculate priority score for a single item.

        Returns:
            Tuple of (score, reasoning_string)
        """
        reasoning_parts = []

        # 1. Deadline urgency
        urgency_score = self._calculate_urgency(item, temporal_context)
        reasoning_parts.append(f"Urgency: {urgency_score:.0f}")

        # 2. Profile alignment (USP: uses identity synthesis)
        alignment_score = self._calculate_alignment(item, student_context)
        reasoning_parts.append(f"Alignment: {alignment_score:.0f}")

        # 3. Impact potential
        impact_score = self._calculate_impact(item, student_context)
        reasoning_parts.append(f"Impact: {impact_score:.0f}")

        # 4. Effort/feasibility
        effort_score = self._calculate_effort_feasibility(item, student_context)
        reasoning_parts.append(f"Feasibility: {effort_score:.0f}")

        # 5. Selectivity match
        selectivity_score = self._calculate_selectivity_match(item, student_context)
        reasoning_parts.append(f"Selectivity: {selectivity_score:.0f}")

        # Weighted combination
        final_score = (
            urgency_score * self.weights["deadline_urgency"] +
            alignment_score * self.weights["profile_alignment"] +
            impact_score * self.weights["impact_potential"] +
            effort_score * self.weights["effort_required"] +
            selectivity_score * self.weights["selectivity_match"]
        )

        reasoning = " | ".join(reasoning_parts) + f" = {final_score:.0f}"

        return final_score, reasoning

    def _calculate_urgency(
        self,
        item: Dict[str, Any],
        temporal_context: Dict[str, Any],
    ) -> float:
        """
        Calculate deadline urgency score (0-100).

        USP: Considers admissions calendar phase.
        """
        deadline = item.get("deadline")
        if not deadline:
            # No deadline - moderate urgency based on phase
            current_phase = temporal_context.get("current_phase", "activities")
            phase_urgency = {
                "summer_programs": 70,
                "activities": 50,
                "essays": 60,
                "applications": 80,
                "decisions": 40,
            }
            return phase_urgency.get(current_phase, 50)

        # Parse deadline
        if isinstance(deadline, str):
            try:
                deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            except ValueError:
                return 50

        # Days until deadline
        days_until = (deadline - datetime.utcnow()).days

        if days_until < 0:
            return 100  # Overdue!

        # Apply urgency multipliers
        for threshold, multiplier in sorted(URGENCY_MULTIPLIERS.items()):
            if days_until <= threshold:
                base_score = 50  # Start from 50
                urgency_boost = (1 - (days_until / threshold)) * 50 * multiplier
                return min(100, base_score + urgency_boost)

        return 30  # Far future deadline

    def _calculate_alignment(
        self,
        item: Dict[str, Any],
        student_context: Dict[str, Any],
    ) -> float:
        """
        Calculate profile alignment score (0-100).

        USP: Uses spike, archetype, pillars for matching.
        """
        alignment = 50  # Base score

        # Check spike alignment
        spike = student_context.get("spike", "")
        item_tags = item.get("tags", []) + item.get("categories", [])
        item_description = item.get("description", "").lower()

        if spike:
            spike_lower = spike.lower()
            # Check if item relates to spike
            spike_words = spike_lower.split()
            matches = sum(
                1 for word in spike_words
                if word in item_description or word in " ".join(item_tags).lower()
            )
            if matches > 0:
                alignment += min(30, matches * 10)

        # Check archetype alignment
        archetype = student_context.get("archetype", "")
        if archetype:
            archetype_alignments = {
                "academic_all_star": ["research", "academic", "honors", "scholarship"],
                "passionate_specialist": ["intensive", "specialized", "advanced"],
                "balanced_achiever": ["leadership", "well-rounded", "diverse"],
                "community_catalyst": ["service", "community", "social", "volunteer"],
                "creative_innovator": ["creative", "arts", "innovation", "design"],
            }
            relevant_keywords = archetype_alignments.get(archetype.lower(), [])
            for keyword in relevant_keywords:
                if keyword in item_description or keyword in " ".join(item_tags).lower():
                    alignment += 5

        # Check pillar alignment
        pillars = student_context.get("pillars", [])
        for pillar in pillars:
            if pillar.lower() in item_description:
                alignment += 10

        return min(100, alignment)

    def _calculate_impact(
        self,
        item: Dict[str, Any],
        student_context: Dict[str, Any],
    ) -> float:
        """
        Calculate potential impact on admission chances (0-100).

        USP: Considers what would strengthen the application most.
        """
        # Start with item's stated impact if available
        impact = item.get("impact_score", 50)

        # Award selectivity boosts impact
        selectivity = item.get("selectivity", "")
        selectivity_boosts = {
            "highly_selective": 30,
            "selective": 20,
            "competitive": 10,
        }
        impact += selectivity_boosts.get(selectivity, 0)

        # National/international scope boosts impact
        scope = item.get("scope", "")
        if scope in ["national", "international"]:
            impact += 15
        elif scope in ["regional", "state"]:
            impact += 5

        # Check if filling a gap in profile
        activities = student_context.get("activities", [])
        activity_categories = [a.get("category", "") for a in activities]

        item_category = item.get("category", "")
        if item_category and item_category not in activity_categories:
            impact += 10  # Fills a gap

        return min(100, impact)

    def _calculate_effort_feasibility(
        self,
        item: Dict[str, Any],
        student_context: Dict[str, Any],
    ) -> float:
        """
        Calculate feasibility given student's constraints (0-100).

        Higher score = more feasible (less effort required).
        """
        feasibility = 70  # Base - most things are doable

        # Check time constraints
        constraints = student_context.get("constraints", {})
        available_hours = constraints.get("weekly_hours_available", 10)

        effort_hours = item.get("effort_hours", item.get("hours_per_week", 5))
        if effort_hours > available_hours * 2:
            feasibility -= 30  # Too time-intensive
        elif effort_hours > available_hours:
            feasibility -= 15

        # Check financial constraints
        cost = item.get("cost", 0)
        budget = constraints.get("budget", 1000)

        if cost > budget * 2:
            feasibility -= 40  # Too expensive
        elif cost > budget:
            feasibility -= 20

        # Check grade eligibility
        student_grade = student_context.get("grade", 11)
        eligible_grades = item.get("eligible_grades", [9, 10, 11, 12])
        if student_grade not in eligible_grades:
            feasibility -= 50  # Not eligible

        # Check GPA requirements
        min_gpa = item.get("min_gpa", 0)
        student_gpa = student_context.get("gpa")
        if student_gpa and min_gpa and student_gpa < min_gpa:
            feasibility -= 30

        return max(0, feasibility)

    def _calculate_selectivity_match(
        self,
        item: Dict[str, Any],
        student_context: Dict[str, Any],
    ) -> float:
        """
        Calculate match to target school selectivity (0-100).

        USP: Ensures recommendations match aspiration level.
        """
        target_schools = student_context.get("target_schools", [])
        if not target_schools:
            return 50  # No targets, neutral score

        # Estimate student's target selectivity
        highly_selective_schools = [
            "harvard", "yale", "princeton", "stanford", "mit",
            "columbia", "penn", "duke", "chicago", "northwestern"
        ]

        target_selectivity = "moderate"
        for school in target_schools:
            if school.lower() in highly_selective_schools:
                target_selectivity = "highly_selective"
                break

        # Match item selectivity to target
        item_selectivity = item.get("selectivity", "competitive")

        selectivity_scores = {
            ("highly_selective", "highly_selective"): 90,
            ("highly_selective", "selective"): 75,
            ("highly_selective", "competitive"): 60,
            ("selective", "highly_selective"): 70,
            ("selective", "selective"): 85,
            ("selective", "competitive"): 70,
            ("moderate", "highly_selective"): 60,
            ("moderate", "selective"): 75,
            ("moderate", "competitive"): 80,
        }

        return selectivity_scores.get(
            (target_selectivity, item_selectivity),
            50
        )

    def _score_to_priority(self, score: float) -> PriorityLevel:
        """Convert numeric score to priority level."""
        if score >= 85:
            return PriorityLevel.CRITICAL
        elif score >= 70:
            return PriorityLevel.HIGH
        elif score >= 50:
            return PriorityLevel.MEDIUM
        elif score >= 30:
            return PriorityLevel.LOW
        else:
            return PriorityLevel.DEFERRED

    def _detect_item_type(self, item: Dict[str, Any]) -> RecommendationType:
        """Detect the type of recommendation."""
        if "award" in item.get("type", "").lower():
            return RecommendationType.AWARD
        if "program" in item.get("type", "").lower():
            return RecommendationType.PROGRAM
        if "activity" in item.get("type", "").lower():
            return RecommendationType.ACTIVITY
        if "essay" in item.get("type", "").lower():
            return RecommendationType.ESSAY
        if "deadline" in item.get("type", "").lower():
            return RecommendationType.DEADLINE

        # Infer from structure
        if "deadline" in item and "name" in item:
            return RecommendationType.DEADLINE
        if "selectivity" in item or "award" in item.get("name", "").lower():
            return RecommendationType.AWARD
        if "program" in item.get("name", "").lower() or "summer" in item.get("name", "").lower():
            return RecommendationType.PROGRAM

        return RecommendationType.TASK

    def _parse_deadline(self, deadline: Any) -> Optional[datetime]:
        """Parse deadline from various formats."""
        if not deadline:
            return None
        if isinstance(deadline, datetime):
            return deadline
        if isinstance(deadline, str):
            try:
                return datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None


# Convenience function
def prioritize_recommendations(
    items: List[Dict[str, Any]],
    student_context: Dict[str, Any],
    temporal_context: Optional[Dict[str, Any]] = None,
    max_items: int = 10,
) -> List[PrioritizedItem]:
    """
    Quick helper to prioritize recommendations.

    Usage:
        prioritized = prioritize_recommendations(
            awards + programs,
            student_context,
            temporal_context,
        )
    """
    prioritizer = Prioritizer()
    return prioritizer.prioritize(
        items,
        student_context,
        temporal_context,
        max_items,
    )
