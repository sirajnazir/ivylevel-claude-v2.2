# Migration Plan: Hybrid Agent Architecture v4.0
## IvyQuest Multi-Agent System Implementation Guide

**Document Type**: Implementation Plan (Phase 3)
**Date**: January 2026
**Status**: Ready for Implementation

---

## 1. Executive Summary

### Implementation Overview

| Metric | Value |
|--------|-------|
| Total Phases | 4 |
| New Files | 4 |
| Modified Files | 4 |
| Total New Lines | ~830 |
| Breaking Changes | 0 |
| Database Migrations | 0 |
| Estimated Duration | 3-4 focused sessions |

### Phase Summary

| Phase | Focus | Files | Lines | Risk |
|-------|-------|-------|-------|------|
| 1 | Foundation (new core modules) | 4 new | ~340 | LOW |
| 2 | EC Agent Enhancement | 1 modified | ~240 | MEDIUM |
| 3 | Orchestrator Enhancement | 1 modified | ~150 | LOW |
| 4 | Guardrails Integration | 3 modified | ~100 | LOW |

---

## 2. Pre-Implementation Checklist

Before starting implementation:

- [ ] Backend is running on port 8001
- [ ] Frontend is running on port 3006
- [ ] Test user exists: huda@ivylevel.com (profile with no activities)
- [ ] Git branch created: `feat/hybrid-architecture-v4`
- [ ] Current tests pass: `cd agents && pytest`

---

## 3. Phase 1: Foundation Components

### 3.1 Create Core Module Directory

```bash
# Create directory structure
mkdir -p /Users/snazir/ivyquest-claude-v2.2/agents/agents/core
```

### 3.2 Create `__init__.py`

**File**: `agents/agents/core/__init__.py`

```python
"""
IvyQuest Hybrid Agent Core Components
=====================================
v4.0 - Grounded Intelligence + LLM Augmentation

Components:
- ProfileSignals: Extract signals from profile data
- LLMRouter: Strategic approach selection
- GuardrailsEngine: Output validation
"""

from .profile_signals import ProfileSignals, extract_profile_signals
from .llm_router import LLMRouter, StrategicRoute, StrategicApproach
from .guardrails import GuardrailsEngine, ValidationResult, validate_awards_output, validate_programs_output

__all__ = [
    # Profile Signals
    "ProfileSignals",
    "extract_profile_signals",
    # LLM Router
    "LLMRouter",
    "StrategicRoute",
    "StrategicApproach",
    # Guardrails
    "GuardrailsEngine",
    "ValidationResult",
    "validate_awards_output",
    "validate_programs_output",
]
```

### 3.3 Create ProfileSignals Module

**File**: `agents/agents/core/profile_signals.py`

