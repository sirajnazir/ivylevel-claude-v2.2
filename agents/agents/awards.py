"""
IvyQuest v10.0 Awards Agent
===========================
Matches and optimizes award applications.

Primitives:
- ACP-001: Hidden Probability Matrix (win probability calculation)
- ACP-005: Multi-Touchpoint Leverage

Autonomy: FULL (deterministic matching)

Huda Benchmark: >40% win rate (Huda actual: 62.5% = 5/8)
"""

from typing import Dict, Any, Optional, List
from .base import BaseAgent
from config import AutonomyLevel
from tools.database import get_profile, get_awards

import structlog

logger = structlog.get_logger()


class AwardsAgent(BaseAgent):
    """
    Awards Agent: Matches students to awards with ROI optimization.

    Key Responsibilities:
    1. Match Awards - Filter by eligibility
    2. Calculate Award ROI - Win probability vs effort
    3. Balance Portfolio - Likely + stretch + skip
    """

    def __init__(self):
        super().__init__(
            name="Awards",
            autonomy_level=AutonomyLevel.FULL
        )

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """Main processing entry point."""
        return await self.match(profile_id)

    async def match(self, profile_id: str) -> Dict[str, Any]:
        """Match profile to awards with ROI calculation."""
        self._log_start("match_awards", profile_id=profile_id)

        profile = await self._get_profile(profile_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}

        # Get all active awards
        awards = await get_awards()

        # Filter by eligibility
        eligible_awards = self._filter_by_eligibility(awards, profile)

        # Calculate ROI for each
        matched_awards = []
        for award in eligible_awards:
            roi = self._calculate_award_roi(award, profile)
            matched_awards.append({
                **award,
                "win_probability": roi["probability"],
                "roi_score": roi["roi"],
                "recommendation": roi["recommendation"],
            })

        # Sort by ROI
        matched_awards.sort(key=lambda x: x["roi_score"], reverse=True)

        # Balance portfolio
        portfolio = self._balance_portfolio(matched_awards)

        self._log_complete("match_awards", profile_id=profile_id, matches=len(matched_awards))

        return {
            "success": True,
            "total_matches": len(matched_awards),
            "portfolio": portfolio,
            "top_recommendations": matched_awards[:10],
        }

    def _filter_by_eligibility(self, awards: List[Dict], profile: Dict) -> List[Dict]:
        """Filter awards by eligibility criteria."""
        eligible = []
        grade = profile.get("grade", 11)

        for award in awards:
            eligibility = award.get("eligibility", {})

            # Check grade eligibility
            eligible_grades = eligibility.get("grades", [9, 10, 11, 12])
            if grade not in eligible_grades:
                continue

            eligible.append(award)

        return eligible

    def _calculate_award_roi(self, award: Dict, profile: Dict) -> Dict:
        """Calculate win probability and ROI."""
        base_rate = award.get("historical_win_rate", 0.1)
        effort_hours = award.get("effort_hours", 20)
        prestige = award.get("prestige_score", 5)

        # Adjust probability based on profile strength
        # TODO: Implement full probability model
        probability = min(base_rate * 1.5, 0.95)

        # ROI = (probability × prestige) / effort
        roi = (probability * prestige) / max(effort_hours, 1)

        # Recommendation based on probability
        if probability > 0.5:
            recommendation = "likely"
        elif probability > 0.2:
            recommendation = "stretch"
        else:
            recommendation = "skip"

        return {
            "probability": round(probability, 3),
            "roi": round(roi, 4),
            "recommendation": recommendation,
        }

    def _balance_portfolio(self, awards: List[Dict]) -> Dict:
        """Balance portfolio: likely + stretch + skip."""
        likely = [a for a in awards if a.get("recommendation") == "likely"]
        stretch = [a for a in awards if a.get("recommendation") == "stretch"]
        skip = [a for a in awards if a.get("recommendation") == "skip"]

        return {
            "likely": likely[:3],  # Top 3 likely
            "stretch": stretch[:3],  # Top 3 stretch
            "skip_count": len(skip),
        }
