# Gap Analysis: Current State vs Hybrid Architecture v4.0
## IvyQuest Multi-Agent System Migration Analysis

**Document Type**: Gap Analysis (Phase 2)
**Date**: January 2026
**Status**: Complete - Ready for Implementation Planning

---

## 1. Executive Summary

### Overall Gap Assessment

| Category | Current | v4.0 Required | Gap Level |
|----------|---------|---------------|-----------|
| **EC Agent** | Activity-only analysis | Profile-based inference + activities | **HIGH** |
| **Awards Agent** | Basic archetype filtering | Full hybrid with guardrails | MEDIUM |
| **Programs Agent** | Basic archetype filtering | Full hybrid with guardrails | MEDIUM |
| **Orchestrator** | Sequential routing | LLM-routed strategic approach | MEDIUM |
| **Routing Layer** | None | LLM decides BUILD/OPTIMIZE/REFRAME | **HIGH** |
| **Guardrails** | None | Full validation pipeline | **HIGH** |
| **Profile Signals** | Partially extracted | Full signal extraction utility | MEDIUM |

### Summary Statistics

| Metric | Value |
|--------|-------|
| Components needing changes | 7 |
| New files to create | 5 |
| Lines of new code (estimated) | ~1,500 |
| Breaking changes | 0 (additive only) |
| Database changes | 0 (use existing schema) |

---

## 2. Component-by-Component Gap Analysis

### 2.1 ExtracurricularsAgent

#### Current State
```
File: agents/agents/extracurriculars.py (631 lines)
Processing: Activity-based only
Failure Mode: Returns placeholder if activities=[]
```

#### v4.0 Requirements
```
Processing: Profile-based inference + Activity analysis
Failure Mode: Always produces meaningful identity synthesis
New Capabilities:
  - _infer_spike_from_profile()
  - _score_archetypes_from_signals()
  - _generate_pillars_from_profile()
```

#### Gap Details

| Feature | Current | v4.0 Required | Gap |
|---------|---------|---------------|-----|
| Activity extraction | ✅ Yes | ✅ Yes | None |
| Spike from activities | ✅ Yes | ✅ Yes | None |
| Spike from profile signals | ❌ No | ✅ Yes | **HIGH** |
| Archetype from activities | ✅ Yes | ✅ Yes | None |
| Archetype from profile signals | ❌ No | ✅ Yes | **HIGH** |
| Portfolio balance | ✅ Yes | ✅ Yes | None |
| Impact assessment | ✅ Yes | ✅ Yes | None |
| Empty activities handling | ❌ Placeholder | ✅ Profile-based | **HIGH** |

#### Required Changes

```python
# NEW: Profile signal extraction (add to extracurriculars.py)
def _extract_profile_signals(self, profile: Dict) -> ProfileSignals:
    """Extract signals from profile_data for inference."""
    profile_data = profile.get("profile_data", {})

    return ProfileSignals(
        # Passion signals
        interests=profile_data.get("passion", {}).get("interests", []),
        dream_career=profile_data.get("passion", {}).get("dream_career", ""),
        causes=profile_data.get("passion", {}).get("causes", []),
        spike_category=profile_data.get("passion", {}).get("spike_category"),

        # Academic signals
        intended_major=profile_data.get("aptitude", {}).get("intended_major", ""),
        favorite_subjects=profile_data.get("aptitude", {}).get("favorite_subjects", []),

        # Identity signals
        strengths=profile_data.get("identity", {}).get("strengths", []),
        values=profile_data.get("identity", {}).get("values", []),

        # Service signals
        volunteer_interests=profile_data.get("service", {}).get("volunteer_interests", []),
    )

# NEW: Spike inference from profile (add to extracurriculars.py)
def _infer_spike_from_profile(self, signals: ProfileSignals) -> Tuple[str, List[str]]:
    """Infer spike when no activities exist."""
    components = []

    if signals.intended_major:
        components.append(signals.intended_major)
    if signals.interests:
        components.extend(signals.interests[:2])
    if signals.causes:
        components.append(signals.causes[0])
    if signals.dream_career:
        components.append(signals.dream_career)

    # Use LLM to synthesize spike phrase
    spike = await self._synthesize_spike_phrase(components)
    return spike, components[:3]

# MODIFY: analyze() method - remove early return
async def analyze(self, profile_id: str) -> Dict[str, Any]:
    profile = await self._get_profile(profile_id)
    if not profile:
        return self._placeholder_response(profile_id)

    # Extract profile signals (ALWAYS)
    signals = self._extract_profile_signals(profile)

    # Extract activities (may be empty)
    activities = self._extract_activities(profile)

    # REMOVE THIS BLOCK:
    # if not activities:
    #     return self._placeholder_response(...)

    # Continue with hybrid processing...
    if activities:
        # Activity-based path (existing logic)
        portfolio_analysis = self._analyze_portfolio_balance(activities)
        identity_synthesis = await self._synthesize_identity(profile, activities, portfolio_analysis)
    else:
        # Profile-based path (NEW)
        identity_synthesis = await self._synthesize_identity_from_profile(profile, signals)

    return {...}
```

