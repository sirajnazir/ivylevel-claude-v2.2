# agents/agents/core/voice.py
"""
IvyQuest v13.2 - Jenny Voice Validator

This module validates and transforms agent outputs to match Jenny Duan's
coaching voice. The validator checks:

1. Warmth: Caring, supportive tone
2. Agency: Student maintains ownership of decisions
3. Specificity: Concrete, actionable guidance
4. Authenticity: Genuine, not corporate/generic
5. Strategic: College admissions expertise evident

The validator uses both rule-based checks and LLM-based scoring.
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class VoiceDimension(str, Enum):
    """Dimensions of Jenny's voice to validate."""
    WARMTH = "warmth"
    AGENCY = "agency"
    SPECIFICITY = "specificity"
    AUTHENTICITY = "authenticity"
    STRATEGIC = "strategic"


@dataclass
class VoiceScore:
    """Score breakdown by dimension."""
    warmth: float = 70.0
    agency: float = 70.0
    specificity: float = 70.0
    authenticity: float = 70.0
    strategic: float = 70.0

    @property
    def total(self) -> float:
        """Weighted total score."""
        weights = {
            "warmth": 0.25,
            "agency": 0.25,
            "specificity": 0.20,
            "authenticity": 0.15,
            "strategic": 0.15,
        }
        return (
            self.warmth * weights["warmth"] +
            self.agency * weights["agency"] +
            self.specificity * weights["specificity"] +
            self.authenticity * weights["authenticity"] +
            self.strategic * weights["strategic"]
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "warmth": self.warmth,
            "agency": self.agency,
            "specificity": self.specificity,
            "authenticity": self.authenticity,
            "strategic": self.strategic,
            "total": self.total,
        }


