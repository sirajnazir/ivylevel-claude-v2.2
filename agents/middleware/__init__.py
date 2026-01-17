"""
Middleware Stack - v5.4 True Autonomous Agents

Central integration layer for Critical 15 Patterns.
Provides single-point integration for existing agents.

Usage (4 lines in existing agent):

```python
from middleware import MiddlewareStack

async def process(self, profile_id: str, **kwargs):
    middleware = MiddlewareStack(self.supabase)
    async with middleware.wrap_agent("my_agent", profile_id) as ctx:
        # ... existing agent code uses ctx.student, ctx.temporal ...
        result = await self._do_work(ctx)
        return middleware.finalize(result)
```
"""

from .stack import (
    MiddlewareStack,
    AgentContext,
    create_middleware,
)

__all__ = [
    "MiddlewareStack",
    "AgentContext",
    "create_middleware",
]