#### Effort Estimate
- **Lines to add**: ~200
- **Lines to modify**: ~50
- **Complexity**: MEDIUM (new methods, existing structure)
- **Risk**: LOW (additive, existing tests still pass)

---

### 2.2 AwardsAgent

#### Current State
```
File: agents/agents/awards.py (1069 lines)
Processing: Eligibility + Archetype filtering + ROI scoring
Guardrails: None
```

#### v4.0 Requirements
```
Processing: Same + Guardrails validation
New Capabilities:
  - Output validation (all awards exist in KB)
  - Schema validation
  - Confidence scoring
```

#### Gap Details

| Feature | Current | v4.0 Required | Gap |
|---------|---------|---------------|-----|
| Load enriched data | ✅ Yes | ✅ Yes | None |
| Eligibility filtering | ✅ Yes | ✅ Yes | None |
| Archetype filtering | ✅ Yes | ✅ Yes | None |
| 2-2-1 portfolio | ✅ Yes | ✅ Yes | None |
| Win probability calc | ✅ LLM | ✅ LLM | None |
| ROI calculation | ✅ Yes | ✅ Yes | None |
| Output guardrails | ❌ No | ✅ Yes | MEDIUM |
| Grounding check | ❌ No | ✅ Yes | MEDIUM |

#### Required Changes

```python
# ADD: Import guardrails at top of awards.py
from agents.core.guardrails import GuardrailsEngine, validate_awards_output

# ADD: Guardrails validation before return in match()
async def match(self, profile_id: str, identity_synthesis: Optional[Dict] = None):
    # ... existing logic ...

    result = {
        "success": True,
        "total_matches": len(matched_awards),
        "portfolio": portfolio,
        # ...
    }

    # NEW: Validate output before returning
    validation = validate_awards_output(result, self._enriched_awards_cache)
    if not validation.passed:
        result["validation_warnings"] = validation.warnings
        result["confidence"] = validation.confidence

    return result
```

#### Effort Estimate
- **Lines to add**: ~30 (in awards.py)
- **New dependency**: guardrails.py (shared)
- **Complexity**: LOW
- **Risk**: LOW (additive validation layer)

---

### 2.3 ProgramsAgent

#### Current State
```
File: agents/agents/programs.py (664 lines)
Processing: Eligibility + Archetype filtering + Fit scoring
Guardrails: None
```

#### v4.0 Requirements
```
Processing: Same + Guardrails validation
New Capabilities:
  - Output validation (all programs exist in KB)
  - Schema validation
```

#### Gap Details

| Feature | Current | v4.0 Required | Gap |
|---------|---------|---------------|-----|
| Load enriched data | ✅ Yes | ✅ Yes | None |
| Eligibility filtering | ✅ Yes | ✅ Yes | None |
| Archetype filtering | ✅ Yes | ✅ Yes | None |
| Fit score calculation | ✅ LLM | ✅ LLM | None |
| Hidden value extraction | ✅ Yes | ✅ Yes | None |
| Synergy recommendations | ✅ Yes | ✅ Yes | None |
| Output guardrails | ❌ No | ✅ Yes | MEDIUM |

