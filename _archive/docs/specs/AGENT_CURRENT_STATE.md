# IvyLevel Multi-Agent System - Current State

## Overview

The IvyLevel platform uses a multi-agent orchestration system where specialized agents handle different aspects of college admissions strategy. All agents share a common middleware infrastructure (v9.0, 50 patterns).

## Agent Inventory

| Agent | File | Size | Primary Function |
|-------|------|------|------------------|
| GamePlan | `gameplan.py` | 78,026 bytes | Master orchestrator, narrative synthesis |
| Extracurriculars (EC) | `extracurriculars.py` | 65,104 bytes | Activity analysis, spike identification |
| Awards | `awards.py` | ~25,000 bytes | Award recommendations, prestige scoring |
| Programs | `programs.py` | ~20,000 bytes | Summer program recommendations |
| Execution | `execution.py` | 38,827 bytes | Strategy-to-action conversion |

## Agent Details

### 1. GamePlan Agent (Master Orchestrator)

**File**: `agents/agents/gameplan.py`
**Version**: v1.0.0 Orchestration + Middleware v8 integration
**Autonomy**: HIGH (planning), handoff if narrative coherence < 80%

**Responsibilities**:
- Master narrative synthesis from 4 Pillars (Identity, Aptitude, Passion, Service)
- Orchestrate sub-agents (EC → Awards+Programs → Synthesis)
- Strategic routing based on timeline
- Apply Strategic Overwhelm (1.4x capacity assignment)
- Multi-touchpoint leverage (≥4 touchpoints required per activity)

**Orchestration Flow**:
```
1. EC Agent (FIRST) → identity_synthesis (spike, archetype, pillars)
2. Awards + Programs (PARALLEL) ← use identity_synthesis for filtering
3. Synthesis → Unified GamePlan with activities, awards, programs
```

**Key Primitives**:
- **ACP-004**: Strategic Overwhelm (1.4x task assignment)
- **ACP-005**: Multi-Touchpoint Leverage (≥4 touchpoints required)
- **ACP-006**: Identity Seed Architecture (6-12 month advance planting)

**Middleware Integration**: MiddlewareStackV8 (40 patterns)
- J1: Reasoning Traces (orchestration visibility)
- J3: Audit Trail (compliance for planning)
- E4: Quality Scoring
- H3: Retry Logic

---

### 2. Extracurriculars (EC) Agent

**File**: `agents/agents/extracurriculars.py`
**Version**: v5.0 with ReAct wrapping support
**Autonomy**: HIGH for analysis, MEDIUM for recommendations

**Responsibilities**:
- Activity portfolio analysis
- Spike identification (primary passion/strength)
- Archetype detection (Leader, Innovator, Specialist, etc.)
- 4 Pillars extraction (Identity, Aptitude, Passion, Service)
- Activity gap identification
- Recommendation generation

**Output (identity_synthesis)**:
```python
{
    "spike": {
        "area": "Computer Science & Education",
        "confidence": 0.85,
        "evidence": [...]
    },
    "archetype": "The Innovator-Educator",
    "pillars": {
        "identity": "Tech-empowered educator bridging gaps",
        "aptitude": "Strong technical + communication skills",
        "passion": "Democratizing education through technology",
        "service": "Community coding programs"
    },
    "recommended_activities": [...],
    "gaps_identified": [...]
}
```

**ReAct Configuration**:
- Wrapped with `create_react_wrapped_agent()`
- max_cycles: 3 (configurable via FEATURE_FLAGS)
- Quality thresholds: 70/70/0.6 (completeness/confidence/coherence)

---

### 3. Awards Agent

**File**: `agents/agents/awards.py`
**Version**: v4.0 with middleware integration
**Autonomy**: HIGH for analysis, MEDIUM for recommendations

**Responsibilities**:
- Award opportunity identification
- Prestige scoring and tier classification
- Timeline alignment with application deadlines
- Profile-to-award matching
- Application strategy recommendations

**Award Tiers**:
| Tier | Examples | Impact |
|------|----------|--------|
| National | Presidential Scholar, Regeneron STS | Highest differentiation |
| Regional | Governor's Award, Regional Science Fair | Strong signal |
| State | State competition winners | Good signal |
| Local | School awards, local competitions | Foundation |

**Key Features**:
- Uses identity_synthesis from EC Agent for filtering
- Considers months-to-ED for timeline feasibility
- Tracks application deadlines and requirements

---

### 4. Programs Agent

**File**: `agents/agents/programs.py`
**Version**: v4.0 with middleware integration
**Autonomy**: HIGH for research, MEDIUM for recommendations

**Responsibilities**:
- Summer program identification
- Program-to-profile matching
- Selectivity assessment
- Cost/scholarship analysis
- Application timeline management

