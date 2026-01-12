# Awards Agent - Complete Implementation
# File: agents/agents/awards.py
#
# This replaces the stub with real win probability and portfolio balancing

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from langchain_openai import ChatOpenAI

from tools.database import get_supabase_client


class AwardsAgent:
    """
    Awards Agent: Matches students to awards with ROI optimization

    Primitives Used:
    - ACP-001: Hidden Probability Matrix (win probability calculation)

    Autonomy: FULL (deterministic matching)
    Huda Benchmark: >40% win rate (Huda actual: 62.5% = 5/8)
    """

    def __init__(self):
        self.name = "Awards"
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.db = get_supabase_client()

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """Main processing entry point."""
        return await self.match(profile_id)

    async def match(self, profile_id: str) -> Dict[str, Any]:
        """Match profile to awards with ROI calculation."""
        try:
            profile = await self._get_profile(profile_id)
            if not profile:
                return {"success": False, "error": "Profile not found"}

            # Get all active awards
            awards = await self._get_awards()

            # Filter by eligibility
            eligible_awards = self._filter_by_eligibility(awards, profile)

            # Calculate win probability for each
            matched_awards = []
            for award in eligible_awards:
                probability = await self.calculate_win_probability(profile, award)
                effort = award.get("effort_hours", 20)
                prestige = award.get("prestige_score", 5)

                # ROI = (probability × prestige) / effort
                roi = (probability * prestige * 100) / max(effort, 1)

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
                    "recommendation": self._get_recommendation(probability)
                })

            # Sort by ROI
            matched_awards.sort(key=lambda x: x["roi"], reverse=True)

            # Balance portfolio
            portfolio = self.balance_portfolio(matched_awards)

            # Version state
            await self._version_state(profile_id, "awards_matched", {
                "matches_count": len(matched_awards),
                "portfolio_summary": {
                    "likely": len(portfolio.get("likely", [])),
                    "target": len(portfolio.get("target", [])),
                    "stretch": len(portfolio.get("stretch", []))
                }
            })

            # Publish event for best matches
            if matched_awards:
                await self._publish_event("AWARD_MATCHED", {
                    "profileId": profile_id,
                    "awardId": matched_awards[0]["award_id"],
                    "probability": matched_awards[0]["win_probability"]
                })

            return {
                "success": True,
                "total_matches": len(matched_awards),
                "portfolio": portfolio,
                "top_recommendations": matched_awards[:10],
                "timeline": self._generate_timeline(matched_awards)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

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
        """Get profile with assessment data"""
        result = self.db.table("profiles").select("*").eq("id", profile_id).single().execute()
        if result.data:
            assessment = self.db.table("assessments").select("profile_data, scores").eq(
                "user_id", profile_id
            ).order("completed_at", desc=True).limit(1).execute()

            if assessment.data:
                result.data["profile_data"] = assessment.data[0].get("profile_data", {})

            return result.data
        return None

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
