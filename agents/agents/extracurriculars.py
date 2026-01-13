# Extracurriculars Agent - Complete Implementation
# File: agents/agents/extracurriculars.py
#
# This agent runs FIRST in the orchestration pipeline to produce
# identity synthesis that feeds into Awards and Programs agents.
#
# Architecture:
# EC Agent (FIRST) → identity_synthesis → Awards + Programs (PARALLEL)
#
# Primitives:
# - TYPE-013: Portfolio Optimization (balance across categories)
# - TYPE-014: Narrative Synthesis (create identity from ECs)
# - TYPE-015: Impact Assessment (evaluate activity impact)

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import json

from langchain_openai import ChatOpenAI

from tools.database import get_supabase_client, get_profile_with_assessment


# =============================================================================
# CONSTANTS & TYPES
# =============================================================================

# 8 Archetypes from strategic intelligence schema
ARCHETYPES = [
    "academic_powerhouse",
    "stem_innovator",
    "creative_visionary",
    "community_changemaker",
    "entrepreneurial_leader",
    "humanities_scholar",
    "athletic_scholar",
    "multi_hyphenate",
]

# Activity category weights for portfolio balance
CATEGORY_WEIGHTS = {
    "academic": 0.25,
    "leadership": 0.20,
    "community_service": 0.20,
    "arts_creative": 0.15,
    "athletics": 0.10,
    "work_experience": 0.10,
}

# Minimum portfolio balance thresholds
MIN_ACTIVITIES_PER_CATEGORY = {
    "academic": 1,
    "leadership": 1,
    "community_service": 1,
    "arts_creative": 0,
    "athletics": 0,
    "work_experience": 0,
}

# Impact scoring rubric
IMPACT_LEVELS = {
    "transformative": {"score": 10, "description": "Changed lives, created lasting systems"},
    "significant": {"score": 8, "description": "Measurable community/organizational impact"},
    "moderate": {"score": 6, "description": "Visible contributions, some outcomes"},
    "developing": {"score": 4, "description": "Participation with some responsibility"},
    "basic": {"score": 2, "description": "Attendance-level involvement"},
}


@dataclass
class IdentitySynthesis:
    """
    Output from EC Agent that feeds into Awards/Programs agents.
    This is the core identity signal extracted from extracurriculars.
    """
    spike: str = ""
    spike_evidence: List[str] = field(default_factory=list)
    archetype: str = "multi_hyphenate"
    archetype_confidence: float = 0.5
    archetype_scores: Dict[str, float] = field(default_factory=dict)
    pillars: List[str] = field(default_factory=list)
    pillar_evidence: Dict[str, List[str]] = field(default_factory=dict)
    portfolio_balance_score: float = 0.0
    portfolio_gaps: List[str] = field(default_factory=list)
    portfolio_strengths: List[str] = field(default_factory=list)
    total_impact_score: float = 0.0
    top_impact_activities: List[Dict] = field(default_factory=list)
    leadership_level: str = "member"
    leadership_evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spike": self.spike,
            "spike_evidence": self.spike_evidence,
            "archetype": self.archetype,
            "archetype_confidence": self.archetype_confidence,
            "archetype_scores": self.archetype_scores,
            "pillars": self.pillars,
            "pillar_evidence": self.pillar_evidence,
            "portfolio_balance_score": self.portfolio_balance_score,
            "portfolio_gaps": self.portfolio_gaps,
            "portfolio_strengths": self.portfolio_strengths,
            "total_impact_score": self.total_impact_score,
            "top_impact_activities": self.top_impact_activities,
            "leadership_level": self.leadership_level,
            "leadership_evidence": self.leadership_evidence,
        }


