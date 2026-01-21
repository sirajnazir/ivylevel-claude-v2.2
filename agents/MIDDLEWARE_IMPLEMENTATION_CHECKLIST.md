# Middleware v8 Implementation Checklist

**Status:** Ready for Implementation
**Generated:** 2025-01-17

---

## Pre-Flight Verification

All verified working:

- [x] `middleware/__init__.py` exports v8 as default
- [x] `MiddlewareStackV8` import works
- [x] `SystemContextProvider` singleton fix applied
- [x] `SystemContextProvider.context` property fix applied
- [x] `get_feature_flag` method fix applied
- [x] `agents/mixins/` directory created
- [x] `agents/mixins/__init__.py` created
- [x] `agents/mixins/middleware_mixin.py` created and importable

---

## Implementation Priority Matrix

### Tier 1: P0 Critical (Week 1)

| Agent | File | Current | Target | Effort |
|-------|------|---------|--------|--------|
| ExecutionAgent | `agents/execution.py` | None | Full v8 | Medium |
| ExtracurricularsAgent | `agents/extracurriculars.py` | None | Full v8 | Medium |

### Tier 2: P1 High (Week 2)

| Agent | File | Current | Target | Effort |
|-------|------|---------|--------|--------|
| AwardsAgent | `agents/awards.py` | None | Full v8 | Medium |
| ProgramsAgent | `agents/programs.py` | None | Full v8 | Medium |

### Tier 3: P2 Medium (Week 3)

| Agent | File | Current | Target | Effort |
|-------|------|---------|--------|--------|
| AssessmentAgent | `agents/assessment.py` | None | Full v8 | Medium |
| ExecutionChatAgent | `agents/execution_chat.py` | None | Full v8 | Medium |
| NarrativeSynthesisAgent | `agents/narrative_synthesis.py` | None | Full v8 | Medium |

### Tier 4: P3 Enhancement (Week 4)

| Agent | File | Current | Target | Effort |
|-------|------|---------|--------|--------|
| GamePlanAgent | `agents/gameplan.py` | Basic | Full v8 | Low (upgrade) |
| ReActAgent | `agents/core/react_base.py` | None | Selective v8 | Low |
| BaseAgent | `agents/base.py` | None | Mixin integration | Low |

---

## Per-Agent Integration Steps

For each agent, follow these steps:

### Step 1: Add Import (1 line)

```python
from .mixins import MiddlewareIntegrationMixin
```

### Step 2: Update Class Definition (1 line change)

```python
# Before
class MyAgent(BaseAgent):

# After
class MyAgent(BaseAgent, MiddlewareIntegrationMixin):
```

### Step 3: Initialize Middleware in `__init__` (1 line)

```python
def __init__(self):
    super().__init__(name="MyAgent", autonomy_level=AutonomyLevel.MEDIUM)
    # ... existing init ...

    # ADD THIS:
    self.init_middleware(supabase_client=self.db, llm_client=self.llm)
```

### Step 4: Wrap `process` Method

```python
async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
    session_id = kwargs.get("session_id") or f"agent_{profile_id}"

    # Start reasoning trace
    trace_id = self.start_reasoning_trace(profile_id, session_id, str(kwargs))

    try:
        async with self.with_middleware_context(profile_id, session_id, "task_type") as ctx:
            self.add_thought(trace_id, "Starting processing")

            # ... existing logic ...
            result = await self._do_work()

            self.add_action(trace_id, "completed_work")

            # Quality check (optional)
            quality = await self.score_quality(str(result))
            if quality:
                result["_quality_score"] = quality.overall_score

            # Finalize with middleware
            result = self.middleware_finalize(result, "output_type")

            # Audit
            await self.audit_action("process", "profile", profile_id)

            await self.end_reasoning_trace(trace_id, success=True)
            return result

    except Exception as e:
        await self.end_reasoning_trace(trace_id, error=str(e), success=False)
        raise
```

---

## Agent-Specific Notes

### ExecutionAgent

```python
# File: agents/execution.py
# Key methods to wrap: scaffold_project, handle_crisis, detect_blockers

# Special considerations:
# - Crisis handling should use retry logic (execute_with_retry)
# - Project creation should use atomic operations
# - EDS computation should record metrics

async def scaffold_project(self, profile_id: str, project_data: Dict) -> Dict[str, Any]:
    # Use retry for database operations
    created_project = await self.execute_with_retry(
        create_project, max_retries=3, project=project
    )

    # Record metric
    self.record_metric("project_created", 1, tags={"type": project_data.get("type")})
```

### ExtracurricularsAgent

```python
# File: agents/extracurriculars.py
# Key considerations:
# - Quality scoring on recommendations is important
# - Coherence checking across multiple EC suggestions
# - Session context for conversation continuity

async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
    # Get session context for conversation continuity
    session = await self.get_session(session_id, profile_id)

    # ... generate recommendations ...

    # Check coherence across recommendations
    if len(recommendations) > 1:
        coherence = await self.check_coherence([r["description"] for r in recommendations])
        if coherence and not coherence.is_coherent:
            # Re-generate with coherence feedback
            pass
```

### AwardsAgent

