# Phase 3 Implementation Specs - AWAITING APPROVAL

## Generated Specs

| Week | Focus | Spec File | Patterns |
|------|-------|-----------|----------|
| 1 | Memory | `PHASE3_WEEK1_MEMORY_SPEC.md` | B3, B4, B5, B6 |
| 2 | Tools | `PHASE3_WEEK2_TOOLS_SPEC.md` | D1, D2, D3, D4, D7 |
| 3 | Learning | `PHASE3_WEEK3_LEARNING_SPEC.md` | I1, I2, I3, I5 |
| 4 | Advanced | `PHASE3_WEEK4_ADVANCED_SPEC.md` | A5, A12, F5, F6 |
| 5 | Observability | `PHASE3_WEEK5_OBSERVABILITY_SPEC.md` | J2, J5, K4 |

## 3P System Decisions

### Using Existing Systems (No New Vendors)

| System | Purpose | Status |
|--------|---------|--------|
| **Supabase** | All storage, pgvector for semantic memory | ✅ Already in use |
| **Redis** | Caching, real-time state | ✅ Already in use |
| **OpenAI** | LLM, embeddings, moderation | ✅ Already in use |
| **Langfuse** | Observability, traces, metrics | ✅ Already in use |
| **Guardrails AI** | Safety validation, PII | ✅ Already in use |
| **Pydantic** | Schema validation | ✅ Already in use |
| **Tenacity** | Retry logic | ✅ Already in use |

### New Dependency (Minimal)

| System | Purpose | Why |
|--------|---------|-----|
| **tiktoken** | Token counting | Official OpenAI library, lightweight, needed for cost tracking |

### Rejected Alternatives

| System | Reason for Rejection |
|--------|---------------------|
| **Pinecone** | Supabase pgvector sufficient for <1M vectors, no new vendor |
| **Weaviate/Chroma** | Same as above |
| **External PII service** | Guardrails AI + regex sufficient |

## Key Architecture Decisions

1. **Supabase pgvector** for semantic memory instead of Pinecone
   - Single source of truth
   - ACID transactions with metadata
   - Built-in row-level security
   - Already have Supabase infrastructure

2. **tiktoken** for token counting
   - Required for accurate cost tracking
   - Official OpenAI library
   - Very lightweight (~1MB)

3. **Defense-in-depth for safety**
   - OpenAI Moderation API (free) for harmful content
   - Guardrails AI for custom rules
   - Regex for deterministic PII

4. **Hierarchical stack inheritance**
   - MiddlewareStackV9 extends V8
   - No modifications to existing files
   - All patterns additive

## What Each Spec Contains

Each spec includes:
- Pattern purpose and use case
- 3P system choice with justification
- Full Python interface (classes, methods, types)
- Supabase database schema (where needed)
- Complete test file with pytest fixtures
- Implementation checklist

## Review Checklist

Please review and confirm:

- [ ] **Week 1 (Memory)**: Supabase pgvector approach acceptable?
- [ ] **Week 2 (Tools)**: Tool registry design meets needs?
- [ ] **Week 3 (Learning)**: Feedback/personalization scope correct?
- [ ] **Week 4 (Safety)**: Moderation categories appropriate for edu context?
- [ ] **Week 5 (Observability)**: Cost tracking granularity sufficient?
- [ ] **New dependency**: tiktoken addition approved?
- [ ] **Implementation order**: Week 1 → 2 → 3 → 4 → 5 acceptable?

## Next Steps (After Approval)

1. Add `tiktoken` to requirements.txt
2. Create database migrations for new tables
3. Implement patterns week by week
4. Run tests after each pattern
5. Create `stack_v9.py` integrating all patterns
6. Update agent mixin for V9 support

---

**Status: AWAITING USER APPROVAL**

*No implementation will proceed until specs are reviewed and approved.*
