"""
A3: Reflective Reasoning Pattern - Implementation

Self-critique and iterative improvement.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import logging
import re

logger = logging.getLogger(__name__)


class ReflectionResult(BaseModel):
    """Result of a reflection cycle."""
    original_response: str
    critique: str
    improved_response: str
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    issues_found: List[str] = Field(default_factory=list)
    improvements_made: List[str] = Field(default_factory=list)
    iteration: int = 1
    total_iterations: int = 1


class ReflectiveReasoner:
    """
    Reflective reasoning with self-critique.

    Pattern A3: Reflective Reasoning

    Process:
    1. Generate initial response
    2. Critique the response
    3. Improve based on critique
    4. Repeat if confidence below threshold

    GUARDRAILS:
    - NEW class - does not modify existing reasoning
    - Uses existing LLM interface
    - Configurable max iterations
    """

    def __init__(
        self,
        llm_client=None,
        max_iterations: int = 3,
        confidence_threshold: float = 0.85,
    ):
        """
        Initialize reflective reasoner.

        Args:
            llm_client: LLM client for generation
            max_iterations: Maximum reflection iterations
            confidence_threshold: Minimum confidence to accept
        """
        self.llm = llm_client
        self.max_iterations = max_iterations
        self.confidence_threshold = confidence_threshold

    async def reason(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ReflectionResult:
        """
        Generate response with reflective improvement.

        Args:
            prompt: The prompt to respond to
            context: Additional context

        Returns:
            ReflectionResult with improved response
        """
        # Generate initial response
        initial = await self._generate(prompt, context)

        best_result = ReflectionResult(
            original_response=initial,
            critique="",
            improved_response=initial,
        )

        for iteration in range(1, self.max_iterations + 1):
            # Critique current response
            critique_result = await self._critique(
                prompt,
                best_result.improved_response,
                context,
            )

            critique, confidence, issues = critique_result

            best_result.critique = critique
            best_result.confidence = confidence
            best_result.issues_found = issues
            best_result.iteration = iteration
            best_result.total_iterations = iteration

            # Check if good enough
            if confidence >= self.confidence_threshold:
                logger.info(
                    f"Reflection complete at iteration {iteration} "
                    f"(confidence: {confidence:.2f})"
                )
                break

            # Improve if issues found
            if issues:
                improved = await self._improve(
                    prompt,
                    best_result.improved_response,
                    issues,
                    context,
                )
                best_result.improved_response = improved
                best_result.improvements_made.append(
                    f"Iteration {iteration}: addressed {len(issues)} issues"
                )

        return best_result

    async def _generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Generate initial response."""
        if not self.llm:
            return f"Response to: {prompt[:100]}..."

        system = """You are a helpful assistant. Provide a thoughtful,
        accurate response to the user's query."""

        if context:
            system += f"\n\nContext: {context}"

        try:
            response = await self.llm.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"Unable to generate response: {e}"

    async def _critique(
        self,
        original_prompt: str,
        response: str,
        context: Optional[Dict[str, Any]],
    ) -> Tuple[str, float, List[str]]:
        """Critique a response."""
        if not self.llm:
            return ("No critique available", 0.7, [])

        critique_prompt = f"""Analyze this response to the user's question.

USER QUESTION: {original_prompt}

RESPONSE TO CRITIQUE:
{response}

Evaluate for:
1. Accuracy - Are all facts correct?
2. Completeness - Does it fully address the question?
3. Clarity - Is it easy to understand?
4. Relevance - Does it stay on topic?
5. Helpfulness - Will it actually help the user?

RESPOND IN THIS FORMAT:
CRITIQUE: [Your detailed critique]
CONFIDENCE: [0.0-1.0 score for response quality]
ISSUES FOUND: [List specific issues, or "None" if the response is good]
"""

        try:
            result = await self.llm.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a critical reviewer."},
                    {"role": "user", "content": critique_prompt},
                ],
                temperature=0.3,
            )
            return self._parse_critique(result.choices[0].message.content)
        except Exception as e:
            logger.error(f"Critique failed: {e}")
            return ("Critique unavailable", 0.7, [])

    def _parse_critique(
        self,
        content: str,
    ) -> Tuple[str, float, List[str]]:
        """Parse critique output."""
        critique = content
        confidence = 0.7
        issues = []

        # Extract confidence
        conf_match = re.search(r"CONFIDENCE[^:]*:\s*([0-9.]+)", content, re.IGNORECASE)
        if conf_match:
            try:
                confidence = float(conf_match.group(1))
                confidence = max(0.0, min(1.0, confidence))
            except ValueError:
                pass

        # Extract critique section
        crit_match = re.search(
            r"CRITIQUE[^:]*:\s*(.+?)(?=CONFIDENCE|ISSUES|$)",
            content,
            re.DOTALL | re.IGNORECASE
        )
        if crit_match:
            critique = crit_match.group(1).strip()

        # Extract issues
        issues_match = re.search(
            r"ISSUES FOUND[^:]*:\s*(.+?)$",
            content,
            re.DOTALL | re.IGNORECASE
        )
        if issues_match:
            issues_text = issues_match.group(1).strip()
            if "none" not in issues_text.lower():
                issues = [
                    line.strip().lstrip("-•*").strip()
                    for line in issues_text.split("\n")
                    if line.strip() and line.strip() not in ["-", "•", "*"]
                ]

        return (critique, confidence, issues)

    async def _improve(
        self,
        original_prompt: str,
        current_response: str,
        issues: List[str],
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Improve response based on issues."""
        if not self.llm:
            return current_response

        improve_prompt = f"""Improve this response by addressing the identified issues.

ORIGINAL QUESTION: {original_prompt}

CURRENT RESPONSE:
{current_response}

ISSUES TO ADDRESS:
{chr(10).join(f"- {issue}" for issue in issues)}

Provide an improved response that addresses all identified issues.

IMPROVED RESPONSE:"""

        try:
            result = await self.llm.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You improve responses based on feedback."},
                    {"role": "user", "content": improve_prompt},
                ],
                temperature=0.5,
            )
            return result.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Improvement failed: {e}")
            return current_response

    async def quick_reflect(
        self,
        response: str,
        criteria: Optional[List[str]] = None,
    ) -> Tuple[float, List[str]]:
        """
        Quick reflection without full improvement cycle.

        Args:
            response: Response to evaluate
            criteria: Specific criteria to check

        Returns:
            Tuple of (confidence, issues)
        """
        criteria = criteria or ["accuracy", "clarity", "helpfulness"]

        if not self.llm:
            return (0.7, [])

        prompt = f"""Rate this response on a scale of 0.0 to 1.0:

RESPONSE: {response}

CRITERIA: {', '.join(criteria)}

OUTPUT FORMAT:
SCORE: [0.0-1.0]
ISSUES: [list any issues, or "None"]
"""

        try:
            result = await self.llm.chat.completions.create(
                model="gpt-4o-mini",  # Faster model for quick check
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )

            content = result.choices[0].message.content

            # Parse score
            score = 0.7
            score_match = re.search(r"SCORE[^:]*:\s*([0-9.]+)", content, re.IGNORECASE)
            if score_match:
                score = float(score_match.group(1))

            # Parse issues
            issues = []
            issues_match = re.search(r"ISSUES[^:]*:\s*(.+?)$", content, re.DOTALL | re.IGNORECASE)
            if issues_match:
                issues_text = issues_match.group(1).strip()
                if "none" not in issues_text.lower():
                    issues = [i.strip() for i in issues_text.split("\n") if i.strip()]

            return (score, issues)
        except Exception as e:
            logger.error(f"Quick reflect failed: {e}")
            return (0.7, [])