@dataclass
class PortfolioAnalysis:
    """Detailed portfolio analysis result"""
    activities_by_category: Dict[str, List[Dict]] = field(default_factory=dict)
    category_counts: Dict[str, int] = field(default_factory=dict)
    category_hours: Dict[str, float] = field(default_factory=dict)
    balance_score: float = 0.0
    gaps: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ExtracurricularsAgent:
    """
    Extracurriculars Agent: Analyzes EC portfolio to produce identity synthesis

    Primitives Used:
    - TYPE-013: Portfolio Optimization
    - TYPE-014: Narrative Synthesis
    - TYPE-015: Impact Assessment

    Runs FIRST in orchestration pipeline.
    """

    def __init__(self):
        self.name = "Extracurriculars"
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.db = get_supabase_client()

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """Main processing entry point."""
        return await self.analyze(profile_id)

    async def analyze(self, profile_id: str) -> Dict[str, Any]:
        """Main analysis pipeline."""
        try:
            profile = await self._get_profile(profile_id)
            if not profile:
                return self._placeholder_response(profile_id)

            activities = self._extract_activities(profile)
            if not activities:
                return self._placeholder_response(profile_id,
                    message="Add extracurricular activities to generate analysis")

            # TYPE-013: Portfolio Optimization
            portfolio_analysis = self._analyze_portfolio_balance(activities)

            # TYPE-014: Narrative Synthesis
            identity_synthesis = await self._synthesize_identity(
                profile, activities, portfolio_analysis
            )

            # TYPE-015: Impact Assessment
            impact_assessment = self._assess_impact(activities)
            identity_synthesis.total_impact_score = impact_assessment["total_score"]
            identity_synthesis.top_impact_activities = impact_assessment["top_activities"]

            await self._version_state(profile_id, "ec_analyzed", {
                "activities_count": len(activities),
                "spike": identity_synthesis.spike,
                "archetype": identity_synthesis.archetype,
            })

            await self._publish_event("EC_IDENTITY_SYNTHESIZED", {
                "profileId": profile_id,
                "spike": identity_synthesis.spike,
                "archetype": identity_synthesis.archetype,
                "pillars": identity_synthesis.pillars,
            })

            return {
                "success": True,
                "profile_id": profile_id,
                "identity_synthesis": identity_synthesis.to_dict(),
                "portfolio_analysis": {
                    "category_counts": portfolio_analysis.category_counts,
                    "balance_score": portfolio_analysis.balance_score,
                    "gaps": portfolio_analysis.gaps,
                    "strengths": portfolio_analysis.strengths,
                    "recommendations": portfolio_analysis.recommendations,
                },
                "impact_assessment": impact_assessment,
                "activities_analyzed": len(activities),
            }

        except Exception as e:
            import traceback
            print(f"[ExtracurricularsAgent] ERROR: {str(e)}")
            print(traceback.format_exc())
            return {"success": False, "error": str(e)}

    def _analyze_portfolio_balance(self, activities: List[Dict]) -> PortfolioAnalysis:
        """TYPE-013: Portfolio Optimization"""
        analysis = PortfolioAnalysis()

        for activity in activities:
            category = self._categorize_activity(activity)
            if category not in analysis.activities_by_category:
                analysis.activities_by_category[category] = []
            analysis.activities_by_category[category].append(activity)

        for category in CATEGORY_WEIGHTS.keys():
            count = len(analysis.activities_by_category.get(category, []))
            analysis.category_counts[category] = count
            hours = sum(
                a.get("hours_per_week", 0) * a.get("weeks_per_year", 40)
                for a in analysis.activities_by_category.get(category, [])
            )
            analysis.category_hours[category] = hours

        total_activities = len(activities) if activities else 1
        balance_scores = []
        for category, weight in CATEGORY_WEIGHTS.items():
            actual_ratio = analysis.category_counts[category] / total_activities
            if weight > 0:
                ratio_score = min(actual_ratio / weight, weight / max(actual_ratio, 0.01))
                balance_scores.append(ratio_score * weight)
            else:
                balance_scores.append(weight)

        analysis.balance_score = min(1.0, sum(balance_scores) / sum(CATEGORY_WEIGHTS.values()))

        for category, min_count in MIN_ACTIVITIES_PER_CATEGORY.items():
            if analysis.category_counts[category] < min_count:
                analysis.gaps.append(category)

        for category, count in analysis.category_counts.items():
            if count >= 2 or analysis.category_hours.get(category, 0) >= 100:
                analysis.strengths.append(category)

        analysis.recommendations = self._generate_portfolio_recommendations(analysis)
        return analysis

    def _categorize_activity(self, activity: Dict) -> str:
        """Categorize an activity into portfolio categories"""
        category = activity.get("category", "").lower()
        category_mapping = {
            "academic": ["academic", "research", "science", "math", "stem", "olympiad"],
            "leadership": ["leadership", "president", "captain", "founder", "officer"],
            "community_service": ["service", "volunteer", "community", "nonprofit", "charity"],
            "arts_creative": ["art", "music", "theater", "creative", "writing", "film", "media"],
            "athletics": ["athletic", "sport", "team", "varsity", "jv"],
            "work_experience": ["work", "intern", "job", "employment", "business"],
        }

        for cat, keywords in category_mapping.items():
            if category in keywords:
                return cat

        text = f"{activity.get('name', '')} {activity.get('description', '')}".lower()
        for cat, keywords in category_mapping.items():
            for keyword in keywords:
                if keyword in text:
                    return cat

        role = activity.get("role", "").lower()
        if any(r in role for r in ["president", "captain", "founder", "chair", "director"]):
            return "leadership"

        return "academic"

    def _generate_portfolio_recommendations(self, analysis: PortfolioAnalysis) -> List[str]:
        """Generate recommendations based on portfolio analysis"""
        recommendations = []

        if "community_service" in analysis.gaps:
            recommendations.append(
                "Add a community service activity - consider tutoring or volunteering"
            )

        if "leadership" in analysis.gaps:
            recommendations.append(
                "Seek leadership roles in existing activities"
            )

        if analysis.balance_score < 0.5:
            dominant = max(analysis.category_counts.items(), key=lambda x: x[1])[0]
            recommendations.append(
                f"Portfolio is heavily weighted toward {dominant.replace('_', ' ')}. Consider diversifying"
            )

        if not recommendations:
            recommendations.append("Portfolio is well-balanced. Focus on deepening impact")

        return recommendations

    async def _synthesize_identity(
        self, profile: Dict, activities: List[Dict], portfolio_analysis: PortfolioAnalysis
    ) -> IdentitySynthesis:
        """TYPE-014: Narrative Synthesis"""
        synthesis = IdentitySynthesis()

        spike, spike_evidence = self._extract_spike(activities, profile)
        synthesis.spike = spike
        synthesis.spike_evidence = spike_evidence

        archetype, confidence, scores = self._determine_archetype(activities, spike, portfolio_analysis)
        synthesis.archetype = archetype
        synthesis.archetype_confidence = confidence
        synthesis.archetype_scores = scores

        pillars, pillar_evidence = self._extract_pillars(activities)
        synthesis.pillars = pillars
        synthesis.pillar_evidence = pillar_evidence

        leadership, evidence = self._assess_leadership(activities)
        synthesis.leadership_level = leadership
        synthesis.leadership_evidence = evidence

        synthesis.portfolio_balance_score = portfolio_analysis.balance_score
        synthesis.portfolio_gaps = portfolio_analysis.gaps
        synthesis.portfolio_strengths = portfolio_analysis.strengths

        return synthesis

    def _extract_spike(self, activities: List[Dict], profile: Dict) -> Tuple[str, List[str]]:
        """Extract student's spike (primary passion/focus area)"""
        category_signals = {}

        for activity in activities:
            category = self._categorize_activity(activity)
            if category not in category_signals:
                category_signals[category] = {"hours": 0, "leadership_weight": 0, "activities": []}

            hours = activity.get("hours_per_week", 3) * activity.get("weeks_per_year", 40)
            category_signals[category]["hours"] += hours
            category_signals[category]["activities"].append(activity.get("name", "Activity"))

            role = activity.get("role", "member").lower()
            if "founder" in role:
                category_signals[category]["leadership_weight"] += 10
            elif "president" in role or "captain" in role:
                category_signals[category]["leadership_weight"] += 8
            elif "officer" in role:
                category_signals[category]["leadership_weight"] += 5
            else:
                category_signals[category]["leadership_weight"] += 1

        category_scores = {}
        for cat, signals in category_signals.items():
            score = signals["hours"] * 0.5 + signals["leadership_weight"] * 10
            category_scores[cat] = score

        if category_scores:
            spike = max(category_scores.items(), key=lambda x: x[1])[0]
            evidence = category_signals[spike]["activities"][:3]
        else:
            spike = "general"
            evidence = []

        profile_data = profile.get("profile_data", {})
        passion = profile_data.get("passion", {})
        if passion.get("spike_category"):
            spike = passion["spike_category"].lower().replace("_", " ")

        return spike, evidence

    def _determine_archetype(
        self, activities: List[Dict], spike: str, portfolio_analysis: PortfolioAnalysis
    ) -> Tuple[str, float, Dict[str, float]]:
        """Determine which of the 8 archetypes best fits"""
        scores = {arch: 0.0 for arch in ARCHETYPES}

        for activity in activities:
            category = self._categorize_activity(activity)
            text = f"{activity.get('name', '')} {activity.get('description', '')}".lower()

            if category == "academic" or "research" in text or "olympiad" in text:
                scores["academic_powerhouse"] += 0.15

            if any(kw in text for kw in ["code", "programming", "engineering", "robot", "app"]):
                scores["stem_innovator"] += 0.15

            if category == "arts_creative" or any(kw in text for kw in ["art", "music", "film", "theater"]):
                scores["creative_visionary"] += 0.15

            if category == "community_service" or "volunteer" in text:
                scores["community_changemaker"] += 0.15

            if any(kw in text for kw in ["business", "startup", "founder", "entrepreneur"]):
                scores["entrepreneurial_leader"] += 0.15

            if any(kw in text for kw in ["history", "philosophy", "debate", "mun", "literature"]):
                scores["humanities_scholar"] += 0.15

            if category == "athletics" or "varsity" in text or "captain" in text:
                scores["athletic_scholar"] += 0.15

        spike_archetype_map = {
            "academic": "academic_powerhouse",
            "stem": "stem_innovator",
            "arts": "creative_visionary",
            "service": "community_changemaker",
            "business": "entrepreneurial_leader",
            "humanities": "humanities_scholar",
            "athletics": "athletic_scholar",
        }

        for keyword, archetype in spike_archetype_map.items():
            if keyword in spike.lower():
                scores[archetype] += 0.3

        if len(portfolio_analysis.strengths) >= 3:
            scores["multi_hyphenate"] += 0.4

        max_score = max(scores.values()) if scores.values() else 1
        for arch in scores:
            scores[arch] = round(scores[arch] / max(max_score, 1), 2)

        best_archetype = max(scores.items(), key=lambda x: x[1])
        return best_archetype[0], best_archetype[1], scores

    def _extract_pillars(self, activities: List[Dict]) -> Tuple[List[str], Dict[str, List[str]]]:
        """Extract 3-5 narrative pillars from activities"""
        pillar_keywords = {
            "innovation": ["create", "build", "develop", "design", "invent"],
            "leadership": ["lead", "president", "captain", "founder", "organize"],
            "community_impact": ["volunteer", "service", "help", "community"],
            "academic_excellence": ["research", "competition", "olympiad", "honors"],
            "creative_expression": ["art", "music", "write", "perform"],
            "advocacy": ["advocate", "voice", "rights", "justice", "change"],
            "mentorship": ["teach", "tutor", "mentor", "guide"],
        }

        pillar_evidence = {pillar: [] for pillar in pillar_keywords}

        for activity in activities:
            text = f"{activity.get('name', '')} {activity.get('description', '')}".lower()
            for pillar, keywords in pillar_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        pillar_evidence[pillar].append(activity.get("name", "Activity"))
                        break

        pillars_with_counts = [
            (pillar, len(evidence))
            for pillar, evidence in pillar_evidence.items()
            if evidence
        ]
        pillars_with_counts.sort(key=lambda x: x[1], reverse=True)

        top_pillars = [p[0] for p in pillars_with_counts[:5]]
        clean_evidence = {pillar: pillar_evidence[pillar][:3] for pillar in top_pillars}

        if len(top_pillars) < 3:
            defaults = ["academic_excellence", "leadership", "community_impact"]
            for default in defaults:
                if default not in top_pillars and len(top_pillars) < 3:
                    top_pillars.append(default)
                    clean_evidence[default] = []

        return top_pillars, clean_evidence

    def _assess_leadership(self, activities: List[Dict]) -> Tuple[str, List[str]]:
        """Assess overall leadership level"""
        levels = {"founder": [], "president": [], "officer": [], "member": []}

        for activity in activities:
            role = activity.get("role", "member").lower()
            name = activity.get("name", "Activity")

            if "founder" in role:
                levels["founder"].append(name)
            elif "president" in role or "captain" in role:
                levels["president"].append(name)
            elif any(r in role for r in ["officer", "vice", "secretary", "treasurer"]):
                levels["officer"].append(name)
            else:
                levels["member"].append(name)

        if levels["founder"]:
            return "founder", levels["founder"]
        elif levels["president"]:
            return "president", levels["president"]
        elif levels["officer"]:
            return "officer", levels["officer"]
        return "member", levels["member"][:3]

    def _assess_impact(self, activities: List[Dict]) -> Dict[str, Any]:
        """TYPE-015: Impact Assessment"""
        assessed_activities = []

        for activity in activities:
            impact = self._calculate_activity_impact(activity)
            assessed_activities.append({
                "name": activity.get("name", "Activity"),
                "impact_score": impact["score"],
                "impact_level": impact["level"],
                "impact_factors": impact["factors"],
            })

        assessed_activities.sort(key=lambda x: x["impact_score"], reverse=True)

        total_score = sum(a["impact_score"] for a in assessed_activities)
        max_possible = len(assessed_activities) * 10
        normalized_score = (total_score / max_possible * 100) if max_possible > 0 else 0

        return {
            "total_score": round(normalized_score, 1),
            "activities_assessed": len(assessed_activities),
            "top_activities": assessed_activities[:5],
        }

    def _calculate_activity_impact(self, activity: Dict) -> Dict[str, Any]:
        """Calculate impact score for a single activity"""
        score = 0
        factors = []

        hours = activity.get("hours_per_week", 0) * activity.get("weeks_per_year", 0)
        if hours >= 200:
            score += 2
            factors.append("High time commitment")
        elif hours >= 100:
            score += 1

        role = activity.get("role", "member").lower()
        if "founder" in role:
            score += 3
            factors.append("Founded organization")
        elif "president" in role or "captain" in role:
            score += 2
            factors.append("Top leadership")
        elif "officer" in role:
            score += 1

        level = activity.get("level", "school").lower()
        if "national" in level or "international" in level:
            score += 3
            factors.append("National/International scope")
        elif "state" in level:
            score += 2

        if activity.get("awards"):
            score += 2
            factors.append("Awards/Recognition")

        if score >= 8:
            level_name = "transformative"
        elif score >= 6:
            level_name = "significant"
        elif score >= 4:
            level_name = "moderate"
        elif score >= 2:
            level_name = "developing"
        else:
            level_name = "basic"

        return {"score": min(10, score), "level": level_name, "factors": factors}

    def _extract_activities(self, profile: Dict) -> List[Dict]:
        """Extract activities from profile data"""
        profile_data = profile.get("profile_data", {})

        if profile_data.get("activities"):
            return profile_data["activities"]
        elif profile_data.get("extracurriculars"):
            return profile_data["extracurriculars"]
        elif profile.get("activities"):
            return profile["activities"]

        return []

    def _placeholder_response(self, profile_id: str, message: str = None) -> Dict[str, Any]:
        """Return placeholder response"""
        return {
            "success": True,
            "profile_id": profile_id,
            "identity_synthesis": IdentitySynthesis().to_dict(),
            "portfolio_analysis": {
                "category_counts": {},
                "balance_score": 0,
                "gaps": list(MIN_ACTIVITIES_PER_CATEGORY.keys()),
                "strengths": [],
                "recommendations": [message or "Complete your profile to generate EC analysis"],
            },
            "impact_assessment": {"total_score": 0, "activities_assessed": 0, "top_activities": []},
            "activities_analyzed": 0,
            "placeholder": True,
        }

    async def _get_profile(self, profile_id: str) -> Optional[Dict]:
        """Get profile with assessment data."""
        return await get_profile_with_assessment(profile_id)

    async def _version_state(self, profile_id: str, event: str, state: Dict, created_by: str = "agent"):
        """Version state change"""
        try:
            version_result = self.db.rpc("get_next_version", {
                "p_profile_id": profile_id,
                "p_agent": self.name
            }).execute()

            self.db.table("agent_state_versions").insert({
                "profile_id": profile_id,
                "agent": self.name,
                "state": state,
                "version": version_result.data if version_result.data else 1,
                "event_type": event,
                "created_by": created_by
            }).execute()
        except Exception as e:
            print(f"State versioning warning: {e}")

    async def _publish_event(self, event_type: str, payload: Dict):
        """Publish event"""
        try:
            self.db.table("events").insert({
                "type": event_type,
                "payload": payload,
                "created_at": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Event publishing warning: {e}")


# Singleton instance
extracurriculars_agent = ExtracurricularsAgent()

# Export class
ExtracurricularsAgent = ExtracurricularsAgent