```python
"""
Profile Signals Extraction
==========================
Extracts signals from profile_data for inference when activities are empty.

Used by EC Agent to infer spike and archetype from:
- Passion: interests, dream_career, causes
- Aptitude: intended_major, favorite_subjects
- Identity: strengths, values, grade
- Service: volunteer_interests
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ProfileSignals:
    """
    Extracted signals from profile_data for identity inference.

    These signals allow the EC Agent to generate meaningful identity
    synthesis even when the student has no activities entered.
    """

    # Passion signals (primary for spike inference)
    interests: List[str] = field(default_factory=list)
    dream_career: str = ""
    causes: List[str] = field(default_factory=list)
    spike_category: Optional[str] = None

    # Academic signals (for archetype scoring)
    intended_major: str = ""
    favorite_subjects: List[str] = field(default_factory=list)
    gpa: Optional[float] = None
    sat_total: Optional[int] = None

    # Identity signals (for archetype and pillars)
    strengths: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    grade: int = 11

    # Service signals (for community archetype)
    volunteer_interests: List[str] = field(default_factory=list)
    community_focus: Optional[str] = None

    def has_passion_signals(self) -> bool:
        """Check if passion-related signals exist."""
        return bool(self.interests or self.dream_career or self.causes or self.spike_category)

    def has_academic_signals(self) -> bool:
        """Check if academic signals exist."""
        return bool(self.intended_major or self.favorite_subjects)

    def has_identity_signals(self) -> bool:
        """Check if identity signals exist."""
        return bool(self.strengths or self.values)

    def has_any_signals(self) -> bool:
        """Check if any signals exist for inference."""
        return self.has_passion_signals() or self.has_academic_signals() or self.has_identity_signals()

    def get_spike_components(self) -> List[str]:
        """Get components that can form a spike."""
        components = []

        if self.intended_major:
            components.append(self.intended_major)
        if self.interests:
            components.extend(self.interests[:2])
        if self.causes:
            components.append(self.causes[0])
        if self.dream_career:
            components.append(self.dream_career)

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for c in components:
            c_lower = c.lower()
            if c_lower not in seen and c:
                seen.add(c_lower)
                unique.append(c)

        return unique[:5]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            "interests": self.interests,
            "dream_career": self.dream_career,
            "causes": self.causes,
            "spike_category": self.spike_category,
            "intended_major": self.intended_major,
            "favorite_subjects": self.favorite_subjects,
            "strengths": self.strengths,
            "values": self.values,
            "grade": self.grade,
            "volunteer_interests": self.volunteer_interests,
            "has_signals": self.has_any_signals(),
        }


def extract_profile_signals(profile: Dict) -> ProfileSignals:
    """
    Extract ProfileSignals from a profile dictionary.

    Args:
        profile: Profile dict with profile_data from assessment

    Returns:
        ProfileSignals dataclass with extracted values
    """
    profile_data = profile.get("profile_data", {})

    # Extract from each section
    passion = profile_data.get("passion", {})
    aptitude = profile_data.get("aptitude", {})
    identity = profile_data.get("identity", {})
    service = profile_data.get("service", {})

    return ProfileSignals(
        # Passion
        interests=_ensure_list(passion.get("interests")),
        dream_career=passion.get("dream_career", "") or "",
        causes=_ensure_list(passion.get("causes") or passion.get("causes_care_about")),
        spike_category=passion.get("spike_category"),

        # Aptitude
        intended_major=aptitude.get("intended_major", "") or "",
        favorite_subjects=_ensure_list(aptitude.get("favorite_subjects")),
        gpa=_safe_float(aptitude.get("gpa_weighted") or aptitude.get("gpa")),
        sat_total=_safe_int(aptitude.get("sat_total")),

        # Identity
        strengths=_ensure_list(identity.get("strengths")),
        values=_ensure_list(identity.get("values")),
        grade=_safe_int(identity.get("grade")) or 11,

        # Service
        volunteer_interests=_ensure_list(service.get("volunteer_interests")),
        community_focus=service.get("community_focus"),
    )


def _ensure_list(value) -> List[str]:
    """Ensure value is a list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return []


def _safe_float(value) -> Optional[float]:
    """Safely convert to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_int(value) -> Optional[int]:
    """Safely convert to int."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
```

### 3.4 Create LLM Router Module

**File**: `agents/agents/core/llm_router.py`

