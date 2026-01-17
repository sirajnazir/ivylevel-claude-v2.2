"""
Pattern E6: Guardrails
v5.4 True Autonomous Agents

3P: Guardrails AI (guardrails-ai)
USP: Minor-appropriate content filtering
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from pydantic import BaseModel, Field
import logging
import re

logger = logging.getLogger(__name__)


class GuardrailType(str, Enum):
    """Types of guardrails."""
    INPUT = "input"           # Filter student input
    OUTPUT = "output"         # Filter agent response
    CONTENT = "content"       # Content appropriateness
    SAFETY = "safety"         # Safety-critical


class GuardrailResult(BaseModel):
    """Result of guardrail check."""
    passed: bool
    guardrail_type: GuardrailType
    guardrail_name: str
    message: str = ""
    severity: str = "info"  # info, warning, error, critical
    blocked_content: Optional[str] = None
    suggested_alternative: Optional[str] = None


class GuardrailViolation(BaseModel):
    """A guardrail violation."""
    guardrail_name: str
    violation_type: str
    severity: str
    content: str
    reason: str
    timestamp: str = Field(default_factory=lambda: __import__("datetime").datetime.utcnow().isoformat())


# Content patterns to block (USP: minor-appropriate)
BLOCKED_PATTERNS = {
    "inappropriate_content": [
        r"\b(explicit|inappropriate|adult)\s+(content|material)\b",
        r"\b(drugs?|alcohol|smoking)\b.*\b(use|abuse|try)\b",
    ],
    "harmful_advice": [
        r"\b(lie|cheat|fake|fabricate)\b.*\b(application|essay|activity)\b",
        r"\b(pay.*for|buy)\b.*\b(recommendation|rec letter)\b",
        r"\b(plagiarize|copy|steal)\b.*\b(essay|writing)\b",
    ],
    "discriminatory": [
        r"\b(racist|sexist|homophobic|discriminatory)\b",
    ],
    "financial_exploitation": [
        r"\b(send.*money|wire.*transfer|gift\s*card)\b",
        r"\b(investment.*opportunity|get\s*rich)\b",
    ],
}

# Sensitive topics that need careful handling
SENSITIVE_TOPICS = [
    "mental health",
    "family problems",
    "financial hardship",
    "discrimination",
    "learning disabilities",
    "health conditions",
]

# Safe alternatives for blocked content
SAFE_ALTERNATIVES = {
    "lie": "honestly present",
    "cheat": "work hard",
    "fake": "authentically develop",
    "fabricate": "genuinely create",
}


class MinorSafetyGuardrail:
    """
    Safety guardrails specifically for minors.

    3P: Uses Guardrails AI patterns
    USP: Age-appropriate content for high school students

    Why this matters:
    - Students are minors (13-18)
    - Content must be appropriate
    - No exploitation or harm
    - Honest, ethical guidance only
    """

    def __init__(
        self,
        blocked_patterns: Optional[Dict[str, List[str]]] = None,
        sensitive_topics: Optional[List[str]] = None,
    ):
        """
        Initialize guardrails.

        Args:
            blocked_patterns: Custom patterns to block
            sensitive_topics: Topics requiring careful handling
        """
        self.blocked_patterns = blocked_patterns or BLOCKED_PATTERNS
        self.sensitive_topics = sensitive_topics or SENSITIVE_TOPICS
        self._compiled_patterns: Dict[str, List[re.Pattern]] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for efficiency."""
        for category, patterns in self.blocked_patterns.items():
            self._compiled_patterns[category] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def check_input(self, content: str) -> GuardrailResult:
        """
        Check student input for issues.

        Args:
            content: Student's message

        Returns:
            GuardrailResult indicating pass/fail
        """
        # Check for blocked patterns
        for category, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(content)
                if match:
                    return GuardrailResult(
                        passed=False,
                        guardrail_type=GuardrailType.INPUT,
                        guardrail_name="blocked_content",
                        message=f"Input contains blocked content: {category}",
                        severity="warning",
                        blocked_content=match.group(),
                    )

        # Check for sensitive topics (don't block, just flag)
        for topic in self.sensitive_topics:
            if topic.lower() in content.lower():
                logger.info(f"Sensitive topic detected: {topic}")
                # Don't block, just note it

        return GuardrailResult(
            passed=True,
            guardrail_type=GuardrailType.INPUT,
            guardrail_name="input_check",
            message="Input passed all guardrails",
        )

    def check_output(self, content: str) -> GuardrailResult:
        """
        Check agent output before sending to student.

        Args:
            content: Agent's response

        Returns:
            GuardrailResult indicating pass/fail
        """
        # Check for harmful advice
        harmful_patterns = self._compiled_patterns.get("harmful_advice", [])
        for pattern in harmful_patterns:
            match = pattern.search(content)
            if match:
                return GuardrailResult(
                    passed=False,
                    guardrail_type=GuardrailType.OUTPUT,
                    guardrail_name="harmful_advice",
                    message="Output contains potentially harmful advice",
                    severity="error",
                    blocked_content=match.group(),
                    suggested_alternative=self._suggest_alternative(match.group()),
                )

        # Check for inappropriate content
        inappropriate = self._compiled_patterns.get("inappropriate_content", [])
        for pattern in inappropriate:
            match = pattern.search(content)
            if match:
                return GuardrailResult(
                    passed=False,
                    guardrail_type=GuardrailType.OUTPUT,
                    guardrail_name="inappropriate_content",
                    message="Output contains inappropriate content for minors",
                    severity="error",
                    blocked_content=match.group(),
                )

        # Check length (responses shouldn't be overwhelming)
        if len(content) > 5000:
            logger.warning("Response may be too long for student attention")

        return GuardrailResult(
            passed=True,
            guardrail_type=GuardrailType.OUTPUT,
            guardrail_name="output_check",
            message="Output passed all guardrails",
        )

    def _suggest_alternative(self, blocked: str) -> Optional[str]:
        """Suggest safe alternative for blocked content."""
        blocked_lower = blocked.lower()
        for bad, good in SAFE_ALTERNATIVES.items():
            if bad in blocked_lower:
                return f"Consider using '{good}' instead"
        return None