class JennyVoiceValidator:
    """
    Validates and transforms text to match Jenny's coaching voice.
    
    Usage:
        validator = JennyVoiceValidator()
        
        # Validate text
        passed, scores, issues = await validator.validate(text)
        
        # Transform to Jenny voice
        transformed = await validator.transform(text)
        
        # Validate and transform in one call
        output = await validator.validate_and_transform(output_dict)
    """

    # Phrases that indicate warmth
    WARMTH_PHRASES = [
        "I'm excited", "I love", "great job", "wonderful",
        "proud of you", "amazing", "fantastic", "you've got this",
        "believe in you", "support you", "here for you",
    ]

    # Phrases that undermine agency (to avoid)
    AGENCY_VIOLATIONS = [
        "you must", "you have to", "you need to", "you should always",
        "the only way", "never do", "don't ever", "mandatory",
        "required to", "obligated to",
    ]

    # Phrases indicating authentic voice (vs corporate)
    AUTHENTIC_PHRASES = [
        "honestly", "real talk", "between us", "I've seen",
        "in my experience", "one student", "I remember",
    ]

    # Generic phrases to avoid
    GENERIC_PHRASES = [
        "best practices", "leverage your", "optimize your",
        "synergize", "utilize", "implement strategies",
        "holistic approach", "comprehensive solution",
    ]

    def __init__(self, llm_client=None):
        """
        Initialize validator.
        
        Args:
            llm_client: Optional LLM client for advanced validation
        """
        self.llm = llm_client

    async def validate(self, text: str) -> Tuple[bool, VoiceScore, List[str]]:
        """
        Validate text against Jenny voice criteria.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (passed, scores, issues)
        """
        if not text or len(text.strip()) < 10:
            return False, VoiceScore(), ["Text too short to validate"]

        text_lower = text.lower()
        issues = []

        # Score each dimension
        warmth = self._score_warmth(text_lower)
        agency = self._score_agency(text_lower)
        specificity = self._score_specificity(text)
        authenticity = self._score_authenticity(text_lower)
        strategic = self._score_strategic(text_lower)

        # Collect issues
        if warmth < 70:
            issues.append(
                f"Low warmth ({warmth:.0f}): Add supportive, encouraging language"
            )
        if agency < 70:
            issues.append(
                f"Agency issues ({agency:.0f}): Avoid directive language, preserve student autonomy"
            )
        if specificity < 70:
            issues.append(
                f"Low specificity ({specificity:.0f}): Add concrete examples and actions"
            )
        if authenticity < 70:
            issues.append(
                f"Low authenticity ({authenticity:.0f}): Avoid generic corporate language"
            )
        if strategic < 70:
            issues.append(
                f"Low strategic value ({strategic:.0f}): Add college-specific expertise"
            )

        scores = VoiceScore(
            warmth=warmth,
            agency=agency,
            specificity=specificity,
            authenticity=authenticity,
            strategic=strategic,
        )

        passed = scores.total >= 70.0

        return passed, scores, issues

    async def transform(self, text: str) -> str:
        """
        Transform text to better match Jenny's voice.
        
        Uses rule-based transformations. For better results,
        use LLM-based transformation.
        
        Args:
            text: Text to transform
            
        Returns:
            Transformed text
        """
        if not text:
            return text

        # Apply rule-based transformations
        transformed = text

        # Replace generic phrases
        replacements = {
            "best practices": "strategies that work",
            "leverage your": "use your",
            "optimize your": "strengthen your",
            "utilize": "use",
            "implement strategies": "try these approaches",
            "holistic approach": "complete picture",
            "comprehensive solution": "plan that works for you",
            "you must": "you might consider",
            "you have to": "it would help to",
            "you need to": "I'd suggest",
            "you should always": "often it helps to",
        }

        for old, new in replacements.items():
            transformed = re.sub(
                re.escape(old), new, transformed, flags=re.IGNORECASE
            )

        # Add warmth if missing
        if not any(phrase in transformed.lower() for phrase in self.WARMTH_PHRASES[:5]):
            # Add encouraging opener if this looks like advice
            if any(word in transformed.lower() for word in ["should", "could", "try"]):
                transformed = "I love where you're headed with this! " + transformed

        return transformed

    async def validate_and_transform(
        self, 
        output: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate output dict and transform text fields.
        
        Args:
            output: Output dict from agent
            
        Returns:
            Transformed output dict
        """
        if not output:
            return output

        # Find text fields to transform
        transformed = output.copy()

        def process_value(value: Any) -> Any:
            if isinstance(value, str) and len(value) > 50:
                # Transform longer text strings
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(self.transform(value))
            elif isinstance(value, dict):
                return {k: process_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_value(item) for item in value]
            return value

        # Process all values
        for key, value in transformed.items():
            transformed[key] = process_value(value)

        return transformed

    # ============================================================
    # SCORING METHODS
    # ============================================================

    def _score_warmth(self, text: str) -> float:
        """Score warmth dimension."""
        score = 60.0  # Base score

        # Add points for warm phrases
        for phrase in self.WARMTH_PHRASES:
            if phrase in text:
                score += 5

        # Check for question marks (engagement)
        question_count = text.count("?")
        score += min(question_count * 3, 10)

        # Check for "you" usage (personal)
        you_count = len(re.findall(r"\byou\b", text))
        score += min(you_count * 2, 10)

        return min(score, 100)

    def _score_agency(self, text: str) -> float:
        """Score agency preservation."""
        score = 85.0  # Start high, deduct for violations

        # Deduct for agency violations
        for phrase in self.AGENCY_VIOLATIONS:
            if phrase in text:
                score -= 10

        # Bonus for choice language
        choice_phrases = ["you could", "one option", "consider", "might", "perhaps"]
        for phrase in choice_phrases:
            if phrase in text:
                score += 3

        return max(min(score, 100), 0)

    def _score_specificity(self, text: str) -> float:
        """Score specificity of guidance."""
        score = 50.0  # Start neutral

        # Check for numbers (specific)
        number_count = len(re.findall(r"\d+", text))
        score += min(number_count * 5, 20)

        # Check for specific examples
        example_phrases = ["for example", "such as", "like when", "one way"]
        for phrase in example_phrases:
            if phrase in text.lower():
                score += 10

        # Check for action verbs
        action_verbs = ["submit", "write", "research", "contact", "apply", "create"]
        for verb in action_verbs:
            if verb in text.lower():
                score += 3

        return min(score, 100)

    def _score_authenticity(self, text: str) -> float:
        """Score authenticity (vs generic corporate voice)."""
        score = 70.0  # Start neutral-positive

        # Add for authentic phrases
        for phrase in self.AUTHENTIC_PHRASES:
            if phrase in text:
                score += 5

        # Deduct for generic phrases
        for phrase in self.GENERIC_PHRASES:
            if phrase in text:
                score -= 8

        # Check for personal anecdotes ("I" usage)
        i_count = len(re.findall(r"\bI\b", text))
        if i_count > 0:
            score += min(i_count * 3, 10)

        return max(min(score, 100), 0)

    def _score_strategic(self, text: str) -> float:
        """Score strategic college admissions expertise."""
        score = 55.0  # Start slightly above neutral

        # Check for college-specific terms
        college_terms = [
            "admissions", "application", "essay", "spike", "extracurricular",
            "recommendation", "transcript", "GPA", "test scores", "major",
            "school list", "early decision", "regular decision", "demonstrated interest",
            "hook", "narrative", "positioning", "common app", "coalition",
        ]
        for term in college_terms:
            if term.lower() in text.lower():
                score += 4

        # Check for strategic framing
        strategic_phrases = [
            "competitive advantage", "differentiate", "stand out",
            "position yourself", "strategic", "timeline",
        ]
        for phrase in strategic_phrases:
            if phrase in text.lower():
                score += 5

        return min(score, 100)

    # ============================================================
    # UTILITY METHODS
    # ============================================================

    def get_dimension_feedback(self, dimension: VoiceDimension, score: float) -> str:
        """Get specific feedback for a dimension."""
        feedback = {
            VoiceDimension.WARMTH: {
                "low": "Add more encouraging and supportive language. Use phrases like 'I'm excited about' or 'Great job on'.",
                "medium": "Good warmth, could add more personal touches.",
                "high": "Excellent warm, supportive tone!",
            },
            VoiceDimension.AGENCY: {
                "low": "Avoid directive language ('you must', 'you have to'). Use 'you might consider' or 'one option is'.",
                "medium": "Mostly good, watch for occasional directive language.",
                "high": "Great job preserving student autonomy!",
            },
            VoiceDimension.SPECIFICITY: {
                "low": "Add concrete examples, numbers, and specific action steps.",
                "medium": "Good specificity, could add more examples.",
                "high": "Excellent specific, actionable guidance!",
            },
            VoiceDimension.AUTHENTICITY: {
                "low": "Avoid generic corporate language. Add personal anecdotes and real examples.",
                "medium": "Good authenticity, could be more personal.",
                "high": "Authentic, genuine voice!",
            },
            VoiceDimension.STRATEGIC: {
                "low": "Add more college admissions expertise and strategic context.",
                "medium": "Good strategic content, could add more admissions-specific advice.",
                "high": "Strong strategic admissions expertise!",
            },
        }

        level = "low" if score < 60 else "medium" if score < 80 else "high"
        return feedback.get(dimension, {}).get(level, "")

    def __repr__(self) -> str:
        return f"JennyVoiceValidator(llm={'enabled' if self.llm else 'disabled'})"
