"""
Content Moderation - Check content for policy violations.

Pattern: F5
3P: OpenAI Moderation API (FREE)
Lines: ~80 (thin wrapper)

Features:
- Check text for harmful content
- Multiple category detection
- Configurable thresholds
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ModerationResult(BaseModel):
    """Result of content moderation check."""
    flagged: bool = False
    categories: Dict[str, bool] = Field(default_factory=dict)
    category_scores: Dict[str, float] = Field(default_factory=dict)
    flagged_categories: List[str] = Field(default_factory=list)


class ContentModerator:
    """
    Checks content for policy violations using OpenAI.

    Pattern F5: Content Moderation
    3P: OpenAI Moderation API (FREE)

    Thin wrapper - delegates moderation to OpenAI's free API.
    """

    MODEL = "text-moderation-latest"

    # Default thresholds for flagging (OpenAI returns scores 0-1)
    DEFAULT_THRESHOLDS = {
        "sexual": 0.5,
        "hate": 0.5,
        "harassment": 0.5,
        "self-harm": 0.5,
        "sexual/minors": 0.1,  # Lower threshold for sensitive content
        "hate/threatening": 0.3,
        "violence/graphic": 0.5,
        "violence": 0.5,
        "harassment/threatening": 0.3,
        "self-harm/intent": 0.3,
        "self-harm/instructions": 0.3,
    }

    def __init__(
        self,
        openai_client=None,
        thresholds: Optional[Dict[str, float]] = None,
    ):
        self.openai = openai_client
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self._initialized = openai_client is not None

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def check(
        self,
        text: str,
    ) -> ModerationResult:
        """Check text for content policy violations."""
        if not self.is_available:
            logger.warning("ContentModerator not available - no OpenAI client")
            return ModerationResult()

        if not text or not text.strip():
            return ModerationResult()

        try:
            response = self.openai.moderations.create(
                input=text,
                model=self.MODEL,
            )

            result = response.results[0]

            # Extract categories and scores
            categories = {}
            category_scores = {}
            flagged_categories = []

            for category, flagged in result.categories.model_dump().items():
                categories[category] = flagged
                score = getattr(result.category_scores, category, 0.0)
                category_scores[category] = score

                # Check against threshold
                threshold = self.thresholds.get(category, 0.5)
                if score >= threshold:
                    flagged_categories.append(category)

            return ModerationResult(
                flagged=result.flagged or len(flagged_categories) > 0,
                categories=categories,
                category_scores=category_scores,
                flagged_categories=flagged_categories,
            )
        except Exception as e:
            logger.error(f"Content moderation failed: {e}")
            return ModerationResult()

    async def check_batch(
        self,
        texts: List[str],
    ) -> List[ModerationResult]:
        """Check multiple texts for policy violations."""
        results = []
        for text in texts:
            result = await self.check(text)
            results.append(result)
        return results

    def set_threshold(
        self,
        category: str,
        threshold: float,
    ) -> None:
        """Update threshold for a specific category."""
        self.thresholds[category] = max(0.0, min(1.0, threshold))

    def is_safe(
        self,
        result: ModerationResult,
    ) -> bool:
        """Check if content passed moderation."""
        return not result.flagged
