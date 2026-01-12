"""
Awards Probability Engine
Implements Jenny's awards strategy with 2-2-1 portfolio structure.

Probability Formula:
  probability = fit*0.4 + (100-competition)*0.3 + quality*0.3 + bonuses

Bonuses:
  - Vulnerability storytelling: +15%
  - Identity alignment: +10%

Portfolio Structure (2-2-1):
  - 2 Likely awards (60%+ chance)
  - 2 Target awards (40-60% chance)
  - 1 Stretch award (20-40% chance)
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import re


@dataclass
class AwardProbability:
    """Calculated probability for a student-award pair."""
    award_id: str
    award_name: str
    probability: float
    tier: str  # likely, target, stretch
    fit_score: float
    competition_factor: float
    submission_quality_score: float
    vulnerability_bonus: bool
    identity_bonus: bool
    reasoning: str


@dataclass
class Portfolio:
    """A balanced 2-2-1 awards portfolio."""
    likely: List[AwardProbability]
    target: List[AwardProbability]
    stretch: List[AwardProbability]
    balance_score: float
    total_expected_wins: float
    recommendations: List[str]


class AwardsProbabilityEngine:
    """Calculates award win probability using Jenny's methodology."""

    LIKELY_THRESHOLD = 60
    TARGET_THRESHOLD = 40
    FIT_WEIGHT = 0.4
    COMPETITION_WEIGHT = 0.3
    QUALITY_WEIGHT = 0.3
    VULNERABILITY_BONUS = 15
    IDENTITY_BONUS = 10
    MAX_PROBABILITY = 95

    def calculate_probability(
        self,
        student: Dict[str, Any],
        award: Dict[str, Any]
    ) -> AwardProbability:
        """Calculate win probability for a student-award pair."""
        # Calculate component scores
        fit_score = self._calculate_fit_score(student, award)
        selectivity = award.get("selectivity_percentile", 50)
        competition_factor = 100 - selectivity
        quality_score = self._estimate_submission_quality(student, award)

        # Base probability
        base_probability = (
            fit_score * self.FIT_WEIGHT +
            competition_factor * self.COMPETITION_WEIGHT +
            quality_score * self.QUALITY_WEIGHT
        )

        # Check for bonuses
        vulnerability_bonus = self._has_vulnerability_story(student, award)
        identity_bonus = self._has_identity_alignment(student, award)

        if vulnerability_bonus:
            base_probability += self.VULNERABILITY_BONUS
        if identity_bonus:
            base_probability += self.IDENTITY_BONUS

        final_probability = min(base_probability, self.MAX_PROBABILITY)
        tier = self._classify_tier(final_probability)

        reasoning = self._generate_reasoning(
            fit_score, competition_factor, quality_score,
            vulnerability_bonus, identity_bonus, award
        )

        return AwardProbability(
            award_id=award.get("id", ""),
            award_name=award.get("name", ""),
            probability=round(final_probability, 1),
            tier=tier,
            fit_score=round(fit_score, 1),
            competition_factor=round(competition_factor, 1),
            submission_quality_score=round(quality_score, 1),
            vulnerability_bonus=vulnerability_bonus,
            identity_bonus=identity_bonus,
            reasoning=reasoning
        )

    def _calculate_fit_score(self, student: Dict, award: Dict) -> float:
        """Calculate how well student fits award criteria."""
        score = 0
        student_spike = student.get("spike", "").lower()
        award_focus = award.get("focus_area", "").lower()
        ideal_candidate = str(award.get("ideal_candidate", "")).lower()

        # Spike alignment (0-40 points)
        if student_spike and (student_spike in award_focus or student_spike in ideal_candidate):
            score += 40
        elif self._has_partial_overlap(student_spike, award_focus):
            score += 25

        # Activity evidence (0-30 points)
        activities = student.get("activities", [])
        relevant_count = self._count_relevant_activities(activities, award)
        score += min(relevant_count * 10, 30)

        # Narrative connection (0-30 points)
        brand_statement = student.get("brand_statement", "").lower()
        award_mission = award.get("mission", "").lower()
        if self._narrative_connects(brand_statement, award_mission):
            score += 30
        elif self._narrative_connects(brand_statement, award_focus):
            score += 20

        return score

    def _estimate_submission_quality(self, student: Dict, award: Dict) -> float:
        """Estimate potential submission quality."""
        score = 50  # Base score

        if student.get("has_working_project"):
            score += 20
        if student.get("project_users", 0) > 1000:
            score += 15
        elif student.get("project_users", 0) > 100:
            score += 10
        if student.get("application_time_available", "medium") == "high":
            score += 15
        elif student.get("application_time_available", "medium") == "medium":
            score += 10

        return min(score, 100)

    def _has_vulnerability_story(self, student: Dict, award: Dict) -> bool:
        """Check if student has vulnerability story that matches award."""
        vulnerability_awards = ["ncwit", "cameron", "coolidge", "breakthrough"]
        award_name = award.get("name", "").lower()

        if not any(va in award_name for va in vulnerability_awards):
            return False

        return (
            student.get("has_overcome_barrier", False) or
            student.get("is_underrepresented", False) or
            student.get("has_origin_story", False)
        )

    def _has_identity_alignment(self, student: Dict, award: Dict) -> bool:
        """Check if student identity aligns with award's diversity goals."""
        identity_awards = {
            "ncwit": ["female", "woman", "girl"],
            "nsbe": ["black", "african american"],
            "shpe": ["hispanic", "latino", "latina"],
        }
        award_name = award.get("name", "").lower()
        student_identity = [i.lower() for i in student.get("identity", [])]

        for award_key, identities in identity_awards.items():
            if award_key in award_name:
                if any(sid in " ".join(student_identity) for sid in identities):
                    return True
        return False

    def _has_partial_overlap(self, text1: str, text2: str) -> bool:
        """Check for partial word overlap between two texts."""
        if not text1 or not text2:
            return False
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        common_words = {"the", "a", "an", "and", "or", "for", "to", "in", "of", "with"}
        overlap = words1.intersection(words2) - common_words
        return len(overlap) >= 2

    def _count_relevant_activities(self, activities: List, award: Dict) -> int:
        """Count activities relevant to award."""
        if not activities:
            return 0
        award_focus = award.get("focus_area", "").lower()
        award_keywords = set(re.findall(r'\w+', award_focus))

        count = 0
        for activity in activities:
            if isinstance(activity, dict):
                activity_text = activity.get("name", "") + " " + activity.get("description", "")
            else:
                activity_text = str(activity)
            activity_words = set(re.findall(r'\w+', activity_text.lower()))
            if activity_words.intersection(award_keywords):
                count += 1
        return count

    def _narrative_connects(self, brand: str, target: str) -> bool:
        """Check if brand narrative connects to target."""
        if not brand or not target:
            return False
        brand_words = set(re.findall(r'\w+', brand))
        target_words = set(re.findall(r'\w+', target))
        common_words = {"the", "a", "an", "and", "or", "for", "to", "in", "of", "with", "is", "are"}
        overlap = brand_words.intersection(target_words) - common_words
        return len(overlap) >= 3

    def _classify_tier(self, probability: float) -> str:
        """Classify award into tier based on probability."""
        if probability >= self.LIKELY_THRESHOLD:
            return "likely"
        elif probability >= self.TARGET_THRESHOLD:
            return "target"
        return "stretch"

    def _generate_reasoning(
        self,
        fit: float,
        competition: float,
        quality: float,
        vulnerability: bool,
        identity: bool,
        award: Dict
    ) -> str:
        """Generate human-readable reasoning for probability."""
        parts = []

        if fit >= 60:
            parts.append(f"Strong fit with {award.get('name', 'this award')}'s focus")
        elif fit >= 40:
            parts.append("Moderate fit with award focus")
        else:
            parts.append("Could strengthen fit with award focus")

        if competition >= 60:
            parts.append("relatively accessible competition level")
        elif competition >= 40:
            parts.append("competitive but achievable")
        else:
            parts.append("highly competitive")

        if vulnerability:
            parts.append("+15% vulnerability storytelling bonus")
        if identity:
            parts.append("+10% identity alignment bonus")

        return "; ".join(parts)

    def build_balanced_portfolio(
        self,
        student: Dict[str, Any],
        awards: List[Dict[str, Any]]
    ) -> Portfolio:
        """Build a 2-2-1 balanced awards portfolio."""
        # Score all awards
        scored = [self.calculate_probability(student, award) for award in awards]
        scored.sort(key=lambda x: x.probability, reverse=True)

        # Separate by tier
        likely_pool = [a for a in scored if a.tier == "likely"]
        target_pool = [a for a in scored if a.tier == "target"]
        stretch_pool = [a for a in scored if a.tier == "stretch"]

        # Select 2-2-1
        likely = likely_pool[:2]
        target = target_pool[:2]
        stretch = stretch_pool[:1]

        # Adjust if pools are unbalanced
        if len(likely) < 2 and len(target) > 2:
            likely.extend(target[2:4 - len(likely)])
            target = target[:2]
        if len(stretch) < 1 and len(target) > 2:
            stretch.append(target[-1])
            target = target[:-1]

        # Calculate metrics
        all_selected = likely + target + stretch
        expected_wins = sum(a.probability / 100 for a in all_selected)
        balance = self._calculate_balance_score(likely, target, stretch)
        recommendations = self._generate_portfolio_recommendations(
            student, likely, target, stretch
        )

        return Portfolio(
            likely=likely,
            target=target,
            stretch=stretch,
            balance_score=balance,
            total_expected_wins=round(expected_wins, 2),
            recommendations=recommendations
        )

    def _calculate_balance_score(
        self,
        likely: List,
        target: List,
        stretch: List
    ) -> float:
        """Calculate how well portfolio matches 2-2-1 ideal."""
        ideal = {"likely": 2, "target": 2, "stretch": 1}
        actual = {"likely": len(likely), "target": len(target), "stretch": len(stretch)}

        score = 100
        for tier, ideal_count in ideal.items():
            diff = abs(actual[tier] - ideal_count)
            score -= diff * 15

        return max(score, 0)

    def _generate_portfolio_recommendations(
        self,
        student: Dict,
        likely: List,
        target: List,
        stretch: List
    ) -> List[str]:
        """Generate recommendations for improving portfolio."""
        recommendations = []

        if len(likely) < 2:
            recommendations.append(
                "Consider adding more 'likely' awards to ensure some wins. "
                "Look for local/regional competitions in your spike area."
            )

        if len(stretch) == 0:
            recommendations.append(
                "Add a stretch goal! Even unlikely awards provide practice "
                "and occasionally surprise us."
            )

        if not recommendations:
            recommendations.append(
                "Great portfolio balance! Focus on strong applications for each."
            )

        return recommendations

    def format_portfolio_summary(self, portfolio: Portfolio) -> str:
        """Format portfolio in Jenny's style."""
        lines = ["Based on your profile, here's your 2-2-1 portfolio:\n"]

        lines.append("**Likely (60%+ chance):**")
        for a in portfolio.likely:
            lines.append(f"- {a.award_name} ({a.probability:.0f}%)")

        lines.append("\n**Target (40-60% chance):**")
        for a in portfolio.target:
            lines.append(f"- {a.award_name} ({a.probability:.0f}%)")

        lines.append("\n**Stretch (reach for the stars):**")
        for a in portfolio.stretch:
            lines.append(f"- {a.award_name} ({a.probability:.0f}%)")

        lines.append(f"\n**Expected wins:** {portfolio.total_expected_wins:.1f} awards")
        lines.append(f"**Portfolio balance:** {portfolio.balance_score:.0f}%")

        lines.append("\n**Recommendations:**")
        for rec in portfolio.recommendations:
            lines.append(f"- {rec}")

        lines.append("\nWhich of these feels most exciting to start with?")

        return "\n".join(lines)

    def to_dict(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Convert Portfolio to dictionary for API response."""
        def award_to_dict(a: AwardProbability) -> Dict:
            return {
                "award_id": a.award_id,
                "award_name": a.award_name,
                "probability": a.probability,
                "tier": a.tier,
                "fit_score": a.fit_score,
                "competition_factor": a.competition_factor,
                "vulnerability_bonus": a.vulnerability_bonus,
                "identity_bonus": a.identity_bonus,
                "reasoning": a.reasoning,
            }

        return {
            "likely": [award_to_dict(a) for a in portfolio.likely],
            "target": [award_to_dict(a) for a in portfolio.target],
            "stretch": [award_to_dict(a) for a in portfolio.stretch],
            "balance_score": portfolio.balance_score,
            "total_expected_wins": portfolio.total_expected_wins,
            "recommendations": portfolio.recommendations,
        }


__all__ = ['AwardsProbabilityEngine', 'AwardProbability', 'Portfolio']
