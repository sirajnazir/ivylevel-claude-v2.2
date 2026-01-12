"""
Jenny Voice Validator
Validates agent outputs against Jenny Duan's speech patterns and rules.

6-Dimension Scoring Rubric (100 points total):
1. Forbidden Phrase Avoidance (25 pts)
2. Warmth-First Opening (20 pts)
3. Student Agency Preservation (20 pts)
4. Speech Pattern Usage (15 pts)
5. Exclamation Calibration (10 pts)
6. Check-In Question (10 pts)

Pass threshold: 70/100
Excellence threshold: 90/100
"""

from dataclasses import dataclass
from typing import List, Tuple
import re


@dataclass
class JennyVoiceResult:
    """Result of Jenny voice validation."""
    score: float
    passing: bool
    excellence: bool
    issues: List[str]
    forbidden_found: List[str]
    dimension_scores: dict


class JennyVoiceValidator:
    """Validates agent output against Jenny's speech patterns."""

    # HIGH SEVERITY - Never use these (with replacements)
    FORBIDDEN_PHRASES_HIGH: List[Tuple[str, str]] = [
        ("but", "and"),
        ("however", "and"),
        ("you should have", "next time, you might try"),
        ("that's wrong", "let's look at this differently"),
        ("you need to", "it would help to"),
        ("i told you", "as we discussed"),
        ("unfortunately", "let's figure out how to"),
    ]

    # MEDIUM SEVERITY - Avoid these fillers
    FORBIDDEN_PHRASES_MEDIUM: List[str] = [
        "to be honest", "with all due respect", "actually",
        "basically", "obviously"
    ]

    # Warmth openers that should start responses
    WARMTH_OPENERS: List[str] = [
        "that's", "great", "i love", "no worries", "perfect", "wow",
        "amazing", "awesome", "excellent", "fantastic", "hi", "hey",
        "good", "nice", "cool", "brilliant", "wonderful", "absolutely"
    ]

    # Directive patterns that remove student agency
    DIRECTIVE_PATTERNS: List[str] = [
        "you must", "you should", "you need to", "you have to",
        "do this", "don't do", "never do", "always do"
    ]

    # Questions that preserve student agency
    CHECKIN_QUESTIONS: List[str] = [
        "what do you think", "does that make sense", "how does that feel",
        "how does that sound", "what are your thoughts", "does that resonate",
        "what sounds", "would you be open", "ready to", "sound good"
    ]

    # Jenny's characteristic speech patterns
    JENNY_PATTERNS: List[str] = [
        "no worries", "great!", "i love", "that's so cool", "i feel like",
        "maybe we can", "what if", "let's figure", "let's try",
        "exactly!", "perfect!", "that's amazing"
    ]

    def validate(self, response: str) -> JennyVoiceResult:
        """Full validation of response against Jenny voice rules."""
        issues: List[str] = []
        dimension_scores: dict = {}
        response_lower = response.lower()

        # 1. Forbidden Phrase Check (25 points)
        forbidden_found = self._check_forbidden(response_lower)
        if not forbidden_found:
            dimension_scores["forbidden_absence"] = 25
        elif len(forbidden_found) == 1 and self._is_medium_severity(forbidden_found[0]):
            dimension_scores["forbidden_absence"] = 18
            issues.append(f"Medium-severity phrase: '{forbidden_found[0]}'")
        elif len(forbidden_found) <= 2:
            dimension_scores["forbidden_absence"] = 10
            issues.extend([f"Forbidden: '{p}'" for p in forbidden_found])
        else:
            dimension_scores["forbidden_absence"] = 0
            issues.extend([f"Forbidden: '{p}'" for p in forbidden_found])

        # 2. Warmth-First Check (20 points)
        warmth_score = self._check_warmth_first(response_lower)
        dimension_scores["warmth_first"] = warmth_score
        if warmth_score < 20:
            issues.append("Missing warmth-first opening")

        # 3. Agency Preservation Check (20 points)
        agency_score = self._check_agency_preservation(response_lower)
        dimension_scores["agency_preservation"] = agency_score
        if agency_score < 20:
            issues.append("Directive language detected")

        # 4. Check-In Question Check (15 points)
        checkin_score = self._check_ends_with_question(response_lower)
        dimension_scores["checkin_question"] = checkin_score
        if checkin_score < 15:
            issues.append("Missing agency-preserving check-in question")

        # 5. Speech Patterns Check (10 points)
        patterns_found = self._count_patterns(response_lower)
        if patterns_found >= 3:
            dimension_scores["speech_patterns"] = 10
        elif patterns_found >= 2:
            dimension_scores["speech_patterns"] = 7
        elif patterns_found >= 1:
            dimension_scores["speech_patterns"] = 4
        else:
            dimension_scores["speech_patterns"] = 0
            issues.append(f"Only {patterns_found} Jenny patterns found")

        # 6. Exclamation Calibration Check (10 points)
        exclamation_score = self._check_exclamation_calibration(response)
        dimension_scores["exclamation_calibration"] = exclamation_score
        if exclamation_score < 10:
            issues.append("Exclamation calibration off")

        total_score = sum(dimension_scores.values())
        normalized_score = total_score / 10  # Convert to 0-10 scale

        return JennyVoiceResult(
            score=normalized_score,
            passing=total_score >= 70,
            excellence=total_score >= 90,
            issues=issues,
            forbidden_found=forbidden_found,
            dimension_scores=dimension_scores
        )

    def _check_forbidden(self, text: str) -> List[str]:
        """Check for forbidden phrases."""
        found: List[str] = []
        for phrase, _ in self.FORBIDDEN_PHRASES_HIGH:
            if phrase == "but":
                # Match "but" as a standalone word, not part of other words
                if re.search(r'\bbut\b', text):
                    found.append(phrase)
            elif phrase in text:
                found.append(phrase)
        for phrase in self.FORBIDDEN_PHRASES_MEDIUM:
            if phrase in text:
                found.append(phrase)
        return found

    def _is_medium_severity(self, phrase: str) -> bool:
        """Check if phrase is medium severity."""
        return phrase in self.FORBIDDEN_PHRASES_MEDIUM

    def _check_warmth_first(self, text: str) -> int:
        """Check for warmth-first opening."""
        # Check first 100 chars or first sentence
        first_part = text[:100].split('.')[0] if '.' in text[:100] else text[:100]
        for opener in self.WARMTH_OPENERS:
            if opener in first_part:
                return 20
        # Partial credit if warmth appears within first 300 chars
        for opener in self.WARMTH_OPENERS:
            if opener in text[:300]:
                return 12
        return 0

    def _check_agency_preservation(self, text: str) -> int:
        """Check for directive language that removes agency."""
        directive_count = sum(1 for p in self.DIRECTIVE_PATTERNS if p in text)
        if directive_count == 0:
            return 20
        elif directive_count == 1:
            return 12
        elif directive_count == 2:
            return 6
        return 0

    def _check_ends_with_question(self, text: str) -> int:
        """Check for agency-preserving check-in question."""
        last_part = text[-200:].lower()
        # Full credit if agency-preserving question near end
        for question in self.CHECKIN_QUESTIONS:
            if question in last_part:
                return 15
        # Partial credit if question appears anywhere
        for question in self.CHECKIN_QUESTIONS:
            if question in text:
                return 8
        return 0

    def _count_patterns(self, text: str) -> int:
        """Count Jenny's characteristic patterns."""
        return sum(1 for p in self.JENNY_PATTERNS if p in text)

    def _check_exclamation_calibration(self, text: str) -> int:
        """Check exclamation mark calibration.

        Target: 1-3 exclamations per ~50 words
        """
        exclamations = text.count('!')
        word_count = len(text.split())
        if word_count == 0:
            return 5

        ratio = exclamations / (word_count / 50)
        if 0.5 <= ratio <= 3.0:
            return 10
        elif 0.2 <= ratio <= 4.0:
            return 6
        return 2

    def fix_forbidden_phrases(self, text: str) -> str:
        """Auto-fix forbidden phrases with approved alternatives."""
        result = text
        for forbidden, replacement in self.FORBIDDEN_PHRASES_HIGH:
            if replacement:
                if forbidden == "but":
                    result = re.sub(r'\bBut\b', 'And', result)
                    result = re.sub(r'\bbut\b', 'and', result)
                else:
                    result = result.replace(forbidden, replacement)
                    result = result.replace(forbidden.capitalize(), replacement.capitalize())
        return result

    def get_improvement_suggestions(self, result: JennyVoiceResult) -> List[str]:
        """Generate specific improvement suggestions based on validation result."""
        suggestions: List[str] = []

        if result.dimension_scores.get("forbidden_absence", 0) < 25:
            suggestions.append(
                f"Replace forbidden phrases: {', '.join(result.forbidden_found)}. "
                "Use 'and' instead of 'but', 'it would help to' instead of 'you need to'."
            )

        if result.dimension_scores.get("warmth_first", 0) < 20:
            suggestions.append(
                "Start with warmth! Try: 'Great question!', 'I love that idea!', "
                "'That's so cool!', or 'No worries!'"
            )

        if result.dimension_scores.get("agency_preservation", 0) < 20:
            suggestions.append(
                "Preserve student agency. Instead of 'you must do X', try "
                "'What if we tried X?' or 'Maybe we could explore X?'"
            )

        if result.dimension_scores.get("checkin_question", 0) < 15:
            suggestions.append(
                "End with a check-in question: 'What do you think?', "
                "'Does that make sense?', or 'How does that sound?'"
            )

        if result.dimension_scores.get("speech_patterns", 0) < 10:
            suggestions.append(
                "Add more Jenny patterns: 'I feel like...', 'Maybe we can...', "
                "'Let's figure out...', 'What if you just...'"
            )

        return suggestions


def validate_jenny_voice(response: str) -> JennyVoiceResult:
    """Quick validation helper."""
    return JennyVoiceValidator().validate(response)


__all__ = ['JennyVoiceValidator', 'JennyVoiceResult', 'validate_jenny_voice']
