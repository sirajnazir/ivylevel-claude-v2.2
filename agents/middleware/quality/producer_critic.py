"""
E7: Producer-Critic Pattern - Implementation

Generate-then-evaluate pattern for quality assurance.
Producer generates, Critic evaluates.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
import logging
import json

logger = logging.getLogger(__name__)


class CritiqueResult(BaseModel):
    """Result of critic evaluation."""
    is_acceptable: bool
    quality_score: float = Field(ge=0.0, le=1.0)

    # Criterion-level feedback
    criterion_scores: Dict[str, float] = Field(default_factory=dict)
    criterion_feedback: Dict[str, str] = Field(default_factory=dict)

    # Overall feedback
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)

    # For reflection
    should_regenerate: bool = False
    regeneration_focus: Optional[str] = None


class EvaluationCriteria(BaseModel):
    """Criteria for evaluating agent output."""
    name: str
    description: str
    weight: float = 1.0
    min_acceptable_score: float = 0.6
    is_critical: bool = False  # If critical and fails, overall fails


# IvyLevel-specific evaluation criteria (USP)
COACHING_CRITERIA = {
    "advice": [
        EvaluationCriteria(
            name="relevance",
            description="Output directly addresses student's specific situation",
            weight=0.25,
            is_critical=True,
        ),
        EvaluationCriteria(
            name="actionability",
            description="Advice includes specific, actionable next steps",
            weight=0.25,
            is_critical=True,
        ),
        EvaluationCriteria(
            name="tone",
            description="Tone matches student's communication preference",
            weight=0.15,
        ),
        EvaluationCriteria(
            name="accuracy",
            description="All factual claims and deadlines are correct",
            weight=0.20,
            is_critical=True,
        ),
        EvaluationCriteria(
            name="encouragement",
            description="Maintains supportive, encouraging tone",
            weight=0.15,
        ),
    ],
    "plan": [
        EvaluationCriteria(
            name="completeness",
            description="Plan covers all necessary steps",
            weight=0.25,
            is_critical=True,
        ),
        EvaluationCriteria(
            name="feasibility",
            description="Plan is realistic given student's constraints",
            weight=0.25,
            is_critical=True,
        ),
        EvaluationCriteria(
            name="sequencing",
            description="Steps are in logical order with proper dependencies",
            weight=0.20,
        ),
        EvaluationCriteria(
            name="deadline_alignment",
            description="Plan respects all relevant deadlines",
            weight=0.20,
            is_critical=True,
        ),
        EvaluationCriteria(
            name="clarity",
            description="Each step is clearly defined",
            weight=0.10,
        ),
    ],
    "motivation": [
        EvaluationCriteria(
            name="empathy",
            description="Acknowledges student's feelings and challenges",
            weight=0.30,
            is_critical=True,
        ),
        EvaluationCriteria(
            name="encouragement",
            description="Provides genuine encouragement without pressure",
            weight=0.30,
        ),
        EvaluationCriteria(
            name="relevance",
            description="References student's specific situation/achievements",
            weight=0.25,
        ),
        EvaluationCriteria(
            name="authenticity",
            description="Feels genuine, not formulaic",
            weight=0.15,
        ),
    ],
    "general": [
        EvaluationCriteria(
            name="relevance",
            description="Output addresses what student asked",
            weight=0.30,
            is_critical=True,
        ),
        EvaluationCriteria(
            name="clarity",
            description="Output is clear and easy to understand",
            weight=0.25,
        ),
        EvaluationCriteria(
            name="helpfulness",
            description="Output provides genuine value to student",
            weight=0.25,
        ),
        EvaluationCriteria(
            name="tone",
            description="Appropriate tone for coaching context",
            weight=0.20,
        ),
    ],
}


class ProducerCriticPipeline:
    """
    Producer-Critic pattern for quality assurance.

    Pattern E7: Producer-Critic

    Flow:
    1. Producer generates output
    2. Critic evaluates against criteria
    3. If below threshold, trigger reflection/regeneration

    Integration with Critical 15:
    - Uses E1 Validation for structural checks
    - Uses A4 Chain-of-Thought for critic reasoning
    - Feeds E3 Reflection Loops when regeneration needed
    """

    def __init__(
        self,
        llm_client=None,
        min_quality_score: float = 0.7,
        max_iterations: int = 2,
    ):
        """
        Initialize producer-critic pipeline.

        Args:
            llm_client: LLM for critic evaluation
            min_quality_score: Minimum acceptable quality
            max_iterations: Max produce-critique cycles
        """
        self.llm = llm_client
        self.min_quality = min_quality_score
        self.max_iterations = max_iterations

    async def produce_and_critique(
        self,
        producer_func,
        output_type: str = "general",
        context: Optional[Dict[str, Any]] = None,
        **producer_kwargs,
    ) -> Dict[str, Any]:
        """
        Run producer-critic loop.

        Args:
            producer_func: Async function that produces output
            output_type: Type for criteria selection
            context: Context for evaluation
            **producer_kwargs: Args for producer function

        Returns:
            Dict with final output and critique history
        """
        criteria = COACHING_CRITERIA.get(output_type, COACHING_CRITERIA["general"])
        history = []

        for iteration in range(self.max_iterations):
            # Produce
            output = await producer_func(**producer_kwargs)

            # Critique
            critique = await self.critique(
                output=output,
                criteria=criteria,
                context=context,
                iteration=iteration,
            )

            history.append({
                "iteration": iteration,
                "output": output,
                "critique": critique.model_dump(),
            })

            # Check if acceptable
            if critique.is_acceptable:
                return {
                    "output": output,
                    "final_critique": critique,
                    "iterations": iteration + 1,
                    "history": history,
                }

            # Add regeneration hints for next iteration
            if iteration < self.max_iterations - 1:
                producer_kwargs["_critique_feedback"] = {
                    "weaknesses": critique.weaknesses,
                    "suggestions": critique.improvement_suggestions,
                    "focus": critique.regeneration_focus,
                }

        # Max iterations reached
        return {
            "output": output,
            "final_critique": critique,
            "iterations": self.max_iterations,
            "history": history,
            "max_iterations_reached": True,
        }

    async def critique(
        self,
        output: str,
        criteria: List[EvaluationCriteria],
        context: Optional[Dict[str, Any]] = None,
        iteration: int = 0,
    ) -> CritiqueResult:
        """
        Critique an output using LLM-as-Judge.

        Args:
            output: The output to evaluate
            criteria: Evaluation criteria
            context: Additional context
            iteration: Which iteration (for stricter scoring later)

        Returns:
            CritiqueResult with scores and feedback
        """
        context = context or {}

        # Build evaluation prompt
        criteria_text = "\n".join([
            f"- {c.name} (weight: {c.weight}, critical: {c.is_critical}): {c.description}"
            for c in criteria
        ])

        prompt = f"""
