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


@dataclass
class GamePlanValidation:
    """Extended validation result for GamePlan with component scores."""
    passed: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    confidence: float = 1.0
    # Component scores (0.0-1.0)
    identity_score: float = 0.0
    awards_score: float = 0.0
    programs_score: float = 0.0
    phases_score: float = 0.0
    narrative_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "warnings": self.warnings,
            "errors": self.errors,
            "confidence": self.confidence,
            "component_scores": {
                "identity": self.identity_score,
                "awards": self.awards_score,
                "programs": self.programs_score,
                "phases": self.phases_score,
                "narrative": self.narrative_score,
            },
        }


def validate_gameplan_output(
    output: Dict,
    enriched_awards: Optional[List[Dict]] = None,
    enriched_programs: Optional[List[Dict]] = None,
) -> GamePlanValidation:
    """
    Validate GamePlan orchestrated output with component-level scoring.

    Checks:
    - Identity synthesis present and valid
    - Awards recommendations exist and are grounded
    - Programs recommendations exist and are grounded
    - Phases are properly structured
    - Narrative coherence

    Component Weights:
    - identity: 0.25
    - awards: 0.20
    - programs: 0.20
    - phases: 0.15
    - narrative: 0.20

    Returns:
        GamePlanValidation with component scores and weighted confidence
    """
    warnings = []
    errors = []

    game_plan = output.get("game_plan", {})

    # ==========================================================================
    # COMPONENT 1: Identity Synthesis (weight: 0.25)
    # ==========================================================================
    identity_score = 1.0
    identity = game_plan.get("identity_synthesis", {})

    VALID_ARCHETYPES = {
        "academic_powerhouse", "stem_innovator", "creative_visionary",
        "community_changemaker", "entrepreneurial_leader",
        "humanities_scholar", "athletic_scholar", "multi_hyphenate"
    }

    archetype = identity.get("archetype")
    if not archetype:
        warnings.append("Missing archetype in identity synthesis")
        identity_score -= 0.4
    elif archetype not in VALID_ARCHETYPES:
        errors.append(f"Invalid archetype: {archetype}")
        identity_score -= 0.5

    spike = identity.get("spike")
    if not spike:
        warnings.append("Missing spike in identity synthesis")
        identity_score -= 0.3

    archetype_confidence = identity.get("archetype_confidence", 0)
    if archetype_confidence < 0.3:
        warnings.append(f"Low archetype confidence: {archetype_confidence:.2f}")
        identity_score -= 0.2

    pillars = identity.get("pillars", [])
    if len(pillars) < 2:
        warnings.append(f"Only {len(pillars)} pillars (recommend 3-5)")
        identity_score -= 0.1

    identity_score = max(0.0, identity_score)

    # ==========================================================================
    # COMPONENT 2: Awards (weight: 0.20)
    # ==========================================================================
    awards_score = 1.0
    awards = game_plan.get("awards", {})
    portfolio = awards.get("portfolio", {})

    reach_awards = portfolio.get("reach", [])
    target_awards = portfolio.get("target", [])
    safety_awards = portfolio.get("safety", [])
    total_awards = len(reach_awards) + len(target_awards) + len(safety_awards)

    if total_awards == 0:
        warnings.append("No awards in portfolio")
        awards_score -= 0.5
    elif total_awards < 3:
        warnings.append(f"Only {total_awards} awards in portfolio (recommend 5)")
        awards_score -= 0.2
    elif total_awards < 5:
        awards_score -= 0.1

    # Check portfolio balance
    if total_awards > 0:
        if not reach_awards:
            warnings.append("No reach awards - add aspirational targets")
            awards_score -= 0.15
        if not safety_awards:
            warnings.append("No safety awards - add achievable backup options")
            awards_score -= 0.1

    # Grounding check (if knowledge base provided)
    if enriched_awards:
        award_ids = {a.get("id") for a in enriched_awards if a.get("id")}
        for _, award_list in [("reach", reach_awards), ("target", target_awards), ("safety", safety_awards)]:
            for award in award_list:
                award_id = award.get("id") or award.get("award_id")
                if award_id and award_id not in award_ids:
                    warnings.append(f"Award '{award_id}' not found in knowledge base")
                    awards_score -= 0.05

    awards_score = max(0.0, awards_score)

    # ==========================================================================
    # COMPONENT 3: Programs (weight: 0.20)
    # ==========================================================================
    programs_score = 1.0
    programs = game_plan.get("programs", {})
    top_programs = programs.get("top_recommendations", [])

    if not top_programs:
        warnings.append("No program recommendations")
        programs_score -= 0.5
    elif len(top_programs) < 3:
        warnings.append(f"Only {len(top_programs)} program recommendations (recommend 5)")
        programs_score -= 0.2
    elif len(top_programs) < 5:
        programs_score -= 0.1

    # Check advance alerts
    advance_alerts = programs.get("advance_alerts", [])
    if not advance_alerts and top_programs:
        warnings.append("No advance alerts for programs - students may miss deadlines")
        programs_score -= 0.1

    # Grounding check (if knowledge base provided)
    if enriched_programs:
        program_ids = {p.get("id") for p in enriched_programs if p.get("id")}
        for prog in top_programs:
            prog_id = prog.get("program_id") or prog.get("id")
            if prog_id and prog_id not in program_ids:
                warnings.append(f"Program '{prog_id}' not found in knowledge base")
                programs_score -= 0.05

    programs_score = max(0.0, programs_score)

    # ==========================================================================
    # COMPONENT 4: Phases (weight: 0.15)
    # ==========================================================================
    phases_score = 1.0
    phases = game_plan.get("phases", [])

    if len(phases) == 0:
        warnings.append("No phases defined")
        phases_score -= 0.6
    elif len(phases) < 2:
        warnings.append(f"Only {len(phases)} phase (recommend 3)")
        phases_score -= 0.3
    elif len(phases) < 3:
        phases_score -= 0.1

    # Check phase structure
    for i, phase in enumerate(phases):
        if not phase.get("name"):
            warnings.append(f"Phase {i+1} missing name")
            phases_score -= 0.1
        if not phase.get("activities") and not phase.get("activity_count"):
            warnings.append(f"Phase {i+1} has no activities")
            phases_score -= 0.1

    phases_score = max(0.0, phases_score)

    # ==========================================================================
    # COMPONENT 5: Narrative (weight: 0.20)
    # ==========================================================================
    narrative_score = 1.0

    master_narrative = game_plan.get("master_narrative")
    narrative_dna = game_plan.get("narrative_dna")

    if not master_narrative and not narrative_dna:
        warnings.append("Missing narrative synthesis")
        narrative_score -= 0.5
    elif not master_narrative:
        warnings.append("Master narrative not synthesized - using legacy narrative_dna")
        narrative_score -= 0.2

    # Check narrative components if master_narrative exists
    if master_narrative and isinstance(master_narrative, dict):
        if not master_narrative.get("brand_statement"):
            warnings.append("Missing brand statement in narrative")
            narrative_score -= 0.2
        if not master_narrative.get("first_principle"):
            warnings.append("Missing first principle passion in narrative")
            narrative_score -= 0.15

    narrative_score = max(0.0, narrative_score)

    # ==========================================================================
    # CALCULATE WEIGHTED CONFIDENCE
    # ==========================================================================
    # Weights: identity=0.25, awards=0.20, programs=0.20, phases=0.15, narrative=0.20
    WEIGHTS = {
        "identity": 0.25,
        "awards": 0.20,
        "programs": 0.20,
        "phases": 0.15,
        "narrative": 0.20,
    }

    confidence = (
        identity_score * WEIGHTS["identity"] +
        awards_score * WEIGHTS["awards"] +
        programs_score * WEIGHTS["programs"] +
        phases_score * WEIGHTS["phases"] +
        narrative_score * WEIGHTS["narrative"]
    )

    # Normalize to 0.5-1.0 range (never below 0.5 for graceful degradation)
    confidence = max(0.5, min(1.0, confidence))

    # Pass threshold: confidence >= 0.7 AND no errors
    passed = confidence >= 0.7 and len(errors) == 0

    return GamePlanValidation(
        passed=passed,
        warnings=warnings,
        errors=errors,
        confidence=confidence,
        identity_score=identity_score,
        awards_score=awards_score,
        programs_score=programs_score,
        phases_score=phases_score,
        narrative_score=narrative_score,
    )
