"""
PII Detection - Detect and redact personally identifiable information.

Pattern: F6
3P: Microsoft Presidio (ML-based)
Lines: ~100 (thin wrapper)

Features:
- Detect PII entities
- Configurable entity types
- Redaction with placeholders
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try to import Presidio (optional dependency)
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False
    logger.warning("Presidio not installed - PII detection will be unavailable")


class PIIEntity(BaseModel):
    """A detected PII entity."""
    entity_type: str
    text: str
    start: int
    end: int
    score: float


class PIIResult(BaseModel):
    """Result of PII detection."""
    has_pii: bool = False
    entities: List[PIIEntity] = Field(default_factory=list)
    redacted_text: Optional[str] = None
    entity_counts: Dict[str, int] = Field(default_factory=dict)


class PIIDetector:
    """
    Detects and redacts PII using Microsoft Presidio.

    Pattern F6: PII Detection
    3P: Microsoft Presidio (ML-based)

    Thin wrapper - delegates detection to Presidio.
    """

    # Default entity types to detect
    DEFAULT_ENTITIES = [
        "PERSON",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "CREDIT_CARD",
        "US_SSN",
        "US_PASSPORT",
        "US_DRIVER_LICENSE",
        "IP_ADDRESS",
        "LOCATION",
        "DATE_TIME",
    ]

    def __init__(
        self,
        entities: Optional[List[str]] = None,
        language: str = "en",
    ):
        self.entities = entities or self.DEFAULT_ENTITIES
        self.language = language
        self._analyzer = None
        self._anonymizer = None
        self._initialized = False

        if PRESIDIO_AVAILABLE:
            try:
                self._analyzer = AnalyzerEngine()
                self._anonymizer = AnonymizerEngine()
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize Presidio: {e}")

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def detect(
        self,
        text: str,
        min_score: float = 0.5,
    ) -> PIIResult:
        """Detect PII in text."""
        if not self.is_available:
            logger.warning("PIIDetector not available - Presidio not initialized")
            return PIIResult()

        if not text or not text.strip():
            return PIIResult()

        try:
            # Analyze text for PII
            results = self._analyzer.analyze(
                text=text,
                entities=self.entities,
                language=self.language,
            )

            # Filter by score
            entities = []
            entity_counts: Dict[str, int] = {}

            for result in results:
                if result.score >= min_score:
                    entity = PIIEntity(
                        entity_type=result.entity_type,
                        text=text[result.start:result.end],
                        start=result.start,
                        end=result.end,
                        score=result.score,
                    )
                    entities.append(entity)

                    # Count by type
                    entity_counts[result.entity_type] = (
                        entity_counts.get(result.entity_type, 0) + 1
                    )

            return PIIResult(
                has_pii=len(entities) > 0,
                entities=entities,
                entity_counts=entity_counts,
            )
        except Exception as e:
            logger.error(f"PII detection failed: {e}")
            return PIIResult()

    async def redact(
        self,
        text: str,
        min_score: float = 0.5,
    ) -> PIIResult:
        """Detect and redact PII in text."""
        if not self.is_available:
            return PIIResult(redacted_text=text)

        if not text or not text.strip():
            return PIIResult(redacted_text=text)

        try:
            # First detect
            detect_result = await self.detect(text, min_score)

            if not detect_result.has_pii:
                return PIIResult(
                    has_pii=False,
                    redacted_text=text,
                )

            # Anonymize
            analyzer_results = self._analyzer.analyze(
                text=text,
                entities=self.entities,
                language=self.language,
            )

            # Filter by score
            filtered_results = [r for r in analyzer_results if r.score >= min_score]

            anonymized = self._anonymizer.anonymize(
                text=text,
                analyzer_results=filtered_results,
            )

            return PIIResult(
                has_pii=detect_result.has_pii,
                entities=detect_result.entities,
                redacted_text=anonymized.text,
                entity_counts=detect_result.entity_counts,
            )
        except Exception as e:
            logger.error(f"PII redaction failed: {e}")
            return PIIResult(redacted_text=text)

    def add_entity_type(self, entity_type: str) -> None:
        """Add an entity type to detect."""
        if entity_type not in self.entities:
            self.entities.append(entity_type)

    def remove_entity_type(self, entity_type: str) -> None:
        """Remove an entity type from detection."""
        if entity_type in self.entities:
            self.entities.remove(entity_type)