```python
# File: agents/awards.py
# Key considerations:
# - Quality scoring on match results
# - Audit trail for award recommendations (compliance)
# - Use fallback if award database is unavailable

async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
    # Use fallback for award lookup
    awards = await self.call_with_fallback(
        "awards_db",
        self._lookup_awards,
        profile_id
    )

    # Audit the recommendation (compliance requirement)
    await self.audit_action(
        action="recommend_awards",
        resource_type="awards",
        resource_id=None,
        details={"count": len(awards), "top_award": awards[0]["name"] if awards else None},
    )
```

### GamePlanAgent (Upgrade from Basic)

```python
# File: agents/gameplan.py
# Current: Uses basic middleware
# Target: Upgrade to full v8 with mixin

# Change the import
from .mixins import MiddlewareIntegrationMixin

# Change class definition
class GamePlanAgent(MiddlewareIntegrationMixin):  # Add mixin

# In __init__, replace:
# self.middleware = create_middleware(self.db) if MIDDLEWARE_AVAILABLE else None
# With:
self.init_middleware(supabase_client=self.db, llm_client=self.llm)
```

---

## Patterns to Enable Per Agent

| Agent | J1 Traces | E4 Quality | H3 Retry | J3 Audit | C1 Session |
|-------|-----------|------------|----------|----------|------------|
| ExecutionAgent | Yes | Yes | Yes | Yes | Optional |
| ExtracurricularsAgent | Yes | Yes | No | Yes | Yes |
| AwardsAgent | Yes | Yes | Yes | Yes | Optional |
| ProgramsAgent | Yes | Yes | Yes | Yes | Optional |
| AssessmentAgent | Yes | Yes | No | Yes | Yes |
| ExecutionChatAgent | Yes | Yes | No | Yes | Yes |
| NarrativeSynthesisAgent | Yes | Yes | No | Yes | Optional |

---

## Testing Checklist

### Unit Tests

```bash
# Run existing tests to ensure no regressions
pytest agents/tests/ -v

# Run middleware tests
pytest agents/tests/phase2b/ -v
```

### Integration Tests

For each integrated agent:

```python
# Test 1: Middleware initializes
agent = ExecutionAgent()
assert agent.middleware is not None

# Test 2: Context works
async with agent.with_middleware_context("test-profile") as ctx:
    assert ctx is not None or agent.middleware is None

# Test 3: Traces work
trace_id = agent.start_reasoning_trace("profile", "session", "test")
if trace_id:
    agent.add_thought(trace_id, "Test thought")
    await agent.end_reasoning_trace(trace_id, success=True)

# Test 4: Quality scoring works
quality = await agent.score_quality("Test content")
# Should return QualityScore or None

# Test 5: Finalize works
result = agent.middleware_finalize({"success": True}, "general")
# Should have _validation key if middleware available
```

### Manual Smoke Tests

1. Run GamePlan generation - verify traces appear
2. Run Execution scaffolding - verify retry works on network error
3. Run EC recommendations - verify quality scores present
4. Check audit trail in Supabase - verify entries logged

---

## Rollback Plan

If issues arise:

1. **Per-Agent Rollback**: Remove mixin from class inheritance
2. **Global Disable**: Set `MIDDLEWARE_AVAILABLE = False` in mixin
3. **Selective Disable**: Use feature flags in SystemContext

```python
# Disable specific patterns
if not self.is_feature_enabled("enable_reasoning_traces"):
    trace_id = None  # Skip tracing
```

---

## Success Metrics

After integration:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Agents with traces | 10/10 | Langfuse dashboard |
| Audit trail coverage | 100% | Supabase `audit_log` table |
| Quality scores present | 80%+ outputs | Check `_quality_score` in responses |
| Zero middleware crashes | 0 | Error logs |
| Performance overhead | <5% | Response time monitoring |

---

## Files Modified Summary

| File | Change Type | Lines Changed |
|------|-------------|---------------|
| `middleware/__init__.py` | Modified | 5 |
| `middleware/stack_v8.py` | Fixed | 3 |
| `agents/mixins/__init__.py` | Created | 8 |
| `agents/mixins/middleware_mixin.py` | Created | 450 |
| `agents/execution.py` | To integrate | ~20 |
| `agents/extracurriculars.py` | To integrate | ~20 |
| `agents/awards.py` | To integrate | ~20 |
| `agents/programs.py` | To integrate | ~20 |
| `agents/assessment.py` | To integrate | ~20 |
| `agents/execution_chat.py` | To integrate | ~20 |
| `agents/narrative_synthesis.py` | To integrate | ~20 |
| `agents/gameplan.py` | To upgrade | ~10 |

---

## Command Reference

```bash
# Verify imports
python3 -c "from middleware import MiddlewareStack; print('OK')"
python3 -c "from agents.mixins import MiddlewareIntegrationMixin; print('OK')"

# Run tests
pytest agents/tests/phase2b/test_quality.py -v
pytest agents/tests/phase2b/test_context.py -v

# Check middleware export
python3 -c "from middleware import MiddlewareStack; print(type(MiddlewareStack))"
# Should print: <class 'type'> (MiddlewareStackV8)
```

---

**Ready for Implementation**

All prerequisites are complete. Integration can begin with ExecutionAgent as the first target.
