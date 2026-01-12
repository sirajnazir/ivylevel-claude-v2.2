"""
IvyQuest v10.0 - Objective Metrics Calculator
=============================================

Calculate automated, deterministic metrics for agent outputs.
These metrics don't require LLM evaluation - they're rule-based.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Any
import re


@dataclass
class ObjectiveScore:
    """A single objective metric score."""
    metric_name: str
    score: float  # 0.0 - 1.0
    max_score: float
    details: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'metric_name': self.metric_name,
            'score': self.score,
            'max_score': self.max_score,
            'details': self.details,
            'passed': self.score >= 0.7,  # 70% threshold
        }


class ObjectiveMetricsCalculator:
    """Calculate automated, deterministic metrics."""

    # Forbidden generic phrases (from Jenny's coaching guidelines)
    FORBIDDEN_PHRASES = [
        "passionate about",
        "making a difference",
        "unique perspective",
        "diverse background",
        "committed to",
        "interested in",
        "aspiring to",
        "hoping to",
        "want to help",
        "driven individual",
        "hardworking student",
        "pursue my passion",
        "follow my dreams",
        "give back to",
        "well-rounded",
        "team player",
        "outside the box",
        "think outside",
        "make an impact",
        "change the world",
    ]

    # First Principle types for validation
    VALID_FIRST_PRINCIPLES = [
        'BUILDER', 'STORYTELLER', 'DISCOVERER', 'ADVOCATE',
        'CONNECTOR', 'HEALER', 'LEADER'
    ]

    def calculate_narrative_metrics(
        self,
        agent_output: Dict[str, Any],
        golden: Dict[str, Any]
    ) -> Dict[str, ObjectiveScore]:
        """
        Calculate objective metrics for narrative synthesis.

        Args:
            agent_output: Output from NarrativeSynthesisAgent
            golden: Golden example with expected_outputs and input_profile

        Returns:
            Dict of metric names to ObjectiveScore
        """
        brand_statement = agent_output.get('brand_statement', '')
        expected = golden.get('expected_outputs', {})
        input_profile = golden.get('input_profile', {})

        return {
            'identity_coverage': self._identity_coverage(
                brand_statement,
                input_profile
            ),
            'theme_alignment': self._theme_alignment(
                agent_output.get('themes', []),
                expected.get('themes', [])
            ),
            'first_principle_match': self._first_principle_match(
                agent_output.get('first_principle'),
                expected.get('first_principle')
            ),
            'first_principle_valid': self._first_principle_valid(
                agent_output.get('first_principle')
            ),
            'forbidden_absence': self._forbidden_phrase_check(brand_statement),
            'length_appropriate': self._length_check(brand_statement, 15, 35),
            'specificity_score': self._specificity_score(brand_statement),
            'narrative_dna_present': self._field_present_check(
                agent_output.get('narrative_dna'),
                'narrative_dna',
                min_length=100
            ),
            'archetype_present': self._archetype_check(
                agent_output.get('archetype')
            ),
        }

    def calculate_awards_metrics(
        self,
        agent_output: Dict[str, Any],
        golden: Dict[str, Any]
    ) -> Dict[str, ObjectiveScore]:
        """
        Calculate objective metrics for awards recommendations.

        Args:
            agent_output: Output from AwardsAgent
            golden: Golden example with expected_outputs

        Returns:
            Dict of metric names to ObjectiveScore
        """
        agent_awards = set(
            a.get('id') or a.get('name', '')
            for a in agent_output.get('awards', [])
        )
        golden_awards = set(
            a.get('id') or a.get('name', '')
            for a in golden.get('expected_outputs', {}).get('awards', [])
        )

        return {
            'precision': self._precision(agent_awards, golden_awards),
            'recall': self._recall(agent_awards, golden_awards),
            'portfolio_balance': self._portfolio_balance(
                agent_output.get('awards', [])
            ),
            'rationale_coverage': self._rationale_coverage(
                agent_output.get('awards', [])
            ),
            'award_count_reasonable': self._count_check(
                len(agent_output.get('awards', [])),
                min_count=3,
                max_count=15,
                name='award_count'
            ),
        }

    def calculate_crisis_metrics(
        self,
        agent_output: Dict[str, Any],
        golden: Dict[str, Any]
    ) -> Dict[str, ObjectiveScore]:
        """
        Calculate objective metrics for Crisis Alchemy responses.

        Args:
            agent_output: Output from Crisis Alchemy
            golden: Golden example with expected response

        Returns:
            Dict of metric names to ObjectiveScore
        """
        return {
            'validation_present': self._field_present_check(
                agent_output.get('validation'),
                'validation',
                min_length=20
            ),
            'micro_action_present': self._field_present_check(
                agent_output.get('micro_action'),
                'micro_action',
                min_length=20
            ),
            'reframe_present': self._field_present_check(
                agent_output.get('reframe'),
                'reframe',
                min_length=20
            ),
            'pivot_activity_present': self._field_present_check(
                agent_output.get('pivot_activity'),
                'pivot_activity',
                min_length=20
            ),
            'forbidden_absence': self._forbidden_phrase_check(
                ' '.join([
                    agent_output.get('validation', ''),
                    agent_output.get('reframe', ''),
                ])
            ),
        }

    def _identity_coverage(
        self,
        text: str,
        profile: Dict[str, Any]
    ) -> ObjectiveScore:
        """Check coverage of identity elements in text."""
        identity_markers = []

        # Extract expected identity markers from profile
        operating = profile.get('operating', {})
        if operating.get('culturalBackground'):
            backgrounds = operating['culturalBackground']
            if isinstance(backgrounds, list):
                identity_markers.extend(backgrounds)
            else:
                identity_markers.append(backgrounds)

        if operating.get('gender'):
            gender = operating['gender']
            # Map gender codes to searchable terms
            gender_map = {
                'FEMALE': ['woman', 'female', 'girl', 'her', 'she'],
                'MALE': ['man', 'male', 'boy', 'his', 'he'],
            }
            identity_markers.extend(gender_map.get(gender, [gender.lower()]))

        if operating.get('religion'):
            identity_markers.append(operating['religion'].lower())

        if operating.get('firstGeneration'):
            identity_markers.extend(['first-gen', 'first generation', 'first-generation'])

        # Extract from passion
        passion = profile.get('passion', {})
        if passion.get('spike_category'):
            identity_markers.append(passion['spike_category'].lower())

        if not identity_markers:
            return ObjectiveScore(
                'identity_coverage', 1.0, 1.0,
                'No identity markers expected'
            )

        text_lower = text.lower()
        found = sum(
            1 for marker in identity_markers
            if isinstance(marker, str) and marker.lower() in text_lower
        )
        score = min(found / max(len(identity_markers) // 2, 1), 1.0)

        return ObjectiveScore(
            'identity_coverage',
            score,
            1.0,
            f"Found {found}/{len(identity_markers)} identity markers"
        )

    def _theme_alignment(
        self,
        agent_themes: List[str],
        expected_themes: List[str]
    ) -> ObjectiveScore:
        """Calculate Jaccard similarity of themes."""
        if not expected_themes:
            return ObjectiveScore(
                'theme_alignment', 1.0, 1.0,
                'No themes expected'
            )

        agent_set = set(t.lower().strip() for t in agent_themes if t)
        expected_set = set(t.lower().strip() for t in expected_themes if t)

        if not agent_set and not expected_set:
            return ObjectiveScore('theme_alignment', 1.0, 1.0, 'Both empty')

        intersection = len(agent_set & expected_set)
        union = len(agent_set | expected_set)
        score = intersection / union if union > 0 else 0

        return ObjectiveScore(
            'theme_alignment',
            score,
            1.0,
            f"Jaccard similarity: {intersection}/{union} themes overlap"
        )

    def _first_principle_match(
        self,
        agent_fp: str,
        expected_fp: str
    ) -> ObjectiveScore:
        """Check match of first principle type."""
        if not expected_fp:
            return ObjectiveScore(
                'first_principle_match', 1.0, 1.0,
                'No first principle expected'
            )

        agent_clean = (agent_fp or '').upper().strip()
        expected_clean = expected_fp.upper().strip()

        match = agent_clean == expected_clean
        return ObjectiveScore(
            'first_principle_match',
            1.0 if match else 0.0,
            1.0,
            f"Expected: {expected_clean}, Got: {agent_clean}"
        )

    def _first_principle_valid(self, first_principle: str) -> ObjectiveScore:
        """Check if first principle is a valid type."""
        if not first_principle:
            return ObjectiveScore(
                'first_principle_valid', 0.0, 1.0,
                'No first principle provided'
            )

        fp_clean = first_principle.upper().strip()
        valid = fp_clean in self.VALID_FIRST_PRINCIPLES

        return ObjectiveScore(
            'first_principle_valid',
            1.0 if valid else 0.0,
            1.0,
            f"'{first_principle}' is {'valid' if valid else 'invalid'}"
        )

    def _forbidden_phrase_check(self, text: str) -> ObjectiveScore:
        """Check absence of forbidden generic phrases."""
        text_lower = text.lower()
        found = [p for p in self.FORBIDDEN_PHRASES if p in text_lower]
        score = 1.0 - (len(found) / len(self.FORBIDDEN_PHRASES))

        return ObjectiveScore(
            'forbidden_absence',
            max(0, score),
            1.0,
            f"Found {len(found)} forbidden phrases" + (
                f": {found[:3]}" if found else ""
            )
        )

    def _length_check(
        self,
        text: str,
        min_words: int,
        max_words: int
    ) -> ObjectiveScore:
        """Check if text is within word count range."""
        if not text:
            return ObjectiveScore(
                'length_appropriate', 0.0, 1.0,
                'No text provided'
            )

        words = len(text.split())

        if min_words <= words <= max_words:
            score = 1.0
        elif words < min_words:
            score = words / min_words
        else:
            score = max_words / words

        return ObjectiveScore(
            'length_appropriate',
            score,
            1.0,
            f"Word count: {words} (target: {min_words}-{max_words})"
        )

    def _specificity_score(self, text: str) -> ObjectiveScore:
        """Score text specificity based on concrete details."""
        if not text:
            return ObjectiveScore(
                'specificity_score', 0.0, 1.0,
                'No text provided'
            )

        # Count specific indicators
        specific_patterns = [
            r'\d+',  # Numbers
            r'[A-Z][a-z]+\s[A-Z][a-z]+',  # Proper nouns (two words)
            r'\b(built|created|founded|organized|led|developed|launched|'
            r'taught|mentored|designed|implemented|established)\b',
        ]

        specific_count = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in specific_patterns
        )

        # Normalize to 0-1 (cap at 5 specifics = 1.0)
        score = min(specific_count / 5, 1.0)

        return ObjectiveScore(
            'specificity_score',
            score,
            1.0,
            f"Found {specific_count} specific details"
        )

    def _field_present_check(
        self,
        value: Any,
        field_name: str,
        min_length: int = 0
    ) -> ObjectiveScore:
        """Check if a field is present and meets minimum length."""
        if not value:
            return ObjectiveScore(
                f'{field_name}_present', 0.0, 1.0,
                f'{field_name} is missing'
            )

        if isinstance(value, str) and len(value) < min_length:
            return ObjectiveScore(
                f'{field_name}_present', 0.5, 1.0,
                f'{field_name} too short ({len(value)} < {min_length})'
            )

        return ObjectiveScore(
            f'{field_name}_present', 1.0, 1.0,
            f'{field_name} present'
        )

    def _archetype_check(self, archetype: Any) -> ObjectiveScore:
        """Check if archetype is properly structured."""
        if not archetype:
            return ObjectiveScore(
                'archetype_present', 0.0, 1.0,
                'No archetype provided'
            )

        if isinstance(archetype, dict):
            has_id = bool(archetype.get('id'))
            has_label = bool(archetype.get('label'))
            score = (0.5 if has_id else 0) + (0.5 if has_label else 0)
            return ObjectiveScore(
                'archetype_present', score, 1.0,
                f"Archetype has id={has_id}, label={has_label}"
            )

        return ObjectiveScore(
            'archetype_present', 0.5, 1.0,
            'Archetype present but not structured'
        )

    def _precision(self, predicted: Set[str], actual: Set[str]) -> ObjectiveScore:
        """Precision = relevant predictions / all predictions."""
        if not predicted:
            return ObjectiveScore('precision', 0.0, 1.0, 'No predictions')

        # Clean up empty strings
        predicted = {p for p in predicted if p}
        actual = {a for a in actual if a}

        relevant = len(predicted & actual)
        score = relevant / len(predicted) if predicted else 0

        return ObjectiveScore(
            'precision', score, 1.0,
            f"{relevant}/{len(predicted)} predictions relevant"
        )

    def _recall(self, predicted: Set[str], actual: Set[str]) -> ObjectiveScore:
        """Recall = relevant predictions / all relevant."""
        # Clean up empty strings
        predicted = {p for p in predicted if p}
        actual = {a for a in actual if a}

        if not actual:
            return ObjectiveScore('recall', 1.0, 1.0, 'No expected items')

        relevant = len(predicted & actual)
        score = relevant / len(actual)

        return ObjectiveScore(
            'recall', score, 1.0,
            f"{relevant}/{len(actual)} expected items found"
        )

    def _portfolio_balance(self, awards: List[Dict]) -> ObjectiveScore:
        """Check if portfolio has good balance of likely/target/stretch."""
        categories = {'likely': 0, 'target': 0, 'stretch': 0}

        for award in awards:
            cat = award.get('category', award.get('tier', 'target'))
            if cat in categories:
                categories[cat] += 1

        total = sum(categories.values())
        if total == 0:
            return ObjectiveScore(
                'portfolio_balance', 0.0, 1.0,
                'No categorized awards'
            )

        # Ideal: 30% likely, 40% target, 30% stretch
        ideal = {'likely': 0.3, 'target': 0.4, 'stretch': 0.3}
        actual = {k: v / total for k, v in categories.items()}

        # Calculate deviation from ideal
        deviation = sum(abs(ideal[k] - actual.get(k, 0)) for k in ideal)
        score = max(0, 1.0 - deviation)

        return ObjectiveScore(
            'portfolio_balance',
            score,
            1.0,
            f"Distribution: {categories}"
        )

    def _rationale_coverage(self, awards: List[Dict]) -> ObjectiveScore:
        """Check if all awards have rationales."""
        if not awards:
            return ObjectiveScore(
                'rationale_coverage', 1.0, 1.0,
                'No awards to check'
            )

        with_rationale = sum(
            1 for a in awards
            if a.get('rationale') or a.get('why')
        )
        score = with_rationale / len(awards)

        return ObjectiveScore(
            'rationale_coverage',
            score,
            1.0,
            f"{with_rationale}/{len(awards)} have rationales"
        )

    def _count_check(
        self,
        count: int,
        min_count: int,
        max_count: int,
        name: str
    ) -> ObjectiveScore:
        """Check if count is within reasonable range."""
        if min_count <= count <= max_count:
            score = 1.0
        elif count < min_count:
            score = count / min_count if min_count > 0 else 0
        else:
            score = max_count / count if count > 0 else 0

        return ObjectiveScore(
            f'{name}_reasonable',
            score,
            1.0,
            f"Count: {count} (target: {min_count}-{max_count})"
        )
