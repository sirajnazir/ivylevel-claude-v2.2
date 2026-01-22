# Phase 3 v9.0 - Truly Autonomous Multi-Agent Implementation

## Overview

MiddlewareStackV9 completes the IvyLevel agent infrastructure with **50 total patterns** enabling truly autonomous multi-agent orchestration.

```
v6.0 (Critical 15) → v7.0 (+10) → v8.0 (+15) → v9.0 (+20) = 50 Patterns
```

## Architecture

### Inheritance Chain
```
MiddlewareStackBasic (v6.0)
    └── MiddlewareStackV7 (v7.0)
            └── MiddlewareStackV8 (v8.0)
                    └── MiddlewareStackV9 (v9.0) ← CURRENT
```

### 3P-First Design Principle

Every pattern follows the **3P-First Thin Wrapper** approach:
- **<150 lines** per pattern implementation
- **Delegates to 3rd-party systems** for heavy lifting
- **Graceful degradation** when dependencies unavailable
- **No reinventing** what already exists

## Phase 3 Patterns (20 New)

### Memory Patterns (B3, B4, B5, B6)

| Pattern | Name | 3P System | Purpose |
|---------|------|-----------|---------|
| B3 | Semantic Memory | Supabase pgvector + OpenAI | Vector similarity search for context retrieval |
| B4 | Long-Term Memory | Supabase JSONB | Persistent key-value memory across sessions |
| B5 | Memory Extraction | OpenAI Function Calling | Extract facts/preferences from conversations |
| B6 | Memory Consolidation | OpenAI | Merge duplicates, prune low-importance |

**Usage:**
```python
# Store a memory
await middleware.remember(profile_id, "goal", "Get into MIT", importance=0.9)

# Recall specific memory
goal = await middleware.recall(profile_id, "goal")

# Semantic search
relevant = await middleware.search_memories(profile_id, "college applications")

# Extract from conversation
count = await middleware.extract_and_store_memories(profile_id, conversation_text)
```

### Tool Patterns (D1, D2, D3, D4, D7)

| Pattern | Name | 3P System | Purpose |
|---------|------|-----------|---------|
| D1 | Tool Registry | Supabase (optional) | Central registry for available tools |
| D2 | Tool Calling | OpenAI Function Calling | Execute tools from LLM responses |
| D3 | Schema Generation | Native Python | Generate OpenAI schemas from functions |
| D4 | Parallel Execution | asyncio | Execute multiple tools concurrently |
| D7 | Tool Chaining | Extends A9 | Chain tools with data flow between them |

**Usage:**
```python
# Register a tool
middleware.register_tool(
    name="search_colleges",
    description="Search for colleges by criteria",
    handler=search_colleges_func,
)

# Call a tool
result = await middleware.call_tool("search_colleges", {"state": "MA"})

# Parallel execution
results = await middleware.call_tools_parallel([
    {"name": "search_colleges", "arguments": {"state": "MA"}},
    {"name": "search_scholarships", "arguments": {"amount": 50000}},
])
```

### Learning Patterns (I1, I2, I3, I5)

| Pattern | Name | 3P System | Purpose |
|---------|------|-----------|---------|
| I1 | Feedback Loop | Supabase | Collect explicit/implicit user feedback |
| I2 | Behavior Adaptation | Supabase | Adapt agent behavior based on feedback |
| I3 | Pattern Recognition | Supabase | Recognize recurring user patterns |
| I5 | Preference Learning | Supabase + B4 | Learn and apply user preferences |

**Usage:**
```python
# Record feedback
await middleware.record_feedback(profile_id, "positive", context="essay help")

# Adapt behavior
await middleware.behavior_adapter.adapt(profile_id, "detail_level", "high")

# Apply learned preferences to prompts
adapted_prompt = await middleware.adapt_prompt(profile_id, base_system_prompt)
```

### Reasoning Patterns (A5, A12)

| Pattern | Name | 3P System | Purpose |
|---------|------|-----------|---------|
| A5 | Adaptive Prompting | Combines I2, I5, B4 | Dynamically adapt prompts to user |
| A12 | Metacognition | OpenAI | Self-reflection on reasoning quality |

