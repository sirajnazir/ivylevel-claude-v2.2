"""
E3: Reflection Loops Pattern - Implementation

Post-generation revision loop. If output doesn't meet criteria, reflect and improve.
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable
from datetime import datetime
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ReflectionStep(BaseModel):
    """A single reflection step."""
    step_number: int
    original_output: str
    reflection: str  # What went wrong
    improvement_plan: str  # How to fix
    revised_output: str
    improvement_score: float = Field(ge=0.0, le=1.0)


class ReflectionResult(BaseModel):
    """Result of reflection loop."""
    final_output: str
    original_output: str

    # Process
    reflection_steps: List[ReflectionStep] = Field(default_factory=list)
    total_iterations: int = 0

    # Outcome
    improved: bool = False
    improvement_delta: float = 0.0
    final_quality_score: float = 0.0


class ReflectionLoop:
    """
    Reflection loop for output improvement.

    Pattern E3: Reflection Loops

    Flow:
    1. Receive output that failed critique
    2. Reflect on what went wrong
    3. Plan improvements
    4. Generate revised output
    5. Repeat until acceptable or max iterations

    Integration with Critical 15:
    - Triggered by E7 Producer-Critic when quality low
    - Uses A4 Chain-of-Thought for structured reflection
    - Uses E1 Validation for checking improvements
    """

    def __init__(
        self,
        llm_client=None,
        max_reflections: int = 2,
    ):
        """
        Initialize reflection loop.

        Args:
            llm_client: LLM for reflection
            max_reflections: Maximum reflection iterations
        """
        self.llm = llm_client
        self.max_reflections = max_reflections

    async def reflect_and_improve(
        self,
        original_output: str,
        critique_feedback: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        regenerate_func: Optional[Callable[..., Awaitable[str]]] = None,
    ) -> ReflectionResult:
        """
        Run reflection loop to improve output.

        Args:
            original_output: The original output that needs improvement
            critique_feedback: Feedback from critic
            context: Additional context
            regenerate_func: Optional function to regenerate (instead of LLM)

        Returns:
            ReflectionResult with improved output
        """
        current_output = original_output
        steps = []
        original_score = critique_feedback.get("quality_score", 0.5)

        for i in range(self.max_reflections):
            # Step 1: Reflect on what went wrong
            reflection = await self._reflect(
                current_output,
                critique_feedback,
                context,
            )

            # Step 2: Plan improvements
            improvement_plan = await self._plan_improvements(
                reflection,
                critique_feedback,
            )

            # Step 3: Generate revised output
            if regenerate_func:
                revised_output = await regenerate_func(
                    _reflection_context={
                        "reflection": reflection,
                        "plan": improvement_plan,
                        "previous_output": current_output,
                    }
                )
            else:
                revised_output = await self._revise(
                    current_output,
                    reflection,
                    improvement_plan,
                    context,
                )

            # Step 4: Evaluate improvement
            improvement_score = await self._evaluate_improvement(
                original_output,
                revised_output,
                critique_feedback,
            )

            steps.append(ReflectionStep(
                step_number=i + 1,
                original_output=current_output,
                reflection=reflection,
                improvement_plan=improvement_plan,
                revised_output=revised_output,
                improvement_score=improvement_score,
            ))

            current_output = revised_output

            # Check if sufficient improvement
            if improvement_score >= 0.7:
                break

        final_score = steps[-1].improvement_score if steps else original_score

        return ReflectionResult(
            final_output=current_output,
            original_output=original_output,
            reflection_steps=steps,
            total_iterations=len(steps),
            improved=final_score > original_score,
            improvement_delta=final_score - original_score,
            final_quality_score=final_score,
        )

    async def _reflect(
        self,
        output: str,
        critique_feedback: Dict[str, Any],
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Reflect on what went wrong with the output."""
        weaknesses = critique_feedback.get("weaknesses", [])
        suggestions = critique_feedback.get("improvement_suggestions", [])

        prompt = f"""
Reflect on why this coaching response needs improvement.

OUTPUT:
{output}

IDENTIFIED WEAKNESSES:
{chr(10).join(f"- {w}" for w in weaknesses)}

IMPROVEMENT SUGGESTIONS:
{chr(10).join(f"- {s}" for s in suggestions)}

Provide a brief reflection (2-3 sentences) on:
1. What's the core issue with this response?
2. Why doesn't it serve the student well?
"""

        if self.llm:
            try:
                response = await self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=200,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Reflection failed: {e}")

        return f"Issues identified: {', '.join(weaknesses[:3])}"

    async def _plan_improvements(
        self,
        reflection: str,
        critique_feedback: Dict[str, Any],
    ) -> str:
        """Plan specific improvements."""
        focus = critique_feedback.get("regeneration_focus", "")
        suggestions = critique_feedback.get("improvement_suggestions", [])

        prompt = f"""
Based on this reflection, plan specific improvements.

REFLECTION:
{reflection}

FOCUS AREA:
{focus}

SUGGESTIONS:
{chr(10).join(f"- {s}" for s in suggestions)}

Provide a brief improvement plan (2-3 bullet points):
"""

        if self.llm:
            try:
                response = await self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=200,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Planning failed: {e}")

        return f"Focus on: {focus or 'addressing identified weaknesses'}"

    async def _revise(
        self,
        original: str,
        reflection: str,
        plan: str,
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Generate revised output."""
        context = context or {}

        prompt = f"""
Revise this coaching response based on the reflection and plan.

ORIGINAL RESPONSE:
{original}

REFLECTION:
{reflection}

IMPROVEMENT PLAN:
{plan}

CONTEXT:
- Student: {context.get('student_name', 'the student')}
- Task: {context.get('task_type', 'coaching')}

Generate an IMPROVED response that addresses all identified issues.
Keep the same general intent but fix the problems.
"""

        if self.llm:
            try:
                response = await self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=500,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Revision failed: {e}")

        return original  # Fallback to original

    async def _evaluate_improvement(
        self,
        original: str,
        revised: str,
        critique_feedback: Dict[str, Any],
    ) -> float:
        """Evaluate how much the revision improved."""
        weaknesses = critique_feedback.get("weaknesses", [])

        prompt = f"""
Evaluate how well the revised response addresses the original issues.

ORIGINAL ISSUES:
{chr(10).join(f"- {w}" for w in weaknesses)}

ORIGINAL RESPONSE:
{original}

REVISED RESPONSE:
{revised}

Score the improvement from 0.0 to 1.0:
- 0.0 = No improvement
- 0.5 = Some issues addressed
- 1.0 = All issues fully addressed

Respond with just the score (e.g., "0.7"):
"""

        if self.llm:
            try:
                response = await self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=10,
                )
                score_text = response.choices[0].message.content.strip()
                return float(score_text)
            except Exception as e:
                logger.error(f"Evaluation failed: {e}")

        return 0.6  # Assume some improvement
