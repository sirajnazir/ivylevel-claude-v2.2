# Awards Agent - Complete Implementation with Strategic Intelligence
# File: agents/agents/awards.py
#
# Enhanced with strategic intelligence enrichment (v1.0.0)
# Uses enriched awards data with archetype_fit, strategic_tier, win_cascade
#
# Accepts identity_synthesis from EC Agent for filtering

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os

from langchain_openai import ChatOpenAI

from tools.database import get_supabase_client, get_profile_with_assessment

# v4.0: Hybrid Architecture imports
from agents.core.guardrails import validate_awards_output
from config import FEATURE_FLAGS

# v8: Middleware Integration (40 patterns)
from .mixins import MiddlewareIntegrationMixin

import logging
mw_logger = logging.getLogger(__name__)


# Path to enriched awards data
ENRICHED_AWARDS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "seeds", "enriched", "awards_enriched.json"
)

# Portfolio strategy: 2-2-1 (2 reach, 2 target, 1 safety)
PORTFOLIO_STRATEGY = {
    "reach": {"count": 2, "tier_range": [1, 2]},     # Tier 1-2 awards
    "target": {"count": 2, "tier_range": [2, 3]},    # Tier 2-3 awards
    "safety": {"count": 1, "tier_range": [3, 4]},    # Tier 3-4 awards
}

# Minimum archetype fit score to include award
MIN_ARCHETYPE_FIT = 0.3