#### Required Changes
Same pattern as AwardsAgent - add guardrails validation.

#### Effort Estimate
- **Lines to add**: ~30
- **Complexity**: LOW
- **Risk**: LOW

---

### 2.4 GamePlanAgent (Orchestrator)

#### Current State
```
File: agents/agents/gameplan.py (1333 lines)
Orchestration: EC → Awards + Programs (parallel)
Routing: None (always runs full pipeline)
```

#### v4.0 Requirements
```
Orchestration: Same flow
Routing: LLM decides strategic approach first
New Capabilities:
  - Strategic route selection (BUILD/OPTIMIZE/REFRAME/URGENT)
  - Route-specific processing
```

#### Gap Details

| Feature | Current | v4.0 Required | Gap |
|---------|---------|---------------|-----|
| EC Agent first | ✅ Yes | ✅ Yes | None |
| Awards + Programs parallel | ✅ Yes | ✅ Yes | None |
| Result synthesis | ✅ Yes | ✅ Yes | None |
| Master narrative | ✅ Yes | ✅ Yes | None |
| LLM routing layer | ❌ No | ✅ Yes | **MEDIUM** |
| Route-specific handling | ❌ No | ✅ Yes | **MEDIUM** |
| Final guardrails | ❌ No | ✅ Yes | MEDIUM |

#### Required Changes

```python
# ADD: Import router at top of gameplan.py
from agents.core.llm_router import LLMRouter, StrategicRoute

# MODIFY: generate_orchestrated() to include routing
async def generate_orchestrated(self, profile_id: str) -> Dict[str, Any]:
    # STEP 0 (NEW): Determine strategic route
    profile = await self._get_profile(profile_id)
    route = await self._determine_strategic_route(profile)
    print(f"[GamePlan] Strategic route: {route.choice} - {route.reasoning}")

    # STEP 1: Run EC Agent FIRST
    ec_result = await self.ec_agent.process(profile_id)
    identity_synthesis = ec_result.get("identity_synthesis", {})

    # STEP 2: Run Awards + Programs in PARALLEL
    # ... existing code ...

    # STEP 3: Synthesize with route context
    unified_plan = self._synthesize_gameplan(
        profile_id=profile_id,
        identity_synthesis=identity_synthesis,
        ec_result=ec_result,
        awards_result=awards_result,
        programs_result=programs_result,
        strategic_route=route,  # NEW: Pass route for customization
    )

    return {...}

# NEW: Strategic route determination
async def _determine_strategic_route(self, profile: Dict) -> StrategicRoute:
    """LLM decides strategic approach based on student context."""
    profile_data = profile.get("profile_data", {})
    activities = profile_data.get("experience", {}).get("activities", [])
    grade = profile_data.get("identity", {}).get("grade", 11)

    context = {
        "grade": grade,
        "activity_count": len(activities),
        "has_tier1": any(a.get("tier") == "T1" for a in activities),
        "months_to_ed": self._calculate_months_to_ed(grade),
    }

    return await self.router.decide_route(context)
```

#### Effort Estimate
- **Lines to add**: ~100
- **New dependency**: llm_router.py
- **Complexity**: MEDIUM
- **Risk**: LOW (additive routing layer)

---

## 3. New Components Required

### 3.1 ProfileSignals Utility

**Status**: ❌ Does not exist
**Required for**: EC Agent profile-based inference

