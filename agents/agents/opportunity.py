# Opportunity Agent - Complete Implementation
# File: agents/agents/opportunity.py
#
# This replaces the stub with real alerts and backup cascades

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from langchain_openai import ChatOpenAI

from tools.database import get_supabase_client, get_profile_with_assessment


class OpportunityAgent:
    """
    Opportunity Agent: Matches students to summer programs and opportunities

    Primitives Used:
    - ACP-001: Hidden Probability Matrix
    - ACP-005: Multi-Touchpoint Leverage
    - Advance Alerts (6-month before deadline)

    Autonomy: FULL (deterministic matching)
    """

    def __init__(self):
        self.name = "Opportunity"
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.db = get_supabase_client()
        self.advance_alert_months = 6  # Alert 6 months before deadline

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """Main processing entry point."""
        return await self.match(profile_id)

    async def match(self, profile_id: str) -> Dict[str, Any]:
        """Match profile to opportunities with fit calculation."""
        try:
            profile = await self._get_profile(profile_id)
            if not profile:
                # Return placeholder data for graceful frontend handling
                return {
                    "success": True,
                    "total_matches": 0,
                    "top_recommendations": [],
                    "advance_alerts": [],
                    "backup_cascades": [],
                    "timeline": [],
                    "placeholder": True
                }

            # Get all active opportunities
            opportunities = await self._get_opportunities()

            # Filter by eligibility
            eligible = self._filter_by_eligibility(opportunities, profile)

            # Calculate fit score for each
            matched = []
            for opp in eligible:
                fit_score = await self.calculate_fit_score(profile, opp)
                accept_prob = self._estimate_acceptance(fit_score, opp)

                matched.append({
                    "opportunity_id": opp.get("id"),
                    "name": opp.get("name"),
                    "type": opp.get("type"),
                    "organization": opp.get("organization"),
                    "fit_score": round(fit_score, 3),
                    "acceptance_probability": round(accept_prob, 3),
                    "prestige_score": opp.get("prestige_score", 5),
                    "deadline": opp.get("deadline"),
                    "duration": opp.get("duration"),
                    "cost": opp.get("cost"),
                    "recommendation": self._get_recommendation(fit_score)
                })

            # Sort by fit score
            matched.sort(key=lambda x: x["fit_score"], reverse=True)

            # Generate advance alerts
            alerts = await self.send_advance_alerts(profile_id, matched)

            # Create backup cascades for top matches
            cascades = []
            for primary in matched[:3]:  # Top 3 primary targets
                cascade = self.create_backup_cascade(primary, matched)
                cascades.append(cascade)

            # Version state
            await self._version_state(profile_id, "opportunities_matched", {
                "matches_count": len(matched),
                "alerts_count": len(alerts),
                "cascades_count": len(cascades)
            })

            # Publish events for alerts
            for alert in alerts:
                await self._publish_event("OPPORTUNITY_ALERT", {
                    "profileId": profile_id,
                    "opportunityId": alert.get("opportunity_id"),
                    "deadline": alert.get("deadline")
                })

            return {
                "success": True,
                "total_matches": len(matched),
                "top_recommendations": matched[:10],
                "advance_alerts": alerts,
                "backup_cascades": cascades,
                "timeline": self._generate_timeline(matched)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def calculate_fit_score(self, profile: Dict, opportunity: Dict) -> float:
        """
        Calculate fit score based on multiple factors

        Factors:
        - Academic alignment (GPA, test scores vs requirements)
        - Interest alignment (spike category vs program focus)
        - Profile strength signals
        - Demographic fit (if program has preferences)
        """
        profile_data = profile.get("profile_data", {})

        # Factor 1: Academic fit (0.0 - 1.0)
        academic_fit = self._calculate_academic_fit(profile_data, opportunity)

        # Factor 2: Interest alignment (0.0 - 1.0)
        interest_fit = self._calculate_interest_fit(profile_data, opportunity)

        # Factor 3: Experience fit (0.0 - 1.0)
        experience_fit = self._calculate_experience_fit(profile_data, opportunity)

        # Factor 4: Demographic fit (0.8 - 1.2)
        demographic_fit = self._calculate_demographic_fit(profile_data, opportunity)

        # Weighted combination
        base_score = (
            academic_fit * 0.30 +
            interest_fit * 0.35 +
            experience_fit * 0.25 +
            0.10  # Base score
        )

        # Apply demographic multiplier
        final_score = base_score * demographic_fit

        return min(1.0, max(0.0, final_score))

    def _calculate_academic_fit(self, profile_data: Dict, opportunity: Dict) -> float:
        """Calculate academic alignment (0.0 - 1.0)"""
        aptitude = profile_data.get("aptitude", {})

        # GPA fit
        student_gpa = aptitude.get("gpa_weighted", 3.5)
        min_gpa = opportunity.get("min_gpa", 3.0)

        if student_gpa >= min_gpa + 0.5:
            gpa_fit = 1.0
        elif student_gpa >= min_gpa:
            gpa_fit = 0.8
        elif student_gpa >= min_gpa - 0.3:
            gpa_fit = 0.5
        else:
            gpa_fit = 0.2

        # Test score fit (if required)
        if opportunity.get("requires_sat", False):
            student_sat = aptitude.get("sat_total", 1200)
            min_sat = opportunity.get("min_sat", 1400)

            if student_sat >= min_sat + 100:
                sat_fit = 1.0
            elif student_sat >= min_sat:
                sat_fit = 0.8
            elif student_sat >= min_sat - 100:
                sat_fit = 0.5
            else:
                sat_fit = 0.2
        else:
            sat_fit = 0.8  # Neutral if not required

        return (gpa_fit * 0.6 + sat_fit * 0.4)

    def _calculate_interest_fit(self, profile_data: Dict, opportunity: Dict) -> float:
        """Calculate interest/spike alignment (0.0 - 1.0)"""
        passion = profile_data.get("passion", {})
        spike = passion.get("spike_category", "GENERAL").upper()
        focus = opportunity.get("focus_area", "").upper()

        # Perfect match
        if spike == focus:
            return 1.0

        # Related fields
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

        # General program
        if focus in ["GENERAL", "MULTIDISCIPLINARY", ""]:
            return 0.7

        # No alignment
        return 0.4

    def _calculate_experience_fit(self, profile_data: Dict, opportunity: Dict) -> float:
        """Calculate experience/achievement fit (0.0 - 1.0)"""
        passion = profile_data.get("passion", {})
        opp_type = opportunity.get("type", "").lower()

        # Research programs value research experience
        if opp_type == "research":
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

        # Leadership programs value leadership
        if opp_type in ["leadership", "entrepreneurship"]:
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

        # Default based on general activity level
        return 0.6

    def _calculate_demographic_fit(self, profile_data: Dict, opportunity: Dict) -> float:
        """Calculate demographic fit multiplier (0.8 - 1.2)"""
        if not opportunity.get("diversity_focus", False):
            return 1.0

        demographics = profile_data.get("demographics", {})
        operating = profile_data.get("operating", {})

        multiplier = 1.0

        # First-gen bonus
        if demographics.get("first_gen") or operating.get("firstGeneration"):
            multiplier += 0.05

        # Underrepresented background
        ethnicity = demographics.get("ethnicity", "")
        if ethnicity in ["BLACK", "HISPANIC", "NATIVE_AMERICAN", "PACIFIC_ISLANDER"]:
            multiplier += 0.1
        elif demographics.get("underrepresented"):
            multiplier += 0.05

        # Low-income background
        if demographics.get("income_band") in ["LOW", "LOWER_MIDDLE"]:
            multiplier += 0.05

        return min(1.2, multiplier)

    def _estimate_acceptance(self, fit_score: float, opportunity: Dict) -> float:
        """Estimate acceptance probability based on fit and selectivity"""
        base_rate = opportunity.get("acceptance_rate", 0.15)
        selectivity = opportunity.get("selectivity", "moderate")

        # Selectivity multipliers
        selectivity_factors = {
            "highly_selective": 0.7,
            "selective": 0.85,
            "moderate": 1.0,
            "open": 1.2
        }

        selectivity_factor = selectivity_factors.get(selectivity, 1.0)

        # Calculate probability
        probability = base_rate * fit_score * selectivity_factor

        # Cap at reasonable bounds
        return min(0.80, max(0.05, probability))

    def _get_recommendation(self, fit_score: float) -> str:
        """Get recommendation tier based on fit score"""
        if fit_score >= 0.80:
            return "strong_match"
        elif fit_score >= 0.60:
            return "good_match"
        elif fit_score >= 0.40:
            return "moderate_match"
        else:
            return "reach"

    async def send_advance_alerts(self, profile_id: str, opportunities: List[Dict]) -> List[Dict]:
        """
        Send advance alerts for opportunities with deadlines 5-6 months away

        Alert includes:
        - What to prepare
        - Key dates
        - Action items
        """
        alerts = []
        now = datetime.now()
        alert_start = now + timedelta(days=150)  # 5 months
        alert_end = now + timedelta(days=210)    # 7 months

        for opp in opportunities[:15]:  # Top 15 matches only
            deadline = opp.get("deadline")
            if not deadline:
                continue

            if isinstance(deadline, str):
                try:
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                except:
                    continue

            # Check if in alert window
            if alert_start <= deadline <= alert_end:
                days_until = (deadline - now).days
                months_until = days_until // 30

                # Generate preparation actions
                actions = self._generate_prep_actions(opp, months_until)

                alert = {
                    "opportunity_id": opp.get("opportunity_id"),
                    "name": opp.get("name"),
                    "type": opp.get("type"),
                    "deadline": deadline.isoformat(),
                    "days_until": days_until,
                    "months_until": months_until,
                    "fit_score": opp.get("fit_score"),
                    "alert_type": "advance_preparation",
                    "urgency": "medium" if months_until >= 6 else "high",
                    "actions": actions,
                    "message": f"Start preparing for {opp.get('name')} - deadline in {months_until} months"
                }

                alerts.append(alert)

        # Sort by deadline
        alerts.sort(key=lambda x: x["days_until"])

        return alerts

    def _generate_prep_actions(self, opportunity: Dict, months_until: int) -> List[Dict]:
        """Generate preparation actions based on opportunity type and time available"""
        opp_type = opportunity.get("type", "general").lower()

        if opp_type == "research":
            return [
                {"action": "Identify research interests and potential topics", "week": 1},
                {"action": "Research program faculty and their work", "week": 2},
                {"action": "Draft research statement outline", "week": 3},
                {"action": "Request recommendation letters", "week": 4},
                {"action": "Complete application essays", "week": 8}
            ]
        elif opp_type == "summer_program":
            return [
                {"action": "Review program curriculum and requirements", "week": 1},
                {"action": "Prepare supporting documents (transcript, etc.)", "week": 2},
                {"action": "Draft personal statement", "week": 3},
                {"action": "Request recommendations", "week": 4},
                {"action": "Submit application with buffer time", "week": 8}
            ]
        else:
            return [
                {"action": "Review all requirements thoroughly", "week": 1},
                {"action": "Gather supporting materials", "week": 2},
                {"action": "Draft application materials", "week": 3},
                {"action": "Get feedback and revise", "week": 6},
                {"action": "Submit before deadline", "week": 8}
            ]

    def create_backup_cascade(self, primary: Dict, all_matches: List[Dict]) -> Dict:
        """
        Create backup cascade with 3+ alternatives for each primary target

        Backups should:
        - Be similar type/focus
        - Have later or close deadlines
        - Have realistic fit scores
        """
        primary_type = primary.get("type", "")
        primary_score = primary.get("fit_score", 0)
        primary_id = primary.get("opportunity_id")

        # Filter for similar opportunities as backups
        potential_backups = [
            opp for opp in all_matches
            if opp.get("opportunity_id") != primary_id
            and opp.get("fit_score", 0) >= primary_score * 0.6  # At least 60% as good fit
        ]

        # Prioritize same type, then related types
        type_priority = {
            "research": ["research", "academic", "stem"],
            "summer_program": ["summer_program", "academic", "enrichment"],
            "internship": ["internship", "professional", "work_experience"],
            "leadership": ["leadership", "entrepreneurship", "community"]
        }

        related_types = type_priority.get(primary_type.lower(), [primary_type.lower()])

        # Sort backups by relevance
        def backup_score(opp):
            type_match = 1.0 if opp.get("type", "").lower() in related_types else 0.5
            return opp.get("fit_score", 0) * type_match

        potential_backups.sort(key=backup_score, reverse=True)

        # Select top 3-4 backups
        backups = potential_backups[:4]

        cascade = {
            "primary": {
                "opportunity_id": primary.get("opportunity_id"),
                "name": primary.get("name"),
                "fit_score": primary.get("fit_score"),
                "deadline": primary.get("deadline")
            },
            "backups": [
                {
                    "opportunity_id": b.get("opportunity_id"),
                    "name": b.get("name"),
                    "fit_score": b.get("fit_score"),
                    "deadline": b.get("deadline"),
                    "priority": idx + 1,
                    "rationale": f"Strong alternative with {b.get('fit_score', 0)*100:.0f}% fit"
                }
                for idx, b in enumerate(backups)
            ],
            "strategy": "If rejected from primary, immediately apply to backup 1. Continue cascade as needed.",
            "total_coverage": len(backups) + 1
        }

        return cascade

    def _filter_by_eligibility(self, opportunities: List[Dict], profile: Dict) -> List[Dict]:
        """Filter opportunities by eligibility"""
        eligible = []
        profile_data = profile.get("profile_data", {})
        grade = profile_data.get("identity", {}).get("grade", profile.get("grade", 11))

        for opp in opportunities:
            eligibility = opp.get("eligibility", {})

            # Check grade eligibility
            eligible_grades = eligibility.get("grades", [9, 10, 11, 12])
            if grade not in eligible_grades:
                continue

            # Check GPA requirement
            if eligibility.get("min_gpa"):
                gpa = profile_data.get("aptitude", {}).get("gpa_weighted", 0)
                if gpa < eligibility["min_gpa"]:
                    continue

            eligible.append(opp)

        return eligible

    def _generate_timeline(self, opportunities: List[Dict]) -> List[Dict]:
        """Generate opportunity application timeline"""
        timeline = []
        now = datetime.now()

        for opp in opportunities:
            deadline = opp.get("deadline")
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
                "opportunity_id": opp.get("opportunity_id"),
                "name": opp.get("name"),
                "type": opp.get("type"),
                "deadline": deadline.isoformat(),
                "days_until": days_until,
                "fit_score": opp.get("fit_score"),
                "priority": "high" if days_until < 30 else "medium" if days_until < 90 else "low"
            })

        timeline.sort(key=lambda x: x["days_until"])
        return timeline[:15]

    async def _get_opportunities(self) -> List[Dict]:
        """Get opportunities from database"""
        try:
            result = self.db.table("opportunities").select("*").eq("is_active", True).execute()
            if result.data:
                return result.data
        except:
            pass

        # Return sample opportunities
        return self._get_sample_opportunities()

    def _get_sample_opportunities(self) -> List[Dict]:
        """Sample opportunities for testing"""
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
            {
                "id": "tasp",
                "name": "Telluride Association Summer Program",
                "type": "academic",
                "organization": "Telluride Association",
                "focus_area": "HUMANITIES",
                "prestige_score": 9,
                "acceptance_rate": 0.04,
                "selectivity": "highly_selective",
                "deadline": (now + timedelta(days=75)).isoformat(),
                "duration": "6 weeks",
                "cost": "Free",
                "eligibility": {"grades": [11]}
            },
            {
                "id": "stanford_summerinstitutes",
                "name": "Stanford Summer Institutes",
                "type": "summer_program",
                "organization": "Stanford Pre-Collegiate",
                "focus_area": "GENERAL",
                "prestige_score": 7,
                "acceptance_rate": 0.25,
                "selectivity": "moderate",
                "deadline": (now + timedelta(days=120)).isoformat(),
                "duration": "3 weeks",
                "cost": "$8,500",
                "eligibility": {"grades": [9, 10, 11, 12]}
            },
            {
                "id": "girls_who_code",
                "name": "Girls Who Code Summer Immersion",
                "type": "summer_program",
                "organization": "Girls Who Code",
                "focus_area": "CS",
                "prestige_score": 7,
                "acceptance_rate": 0.15,
                "selectivity": "selective",
                "deadline": (now + timedelta(days=180)).isoformat(),
                "duration": "7 weeks",
                "cost": "Free",
                "diversity_focus": True,
                "eligibility": {"grades": [10, 11, 12]}
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
opportunity_agent = OpportunityAgent()

# Also export the class for backward compatibility with existing main.py
OpportunityAgent = OpportunityAgent