class AwardsAgent(MiddlewareIntegrationMixin):
    """
    Awards Agent: Matches students to awards with Strategic Intelligence

    Enhanced Features (v1.0.0):
    - Strategic tier-based filtering (Tier 1-4)
    - Archetype fit scoring (8 archetypes)
    - Win cascade positioning (entry → building → capstone)
    - 2-2-1 Portfolio Strategy (2 reach, 2 target, 1 safety)

    Primitives Used:
    - ACP-001: Hidden Probability Matrix (win probability calculation)
    - TYPE-014: Archetype-based filtering

    Accepts: identity_synthesis from EC Agent
    Autonomy: FULL (deterministic matching)

    v8: Integrated with MiddlewareStackV8 (40 patterns) for:
    - J1: Reasoning Traces
    - J3: Audit Trail (COMPLIANCE REQUIRED for award recommendations)
    - E4: Quality Scoring
    - H3: Retry Logic
    """

    def __init__(self):
        self.name = "Awards"
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.db = get_supabase_client()
        self._enriched_awards_cache = None

        # v8: Initialize middleware integration (40 patterns)
        try:
            self.init_middleware(
                supabase_client=self.db,
                llm_client=self.llm,
            )
        except Exception as e:
            mw_logger.warning(f"Middleware init failed (non-fatal): {e}")

    def _load_enriched_awards(self) -> List[Dict]:
        """Load enriched awards from JSON file with caching"""
        if self._enriched_awards_cache is not None:
            return self._enriched_awards_cache

        try:
            if os.path.exists(ENRICHED_AWARDS_PATH):
                with open(ENRICHED_AWARDS_PATH, 'r') as f:
                    self._enriched_awards_cache = json.load(f)
                    return self._enriched_awards_cache
        except Exception as e:
            print(f"[AwardsAgent] Warning: Could not load enriched awards: {e}")

        self._enriched_awards_cache = []
        return self._enriched_awards_cache

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Main processing entry point with middleware integration.

        Args:
            profile_id: Student profile ID
            identity_synthesis: (optional) Output from EC Agent with spike, archetype, pillars
            route_config: (optional) Strategic routing config from GamePlan

        v8: Integrated with MiddlewareStackV8 (40 patterns).
        """
        session_id = kwargs.get("session_id") or f"awards_{profile_id}"
        identity_synthesis = kwargs.get("identity_synthesis")
        route_config = kwargs.get("route_config", {})

        # v8: Start reasoning trace (J1)
        trace_id = self.start_reasoning_trace(
            profile_id=profile_id,
            session_id=session_id,
            input_message=f"Awards matching for profile {profile_id}",
        )

        try:
            # v8: Use middleware context (C1 Session, C2 User Context)
            async with self.with_middleware_context(
                profile_id=profile_id,
                session_id=session_id,
                task_type="awards",
            ) as ctx:
                self.add_thought(trace_id, f"Starting awards matching with identity_synthesis={identity_synthesis is not None}")

                # Execute the core matching (EXISTING LOGIC PRESERVED)
                result = await self.match(
                    profile_id,
                    identity_synthesis=identity_synthesis,
                    route_config=route_config,
                )

                self.add_action(trace_id, "matching_complete")

                # v8: Quality scoring on portfolio (E4)
                if result.get("success") and result.get("portfolio"):
                    portfolio_str = str(result.get("portfolio", {}))[:1000]
                    quality = await self.score_quality(portfolio_str, "awards_portfolio")
                    if quality:
                        result["_quality_score"] = quality.overall_score

                # v8: Finalize with middleware validation
                result = self.middleware_finalize(result, output_type="awards")

                # v8: MANDATORY Audit trail (J3) - compliance requirement
                await self.audit_action(
                    action="award_recommendation",
                    resource_type="awards",
                    resource_id=profile_id,
                    details={
                        "success": result.get("success", True),
                        "total_matches": result.get("total_matches", 0),
                        "archetype": identity_synthesis.get("archetype") if identity_synthesis else None,
                    },
                    session_id=session_id,
                    success=result.get("success", True),
                )

                # v8: Complete trace successfully
                await self.end_reasoning_trace(trace_id, success=True)

                return result

        except Exception as e:
            # v8: Record error in trace
            self.add_action(trace_id, "matching_error", metadata={"error": str(e)})

            # v8: Audit the error (J3) - compliance requirement
            await self.audit_action(
                action="award_recommendation_error",
                resource_type="awards",
                resource_id=profile_id,
                details={"error": str(e)},
                session_id=session_id,
                success=False,
            )

            # v8: Complete trace with failure
            await self.end_reasoning_trace(trace_id, success=False, error=str(e))

            # Re-raise to preserve existing error handling
            raise

    async def match(
        self,
        profile_id: str,
        identity_synthesis: Optional[Dict] = None,
        route_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Match profile to awards with Strategic Intelligence filtering.

        Uses identity_synthesis from EC Agent to filter by:
        - Archetype fit scores
        - Strategic tier positioning
        - Win cascade readiness

        Uses route_config for:
        - be_prescriptive: Whether to provide detailed action steps
        - max_recommendations: Limit results for URGENT_TRIAGE
        - timeline_horizon: Adjust recommendations based on time available
        """
        route_config = route_config or {}
        try:
            profile = await self._get_profile(profile_id)
            if not profile:
                return {
                    "success": True,
                    "total_matches": 0,
                    "portfolio": {"reach": [], "target": [], "safety": [], "skip": []},
                    "top_recommendations": [],
                    "timeline": [],
                    "strategic_insights": [],
                    "placeholder": True
                }

            # Get enriched awards (with strategic intelligence)
            awards = self._load_enriched_awards()
            if not awards:
                # Fallback to database/sample awards
                awards = await self._get_awards()

            # Extract archetype from identity_synthesis
            archetype = None
            if identity_synthesis:
                archetype = identity_synthesis.get("archetype", "multi_hyphenate")
            else:
                # Try to get from profile
                profile_data = profile.get("profile_data", {})
                archetype = profile_data.get("archetype", "multi_hyphenate")

            # Filter by eligibility
            eligible_awards = self._filter_by_eligibility(awards, profile)

            # Filter by archetype fit (if enriched data available)
            if archetype:
                eligible_awards = self._filter_by_archetype(eligible_awards, archetype)

            # Calculate win probability and strategic fit for each
            matched_awards = []
            for award in eligible_awards:
                probability = await self.calculate_win_probability(profile, award)
                effort = award.get("effort_hours", 20)
                prestige = award.get("prestige_score", 5)
                strategic_tier = award.get("strategic_tier", 3)

                # ROI = (probability × prestige × tier_boost) / effort
                tier_boost = {1: 1.5, 2: 1.2, 3: 1.0, 4: 0.8}.get(strategic_tier, 1.0)
                roi = (probability * prestige * tier_boost * 100) / max(effort, 1)

                # Get archetype fit score
                archetype_fit = 0.5
                if archetype and award.get("archetype_fit"):
                    archetype_fit = award["archetype_fit"].get(archetype, 0.5)

                matched_awards.append({
                    "award_id": award.get("id"),
                    "name": award.get("name"),
                    "category": award.get("category"),
                    "level": award.get("level"),
                    "organization": award.get("organization"),
                    "win_probability": round(probability, 3),
                    "effort_hours": effort,
                    "prestige_score": prestige,
                    "roi": round(roi, 3),
                    "deadline": award.get("deadline"),
                    "recommendation": self._get_recommendation(probability),
                    # Strategic intelligence fields
                    "strategic_tier": strategic_tier,
                    "archetype_fit": round(archetype_fit, 2),
                    "strategic_notes": award.get("strategic_notes", ""),
                    "success_patterns": award.get("success_patterns", []),
                    "common_mistakes": award.get("common_mistakes", []),
                    "win_cascade": award.get("win_cascade", {}),
                    "differentiation_factor": award.get("differentiation_factor", ""),
                })

            # Sort by ROI × archetype_fit
            matched_awards.sort(
                key=lambda x: x["roi"] * x.get("archetype_fit", 0.5),
                reverse=True
            )

            # Balance portfolio using 2-2-1 strategy
            portfolio = self.balance_portfolio_strategic(matched_awards)

            # Version state
            await self._version_state(profile_id, "awards_matched", {
                "matches_count": len(matched_awards),
                "archetype_used": archetype,
                "portfolio_summary": {
                    "reach": len(portfolio.get("reach", [])),
                    "target": len(portfolio.get("target", [])),
                    "safety": len(portfolio.get("safety", []))
                }
            })

            # Publish event for best matches
            if matched_awards:
                await self._publish_event("AWARD_MATCHED", {
                    "profileId": profile_id,
                    "awardId": matched_awards[0]["award_id"],
                    "probability": matched_awards[0]["win_probability"],
                    "archetype": archetype,
                    "strategic_tier": matched_awards[0].get("strategic_tier"),
                })

            # Generate strategic insights
            strategic_insights = self._generate_strategic_insights(
                matched_awards, archetype, identity_synthesis
            )

            # v4.0: Apply route_config adjustments
            max_recs = route_config.get("max_recommendations", 10)
            be_prescriptive = route_config.get("be_prescriptive", False)

            result = {
                "success": True,
                "total_matches": len(matched_awards),
                "portfolio": portfolio,
                "top_recommendations": matched_awards[:max_recs],
                "timeline": self._generate_timeline(matched_awards[:max_recs]),
                "strategic_insights": strategic_insights,
                "archetype_used": archetype,
                "route_config_applied": route_config if route_config else None,
            }

            # v4.0: Add prescriptive action steps if enabled
            if be_prescriptive and matched_awards:
                result["prescriptive_actions"] = self._generate_prescriptive_actions(
                    matched_awards[:3], portfolio
                )

            # v4.0: Validate output against knowledge base
            if FEATURE_FLAGS.get("enable_guardrails", True):
                validation = validate_awards_output(result, self._load_enriched_awards())
                if validation.warnings:
                    result["validation_warnings"] = validation.warnings
                result["confidence"] = validation.confidence

            return result

        except Exception as e:
            import traceback
            print(f"[AwardsAgent] ERROR: {str(e)}")
            print(traceback.format_exc())
            return {"success": False, "error": str(e)}

    def _filter_by_archetype(self, awards: List[Dict], archetype: str) -> List[Dict]:
        """
        Filter awards by archetype fit score.

        Only include awards where archetype_fit[archetype] >= MIN_ARCHETYPE_FIT
        """
        filtered = []
        for award in awards:
            archetype_fit = award.get("archetype_fit", {})
            fit_score = archetype_fit.get(archetype, 0.5)

            if fit_score >= MIN_ARCHETYPE_FIT:
                filtered.append(award)

        return filtered

    def balance_portfolio_strategic(self, awards: List[Dict]) -> Dict:
        """
        Balance portfolio using 2-2-1 strategy based on strategic tiers.

        - Reach (2): Tier 1-2 awards (low win probability, high prestige)
        - Target (2): Tier 2-3 awards (moderate win probability)
        - Safety (1): Tier 3-4 awards (higher win probability)
        """
        reach = []
        target = []
        safety = []

        for award in awards:
            tier = award.get("strategic_tier", 3)
            prob = award.get("win_probability", 0.1)

            # Categorize by tier and probability
            if tier <= 2 and prob < 0.25:
                reach.append(award)
            elif tier in [2, 3] and 0.15 <= prob <= 0.50:
                target.append(award)
            elif tier >= 3 or prob > 0.40:
                safety.append(award)
            else:
                # Default to target
                target.append(award)

        # Apply 2-2-1 limits
        portfolio = {
            "reach": reach[:PORTFOLIO_STRATEGY["reach"]["count"]],
            "target": target[:PORTFOLIO_STRATEGY["target"]["count"]],
            "safety": safety[:PORTFOLIO_STRATEGY["safety"]["count"]],
            "summary": {
                "total_awards": min(5, len(reach[:2]) + len(target[:2]) + len(safety[:1])),
                "strategy": "2-2-1 (Reach-Target-Safety)",
                "expected_wins": sum(
                    a.get("win_probability", 0)
                    for a in reach[:2] + target[:2] + safety[:1]
                ),
                "total_effort_hours": sum(
                    a.get("effort_hours", 0)
                    for a in reach[:2] + target[:2] + safety[:1]
                ),
            },
            # Win cascade sequencing
            "application_sequence": self._sequence_by_cascade(
                reach[:2] + target[:2] + safety[:1]
            )
        }

        return portfolio

    def _sequence_by_cascade(self, awards: List[Dict]) -> List[Dict]:
        """
        Sequence awards by win cascade position.

        Order: entry → building → capstone
        """
        position_order = {"entry": 0, "building": 1, "capstone": 2}

        def get_position_score(award):
            cascade = award.get("win_cascade", {})
            position = cascade.get("position", "building")
            return position_order.get(position, 1)

        sorted_awards = sorted(awards, key=get_position_score)

        sequenced = []
        for i, award in enumerate(sorted_awards):
            cascade = award.get("win_cascade", {})
            sequenced.append({
                "sequence": i + 1,
                "award_id": award.get("award_id"),
                "name": award.get("name"),
                "win_probability": award.get("win_probability"),
                "strategic_tier": award.get("strategic_tier"),
                "cascade_position": cascade.get("position", "building"),
                "prerequisites": cascade.get("prerequisites", []),
                "enables": cascade.get("enables", []),
                "rationale": self._get_cascade_rationale(cascade, i)
            })

        return sequenced

    def _get_cascade_rationale(self, cascade: Dict, position: int) -> str:
        """Generate rationale for cascade position"""
        pos = cascade.get("position", "building")

        if pos == "entry":
            return "Entry-level award - build foundation and confidence"
        elif pos == "building":
            prereqs = cascade.get("prerequisites", [])
            if prereqs:
                return f"Building award - requires: {', '.join(prereqs[:2])}"
            return "Building award - demonstrates growing expertise"
        else:
            enables = cascade.get("enables", [])
            if enables:
                return f"Capstone award - enables: {', '.join(enables[:2])}"
            return "Capstone award - crowning achievement"

    def _generate_strategic_insights(
        self,
        awards: List[Dict],
        archetype: str,
        identity_synthesis: Optional[Dict]
    ) -> List[Dict]:
        """Generate strategic insights based on matches and identity"""
        insights = []

        if not awards:
            return insights

        # Insight 1: Archetype alignment
        avg_fit = sum(a.get("archetype_fit", 0.5) for a in awards[:5]) / min(5, len(awards))
        if avg_fit >= 0.7:
            insights.append({
                "type": "archetype_alignment",
                "title": "Strong Archetype Match",
                "message": f"Your {archetype.replace('_', ' ')} profile aligns well with top recommendations (avg fit: {avg_fit:.0%})",
                "priority": "high"
            })

        # Insight 2: Tier distribution
        tier_counts = {}
        for a in awards[:10]:
            tier = a.get("strategic_tier", 3)
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        if tier_counts.get(1, 0) >= 2:
            insights.append({
                "type": "tier_opportunity",
                "title": "Elite Award Opportunities",
                "message": f"You qualify for {tier_counts.get(1, 0)} Tier-1 elite awards. These are highly competitive but transformative.",
                "priority": "high"
            })

        # Insight 3: Success pattern
        if awards and awards[0].get("success_patterns"):
            top_pattern = awards[0]["success_patterns"][0]
            insights.append({
                "type": "success_pattern",
                "title": "Key to Winning",
                "message": f"For {awards[0]['name']}: {top_pattern}",
                "priority": "medium"
            })

        # Insight 4: Common mistake to avoid
        if awards and awards[0].get("common_mistakes"):
            top_mistake = awards[0]["common_mistakes"][0]
            insights.append({
                "type": "avoid_mistake",
                "title": "Pitfall to Avoid",
                "message": f"Common mistake: {top_mistake}",
                "priority": "medium"
            })

        return insights

    def _generate_prescriptive_actions(
        self,
        top_awards: List[Dict],
        portfolio: Dict
    ) -> List[Dict]:
        """
        Generate specific, actionable steps for award applications.
        Used when be_prescriptive=True in route_config (BUILD_FRESH, URGENT_TRIAGE).
        """
        actions = []

        for i, award in enumerate(top_awards, 1):
            action = {
                "priority": i,
                "award": award.get("name"),
                "deadline": award.get("deadline"),
                "action_steps": [],
            }

            # Add specific action steps
            if award.get("deadline"):
                action["action_steps"].append(
                    f"Mark deadline on calendar: {award['deadline']}"
                )

            if award.get("effort_hours"):
                action["action_steps"].append(
                    f"Block {award['effort_hours']} hours for application prep"
                )

            if award.get("success_patterns"):
                action["action_steps"].append(
                    f"Key to winning: {award['success_patterns'][0]}"
                )

            if award.get("common_mistakes"):
                action["action_steps"].append(
                    f"Avoid: {award['common_mistakes'][0]}"
                )

            # Add portfolio context
            tier = award.get("strategic_tier", 3)
            category = "reach" if tier <= 2 else ("target" if tier == 3 else "safety")
            action["portfolio_category"] = category
            action["action_steps"].append(
                f"This is a {category.upper()} award - {'aim high!' if category == 'reach' else 'solid chance' if category == 'target' else 'good backup'}"
            )

            actions.append(action)

        # Add portfolio-level guidance
        if portfolio:
            reach_count = len(portfolio.get("reach", []))
            target_count = len(portfolio.get("target", []))
            safety_count = len(portfolio.get("safety", []))
            actions.append({
                "priority": 0,
                "award": "Portfolio Strategy",
                "action_steps": [
                    f"Your portfolio: {reach_count} reach, {target_count} target, {safety_count} safety",
                    "Recommended: 2 reach, 2 target, 1 safety (2-2-1 strategy)",
                    "Apply to safety awards first to build confidence",
                ]
            })

        return sorted(actions, key=lambda x: x["priority"])

    async def calculate_win_probability(self, profile: Dict, award: Dict) -> float:
        """
        ACP-001: Hidden Probability Matrix (Applied to Awards)

        Multi-factor probability calculation:
        probability = base_rate × strength_factor × spike_alignment × leadership_factor × demographic_factor × cri_boost
        """
        # Base rate from historical data
        base_rate = award.get("historical_win_rate", 0.10)

        # Factor 1: Profile Strength (academics + achievements)
        strength_factor = self._calculate_strength_factor(profile)

        # Factor 2: Spike Alignment (how well spike matches award category)
        spike_factor = self._calculate_spike_alignment(profile, award)

        # Factor 3: Leadership Level
        leadership_factor = self._calculate_leadership_factor(profile)

        # Factor 4: Demographic factors (if award considers diversity)
        demographic_factor = self._calculate_demographic_factor(profile, award)

        # Factor 5: CRI boost
        cri = profile.get("cri", 1.0)
        cri_factor = 1.0 + (cri - 1.0) * 0.2  # Moderate CRI impact

        # Calculate final probability
        probability = (
            base_rate *
            strength_factor *
            spike_factor *
            leadership_factor *
            demographic_factor *
            cri_factor
        )

        # Cap probability (never over 85% - nothing is certain)
        probability = min(0.85, max(0.01, probability))

        return probability

    def _calculate_strength_factor(self, profile: Dict) -> float:
        """Calculate academic/achievement strength factor (0.5 - 1.5)"""
        profile_data = profile.get("profile_data", {})
        aptitude = profile_data.get("aptitude", {})

        strength = 0.8  # Base

        # GPA impact
        gpa = aptitude.get("gpa_weighted", 3.5)
        if gpa >= 4.5:
            strength += 0.3
        elif gpa >= 4.0:
            strength += 0.2
        elif gpa >= 3.7:
            strength += 0.1

        # SAT impact
        sat = aptitude.get("sat_total", 1200)
        if sat >= 1550:
            strength += 0.2
        elif sat >= 1500:
            strength += 0.15
        elif sat >= 1450:
            strength += 0.1

        # AP courses
        ap_count = aptitude.get("ap_courses", 0)
        if ap_count >= 10:
            strength += 0.2
        elif ap_count >= 7:
            strength += 0.1
        elif ap_count >= 5:
            strength += 0.05

        return min(1.5, strength)

    def _calculate_spike_alignment(self, profile: Dict, award: Dict) -> float:
        """Calculate how well student's spike aligns with award category (0.5 - 1.5)"""
        profile_data = profile.get("profile_data", {})
        passion = profile_data.get("passion", {})

        spike = passion.get("spike_category", "GENERAL").upper()
        award_category = award.get("category", "").upper()

        # Perfect match
        if spike == award_category:
            return 1.4

        # Category mapping for related fields
        related_categories = {
            "STEM": ["SCIENCE", "TECHNOLOGY", "ENGINEERING", "MATH", "CS", "COMPUTER SCIENCE"],
            "ARTS": ["CREATIVE", "HUMANITIES", "WRITING", "MUSIC", "VISUAL"],
            "SERVICE": ["COMMUNITY", "SOCIAL", "VOLUNTEER", "NONPROFIT"],
            "LEADERSHIP": ["BUSINESS", "ENTREPRENEURSHIP", "MANAGEMENT"]
        }

        for main_cat, related in related_categories.items():
            if spike == main_cat and award_category in related:
                return 1.2
            if spike in related and award_category == main_cat:
                return 1.2

        # General award or no specific alignment
        if award_category in ["GENERAL", "ACADEMIC", ""]:
            return 1.0

        # Weak alignment
        return 0.7

    def _calculate_leadership_factor(self, profile: Dict) -> float:
        """Calculate leadership impact (0.8 - 1.4)"""
        profile_data = profile.get("profile_data", {})
        passion = profile_data.get("passion", {})

        leadership = passion.get("leadership_level", "MEMBER")

        leadership_multipliers = {
            "FOUNDER_NATIONAL": 1.4,
            "FOUNDER_STATE": 1.3,
            "NATIONAL_PRES": 1.25,
            "STATE_PRES": 1.2,
            "SCHOOL_PRES": 1.15,
            "OFFICER": 1.1,
            "MEMBER": 1.0
        }

        return leadership_multipliers.get(leadership, 1.0)

    def _calculate_demographic_factor(self, profile: Dict, award: Dict) -> float:
        """Calculate demographic boost if award considers diversity (0.9 - 1.3)"""
        if not award.get("considers_diversity", False):
            return 1.0

        profile_data = profile.get("profile_data", {})
        demographics = profile_data.get("demographics", {})

        factor = 1.0

        # First-gen boost
        if demographics.get("first_gen") or profile_data.get("operating", {}).get("firstGeneration"):
            factor += 0.1

        # Underrepresented boost
        ethnicity = demographics.get("ethnicity", "")
        if ethnicity in ["BLACK", "HISPANIC", "NATIVE_AMERICAN", "PACIFIC_ISLANDER"]:
            factor += 0.15
        elif demographics.get("underrepresented"):
            factor += 0.1

        # Gender in STEM (if relevant)
        if award.get("category", "").upper() in ["STEM", "SCIENCE", "ENGINEERING", "CS"]:
            if demographics.get("gender") == "FEMALE":
                factor += 0.1

        return min(1.3, factor)

    def _get_recommendation(self, probability: float) -> str:
        """Get recommendation tier based on probability"""
        if probability >= 0.50:
            return "likely"
        elif probability >= 0.25:
            return "target"
        else:
            return "stretch"

    def balance_portfolio(self, awards: List[Dict]) -> Dict:
        """
        Balance portfolio across risk levels:
        - Likely (>50%): Awards with strong chance of winning
        - Target (25-50%): Core strategic targets
        - Stretch (<25%): High-prestige long shots

        Optimal portfolio: 2-3 likely, 3-4 target, 1-2 stretch
        """
        likely = [a for a in awards if a.get("win_probability", 0) >= 0.50]
        target = [a for a in awards if 0.25 <= a.get("win_probability", 0) < 0.50]
        stretch = [a for a in awards if a.get("win_probability", 0) < 0.25]

        # Select optimal mix
        portfolio = {
            "likely": likely[:3],      # Top 3 likely wins
            "target": target[:4],      # Top 4 targets
            "stretch": stretch[:2],    # Top 2 stretch
            "summary": {
                "total_awards": len(likely[:3]) + len(target[:4]) + len(stretch[:2]),
                "expected_wins": sum(a.get("win_probability", 0) for a in likely[:3]) +
                               sum(a.get("win_probability", 0) for a in target[:4]) +
                               sum(a.get("win_probability", 0) for a in stretch[:2]),
                "total_effort_hours": sum(a.get("effort_hours", 0) for a in likely[:3] + target[:4] + stretch[:2]),
                "risk_distribution": {
                    "likely_count": len(likely[:3]),
                    "target_count": len(target[:4]),
                    "stretch_count": len(stretch[:2])
                }
            },
            # Jenny Intelligence: Probability Sequencing
            "application_sequence": self._sequence_applications(likely[:3] + target[:4] + stretch[:2])
        }

        return portfolio

    def _sequence_applications(self, awards: List[Dict]) -> List[Dict]:
        """
        Jenny Intelligence: Probability Sequencing
        Order awards by optimal application sequence considering:
        1. Deadline urgency
        2. Confidence building (start with likely wins)
        3. Effort distribution (avoid burnout)
        4. Synergy (similar applications together)
        """
        sequenced = []
        now = datetime.now()

        # Group by urgency and probability
        urgent_likely = []
        urgent_other = []
        regular_likely = []
        regular_other = []

        for award in awards:
            deadline = award.get("deadline")
            is_urgent = False

            if deadline:
                try:
                    if isinstance(deadline, str):
                        deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                    days_until = (deadline - now).days
                    is_urgent = days_until < 30
                except:
                    pass

            prob = award.get("win_probability", 0)

            if is_urgent and prob >= 0.50:
                urgent_likely.append(award)
            elif is_urgent:
                urgent_other.append(award)
            elif prob >= 0.50:
                regular_likely.append(award)
            else:
                regular_other.append(award)

        # Build sequence: urgent first, then likely (for confidence), then others
        sequence_order = urgent_likely + urgent_other + regular_likely + regular_other

        for i, award in enumerate(sequence_order):
            sequenced.append({
                "sequence": i + 1,
                "award_id": award.get("award_id"),
                "name": award.get("name"),
                "win_probability": award.get("win_probability"),
                "effort_hours": award.get("effort_hours"),
                "rationale": self._get_sequence_rationale(award, i)
            })

        return sequenced

    def _get_sequence_rationale(self, award: Dict, position: int) -> str:
        """Get rationale for award sequence position"""
        prob = award.get("win_probability", 0)

        if position == 0:
            if prob >= 0.50:
                return "Start with high-probability win to build momentum"
            else:
                return "Urgent deadline - apply immediately"
        elif prob >= 0.50:
            return "High-probability opportunity for confidence building"
        elif prob >= 0.25:
            return "Strategic target - balanced effort/reward ratio"
        else:
            return "Stretch goal - apply if time permits"

    async def process_rejection(self, profile_id: str, award_id: str, feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Jenny Intelligence: Rejection Alchemy
        Transform rejection into actionable improvements

        Converts setback into:
        1. Gap analysis (what was missing)
        2. Improvement actions
        3. Alternative award suggestions
        4. Narrative reframe opportunity
        """
        try:
            profile = await self._get_profile(profile_id)
            if not profile:
                return {"success": False, "error": "Profile not found"}

            # Find the award
            awards = await self._get_awards()
            award = next((a for a in awards if a.get("id") == award_id), None)
            if not award:
                return {"success": False, "error": "Award not found"}

            # Analyze potential gaps
            gaps = self._analyze_rejection_gaps(profile, award, feedback)

            # Generate improvement actions
            improvements = self._generate_improvement_actions(gaps, profile)

            # Find alternative awards
            alternatives = await self._find_alternative_awards(profile, award, awards)

            # Create narrative reframe
            narrative_reframe = self._create_rejection_narrative(award, gaps)

            # Store rejection for future probability adjustments
            await self._store_rejection_data(profile_id, award_id, gaps)

            return {
                "success": True,
                "award_name": award.get("name"),
                "gap_analysis": gaps,
                "improvement_actions": improvements,
                "alternative_awards": alternatives[:5],
                "narrative_reframe": narrative_reframe,
                "encouragement": self._get_encouragement_message(gaps)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_rejection_gaps(self, profile: Dict, award: Dict, feedback: Optional[str]) -> List[Dict]:
        """Analyze potential gaps that led to rejection"""
        gaps = []
        profile_data = profile.get("profile_data", {})
        aptitude = profile_data.get("aptitude", {})
        passion = profile_data.get("passion", {})

        # Academic gap check
        award_category = award.get("category", "").upper()
        if award_category in ["STEM", "ACADEMIC", "SCIENCE"]:
            gpa = aptitude.get("gpa_weighted", 0)
            if gpa < 4.0:
                gaps.append({
                    "area": "academics",
                    "issue": f"GPA ({gpa:.2f}) may be below competitive threshold",
                    "severity": "high" if gpa < 3.7 else "medium",
                    "improvable": True
                })

        # Leadership gap check
        leadership = passion.get("leadership_level", "MEMBER")
        if leadership in ["MEMBER", "OFFICER"] and award.get("level") == "national":
            gaps.append({
                "area": "leadership",
                "issue": f"Leadership level ({leadership}) may not demonstrate sufficient initiative",
                "severity": "medium",
                "improvable": True
            })

        # Spike alignment check
        spike = passion.get("spike_category", "GENERAL").upper()
        if spike != award_category and award_category not in ["GENERAL", "ACADEMIC"]:
            gaps.append({
                "area": "alignment",
                "issue": f"Profile spike ({spike}) doesn't align with award category ({award_category})",
                "severity": "high",
                "improvable": False  # Can't change quickly
            })

        # If feedback provided, analyze it
        if feedback:
            gaps.append({
                "area": "feedback",
                "issue": f"Evaluator feedback: {feedback}",
                "severity": "medium",
                "improvable": True
            })

        # Default gap if nothing else identified
        if not gaps:
            gaps.append({
                "area": "competition",
                "issue": "Highly competitive pool - application may have been strong but exceeded by others",
                "severity": "low",
                "improvable": True
            })

        return gaps

    def _generate_improvement_actions(self, gaps: List[Dict], profile: Dict) -> List[Dict]:
        """Generate specific improvement actions based on gaps"""
        actions = []

        action_map = {
            "academics": {
                "action": "Focus on grade improvement in challenging courses",
                "timeframe": "1 semester",
                "resources": ["Tutoring", "Office hours", "Study groups"]
            },
            "leadership": {
                "action": "Seek officer/founder role in existing activity",
                "timeframe": "3-6 months",
                "resources": ["Mentorship", "Leadership training"]
            },
            "alignment": {
                "action": "Develop stronger narrative connecting your spike to desired areas",
                "timeframe": "Immediate (narrative work)",
                "resources": ["Essay coaching", "Personal statement revision"]
            },
            "competition": {
                "action": "Build unique differentiators that stand out in competitive pools",
                "timeframe": "6-12 months",
                "resources": ["Project development", "Research opportunities"]
            },
            "feedback": {
                "action": "Address specific feedback points through targeted improvement",
                "timeframe": "Variable",
                "resources": ["Coaching", "Skill development"]
            }
        }

        for gap in gaps:
            area = gap.get("area")
            if area in action_map:
                actions.append({
                    "area": area,
                    "gap": gap.get("issue"),
                    **action_map[area],
                    "priority": "high" if gap.get("severity") == "high" else "medium"
                })

        return actions

    async def _find_alternative_awards(self, profile: Dict, rejected_award: Dict, all_awards: List[Dict]) -> List[Dict]:
        """Find alternative awards similar to rejected one but with better fit"""
        alternatives = []
        rejected_category = rejected_award.get("category", "").upper()

        for award in all_awards:
            if award.get("id") == rejected_award.get("id"):
                continue

            # Calculate probability
            prob = await self.calculate_win_probability(profile, award)

            # Score by similarity and probability
            category_match = 1.2 if award.get("category", "").upper() == rejected_category else 1.0
            level_similar = 1.1 if award.get("level") == rejected_award.get("level") else 1.0

            adjusted_score = prob * category_match * level_similar

            alternatives.append({
                "award_id": award.get("id"),
                "name": award.get("name"),
                "category": award.get("category"),
                "level": award.get("level"),
                "win_probability": round(prob, 3),
                "similarity_score": round(adjusted_score, 3),
                "rationale": f"Similar to {rejected_award.get('name')} but with {round(prob*100)}% win probability"
            })

        # Sort by similarity score
        alternatives.sort(key=lambda x: x["similarity_score"], reverse=True)
        return alternatives

    def _create_rejection_narrative(self, award: Dict, gaps: List[Dict]) -> str:
        """Create a narrative reframe for the rejection"""
        award_name = award.get("name", "this award")
        primary_gap = gaps[0].get("area") if gaps else "competition"

        reframes = {
            "academics": f"Not winning {award_name} highlighted an opportunity to strengthen your academic foundation. Many successful applicants use this experience to fuel remarkable grade improvements.",
            "leadership": f"This feedback suggests focusing on demonstrable leadership impact. Consider how you can create visible change in your activities.",
            "alignment": f"This experience clarifies that your unique strengths may shine brighter in awards aligned with your core interests. Your spike is your superpower.",
            "competition": f"In highly competitive pools like {award_name}, exceptional applications can still not win. This is NOT a reflection of your worth—it's a numbers game. Keep applying.",
            "feedback": f"Specific feedback is a gift. Use it to make your next application even stronger."
        }

        return reframes.get(primary_gap, f"Every rejection is a redirect. Use this experience to strengthen your next application.")

    def _get_encouragement_message(self, gaps: List[Dict]) -> str:
        """Get encouraging message based on gap analysis"""
        improvable = sum(1 for g in gaps if g.get("improvable"))

        if improvable == len(gaps):
            return "✨ Good news: All identified gaps are improvable. With focused effort, your next application will be stronger."
        elif improvable > 0:
            return f"📈 {improvable} of {len(gaps)} identified areas can be improved. Focus your energy there."
        else:
            return "🎯 This may not have been the right fit. Let's find awards better aligned with your unique strengths."

    async def _store_rejection_data(self, profile_id: str, award_id: str, gaps: List[Dict]):
        """Store rejection data for future probability adjustments"""
        try:
            self.db.table("award_rejections").insert({
                "profile_id": profile_id,
                "award_id": award_id,
                "gaps": gaps,
                "created_at": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Rejection storage warning: {e}")

    def _filter_by_eligibility(self, awards: List[Dict], profile: Dict) -> List[Dict]:
        """Filter awards by eligibility criteria"""
        eligible = []
        profile_data = profile.get("profile_data", {})
        grade = profile_data.get("identity", {}).get("grade", profile.get("grade", 11))

        for award in awards:
            eligibility = award.get("eligibility", {})

            # Check grade eligibility
            eligible_grades = eligibility.get("grades", [9, 10, 11, 12])
            if grade not in eligible_grades:
                continue

            # Check other eligibility criteria
            if eligibility.get("min_gpa"):
                gpa = profile_data.get("aptitude", {}).get("gpa_weighted", 0)
                if gpa < eligibility["min_gpa"]:
                    continue

            eligible.append(award)

        return eligible

    def _generate_timeline(self, awards: List[Dict]) -> List[Dict]:
        """Generate award application timeline"""
        timeline = []
        now = datetime.now()

        for award in awards:
            deadline = award.get("deadline")
            if not deadline:
                continue

            if isinstance(deadline, str):
                try:
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                except:
                    continue

            days_until = (deadline - now).days
            if days_until < 0:
                continue

            timeline.append({
                "award_id": award.get("award_id"),
                "name": award.get("name"),
                "deadline": deadline.isoformat(),
                "days_until": days_until,
                "effort_hours": award.get("effort_hours", 20),
                "priority": "high" if days_until < 30 else "medium" if days_until < 90 else "low"
            })

        timeline.sort(key=lambda x: x["days_until"])
        return timeline[:10]  # Top 10 upcoming

    async def _get_awards(self) -> List[Dict]:
        """Get awards from database"""
        try:
            result = self.db.table("awards").select("*").eq("is_active", True).execute()
            if result.data:
                return result.data
        except:
            pass

        # Return sample awards if database empty
        return self._get_sample_awards()

    def _get_sample_awards(self) -> List[Dict]:
        """Sample awards for testing"""
        return [
            {
                "id": "ncwit",
                "name": "NCWIT Award for Aspirations in Computing",
                "category": "STEM",
                "level": "national",
                "organization": "NCWIT",
                "historical_win_rate": 0.10,
                "prestige_score": 8,
                "effort_hours": 15,
                "considers_diversity": True,
                "eligibility": {"grades": [9, 10, 11, 12]}
            },
            {
                "id": "usabo",
                "name": "USA Biology Olympiad",
                "category": "STEM",
                "level": "national",
                "organization": "CEE",
                "historical_win_rate": 0.05,
                "prestige_score": 9,
                "effort_hours": 100,
                "considers_diversity": False,
                "eligibility": {"grades": [9, 10, 11, 12]}
            },
            {
                "id": "scholastic",
                "name": "Scholastic Art & Writing Awards",
                "category": "ARTS",
                "level": "national",
                "organization": "Alliance for Young Artists",
                "historical_win_rate": 0.08,
                "prestige_score": 8,
                "effort_hours": 30,
                "considers_diversity": False,
                "eligibility": {"grades": [7, 8, 9, 10, 11, 12]}
            },
            {
                "id": "pvsa",
                "name": "Presidential Volunteer Service Award",
                "category": "SERVICE",
                "level": "national",
                "organization": "Corporation for National and Community Service",
                "historical_win_rate": 0.30,
                "prestige_score": 6,
                "effort_hours": 100,
                "considers_diversity": False,
                "eligibility": {"grades": [9, 10, 11, 12]}
            },
            {
                "id": "deca",
                "name": "DECA International Career Development Conference",
                "category": "BUSINESS",
                "level": "national",
                "organization": "DECA",
                "historical_win_rate": 0.15,
                "prestige_score": 7,
                "effort_hours": 50,
                "considers_diversity": False,
                "eligibility": {"grades": [9, 10, 11, 12]}
            }
        ]

    async def _get_profile(self, profile_id: str) -> Optional[Dict]:
        """Get profile with assessment data using centralized function."""
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


# Export
awards_agent = AwardsAgent()

# Also export the class for backward compatibility with existing main.py
AwardsAgent = AwardsAgent
