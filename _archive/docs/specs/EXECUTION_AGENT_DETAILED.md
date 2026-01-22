# Execution Agent - Detailed Documentation

## Version Information

| Property | Value |
|----------|-------|
| **Framework Version** | IvyQuest v10.0 |
| **File** | `agents/agents/execution.py` |
| **Size** | 38,827 bytes (~1,000 lines) |
| **Middleware Version** | v8 (40 patterns) |
| **Autonomy Level** | MEDIUM (most actions), LOW (crises require HITL) |

## Purpose

The Execution Agent bridges the **strategy-execution gap** - the critical gap between having a college admissions strategy and actually executing it. This agent prevents the **80% user abandonment** that occurs when students receive great advice but fail to follow through.

## Core Primitives

### ACP-003: Crisis Alchemy Protocol

**Purpose**: Transform crises into opportunities (rejection → pivot → stronger application)

**Implementation**: Uses LangGraph for 4-step protocol execution

**4-Step Protocol**:

| Step | Duration | Action |
|------|----------|--------|
| 1. Validate | 2 seconds | Acknowledge emotion immediately |
| 2. Act | 10 seconds | Provide one concrete micro-action |
| 3. Reframe | 30 seconds | Find the opportunity angle |
| 4. Create | 2 minutes | Design new activity/pivot |

**Code Location**: `agents/agents/execution.py:396-502`

```python
async def handle_crisis(
    self,
    profile_id: str,
    crisis_type: str,
    description: str,
    urgency: int = 3
) -> Dict[str, Any]:
    """
    Execute Crisis Alchemy Protocol via LangGraph.
    Autonomy: LOW - Requires HITL approval within 1 hour.
    """
    # Creates crisis record
    # Runs 4-step protocol via CrisisAlchemyGraph
    # Returns proposed response for human approval
```

**LangGraph Integration**: `graphs/crisis_alchemy.py` (separate file)

---

### ACP-004: Strategic Overwhelm

**Purpose**: Assign 1.4x tasks because completing 73% of 10 tasks is better than completing 70% of 7 tasks.

**The Math**:
- Assign 10 tasks → Student completes 7 (70%) → **7 tasks done**
- Assign 7 tasks → Student completes 5 (71%) → **5 tasks done**
- Net gain: **2 additional completed tasks**

**Configuration**:
```python
settings.overwhelm_factor = 1.4  # 40% inflation
settings.target_completion_rate = 0.73  # 73% expected completion
```

**Code Location**: `agents/agents/execution.py:361-390`

```python
def _apply_strategic_overwhelm(self, base_steps: List[Dict]) -> List[Dict]:
    """
    Apply Strategic Overwhelm: inflate tasks by 1.4x.
    Adds stretch goals and enhanced versions of base steps.
    """
    overwhelm_factor = settings.overwhelm_factor  # 1.4
    base_count = len(base_steps)
    target_count = int(base_count * overwhelm_factor)

    result = list(base_steps)

    # Add stretch goals to reach target
    while len(result) < target_count:
        # Create stretch versions of existing steps
        stretch_step = {
            "title": f"Stretch: {base_step['title']} (enhanced)",
            "is_stretch": True,
            "difficulty": base_step.get("difficulty", 0.5) * 0.5,  # Lower difficulty
        }
        result.append(stretch_step)

    return result
```

---

### ACP-007: Talk-First-Write-Second

**Purpose**: Overcome the blank page problem by speaking first, then transcribing and refining.

**Essay Template Steps** (from `_generate_base_steps`):
```python
"essay": [
    {"title": "Brainstorm essay topics (5-10 ideas)"},
    {"title": "Record voice memo about chosen topic"},      # <-- Talk-First
    {"title": "Transcribe and identify key themes"},       # <-- Write-Second
    {"title": "Create outline from themes"},
    {"title": "Write first draft (no editing)"},
    {"title": "Let draft sit for 24 hours"},
    {"title": "Read aloud and note awkward parts"},
    {"title": "Revise for clarity and flow"},
    {"title": "Get feedback from trusted reader"},
    {"title": "Apply micro-edits (word choice)"},
    {"title": "Final proofread"},
    {"title": "Submit or save final version"},
]
```

