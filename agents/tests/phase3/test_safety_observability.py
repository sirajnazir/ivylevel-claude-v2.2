"""
Tests for Safety & Observability Patterns (F5, F6, J2, J5, K4)

Pattern: F5 (Moderation), F6 (PII), J2 (Logging), J5 (Cost), K4 (Compression)
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.safety.moderation_v9 import ContentModerator, ModerationResult
from middleware.safety.pii_v9 import PIIDetector, PIIResult, PIIEntity, PRESIDIO_AVAILABLE
from middleware.observability.logging_v9 import RequestLogger, RequestLog
from middleware.observability.cost_v9 import CostTracker, CostRecord, TIKTOKEN_AVAILABLE
from middleware.optimization.compression_v9 import ContextCompressor, CompressionResult


# ============= F5: Content Moderation Tests =============

class TestContentModerator:
    """Tests for F5: Content Moderation."""

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI client with moderation API."""
        client = MagicMock()

        # Mock moderation response
        mock_result = MagicMock()
        mock_result.flagged = False
        mock_result.categories = MagicMock()
        mock_result.categories.model_dump.return_value = {
            "sexual": False,
            "hate": False,
            "harassment": False,
            "self-harm": False,
            "violence": False,
        }
        mock_result.category_scores = MagicMock()
        mock_result.category_scores.sexual = 0.01
        mock_result.category_scores.hate = 0.02
        mock_result.category_scores.harassment = 0.01
        setattr(mock_result.category_scores, "self-harm", 0.001)
        mock_result.category_scores.violence = 0.03

        mock_response = MagicMock()
        mock_response.results = [mock_result]

        client.moderations.create.return_value = mock_response
        return client

    @pytest.fixture
    def moderator(self, mock_openai):
        return ContentModerator(openai_client=mock_openai)

    @pytest.fixture
    def moderator_no_client(self):
        return ContentModerator(openai_client=None)

    def test_is_available_with_client(self, moderator):
        """Test availability with client."""
        assert moderator.is_available is True

    def test_is_available_without_client(self, moderator_no_client):
        """Test availability without client."""
        assert moderator_no_client.is_available is False

    @pytest.mark.asyncio
    async def test_check_safe_content(self, moderator):
        """Test checking safe content."""
        result = await moderator.check("Hello, how are you today?")

        assert isinstance(result, ModerationResult)
        assert result.flagged is False

    @pytest.mark.asyncio
    async def test_check_empty_text(self, moderator):
        """Test checking empty text."""
        result = await moderator.check("")

        assert result.flagged is False

    @pytest.mark.asyncio
    async def test_check_graceful_degradation(self, moderator_no_client):
        """Test graceful degradation without client."""
        result = await moderator_no_client.check("Test text")

        assert isinstance(result, ModerationResult)
        assert result.flagged is False

    def test_is_safe_helper(self, moderator):
        """Test is_safe helper method."""
        safe_result = ModerationResult(flagged=False)
        unsafe_result = ModerationResult(flagged=True)

        assert moderator.is_safe(safe_result) is True
        assert moderator.is_safe(unsafe_result) is False

    def test_set_threshold(self, moderator):
        """Test setting threshold."""
        moderator.set_threshold("hate", 0.3)
        assert moderator.thresholds["hate"] == 0.3


# ============= F6: PII Detection Tests =============

