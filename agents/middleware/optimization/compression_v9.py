"""
Context Compression - Compress long contexts to fit token limits.

Pattern: K4
3P: tiktoken + OpenAI (for summarization)
Lines: ~120 (thin wrapper)

Features:
- Count tokens accurately
- Compress via summarization
- Preserve critical information
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try to import tiktoken
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class CompressionResult(BaseModel):
    """Result of context compression."""
    original_tokens: int = 0
    compressed_tokens: int = 0
    compression_ratio: float = 1.0
    compressed_text: str = ""
    truncated: bool = False
    summarized: bool = False


SUMMARIZE_PROMPT = """Summarize the following text, preserving all critical information, facts, and key details. Be concise but comprehensive.

Text to summarize:
{text}

Summary:"""


class ContextCompressor:
    """
    Compresses long contexts to fit token limits.

    Pattern K4: Context Compression
    3P: tiktoken (counting) + OpenAI (summarization)

    Thin wrapper - uses tiktoken for counting, OpenAI for intelligent compression.
    """

    DEFAULT_ENCODING = "cl100k_base"
    MODEL = "gpt-4o-mini"  # Fast and cheap for summarization

    def __init__(
        self,
        openai_client=None,
        encoding_name: str = DEFAULT_ENCODING,
    ):
        self.openai = openai_client
        self._encoder = None
        self._initialized = True  # Always available for counting

        if TIKTOKEN_AVAILABLE:
            try:
                self._encoder = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                logger.warning(f"Failed to initialize tiktoken encoder: {e}")

    @property
    def is_available(self) -> bool:
        return self._initialized

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if not text:
            return 0

        if self._encoder:
            return len(self._encoder.encode(text))

        # Fallback estimate
        return len(text) // 4

    def count_messages_tokens(
        self,
        messages: List[Dict[str, str]],
    ) -> int:
        """Count tokens in a message list."""
        total = 0
        for msg in messages:
            total += self.count_tokens(msg.get("content", ""))
            total += 4  # Message overhead
        total += 2  # Conversation overhead
        return total

    async def compress(
        self,
        text: str,
        max_tokens: int = 4000,
        preserve_start: int = 500,
        preserve_end: int = 500,
    ) -> CompressionResult:
        """Compress text to fit within token limit."""
        original_tokens = self.count_tokens(text)

        if original_tokens <= max_tokens:
            return CompressionResult(
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                compressed_text=text,
            )

        # Try summarization if OpenAI available
        if self.openai and original_tokens > max_tokens * 1.5:
            summarized = await self._summarize(text, max_tokens)
            if summarized:
                return summarized

        # Fallback to truncation with preserved ends
        truncated = self._truncate(
            text, max_tokens, preserve_start, preserve_end
        )
        return truncated

    async def _summarize(
        self,
        text: str,
        max_tokens: int,
    ) -> Optional[CompressionResult]:
        """Summarize text using LLM."""
        try:
            response = self.openai.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a summarization assistant. Create concise but comprehensive summaries."
                    },
                    {
                        "role": "user",
                        "content": SUMMARIZE_PROMPT.format(text=text)
                    }
                ],
                max_tokens=max_tokens,
            )

            summary = response.choices[0].message.content
            compressed_tokens = self.count_tokens(summary)
            original_tokens = self.count_tokens(text)

            return CompressionResult(
                original_tokens=original_tokens,
                compressed_tokens=compressed_tokens,
                compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 1.0,
                compressed_text=summary,
                summarized=True,
            )
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return None

    def _truncate(
        self,
        text: str,
        max_tokens: int,
        preserve_start: int,
        preserve_end: int,
    ) -> CompressionResult:
        """Truncate text while preserving start and end."""
        original_tokens = self.count_tokens(text)

        if self._encoder:
            tokens = self._encoder.encode(text)

            # Calculate how many tokens to keep
            middle_tokens = max_tokens - preserve_start - preserve_end - 10  # Buffer

            if middle_tokens <= 0:
                # Just truncate to max
                truncated_tokens = tokens[:max_tokens]
                truncated = self._encoder.decode(truncated_tokens)
            else:
                # Preserve start and end
                start_tokens = tokens[:preserve_start]
                end_tokens = tokens[-preserve_end:]
                truncated_tokens = start_tokens + end_tokens
                truncated = self._encoder.decode(truncated_tokens)
                truncated = truncated[:len(truncated)//2] + "\n\n[...content truncated...]\n\n" + truncated[len(truncated)//2:]

            compressed_tokens = self.count_tokens(truncated)
        else:
            # Fallback: character-based truncation
            char_limit = max_tokens * 4
            if len(text) > char_limit:
                start_chars = preserve_start * 4
                end_chars = preserve_end * 4
                truncated = text[:start_chars] + "\n\n[...content truncated...]\n\n" + text[-end_chars:]
            else:
                truncated = text

            compressed_tokens = self.count_tokens(truncated)

        return CompressionResult(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 1.0,
            compressed_text=truncated,
            truncated=True,
        )

    async def compress_messages(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4000,
    ) -> List[Dict[str, str]]:
        """Compress a list of messages to fit within token limit."""
        total_tokens = self.count_messages_tokens(messages)

        if total_tokens <= max_tokens:
            return messages

        # Compress older messages (preserve recent)
        result = []
        recent_messages = messages[-3:]  # Keep last 3 messages
        older_messages = messages[:-3]

        # Combine older messages for compression
        if older_messages:
            combined = "\n\n".join([
                f"{m.get('role', 'user')}: {m.get('content', '')}"
                for m in older_messages
            ])

            # Leave room for recent messages
            recent_tokens = self.count_messages_tokens(recent_messages)
            available = max_tokens - recent_tokens - 100

            compressed = await self.compress(combined, max_tokens=available)

            result.append({
                "role": "system",
                "content": f"[Previous conversation summary]\n{compressed.compressed_text}"
            })

        result.extend(recent_messages)
        return result
