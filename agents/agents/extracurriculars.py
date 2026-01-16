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

# v4.0: Hybrid Architecture imports
from agents.core.profile_signals import ProfileSignals, extract_profile_signals
from agents.core.guardrails import validate_identity_synthesis
from config import FEATURE_FLAGS


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
        """
        Main processing entry point.

        v4.1: Accepts react_hints from ReActWrapper for self-correction.

        Args:
            profile_id: Profile to analyze
            **kwargs: Additional arguments
                - react_hints: List[str] - Improvement hints from ReAct cycle
        """
        # v4.1: Extract ReAct hints if present
        react_hints = kwargs.get("react_hints", [])
        if react_hints:
            print(f"[EC Agent] Processing with {len(react_hints)} ReAct hints")

        return await self.analyze(profile_id, react_hints=react_hints)

    async def analyze(self, profile_id: str, react_hints: List[str] = None) -> Dict[str, Any]:
        """
        Main analysis pipeline.

        Hybrid Architecture v4.0:
        - If activities exist: Use activity-based analysis (existing logic)
        - If no activities: Use profile-based inference (NEW)

        v4.1: Accepts react_hints for self-correction in ReAct cycles.

        Args:
            profile_id: Profile to analyze
            react_hints: Optional list of improvement hints from ReAct wrapper
        """
        react_hints = react_hints or []
        try:
            profile = await self._get_profile(profile_id)
            if not profile:
                return self._placeholder_response(profile_id)

            # ALWAYS extract profile signals (v4.0)
            signals = self._extract_profile_signals(profile)

            # Extract activities (may be empty)
            activities = self._extract_activities(profile)

            # =========================================================
            # HYBRID PATH SELECTION (v4.0)
            # =========================================================
            use_profile_inference = FEATURE_FLAGS.get("use_profile_inference", True)

            if activities:
                # PATH A: Activity-based analysis (existing logic)
                print(f"[EC Agent] Using activity-based analysis ({len(activities)} activities)")

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

            elif use_profile_inference and signals.has_any_signals():
                # PATH B: Profile-based inference (v4.0 NEW)
                print(f"[EC Agent] Using profile-based inference (no activities, has signals)")

                identity_synthesis = await self._synthesize_identity_from_profile(profile, signals)
                portfolio_analysis = PortfolioAnalysis()  # Empty portfolio
                portfolio_analysis.gaps = list(CATEGORY_WEIGHTS.keys())
                portfolio_analysis.recommendations = [
                    "Start building your extracurricular portfolio",
                    f"Consider activities aligned with your interest in {signals.intended_major or 'your passions'}",
                ]
                impact_assessment = {"total_score": 0, "activities_assessed": 0, "top_activities": []}

            else:
                # PATH C: Placeholder (no activities AND no signals)
                print(f"[EC Agent] No activities and no profile signals - returning placeholder")
                return self._placeholder_response(
                    profile_id,
                    message="Complete your profile to get personalized recommendations"
                )

            # Version state
            await self._version_state(profile_id, "ec_analyzed", {
                "activities_count": len(activities),
                "spike": identity_synthesis.spike,
                "archetype": identity_synthesis.archetype,
                "inference_mode": "activities" if activities else "profile_signals",
            })

            # Publish event
            await self._publish_event("EC_IDENTITY_SYNTHESIZED", {
                "profileId": profile_id,
                "spike": identity_synthesis.spike,
                "archetype": identity_synthesis.archetype,
                "pillars": identity_synthesis.pillars,
                "inference_mode": "activities" if activities else "profile_signals",
            })

            result = {
                "success": True,
                "profile_id": profile_id,
                "identity_synthesis": identity_synthesis.to_dict(),
                "portfolio_analysis": {
                    "category_counts": getattr(portfolio_analysis, 'category_counts', {}),
                    "balance_score": getattr(portfolio_analysis, 'balance_score', 0),
                    "gaps": getattr(portfolio_analysis, 'gaps', []),
                    "strengths": getattr(portfolio_analysis, 'strengths', []),
                    "recommendations": getattr(portfolio_analysis, 'recommendations', []),
                },
                "impact_assessment": impact_assessment if activities else {"total_score": 0, "activities_assessed": 0, "top_activities": []},
                "activities_analyzed": len(activities),
                "inference_mode": "activities" if activities else "profile_signals",
            }

            # v4.1: Apply ReAct hints to improve output if provided
            if react_hints:
                result = self._apply_react_hints(result, react_hints, signals)

            # v4.1: Validate output against guardrails
            if FEATURE_FLAGS.get("enable_guardrails", True):
                validation = validate_identity_synthesis(result)
                if validation.warnings:
                    result["validation_warnings"] = validation.warnings
                result["confidence"] = validation.confidence

            return result

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

    # =========================================================================
    # HYBRID ARCHITECTURE v4.0: Profile-Based Inference
    # =========================================================================

    def _extract_profile_signals(self, profile: Dict) -> ProfileSignals:
        """Extract signals from profile for inference when activities are empty."""
        return extract_profile_signals(profile)

    async def _synthesize_identity_from_profile(
        self,
        profile: Dict,
        signals: ProfileSignals
    ) -> IdentitySynthesis:
        """
        Synthesize identity when no activities exist.
        Uses profile signals (interests, major, causes) to infer spike and archetype.
        """
        synthesis = IdentitySynthesis()

        # Infer spike from profile signals
        spike, spike_evidence = self._infer_spike_from_signals(signals)
        synthesis.spike = spike
        synthesis.spike_evidence = spike_evidence

        # Score archetypes from profile signals
        archetype, confidence, scores = self._score_archetypes_from_signals(signals)
        synthesis.archetype = archetype
        synthesis.archetype_confidence = confidence
        synthesis.archetype_scores = scores

        # Generate pillars from profile signals
        pillars = self._generate_pillars_from_signals(signals)
        synthesis.pillars = pillars

        # Set portfolio as empty with recommendations
        synthesis.portfolio_balance_score = 0.0
        synthesis.portfolio_gaps = list(CATEGORY_WEIGHTS.keys())
        synthesis.portfolio_strengths = []

        # Leadership defaults to potential (no evidence yet)
        synthesis.leadership_level = "potential"
        synthesis.leadership_evidence = []

        return synthesis

    def _infer_spike_from_signals(self, signals: ProfileSignals) -> Tuple[str, List[str]]:
        """
        Infer spike from profile signals.

        Priority:
        1. Explicit spike_category from passion
        2. Intended major + interests combination
        3. Dream career + causes combination
        """
        # Priority 1: If spike_category is explicitly set, use it
        if signals.spike_category:
            spike = signals.spike_category.lower().replace("_", " ")
            evidence = [f"spike_category: {signals.spike_category}"]
            if signals.interests:
                evidence.extend(signals.interests[:2])
            return spike, evidence

        components = signals.get_spike_components()

        # Priority 2/3: Synthesize from components
        if len(components) >= 2:
            spike = f"{components[0]} + {components[1]}"
        elif len(components) == 1:
            spike = components[0]
        else:
            spike = "exploring interests"

        return spike, components[:3]

    def _score_archetypes_from_signals(
        self,
        signals: ProfileSignals
    ) -> Tuple[str, float, Dict[str, float]]:
        """
        Score archetypes based on profile signals (not activities).

        Uses:
        - intended_major, favorite_subjects → academic archetypes
        - interests, causes → passion-based archetypes
        - strengths, values → identity-based archetypes
        """
        scores = {arch: 0.0 for arch in ARCHETYPES}

        # Major to archetype mapping
        major_mapping = {
            "computer science": {"stem_innovator": 0.4, "academic_powerhouse": 0.2},
            "engineering": {"stem_innovator": 0.4, "academic_powerhouse": 0.2},
            "biology": {"stem_innovator": 0.3, "academic_powerhouse": 0.3},
            "medicine": {"stem_innovator": 0.3, "community_changemaker": 0.3},
            "business": {"entrepreneurial_leader": 0.4, "academic_powerhouse": 0.2},
            "economics": {"entrepreneurial_leader": 0.3, "academic_powerhouse": 0.3},
            "art": {"creative_visionary": 0.5},
            "music": {"creative_visionary": 0.5},
            "film": {"creative_visionary": 0.4, "entrepreneurial_leader": 0.2},
            "history": {"humanities_scholar": 0.4, "academic_powerhouse": 0.2},
            "political science": {"humanities_scholar": 0.3, "community_changemaker": 0.3},
            "law": {"humanities_scholar": 0.3, "entrepreneurial_leader": 0.3},
            "psychology": {"community_changemaker": 0.3, "humanities_scholar": 0.3},
            "education": {"community_changemaker": 0.4, "humanities_scholar": 0.2},
        }

        # Score from intended major
        major_lower = signals.intended_major.lower()
        for keyword, arch_scores in major_mapping.items():
            if keyword in major_lower:
                for arch, score in arch_scores.items():
                    scores[arch] += score

        # Score from interests
        interest_mapping = {
            "research": {"academic_powerhouse": 0.2, "stem_innovator": 0.2},
            "coding": {"stem_innovator": 0.3},
            "robotics": {"stem_innovator": 0.3},
            "ai": {"stem_innovator": 0.3},
            "art": {"creative_visionary": 0.3},
            "music": {"creative_visionary": 0.3},
            "writing": {"creative_visionary": 0.2, "humanities_scholar": 0.2},
            "debate": {"humanities_scholar": 0.3},
            "volunteer": {"community_changemaker": 0.3},
            "nonprofit": {"community_changemaker": 0.3},
            "startup": {"entrepreneurial_leader": 0.3},
            "business": {"entrepreneurial_leader": 0.3},
            "sports": {"athletic_scholar": 0.4},
        }

        for interest in signals.interests:
            interest_lower = interest.lower()
            for keyword, arch_scores in interest_mapping.items():
                if keyword in interest_lower:
                    for arch, score in arch_scores.items():
                        scores[arch] += score

        # Score from causes (boosts community_changemaker)
        if signals.causes:
            scores["community_changemaker"] += 0.2 * min(len(signals.causes), 3)

        # Score from volunteer interests
        if signals.volunteer_interests:
            scores["community_changemaker"] += 0.15 * min(len(signals.volunteer_interests), 3)

        # Score from spike_category (explicit category from assessment)
        spike_category_mapping = {
            "SERVICE": {"community_changemaker": 0.5},
            "STEM": {"stem_innovator": 0.5},
            "BUSINESS": {"entrepreneurial_leader": 0.5},
            "ARTS": {"creative_visionary": 0.5},
            "HUMANITIES": {"humanities_scholar": 0.5},
            "ATHLETICS": {"athletic_scholar": 0.5},
            "ACADEMIC": {"academic_powerhouse": 0.5},
        }
        if signals.spike_category:
            category_upper = signals.spike_category.upper()
            if category_upper in spike_category_mapping:
                for arch, score in spike_category_mapping[category_upper].items():
                    scores[arch] += score

        # Normalize scores
        max_score = max(scores.values()) if max(scores.values()) > 0 else 1
        scores = {k: round(v / max_score, 2) for k, v in scores.items()}

        # Determine primary archetype
        primary = max(scores, key=scores.get)
        confidence = scores[primary]

        # If no strong signal, default to multi_hyphenate with lower confidence
        if confidence < 0.3:
            primary = "multi_hyphenate"
            confidence = 0.4
            scores["multi_hyphenate"] = 0.4

        return primary, confidence, scores

    def _generate_pillars_from_signals(self, signals: ProfileSignals) -> List[str]:
        """Generate pillars from profile signals."""
        pillars = []

        if signals.intended_major:
            pillars.append(signals.intended_major)

        if signals.interests:
            pillars.extend(signals.interests[:2])

        if signals.causes:
            pillars.append(f"Impact: {signals.causes[0]}")

        if signals.strengths:
            pillars.append(f"Strength: {signals.strengths[0]}")

        # Limit to 5 pillars
        return pillars[:5] if pillars else ["Exploring interests", "Building foundation"]

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

    # =========================================================================
    # v4.1: ReAct Self-Correction Support
    # =========================================================================

    def _apply_react_hints(
        self,
        result: Dict[str, Any],
        hints: List[str],
        signals: "ProfileSignals"
    ) -> Dict[str, Any]:
        """
        Apply ReAct improvement hints to enhance output quality.

        This method interprets hints from the ReAct wrapper and makes
        targeted improvements to the result.

        Args:
            result: Current analysis result
            hints: List of improvement hints from ReAct
            signals: Profile signals for additional context

        Returns:
            Enhanced result with improvements applied
        """
        identity = result.get("identity_synthesis", {})

        for hint in hints:
            hint_lower = hint.lower()

            # Handle missing archetype hints
            if "archetype" in hint_lower and not identity.get("archetype"):
                # Attempt to infer archetype from signals
                if signals and signals.intended_major:
                    inferred = self._infer_archetype_from_major(signals.intended_major)
                    identity["archetype"] = inferred
                    identity["archetype_confidence"] = 0.5  # Lower confidence for inferred
                    print(f"[EC Agent] Applied hint: inferred archetype '{inferred}' from major")

            # Handle missing spike hints
            if "spike" in hint_lower and not identity.get("spike"):
                if signals:
                    components = signals.get_spike_components()
                    if components:
                        identity["spike"] = components[0]
                        identity["spike_evidence"] = components[:3]
                        print(f"[EC Agent] Applied hint: inferred spike from profile signals")

            # Handle low confidence hints
            if "confidence" in hint_lower and identity.get("archetype_confidence", 0) < 0.5:
                # Add more evidence to boost confidence
                if signals and signals.interests:
                    identity["spike_evidence"] = identity.get("spike_evidence", []) + signals.interests[:2]
                    print(f"[EC Agent] Applied hint: added evidence to boost confidence")

            # Handle pillar hints
            if "pillar" in hint_lower and len(identity.get("pillars", [])) < 3:
                if signals:
                    new_pillars = self._generate_pillars_from_signals(signals)
                    identity["pillars"] = new_pillars
                    print(f"[EC Agent] Applied hint: generated {len(new_pillars)} pillars from signals")

        result["identity_synthesis"] = identity
        result["react_hints_applied"] = len(hints)

        return result

    def _infer_archetype_from_major(self, intended_major: str) -> str:
        """Infer archetype from intended major when activities are missing."""
        major_lower = intended_major.lower()

        archetype_mapping = {
            "computer": "stem_innovator",
            "engineering": "stem_innovator",
            "physics": "academic_powerhouse",
            "math": "academic_powerhouse",
            "biology": "stem_innovator",
            "chemistry": "academic_powerhouse",
            "business": "entrepreneurial_leader",
            "economics": "entrepreneurial_leader",
            "art": "creative_visionary",
            "music": "creative_visionary",
            "film": "creative_visionary",
            "theater": "creative_visionary",
            "history": "humanities_scholar",
            "political": "humanities_scholar",
            "philosophy": "humanities_scholar",
            "psychology": "community_changemaker",
            "sociology": "community_changemaker",
            "education": "community_changemaker",
        }

        for keyword, archetype in archetype_mapping.items():
            if keyword in major_lower:
                return archetype

        return "multi_hyphenate"  # Default fallback

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
