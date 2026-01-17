"""
Pattern E1: Output Validation
v5.4 True Autonomous Agents

3P: Pydantic for validation schemas
USP: Quality assurance for coaching outputs
"""

from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from pydantic import BaseModel, Field, validator
import logging
import re

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    """Result of output validation."""
    valid: bool
    score: float = Field(ge=0.0, le=100.0)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QualityDimension(BaseModel):
    """A quality dimension to check."""
    name: str
    weight: float = 1.0
    min_score: float = 0.0
    max_score: float = 100.0


# Quality dimensions for different output types (USP)
QUALITY_DIMENSIONS = {
    "spike": [
        QualityDimension(name="specificity", weight=0.3, min_score=70),
        QualityDimension(name="uniqueness", weight=0.3, min_score=60),
        QualityDimension(name="evidence_based", weight=0.2, min_score=60),
        QualityDimension(name="actionability", weight=0.2, min_score=50),
    ],
    "narrative": [
        QualityDimension(name="coherence", weight=0.25, min_score=60),
        QualityDimension(name="authenticity", weight=0.25, min_score=60),
        QualityDimension(name="differentiation", weight=0.25, min_score=50),
        QualityDimension(name="connection", weight=0.25, min_score=50),
    ],
    "recommendation": [
        QualityDimension(name="relevance", weight=0.3, min_score=70),
        QualityDimension(name="feasibility", weight=0.3, min_score=60),
        QualityDimension(name="specificity", weight=0.2, min_score=50),
        QualityDimension(name="timing", weight=0.2, min_score=50),
    ],
    "gameplan": [
        QualityDimension(name="comprehensiveness", weight=0.2, min_score=60),
        QualityDimension(name="prioritization", weight=0.25, min_score=60),
        QualityDimension(name="personalization", weight=0.25, min_score=60),
        QualityDimension(name="actionability", weight=0.3, min_score=70),
    ],
}