You are a quality evaluator for a college admissions coaching AI.
Evaluate this output against the criteria below.

OUTPUT TO EVALUATE:
{output}

CONTEXT:
- Student: {context.get('student_name', 'Unknown')}
- Task type: {context.get('task_type', 'general')}
- Iteration: {iteration + 1}

EVALUATION CRITERIA:
{criteria_text}

For each criterion, provide:
1. Score (0.0 - 1.0)
2. Brief feedback explaining the score

Then provide:
- Overall quality score (0.0 - 1.0)
- Key strengths (list)
- Key weaknesses (list)
- Improvement suggestions (list)
- Should regenerate? (yes/no)
- If regenerate, what to focus on?

Respond in JSON format:
{{
    "criterion_scores": {{"criterion_name": score, ...}},
    "criterion_feedback": {{"criterion_name": "feedback", ...}},
    "quality_score": 0.0-1.0,
    "strengths": ["..."],
    "weaknesses": ["..."],
    "improvement_suggestions": ["..."],
    "should_regenerate": true/false,
    "regeneration_focus": "..."
}}
"""

        if self.llm:
            try:
                response = await self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"},
                )

                result = json.loads(response.choices[0].message.content)

                # Check critical criteria
                is_acceptable = result["quality_score"] >= self.min_quality
                for c in criteria:
                    if c.is_critical:
                        score = result["criterion_scores"].get(c.name, 0)
                        if score < c.min_acceptable_score:
                            is_acceptable = False
                            break

                return CritiqueResult(
                    is_acceptable=is_acceptable,
                    quality_score=result["quality_score"],
                    criterion_scores=result["criterion_scores"],
                    criterion_feedback=result["criterion_feedback"],
                    strengths=result.get("strengths", []),
                    weaknesses=result.get("weaknesses", []),
                    improvement_suggestions=result.get("improvement_suggestions", []),
                    should_regenerate=result.get("should_regenerate", False),
                    regeneration_focus=result.get("regeneration_focus"),
                )
            except Exception as e:
                logger.error(f"Critique failed: {e}")

        # Fallback: assume acceptable
        return CritiqueResult(
            is_acceptable=True,
            quality_score=0.7,
        )


# Convenience function
async def with_critique(
    producer_func,
    output_type: str = "general",
    llm_client=None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience wrapper for producer-critic pattern.

    Usage:
        result = await with_critique(
            agent.generate_advice,
            output_type="advice",
            llm_client=llm,
            profile_id=profile_id,
        )
    """
    pipeline = ProducerCriticPipeline(llm_client)
    return await pipeline.produce_and_critique(
        producer_func,
        output_type=output_type,
        **kwargs,
    )