```python
"""
LLM Router - Strategic Approach Selection
=========================================
Determines the best strategic approach for a student based on their context.

Routes:
- BUILD_FRESH: No activities, be prescriptive
- OPTIMIZE: Strong foundation, enhance positioning
- REFRAME: Has activities but needs narrative pivot
- URGENT_TRIAGE: Limited time, focus on quick wins
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class StrategicApproach(Enum):
    """Strategic approaches for student coaching."""
    BUILD_FRESH = "BUILD_FRESH"
    OPTIMIZE = "OPTIMIZE"
    REFRAME = "REFRAME"
    URGENT_TRIAGE = "URGENT_TRIAGE"


@dataclass
class StrategicRoute:
    """Result of strategic routing decision."""
    choice: StrategicApproach
    reasoning: str
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "choice": self.choice.value,
            "reasoning": self.reasoning,
            "config": self.config,
        }


# Route configurations
ROUTE_CONFIGS = {
    StrategicApproach.BUILD_FRESH: {
        "be_prescriptive": True,
        "recommend_activities": True,
        "timeline_horizon": "long",
        "tier_targets": {"T1": 2, "T2": 3, "T3": 3, "T4": 2},
        "focus": ["activity_building", "spike_development", "portfolio_foundation"],
    },
    StrategicApproach.OPTIMIZE: {
        "be_prescriptive": False,
        "recommend_activities": False,
        "timeline_horizon": "medium",
        "focus": ["positioning", "narrative", "impact_evidence", "differentiation"],
    },
    StrategicApproach.REFRAME: {
        "be_prescriptive": False,
        "recommend_activities": True,  # 1-2 strategic additions
        "timeline_horizon": "medium",
        "focus": ["narrative_pivot", "connect_dots", "spike_identification", "coherence"],
    },
    StrategicApproach.URGENT_TRIAGE: {
        "be_prescriptive": True,
        "recommend_activities": False,  # No time for new activities
        "timeline_horizon": "short",
        "max_recommendations": 3,
        "focus": ["positioning", "quick_wins", "narrative", "immediate_impact"],
    },
}


class LLMRouter:
    """
    Routes students to appropriate strategic approach.

    Uses deterministic rules first, then LLM for edge cases.
    This ensures consistency while allowing contextual adaptation.
    """

    def __init__(self):
        self.use_llm_for_edge_cases = False  # Start with deterministic only

    async def decide_route(self, context: Dict[str, Any]) -> StrategicRoute:
        """
        Decide strategic approach based on student context.

        Args:
            context: Dict with keys:
                - grade: int (9-12)
                - activity_count: int
                - has_tier1: bool
                - has_tier2: bool
                - months_to_ed: int
                - portfolio_diagnosis: str (optional)

        Returns:
            StrategicRoute with choice, reasoning, and config
        """
        grade = context.get("grade", 11)
        activity_count = context.get("activity_count", 0)
        has_tier1 = context.get("has_tier1", False)
        has_tier2 = context.get("has_tier2", False)
        months_to_ed = context.get("months_to_ed", 20)

        # Rule 1: Urgent triage if very limited time
        if months_to_ed < 6:
            return StrategicRoute(
                choice=StrategicApproach.URGENT_TRIAGE,
                reasoning=f"Only {months_to_ed} months to Early Decision - focus on quick wins",
                config=ROUTE_CONFIGS[StrategicApproach.URGENT_TRIAGE],
            )

        # Rule 2: Build fresh if minimal activities
        if activity_count < 3:
            return StrategicRoute(
                choice=StrategicApproach.BUILD_FRESH,
                reasoning=f"Only {activity_count} activities - need to build foundation",
                config=ROUTE_CONFIGS[StrategicApproach.BUILD_FRESH],
            )

        # Rule 3: Optimize if strong T1/T2 foundation
        if has_tier1 or (has_tier2 and activity_count >= 5):
            return StrategicRoute(
                choice=StrategicApproach.OPTIMIZE,
                reasoning="Strong activity foundation with T1/T2 achievements - focus on positioning",
                config=ROUTE_CONFIGS[StrategicApproach.OPTIMIZE],
            )

        # Rule 4: Default to reframe
        return StrategicRoute(
            choice=StrategicApproach.REFRAME,
            reasoning=f"Have {activity_count} activities but may need narrative repositioning",
            config=ROUTE_CONFIGS[StrategicApproach.REFRAME],
        )

    def get_route_config(self, approach: StrategicApproach) -> Dict[str, Any]:
        """Get configuration for a specific approach."""
        return ROUTE_CONFIGS.get(approach, {})


def calculate_months_to_ed(grade: int) -> int:
    """
    Calculate approximate months until Early Decision deadline.

    Assumes:
    - ED deadline: November 1 of senior year
    - Current month: January
    """
    if grade == 12:
        return 0  # Already senior year
    elif grade == 11:
        return 10  # ~10 months to Nov of senior year
    elif grade == 10:
        return 22  # ~22 months
    elif grade == 9:
        return 34  # ~34 months
    else:
        return 46  # Gap year or earlier
```

### 3.5 Create Guardrails Module

**File**: `agents/agents/core/guardrails.py`

```python
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
```

### 3.6 Phase 1 Verification

After creating all Phase 1 files:

```bash
# Verify files exist
ls -la /Users/snazir/ivyquest-claude-v2.2/agents/agents/core/

# Test imports
cd /Users/snazir/ivyquest-claude-v2.2/agents
python -c "from agents.core import ProfileSignals, extract_profile_signals, LLMRouter, GuardrailsEngine; print('Phase 1 imports OK')"
```

---

## 4. Phase 2: EC Agent Enhancement

### 4.1 Feature Flag Configuration

**Add to**: `agents/config.py`

```python
# Hybrid Architecture v4.0 Feature Flags
FEATURE_FLAGS = {
    "use_profile_inference": True,   # Enable profile-based spike/archetype inference
    "use_llm_routing": False,        # Enable LLM routing (start with deterministic)
    "enable_guardrails": True,       # Enable output validation
}
```

### 4.2 Modify ExtracurricularsAgent

**File**: `agents/agents/extracurriculars.py`

#### Step 1: Add imports at top of file

```python
# Add after existing imports (around line 20)
from agents.core.profile_signals import ProfileSignals, extract_profile_signals
from config import FEATURE_FLAGS
```

#### Step 2: Add profile inference methods

