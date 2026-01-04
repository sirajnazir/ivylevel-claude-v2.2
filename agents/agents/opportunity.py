"""
IvyQuest v10.0 Opportunity Agent
================================
Matches summer programs and opportunities.

Primitives:
- ACP-001: Hidden Probability Matrix
- ACP-005: Multi-Touchpoint Leverage
- Advance Alerts (6-month before deadline)

Autonomy: FULL (deterministic matching)
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .base import BaseAgent
from config import AutonomyLevel
from tools.database import get_profile, get_opportunities

import structlog

logger = structlog.get_logger()


class OpportunityAgent(BaseAgent):
    """
    Opportunity Agent: Matches students to summer programs.

    Key Responsibilities:
    1. Match Opportunities - Filter by eligibility and fit
    2. Send Advance Alerts - 6 months before deadline
    3. Create Backup Cascade - Alternative options on rejection
    """

    def __init__(self):
        super().__init__(
            name="Opportunity",
            autonomy_level=AutonomyLevel.FULL
        )

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """Main processing entry point."""
        return await self.match(profile_id)

    async def match(self, profile_id: str) -> Dict[str, Any]:
        """Match profile to opportunities."""
        self._log_start("match_opportunities", profile_id=profile_id)

        profile = await self._get_profile(profile_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}

        # Get all active opportunities
        opportunities = await get_opportunities()

        # Filter by eligibility
        eligible = self._filter_by_eligibility(opportunities, profile)

        # Calculate fit scores
        matched = []
        for opp in eligible:
            fit = self._calculate_fit(opp, profile)
            matched.append({
                **opp,
                "fit_score": fit["score"],
                "accept_probability": fit["probability"],
                "recommendation": fit["recommendation"],
            })

        # Sort by fit
        matched.sort(key=lambda x: x["fit_score"], reverse=True)

        # Identify upcoming deadlines needing alerts
        alerts = self._generate_advance_alerts(matched)

        # Create backup cascade
        backups = self._create_backup_cascade(matched)

        self._log_complete("match_opportunities", profile_id=profile_id, matches=len(matched))

        return {
            "success": True,
            "total_matches": len(matched),
            "top_recommendations": matched[:10],
            "advance_alerts": alerts,
            "backup_cascade": backups,
        }

    def _filter_by_eligibility(self, opportunities: List[Dict], profile: Dict) -> List[Dict]:
        """Filter opportunities by eligibility."""
        eligible = []
        grade = profile.get("grade", 11)

        for opp in opportunities:
            eligibility = opp.get("eligibility", {})
            eligible_grades = eligibility.get("grades", [9, 10, 11, 12])
            if grade not in eligible_grades:
                continue
            eligible.append(opp)

        return eligible

    def _calculate_fit(self, opportunity: Dict, profile: Dict) -> Dict:
        """Calculate fit score and acceptance probability."""
        base_rate = opportunity.get("acceptance_rate", 0.1)
        prestige = opportunity.get("prestige_score", 5)

        # TODO: Implement full fit calculation
        probability = min(base_rate * 1.3, 0.95)
        fit_score = probability * prestige

        if probability > 0.4:
            recommendation = "strong_match"
        elif probability > 0.15:
            recommendation = "good_match"
        else:
            recommendation = "reach"

        return {
            "score": round(fit_score, 3),
            "probability": round(probability, 3),
            "recommendation": recommendation,
        }

    def _generate_advance_alerts(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Generate alerts for opportunities with deadlines 6+ months away.
        """
        alerts = []
        now = datetime.now()
        alert_threshold = now + timedelta(days=180)  # 6 months

        for opp in opportunities[:10]:  # Top 10 matches
            deadline = opp.get("application_deadline")
            if not deadline:
                continue

            if isinstance(deadline, str):
                try:
                    deadline = datetime.fromisoformat(deadline)
                except:
                    continue

            if deadline > alert_threshold:
                alerts.append({
                    "opportunity_id": opp.get("id"),
                    "name": opp.get("name"),
                    "deadline": deadline.isoformat(),
                    "days_until": (deadline - now).days,
                    "alert_type": "advance_planning",
                })

        return alerts

    def _create_backup_cascade(self, opportunities: List[Dict]) -> Dict:
        """
        Create backup cascade for rejections.

        For each primary target, identify 2-3 backups.
        """
        primary = opportunities[:3] if len(opportunities) >= 3 else opportunities
        backups = opportunities[3:9] if len(opportunities) > 3 else []

        return {
            "primary_targets": [o.get("name") for o in primary],
            "backup_options": [o.get("name") for o in backups],
            "cascade_depth": len(backups),
        }