**Usage:**
```python
# Analyze response quality
analysis = await middleware.metacognitor.analyze(request, response)
if analysis.overall_confidence < 0.5:
    # Ask for clarification or try different approach
    pass

# Check for uncertainty
markers = middleware.metacognitor.check_for_uncertainty_markers(response)
```

### Safety Patterns (F5, F6)

| Pattern | Name | 3P System | Purpose |
|---------|------|-----------|---------|
| F5 | Content Moderation | OpenAI Moderation API (FREE) | Check for policy violations |
| F6 | PII Detection | Microsoft Presidio | Detect and redact personal information |

**Usage:**
```python
# Check content safety
is_safe = await middleware.check_content_safety(user_input)

# Redact PII before logging
safe_text = await middleware.redact_pii(user_input)
```

### Observability Patterns (J2, J5, K4)

| Pattern | Name | 3P System | Purpose |
|---------|------|-----------|---------|
| J2 | Request Logging | Langfuse + Supabase | Log all requests with metadata |
| J5 | Cost Tracking | tiktoken | Track token usage and costs |
| K4 | Context Compression | tiktoken + OpenAI | Compress long contexts to fit limits |

**Usage:**
```python
# Track costs
await middleware.track_cost("gpt-4o", input_tokens=500, output_tokens=200)
costs = middleware.get_session_costs()

# Compress context
compressed = await middleware.compress_context(long_text, max_tokens=4000)

# Count tokens
tokens = middleware.count_tokens(text)
```

## Database Schema

### New Tables (Phase 3)

```sql
-- B3: Semantic Memory
phase3_semantic_memories (
    id, profile_id, content, embedding vector(1536),
    memory_type, importance, metadata, created_at
)

-- B4: Long-Term Memory
phase3_longterm_memories (
    id, profile_id, memory_key, memory_value JSONB,
    memory_type, importance, confidence, access_count
)

-- I1: Feedback
phase3_feedback (
    id, profile_id, feedback_type, sentiment, score,
    context, message, metadata
)

-- I2/I3: Behavior & Patterns
phase3_behavior_adaptations (profile_id, behavior_key, behavior_value, confidence)
phase3_recognized_patterns (profile_id, pattern_type, pattern_value, frequency)

-- D1: Tool Registry
phase3_tool_registry (tool_name, tool_schema JSONB, category, is_active)

-- J5: Cost Tracking
phase3_cost_records (model, input_tokens, output_tokens, cost_usd)
```

### Vector Search Function

```sql
SELECT * FROM match_semantic_memories(
    query_embedding := $embedding,
    match_profile_id := 'user-123',
    match_count := 5,
    match_threshold := 0.7
);
```

## Pattern Availability

With full configuration (all clients provided):
```python
middleware = MiddlewareStackV9(
    supabase_client=supabase,
    redis_client=redis,
    openai_client=openai,
    langfuse_client=langfuse,
)

# Check what's available
summary = middleware.get_phase3_summary()
# {
#   "phase": "3",
#   "version": "9.0",
#   "total_patterns": 20,
#   "available_patterns": 20,
#   ...
# }
```

### Graceful Degradation

All patterns handle missing dependencies:

| Missing | Impact |
|---------|--------|
| Supabase | Memory persists in-memory only, no long-term storage |
| OpenAI | No embeddings, extraction, moderation, metacognition |
| Redis | Working memory falls back to in-memory dict |
| Langfuse | Logging falls back to Supabase or in-memory |
| Presidio | PII detection unavailable, returns original text |

## Integration Example

### Full Autonomous Agent