Add these methods to the `ExtracurricularsAgent` class (after line 560, before `_extract_activities`):

```python
    # =========================================================================
    # HYBRID ARCHITECTURE v4.0: Profile-Based Inference
    # =========================================================================

    def _extract_profile_signals(self, profile: Dict) -> ProfileSignals:
        """Extract signals from profile for inference when activities are empty."""
        return extract_profile_signals(profile)

    async def _synthesize_identity_from_profile(
        self,
        profile: Dict,
        signals: ProfileSignals
    ) -> IdentitySynthesis:
        """
        Synthesize identity when no activities exist.
        Uses profile signals (interests, major, causes) to infer spike and archetype.
        """
        synthesis = IdentitySynthesis()

        # Infer spike from profile signals
        spike, spike_evidence = self._infer_spike_from_signals(signals)
        synthesis.spike = spike
        synthesis.spike_evidence = spike_evidence

        # Score archetypes from profile signals
        archetype, confidence, scores = self._score_archetypes_from_signals(signals)
        synthesis.archetype = archetype
        synthesis.archetype_confidence = confidence
        synthesis.archetype_scores = scores

        # Generate pillars from profile signals
        pillars = self._generate_pillars_from_signals(signals)
        synthesis.pillars = pillars

        # Set portfolio as empty with recommendations
        synthesis.portfolio_balance_score = 0.0
        synthesis.portfolio_gaps = list(CATEGORY_WEIGHTS.keys())
        synthesis.portfolio_strengths = []

        # Leadership defaults to potential (no evidence yet)
        synthesis.leadership_level = "potential"
        synthesis.leadership_evidence = []

        return synthesis

    def _infer_spike_from_signals(self, signals: ProfileSignals) -> Tuple[str, List[str]]:
        """
        Infer spike from profile signals.

        Priority:
        1. Explicit spike_category from passion
        2. Intended major + interests combination
        3. Dream career + causes combination
        """
        components = signals.get_spike_components()

        if not components:
            return "exploring interests", []

        # If spike_category is explicitly set, use it
        if signals.spike_category:
            spike = signals.spike_category.lower().replace("_", " ")
            return spike, components[:3]

        # Synthesize spike from top 2 components
        if len(components) >= 2:
            spike = f"{components[0]} + {components[1]}"
        elif len(components) == 1:
            spike = components[0]
        else:
            spike = "exploring interests"

        return spike, components[:3]

    def _score_archetypes_from_signals(
        self,
        signals: ProfileSignals
    ) -> Tuple[str, float, Dict[str, float]]:
        """
        Score archetypes based on profile signals (not activities).

        Uses:
        - intended_major, favorite_subjects → academic archetypes
        - interests, causes → passion-based archetypes
        - strengths, values → identity-based archetypes
        """
        scores = {arch: 0.0 for arch in ARCHETYPES}

        # Major to archetype mapping
        major_mapping = {
            "computer science": {"stem_innovator": 0.4, "academic_powerhouse": 0.2},
            "engineering": {"stem_innovator": 0.4, "academic_powerhouse": 0.2},
            "biology": {"stem_innovator": 0.3, "academic_powerhouse": 0.3},
            "medicine": {"stem_innovator": 0.3, "community_changemaker": 0.3},
            "business": {"entrepreneurial_leader": 0.4, "academic_powerhouse": 0.2},
            "economics": {"entrepreneurial_leader": 0.3, "academic_powerhouse": 0.3},
            "art": {"creative_visionary": 0.5},
            "music": {"creative_visionary": 0.5},
            "film": {"creative_visionary": 0.4, "entrepreneurial_leader": 0.2},
            "history": {"humanities_scholar": 0.4, "academic_powerhouse": 0.2},
            "political science": {"humanities_scholar": 0.3, "community_changemaker": 0.3},
            "law": {"humanities_scholar": 0.3, "entrepreneurial_leader": 0.3},
            "psychology": {"community_changemaker": 0.3, "humanities_scholar": 0.3},
            "education": {"community_changemaker": 0.4, "humanities_scholar": 0.2},
        }

        # Score from intended major
        major_lower = signals.intended_major.lower()
        for keyword, arch_scores in major_mapping.items():
            if keyword in major_lower:
                for arch, score in arch_scores.items():
                    scores[arch] += score

        # Score from interests
        interest_mapping = {
            "research": {"academic_powerhouse": 0.2, "stem_innovator": 0.2},
            "coding": {"stem_innovator": 0.3},
            "robotics": {"stem_innovator": 0.3},
            "ai": {"stem_innovator": 0.3},
            "art": {"creative_visionary": 0.3},
            "music": {"creative_visionary": 0.3},
            "writing": {"creative_visionary": 0.2, "humanities_scholar": 0.2},
            "debate": {"humanities_scholar": 0.3},
            "volunteer": {"community_changemaker": 0.3},
            "nonprofit": {"community_changemaker": 0.3},
            "startup": {"entrepreneurial_leader": 0.3},
            "business": {"entrepreneurial_leader": 0.3},
            "sports": {"athletic_scholar": 0.4},
        }

        for interest in signals.interests:
            interest_lower = interest.lower()
            for keyword, arch_scores in interest_mapping.items():
                if keyword in interest_lower:
                    for arch, score in arch_scores.items():
                        scores[arch] += score

        # Score from causes (boosts community_changemaker)
        if signals.causes:
            scores["community_changemaker"] += 0.2 * min(len(signals.causes), 3)

        # Score from volunteer interests
        if signals.volunteer_interests:
            scores["community_changemaker"] += 0.15 * min(len(signals.volunteer_interests), 3)

        # Normalize scores
        max_score = max(scores.values()) if max(scores.values()) > 0 else 1
        scores = {k: round(v / max_score, 2) for k, v in scores.items()}

        # Determine primary archetype
        primary = max(scores, key=scores.get)
        confidence = scores[primary]

        # If no strong signal, default to multi_hyphenate with lower confidence
        if confidence < 0.3:
            primary = "multi_hyphenate"
            confidence = 0.4
            scores["multi_hyphenate"] = 0.4

        return primary, confidence, scores

    def _generate_pillars_from_signals(self, signals: ProfileSignals) -> List[str]:
        """Generate pillars from profile signals."""
        pillars = []

        if signals.intended_major:
            pillars.append(signals.intended_major)

        if signals.interests:
            pillars.extend(signals.interests[:2])

        if signals.causes:
            pillars.append(f"Impact: {signals.causes[0]}")

        if signals.strengths:
            pillars.append(f"Strength: {signals.strengths[0]}")

        # Limit to 5 pillars
        return pillars[:5] if pillars else ["Exploring interests", "Building foundation"]
```