```python
# NEW FILE: agents/core/profile_signals.py

from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class ProfileSignals:
    """Extracted signals from profile_data for inference."""

    # Passion signals
    interests: List[str] = field(default_factory=list)
    dream_career: str = ""
    causes: List[str] = field(default_factory=list)
    spike_category: Optional[str] = None

    # Academic signals
    intended_major: str = ""
    favorite_subjects: List[str] = field(default_factory=list)
    gpa: Optional[float] = None
    sat_total: Optional[int] = None

    # Identity signals
    strengths: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    grade: int = 11

    # Service signals
    volunteer_interests: List[str] = field(default_factory=list)
    community_focus: Optional[str] = None

    def has_passion_signals(self) -> bool:
        return bool(self.interests or self.dream_career or self.causes)

    def has_academic_signals(self) -> bool:
        return bool(self.intended_major or self.favorite_subjects)


def extract_profile_signals(profile: Dict) -> ProfileSignals:
    """Extract signals from profile dict."""
    profile_data = profile.get("profile_data", {})

    passion = profile_data.get("passion", {})
    aptitude = profile_data.get("aptitude", {})
    identity = profile_data.get("identity", {})
    service = profile_data.get("service", {})

    return ProfileSignals(
        interests=passion.get("interests", []),
        dream_career=passion.get("dream_career", ""),
        causes=passion.get("causes", passion.get("causes_care_about", [])),
        spike_category=passion.get("spike_category"),
        intended_major=aptitude.get("intended_major", ""),
        favorite_subjects=aptitude.get("favorite_subjects", []),
        gpa=aptitude.get("gpa_weighted"),
        sat_total=aptitude.get("sat_total"),
        strengths=identity.get("strengths", []),
        values=identity.get("values", []),
        grade=identity.get("grade", 11),
        volunteer_interests=service.get("volunteer_interests", []),
        community_focus=service.get("community_focus"),
    )
```

**Effort**: ~80 lines, LOW complexity

---

### 3.2 LLM Router

**Status**: ❌ Does not exist
**Required for**: Strategic approach selection

```python
# NEW FILE: agents/core/llm_router.py

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum
from langchain_openai import ChatOpenAI

class StrategicApproach(Enum):
    BUILD_FRESH = "BUILD_FRESH"       # No activities, be prescriptive
    OPTIMIZE = "OPTIMIZE"             # Strong foundation, enhance
    REFRAME = "REFRAME"               # Has activities, need narrative pivot
    URGENT_TRIAGE = "URGENT_TRIAGE"   # Limited time, quick wins only

@dataclass
class StrategicRoute:
    choice: StrategicApproach
    reasoning: str
    config: Dict

class LLMRouter:
    """Routes students to appropriate strategic approach."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    async def decide_route(self, context: Dict) -> StrategicRoute:
        """Decide strategic approach based on student context."""

        # Deterministic rules first
        if context.get("months_to_ed", 20) < 6:
            return StrategicRoute(
                choice=StrategicApproach.URGENT_TRIAGE,
                reasoning="Less than 6 months to Early Decision",
                config={"focus": ["positioning", "quick_wins"]}
            )

        if context.get("activity_count", 0) < 3:
            return StrategicRoute(
                choice=StrategicApproach.BUILD_FRESH,
                reasoning="Minimal activities, need to build foundation",
                config={"be_prescriptive": True, "recommend_activities": True}
            )

        if context.get("has_tier1"):
            return StrategicRoute(
                choice=StrategicApproach.OPTIMIZE,
                reasoning="Strong T1 activity foundation",
                config={"focus": ["positioning", "narrative", "impact_evidence"]}
            )

        # Default: REFRAME
        return StrategicRoute(
            choice=StrategicApproach.REFRAME,
            reasoning="Activities exist but may need narrative repositioning",
            config={"focus": ["narrative_pivot", "connect_dots"]}
        )
```

**Effort**: ~100 lines, MEDIUM complexity

---

### 3.3 Guardrails Engine

**Status**: ❌ Does not exist
**Required for**: Output validation, hallucination prevention

