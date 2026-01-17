"""
H4: Pivot Strategy Pattern - Implementation

Alternative approaches when current approach fails. Graceful recovery with new direction.
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PivotTrigger(BaseModel):
    """Condition that triggers a pivot."""
    trigger_type: str  # "max_attempts", "low_confidence", "student_feedback", "deadline_pressure"
    description: str
    threshold: Optional[float] = None


class PivotOption(BaseModel):
    """A potential pivot strategy."""
    option_id: str
    name: str
    description: str
    approach_type: str

    # Selection criteria
    applicability_score: float = Field(default=0.5, ge=0.0, le=1.0)
    historical_success_rate: Optional[float] = None

    # Implementation
    action: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class PivotResult(BaseModel):
    """Result of a pivot operation."""
    pivoted: bool
    original_approach: str
    new_approach: Optional[str] = None

    # Decision
    pivot_reason: str
    options_considered: List[PivotOption] = Field(default_factory=list)

    # Outcome
    pivot_successful: Optional[bool] = None
    result: Optional[Any] = None


class PivotStrategy:
    """
    Pivot strategy for graceful recovery.

    Pattern H4: Pivot Strategy (USP)

    When an approach isn't working:
    1. Recognize the failure
    2. Identify alternative approaches
    3. Select best pivot based on context
    4. Execute new approach

    Integration with Critical 15:
    - Triggered by H1 Exception Handling
    - Uses B2 Episodic Memory to find what worked
    - Feeds I3 Goal Monitoring with approach changes
    """

    def __init__(
        self,
        episodic_memory=None,
    ):
        """
        Initialize pivot strategy.

        Args:
            episodic_memory: For historical success data
        """
        self.episodic = episodic_memory

    async def should_pivot(
        self,
        context: Dict[str, Any],
        triggers: Optional[List[PivotTrigger]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if a pivot is needed.

        Args:
            context: Current situation context
            triggers: Custom triggers (or use defaults)

        Returns:
            (should_pivot, reason)
        """
        triggers = triggers or self._get_default_triggers()

        for trigger in triggers:
            if self._check_trigger(trigger, context):
                return (True, trigger.description)

        return (False, None)

    async def get_pivot_options(
        self,
        profile_id: str,
        current_approach: str,
        context: Dict[str, Any],
    ) -> List[PivotOption]:
        """
        Get available pivot options.

        Args:
            profile_id: Student profile
            current_approach: What's currently being tried
            context: Situation context

        Returns:
            List of pivot options ranked by applicability
        """
        options = []

        # Get coaching-specific pivot options
        coaching_pivots = self._get_coaching_pivot_options(current_approach, context)

        # Enrich with historical data if available
        if self.episodic:
            success_patterns = await self.episodic.get_success_patterns(profile_id)

            for option in coaching_pivots:
                if option.approach_type in success_patterns:
                    pattern = success_patterns[option.approach_type]
                    option.historical_success_rate = pattern["success_rate"]
                    # Boost applicability if historically successful
                    if pattern["success_rate"] >= 0.6:
                        option.applicability_score = min(
                            option.applicability_score + 0.2,
                            1.0
                        )

        # Sort by applicability
        options = sorted(coaching_pivots, key=lambda o: o.applicability_score, reverse=True)

        return options

    async def execute_pivot(
        self,
        profile_id: str,
        original_approach: str,
        selected_option: PivotOption,
        execute_func: Callable[..., Awaitable[Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> PivotResult:
        """
        Execute a pivot to new approach.

        Args:
            profile_id: Student profile
            original_approach: What was being tried
            selected_option: The pivot option to try
            execute_func: Function to execute new approach
            context: Additional context

        Returns:
            PivotResult
        """
        logger.info(
            f"Pivoting from {original_approach} to {selected_option.name} "
            f"for profile {profile_id}"
        )

        try:
            # Execute new approach
            result = await execute_func(
                approach=selected_option.approach_type,
                **selected_option.parameters,
            )

            # Record the pivot in episodic memory
            if self.episodic:
                await self.episodic.record_episode(
                    profile_id=profile_id,
                    situation=f"Pivoted from {original_approach}",
                    action_taken=f"Switched to {selected_option.name}",
                    approach_type=selected_option.approach_type,
                    agent_name="pivot_strategy",
                    outcome="success" if result else "partial",
                    context={
                        "original_approach": original_approach,
                        "pivot_reason": context.get("pivot_reason") if context else None,
                    },
                )

            return PivotResult(
                pivoted=True,
                original_approach=original_approach,
                new_approach=selected_option.approach_type,
                pivot_reason=context.get("pivot_reason", "approach not working") if context else "approach not working",
                pivot_successful=True,
                result=result,
            )
        except Exception as e:
            logger.error(f"Pivot execution failed: {e}")

            return PivotResult(
                pivoted=True,
                original_approach=original_approach,
                new_approach=selected_option.approach_type,
                pivot_reason=context.get("pivot_reason", "approach not working") if context else "approach not working",
                pivot_successful=False,
                result=str(e),
            )

    def _get_default_triggers(self) -> List[PivotTrigger]:
        """Default pivot triggers."""
        return [
            PivotTrigger(
                trigger_type="max_attempts",
                description="Maximum attempts reached without success",
                threshold=3,
            ),
            PivotTrigger(
                trigger_type="low_confidence",
                description="Agent confidence dropped below threshold",
                threshold=0.4,
            ),
            PivotTrigger(
                trigger_type="student_feedback",
                description="Student expressed confusion or frustration",
            ),
            PivotTrigger(
                trigger_type="deadline_pressure",
                description="Deadline approaching with insufficient progress",
                threshold=3,  # days
            ),
        ]

    def _check_trigger(
        self,
        trigger: PivotTrigger,
        context: Dict[str, Any],
    ) -> bool:
        """Check if a trigger condition is met."""
        if trigger.trigger_type == "max_attempts":
            attempts = context.get("attempts", 0)
            return attempts >= (trigger.threshold or 3)

        elif trigger.trigger_type == "low_confidence":
            confidence = context.get("confidence", 1.0)
            return confidence < (trigger.threshold or 0.4)

        elif trigger.trigger_type == "student_feedback":
            sentiment = context.get("student_sentiment", "neutral")
            return sentiment in ["frustrated", "confused", "negative"]

        elif trigger.trigger_type == "deadline_pressure":
            days_until = context.get("days_until_deadline")
            if days_until is not None:
                return days_until <= (trigger.threshold or 3)

        return False

    def _get_coaching_pivot_options(
        self,
        current_approach: str,
        context: Dict[str, Any],
    ) -> List[PivotOption]:
        """
        Get coaching-specific pivot options.

        USP: These pivots are based on Jenny's coaching methodology.
        """
        options = []

        # Communication style pivots
        if current_approach != "examples_over_instructions":
            options.append(PivotOption(
                option_id="pivot_examples",
                name="Switch to Examples",
                description="Show examples instead of explaining",
                approach_type="examples_over_instructions",
                applicability_score=0.8,
            ))

        if current_approach != "break_into_smaller_tasks":
            options.append(PivotOption(
                option_id="pivot_smaller",
                name="Break Into Smaller Tasks",
                description="Divide the task into 15-minute chunks",
                approach_type="break_into_smaller_tasks",
                applicability_score=0.7,
            ))

        if current_approach != "socratic_questioning":
            options.append(PivotOption(
                option_id="pivot_socratic",
                name="Socratic Approach",
                description="Guide through questions instead of answers",
                approach_type="socratic_questioning",
                applicability_score=0.6,
            ))

        # Emotional support pivots
        if context.get("student_sentiment") in ["frustrated", "overwhelmed"]:
            options.append(PivotOption(
                option_id="pivot_empathy",
                name="Empathy First",
                description="Acknowledge feelings before problem-solving",
                approach_type="empathy_first",
                applicability_score=0.9,
            ))

        # Deadline pivots
        if context.get("days_until_deadline", 100) <= 7:
            options.append(PivotOption(
                option_id="pivot_triage",
                name="Urgent Triage",
                description="Focus on minimum viable completion",
                approach_type="urgent_triage",
                applicability_score=0.85,
            ))

        return options