class TestPIIDetector:
    """Tests for F6: PII Detection."""

    @pytest.fixture
    def detector(self):
        return PIIDetector()

    def test_is_available(self, detector):
        """Test availability depends on Presidio."""
        assert detector.is_available == PRESIDIO_AVAILABLE

    @pytest.mark.asyncio
    async def test_detect_empty_text(self, detector):
        """Test detecting PII in empty text."""
        result = await detector.detect("")

        assert result.has_pii is False

    @pytest.mark.asyncio
    @pytest.mark.skipif(not PRESIDIO_AVAILABLE, reason="Presidio not installed")
    async def test_detect_email(self, detector):
        """Test detecting email addresses."""
        result = await detector.detect("Contact me at john.doe@example.com")

        assert result.has_pii is True
        assert "EMAIL_ADDRESS" in result.entity_counts

    @pytest.mark.asyncio
    @pytest.mark.skipif(not PRESIDIO_AVAILABLE, reason="Presidio not installed")
    async def test_detect_phone(self, detector):
        """Test detecting phone numbers."""
        result = await detector.detect("Call me at 555-123-4567")

        assert result.has_pii is True

    @pytest.mark.asyncio
    @pytest.mark.skipif(not PRESIDIO_AVAILABLE, reason="Presidio not installed")
    async def test_redact_pii(self, detector):
        """Test redacting PII."""
        result = await detector.redact("Email me at test@test.com")

        assert result.redacted_text is not None
        if result.has_pii:
            assert "test@test.com" not in result.redacted_text

    @pytest.mark.asyncio
    async def test_detect_graceful_degradation(self):
        """Test graceful degradation when Presidio unavailable."""
        # Create detector that simulates no Presidio
        detector = PIIDetector()
        detector._initialized = False

        result = await detector.detect("test@example.com")

        assert result.has_pii is False

    def test_add_entity_type(self, detector):
        """Test adding entity type."""
        original_count = len(detector.entities)
        detector.add_entity_type("CUSTOM_TYPE")
        assert len(detector.entities) == original_count + 1

    def test_remove_entity_type(self, detector):
        """Test removing entity type."""
        detector.add_entity_type("TEMP_TYPE")
        detector.remove_entity_type("TEMP_TYPE")
        assert "TEMP_TYPE" not in detector.entities


# ============= J2: Request Logging Tests =============

class TestRequestLogger:
    """Tests for J2: Request Logging."""

    @pytest.fixture
    def logger(self):
        return RequestLogger()

    def test_is_available(self, logger):
        """Test logger is always available."""
        assert logger.is_available is True

    @pytest.mark.asyncio
    async def test_log_request(self, logger):
        """Test logging a request."""
        log = await logger.log(
            profile_id="test-profile",
            request_type="chat",
            input_data={"message": "Hello"},
            output_data={"response": "Hi there"},
            latency_ms=150,
            success=True,
        )

        assert isinstance(log, RequestLog)
        assert log.profile_id == "test-profile"
        assert log.request_type == "chat"
        assert log.success is True

    @pytest.mark.asyncio
    async def test_log_error(self, logger):
        """Test logging an error."""
        log = await logger.log_error(
            profile_id="test-profile",
            request_type="chat",
            error="Something went wrong",
        )

        assert log.success is False
        assert log.error == "Something went wrong"

    @pytest.mark.asyncio
    async def test_get_recent(self, logger):
        """Test getting recent logs."""
        await logger.log(profile_id="test", request_type="test")
        await logger.log(profile_id="test", request_type="test")

        recent = await logger.get_recent(profile_id="test")

        assert len(recent) >= 2

    @pytest.mark.asyncio
    async def test_get_stats(self, logger):
        """Test getting stats."""
        await logger.log(profile_id="test", success=True, latency_ms=100)
        await logger.log(profile_id="test", success=True, latency_ms=200)

        stats = await logger.get_stats(profile_id="test")

        assert "total_requests" in stats
        assert "success_rate" in stats
        assert "avg_latency_ms" in stats

    def test_clear_memory(self, logger):
        """Test clearing memory."""
        logger._in_memory_logs.append(RequestLog())
        logger.clear_memory()
        assert len(logger._in_memory_logs) == 0


# ============= J5: Cost Tracking Tests =============