class OutputValidator:
    """
    Validates agent outputs for quality.

    Pattern E1: Output Validation (3P: Pydantic)

    Why this matters:
    1. Ensures consistent quality
    2. Catches errors before user sees them
    3. Enables iterative improvement
    4. Builds trust with users
    """

    def __init__(
        self,
        dimensions: Optional[Dict[str, List[QualityDimension]]] = None,
    ):
        """
        Initialize validator.

        Args:
            dimensions: Custom quality dimensions by output type
        """
        self.dimensions = dimensions or QUALITY_DIMENSIONS

    def validate(
        self,
        output: Dict[str, Any],
        output_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Validate an agent output.

        Args:
            output: The output to validate
            output_type: Type of output (spike, narrative, etc.)
            context: Additional context for validation

        Returns:
            ValidationResult
        """
        context = context or {}
        errors = []
        warnings = []
        suggestions = []
        scores = {}

        # Get dimensions for this output type
        dimensions = self.dimensions.get(output_type, [])

        for dimension in dimensions:
            score = self._score_dimension(output, dimension, context)
            scores[dimension.name] = score

            if score < dimension.min_score:
                errors.append(
                    f"{dimension.name} score ({score:.0f}) below minimum ({dimension.min_score:.0f})"
                )
            elif score < dimension.min_score + 10:
                warnings.append(
                    f"{dimension.name} score ({score:.0f}) is marginal"
                )

        # Calculate weighted overall score
        total_weight = sum(d.weight for d in dimensions)
        if total_weight > 0 and scores:
            overall_score = sum(
                scores[d.name] * d.weight
                for d in dimensions
                if d.name in scores
            ) / total_weight
        else:
            overall_score = 50  # Default

        # Type-specific validation
        type_errors = self._validate_type_specific(output, output_type, context)
        errors.extend(type_errors)

        # Generate suggestions
        suggestions = self._generate_suggestions(scores, dimensions, output_type)

        return ValidationResult(
            valid=len(errors) == 0,
            score=overall_score,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            metadata={
                "dimension_scores": scores,
                "output_type": output_type,
            },
        )

    def _score_dimension(
        self,
        output: Dict[str, Any],
        dimension: QualityDimension,
        context: Dict[str, Any],
    ) -> float:
        """Score a single quality dimension."""
        # These are heuristic scoring methods
        # In production, could use LLM or more sophisticated analysis

        if dimension.name == "specificity":
            return self._score_specificity(output)
        elif dimension.name == "uniqueness":
            return self._score_uniqueness(output, context)
        elif dimension.name == "evidence_based":
            return self._score_evidence(output, context)
        elif dimension.name == "actionability":
            return self._score_actionability(output)
        elif dimension.name == "coherence":
            return self._score_coherence(output)
        elif dimension.name == "authenticity":
            return self._score_authenticity(output, context)
        elif dimension.name == "differentiation":
            return self._score_differentiation(output, context)
        elif dimension.name == "connection":
            return self._score_connection(output)
        elif dimension.name == "relevance":
            return self._score_relevance(output, context)
        elif dimension.name == "feasibility":
            return self._score_feasibility(output, context)
        elif dimension.name == "timing":
            return self._score_timing(output, context)
        elif dimension.name == "comprehensiveness":
            return self._score_comprehensiveness(output)
        elif dimension.name == "prioritization":
            return self._score_prioritization(output)
        elif dimension.name == "personalization":
            return self._score_personalization(output, context)
        else:
            return 70  # Default score

    def _score_specificity(self, output: Dict[str, Any]) -> float:
        """Score how specific the output is."""
        text = str(output)

        # Generic phrases reduce score
        generic_phrases = [
            "various", "different", "many", "some", "things",
            "general", "overall", "etc", "and more",
        ]
        generic_count = sum(1 for phrase in generic_phrases if phrase in text.lower())

        # Specific details increase score
        has_numbers = bool(re.search(r'\d+', text))
        has_names = bool(re.search(r'[A-Z][a-z]+', text))
        word_count = len(text.split())

        base_score = 70
        score = base_score - (generic_count * 5) + (10 if has_numbers else 0)
        score += (10 if has_names else 0)
        score += min(10, word_count / 50)  # Longer = potentially more specific

        return max(0, min(100, score))

    def _score_uniqueness(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """Score how unique/differentiated the output is."""
        text = str(output).lower()

        # Cliche phrases reduce uniqueness
        cliches = [
            "passionate about", "love to help", "make a difference",
            "since i was young", "always wanted", "dream school",
            "well-rounded", "stand out", "be myself",
        ]
        cliche_count = sum(1 for cliche in cliches if cliche in text)

        base_score = 80
        return max(0, min(100, base_score - (cliche_count * 15)))

    def _score_evidence(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """Score how well the output is supported by evidence."""
        text = str(output)

        # Evidence indicators
        evidence_words = [
            "because", "since", "shows", "demonstrates",
            "achieved", "won", "founded", "created", "led",
        ]
        evidence_count = sum(1 for word in evidence_words if word in text.lower())

        # Check if references context data
        activities = context.get("activities", [])
        activity_names = [a.get("name", "").lower() for a in activities]
        references_activities = any(name in text.lower() for name in activity_names if name)

        base_score = 60
        score = base_score + (evidence_count * 5) + (20 if references_activities else 0)
        return max(0, min(100, score))

    def _score_actionability(self, output: Dict[str, Any]) -> float:
        """Score how actionable the output is."""
        text = str(output).lower()

        # Action words
        action_words = [
            "should", "recommend", "try", "apply", "start",
            "focus", "develop", "create", "join", "submit",
        ]
        action_count = sum(1 for word in action_words if word in text)

        # Step indicators
        has_steps = bool(re.search(r'(step|first|next|then|\d\.)', text))

        base_score = 50
        score = base_score + (action_count * 8) + (20 if has_steps else 0)
        return max(0, min(100, score))

    def _score_coherence(self, output: Dict[str, Any]) -> float:
        """Score logical coherence."""
        # Simplified - would need NLP for full analysis
        text = str(output)
        sentences = text.split('. ')

        if len(sentences) < 2:
            return 60

        # Check for transition words
        transitions = ["however", "therefore", "additionally", "moreover", "because"]
        has_transitions = any(t in text.lower() for t in transitions)

        return 75 if has_transitions else 65

    def _score_authenticity(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """Score how authentic the output feels."""
        # Check for personal details
        text = str(output)
        has_specifics = bool(re.search(r'\b(I|my|me)\b', text))
        return 75 if has_specifics else 60

    def _score_differentiation(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """Score differentiation from typical applicants."""
        return self._score_uniqueness(output, context)

    def _score_connection(self, output: Dict[str, Any]) -> float:
        """Score narrative connection/flow."""
        return self._score_coherence(output)

    def _score_relevance(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """Score relevance to student profile."""
        # Check if output references student's interests
        profile = context.get("profile", {})
        spike = profile.get("spike", "")
        archetype = profile.get("archetype", "")

        text = str(output).lower()
        references_spike = spike and spike.lower() in text
        references_archetype = archetype and archetype.lower() in text

        base_score = 60
        return base_score + (20 if references_spike else 0) + (10 if references_archetype else 0)

    def _score_feasibility(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """Score feasibility of recommendations."""
        constraints = context.get("constraints", {})
        budget = constraints.get("budget", float("inf"))
        hours = constraints.get("weekly_hours", float("inf"))

        # Check if output respects constraints
        items = output.get("items", [])
        if not items:
            return 70

        feasible_count = 0
        for item in items:
            cost = item.get("cost", 0)
            time = item.get("hours", 0)
            if cost <= budget and time <= hours:
                feasible_count += 1

        return min(100, 50 + (feasible_count / max(1, len(items))) * 50)

    def _score_timing(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """Score timing appropriateness."""
        grade = context.get("grade", 11)
        phase = context.get("current_phase", "activities")

        # Check if recommendations are grade-appropriate
        items = output.get("items", [])
        if not items:
            return 70

        appropriate_count = sum(
            1 for item in items
            if grade in item.get("eligible_grades", [9, 10, 11, 12])
        )

        return min(100, 50 + (appropriate_count / max(1, len(items))) * 50)

    def _score_comprehensiveness(self, output: Dict[str, Any]) -> float:
        """Score completeness of gameplan."""
        required_sections = [
            "priorities", "timeline", "activities", "awards",
            "programs", "next_steps"
        ]

        present = sum(1 for section in required_sections if section in output)
        return (present / len(required_sections)) * 100

    def _score_prioritization(self, output: Dict[str, Any]) -> float:
        """Score quality of prioritization."""
        priorities = output.get("priorities", [])
        if not priorities:
            return 50

        # Check for priority levels
        has_levels = all(
            "priority" in p or "level" in p or "order" in p
            for p in priorities
        )

        return 80 if has_levels else 60

    def _score_personalization(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """Score level of personalization."""
        profile = context.get("profile", {})
        name = profile.get("name", "")
        spike = profile.get("spike", "")

        text = str(output)
        uses_name = name and name in text
        references_spike = spike and spike.lower() in text.lower()

        base_score = 50
        return base_score + (25 if uses_name else 0) + (25 if references_spike else 0)

    def _validate_type_specific(
        self,
        output: Dict[str, Any],
        output_type: str,
        context: Dict[str, Any],
    ) -> List[str]:
        """Type-specific validation rules."""
        errors = []

        if output_type == "spike":
            spike = output.get("spike", "")
            if len(spike) < 20:
                errors.append("Spike is too short (needs more detail)")
            if len(spike) > 200:
                errors.append("Spike is too long (should be concise)")

        elif output_type == "gameplan":
            if not output.get("priorities"):
                errors.append("Gameplan missing priorities section")
            if not output.get("next_steps"):
                errors.append("Gameplan missing next steps")

        elif output_type == "recommendation":
            items = output.get("items", [])
            if len(items) == 0:
                errors.append("No recommendations provided")
            if len(items) > 20:
                errors.append("Too many recommendations (may overwhelm student)")

        return errors

    def _generate_suggestions(
        self,
        scores: Dict[str, float],
        dimensions: List[QualityDimension],
        output_type: str,
    ) -> List[str]:
        """Generate improvement suggestions based on scores."""
        suggestions = []

        for dim in dimensions:
            if dim.name in scores and scores[dim.name] < dim.min_score + 20:
                if dim.name == "specificity":
                    suggestions.append("Add more specific details and examples")
                elif dim.name == "uniqueness":
                    suggestions.append("Avoid cliches; highlight what makes this unique")
                elif dim.name == "actionability":
                    suggestions.append("Include clear action steps")
                elif dim.name == "personalization":
                    suggestions.append("Reference student's specific interests and activities")

        return suggestions[:3]  # Top 3 suggestions


# Convenience function
def validate_output(
    output: Dict[str, Any],
    output_type: str,
    context: Optional[Dict[str, Any]] = None,
) -> ValidationResult:
    """Quick helper to validate output."""
    validator = OutputValidator()
    return validator.validate(output, output_type, context)