---

## Implemented Features

### 1. Project Scaffolding

**Purpose**: Break projects into 20+ microsteps for manageable execution

**Process**:
1. Accept project definition (name, type, description)
2. Generate base steps from template (12-15 steps per type)
3. Apply Strategic Overwhelm (1.4x inflation)
4. Create project record with touchpoints
5. Create step records with difficulty weights

**Project Types Supported**:
| Type | Base Steps | Template |
|------|------------|----------|
| Extracurricular | 12 | Club creation, events, impact |
| Research | 13 | Literature review, data, publication |
| Essay | 12 | Brainstorm, talk-first, revise |
| Community | 12 | Need identification, service, impact |

**Code Location**: `agents/agents/execution.py:178-276`

---

### 2. Crisis Alchemy via LangGraph

**Purpose**: Transform setbacks into opportunities

**Crisis Types Handled**:
- `blocker` - Project stalled, can't proceed
- `rejection` - Award/program rejection
- `failure` - Competition/test failure
- `overwhelm` - Too many tasks, paralysis
- `deadline` - Missed or approaching deadline

**Urgency Mapping**:
```python
def _map_urgency(self, numeric_urgency: int) -> str:
    mapping = {
        1: "low",
        2: "low",
        3: "medium",
        4: "high",
        5: "critical",
    }
```

**HITL Requirement**: All crisis responses require human approval within 1 hour

**Fallback Response** (if LangGraph fails):
```python
def _generate_fallback_response(self, crisis_type, description):
    return {
        "step1_validation": {
            "message": "I hear you. This is a difficult situation...",
        },
        "step2_micro_action": {
            "action": "Take 5 minutes to write down exactly what happened...",
        },
        "step3_reframe": {
            "opportunity_angle": "Every setback reveals a gap that can become your unique contribution.",
        },
        "step4_creation": {
            "activity_name": "Reflection and Pivot Planning",
            "first_step": "Schedule 30 minutes tomorrow to brainstorm alternatives.",
        },
    }
```

**Code Location**: `agents/agents/execution.py:396-535`

---

### 3. Blocker Detection

**Purpose**: Monitor for projects with >5 days inactivity

**Configuration**:
```python
self.blocker_threshold_days = settings.blocker_threshold_days  # Default: 5
```

**Detection Logic**:
```python
async def detect_blockers(self, profile_id: str):
    projects = await get_projects(profile_id, status="active")
    blockers = []

    for project in projects:
        days_stuck = (datetime.now() - last_activity).days

        if days_stuck >= self.blocker_threshold_days:
            blockers.append({
                "project_id": project["id"],
                "days_stuck": days_stuck,
                "type": "inactivity",
            })

            # Publish event
            await self._publish_event("PROJECT_STALLED", {...})

    return {"blockers": blockers, "count": len(blockers)}
```

**Code Location**: `agents/agents/execution.py:612-666`

---

### 4. EDS (Execution Debt Score) Tracking

**Purpose**: Quantify execution gap for intervention triggers

**Formula**:
```
EDS = Σ(missed_microsteps × days_delayed × difficulty_weight)
```

**Thresholds**:
| EDS | Status | Action |
|-----|--------|--------|
| <50 | Healthy | Continue normal operation |
| 50-99 | At Risk | Send gentle nudge |
| ≥100 | Critical | Intervention required |

**Huda Benchmark**: EDS = 12 (excellent execution discipline)

**Code Location**: `agents/agents/execution.py:672-690`

---

### 5. Jenny Intelligence Features

#### 5a. Celebration Calibration

**Purpose**: Celebrate wins proportional to difficulty

**Celebration Levels**:
| Level | Score | Response |
|-------|-------|----------|
| Micro | <0.5 | "Step completed. Keep the momentum!" |
| Minor | 0.5-1.0 | "Nice work! You're making real progress." |
| Major | 1.0-1.5 | "Major milestone achieved! Document this." |
| Breakthrough | ≥1.5 | "Outstanding achievement! This sets you apart." |