class TestCostTracker:
    """Tests for J5: Cost Tracking."""

    @pytest.fixture
    def tracker(self):
        return CostTracker()

    def test_is_available(self, tracker):
        """Test tracker is always available."""
        assert tracker.is_available is True

    def test_count_tokens(self, tracker):
        """Test counting tokens."""
        text = "Hello, how are you today?"
        tokens = tracker.count_tokens(text)

        assert isinstance(tokens, int)
        assert tokens > 0

    def test_count_tokens_empty(self, tracker):
        """Test counting tokens in empty text."""
        tokens = tracker.count_tokens("")
        assert tokens == 0

    def test_calculate_cost(self, tracker):
        """Test calculating cost."""
        costs = tracker.calculate_cost(
            input_tokens=1000,
            output_tokens=500,
            model="gpt-4o",
        )

        assert "input_cost" in costs
        assert "output_cost" in costs
        assert "total_cost" in costs
        assert costs["total_cost"] > 0

    @pytest.mark.asyncio
    async def test_track(self, tracker):
        """Test tracking a cost record."""
        record = await tracker.track(
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            profile_id="test",
        )

        assert isinstance(record, CostRecord)
        assert record.total_tokens == 150

    def test_get_session_total(self, tracker):
        """Test getting session totals."""
        tracker._session_costs.append(
            CostRecord(model="gpt-4o", input_tokens=100, output_tokens=50, total_cost=0.01)
        )

        total = tracker.get_session_total()

        assert total["total_tokens"] == 150
        assert total["request_count"] == 1

    def test_clear_session(self, tracker):
        """Test clearing session."""
        tracker._session_costs.append(CostRecord(model="test"))
        tracker.clear_session()
        assert len(tracker._session_costs) == 0

    @pytest.mark.skipif(not TIKTOKEN_AVAILABLE, reason="tiktoken not installed")
    def test_accurate_token_count(self, tracker):
        """Test accurate token counting with tiktoken."""
        # A known string
        text = "The quick brown fox jumps over the lazy dog."
        tokens = tracker.count_tokens(text, model="gpt-4o")

        # Should be around 9-11 tokens
        assert 5 < tokens < 20


# ============= K4: Context Compression Tests =============

class TestContextCompressor:
    """Tests for K4: Context Compression."""

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI client for summarization."""
        client = MagicMock()

        mock_message = MagicMock()
        mock_message.content = "This is a compressed summary of the content."

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        client.chat.completions.create.return_value = mock_response
        return client

    @pytest.fixture
    def compressor(self, mock_openai):
        return ContextCompressor(openai_client=mock_openai)

    @pytest.fixture
    def compressor_no_openai(self):
        return ContextCompressor(openai_client=None)

    def test_is_available(self, compressor):
        """Test compressor is always available."""
        assert compressor.is_available is True

    def test_count_tokens(self, compressor):
        """Test counting tokens."""
        text = "Hello world"
        tokens = compressor.count_tokens(text)

        assert isinstance(tokens, int)
        assert tokens > 0

    @pytest.mark.asyncio
    async def test_compress_short_text(self, compressor):
        """Test compressing short text (no compression needed)."""
        text = "Short text"
        result = await compressor.compress(text, max_tokens=100)

        assert result.compressed_text == text
        assert result.compression_ratio == 1.0

    @pytest.mark.asyncio
    async def test_compress_long_text(self, compressor):
        """Test compressing long text."""
        text = "This is a very long text. " * 500  # ~2500+ tokens
        result = await compressor.compress(text, max_tokens=100)

        assert isinstance(result, CompressionResult)
        assert result.compression_ratio < 1.0

    @pytest.mark.asyncio
    async def test_compress_with_truncation(self, compressor_no_openai):
        """Test compression falls back to truncation without OpenAI."""
        text = "Word " * 1000  # Long text
        result = await compressor_no_openai.compress(text, max_tokens=100)

        assert result.truncated is True
        assert result.compressed_tokens <= result.original_tokens

    @pytest.mark.asyncio
    async def test_compress_messages(self, compressor):
        """Test compressing message list."""
        messages = [
            {"role": "user", "content": "Hello " * 100},
            {"role": "assistant", "content": "Hi there " * 100},
            {"role": "user", "content": "Recent message"},
        ]

        compressed = await compressor.compress_messages(messages, max_tokens=200)

        assert isinstance(compressed, list)


class TestCompressionResult:
    """Tests for CompressionResult model."""

    def test_default_values(self):
        """Test default values."""
        result = CompressionResult()

        assert result.original_tokens == 0
        assert result.compression_ratio == 1.0
        assert result.truncated is False
        assert result.summarized is False

    def test_custom_values(self):
        """Test custom values."""
        result = CompressionResult(
            original_tokens=1000,
            compressed_tokens=200,
            compression_ratio=0.2,
            compressed_text="Summary",
            summarized=True,
        )

        assert result.original_tokens == 1000
        assert result.compression_ratio == 0.2
        assert result.summarized is True


# Run with: pytest tests/phase3/test_safety_observability.py -v
