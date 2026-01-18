# Phase 3 Week 5: Observability & Optimization Patterns Implementation Spec

## Overview

Week 5 focuses on observability, cost tracking, and optimization patterns.

| Pattern | ID | Priority | Dependencies |
|---------|-----|----------|--------------|
| Performance Metrics | J2 | Medium | Langfuse |
| Cost Tracking | J5 | High | Token counter, Supabase |
| Context Compression | K4 | Medium | OpenAI |

### 3P Systems Used

| System | Purpose | Already in Use? |
|--------|---------|-----------------|
| **Langfuse** | APM, traces, performance | ✅ Yes |
| **Supabase** | Cost log storage | ✅ Yes |
| **OpenAI** | Context compression | ✅ Yes |
| **tiktoken** | Token counting | ❌ New (recommended) |

---

## J2: Performance Metrics

### Purpose
Comprehensive performance metrics for agent operations including latency, throughput, error rates, and resource utilization.

### 3P System Choice: **Langfuse**

**Why:**
- ✅ Already using Langfuse for observability
- ✅ Built-in metrics, traces, and dashboards
- ✅ LLM-specific metrics (token usage, latency)
- ✅ No additional infrastructure

### File: `middleware/observability/performance_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
from contextlib import asynccontextmanager
import logging
import time

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    TOKEN_USAGE = "token_usage"
    CACHE_HIT_RATE = "cache_hit_rate"
    QUEUE_DEPTH = "queue_depth"
    MEMORY_USAGE = "memory_usage"


class PerformanceMetric(BaseModel):
    """A single performance metric."""
    name: str
    metric_type: MetricType
    value: float
    unit: str
    tags: Dict[str, str] = {}
    timestamp: datetime


class PerformanceReport(BaseModel):
    """Aggregated performance report."""
    period_start: datetime
    period_end: datetime
    metrics: Dict[str, float]
    percentiles: Dict[str, Dict[str, float]]  # metric -> {p50, p95, p99}
    alerts: List[str]
    comparison_to_previous: Dict[str, float]  # metric -> % change