```python
# NEW FILE: agents/core/guardrails.py

from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class CheckResult:
    passed: bool
    guardrail: str
    message: str = ""
    details: Optional[Dict] = None

@dataclass
class ValidationResult:
    passed: bool
    warnings: List[str]
    confidence: float
    checks: List[CheckResult]

class GuardrailsEngine:
    """Validates agent outputs to prevent hallucination."""

    def __init__(self, knowledge_base: Dict[str, List]):
        self.kb = knowledge_base
        self._award_ids = {a["id"] for a in knowledge_base.get("awards", [])}
        self._program_ids = {p["id"] for p in knowledge_base.get("programs", [])}

    def validate_awards_output(self, output: Dict) -> ValidationResult:
        """Validate awards agent output."""
        checks = []
        warnings = []

        # Check all recommended awards exist in KB
        portfolio = output.get("portfolio", {})
        for category in ["reach", "target", "safety"]:
            for award in portfolio.get(category, []):
                award_id = award.get("id") or award.get("award_id")
                if award_id and award_id not in self._award_ids:
                    checks.append(CheckResult(
                        passed=False,
                        guardrail="grounded_awards",
                        message=f"Award '{award_id}' not found in knowledge base",
                    ))
                    warnings.append(f"Ungrounded award: {award_id}")

        # Schema validation
        if not portfolio:
            checks.append(CheckResult(
                passed=False,
                guardrail="valid_schema",
                message="Missing portfolio in output",
            ))

        passed = all(c.passed for c in checks) if checks else True
        confidence = 1.0 - (len(warnings) * 0.1)

        return ValidationResult(
            passed=passed,
            warnings=warnings,
            confidence=max(0.5, confidence),
            checks=checks,
        )

    def validate_programs_output(self, output: Dict) -> ValidationResult:
        """Validate programs agent output."""
        # Similar pattern to awards
        ...


def validate_awards_output(output: Dict, awards_cache: List[Dict]) -> ValidationResult:
    """Convenience function for awards validation."""
    engine = GuardrailsEngine({"awards": awards_cache})
    return engine.validate_awards_output(output)
```

**Effort**: ~150 lines, MEDIUM complexity

---

## 4. Database Analysis

### 4.1 Current Schema (No Changes Needed)

The current database schema is sufficient for v4.0:

| Table | Used For | v4.0 Compatible |
|-------|----------|-----------------|
| `profiles` | User profiles | ✅ Yes |
| `assessments` | Assessment + profile_data | ✅ Yes |
| `agent_state_versions` | State versioning | ✅ Yes |
| `agent_events` | Event logging | ✅ Yes |

### 4.2 Profile Data Structure

The `assessments.profile_data` JSON already contains all signals needed for profile-based inference:

```json
{
  "identity": { "grade": 11, "strengths": [...], "values": [...] },
  "aptitude": { "gpa_weighted": 4.0, "intended_major": "...", "favorite_subjects": [...] },
  "passion": { "interests": [...], "dream_career": "...", "causes": [...] },
  "service": { "volunteer_interests": [...] },
  "experience": { "activities": [...] }
}
```

**Conclusion**: No database migrations required.

### 4.3 Supabase Vector (pgvector)

**Assessment**: NOT NEEDED for v4.0

Current implementation uses:
- JSON file-based knowledge base (awards_enriched.json, programs_enriched.json)
- In-memory filtering by archetype fit scores

Vector embeddings would be beneficial for:
- Semantic search ("find awards similar to X")
- More nuanced matching

**Recommendation**: Defer to future version (v4.1+)

---

## 5. Risk Assessment

### 5.1 Change Risk Matrix

| Change | Impact | Likelihood | Mitigation |
|--------|--------|------------|------------|
| EC Agent profile inference | HIGH | LOW | Feature flag, fallback to placeholder |
| LLM Router | MEDIUM | LOW | Deterministic rules first, LLM optional |
| Guardrails | LOW | LOW | Additive validation, doesn't block output |
| Awards/Programs guardrails | LOW | LOW | Warnings only, doesn't break flow |

### 5.2 Rollback Strategies

| Component | Rollback Strategy |
|-----------|-------------------|
| EC Agent | Feature flag `USE_PROFILE_INFERENCE=false` |
| LLM Router | Feature flag `USE_LLM_ROUTING=false` |
| Guardrails | Feature flag `ENABLE_GUARDRAILS=false` |

### 5.3 Testing Requirements

| Component | Test Type | Priority |
|-----------|-----------|----------|
| ProfileSignals extraction | Unit | HIGH |
| Spike inference from profile | Unit + Integration | HIGH |
| Archetype scoring from signals | Unit | HIGH |
| LLM Router decisions | Unit | MEDIUM |
| Guardrails validation | Unit | MEDIUM |
| End-to-end orchestration | Integration | HIGH |

