"""
Middleware Stack - v8.0 Full Integration (40 Patterns)

Central integration layer for all agentic patterns:
- Phase 1: Critical 15 Patterns
- Phase 2A: Important 10 Patterns
- Phase 2B: Enhancement 15 Patterns

Usage (4 lines in existing agent):

```python
from middleware import MiddlewareStack

async def process(self, profile_id: str, **kwargs):
    middleware = MiddlewareStack(self.supabase, self.redis, self.llm)
    async with middleware.wrap_agent("my_agent", profile_id) as ctx:
        # ... existing agent code uses ctx.student, ctx.temporal ...
        result = await self._do_work(ctx)
        return middleware.finalize(result)
```

v8.0 adds observability, quality scoring, graceful degradation, and more.
"""

# Import v8 stack with all 40 patterns
from .stack_v8 import (
    MiddlewareStackV8 as MiddlewareStack,
    create_middleware_v8 as create_middleware,
)

# Import AgentContext from base stack for backward compatibility
from .stack import AgentContext

# Also expose individual stack versions for explicit use
from .stack import MiddlewareStack as MiddlewareStackBasic
from .stack_v7 import MiddlewareStackV7
from .stack_v8 import MiddlewareStackV8

__all__ = [
    # Default exports (v8)
    "MiddlewareStack",
    "AgentContext",
    "create_middleware",
    # Explicit version exports
    "MiddlewareStackBasic",
    "MiddlewareStackV7",
    "MiddlewareStackV8",
]