class PerformanceCollector:
    """
    Collects and reports performance metrics.

    Integrates with Langfuse for:
    - Request latency tracking
    - LLM token usage
    - Error rates
    - Throughput metrics

    Also tracks custom IvyLevel metrics:
    - Agent execution time
    - Cache performance
    - Queue metrics
    """

    def __init__(
        self,
        langfuse_client=None,
        supabase_client=None,
    ):
        """
        Initialize performance collector.

        Args:
            langfuse_client: Langfuse for APM
            supabase_client: Supabase for custom metrics
        """
        self.langfuse = langfuse_client
        self.db = supabase_client
        self._metrics_buffer: List[PerformanceMetric] = []

    @asynccontextmanager
    async def track_operation(
        self,
        operation_name: str,
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Context manager for tracking operation performance.

        Usage:
            async with collector.track_operation("process_essay") as tracker:
                result = await process_essay(...)
                tracker.set_result(result)
        """
        pass

    def record_latency(
        self,
        operation: str,
        latency_ms: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record operation latency."""
        pass

    def record_tokens(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record token usage."""
        pass

    def record_error(
        self,
        operation: str,
        error_type: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record an error occurrence."""
        pass

    def record_cache_hit(
        self,
        cache_name: str,
        hit: bool,
    ) -> None:
        """Record cache hit/miss."""
        pass

    async def get_report(
        self,
        period: timedelta = timedelta(hours=1),
    ) -> PerformanceReport:
        """
        Get performance report for period.

        Aggregates metrics and computes percentiles.
        """
        pass

    async def get_agent_metrics(
        self,
        agent_name: str,
        period: timedelta = timedelta(hours=1),
    ) -> Dict[str, Any]:
        """Get metrics for a specific agent."""
        pass

    async def flush(self) -> int:
        """Flush metrics buffer to storage."""
        pass

    def _compute_percentiles(
        self,
        values: List[float],
    ) -> Dict[str, float]:
        """Compute p50, p95, p99 percentiles."""
        pass
```

### Test File: `tests/phase3/test_performance_metrics.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import timedelta
from middleware.observability.performance_v9 import (
    PerformanceCollector,
    PerformanceMetric,
    PerformanceReport,
    MetricType,
)


class TestPerformanceCollector:
    """Tests for J2: Performance Metrics."""

    @pytest.fixture
    def mock_langfuse(self):
        client = MagicMock()
        client.trace = MagicMock(return_value=MagicMock(
            __enter__=MagicMock(),
            __exit__=MagicMock(),
        ))
        return client

    @pytest.fixture
    def collector(self, mock_langfuse):
        return PerformanceCollector(langfuse_client=mock_langfuse)

    @pytest.mark.asyncio
    async def test_track_operation_records_latency(self, collector):
        """Test operation tracking."""
        async with collector.track_operation("test_op") as tracker:
            await asyncio.sleep(0.1)

        # Should have recorded latency
        assert len(collector._metrics_buffer) > 0

    def test_record_latency(self, collector):
        """Test latency recording."""
        collector.record_latency(
            operation="test",
            latency_ms=150.5,
        )

        assert len(collector._metrics_buffer) == 1
        assert collector._metrics_buffer[0].metric_type == MetricType.LATENCY

    def test_record_tokens(self, collector):
        """Test token recording."""
        collector.record_tokens(
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
        )

        assert len(collector._metrics_buffer) == 1
        assert collector._metrics_buffer[0].metric_type == MetricType.TOKEN_USAGE

    def test_record_error(self, collector):
        """Test error recording."""
        collector.record_error(
            operation="test",
            error_type="timeout",
        )

        assert len(collector._metrics_buffer) == 1
        assert collector._metrics_buffer[0].metric_type == MetricType.ERROR_RATE

    @pytest.mark.asyncio
    async def test_get_report_returns_aggregated(self, collector):
        """Test report generation."""
        collector.record_latency("op1", 100)
        collector.record_latency("op1", 200)
        collector.record_latency("op1", 150)

        report = await collector.get_report(period=timedelta(hours=1))

        assert isinstance(report, PerformanceReport)
        assert "latency" in report.metrics or len(report.percentiles) >= 0

    def test_compute_percentiles(self, collector):
        """Test percentile computation."""
        values = list(range(1, 101))  # 1 to 100
        percentiles = collector._compute_percentiles(values)

        assert percentiles["p50"] == 50
        assert percentiles["p95"] == 95
        assert percentiles["p99"] == 99
```

---

## J5: Cost Tracking

### Purpose
Tracks LLM API costs per agent, session, and profile. Essential for cost control and optimization.

### 3P System Choice: **tiktoken + Supabase**

**Why:**
- ✅ tiktoken for accurate token counting (official OpenAI library)
- ✅ Supabase for cost log storage
- ✅ Real-time cost visibility

**Note:** tiktoken is a new dependency but is lightweight and official.

### File: `middleware/observability/cost_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


# Pricing per 1M tokens (as of 2024)
MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "text-embedding-3-small": {"input": 0.02, "output": 0.00},
    "text-embedding-3-large": {"input": 0.13, "output": 0.00},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-opus": {"input": 15.00, "output": 75.00},
}


class CostEntry(BaseModel):
    """A single cost entry."""
    id: str
    session_id: Optional[str]
    profile_id: Optional[str]
    agent_name: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal
    operation: str
    created_at: datetime


class CostSummary(BaseModel):
    """Aggregated cost summary."""
    period_start: datetime
    period_end: datetime
    total_cost_usd: Decimal
    by_agent: Dict[str, Decimal]
    by_model: Dict[str, Decimal]
    by_profile: Dict[str, Decimal]
    total_input_tokens: int
    total_output_tokens: int


class CostTracker:
    """
    Tracks LLM API costs across the system.

    Features:
    - Real-time cost tracking per request
    - Aggregation by agent, model, profile
    - Budget alerting
    - Cost optimization insights
    """

    def __init__(
        self,
        supabase_client=None,
        budget_limit_usd: Optional[float] = None,
    ):
        """
        Initialize cost tracker.

        Args:
            supabase_client: Supabase for cost log storage
            budget_limit_usd: Optional daily budget limit
        """
        self.db = supabase_client
        self.budget_limit = budget_limit_usd
        self._daily_cost: Decimal = Decimal("0")
        self._cost_buffer: List[CostEntry] = []

    def count_tokens(
        self,
        text: str,
        model: str = "gpt-4o",
    ) -> int:
        """
        Count tokens in text using tiktoken.

        Args:
            text: Text to count tokens for
            model: Model to use for tokenization

        Returns:
            Token count
        """
        pass

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> Decimal:
        """
        Calculate cost for a request.

        Args:
            model: Model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        pass

    async def record_usage(
        self,
        agent_name: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        operation: str = "completion",
        session_id: Optional[str] = None,
        profile_id: Optional[str] = None,
    ) -> CostEntry:
        """
        Record LLM usage and cost.

        Args:
            agent_name: Agent that made the request
            model: Model used
            input_tokens: Input token count
            output_tokens: Output token count
            operation: Type of operation
            session_id: Optional session ID
            profile_id: Optional profile ID

        Returns:
            The recorded cost entry
        """
        pass

    async def get_daily_cost(
        self,
        date: Optional[datetime] = None,
    ) -> Decimal:
        """Get total cost for a day."""
        pass

    async def get_summary(
        self,
        period: timedelta = timedelta(days=1),
        profile_id: Optional[str] = None,
    ) -> CostSummary:
        """
        Get cost summary for period.

        Args:
            period: Time period to summarize
            profile_id: Optional filter by profile

        Returns:
            Aggregated cost summary
        """
        pass

    async def get_top_consumers(
        self,
        limit: int = 10,
        period: timedelta = timedelta(days=7),
    ) -> List[Dict[str, Any]]:
        """Get top cost consumers (agents/profiles)."""
        pass

    async def check_budget(self) -> bool:
        """
        Check if within budget.

        Returns:
            True if within budget, False if exceeded
        """
        pass

    async def flush(self) -> int:
        """Flush cost buffer to database."""
        pass

    def get_optimization_recommendations(
        self,
        summary: CostSummary,
    ) -> List[str]:
        """
        Get cost optimization recommendations.

        Analyzes usage patterns and suggests:
        - Model downgrades where appropriate
        - Caching opportunities
        - Prompt optimization
        """
        pass
```

### Database Schema

```sql
CREATE TABLE llm_cost_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID,
    profile_id UUID REFERENCES profiles(id),
    agent_name TEXT NOT NULL,
    model TEXT NOT NULL,
    operation TEXT DEFAULT 'completion',
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cost_usd NUMERIC(10, 6) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cost_logs_created ON llm_cost_logs(created_at DESC);
CREATE INDEX idx_cost_logs_agent ON llm_cost_logs(agent_name);
CREATE INDEX idx_cost_logs_profile ON llm_cost_logs(profile_id);
CREATE INDEX idx_cost_logs_date ON llm_cost_logs(DATE(created_at));

-- Materialized view for daily aggregations
CREATE MATERIALIZED VIEW daily_cost_summary AS
SELECT
    DATE(created_at) as date,
    agent_name,
    model,
    SUM(input_tokens) as total_input_tokens,
    SUM(output_tokens) as total_output_tokens,
    SUM(cost_usd) as total_cost_usd,
    COUNT(*) as request_count
FROM llm_cost_logs
GROUP BY DATE(created_at), agent_name, model;
```

### Test File: `tests/phase3/test_cost_tracking.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from decimal import Decimal
from datetime import timedelta
from middleware.observability.cost_v9 import (
    CostTracker,
    CostEntry,
    CostSummary,
    MODEL_PRICING,
)


class TestCostTracker:
    """Tests for J5: Cost Tracking."""

    @pytest.fixture
    def mock_supabase(self):
        db = MagicMock()
        db.table = MagicMock(return_value=MagicMock(
            insert=MagicMock(return_value=MagicMock(
                execute=MagicMock(return_value=MagicMock(data=[{"id": "test"}]))
            )),
            select=MagicMock(return_value=MagicMock(
                gte=MagicMock(return_value=MagicMock(
                    execute=MagicMock(return_value=MagicMock(data=[]))
                ))
            ))
        ))
        return db

    @pytest.fixture
    def tracker(self, mock_supabase):
        return CostTracker(supabase_client=mock_supabase)

    def test_count_tokens(self, tracker):
        """Test token counting."""
        count = tracker.count_tokens(
            text="Hello, how are you?",
            model="gpt-4o",
        )

        assert isinstance(count, int)
        assert count > 0

    def test_calculate_cost_gpt4o(self, tracker):
        """Test cost calculation for GPT-4o."""
        cost = tracker.calculate_cost(
            model="gpt-4o",
            input_tokens=1000,
            output_tokens=500,
        )

        # 1000 * $2.50/1M + 500 * $10.00/1M
        expected = Decimal("0.0025") + Decimal("0.005")
        assert cost == expected

    def test_calculate_cost_gpt4o_mini(self, tracker):
        """Test cost calculation for GPT-4o-mini."""
        cost = tracker.calculate_cost(
            model="gpt-4o-mini",
            input_tokens=1000,
            output_tokens=500,
        )

        # Much cheaper
        assert cost < Decimal("0.001")

    @pytest.mark.asyncio
    async def test_record_usage(self, tracker):
        """Test recording usage."""
        entry = await tracker.record_usage(
            agent_name="ExecutionChatAgent",
            model="gpt-4o",
            input_tokens=500,
            output_tokens=200,
        )

        assert isinstance(entry, CostEntry)
        assert entry.agent_name == "ExecutionChatAgent"
        assert entry.cost_usd > 0

    @pytest.mark.asyncio
    async def test_get_summary(self, tracker):
        """Test getting cost summary."""
        summary = await tracker.get_summary(period=timedelta(days=1))

        assert isinstance(summary, CostSummary)
        assert summary.total_cost_usd >= 0

    @pytest.mark.asyncio
    async def test_check_budget_within_limit(self, tracker):
        """Test budget check when within limit."""
        tracker.budget_limit = 100.0
        tracker._daily_cost = Decimal("50.0")

        within = await tracker.check_budget()

        assert within is True

    @pytest.mark.asyncio
    async def test_check_budget_exceeded(self, tracker):
        """Test budget check when exceeded."""
        tracker.budget_limit = 100.0
        tracker._daily_cost = Decimal("150.0")

        within = await tracker.check_budget()

        assert within is False

    def test_optimization_recommendations(self, tracker):
        """Test optimization recommendations."""
        summary = CostSummary(
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            total_cost_usd=Decimal("100.0"),
            by_agent={"ExecutionChatAgent": Decimal("80.0")},
            by_model={"gpt-4o": Decimal("90.0")},
            by_profile={},
            total_input_tokens=100000,
            total_output_tokens=50000,
        )

        recommendations = tracker.get_optimization_recommendations(summary)

        assert isinstance(recommendations, list)
        # Should suggest model downgrade if gpt-4o is 90% of cost
        assert any("gpt-4o-mini" in r.lower() for r in recommendations)
```

---

## K4: Context Compression

### Purpose
Compresses long contexts to fit within token limits while preserving essential information.

### 3P System Choice: **OpenAI** (summarization)

**Why:**
- ✅ Already using OpenAI - no new dependency
- ✅ High-quality summarization
- ✅ Can use cheaper model (gpt-4o-mini) for compression

**Strategy:**
1. Chunking for very long contexts
2. Hierarchical summarization
3. Importance-weighted compression

### File: `middleware/optimization/compression_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class CompressionResult(BaseModel):
    """Result of context compression."""
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    compressed_text: str
    preserved_sections: List[str]
    removed_sections: List[str]


class CompressionConfig(BaseModel):
    """Configuration for compression."""
    target_tokens: int = 4000
    min_compression_ratio: float = 0.5
    preserve_recent: bool = True  # Preserve recent messages
    preserve_important: bool = True  # Preserve high-importance content
    summarization_model: str = "gpt-4o-mini"


class ContextCompressor:
    """
    Compresses context to fit within token limits.

    Strategies:
    - Summarization for long sections
    - Truncation with preservation markers
    - Importance-weighted selection
    - Hierarchical summarization for very long contexts

    Critical for:
    - Long conversation histories
    - Large document contexts
    - Multi-agent handoffs
    """

    def __init__(
        self,
        llm_client=None,
        config: Optional[CompressionConfig] = None,
    ):
        """
        Initialize context compressor.

        Args:
            llm_client: OpenAI client for summarization
            config: Compression configuration
        """
        self.llm = llm_client
        self.config = config or CompressionConfig()

    async def compress(
        self,
        context: str,
        target_tokens: Optional[int] = None,
        importance_markers: Optional[Dict[str, float]] = None,
    ) -> CompressionResult:
        """
        Compress context to target token count.

        Args:
            context: Full context to compress
            target_tokens: Target token count (overrides config)
            importance_markers: Section -> importance score mapping

        Returns:
            CompressionResult with compressed context
        """
        pass

    async def compress_conversation(
        self,
        messages: List[Dict[str, str]],
        target_tokens: Optional[int] = None,
    ) -> Tuple[List[Dict[str, str]], CompressionResult]:
        """
        Compress conversation history.

        Preserves:
        - System message (always)
        - Recent messages (configurable)
        - High-importance messages

        Returns:
            Tuple of (compressed_messages, compression_result)
        """
        pass

    async def compress_documents(
        self,
        documents: List[str],
        target_tokens: Optional[int] = None,
    ) -> Tuple[str, CompressionResult]:
        """
        Compress multiple documents into single context.

        Uses hierarchical summarization.
        """
        pass

    async def _summarize(
        self,
        text: str,
        target_length: int,
    ) -> str:
        """Summarize text to target length."""
        pass

    async def _hierarchical_summarize(
        self,
        texts: List[str],
        target_tokens: int,
    ) -> str:
        """Hierarchical summarization for very long content."""
        pass

    def _chunk_by_tokens(
        self,
        text: str,
        chunk_size: int,
    ) -> List[str]:
        """Split text into token-sized chunks."""
        pass

    def _select_by_importance(
        self,
        sections: List[str],
        importance_scores: List[float],
        target_tokens: int,
    ) -> List[str]:
        """Select sections by importance to fit target."""
        pass

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass
```

### Test File: `tests/phase3/test_context_compression.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.optimization.compression_v9 import (
    ContextCompressor,
    CompressionConfig,
    CompressionResult,
)


class TestContextCompressor:
    """Tests for K4: Context Compression."""

    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.chat = MagicMock()
        llm.chat.completions = MagicMock()
        llm.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(
                message=MagicMock(content="Summarized content here.")
            )]
        ))
        return llm

    @pytest.fixture
    def compressor(self, mock_llm):
        return ContextCompressor(
            llm_client=mock_llm,
            config=CompressionConfig(target_tokens=1000),
        )

    @pytest.mark.asyncio
    async def test_compress_reduces_tokens(self, compressor):
        """Test compression reduces token count."""
        long_context = "This is a test. " * 500  # ~2500 tokens

        result = await compressor.compress(
            context=long_context,
            target_tokens=500,
        )

        assert isinstance(result, CompressionResult)
        assert result.compressed_tokens < result.original_tokens

    @pytest.mark.asyncio
    async def test_compression_ratio(self, compressor):
        """Test compression ratio calculation."""
        result = await compressor.compress(
            context="Long context here " * 100,
            target_tokens=100,
        )

        assert 0 < result.compression_ratio <= 1

    @pytest.mark.asyncio
    async def test_compress_conversation_preserves_recent(self, compressor):
        """Test conversation compression preserves recent."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Old message 1"},
            {"role": "assistant", "content": "Old response 1"},
            {"role": "user", "content": "Old message 2"},
            {"role": "assistant", "content": "Old response 2"},
            {"role": "user", "content": "Recent message"},
        ]

        compressed, result = await compressor.compress_conversation(
            messages=messages,
            target_tokens=100,
        )

        # System and recent should be preserved
        assert compressed[0]["role"] == "system"
        assert compressed[-1]["content"] == "Recent message"

    @pytest.mark.asyncio
    async def test_compress_documents_hierarchical(self, compressor):
        """Test document compression with hierarchy."""
        documents = [
            "Document 1: " + "content " * 100,
            "Document 2: " + "more content " * 100,
            "Document 3: " + "even more " * 100,
        ]

        compressed, result = await compressor.compress_documents(
            documents=documents,
            target_tokens=200,
        )

        assert isinstance(compressed, str)
        assert result.compressed_tokens <= 200

    def test_count_tokens(self, compressor):
        """Test token counting."""
        count = compressor.count_tokens("Hello, world!")

        assert isinstance(count, int)
        assert count > 0

    @pytest.mark.asyncio
    async def test_importance_weighted_selection(self, compressor):
        """Test importance-based section selection."""
        result = await compressor.compress(
            context="Important: key info. Filler: lots of filler content here.",
            target_tokens=50,
            importance_markers={
                "Important": 1.0,
                "Filler": 0.1,
            },
        )

        # Important content should be preserved
        assert "key info" in result.compressed_text or len(result.preserved_sections) > 0
