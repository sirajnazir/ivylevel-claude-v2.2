# Programs Agent - Complete Implementation with Strategic Intelligence
# File: agents/agents/programs.py
#
# Renamed from opportunity.py and enhanced with strategic intelligence (v1.0.0)
# Uses enriched programs data with archetype_fit, strategic_tier, synergies
#
# Accepts identity_synthesis from EC Agent for filtering

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os

from langchain_openai import ChatOpenAI

from tools.database import get_supabase_client, get_profile_with_assessment

# v4.0: Hybrid Architecture imports
from agents.core.guardrails import validate_programs_output
from config import FEATURE_FLAGS


# Path to enriched programs data
ENRICHED_PROGRAMS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "seeds", "enriched", "programs_enriched.json"
)

# Minimum archetype fit score to include program
MIN_ARCHETYPE_FIT = 0.3


class ProgramsAgent:
    """
    Programs Agent: Matches students to summer programs with Strategic Intelligence

    Enhanced Features (v1.0.0):
    - Strategic tier-based filtering (Tier 1-4)
    - Archetype fit scoring (8 archetypes)
    - Hidden value identification
    - Synergy recommendations (pairs_well_with, leads_to)
    - Application intensity planning

    Primitives Used:
    - ACP-001: Hidden Probability Matrix
    - ACP-005: Multi-Touchpoint Leverage
    - TYPE-014: Archetype-based filtering

    Accepts: identity_synthesis from EC Agent
    Autonomy: FULL (deterministic matching)
    """

    def __init__(self):
        self.name = "Programs"
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.db = get_supabase_client()
        self.advance_alert_months = 6
        self._enriched_programs_cache = None

    def _load_enriched_programs(self) -> List[Dict]:
        """Load enriched programs from JSON file with caching"""
        if self._enriched_programs_cache is not None:
            return self._enriched_programs_cache

        try:
            if os.path.exists(ENRICHED_PROGRAMS_PATH):
                with open(ENRICHED_PROGRAMS_PATH, 'r') as f:
                    self._enriched_programs_cache = json.load(f)
                    return self._enriched_programs_cache
        except Exception as e:
            print(f"[ProgramsAgent] Warning: Could not load enriched programs: {e}")

        self._enriched_programs_cache = []
        return self._enriched_programs_cache

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Main processing entry point.

        Args:
            profile_id: Student profile ID
            identity_synthesis: (optional) Output from EC Agent
            route_config: (optional) Strategic routing config from GamePlan
        """
        identity_synthesis = kwargs.get("identity_synthesis")
        route_config = kwargs.get("route_config", {})
        return await self.match(profile_id, identity_synthesis=identity_synthesis, route_config=route_config)

    async def match(
        self,
        profile_id: str,
        identity_synthesis: Optional[Dict] = None,
        route_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Match profile to programs with Strategic Intelligence filtering.

        Uses identity_synthesis from EC Agent to filter by:
        - Archetype fit scores
        - Strategic tier positioning
        - Hidden value alignment

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
                    "top_recommendations": [],
                    "advance_alerts": [],
                    "synergy_recommendations": [],
                    "timeline": [],
                    "strategic_insights": [],
                    "placeholder": True
                }

            # Get enriched programs (with strategic intelligence)
            programs = self._load_enriched_programs()
            if not programs:
                # Fallback to database/sample
                programs = await self._get_programs()

            # Extract archetype from identity_synthesis
            archetype = None
            if identity_synthesis:
                archetype = identity_synthesis.get("archetype", "multi_hyphenate")
            else:
                profile_data = profile.get("profile_data", {})
                archetype = profile_data.get("archetype", "multi_hyphenate")

            # Filter by eligibility
            eligible = self._filter_by_eligibility(programs, profile)

            # Filter by archetype fit
            if archetype:
                eligible = self._filter_by_archetype(eligible, archetype)

            # Calculate fit score for each
            matched = []
            for prog in eligible:
                fit_score = await self.calculate_fit_score(profile, prog)
                accept_prob = self._estimate_acceptance(fit_score, prog)
                strategic_tier = prog.get("strategic_tier", 3)

                # Get archetype fit score
                archetype_fit = 0.5
                if archetype and prog.get("archetype_fit"):
                    archetype_fit = prog["archetype_fit"].get(archetype, 0.5)

                matched.append({
                    "program_id": prog.get("id"),
                    "name": prog.get("name"),
                    "type": prog.get("type"),
                    "organization": prog.get("organization"),
                    "fit_score": round(fit_score, 3),
                    "acceptance_probability": round(accept_prob, 3),
                    "prestige_score": prog.get("prestige_score", 5),
                    "deadline": prog.get("deadline"),
                    "duration": prog.get("duration"),
                    "cost": prog.get("cost"),
                    "recommendation": self._get_recommendation(fit_score),
                    # Strategic intelligence fields
                    "strategic_tier": strategic_tier,
                    "archetype_fit": round(archetype_fit, 2),
                    "strategic_notes": prog.get("strategic_notes", ""),
                    "success_patterns": prog.get("success_patterns", []),
                    "common_mistakes": prog.get("common_mistakes", []),
                    "hidden_value": prog.get("hidden_value", []),
                    "synergies": prog.get("synergies", {}),
                    "timing": prog.get("timing", {}),
                    "differentiation_factor": prog.get("differentiation_factor", ""),
                })

            # Sort by fit × archetype_fit
            matched.sort(
                key=lambda x: x["fit_score"] * x.get("archetype_fit", 0.5),
                reverse=True
            )

            # Generate advance alerts
            alerts = await self.send_advance_alerts(profile_id, matched)

            # Generate synergy recommendations
            synergy_recs = self._generate_synergy_recommendations(matched[:5])

            # Version state
            await self._version_state(profile_id, "programs_matched", {
                "matches_count": len(matched),
                "archetype_used": archetype,
                "alerts_count": len(alerts),
            })

            # Publish events
            for alert in alerts[:3]:
                await self._publish_event("PROGRAM_ALERT", {
                    "profileId": profile_id,
                    "programId": alert.get("program_id"),
                    "deadline": alert.get("deadline")
                })

            # Generate strategic insights
            strategic_insights = self._generate_strategic_insights(
                matched, archetype, identity_synthesis
            )

            # v4.0: Apply route_config adjustments
            max_recs = route_config.get("max_recommendations", 10)
            be_prescriptive = route_config.get("be_prescriptive", False)

            result = {
                "success": True,
                "total_matches": len(matched),
                "top_recommendations": matched[:max_recs],
                "advance_alerts": alerts[:max_recs] if alerts else [],
                "synergy_recommendations": synergy_recs,
                "timeline": self._generate_timeline(matched[:max_recs]),
                "strategic_insights": strategic_insights,
                "archetype_used": archetype,
                "route_config_applied": route_config if route_config else None,
            }

            # v4.0: Add prescriptive action steps if enabled
            if be_prescriptive and matched:
                result["prescriptive_actions"] = self._generate_prescriptive_actions(matched[:3])

            # v4.0: Validate output against knowledge base
            if FEATURE_FLAGS.get("enable_guardrails", True):
                validation = validate_programs_output(result, self._load_enriched_programs())
                if validation.warnings:
                    result["validation_warnings"] = validation.warnings
                result["confidence"] = validation.confidence

            return result

        except Exception as e:
            import traceback
            print(f"[ProgramsAgent] ERROR: {str(e)}")
            print(traceback.format_exc())
            return {"success": False, "error": str(e)}

    def _filter_by_archetype(self, programs: List[Dict], archetype: str) -> List[Dict]:
        """Filter programs by archetype fit score"""
        filtered = []
        for prog in programs:
            archetype_fit = prog.get("archetype_fit", {})
            fit_score = archetype_fit.get(archetype, 0.5)

            if fit_score >= MIN_ARCHETYPE_FIT:
                filtered.append(prog)

        return filtered

    def _generate_synergy_recommendations(self, top_programs: List[Dict]) -> List[Dict]:
        """
        Generate synergy recommendations based on program pairings.

        Uses synergies.pairs_well_with and synergies.leads_to fields.
        """
        recommendations = []

        for prog in top_programs:
            synergies = prog.get("synergies", {})
            pairs = synergies.get("pairs_well_with", [])
            leads_to = synergies.get("leads_to", [])

            if pairs:
                recommendations.append({
                    "type": "pairing",
                    "primary_program": prog.get("name"),
                    "complementary": pairs[:2],
                    "rationale": f"{prog.get('name')} pairs well with these programs for narrative coherence"
                })

            if leads_to:
                recommendations.append({
                    "type": "pathway",
                    "starting_program": prog.get("name"),
                    "opens_doors_to": leads_to[:2],
                    "rationale": f"Completing {prog.get('name')} positions you for these opportunities"
                })

        return recommendations[:5]

    def _generate_strategic_insights(
        self,
        programs: List[Dict],
        archetype: str,
        identity_synthesis: Optional[Dict]
    ) -> List[Dict]:
        """Generate strategic insights based on matches"""
        insights = []

        if not programs:
            return insights

        # Insight 1: Archetype alignment
        avg_fit = sum(p.get("archetype_fit", 0.5) for p in programs[:5]) / min(5, len(programs))
        if avg_fit >= 0.7:
            insights.append({
                "type": "archetype_alignment",
                "title": "Strong Program Alignment",
                "message": f"Your {archetype.replace('_', ' ')} profile matches well with top programs (avg fit: {avg_fit:.0%})",
                "priority": "high"
            })

        # Insight 2: Hidden value highlight
        for prog in programs[:3]:
            hidden_values = prog.get("hidden_value", [])
            if hidden_values:
                insights.append({
                    "type": "hidden_value",
                    "title": f"Hidden Value: {prog.get('name')}",
                    "message": hidden_values[0],
                    "priority": "medium"
                })
                break

        # Insight 3: Application intensity planning
        intensities = {"light": 0, "moderate": 0, "heavy": 0}
        for prog in programs[:5]:
            timing = prog.get("timing", {})
            intensity = timing.get("application_intensity", "moderate")
            intensities[intensity] = intensities.get(intensity, 0) + 1

        if intensities.get("heavy", 0) >= 2:
            insights.append({
                "type": "workload_warning",
                "title": "High Application Workload",
                "message": f"You have {intensities.get('heavy', 0)} programs with heavy application requirements. Plan accordingly.",
                "priority": "high"
            })

        return insights

    def _generate_prescriptive_actions(self, top_programs: List[Dict]) -> List[Dict]:
        """
        Generate specific, actionable steps for program applications.
        Used when be_prescriptive=True in route_config (BUILD_FRESH, URGENT_TRIAGE).
        """
        actions = []

        for i, prog in enumerate(top_programs, 1):
            action = {
                "priority": i,
                "program": prog.get("name"),
                "deadline": prog.get("deadline"),
                "action_steps": [],
            }

            # Add specific action steps
            if prog.get("deadline"):
                action["action_steps"].append(
                    f"Application deadline: {prog['deadline']}"
                )

            timing = prog.get("timing", {})
            if timing.get("ideal_apply_window"):
                action["action_steps"].append(
                    f"Best time to apply: {timing['ideal_apply_window']}"
                )

            if timing.get("application_intensity"):
                intensity = timing["application_intensity"]
                if intensity == "heavy":
                    action["action_steps"].append(
                        "Heavy application - start prep 4+ weeks early"
                    )
                elif intensity == "moderate":
                    action["action_steps"].append(
                        "Moderate application - plan 2-3 weeks prep time"
                    )

            if prog.get("success_patterns"):
                action["action_steps"].append(
                    f"Key to success: {prog['success_patterns'][0]}"
                )

            if prog.get("hidden_value"):
                action["action_steps"].append(
                    f"Hidden benefit: {prog['hidden_value'][0]}"
                )

            # Add synergy info
            synergies = prog.get("synergies", {})
            if synergies.get("pairs_well_with"):
                action["action_steps"].append(
                    f"Pairs well with: {synergies['pairs_well_with'][0]}"
                )

            actions.append(action)

        return actions

    async def calculate_fit_score(self, profile: Dict, program: Dict) -> float:
        """Calculate fit score based on multiple factors"""
        profile_data = profile.get("profile_data", {})

        academic_fit = self._calculate_academic_fit(profile_data, program)
        interest_fit = self._calculate_interest_fit(profile_data, program)
        experience_fit = self._calculate_experience_fit(profile_data, program)
        demographic_fit = self._calculate_demographic_fit(profile_data, program)

        base_score = (
            academic_fit * 0.30 +
            interest_fit * 0.35 +
            experience_fit * 0.25 +
            0.10
        )

        final_score = base_score * demographic_fit
        return min(1.0, max(0.0, final_score))

    def _calculate_academic_fit(self, profile_data: Dict, program: Dict) -> float:
        """Calculate academic alignment"""
        aptitude = profile_data.get("aptitude", {})
        student_gpa = aptitude.get("gpa_weighted", 3.5)
        min_gpa = program.get("min_gpa", 3.0)

        if student_gpa >= min_gpa + 0.5:
            gpa_fit = 1.0
        elif student_gpa >= min_gpa:
            gpa_fit = 0.8
        elif student_gpa >= min_gpa - 0.3:
            gpa_fit = 0.5
        else:
            gpa_fit = 0.2

        if program.get("requires_sat", False):
            student_sat = aptitude.get("sat_total", 1200)
            min_sat = program.get("min_sat", 1400)

            if student_sat >= min_sat + 100:
                sat_fit = 1.0
            elif student_sat >= min_sat:
                sat_fit = 0.8
            elif student_sat >= min_sat - 100:
                sat_fit = 0.5
            else:
                sat_fit = 0.2
        else:
            sat_fit = 0.8

        return (gpa_fit * 0.6 + sat_fit * 0.4)

    def _calculate_interest_fit(self, profile_data: Dict, program: Dict) -> float:
        """Calculate interest/spike alignment"""
        passion = profile_data.get("passion", {})
        spike = passion.get("spike_category", "GENERAL").upper()
        focus = program.get("focus_area", "").upper()

        if spike == focus:
            return 1.0

        related_mapping = {
            "STEM": ["SCIENCE", "TECHNOLOGY", "ENGINEERING", "MATH", "COMPUTER SCIENCE", "CS", "RESEARCH"],
            "ARTS": ["CREATIVE", "HUMANITIES", "WRITING", "VISUAL", "PERFORMING"],
            "SERVICE": ["COMMUNITY", "SOCIAL", "VOLUNTEER", "CIVIC", "PUBLIC POLICY"],
            "BUSINESS": ["ENTREPRENEURSHIP", "ECONOMICS", "FINANCE", "LEADERSHIP"]
        }

        for main_cat, related in related_mapping.items():
            if spike == main_cat and focus in related:
                return 0.85
            if spike in related and focus == main_cat:
                return 0.85

        if focus in ["GENERAL", "MULTIDISCIPLINARY", ""]:
            return 0.7

        return 0.4

    def _calculate_experience_fit(self, profile_data: Dict, program: Dict) -> float:
        """Calculate experience/achievement fit"""
        passion = profile_data.get("passion", {})
        prog_type = program.get("type", "").lower()

        if prog_type == "research":
            research_level = passion.get("research_level", "NONE")
            research_scores = {
                "PUBLISHED": 1.0,
                "PRESENTED_NATIONAL": 0.9,
                "PRESENTED_STATE": 0.8,
                "COMPLETED": 0.6,
                "IN_PROGRESS": 0.5,
                "NONE": 0.3
            }
            return research_scores.get(research_level, 0.3)

        if prog_type in ["leadership", "entrepreneurship"]:
            leadership = passion.get("leadership_level", "MEMBER")
            leadership_scores = {
                "FOUNDER_NATIONAL": 1.0,
                "FOUNDER_STATE": 0.9,
                "NATIONAL_PRES": 0.85,
                "STATE_PRES": 0.75,
                "SCHOOL_PRES": 0.65,
                "OFFICER": 0.55,
                "MEMBER": 0.4
            }
            return leadership_scores.get(leadership, 0.4)

        return 0.6

    def _calculate_demographic_fit(self, profile_data: Dict, program: Dict) -> float:
        """Calculate demographic fit multiplier"""
        if not program.get("diversity_focus", False):
            return 1.0

        demographics = profile_data.get("demographics", {})
        operating = profile_data.get("operating", {})
        multiplier = 1.0

        if demographics.get("first_gen") or operating.get("firstGeneration"):
            multiplier += 0.05

        ethnicity = demographics.get("ethnicity", "")
        if ethnicity in ["BLACK", "HISPANIC", "NATIVE_AMERICAN", "PACIFIC_ISLANDER"]:
            multiplier += 0.1
        elif demographics.get("underrepresented"):
            multiplier += 0.05

        if demographics.get("income_band") in ["LOW", "LOWER_MIDDLE"]:
            multiplier += 0.05

        return min(1.2, multiplier)

    def _estimate_acceptance(self, fit_score: float, program: Dict) -> float:
        """Estimate acceptance probability"""
        base_rate = program.get("acceptance_rate", 0.15)
        selectivity = program.get("selectivity", "moderate")

        selectivity_factors = {
            "highly_selective": 0.7,
            "selective": 0.85,
            "moderate": 1.0,
            "open": 1.2
        }

        selectivity_factor = selectivity_factors.get(selectivity, 1.0)
        probability = base_rate * fit_score * selectivity_factor
        return min(0.80, max(0.05, probability))

    def _get_recommendation(self, fit_score: float) -> str:
        """Get recommendation tier"""
        if fit_score >= 0.80:
            return "strong_match"
        elif fit_score >= 0.60:
            return "good_match"
        elif fit_score >= 0.40:
            return "moderate_match"
        return "reach"

    async def send_advance_alerts(self, profile_id: str, programs: List[Dict]) -> List[Dict]:
        """Send advance alerts for programs with upcoming deadlines"""
        alerts = []
        now = datetime.now()
        alert_start = now + timedelta(days=150)
        alert_end = now + timedelta(days=210)

        for prog in programs[:15]:
            deadline = prog.get("deadline")
            if not deadline:
                continue

            if isinstance(deadline, str):
                try:
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                except:
                    continue

            if alert_start <= deadline <= alert_end:
                days_until = (deadline - now).days
                months_until = days_until // 30

                timing = prog.get("timing", {})
                intensity = timing.get("application_intensity", "moderate")

                alerts.append({
                    "program_id": prog.get("program_id"),
                    "name": prog.get("name"),
                    "type": prog.get("type"),
                    "deadline": deadline.isoformat(),
                    "days_until": days_until,
                    "months_until": months_until,
                    "fit_score": prog.get("fit_score"),
                    "application_intensity": intensity,
                    "alert_type": "advance_preparation",
                    "urgency": "medium" if months_until >= 6 else "high",
                    "message": f"Start preparing for {prog.get('name')} - deadline in {months_until} months"
                })

        alerts.sort(key=lambda x: x["days_until"])
        return alerts

    def _filter_by_eligibility(self, programs: List[Dict], profile: Dict) -> List[Dict]:
        """Filter programs by eligibility"""
        eligible = []
        profile_data = profile.get("profile_data", {})
        grade = profile_data.get("identity", {}).get("grade", profile.get("grade", 11))

        for prog in programs:
            eligibility = prog.get("eligibility", {})
            eligible_grades = eligibility.get("grades", [9, 10, 11, 12])
            if grade not in eligible_grades:
                continue

            if eligibility.get("min_gpa"):
                gpa = profile_data.get("aptitude", {}).get("gpa_weighted", 0)
                if gpa < eligibility["min_gpa"]:
                    continue

            eligible.append(prog)

        return eligible

    def _generate_timeline(self, programs: List[Dict]) -> List[Dict]:
        """Generate program application timeline"""
        timeline = []
        now = datetime.now()

        for prog in programs:
            deadline = prog.get("deadline")
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

            timing = prog.get("timing", {})

            timeline.append({
                "program_id": prog.get("program_id"),
                "name": prog.get("name"),
                "type": prog.get("type"),
                "deadline": deadline.isoformat(),
                "days_until": days_until,
                "fit_score": prog.get("fit_score"),
                "application_intensity": timing.get("application_intensity", "moderate"),
                "priority": "high" if days_until < 30 else "medium" if days_until < 90 else "low"
            })

        timeline.sort(key=lambda x: x["days_until"])
        return timeline[:15]

    async def _get_programs(self) -> List[Dict]:
        """Get programs from database"""
        try:
            result = self.db.table("programs").select("*").eq("is_active", True).execute()
            if result.data:
                return result.data
        except:
            pass

        # Try opportunities table (legacy)
        try:
            result = self.db.table("opportunities").select("*").eq("is_active", True).execute()
            if result.data:
                return result.data
        except:
            pass

        return self._get_sample_programs()

    def _get_sample_programs(self) -> List[Dict]:
        """Sample programs for testing"""
        now = datetime.now()
        return [
            {
                "id": "rsi",
                "name": "Research Science Institute",
                "type": "research",
                "organization": "MIT/CEE",
                "focus_area": "STEM",
                "prestige_score": 10,
                "acceptance_rate": 0.03,
                "selectivity": "highly_selective",
                "deadline": (now + timedelta(days=60)).isoformat(),
                "duration": "6 weeks",
                "cost": "Free",
                "diversity_focus": True,
                "eligibility": {"grades": [11]}
            },
            {
                "id": "ssp",
                "name": "Summer Science Program",
                "type": "research",
                "organization": "SSP",
                "focus_area": "STEM",
                "prestige_score": 9,
                "acceptance_rate": 0.08,
                "selectivity": "highly_selective",
                "deadline": (now + timedelta(days=90)).isoformat(),
                "duration": "6 weeks",
                "cost": "Financial aid available",
                "eligibility": {"grades": [10, 11]}
            },
        ]

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
programs_agent = ProgramsAgent()

# Export class
ProgramsAgent = ProgramsAgent

# Backward compatibility alias
OpportunityAgent = ProgramsAgent
opportunity_agent = programs_agent
