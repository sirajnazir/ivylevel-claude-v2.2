"""
Request Logging - Log requests for observability.

Pattern: J2
3P: Langfuse (optional), Supabase (fallback)
Lines: ~100 (thin wrapper)

Features:
- Log requests with metadata
- Track latency
- Error tracking
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


class RequestLog(BaseModel):
    """A logged request."""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: Optional[str] = None
    request_type: str = "unknown"
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    latency_ms: float = 0
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RequestLogger:
    """
    Logs requests for observability.

    Pattern J2: Request Logging
    3P: Langfuse (optional), Supabase (fallback)

    Thin wrapper - delegates to Langfuse or Supabase for persistence.
    """

    TABLE = "phase3_request_logs"

    def __init__(
        self,
        langfuse_client=None,
        supabase_client=None,
    ):
        self.langfuse = langfuse_client
        self.supabase = supabase_client
        self._initialized = langfuse_client is not None or supabase_client is not None
        self._in_memory_logs: List[RequestLog] = []  # Fallback

    @property
    def is_available(self) -> bool:
        return True  # Always available (in-memory fallback)

    async def log(
        self,
        profile_id: Optional[str] = None,
        request_type: str = "unknown",
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RequestLog:
        """Log a request."""
        log = RequestLog(
            profile_id=profile_id,
            request_type=request_type,
            input_data=input_data,
            output_data=output_data,
            latency_ms=latency_ms,
            success=success,
            error=error,
            metadata=metadata or {},
        )

        # Try Langfuse first
        if self.langfuse:
            try:
                self.langfuse.trace(
                    name=request_type,
                    user_id=profile_id,
                    input=input_data,
                    output=output_data,
                    metadata={
                        "latency_ms": latency_ms,
                        "success": success,
                        "error": error,
                        **(metadata or {}),
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to log to Langfuse: {e}")

        # Try Supabase
        if self.supabase:
            try:
                self.supabase.table(self.TABLE).insert({
                    "request_id": log.request_id,
                    "profile_id": profile_id,
                    "request_type": request_type,
                    "input_data": input_data,
                    "output_data": output_data,
                    "latency_ms": latency_ms,
                    "success": success,
                    "error": error,
                    "metadata": metadata or {},
                    "created_at": log.created_at.isoformat(),
                }).execute()
            except Exception as e:
                logger.warning(f"Failed to log to Supabase: {e}")

        # Always store in memory as fallback
        self._in_memory_logs.append(log)

        # Keep memory bounded
        if len(self._in_memory_logs) > 1000:
            self._in_memory_logs = self._in_memory_logs[-500:]

        return log

    async def log_error(
        self,
        profile_id: Optional[str] = None,
        request_type: str = "unknown",
        error: str = "",
        input_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RequestLog:
        """Log an error request."""
        return await self.log(
            profile_id=profile_id,
            request_type=request_type,
            input_data=input_data,
            success=False,
            error=error,
            metadata=metadata,
        )

    async def get_recent(
        self,
        profile_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[RequestLog]:
        """Get recent logs (from memory)."""
        logs = self._in_memory_logs

        if profile_id:
            logs = [l for l in logs if l.profile_id == profile_id]

        return logs[-limit:]

    async def get_stats(
        self,
        profile_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get basic stats from in-memory logs."""
        logs = self._in_memory_logs

        if profile_id:
            logs = [l for l in logs if l.profile_id == profile_id]

        if not logs:
            return {
                "total_requests": 0,
                "success_rate": 0,
                "avg_latency_ms": 0,
            }

        successes = sum(1 for l in logs if l.success)
        latencies = [l.latency_ms for l in logs if l.latency_ms > 0]

        return {
            "total_requests": len(logs),
            "success_rate": successes / len(logs) if logs else 0,
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "request_types": list(set(l.request_type for l in logs)),
        }

    def clear_memory(self) -> None:
        """Clear in-memory logs."""
        self._in_memory_logs.clear()
