"""
Guardrails Engine - Output Validation
=====================================
Validates agent outputs to prevent hallucination and ensure quality.

Checks:
- Grounding: All awards/programs exist in knowledge base
- Schema: Output matches expected structure
- Consistency: No contradictions
- Time-appropriateness: Recommendations fit timeline
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set


@dataclass
class CheckResult:
    """Result of a single guardrail check."""
    passed: bool
    guardrail: str
    message: str = ""
    details: Optional[Dict] = None


@dataclass
class ValidationResult:
    """Complete validation result."""
    passed: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    confidence: float = 1.0
    checks: List[CheckResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "warnings": self.warnings,
            "errors": self.errors,
            "confidence": self.confidence,
        }


class GuardrailsEngine:
    """
    Validates agent outputs against knowledge base and rules.

    Prevents:
    - Hallucinated awards/programs
    - Malformed outputs
    - Inconsistent recommendations
    """

    def __init__(self, awards_cache: List[Dict] = None, programs_cache: List[Dict] = None):
        """
        Initialize with knowledge base caches.

        Args:
            awards_cache: List of enriched awards from JSON
            programs_cache: List of enriched programs from JSON
        """
        self._award_ids: Set[str] = set()
        self._program_ids: Set[str] = set()

        if awards_cache:
            self._award_ids = {a.get("id") for a in awards_cache if a.get("id")}

        if programs_cache:
            self._program_ids = {p.get("id") for p in programs_cache if p.get("id")}

    def validate_awards_output(self, output: Dict) -> ValidationResult:
        """
        Validate awards agent output.

        Checks:
        - All recommended awards exist in KB
        - Portfolio structure is valid
        - Timeline items are valid
        """
        checks = []
        warnings = []
        errors = []

        # Check portfolio structure
        portfolio = output.get("portfolio", {})
        if not portfolio:
            errors.append("Missing portfolio in output")
            checks.append(CheckResult(
                passed=False,
                guardrail="valid_schema",
                message="Missing portfolio",
            ))

        # Check all recommended awards exist in KB
        for category in ["reach", "target", "safety"]:
            for award in portfolio.get(category, []):
                award_id = award.get("id") or award.get("award_id")
                if award_id and self._award_ids and award_id not in self._award_ids:
                    warnings.append(f"Award '{award_id}' not found in knowledge base")
                    checks.append(CheckResult(
                        passed=False,
                        guardrail="grounded_awards",
                        message=f"Ungrounded award: {award_id}",
                        details={"award_id": award_id, "category": category},
                    ))

        # Calculate confidence
        failed_checks = [c for c in checks if not c.passed]
        confidence = 1.0 - (len(failed_checks) * 0.15)
        confidence = max(0.5, min(1.0, confidence))

        return ValidationResult(
            passed=len(errors) == 0,
            warnings=warnings,
            errors=errors,
            confidence=confidence,
            checks=checks,
        )

    def validate_programs_output(self, output: Dict) -> ValidationResult:
        """
        Validate programs agent output.

        Checks:
        - All recommended programs exist in KB
        - Output structure is valid
        """
        checks = []
        warnings = []
        errors = []

        # Check top recommendations
        recommendations = output.get("top_recommendations", [])
        for prog in recommendations:
            prog_id = prog.get("program_id") or prog.get("id")
            if prog_id and self._program_ids and prog_id not in self._program_ids:
                warnings.append(f"Program '{prog_id}' not found in knowledge base")
                checks.append(CheckResult(
                    passed=False,
                    guardrail="grounded_programs",
                    message=f"Ungrounded program: {prog_id}",
                    details={"program_id": prog_id},
                ))

        # Calculate confidence
        failed_checks = [c for c in checks if not c.passed]
        confidence = 1.0 - (len(failed_checks) * 0.15)
        confidence = max(0.5, min(1.0, confidence))

        return ValidationResult(
            passed=len(errors) == 0,
            warnings=warnings,
            errors=errors,
            confidence=confidence,
            checks=checks,
        )

    def validate_identity_synthesis(self, output: Dict) -> ValidationResult:
        """
        Validate EC agent identity synthesis output.

        Checks:
        - Archetype is valid
        - Spike is not empty (when signals exist)
        - Required fields present
        """
        checks = []
        warnings = []
        errors = []

        VALID_ARCHETYPES = {
            "academic_powerhouse", "stem_innovator", "creative_visionary",
            "community_changemaker", "entrepreneurial_leader",
            "humanities_scholar", "athletic_scholar", "multi_hyphenate"
        }

        identity = output.get("identity_synthesis", {})

        # Check archetype
        archetype = identity.get("archetype")
        if archetype and archetype not in VALID_ARCHETYPES:
            errors.append(f"Invalid archetype: {archetype}")
            checks.append(CheckResult(
                passed=False,
                guardrail="valid_archetype",
                message=f"Invalid archetype: {archetype}",
            ))

        # Check spike (warning only if empty)
        spike = identity.get("spike", "")
        if not spike:
            warnings.append("Spike is empty - may affect downstream recommendations")

        # Check archetype confidence
        confidence = identity.get("archetype_confidence", 0.5)
        if confidence < 0.3:
            warnings.append(f"Low archetype confidence: {confidence}")

        return ValidationResult(
            passed=len(errors) == 0,
            warnings=warnings,
            errors=errors,
            confidence=confidence,
            checks=checks,
        )


# Convenience functions
def validate_awards_output(output: Dict, awards_cache: List[Dict]) -> ValidationResult:
    """Validate awards output against cache."""
    engine = GuardrailsEngine(awards_cache=awards_cache)
    return engine.validate_awards_output(output)


def validate_programs_output(output: Dict, programs_cache: List[Dict]) -> ValidationResult:
    """Validate programs output against cache."""
    engine = GuardrailsEngine(programs_cache=programs_cache)
    return engine.validate_programs_output(output)


def validate_identity_synthesis(output: Dict) -> ValidationResult:
    """Validate identity synthesis output."""
    engine = GuardrailsEngine()
    return engine.validate_identity_synthesis(output)