```python
from middleware import MiddlewareStack

class AutonomousAdvisor:
    def __init__(self, supabase, openai, langfuse):
        self.middleware = MiddlewareStack(
            supabase_client=supabase,
            openai_client=openai,
            langfuse_client=langfuse,
        )

        # Register tools
        self.middleware.register_tool(
            name="search_colleges",
            description="Search colleges by criteria",
            handler=self.search_colleges,
        )

    async def process(self, profile_id: str, message: str):
        # Safety check
        if not await self.middleware.check_content_safety(message):
            return "I can't help with that request."

        # Redact PII for logging
        safe_message = await self.middleware.redact_pii(message)

        # Get adapted system prompt
        system_prompt = await self.middleware.adapt_prompt(
            profile_id,
            "You are a college admissions advisor...",
        )

        # Search relevant memories
        memories = await self.middleware.search_memories(profile_id, message)

        # Generate response with tools
        response = await self.generate_with_tools(
            system_prompt, message, memories
        )

        # Extract and store new memories
        await self.middleware.extract_and_store_memories(profile_id, message)

        # Track costs
        await self.middleware.track_cost(
            "gpt-4o",
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            profile_id=profile_id,
        )

        # Metacognitive analysis
        analysis = await self.middleware.metacognitor.analyze(message, response.text)
        if self.middleware.metacognitor.should_ask_for_clarification(analysis):
            # Adjust response to ask for clarification
            pass

        return response.text
```

## Test Coverage

```
Phase 3 Tests: 196 passed, 3 skipped
├── Memory Tests: 65 tests
├── Tool Tests: 39 tests
├── Safety/Observability Tests: 34 tests
├── Learning/Reasoning Tests: 39 tests
└── Stack Integration Tests: 19 tests
```

## Dependencies

```
# requirements.txt additions
tiktoken>=0.5.0          # Token counting (J5, K4)
presidio-analyzer>=2.2.0  # PII detection (F6)
presidio-anonymizer>=2.2.0
```

## Migration Path

1. **Update requirements**: `pip install -r requirements.txt`
2. **Run migration**: `supabase db push` (038_phase3_v9.0_tables.sql)
3. **Update imports**: `from middleware import MiddlewareStack` (now v9)
4. **Add OpenAI client**: Pass to middleware for embeddings/moderation

## File Structure

```
middleware/
├── __init__.py              # Exports MiddlewareStackV9 as default
├── stack_v9.py              # Complete 50-pattern stack
├── memory/
│   ├── semantic_v9.py       # B3: Semantic Memory
│   ├── longterm_v9.py       # B4: Long-Term Memory
│   ├── extraction_v9.py     # B5: Memory Extraction
│   └── consolidation_v9.py  # B6: Memory Consolidation
├── tools/
│   ├── registry_v9.py       # D1: Tool Registry
│   ├── calling_v9.py        # D2: Tool Calling
│   ├── schema_v9.py         # D3: Schema Generation
│   ├── parallel_v9.py       # D4: Parallel Execution
│   └── chaining_v9.py       # D7: Tool Chaining
├── learning/
│   ├── feedback_v9.py       # I1: Feedback Loop
│   ├── adaptation_v9.py     # I2: Behavior Adaptation
│   ├── patterns_v9.py       # I3: Pattern Recognition
│   └── preferences_v9.py    # I5: Preference Learning
├── reasoning/
│   ├── adaptive_v9.py       # A5: Adaptive Prompting
│   └── metacognition_v9.py  # A12: Metacognition
├── safety/
│   ├── moderation_v9.py     # F5: Content Moderation
│   └── pii_v9.py            # F6: PII Detection
├── observability/
│   ├── logging_v9.py        # J2: Request Logging
│   └── cost_v9.py           # J5: Cost Tracking
└── optimization/
    └── compression_v9.py    # K4: Context Compression
```

## Next Steps: True Autonomous Agents

With v9.0 complete, the foundation is ready for:

1. **Multi-Agent Orchestration**: Agents can now share memory, coordinate tools, and learn from each other
2. **Autonomous Planning**: Combine A11 (Planning) with D7 (Tool Chaining) for complex task execution
3. **Self-Improvement**: I1-I5 patterns enable agents to improve based on feedback
4. **Safety Guardrails**: F5/F6 ensure safe operation in production

---

*Phase 3 v9.0 - Complete Autonomous Agent Infrastructure*
*196 tests passing | 50 patterns | 3P-first thin wrappers*