---

## 6. Prioritized Implementation Plan

### Phase 1: Foundation (No Breaking Changes)

| Priority | Task | Files | Effort |
|----------|------|-------|--------|
| P0 | Create ProfileSignals utility | `agents/core/profile_signals.py` | 80 lines |
| P0 | Create LLM Router | `agents/core/llm_router.py` | 100 lines |
| P0 | Create Guardrails Engine | `agents/core/guardrails.py` | 150 lines |
| P0 | Create `agents/core/__init__.py` | Export new modules | 10 lines |

**Total Phase 1**: ~340 lines, 0 breaking changes

### Phase 2: EC Agent Enhancement

| Priority | Task | Files | Effort |
|----------|------|-------|--------|
| P0 | Add `_extract_profile_signals()` | `extracurriculars.py` | 50 lines |
| P0 | Add `_infer_spike_from_profile()` | `extracurriculars.py` | 60 lines |
| P0 | Add `_score_archetypes_from_signals()` | `extracurriculars.py` | 80 lines |
| P0 | Modify `analyze()` to use hybrid path | `extracurriculars.py` | 40 lines |
| P1 | Add feature flag for new behavior | `extracurriculars.py` | 10 lines |

**Total Phase 2**: ~240 lines

### Phase 3: Orchestrator Enhancement

| Priority | Task | Files | Effort |
|----------|------|-------|--------|
| P1 | Add routing step to `generate_orchestrated()` | `gameplan.py` | 50 lines |
| P1 | Add `_determine_strategic_route()` | `gameplan.py` | 40 lines |
| P2 | Add route-specific synthesis customization | `gameplan.py` | 60 lines |

**Total Phase 3**: ~150 lines

### Phase 4: Guardrails Integration

| Priority | Task | Files | Effort |
|----------|------|-------|--------|
| P2 | Add guardrails to AwardsAgent | `awards.py` | 30 lines |
| P2 | Add guardrails to ProgramsAgent | `programs.py` | 30 lines |
| P2 | Add final guardrails to GamePlanAgent | `gameplan.py` | 40 lines |

**Total Phase 4**: ~100 lines

---

## 7. Summary

### What Exists (Keep As-Is)
- ✅ Orchestration flow (EC → Awards + Programs parallel)
- ✅ Enriched knowledge base (97 awards, 58 programs)
- ✅ Strategic Intelligence fields (archetype_fit, strategic_tier, etc.)
- ✅ 2-2-1 portfolio strategy
- ✅ Frontend components and stores
- ✅ Database schema

### What Needs Adding
- ❌ ProfileSignals utility for profile data extraction
- ❌ LLM Router for strategic approach selection
- ❌ Guardrails Engine for output validation
- ❌ EC Agent profile-based inference methods

### What Needs Modifying
- ⚠️ EC Agent `analyze()` method - add hybrid path
- ⚠️ GamePlan `generate_orchestrated()` - add routing step
- ⚠️ Awards/Programs agents - add guardrails validation

### What Stays Unchanged
- Database schema (no migrations)
- API endpoints (same contracts)
- Frontend stores (already have Strategic Intelligence types)
- Enriched seed data (already complete)

---

## 8. Recommended Next Steps

1. **Create new core modules** (Phase 1) - No risk, pure additions
2. **Enhance EC Agent** (Phase 2) - With feature flag
3. **Test with huda@ivylevel.com** - Verify spike is generated
4. **Add routing to orchestrator** (Phase 3)
5. **Add guardrails** (Phase 4)

### Implementation Order

```
Week 1: Phase 1 (Foundation)
├── profile_signals.py
├── llm_router.py
└── guardrails.py

Week 2: Phase 2 (EC Agent)
├── Add profile inference methods
├── Modify analyze() with feature flag
└── Test with empty-activity profiles

Week 3: Phase 3 + 4 (Orchestrator + Guardrails)
├── Add routing to GamePlan
├── Add guardrails to all agents
└── End-to-end testing
```

---

*Document Version: 1.0*
*Gap Analysis Complete*
*Ready for Phase 3: Implementation Planning*
