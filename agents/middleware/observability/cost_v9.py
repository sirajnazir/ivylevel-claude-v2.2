"""
Cost Tracking - Track token usage and costs.

Pattern: J5
3P: tiktoken (token counting)
Lines: ~120 (thin wrapper)

Features:
- Count tokens accurately
- Track costs by model
- Session-level aggregation
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try to import tiktoken (optional dependency)
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not installed - token counting will use estimates")


class CostRecord(BaseModel):
    """A single cost record."""
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    input_cost: float = 0
    output_cost: float = 0
    total_cost: float = 0
    profile_id: Optional[str] = None
    request_type: str = "unknown"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CostTracker:
    """
    Tracks token usage and costs.

    Pattern J5: Cost Tracking
    3P: tiktoken (accurate token counting)

    Thin wrapper - uses tiktoken for counting, optional Supabase for persistence.
    """

    TABLE = "phase3_cost_records"

    # Cost per 1K tokens (as of 2024)
    MODEL_COSTS = {
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "text-embedding-3-small": {"input": 0.00002, "output": 0},
        "text-embedding-3-large": {"input": 0.00013, "output": 0},
    }

    # Model to tiktoken encoding mapping
    MODEL_ENCODINGS = {
        "gpt-4o": "o200k_base",
        "gpt-4o-mini": "o200k_base",
        "gpt-4-turbo": "cl100k_base",
        "gpt-4": "cl100k_base",
        "gpt-3.5-turbo": "cl100k_base",
        "text-embedding-3-small": "cl100k_base",
        "text-embedding-3-large": "cl100k_base",
    }

    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self._initialized = True  # Always available
        self._session_costs: List[CostRecord] = []
        self._encoders: Dict[str, Any] = {}

    @property
    def is_available(self) -> bool:
        return self._initialized

    def _get_encoder(self, model: str):
        """Get or create encoder for a model."""
        if not TIKTOKEN_AVAILABLE:
            return None

        if model not in self._encoders:
            encoding_name = self.MODEL_ENCODINGS.get(model, "cl100k_base")
            try:
                self._encoders[model] = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                logger.warning(f"Failed to get encoder for {model}: {e}")
                return None

        return self._encoders.get(model)

    def count_tokens(
        self,
        text: str,
        model: str = "gpt-4o",
    ) -> int:
        """Count tokens in text."""
        if not text:
            return 0

        encoder = self._get_encoder(model)
        if encoder:
            return len(encoder.encode(text))

        # Fallback: rough estimate (4 chars per token)
        return len(text) // 4

    def count_message_tokens(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
    ) -> int:
        """Count tokens in a message list."""
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            total += self.count_tokens(content, model)
            total += 4  # Message overhead

        total += 2  # Conversation overhead
        return total

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str = "gpt-4o",
    ) -> Dict[str, float]:
        """Calculate cost for token usage."""
        costs = self.MODEL_COSTS.get(model, {"input": 0.01, "output": 0.03})

        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]

        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": input_cost + output_cost,
        }

    async def track(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        profile_id: Optional[str] = None,
        request_type: str = "unknown",
    ) -> CostRecord:
        """Track a cost record."""
        costs = self.calculate_cost(input_tokens, output_tokens, model)

        record = CostRecord(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            input_cost=costs["input_cost"],
            output_cost=costs["output_cost"],
            total_cost=costs["total_cost"],
            profile_id=profile_id,
            request_type=request_type,
        )

        # Store in session
        self._session_costs.append(record)

        # Persist to Supabase if available
        if self.supabase:
            try:
                self.supabase.table(self.TABLE).insert({
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "input_cost": costs["input_cost"],
                    "output_cost": costs["output_cost"],
                    "total_cost": costs["total_cost"],
                    "profile_id": profile_id,
                    "request_type": request_type,
                    "created_at": record.created_at.isoformat(),
                }).execute()
            except Exception as e:
                logger.warning(f"Failed to persist cost record: {e}")

        return record

    async def track_from_response(
        self,
        response: Any,
        model: str,
        profile_id: Optional[str] = None,
        request_type: str = "unknown",
    ) -> CostRecord:
        """Track cost from OpenAI response object."""
        usage = getattr(response, "usage", None)
        if usage:
            return await self.track(
                model=model,
                input_tokens=getattr(usage, "prompt_tokens", 0),
                output_tokens=getattr(usage, "completion_tokens", 0),
                profile_id=profile_id,
                request_type=request_type,
            )
        return CostRecord(model=model)

    def get_session_total(self) -> Dict[str, Any]:
        """Get total costs for current session."""
        total_input = sum(r.input_tokens for r in self._session_costs)
        total_output = sum(r.output_tokens for r in self._session_costs)
        total_cost = sum(r.total_cost for r in self._session_costs)

        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "total_cost": total_cost,
            "request_count": len(self._session_costs),
        }

    def clear_session(self) -> None:
        """Clear session cost tracking."""
        self._session_costs.clear()