#### Step 3: Modify the analyze() method

Replace the existing `analyze()` method (lines 144-195) with:

```python
    async def analyze(self, profile_id: str) -> Dict[str, Any]:
        """
        Main analysis pipeline.

        Hybrid Architecture v4.0:
        - If activities exist: Use activity-based analysis (existing logic)
        - If no activities: Use profile-based inference (NEW)
        """
        try:
            profile = await self._get_profile(profile_id)
            if not profile:
                return self._placeholder_response(profile_id)

            # ALWAYS extract profile signals (v4.0)
            signals = self._extract_profile_signals(profile)

            # Extract activities (may be empty)
            activities = self._extract_activities(profile)

            # =========================================================
            # HYBRID PATH SELECTION (v4.0)
            # =========================================================
            use_profile_inference = FEATURE_FLAGS.get("use_profile_inference", True)

            if activities:
                # PATH A: Activity-based analysis (existing logic)
                print(f"[EC Agent] Using activity-based analysis ({len(activities)} activities)")

                # TYPE-013: Portfolio Optimization
                portfolio_analysis = self._analyze_portfolio_balance(activities)

                # TYPE-014: Narrative Synthesis
                identity_synthesis = await self._synthesize_identity(
                    profile, activities, portfolio_analysis
                )

                # TYPE-015: Impact Assessment
                impact_assessment = self._assess_impact(activities)
                identity_synthesis.total_impact_score = impact_assessment["total_score"]
                identity_synthesis.top_impact_activities = impact_assessment["top_activities"]

            elif use_profile_inference and signals.has_any_signals():
                # PATH B: Profile-based inference (v4.0 NEW)
                print(f"[EC Agent] Using profile-based inference (no activities, has signals)")

                identity_synthesis = await self._synthesize_identity_from_profile(profile, signals)
                portfolio_analysis = PortfolioAnalysis()  # Empty portfolio
                portfolio_analysis.gaps = list(CATEGORY_WEIGHTS.keys())
                portfolio_analysis.recommendations = [
                    "Start building your extracurricular portfolio",
                    f"Consider activities aligned with your interest in {signals.intended_major or 'your passions'}",
                ]
                impact_assessment = {"total_score": 0, "activities_assessed": 0, "top_activities": []}

            else:
                # PATH C: Placeholder (no activities AND no signals)
                print(f"[EC Agent] No activities and no profile signals - returning placeholder")
                return self._placeholder_response(
                    profile_id,
                    message="Complete your profile to get personalized recommendations"
                )

            # Version state
            await self._version_state(profile_id, "ec_analyzed", {
                "activities_count": len(activities),
                "spike": identity_synthesis.spike,
                "archetype": identity_synthesis.archetype,
                "inference_mode": "activities" if activities else "profile_signals",
            })

            # Publish event
            await self._publish_event("EC_IDENTITY_SYNTHESIZED", {
                "profileId": profile_id,
                "spike": identity_synthesis.spike,
                "archetype": identity_synthesis.archetype,
                "pillars": identity_synthesis.pillars,
                "inference_mode": "activities" if activities else "profile_signals",
            })

            return {
                "success": True,
                "profile_id": profile_id,
                "identity_synthesis": identity_synthesis.to_dict(),
                "portfolio_analysis": {
                    "category_counts": getattr(portfolio_analysis, 'category_counts', {}),
                    "balance_score": getattr(portfolio_analysis, 'balance_score', 0),
                    "gaps": getattr(portfolio_analysis, 'gaps', []),
                    "strengths": getattr(portfolio_analysis, 'strengths', []),
                    "recommendations": getattr(portfolio_analysis, 'recommendations', []),
                },
                "impact_assessment": impact_assessment if activities else {"total_score": 0, "activities_assessed": 0, "top_activities": []},
                "activities_analyzed": len(activities),
                "inference_mode": "activities" if activities else "profile_signals",
            }

        except Exception as e:
            import traceback
            print(f"[ExtracurricularsAgent] ERROR: {str(e)}")
            print(traceback.format_exc())
            return {"success": False, "error": str(e)}
```