**Program Categories**:
- Research programs (RSI, SSP, etc.)
- Academic enrichment (Governor's Schools)
- Pre-college programs (university-sponsored)
- Competition prep (Math Olympiad camps)
- Leadership programs (HOBY, etc.)

**Key Features**:
- Uses identity_synthesis for program alignment
- Considers grade-appropriate timing
- Tracks application deadlines

---

### 5. Execution Agent

**File**: `agents/agents/execution.py`
**Version**: v10.0 Framework / Middleware v8 integration
**Autonomy**: MEDIUM for most actions, LOW for crises (HITL required)

**Responsibilities**:
- Project scaffolding (break into 20+ microsteps)
- Crisis Alchemy Protocol (transform crises → opportunities)
- Blocker detection (>5 days inactivity)
- EDS (Execution Debt Score) tracking
- Talk-First-Write-Second essay support
- Jenny Intelligence features

**Key Primitives**:
- **ACP-003**: Crisis Alchemy Protocol (4-step: Validate, Act, Reframe, Create)
- **ACP-004**: Strategic Overwhelm (1.4x capacity, 73% completion target)
- **ACP-007**: Talk-First-Write-Second

**Huda Benchmarks** (Target vs Achieved):
| Metric | Target | Huda Benchmark |
|--------|--------|----------------|
| Project Completion | >80% | 100% |
| Crisis Recovery | <72 hours | <2 hours |
| Task Completion | >70% | 73% |
| EDS | <50 | 12 |

*See EXECUTION_AGENT_DETAILED.md for full feature documentation*

---

## Shared Infrastructure

### Middleware Stack v9.0

All agents share access to the MiddlewareStack, though integration depth varies:

| Agent | Middleware Version | Integration Depth |
|-------|-------------------|-------------------|
| GamePlan | v8 (40 patterns) | Full |
| EC | v8 via wrapper | Full |
| Awards | v8 | Partial |
| Programs | v8 | Partial |
| Execution | v8 (40 patterns) | Full |

**Common Patterns Used**:
- **C1/C2**: Session and user context management
- **J1**: Reasoning traces for observability
- **J3**: Audit trail for compliance
- **E4**: Quality scoring
- **H3**: Retry logic with exponential backoff

### ReAct Framework v13.2

**Status**: Available, feature-flagged

```python
FEATURE_FLAGS = {
    "enable_react": False,          # Master switch
    "react_wrap_sub_agents": True,  # Wrap EC/Awards/Programs
    "react_max_cycles": 3,          # Max iterations
}
```

**Quality Thresholds**:
```python
ReActAgentConfig:
    quality_thresholds:
        completeness: 70
        confidence: 70
        coherence: 0.6
```

### Event Bus

Agents communicate via an event bus (Supabase `events` table):

| Event Type | Publisher | Subscribers |
|------------|-----------|-------------|
| GAMEPLAN_GENERATED | GamePlan | Dashboard, Execution |
| CRISIS_DETECTED | Execution | Dashboard, Notifications |
| PROJECT_STALLED | Execution | Dashboard, Notifications |
| ASSESSMENT_COMPLETE | Assessment | GamePlan, Scoring |

---

## Agent Communication Patterns

### Orchestration Pattern (GamePlan → Sub-agents)

```
GamePlan.generate_orchestrated(profile_id)
    │
    ├─→ EC Agent.process(profile_id)
    │       └─→ Returns: identity_synthesis
    │
    ├─→ (PARALLEL)
    │   ├─→ Awards Agent.process(profile_id, identity_synthesis)
    │   └─→ Programs Agent.process(profile_id, identity_synthesis)
    │
    └─→ Narrative Synthesis
            └─→ Unified GamePlan
```

### Handoff Pattern (Agent → Human)

```
Agent detects condition requiring human review
    │
    ├─→ Create pending_approval record
    ├─→ Publish APPROVAL_NEEDED event
    ├─→ Set deadline (configurable, default 1 hour)
    │
    └─→ Wait for human response
            ├─→ Approved: Continue execution
            └─→ Rejected: Escalate or adjust
```

---

## Current Limitations

1. **ReAct Disabled by Default**: Feature-flagged off, needs explicit enablement
2. **No Real-time Collaboration**: Agents don't share working memory during execution
3. **Linear Orchestration**: EC must complete before Awards/Programs start
4. **Limited Learning**: Phase 3 learning patterns (I1-I5) newly available, not yet utilized
5. **Memory Isolation**: Each agent session starts fresh, semantic memory underutilized

## Version Summary

| Component | Current Version | Notes |
|-----------|-----------------|-------|
| Framework | v10.0 | IvyQuest overall |
| Middleware | v9.0 (50 patterns) | Phase 3 complete |
| ReAct | v13.2 | Feature-flagged |
| GamePlan | v1.0.0 Orchestration | Middleware v8 |
| EC Agent | v5.0 | ReAct-wrappable |
| Execution | v10.0 | Full middleware integration |

---

*Document generated: Platform Discovery Phase 2*
*Agent System Status: Production-ready with enhancement opportunities*