**Score Calculation**:
```python
celebration_score = difficulty
if is_milestone: celebration_score *= 1.5
if was_stretch: celebration_score *= 1.3
if days_early > 0: celebration_score *= 1.1
```

**Code Location**: `agents/agents/execution.py:731-800`

---

#### 5b. Silence Detection

**Purpose**: Detect when student has been quiet too long

**Thresholds**:
| Days Silent | Severity | Nudge |
|-------------|----------|-------|
| 3-6 | Warning | "Just checking in! Small steps daily beat big bursts weekly." |
| 7-13 | Concern | "It's been a week. What's one small thing you could do today?" |
| ≥14 | Critical | "We haven't heard from you in over 2 weeks. Is everything okay?" |

**Suggested Actions**:
- Warning: Send gentle reminder about current step
- Concern: Send personalized check-in with specific, low-effort task
- Critical: Schedule coaching call or reach out via preferred channel

**Code Location**: `agents/agents/execution.py:873-935`

---

#### 5c. 3x Time Buffer

**Purpose**: Apply realistic time estimates (students chronically underestimate)

**Buffer Multipliers**:
| Task Type | Multiplier | Rationale |
|-----------|------------|-----------|
| Essay | 3.0x | Essays take WAY longer than expected |
| Research | 2.5x | Research has many unknowns |
| Creative | 3.0x | Creative work is hard to estimate |
| Admin | 2.0x | Administrative tasks relatively predictable |
| Default | 2.5x | Safe default |

**Example**:
```python
# Input: 4 hours estimated for essay
# Output: {
#   "original_estimate": 4,
#   "buffer_multiplier": 3.0,
#   "buffered_estimate": 12.0,
#   "recommended_schedule": {
#     "hours_per_week": 3,
#     "weeks_needed": 4.0,
#     "target_completion": "2024-02-15"
#   }
# }
```

**Code Location**: `agents/agents/execution.py:940-999`

---

## Middleware Integration (v8)

### Integrated Patterns

| Pattern | Usage in Execution Agent |
|---------|-------------------------|
| J1 Reasoning Traces | Track all actions for observability |
| J3 Audit Trail | Log all state changes for compliance |
| J4 Metrics | Record EDS values for monitoring |
| E4 Quality Scoring | Validate output quality |
| H3 Retry Logic | Handle transient failures |
| C1 Session Context | Maintain conversation context |
| C2 User Context | Load profile preferences |

### Integration Code

```python
async def process(self, profile_id: str, **kwargs):
    # Start reasoning trace (J1)
    trace_id = self.start_reasoning_trace(
        profile_id=profile_id,
        session_id=session_id,
        input_message=f"action={action}",
    )

    try:
        # Use middleware context (C1, C2)
        async with self.with_middleware_context(
            profile_id=profile_id,
            session_id=session_id,
            task_type="execution",
        ) as ctx:
            self.add_thought(trace_id, f"Processing action: {action}")

            # Execute action...
            result = await self.scaffold_project(...)

            # Finalize with middleware validation
            result = self.middleware_finalize(result, output_type="execution")

            # Audit trail (J3)
            await self.audit_action(
                action=action,
                resource_type="execution",
                resource_id=profile_id,
                details={"success": True},
            )

            # Complete trace (J1)
            await self.end_reasoning_trace(trace_id, success=True)

            return result

    except Exception as e:
        await self.end_reasoning_trace(trace_id, success=False, error=str(e))
        raise
```

---

## API Actions

| Action | Method | Purpose | Autonomy |
|--------|--------|---------|----------|
| `scaffold_project` | `scaffold_project()` | Create project with microsteps | MEDIUM |
| `handle_crisis` | `handle_crisis()` | Execute Crisis Alchemy | LOW (HITL) |
| `detect_blockers` | `detect_blockers()` | Find stalled projects | HIGH |
| `compute_eds` | `compute_eds()` | Calculate Execution Debt Score | HIGH |
| `check_status` | `check_status()` | Get overall execution status | HIGH |
| `complete_step` | `complete_step()` | Mark step done + celebration | MEDIUM |
| `process_handoff` | `process_handoff()` | Handle HITL approval/rejection | N/A (human) |