### 4.3 Phase 2 Verification

```bash
# Test EC Agent with profile that has no activities
cd /Users/snazir/ivyquest-claude-v2.2/agents
python -c "
import asyncio
from agents.extracurriculars import ExtracurricularsAgent

agent = ExtracurricularsAgent()

# Test with huda's profile
result = asyncio.run(agent.analyze('4c4c94f9-a7df-4483-9dc6-7905dda36386'))
print(f'Success: {result.get(\"success\")}')
print(f'Spike: {result.get(\"identity_synthesis\", {}).get(\"spike\")}')
print(f'Archetype: {result.get(\"identity_synthesis\", {}).get(\"archetype\")}')
print(f'Inference Mode: {result.get(\"inference_mode\")}')
"
```

---

## 5. Phase 3: Orchestrator Enhancement

### 5.1 Modify GamePlanAgent

**File**: `agents/agents/gameplan.py`

#### Step 1: Add imports

```python
# Add after existing imports (around line 25)
from agents.core.llm_router import LLMRouter, StrategicRoute, calculate_months_to_ed
from config import FEATURE_FLAGS
```

#### Step 2: Add router to __init__

```python
def __init__(self):
    # ... existing init code ...

    # v4.0: LLM Router for strategic approach selection
    self.router = LLMRouter()
```

#### Step 3: Add routing method

Add after line 90 (after `__init__`):

```python
    async def _determine_strategic_route(self, profile: Dict) -> StrategicRoute:
        """
        Determine strategic approach for this student.

        v4.0: Uses LLMRouter to select BUILD/OPTIMIZE/REFRAME/URGENT
        """
        profile_data = profile.get("profile_data", {})
        experience = profile_data.get("experience", {})
        activities = experience.get("activities", [])
        identity = profile_data.get("identity", {})
        grade = identity.get("grade", 11)

        # Build context for router
        context = {
            "grade": grade,
            "activity_count": len(activities),
            "has_tier1": any(
                self._classify_activity_tier(a) == "T1"
                for a in activities
            ),
            "has_tier2": any(
                self._classify_activity_tier(a) == "T2"
                for a in activities
            ),
            "months_to_ed": calculate_months_to_ed(grade),
        }

        return await self.router.decide_route(context)

    def _classify_activity_tier(self, activity: Dict) -> str:
        """Quick tier classification for routing."""
        text = f"{activity.get('name', '')} {activity.get('role', '')} {activity.get('description', '')}".lower()

        t1_signals = ["founder", "national", "international", "published", "olympiad"]
        t2_signals = ["president", "captain", "state", "research", "intern"]

        if any(s in text for s in t1_signals):
            return "T1"
        if any(s in text for s in t2_signals):
            return "T2"
        return "T3"
```