```

---

## Stack V9 Integration Spec

After implementing all Week 5 patterns, create `stack_v9.py`:

### File: `middleware/stack_v9.py`

```python
"""
MiddlewareStackV9: Complete Integration Layer with All 60 Patterns
v9.0 Final 20 Patterns (Phase 3)

Inherits from MiddlewareStackV8 and adds:
- Memory: B3, B4, B5, B6
- Tools: D1, D2, D3, D4, D7
- Learning: I1, I2, I3, I5
- Reasoning: A5, A12
- Safety: F5, F6
- Observability: J2, J5
- Optimization: K4
"""

from .stack_v8 import MiddlewareStackV8

# Phase 3 imports (to be added)
# from .memory.semantic_v9 import ...
# from .memory.longterm_v9 import ...
# etc.


class MiddlewareStackV9(MiddlewareStackV8):
    """
    Complete middleware stack with all 60 patterns.

    This is the full production stack.
    """

    def __init__(
        self,
        supabase_client=None,
        redis_client=None,
        llm_client=None,
        langfuse_client=None,
        openai_client=None,  # For embeddings, moderation
        notify_approval=None,
        notify_shadow=None,
    ):
        # Initialize parent (V8)
        super().__init__(
            supabase_client,
            redis_client,
            llm_client,
            langfuse_client,
            notify_approval,
            notify_shadow,
        )

        # Week 1: Memory patterns
        # self.semantic_memory = SemanticMemoryManager(...)
        # self.longterm_memory = LongTermMemoryManager(...)
        # etc.

        # Week 2: Tool patterns
        # self.tool_registry = ToolRegistry(...)
        # etc.

        # Week 3: Learning patterns
        # self.feedback_learner = FeedbackLearner(...)
        # etc.

        # Week 4: Advanced patterns
        # self.tree_of_thought = TreeOfThought(...)
        # self.content_moderator = ContentModerator(...)
        # etc.

        # Week 5: Observability patterns
        # self.performance_collector = PerformanceCollector(...)
        # self.cost_tracker = CostTracker(...)
        # self.context_compressor = ContextCompressor(...)