---

## Event Publishing

| Event Type | Trigger | Payload |
|------------|---------|---------|
| `GAMEPLAN_GENERATED` | Project scaffolded | profileId, activities, seeds |
| `CRISIS_DETECTED` | Crisis identified | profileId, crisisId, severity, type |
| `PROJECT_STALLED` | Blocker detected | profileId, projectId, days, debt |

---

## Huda Benchmarks

The Execution Agent is calibrated against "Huda" - the ideal student execution profile:

| Metric | Target | Huda Achieved |
|--------|--------|---------------|
| Project Completion Rate | >80% | 100% |
| Crisis Recovery Time | <72 hours | <2 hours |
| Task Completion Rate | >70% | 73% |
| Execution Debt Score | <50 | 12 |

---

## Missing/Incomplete Features

Based on code analysis, the following features are partially implemented or missing:

### Partially Implemented

1. **Voice Recording Integration** (ACP-007)
   - Template steps reference voice memos
   - Actual recording/transcription not implemented
   - **Gap**: No audio capture or transcription service

2. **LangGraph Crisis Graph**
   - Import statement present: `from graphs.crisis_alchemy import CrisisAlchemyGraph`
   - Fallback handler exists (suggests graph may fail)
   - **Gap**: Need to verify graph implementation completeness

### Not Yet Implemented

1. **Middleware v9 Integration**
   - Currently uses v8 (40 patterns)
   - v9 patterns (semantic memory, cost tracking) available but not used
   - **Gap**: Could benefit from B3 (semantic memory) for context

2. **Real-time EDS Dashboard**
   - EDS computed but not continuously monitored
   - No push notifications for threshold breaches
   - **Gap**: Dashboard widget for live EDS

3. **Automated Intervention Triggers**
   - Silence detection exists but manual review required
   - No automated outreach for critical silence
   - **Gap**: Automated nudge system

---

## Enhancement Recommendations

### P0 - Immediate

1. **Upgrade to Middleware v9**
   - Change: `from .stack_v8 import MiddlewareStackV8` → `from .stack_v9 import MiddlewareStackV9`
   - Add cost tracking after LLM calls
   - Enable semantic memory for crisis context

### P1 - Short-term

2. **Integrate Cost Tracking (J5)**
   ```python
   # After any LLM call
   await self.middleware.track_cost(
       model="gpt-4o",
       input_tokens=response.usage.prompt_tokens,
       output_tokens=response.usage.completion_tokens,
       profile_id=profile_id,
       request_type="crisis_alchemy",
   )
   ```

3. **Add Automated Silence Nudges**
   - Scheduled job to run `_detect_silence()` daily
   - Automated email/SMS for concern/critical levels
   - Configurable notification preferences

### P2 - Medium-term

4. **Voice Integration for Talk-First**
   - Integrate Whisper API for transcription
   - Add voice recording endpoint
   - Auto-generate essay outline from transcript

5. **Semantic Memory for Crisis Context**
   ```python
   # In handle_crisis():
   past_crises = await self.middleware.search_memories(
       profile_id,
       f"crisis resolution {crisis_type}",
       limit=3
   )
   # Inject past resolutions into Crisis Alchemy context
   ```

---

## File Dependencies

| File | Purpose |
|------|---------|
| `agents/agents/base.py` | BaseAgent class |
| `agents/agents/mixins.py` | MiddlewareIntegrationMixin |
| `config.py` | Settings, AutonomyLevel |
| `tools/database.py` | Supabase operations |
| `tools/cri.py` | compute_eds function |
| `graphs/crisis_alchemy.py` | LangGraph crisis protocol |

---

*Document generated: Platform Discovery Phase 4*
*Execution Agent Version: v10.0 Framework / Middleware v8*
*Status: Production-ready with enhancement opportunities*
