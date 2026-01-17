"""
A2: Deliberative Reasoning Pattern - Implementation

Multi-step planning before acting. Used for complex tasks that require careful consideration.
"""

from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class DeliberationStep(BaseModel):
    """A step in deliberative reasoning."""
    step_name: str
    question: str
    analysis: str
    conclusion: str
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)


class DeliberationResult(BaseModel):
    """Result of deliberative reasoning."""
    task: str
    steps: List[DeliberationStep] = Field(default_factory=list)

    # Final decision
    final_decision: str = ""
    decision_reasoning: str = ""
    decision_confidence: float = 0.7

    # Alternatives considered
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)

    # Metadata
    deliberation_time_ms: int = 0


class DeliberativeReasoner:
    """
    Deliberative reasoning for complex decisions.

    Pattern A2: Deliberative Reasoning

    Unlike reactive (quick response) or reflective (learning from past),
    deliberative reasoning plans multiple steps before acting.

    Steps:
    1. Understand: What is actually being asked?
    2. Context: What relevant information do I have?
    3. Options: What are the possible approaches?
    4. Evaluate: Which approach is best for this student?
    5. Plan: What specific steps should be taken?
    """

    def __init__(
        self,
        llm_client=None,
    ):
        self.llm = llm_client

    async def deliberate(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        deliberation_steps: Optional[List[Tuple[str, str]]] = None,
    ) -> DeliberationResult:
        """
        Perform deliberative reasoning on a task.

        Args:
            task: The task/question to deliberate on
            context: Student and situation context
            deliberation_steps: Custom steps (or use default)

        Returns:
            DeliberationResult with reasoned decision
        """
        start_time = datetime.utcnow()
        context = context or {}

        # Default deliberation framework
        default_steps = [
            ("understand", "What is the student actually asking for or needing?"),
            ("context", "What relevant context do I have about this student?"),
            ("options", "What are the possible approaches or responses?"),
            ("evaluate", "Which approach best fits this student's situation?"),
            ("plan", "What specific recommendation or action should I take?"),
        ]

        steps = []
        accumulated_reasoning = ""

        for step_name, question in (deliberation_steps or default_steps):
            step_result = await self._deliberate_step(
                task=task,
                step_name=step_name,
                question=question,
                context=context,
                previous_reasoning=accumulated_reasoning,
            )

            steps.append(DeliberationStep(
                step_name=step_name,
                question=question,
                analysis=step_result["analysis"],
                conclusion=step_result["conclusion"],
                confidence=step_result.get("confidence", 0.7),
            ))

            accumulated_reasoning += f"\n{step_name}: {step_result['conclusion']}"

        # Generate final decision
        final_decision, reasoning, confidence = await self._synthesize_decision(
            task=task,
            steps=steps,
            context=context,
        )

        end_time = datetime.utcnow()

        return DeliberationResult(
            task=task,
            steps=steps,
            final_decision=final_decision,
            decision_reasoning=reasoning,
            decision_confidence=confidence,
            deliberation_time_ms=int((end_time - start_time).total_seconds() * 1000),
        )

    async def _deliberate_step(
        self,
        task: str,
        step_name: str,
        question: str,
        context: Dict[str, Any],
        previous_reasoning: str,
    ) -> Dict[str, Any]:
        """Execute a single deliberation step."""
        prompt = f"""
You are deliberating on a coaching task.

TASK: {task}

STUDENT CONTEXT:
- Name: {context.get('student_name', 'the student')}
- Archetype: {context.get('archetype', 'unknown')}
- Current phase: {context.get('phase', 'unknown')}

PREVIOUS REASONING:
{previous_reasoning or "None yet"}

CURRENT STEP: {step_name}
QUESTION: {question}

Provide:
1. ANALYSIS: Your thinking process (2-3 sentences)
2. CONCLUSION: Your answer to the question (1-2 sentences)
3. CONFIDENCE: How confident are you (0.0-1.0)

Respond in JSON:
{{"analysis": "...", "conclusion": "...", "confidence": 0.X}}
"""

        if self.llm:
            try:
                response = await self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"},
                )

                return json.loads(response.choices[0].message.content)
            except Exception as e:
                logger.error(f"Deliberation step failed: {e}")

        return {
            "analysis": "Unable to analyze",
            "conclusion": "Proceeding with best available information",
            "confidence": 0.5,
        }

    async def _synthesize_decision(
        self,
        task: str,
        steps: List[DeliberationStep],
        context: Dict[str, Any],
    ) -> Tuple[str, str, float]:
        """Synthesize final decision from deliberation steps."""
        steps_summary = "\n".join([
            f"{s.step_name}: {s.conclusion}"
            for s in steps
        ])

        prompt = f"""
Based on deliberative reasoning, provide your final recommendation.

TASK: {task}

DELIBERATION SUMMARY:
{steps_summary}

Provide:
1. DECISION: Your specific recommendation (1-2 sentences)
2. REASONING: Brief justification (1-2 sentences)
3. CONFIDENCE: Overall confidence (0.0-1.0)

Respond in JSON:
{{"decision": "...", "reasoning": "...", "confidence": 0.X}}
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
                return (
                    result.get("decision", ""),
                    result.get("reasoning", ""),
                    result.get("confidence", 0.7),
                )
            except Exception as e:
                logger.error(f"Decision synthesis failed: {e}")

        # Fallback
        avg_confidence = sum(s.confidence for s in steps) / len(steps) if steps else 0.5
        return (
            steps[-1].conclusion if steps else "Unable to determine",
            "Based on available deliberation",
            avg_confidence,
        )
