"""
Middleware Stack - v9.0 Complete Integration (50 Patterns)

Central integration layer for all agentic patterns:
- Phase 1: Critical 15 Patterns (v6.0)
- Phase 2A: Important 10 Patterns (v7.0)
- Phase 2B: Enhancement 15 Patterns (v8.0)
- Phase 3: Final 20 Patterns (v9.0)

Usage (4 lines in existing agent):

```python
from middleware import MiddlewareStack

async def process(self, profile_id: str, **kwargs):
    middleware = MiddlewareStack(self.supabase, self.redis, self.openai)
    async with middleware.wrap_agent("my_agent", profile_id) as ctx:
        # ... existing agent code uses ctx.student, ctx.temporal ...
        result = await self._do_work(ctx)
        return middleware.finalize(result)
```

v9.0 adds: semantic memory, tool orchestration, adaptive learning,
content moderation, PII detection, cost tracking, and more.
"""

# Import v9 stack with all 50 patterns
from .stack_v9 import MiddlewareStackV9 as MiddlewareStack

# Import AgentContext from base stack for backward compatibility
from .stack import AgentContext

# Also expose individual stack versions for explicit use
from .stack import MiddlewareStack as MiddlewareStackBasic
from .stack_v7 import MiddlewareStackV7
from .stack_v8 import MiddlewareStackV8
from .stack_v9 import MiddlewareStackV9

__all__ = [
    # Default exports (v9)
    "MiddlewareStack",
    "AgentContext",
    # Explicit version exports
    "MiddlewareStackBasic",
    "MiddlewareStackV7",
    "MiddlewareStackV8",
    "MiddlewareStackV9",
]
