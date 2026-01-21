# Critical 15 Patterns Test Suite v2
## Corrected to Match Actual Implementation API

**Version:** 2.0
**Status:** API-Aligned

---

## Key Fixes Applied

### 1. Memory Pattern (B1)
- Changed `conversation_turns` → `conversation_buffer`
- Fixed WorkingMemory field references

### 2. Governance Pattern (G1)
- Changed `DecisionLevel.ESCALATE` → `DecisionLevel.HUMAN_REVIEW`
- Updated enum value expectations

### 3. Intelligence Pattern (A12)
- Changed `PrioritizedItem.priority_level` → `PrioritizedItem.priority`
- Updated prioritization output fields

### 4. Observability Pattern (J2)
- Changed `record_llm_call(metrics_id, model, tokens, latency_ms)` →
         `record_llm_call(metrics_id, tokens_input, tokens_output)`
- Fixed API signature

### 5. Middleware Stack
- Fixed import path for WorkingMemory
- Added error handling for optional dependencies

---

## Test Structure

```
tests_v2/
├── conftest.py                    # Shared fixtures (18)
├── pytest.ini                     # Pytest configuration
├── agents/
│   ├── patterns/                  # Pattern tests
│   │   ├── test_context.py        # C2, C4, C6 (20 tests)
│   │   ├── test_memory.py         # B1, B7 (14 tests)
│   │   ├── test_intelligence.py   # A12, I3 USP (18 tests)
│   │   ├── test_governance.py     # G1, G3 (18 tests)
│   │   ├── test_safety.py         # E6 CRITICAL (16 tests)
│   │   ├── test_resilience.py     # H1 (18 tests)
│   │   ├── test_observability.py  # J2 (10 tests)
│   │   └── test_middleware.py     # Stack (14 tests)
│   │
│   └── integration/               # Integration tests
│       ├── test_non_breaking.py   # Import tests (20 tests)
│       └── test_performance.py    # Benchmarks (8 tests)
```

---

## Run Commands

```bash
# 1. Run all tests
pytest tests_v2/ -v

# 2. Run pattern tests only
pytest tests_v2/agents/patterns/ -v

# 3. Run integration tests only
pytest tests_v2/agents/integration/ -v

# 4. Run specific pattern
pytest tests_v2/agents/patterns/test_safety.py -v

# 5. Run with coverage
pytest tests_v2/ --cov=agents --cov-report=html
```

---

## Expected Results

With corrected API signatures, expect **>90% pass rate**:

| Category | Tests | Expected Pass |
|----------|-------|---------------|
| Context | 20 | 95% |
| Memory | 14 | 90% |
| Intelligence (USP) | 18 | 95% |
| Governance | 18 | 95% |
| Safety (CRITICAL) | 16 | 100% |
| Resilience | 18 | 90% |
| Observability | 10 | 90% |
| Middleware | 14 | 85% |
| Integration | 28 | 95% |
| **Total** | **156** | **>90%** |

---

## Key Test Validations

### Safety Tests (Must Pass 100%)
- Self-harm detection
- Suicide mention detection
- Abuse signal detection
- Guarantee language blocking
- Diagnosis language blocking

### USP Tests (Prioritization & Goal Monitoring)
- Urgency-based prioritization
- Importance scoring by category
- Student energy matching
- Goal progress tracking
- Alert generation

### Non-Breaking Tests
- All modules importable
- No circular dependencies
- Middleware purely additive
- Existing agents intact

---

## Notes

1. Tests are written to be **flexible** - they check for presence of attributes/methods rather than exact values where implementation may vary

2. **Async tests** use `@pytest.mark.asyncio` decorator

3. **Mock fixtures** in conftest.py provide Supabase, Redis, and Langfuse mocks

4. **Performance tests** verify <100ms overhead for middleware operations