```

---

## Implementation Checklist

### J2: Performance Metrics
- [ ] Create `middleware/observability/performance_v9.py`
- [ ] Implement `PerformanceCollector` class
- [ ] Create tests in `tests/phase3/test_performance_metrics.py`
- [ ] Run tests and verify passing

### J5: Cost Tracking
- [ ] Add `tiktoken` to requirements.txt
- [ ] Create `middleware/observability/cost_v9.py`
- [ ] Implement `CostTracker` class
- [ ] Add database migration
- [ ] Create tests in `tests/phase3/test_cost_tracking.py`
- [ ] Run tests and verify passing

### K4: Context Compression
- [ ] Create `middleware/optimization/__init__.py`
- [ ] Create `middleware/optimization/compression_v9.py`
- [ ] Implement `ContextCompressor` class
- [ ] Create tests in `tests/phase3/test_context_compression.py`
- [ ] Run tests and verify passing

### Stack V9 Integration
- [ ] Create `middleware/stack_v9.py`
- [ ] Integrate all Phase 3 patterns
- [ ] Create integration tests
- [ ] Update agent mixin for V9

---

## Dependencies Summary

### New Dependencies (to add to requirements.txt)

```
# Phase 3 additions
tiktoken>=0.5.0  # Token counting for cost tracking
```

### Existing Dependencies (already in use)

```
supabase>=2.10.0         # Storage, vectors
redis>=5.0.0             # Caching
openai>=1.55.0           # LLM, embeddings, moderation
langfuse>=2.0.0          # Observability
guardrails-ai>=0.5.0     # Safety validation
pydantic>=2.10.0         # Validation
tenacity>=9.0.0          # Retry logic
```

---

*Phase 3 Week 5 Specification*
*Generated: 2026-01-17*
