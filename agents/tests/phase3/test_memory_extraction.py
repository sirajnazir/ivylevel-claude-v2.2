"""
Tests for B5: Memory Extraction

Pattern: B5
3P: OpenAI (structured output extraction)
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.memory.extraction_v9 import (
    MemoryExtractor,
    ExtractedMemory,
    EXTRACTION_SCHEMA,
)


class TestMemoryExtractor:
    """Tests for B5: Memory Extraction."""

    @pytest.fixture
    def mock_extraction_response(self):
        """Mock extraction response data."""
        return {
            "memories": [
                {
                    "content": "User is a high school junior",
                    "memory_type": "fact",
                    "importance": 0.9,
                    "confidence": 0.95
                },
                {
                    "content": "User wants to attend MIT",
                    "memory_type": "goal",
                    "importance": 1.0,
                    "confidence": 0.9
                },
                {
                    "content": "User prefers detailed explanations",
                    "memory_type": "preference",
                    "importance": 0.7,
                    "confidence": 0.85
                }
            ]
        }

    @pytest.fixture
    def mock_openai(self, mock_extraction_response):
        """Mock OpenAI client with function calling."""
        client = MagicMock()

        # Mock function call response
        mock_function_call = MagicMock()
        mock_function_call.arguments = json.dumps(mock_extraction_response)

        mock_message = MagicMock()
        mock_message.function_call = mock_function_call

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        client.chat.completions.create.return_value = mock_response

        return client

    @pytest.fixture
    def extractor(self, mock_openai):
        return MemoryExtractor(openai_client=mock_openai)

    @pytest.fixture
    def extractor_no_client(self):
        """Extractor without OpenAI (tests graceful degradation)."""
        return MemoryExtractor(openai_client=None)

    def test_is_available_with_client(self, extractor):
        """Test availability check with client."""
        assert extractor.is_available is True

    def test_is_available_without_client(self, extractor_no_client):
        """Test availability check without client."""
        assert extractor_no_client.is_available is False

    @pytest.mark.asyncio
    async def test_extract_returns_memories(self, extractor):
        """Test extraction returns list of memories."""
        memories = await extractor.extract(
            text="I'm a high school junior and I really want to go to MIT. I like when you explain things in detail."
        )

        assert isinstance(memories, list)
        assert len(memories) == 3

    @pytest.mark.asyncio
    async def test_extract_filters_by_importance(self, extractor, mock_openai, mock_extraction_response):
        """Test extraction filters by minimum importance."""
        # Add a low-importance memory
        mock_extraction_response["memories"].append({
            "content": "User mentioned the weather",
            "memory_type": "fact",
            "importance": 0.2,
            "confidence": 0.5
        })

        mock_openai.chat.completions.create.return_value.choices[0].message.function_call.arguments = json.dumps(
            mock_extraction_response
        )

        memories = await extractor.extract(
            text="Some conversation text...",
            min_importance=0.5,
        )

        # Should filter out the 0.2 importance memory
        assert all(m.importance >= 0.5 for m in memories)

    @pytest.mark.asyncio
    async def test_extract_memory_types(self, extractor):
        """Test extraction identifies different memory types."""
        memories = await extractor.extract(
            text="I'm applying to colleges and want to study computer science."
        )

        memory_types = {m.memory_type for m in memories}
        assert "fact" in memory_types
        assert "goal" in memory_types

    @pytest.mark.asyncio
    async def test_extract_includes_source_text(self, extractor):
        """Test extracted memories include source text reference."""
        text = "Test conversation about college applications"
        memories = await extractor.extract(text=text)

        for memory in memories:
            assert memory.source_text is not None

    @pytest.mark.asyncio
    async def test_extract_graceful_degradation(self, extractor_no_client):
        """Test extract returns empty list when no client."""
        memories = await extractor_no_client.extract(
            text="Some text to extract from"
        )

        assert memories == []

    @pytest.mark.asyncio
    async def test_extract_empty_text(self, extractor):
        """Test extract handles empty text."""
        memories = await extractor.extract(text="")

        assert memories == []

    @pytest.mark.asyncio
    async def test_extract_short_text(self, extractor):
        """Test extract handles very short text."""
        memories = await extractor.extract(text="Hi")

        assert memories == []

    @pytest.mark.asyncio
    async def test_extract_from_messages(self, extractor):
        """Test extraction from message list."""
        messages = [
            {"role": "user", "content": "I'm a junior in high school"},
            {"role": "assistant", "content": "Great! What are your college goals?"},
            {"role": "user", "content": "I want to go to MIT for computer science"},
        ]

        memories = await extractor.extract_from_messages(messages)

        assert isinstance(memories, list)
        assert len(memories) > 0

    @pytest.mark.asyncio
    async def test_extract_from_empty_messages(self, extractor):
        """Test extraction from empty message list."""
        memories = await extractor.extract_from_messages([])

        assert memories == []

    @pytest.mark.asyncio
    async def test_extract_uses_function_calling(self, extractor, mock_openai):
        """Test extraction uses OpenAI function calling."""
        await extractor.extract(text="Test text for extraction")

        call_args = mock_openai.chat.completions.create.call_args
        assert "functions" in call_args.kwargs
        assert "function_call" in call_args.kwargs

    @pytest.mark.asyncio
    async def test_extract_handles_api_error(self, extractor, mock_openai):
        """Test extraction handles API errors gracefully."""
        mock_openai.chat.completions.create.side_effect = Exception("API Error")

        memories = await extractor.extract(text="Test text")

        assert memories == []


class TestExtractedMemoryModel:
    """Tests for the ExtractedMemory Pydantic model."""

    def test_default_values(self):
        """Test default values are set."""
        memory = ExtractedMemory(content="Test content")

        assert memory.memory_type == "fact"
        assert memory.importance == 0.5
        assert memory.confidence == 1.0
        assert memory.source_text is None

    def test_custom_values(self):
        """Test custom values are preserved."""
        memory = ExtractedMemory(
            content="User wants to study medicine",
            memory_type="goal",
            importance=0.9,
            confidence=0.85,
            source_text="I want to become a doctor",
        )

        assert memory.content == "User wants to study medicine"
        assert memory.memory_type == "goal"
        assert memory.importance == 0.9
        assert memory.confidence == 0.85
        assert memory.source_text == "I want to become a doctor"

    def test_memory_types(self):
        """Test all memory types are valid."""
        for mtype in ["fact", "preference", "goal", "insight"]:
            memory = ExtractedMemory(content="Test", memory_type=mtype)
            assert memory.memory_type == mtype


class TestExtractionSchema:
    """Tests for the extraction JSON schema."""

    def test_schema_has_memories_array(self):
        """Test schema defines memories array."""
        assert "memories" in EXTRACTION_SCHEMA["properties"]
        assert EXTRACTION_SCHEMA["properties"]["memories"]["type"] == "array"

    def test_schema_memory_properties(self):
        """Test schema defines memory item properties."""
        item_props = EXTRACTION_SCHEMA["properties"]["memories"]["items"]["properties"]
        assert "content" in item_props
        assert "memory_type" in item_props
        assert "importance" in item_props
        assert "confidence" in item_props

    def test_schema_importance_bounds(self):
        """Test importance has min/max bounds."""
        importance = EXTRACTION_SCHEMA["properties"]["memories"]["items"]["properties"]["importance"]
        assert importance["minimum"] == 0
        assert importance["maximum"] == 1


# Run with: pytest tests/phase3/test_memory_extraction.py -v