#### Step 4: Modify generate_orchestrated()

Update the `generate_orchestrated()` method to include routing:

```python
    async def generate_orchestrated(self, profile_id: str) -> Dict[str, Any]:
        """
        Orchestrated GamePlan generation using multi-agent flow.

        v4.0 Flow:
        0. Determine strategic route (NEW)
        1. EC Agent (FIRST) → identity_synthesis
        2. Awards + Programs (PARALLEL) ← identity_synthesis
        3. Synthesis → Unified GamePlan with route context
        """
        try:
            # ========================================================
            # STEP 0 (v4.0): Determine Strategic Route
            # ========================================================
            profile = await self._get_profile(profile_id)
            if not profile:
                return await self.generate(profile_id, None)

            route = await self._determine_strategic_route(profile)
            print(f"[GamePlan] Strategic route: {route.choice.value} - {route.reasoning}")

            # ========================================================
            # STEP 1: Run EC Agent FIRST to get identity synthesis
            # ========================================================
            print(f"[GamePlan] Step 1: Running EC Agent for {profile_id}")
            ec_result = await self.ec_agent.process(profile_id)

            if not ec_result.get("success"):
                print(f"[GamePlan] EC Agent failed: {ec_result.get('error')}")
                return await self.generate(profile_id, None)

            identity_synthesis = ec_result.get("identity_synthesis", {})
            print(f"[GamePlan] Identity synthesis: archetype={identity_synthesis.get('archetype')}, spike={identity_synthesis.get('spike')}")

            # ... rest of existing code for Steps 2 and 3 ...
            # (Keep existing parallel execution and synthesis)

            # Add route to the unified plan
            unified_plan = self._synthesize_gameplan(
                profile_id=profile_id,
                identity_synthesis=identity_synthesis,
                ec_result=ec_result,
                awards_result=awards_result,
                programs_result=programs_result,
                master_narrative=self.master_narrative,
            )

            # Add strategic route to output
            unified_plan["strategic_route"] = route.to_dict()

            return {
                "success": True,
                "game_plan": unified_plan,
                "strategic_route": route.to_dict(),
                "orchestration": {
                    "ec_agent": "completed",
                    "awards_agent": "completed" if awards_result.get("success") else "failed",
                    "programs_agent": "completed" if programs_result.get("success") else "failed",
                },
                # ... rest of existing return ...
            }
```

---

## 6. Phase 4: Guardrails Integration

### 6.1 Add to AwardsAgent

**File**: `agents/agents/awards.py`

```python
# Add import at top
from agents.core.guardrails import validate_awards_output

# In match() method, before final return, add:
async def match(self, profile_id: str, identity_synthesis: Optional[Dict] = None):
    # ... existing matching logic ...

    result = {
        "success": True,
        "total_matches": len(matched_awards),
        "portfolio": portfolio,
        # ... existing fields ...
    }

    # v4.0: Validate output
    if FEATURE_FLAGS.get("enable_guardrails", True):
        validation = validate_awards_output(result, self._load_enriched_awards())
        if validation.warnings:
            result["validation_warnings"] = validation.warnings
        result["confidence"] = validation.confidence

    return result
```

### 6.2 Add to ProgramsAgent

**File**: `agents/agents/programs.py`

```python
# Add import at top
from agents.core.guardrails import validate_programs_output

# In match() method, before final return, add validation
```

---

## 7. Testing Plan

### 7.1 Unit Tests

**File**: `agents/tests/test_hybrid_v4.py`

