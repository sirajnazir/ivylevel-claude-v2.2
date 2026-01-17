"""
A7: Self-Correction Pattern - Implementation

Internal critique and revision within a single generation, without full reflection loop.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import logging
import re

logger = logging.getLogger(__name__)


class CorrectionAttempt(BaseModel):
    """A self-correction attempt."""
    attempt_number: int
    original_response: str
    identified_issues: List[str]
    corrected_response: str
    confidence_before: float
    confidence_after: float


class SelfCorrectionResult(BaseModel):
    """Result of self-correction process."""
    final_response: str
    was_corrected: bool = False
    correction_attempts: List[CorrectionAttempt] = Field(default_factory=list)
    final_confidence: float = 0.7


class SelfCorrector:
    """
    Self-correction pattern for agent responses.

    Pattern A7: Self-Correction

    Unlike E3 Reflection Loops (post-generation), this happens
    within a single generation cycle - the model critiques and
    fixes its own output before returning.

    Integration with Critical 15:
    - Uses A4 Chain-of-Thought for critique
    - Lighter weight than E7 Producer-Critic
    """

    def __init__(
        self,
        llm_client=None,
        max_corrections: int = 1,
        min_confidence: float = 0.7,
    ):
        """
        Initialize self-corrector.

        Args:
            llm_client: LLM for self-critique
            max_corrections: Maximum correction attempts
            min_confidence: Minimum confidence to skip correction
        """
        self.llm = llm_client
        self.max_corrections = max_corrections
        self.min_confidence = min_confidence

    async def generate_with_self_correction(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        check_criteria: Optional[List[str]] = None,
    ) -> SelfCorrectionResult:
        """
        Generate response with built-in self-correction.

        Args:
            prompt: The prompt to respond to
            context: Additional context
            check_criteria: Specific things to check for

        Returns:
            SelfCorrectionResult with corrected response
        """
        context = context or {}
        check_criteria = check_criteria or [
            "factual accuracy",
            "relevance to question",
            "clarity and actionability",
            "appropriate tone",
        ]

        # Initial generation with self-critique prompt
        initial_response, initial_confidence, issues = await self._generate_and_critique(
            prompt=prompt,
            context=context,
            check_criteria=check_criteria,
        )

        if initial_confidence >= self.min_confidence or not issues:
            return SelfCorrectionResult(
                final_response=initial_response,
                was_corrected=False,
                final_confidence=initial_confidence,
            )

        # Self-correction needed
        attempts = []
        current_response = initial_response
        current_issues = issues

        for i in range(self.max_corrections):
            # Generate corrected version
            corrected, new_confidence, new_issues = await self._correct(
                original=current_response,
                issues=current_issues,
                prompt=prompt,
                context=context,
            )

            attempts.append(CorrectionAttempt(
                attempt_number=i + 1,
                original_response=current_response,
                identified_issues=current_issues,
                corrected_response=corrected,
                confidence_before=initial_confidence if i == 0 else attempts[-1].confidence_after,
                confidence_after=new_confidence,
            ))

            if new_confidence >= self.min_confidence or not new_issues:
                break

            current_response = corrected
            current_issues = new_issues

        return SelfCorrectionResult(
            final_response=attempts[-1].corrected_response if attempts else initial_response,
            was_corrected=True,
            correction_attempts=attempts,
            final_confidence=attempts[-1].confidence_after if attempts else initial_confidence,
        )

    async def _generate_and_critique(
        self,
        prompt: str,
        context: Dict[str, Any],
        check_criteria: List[str],
    ) -> tuple:
        """Generate response and self-critique in one call."""
        criteria_text = "\n".join(f"- {c}" for c in check_criteria)

        full_prompt = f"""
{prompt}

CONTEXT:
{context}

---

After generating your response, critique it against these criteria:
{criteria_text}

Respond in this format:

RESPONSE:
[Your response to the prompt]

SELF-CRITIQUE:
- Confidence (0.0-1.0): [score]
- Issues found: [list any issues, or "None"]
"""

        if self.llm:
            try:
                response = await self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.5,
                )

                content = response.choices[0].message.content
                return self._parse_response_and_critique(content)
            except Exception as e:
                logger.error(f"Generate and critique failed: {e}")

        return ("Unable to generate response", 0.5, ["Generation failed"])

    async def _correct(
        self,
        original: str,
        issues: List[str],
        prompt: str,
        context: Dict[str, Any],
    ) -> tuple:
        """Generate corrected version addressing issues."""
        correction_prompt = f"""
Original prompt: {prompt}

Original response:
{original}

Issues identified:
{chr(10).join(f"- {i}" for i in issues)}

Generate a CORRECTED response that fixes these issues.
Then self-critique the corrected version.

CORRECTED RESPONSE:
[Your improved response]

SELF-CRITIQUE:
- Confidence (0.0-1.0): [score]
- Remaining issues: [list any remaining issues, or "None"]
"""

        if self.llm:
            try:
                response = await self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": correction_prompt}],
                    temperature=0.3,
                )

                content = response.choices[0].message.content
                return self._parse_response_and_critique(content)
            except Exception as e:
                logger.error(f"Correction failed: {e}")

        return (original, 0.5, issues)

    def _parse_response_and_critique(
        self,
        content: str,
    ) -> tuple:
        """Parse response and self-critique from LLM output."""
        # Extract response
        response = content
        confidence = 0.5  # Default when parsing fails
        issues = []

        if "RESPONSE:" in content and "SELF-CRITIQUE:" in content:
            parts = content.split("SELF-CRITIQUE:")
            response = parts[0].replace("RESPONSE:", "").strip()
            critique = parts[1]

            # Extract confidence - match patterns like "Confidence (0.0-1.0): 0.8" or "Confidence: 0.8"
            conf_match = re.search(r"Confidence[^:]*:\s*([0-9.]+)", critique)
            if conf_match:
                try:
                    confidence = float(conf_match.group(1))
                except ValueError:
                    pass

            # Extract issues - check for "None" first
            if "Issues found:" in critique:
                issues_part = critique.split("Issues found:")[-1].strip()
                # Check if first line contains "None"
                first_line = issues_part.split("\n")[0].strip()
                if "none" not in first_line.lower():
                    issues = [
                        i.strip().lstrip("-").strip()
                        for i in issues_part.split("\n")
                        if i.strip() and i.strip() != "-" and not i.strip().startswith("Confidence")
                    ]

        elif "CORRECTED RESPONSE:" in content:
            parts = content.split("SELF-CRITIQUE:")
            response = parts[0].replace("CORRECTED RESPONSE:", "").strip()
            if len(parts) > 1:
                critique = parts[1]
                conf_match = re.search(r"Confidence[^:]*:\s*([0-9.]+)", critique)
                if conf_match:
                    try:
                        confidence = float(conf_match.group(1))
                    except ValueError:
                        pass

        return (response, confidence, issues)