class OutputValidator:
    """
    Validates agent outputs against quality standards.

    3P: Guardrails AI validation patterns
    """

    def __init__(self):
        self.min_response_length = 50
        self.max_response_length = 5000
        self.required_elements: Dict[str, List[str]] = {
            "recommendation": ["reasoning", "action"],
            "assessment": ["analysis", "conclusion"],
            "gameplan": ["priorities", "timeline"],
        }

    def validate(
        self,
        content: str,
        output_type: str = "general",
    ) -> GuardrailResult:
        """
        Validate agent output.

        Args:
            content: Agent's response
            output_type: Type of output (recommendation, assessment, etc.)

        Returns:
            GuardrailResult
        """
        # Length check
        if len(content) < self.min_response_length:
            return GuardrailResult(
                passed=False,
                guardrail_type=GuardrailType.OUTPUT,
                guardrail_name="min_length",
                message="Response too short to be helpful",
                severity="warning",
            )

        if len(content) > self.max_response_length:
            return GuardrailResult(
                passed=False,
                guardrail_type=GuardrailType.OUTPUT,
                guardrail_name="max_length",
                message="Response too long, may overwhelm student",
                severity="warning",
            )

        # Required elements check
        required = self.required_elements.get(output_type, [])
        content_lower = content.lower()
        missing = [elem for elem in required if elem not in content_lower]

        if missing:
            return GuardrailResult(
                passed=False,
                guardrail_type=GuardrailType.OUTPUT,
                guardrail_name="required_elements",
                message=f"Response missing required elements: {missing}",
                severity="warning",
            )

        return GuardrailResult(
            passed=True,
            guardrail_type=GuardrailType.OUTPUT,
            guardrail_name="output_validation",
            message="Output validated successfully",
        )


class GuardrailsManager:
    """
    Central manager for all guardrails.

    Combines multiple guardrail types into single check.
    """

    def __init__(self):
        self.safety_guardrail = MinorSafetyGuardrail()
        self.output_validator = OutputValidator()
        self._violations: List[GuardrailViolation] = []

    def check_input(self, content: str) -> GuardrailResult:
        """Check input against all guardrails."""
        return self.safety_guardrail.check_input(content)

    def check_output(
        self,
        content: str,
        output_type: str = "general",
    ) -> List[GuardrailResult]:
        """
        Check output against all guardrails.

        Returns list of results (can have multiple issues).
        """
        results = []

        # Safety check
        safety_result = self.safety_guardrail.check_output(content)
        results.append(safety_result)
        if not safety_result.passed:
            self._record_violation(safety_result)

        # Validation check
        validation_result = self.output_validator.validate(content, output_type)
        results.append(validation_result)
        if not validation_result.passed:
            self._record_violation(validation_result)

        return results

    def all_passed(self, results: List[GuardrailResult]) -> bool:
        """Check if all guardrails passed."""
        return all(r.passed for r in results)

    def _record_violation(self, result: GuardrailResult) -> None:
        """Record a guardrail violation."""
        self._violations.append(GuardrailViolation(
            guardrail_name=result.guardrail_name,
            violation_type=result.guardrail_type.value,
            severity=result.severity,
            content=result.blocked_content or "",
            reason=result.message,
        ))

    def get_violations(self) -> List[GuardrailViolation]:
        """Get all recorded violations."""
        return self._violations

    def clear_violations(self) -> None:
        """Clear recorded violations."""
        self._violations.clear()


# Convenience functions
def check_content_safety(content: str) -> GuardrailResult:
    """Quick safety check for content."""
    guardrail = MinorSafetyGuardrail()
    return guardrail.check_output(content)


def validate_agent_output(
    content: str,
    output_type: str = "general",
) -> bool:
    """
    Quick validation of agent output.

    Returns True if output passes all guardrails.
    """
    manager = GuardrailsManager()
    results = manager.check_output(content, output_type)
    return manager.all_passed(results)