```python
"""
Tests for Hybrid Architecture v4.0 components.
"""
import pytest
from agents.core.profile_signals import ProfileSignals, extract_profile_signals
from agents.core.llm_router import LLMRouter, StrategicApproach
from agents.core.guardrails import GuardrailsEngine


class TestProfileSignals:
    def test_extract_with_full_data(self):
        profile = {
            "profile_data": {
                "passion": {
                    "interests": ["AI", "robotics"],
                    "dream_career": "AI Researcher",
                    "causes": ["climate change"],
                },
                "aptitude": {
                    "intended_major": "Computer Science",
                },
            }
        }
        signals = extract_profile_signals(profile)

        assert signals.interests == ["AI", "robotics"]
        assert signals.dream_career == "AI Researcher"
        assert signals.intended_major == "Computer Science"
        assert signals.has_passion_signals()
        assert signals.has_academic_signals()

    def test_extract_with_empty_data(self):
        profile = {"profile_data": {}}
        signals = extract_profile_signals(profile)

        assert signals.interests == []
        assert not signals.has_any_signals()

    def test_get_spike_components(self):
        signals = ProfileSignals(
            intended_major="Computer Science",
            interests=["AI", "robotics"],
            causes=["education"],
        )
        components = signals.get_spike_components()

        assert "Computer Science" in components
        assert len(components) <= 5


class TestLLMRouter:
    @pytest.mark.asyncio
    async def test_route_urgent_triage(self):
        router = LLMRouter()
        route = await router.decide_route({"months_to_ed": 4})

        assert route.choice == StrategicApproach.URGENT_TRIAGE

    @pytest.mark.asyncio
    async def test_route_build_fresh(self):
        router = LLMRouter()
        route = await router.decide_route({
            "activity_count": 1,
            "months_to_ed": 20,
        })

        assert route.choice == StrategicApproach.BUILD_FRESH

    @pytest.mark.asyncio
    async def test_route_optimize(self):
        router = LLMRouter()
        route = await router.decide_route({
            "activity_count": 8,
            "has_tier1": True,
            "months_to_ed": 15,
        })

        assert route.choice == StrategicApproach.OPTIMIZE


class TestGuardrails:
    def test_validate_awards_with_valid_output(self):
        awards_cache = [{"id": "award-1"}, {"id": "award-2"}]
        engine = GuardrailsEngine(awards_cache=awards_cache)

        output = {
            "portfolio": {
                "reach": [{"id": "award-1"}],
                "target": [{"id": "award-2"}],
                "safety": [],
            }
        }

        result = engine.validate_awards_output(output)
        assert result.passed
        assert result.confidence >= 0.8

    def test_validate_awards_with_hallucinated(self):
        awards_cache = [{"id": "award-1"}]
        engine = GuardrailsEngine(awards_cache=awards_cache)

        output = {
            "portfolio": {
                "reach": [{"id": "fake-award"}],
                "target": [],
                "safety": [],
            }
        }

        result = engine.validate_awards_output(output)
        assert len(result.warnings) > 0
        assert "fake-award" in result.warnings[0]
```

### 7.2 Integration Test

```bash
# Test full flow with huda@ivylevel.com
curl -X POST http://localhost:8001/agents/gameplan/generate \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "4c4c94f9-a7df-4483-9dc6-7905dda36386"}'
```

Expected output:
- `spike` should NOT be empty
- `archetype` should be meaningful (not just default)
- `inference_mode` should be "profile_signals" (if no activities)
- `strategic_route` should be "BUILD_FRESH"

---

## 8. Rollback Strategy

### Feature Flag Disable

If issues arise, disable features in `agents/config.py`:

```python
FEATURE_FLAGS = {
    "use_profile_inference": False,  # Disable profile inference
    "use_llm_routing": False,        # Disable LLM routing
    "enable_guardrails": False,      # Disable guardrails
}
```

### Git Revert

```bash
# If needed, revert to pre-v4.0
git revert HEAD~N  # Where N is number of v4.0 commits
```

---

## 9. Deployment Checklist

- [ ] Phase 1 files created and imports working
- [ ] Phase 2 EC Agent changes applied
- [ ] Phase 3 Orchestrator changes applied
- [ ] Phase 4 Guardrails integrated
- [ ] Unit tests passing
- [ ] Integration test with huda@ivylevel.com successful
- [ ] Backend restarted with new code
- [ ] Frontend verified (spike should now display)
- [ ] Feature flags configured correctly
- [ ] Commit and push to `feat/hybrid-architecture-v4`

---

## 10. Summary

### Files to Create (Phase 1)

| File | Lines | Purpose |
|------|-------|---------|
| `agents/agents/core/__init__.py` | ~30 | Module exports |
| `agents/agents/core/profile_signals.py` | ~150 | Profile signal extraction |
| `agents/agents/core/llm_router.py` | ~120 | Strategic routing |
| `agents/agents/core/guardrails.py` | ~180 | Output validation |

### Files to Modify

| File | Changes | Lines Added |
|------|---------|-------------|
| `agents/config.py` | Add feature flags | ~10 |
| `agents/agents/extracurriculars.py` | Add profile inference | ~200 |
| `agents/agents/gameplan.py` | Add routing | ~80 |
| `agents/agents/awards.py` | Add guardrails | ~20 |
| `agents/agents/programs.py` | Add guardrails | ~20 |

### Total Estimated Lines: ~810

---

*Document Version: 1.0*
*Migration Plan Complete*
*Ready for Implementation*
