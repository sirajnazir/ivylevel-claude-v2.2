"""
Memory Extraction - Extract memorable facts from conversations.

Pattern: B5
3P: OpenAI (structured output extraction)
Lines: ~100 (thin wrapper)

Features:
- Extract facts, preferences, goals from text
- Structured output via OpenAI function calling
- Importance scoring
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class ExtractedMemory(BaseModel):
    """A memory extracted from conversation."""
    content: str
    memory_type: str = "fact"  # fact, preference, goal, insight
    importance: float = 0.5
    confidence: float = 1.0
    source_text: Optional[str] = None


EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "memories": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The extracted memory content"
                    },
                    "memory_type": {
                        "type": "string",
                        "enum": ["fact", "preference", "goal", "insight"],
                        "description": "Type of memory"
                    },
                    "importance": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "Importance score 0-1"
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "Confidence in extraction accuracy"
                    }
                },
                "required": ["content", "memory_type", "importance"]
            }
        }
    },
    "required": ["memories"]
}

EXTRACTION_PROMPT = """Extract memorable information from this conversation.

Focus on:
- Facts: Concrete information about the user (e.g., "User is a high school junior")
- Preferences: What the user likes/dislikes (e.g., "User prefers detailed explanations")
- Goals: What the user wants to achieve (e.g., "User wants to attend MIT")
- Insights: Patterns or observations (e.g., "User learns better with examples")

Rate importance (0-1):
- 1.0: Critical info (name, major goals, key constraints)
- 0.7-0.9: Important preferences and context
- 0.4-0.6: Useful but not essential
- 0.1-0.3: Minor details

Only extract genuinely useful information. Skip trivial or temporary info.

Conversation:
{text}"""


class MemoryExtractor:
    """
    Extracts memorable facts from conversations using OpenAI.

    Pattern B5: Memory Extraction
    3P: OpenAI (structured output)

    Thin wrapper - delegates extraction to OpenAI with structured output.
    """

    MODEL = "gpt-4o-mini"  # Fast and cheap for extraction

    def __init__(self, openai_client=None):
        self.openai = openai_client
        self._initialized = openai_client is not None

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def extract(
        self,
        text: str,
        min_importance: float = 0.3,
    ) -> List[ExtractedMemory]:
        """Extract memories from text."""
        if not self.is_available:
            logger.warning("MemoryExtractor not available - no OpenAI client")
            return []

        if not text or len(text.strip()) < 10:
            return []

        try:
            response = self.openai.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You extract memorable information from conversations. Return structured JSON."
                    },
                    {
                        "role": "user",
                        "content": EXTRACTION_PROMPT.format(text=text)
                    }
                ],
                functions=[{
                    "name": "extract_memories",
                    "description": "Extract memorable information from text",
                    "parameters": EXTRACTION_SCHEMA,
                }],
                function_call={"name": "extract_memories"},
            )

            # Parse function call result
            function_call = response.choices[0].message.function_call
            if function_call and function_call.arguments:
                data = json.loads(function_call.arguments)
                memories = data.get("memories", [])

                return [
                    ExtractedMemory(
                        content=m["content"],
                        memory_type=m["memory_type"],
                        importance=m["importance"],
                        confidence=m.get("confidence", 1.0),
                        source_text=text[:200] if len(text) > 200 else text,
                    )
                    for m in memories
                    if m["importance"] >= min_importance
                ]

            return []
        except Exception as e:
            logger.error(f"Failed to extract memories: {e}")
            return []

    async def extract_from_messages(
        self,
        messages: List[Dict[str, str]],
        min_importance: float = 0.3,
    ) -> List[ExtractedMemory]:
        """Extract memories from a list of messages."""
        if not messages:
            return []

        # Format messages into text
        text_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            text_parts.append(f"{role.upper()}: {content}")

        text = "\n\n".join(text_parts)
        return await self.extract(text, min_importance)
