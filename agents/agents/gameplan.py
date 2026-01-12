# Game Plan Agent - Complete Implementation
# File: agents/agents/gameplan.py
#
# This replaces the stub implementation with real ROI filtering and identity seeds
#
# Architecture (Surgical Enhancement v2):
# ========================================
# Assessment (DIAGNOSIS) → Game Plan (PRESCRIPTION)
#
# Assessment extracts RAW components:
# - raw_identity: ethnicity, first-gen, geographic, self-described
# - raw_aptitude: GPA, SAT, skills, achievements
# - raw_passion: spike, brag text, keywords
# - raw_service: hours, leadership, communities served
#
# Game Plan Agent SYNTHESIZES these into Master Narrative:
# 1. Extract First Principle passion (Jenny's "Who are you fundamentally?")
# 2. Create brand statement from IDENTITY + APTITUDE + PASSION + SERVICE
# 3. Filter ALL recommendations through narrative lens
# 4. Build roadmap structured around narrative

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio

from langchain_openai import ChatOpenAI

from tools.database import get_supabase_client
from .gameplan_narrative import (
    NarrativeSynthesizer,
    NarrativeFilter,
    MasterNarrative,
    FirstPrinciplePassion,
)


# Touchpoint types for activity evaluation (ACP-005)
TOUCHPOINTS = [
    "club_leadership",      # Can lead a club related to this
    "workshop_teaching",    # Can teach workshops about this
    "research_publication", # Can produce research/publication
    "award_application",    # Can apply to awards with this
    "essay_material",       # Provides essay content
    "internship_connection", # Opens internship doors
    "rec_letter_source"     # Recommender can speak to this
]


class GamePlanAgent:
    """
    Game Plan Agent: Generates strategic roadmap optimized for hidden target

    Primitives Used:
    - ACP-004: Strategic Overwhelm (1.4x task assignment)
    - ACP-005: Multi-Touchpoint Leverage (>=4 touchpoints required)
    - ACP-006: Identity Seed Architecture (6-12 month advance planting)

    Autonomy: HIGH (planning), handoff if narrative coherence < 80%
    """

    def __init__(self):
        self.name = "GamePlan"
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        self.db = get_supabase_client()
        self.overwhelm_factor = 1.4  # ACP-004: 1.4x capacity assignment
        self.min_touchpoints = 4     # ACP-005: Minimum touchpoints required

        # Narrative synthesis components (Surgical Enhancement v2)
        self.narrative_synthesizer = NarrativeSynthesizer()
        self.narrative_filter: Optional[NarrativeFilter] = None
        self.master_narrative: Optional[MasterNarrative] = None

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """Main processing entry point."""
        return await self.generate(profile_id, kwargs.get("data"))

    async def generate(self, profile_id: str, assessment_data: Optional[Dict] = None) -> Dict:
        """
        Generate complete game plan with:
        1. Master Narrative synthesis (PRESCRIPTION phase)
        2. Activities filtered by ROI AND narrative alignment
        3. Identity seeds planted
        4. Strategic overwhelm applied
        5. All recommendations filtered through narrative

        Architecture:
        Assessment (DIAGNOSIS) provides raw_identity, raw_aptitude, raw_passion, raw_service
        Game Plan (PRESCRIPTION) synthesizes these into Master Narrative
        Every recommendation is filtered through narrative lens
        """
        try:
            # Get profile and assessment data
            profile = await self._get_profile(profile_id)
            if not profile:
                return {"success": False, "error": "Profile not found"}

            # =====================================================================
            # STEP 0: SYNTHESIZE MASTER NARRATIVE (Surgical Enhancement v2)
            # This is the foundation of the entire game plan
            # Jenny's Formula: IDENTITY + APTITUDE + PASSION + SERVICE = NARRATIVE
            # =====================================================================

            raw_extraction = self._extract_raw_components(profile, assessment_data)
            self.master_narrative = self.narrative_synthesizer.synthesize(raw_extraction)
            self.narrative_filter = NarrativeFilter(self.master_narrative)

            # Legacy support: narrative_dna is now the brand_statement
            narrative_dna = self.master_narrative.brand_statement
            hidden_target = profile.get("hidden_target")

            # Step 1: Filter activities by ROI (ACP-005)
            activities = await self.filter_activities_by_roi(profile)

            # Step 1.5: Filter activities through narrative (NEW)
            if self.narrative_filter and activities:
                activities = self.narrative_filter.filter_recommendations(activities)

            # Step 2: Plant identity seeds (ACP-006)
            deadlines = self._get_target_deadlines(profile)
            seeds = await self.plant_identity_seeds(profile, deadlines)

            # Step 3: Apply strategic overwhelm (ACP-004)
            overwhelmed_activities = self.apply_strategic_overwhelm(activities)

            # Step 4: Thread narrative DNA through activities
            threaded_plan = await self.thread_narrative_dna(
                overwhelmed_activities, narrative_dna, hidden_target
            )

            # Step 5: Generate phases and timeline
            phases = await self.generate_phases(threaded_plan, profile)

            # Step 6: Validate narrative coherence (NEW)
            narrative_coherence = None
            if self.narrative_filter:
                narrative_coherence = self.narrative_filter.validate_gameplan_coherence(
                    activities=threaded_plan,
                    awards=[],  # Will be populated when Awards Agent is integrated
                    programs=[],  # Will be populated when Opportunity Agent is integrated
                )

            # Build game plan
            game_plan = {
                "profile_id": profile_id,
                # Master Narrative (NEW - Surgical Enhancement v2)
                "master_narrative": self.master_narrative.to_dict() if self.master_narrative else None,
                "narrative_coherence": narrative_coherence,
                # Legacy support
                "narrative_dna": narrative_dna,
                "hidden_target": hidden_target,
                "activities": threaded_plan,
                "identity_seeds": seeds,
                "phases": phases,
                "summary": {
                    "total_activities": len(threaded_plan),
                    "total_touchpoints": sum(a.get("touchpoint_count", 0) for a in threaded_plan),
                    "average_roi": sum(a.get("roi", 0) for a in threaded_plan) / len(threaded_plan) if threaded_plan else 0,
                    "expected_completion_rate": 0.73,  # Strategic overwhelm target
                    "narrative_score": self.master_narrative.total_score if self.master_narrative else 0,
                    "narrative_coherence_score": narrative_coherence.get("coherence_score", 0) if narrative_coherence else 0,
                },
                "created_at": datetime.now().isoformat()
            }

            # Store in database
            await self._save_game_plan(profile_id, game_plan)

            # Update profile with identity seeds
            self.db.table("profiles").update({
                "identity_seeds": seeds,
                "updated_at": datetime.now().isoformat()
            }).eq("id", profile_id).execute()

            # Version state
            await self._version_state(profile_id, "gameplan_generated", {
                "activities_count": len(threaded_plan),
                "seeds_count": len(seeds),
                "phases_count": len(phases)
            })

            # Publish event
            await self._publish_event("GAMEPLAN_GENERATED", {
                "profileId": profile_id,
                "activities": [a.get("name", a.get("title", "")) for a in threaded_plan[:5]],
                "seeds": [s.get("target", "") for s in seeds]
            })

            return {
                "success": True,
                "game_plan": game_plan,
                "requires_handoff": len(threaded_plan) < 3  # Too few activities
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def filter_activities_by_roi(self, profile: Dict) -> List[Dict]:
        """
        ACP-005: Multi-Touchpoint Leverage

        Every activity MUST serve >=4 application touchpoints or be filtered out.
        ROI = (touchpoints x prestige_multiplier) / hours_invested
        """
        # Get profile signals
        profile_data = profile.get("profile_data", {})
        passion = profile_data.get("passion", {})
        aptitude = profile_data.get("aptitude", {})

        spike_category = passion.get("spike_category", "GENERAL")
        intended_major = profile_data.get("intended_major", profile.get("intended_major", ""))
        grade = profile_data.get("identity", {}).get("grade", 11)

        # Get activity templates from database or generate recommendations
        activities = await self._get_activity_recommendations(spike_category, intended_major, grade)

        evaluated_activities = []

        for activity in activities:
            # Count touchpoints
            touchpoints = self._count_touchpoints(activity, profile)
            touchpoint_count = len(touchpoints)

            # Skip if below minimum (ACP-005 rule)
            if touchpoint_count < self.min_touchpoints:
                continue

            # Calculate ROI
            prestige = activity.get("prestige_score", 5)
            hours = activity.get("hours_per_week", 5) * activity.get("weeks_per_year", 40)
            hours = max(hours, 10)  # Minimum to avoid division issues

            roi = (touchpoint_count * prestige) / (hours / 100)  # Normalize

            # Calculate narrative alignment
            narrative_dna = profile.get("narrative_dna", "")
            alignment = await self._calculate_narrative_alignment(activity, narrative_dna)

            evaluated_activities.append({
                "activity": activity,
                "name": activity.get("name", activity.get("title", "Activity")),
                "description": activity.get("description", ""),
                "category": activity.get("category", spike_category),
                "touchpoints": touchpoints,
                "touchpoint_count": touchpoint_count,
                "prestige_score": prestige,
                "hours_required": hours,
                "roi": round(roi, 3),
                "narrative_alignment": alignment,
                "recommended": True,
                "rationale": f"Serves {touchpoint_count} touchpoints with ROI of {roi:.2f}"
            })

        # Sort by ROI * alignment
        evaluated_activities.sort(
            key=lambda x: x["roi"] * x.get("narrative_alignment", 1.0),
            reverse=True
        )

        return evaluated_activities

    def _count_touchpoints(self, activity: Dict, profile: Dict) -> List[str]:
        """Count which touchpoints an activity serves"""
        touchpoints = []

        activity_type = activity.get("type", "").lower()
        category = activity.get("category", "").lower()
        name = activity.get("name", "").lower()

        # Club leadership potential
        if activity_type in ["club", "organization", "leadership"] or "club" in name or "lead" in name:
            touchpoints.append("club_leadership")

        # Workshop teaching potential
        if activity_type in ["teaching", "tutoring", "workshop"] or "teach" in name or "mentor" in name:
            touchpoints.append("workshop_teaching")

        # Research/publication potential
        if activity_type in ["research", "project", "independent"] or "research" in name or "project" in name:
            touchpoints.append("research_publication")

        # Award application potential
        if activity.get("has_awards", False) or category in ["competition", "academic", "stem"]:
            touchpoints.append("award_application")

        # Essay material (almost everything)
        if activity.get("impact_potential", 5) >= 5 or activity.get("personal_growth", False):
            touchpoints.append("essay_material")

        # Internship connection
        if activity_type in ["internship", "work", "professional"] or "intern" in name or "work" in name:
            touchpoints.append("internship_connection")

        # Recommendation letter source
        if activity.get("has_mentor", False) or activity_type in ["research", "internship", "club"]:
            touchpoints.append("rec_letter_source")

        # Default: at least essay material for any substantive activity
        if not touchpoints and activity.get("hours_per_week", 0) >= 3:
            touchpoints.append("essay_material")
            if activity.get("hours_per_week", 0) >= 5:
                touchpoints.append("rec_letter_source")

        return touchpoints

    async def _get_activity_recommendations(self, spike: str, major: str, grade: int) -> List[Dict]:
        """Get activity recommendations based on profile"""

        # Try database first
        try:
            result = self.db.table("activity_templates").select("*").execute()
            if result.data and len(result.data) > 0:
                # Filter by spike/major relevance
                return [a for a in result.data if self._activity_matches(a, spike, major)]
        except:
            pass

        # Generate recommendations using LLM
        prompt = f"""Generate 10 high-impact extracurricular activity recommendations for a student with:

- Spike Category: {spike}
- Intended Major: {major}
- Current Grade: {grade}

For each activity, provide:
- name: Activity name
- description: Brief description
- type: club/research/competition/service/internship/creative
- category: Academic category
- hours_per_week: Estimated weekly hours (3-15)
- weeks_per_year: Weeks active (20-52)
- prestige_score: 1-10 prestige rating
- has_awards: boolean - are there awards available?
- has_mentor: boolean - will they have a mentor?
- impact_potential: 1-10 impact score
- personal_growth: boolean

Return as JSON array. Focus on activities that serve MULTIPLE touchpoints (leadership, research, awards, essays, etc.)."""

        try:
            response = await self.llm.ainvoke(prompt)
            # Clean response and parse JSON
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content)
        except:
            # Fallback activities
            return self._get_fallback_activities(spike, major)

    def _activity_matches(self, activity: Dict, spike: str, major: str) -> bool:
        """Check if activity matches student profile"""
        activity_category = activity.get("category", "").upper()
        activity_spike = activity.get("spike_category", "").upper()

        return (
            activity_category in [spike.upper(), major.upper(), "GENERAL"] or
            activity_spike in [spike.upper(), "GENERAL"] or
            spike.upper() in activity.get("tags", [])
        )

    def _get_fallback_activities(self, spike: str, major: str) -> List[Dict]:
        """Fallback activity recommendations"""
        base_activities = [
            {
                "name": f"{spike} Research Project",
                "description": f"Independent research in {major} under faculty mentorship",
                "type": "research",
                "category": spike,
                "hours_per_week": 8,
                "weeks_per_year": 40,
                "prestige_score": 8,
                "has_awards": True,
                "has_mentor": True,
                "impact_potential": 8,
                "personal_growth": True
            },
            {
                "name": f"{spike} Club Founder/President",
                "description": f"Lead a student organization focused on {major}",
                "type": "club",
                "category": spike,
                "hours_per_week": 6,
                "weeks_per_year": 36,
                "prestige_score": 7,
                "has_awards": True,
                "has_mentor": False,
                "impact_potential": 7,
                "personal_growth": True
            },
            {
                "name": "Community Teaching Initiative",
                "description": f"Teach {major} concepts to underserved students",
                "type": "teaching",
                "category": "SERVICE",
                "hours_per_week": 4,
                "weeks_per_year": 30,
                "prestige_score": 6,
                "has_awards": True,
                "has_mentor": True,
                "impact_potential": 8,
                "personal_growth": True
            },
            {
                "name": f"{spike} Competition Team",
                "description": f"Compete in national {major}-related competitions",
                "type": "competition",
                "category": spike,
                "hours_per_week": 5,
                "weeks_per_year": 35,
                "prestige_score": 8,
                "has_awards": True,
                "has_mentor": True,
                "impact_potential": 7,
                "personal_growth": True
            },
            {
                "name": "Industry Internship",
                "description": f"Professional experience in {major} field",
                "type": "internship",
                "category": "PROFESSIONAL",
                "hours_per_week": 20,
                "weeks_per_year": 10,
                "prestige_score": 8,
                "has_awards": False,
                "has_mentor": True,
                "impact_potential": 7,
                "personal_growth": True
            }
        ]
        return base_activities

    async def _calculate_narrative_alignment(self, activity: Dict, narrative_dna: str) -> float:
        """Calculate how well activity aligns with narrative DNA"""
        if not narrative_dna:
            return 0.7  # Default alignment

        activity_text = f"{activity.get('name', '')} {activity.get('description', '')}"

        # Quick keyword matching for performance
        narrative_words = set(narrative_dna.lower().split())
        activity_words = set(activity_text.lower().split())

        overlap = len(narrative_words & activity_words)
        if overlap >= 3:
            return 0.95
        elif overlap >= 2:
            return 0.85
        elif overlap >= 1:
            return 0.75
        else:
            return 0.6

    async def plant_identity_seeds(self, profile: Dict, deadlines: List[Dict]) -> List[Dict]:
        """
        ACP-006: Identity Seed Architecture

        Plant identity seeds 6-12 months before they need to bloom.
        Backward-schedule from target deadlines.
        """
        if not deadlines:
            # Generate default deadlines based on grade
            profile_data = profile.get("profile_data", {})
            grade = profile_data.get("identity", {}).get("grade", 11)
            deadlines = self._generate_default_deadlines(grade)

        seeds = []
        narrative_dna = profile.get("narrative_dna", "")

        for deadline in deadlines:
            deadline_date = deadline.get("date")
            if isinstance(deadline_date, str):
                try:
                    deadline_date = datetime.fromisoformat(deadline_date.replace("Z", "+00:00"))
                except:
                    deadline_date = datetime.now() + timedelta(days=180)

            # Calculate seed planting date (8 months before)
            seed_date = deadline_date - timedelta(days=240)

            # Generate seed actions
            actions = await self._generate_seed_actions(
                profile, deadline, narrative_dna
            )

            seed = {
                "id": f"seed-{deadline.get('name', 'unknown').lower().replace(' ', '-')}",
                "target": deadline.get("name", "Unknown Deadline"),
                "target_type": deadline.get("type", "application"),
                "plant_date": seed_date.isoformat(),
                "bloom_date": deadline_date.isoformat(),
                "months_until_bloom": max(0, (deadline_date - datetime.now()).days // 30),
                "actions": actions,
                "status": "planned",
                "narrative_connection": self._connect_to_narrative(deadline, narrative_dna)
            }

            seeds.append(seed)

            # Publish event for each seed
            await self._publish_event("IDENTITY_SEED_PLANTED", {
                "profileId": profile.get("id"),
                "seed": seed["target"],
                "bloomDate": seed["bloom_date"]
            })

        # Sort by bloom date
        seeds.sort(key=lambda x: x["bloom_date"])

        return seeds

    def _get_target_deadlines(self, profile: Dict) -> List[Dict]:
        """Extract target deadlines from profile"""
        deadlines = []

        target_schools = profile.get("target_schools",
                         profile.get("profile_data", {}).get("target_schools", []))

        # Add Early Action/Early Decision deadlines
        for school in target_schools[:4]:  # Top 4 schools
            school_name = school if isinstance(school, str) else school.get("name", "School")
            deadlines.append({
                "name": f"{school_name} Early Application",
                "type": "early_application",
                "date": (datetime.now().replace(month=11, day=1) + timedelta(days=365 if datetime.now().month > 9 else 0)).isoformat()
            })

        # Add Regular Decision
        deadlines.append({
            "name": "Regular Decision Applications",
            "type": "regular_application",
            "date": (datetime.now().replace(month=1, day=1) + timedelta(days=365 if datetime.now().month > 1 else 0)).isoformat()
        })

        # Add summer program deadlines
        deadlines.append({
            "name": "Summer Program Applications",
            "type": "summer_program",
            "date": (datetime.now().replace(month=2, day=1) + timedelta(days=365 if datetime.now().month > 2 else 0)).isoformat()
        })

        return deadlines

    def _generate_default_deadlines(self, grade: int) -> List[Dict]:
        """Generate default deadlines based on grade"""
        now = datetime.now()

        if grade <= 10:
            # Focus on summer programs and skill building
            return [
                {"name": "Summer Program Applications", "type": "summer_program",
                 "date": (now + timedelta(days=180)).isoformat()},
                {"name": "Research Opportunity Search", "type": "research",
                 "date": (now + timedelta(days=120)).isoformat()},
                {"name": "Award Applications Round 1", "type": "awards",
                 "date": (now + timedelta(days=240)).isoformat()}
            ]
        elif grade == 11:
            # Focus on test prep, research, applications
            return [
                {"name": "SAT/ACT Target Date", "type": "testing",
                 "date": (now + timedelta(days=120)).isoformat()},
                {"name": "Summer Program Applications", "type": "summer_program",
                 "date": (now + timedelta(days=60)).isoformat()},
                {"name": "Research Publication Deadline", "type": "research",
                 "date": (now + timedelta(days=180)).isoformat()},
                {"name": "Early Application Prep", "type": "early_application",
                 "date": (now + timedelta(days=300)).isoformat()}
            ]
        else:
            # Grade 12 - focus on applications
            return [
                {"name": "Early Decision/Action", "type": "early_application",
                 "date": now.replace(month=11, day=1).isoformat()},
                {"name": "Regular Decision", "type": "regular_application",
                 "date": (now.replace(month=1, day=1) + timedelta(days=365 if now.month > 1 else 0)).isoformat()}
            ]

    async def _generate_seed_actions(self, profile: Dict, deadline: Dict, narrative_dna: str) -> List[Dict]:
        """Generate specific actions for an identity seed"""

        prompt = f"""Generate 4-5 specific preparatory actions a student should take 6-8 months before:

**Deadline:** {deadline.get('name')}
**Deadline Type:** {deadline.get('type')}
**Student's Narrative DNA:** {narrative_dna if narrative_dna else 'Not yet synthesized'}

Each action should:
1. Be specific and actionable (start with a verb)
2. Have a clear completion criteria
3. Connect to their narrative when possible
4. Be completable in 1-4 weeks

Return as JSON array:
[
    {{
        "action": "Specific action description",
        "timeframe": "Week 1-2",
        "completion_criteria": "How to know it's done",
        "narrative_connection": "How this supports their story"
    }}
]"""

        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content)
        except:
            # Fallback actions
            return [
                {
                    "action": f"Research requirements for {deadline.get('name')}",
                    "timeframe": "Week 1-2",
                    "completion_criteria": "Have complete list of requirements",
                    "narrative_connection": "Understand how to present your story"
                },
                {
                    "action": "Identify 2-3 accomplishments to highlight",
                    "timeframe": "Week 2-3",
                    "completion_criteria": "Have specific examples ready",
                    "narrative_connection": "Select achievements that match narrative"
                },
                {
                    "action": "Draft initial materials/essays",
                    "timeframe": "Week 3-6",
                    "completion_criteria": "Complete first draft",
                    "narrative_connection": "Thread narrative DNA throughout"
                },
                {
                    "action": "Get feedback from mentor/counselor",
                    "timeframe": "Week 6-8",
                    "completion_criteria": "Incorporate feedback into revision",
                    "narrative_connection": "Ensure authenticity"
                }
            ]

    def _connect_to_narrative(self, deadline: Dict, narrative_dna: str) -> str:
        """Generate connection between deadline and narrative"""
        if not narrative_dna:
            return "Develop and demonstrate your unique story"

        deadline_type = deadline.get("type", "")
        if deadline_type == "early_application":
            return f"Show how '{narrative_dna}' evolved through your activities"
        elif deadline_type == "summer_program":
            return f"Demonstrate commitment to '{narrative_dna}' through structured program"
        elif deadline_type == "research":
            return f"Produce tangible evidence supporting '{narrative_dna}'"
        else:
            return f"Another chapter in the story of '{narrative_dna}'"

    def apply_strategic_overwhelm(self, activities: List[Dict]) -> List[Dict]:
        """
        ACP-004: Strategic Overwhelm

        Assign 10 tasks -> complete 7 is BETTER than assign 7 -> complete 5
        Inflate task list by 1.4x factor
        """
        if not activities:
            return activities

        base_count = len(activities)
        target_count = int(base_count * self.overwhelm_factor)

        # If we need more activities, add stretch versions
        overwhelmed = activities.copy()

        while len(overwhelmed) < target_count and activities:
            # Create stretch versions of top activities
            source_idx = (len(overwhelmed) - base_count) % len(activities)
            source = activities[source_idx]

            stretch = {
                **source,
                "name": f"{source.get('name', 'Activity')} (Advanced)",
                "description": f"Enhanced version: {source.get('description', '')}",
                "is_stretch": True,
                "difficulty_multiplier": 1.3,
                "prestige_score": min(10, source.get("prestige_score", 5) + 1)
            }
            overwhelmed.append(stretch)

        return overwhelmed

    async def thread_narrative_dna(self, activities: List[Dict], narrative_dna: str, hidden_target: str) -> List[Dict]:
        """
        Thread narrative DNA through all activities
        Add narrative connection to each activity
        """
        if not narrative_dna:
            return activities

        threaded = []
        for activity in activities:
            activity_copy = activity.copy()

            # Generate narrative thread
            activity_copy["narrative_thread"] = await self._generate_narrative_thread(
                activity, narrative_dna
            )

            # Add hidden target optimization note (internal only)
            if hidden_target:
                activity_copy["_hidden_target_alignment"] = self._calculate_target_alignment(
                    activity, hidden_target
                )

            threaded.append(activity_copy)

        return threaded

    async def _generate_narrative_thread(self, activity: Dict, narrative_dna: str) -> str:
        """Generate how this activity connects to narrative"""
        activity_name = activity.get("name", "this activity")

        # Simple template-based threading for performance
        templates = [
            f"Through {activity_name}, I demonstrate my commitment to {narrative_dna}",
            f"{activity_name} represents a tangible expression of my mission: {narrative_dna}",
            f"This activity shows how I'm actively working toward {narrative_dna}",
            f"{activity_name} builds the skills needed to achieve {narrative_dna}"
        ]

        # Pick based on activity type
        activity_type = activity.get("type", "general").lower()
        if activity_type in ["research", "project"]:
            return templates[0]
        elif activity_type in ["club", "leadership"]:
            return templates[1]
        elif activity_type in ["service", "teaching"]:
            return templates[2]
        else:
            return templates[3]

    def _calculate_target_alignment(self, activity: Dict, hidden_target: str) -> float:
        """Calculate how well activity aligns with hidden target school"""
        # Simple heuristic - in production, use school-specific data
        return 0.8  # Default good alignment

    async def generate_phases(self, activities: List[Dict], profile: Dict) -> List[Dict]:
        """Generate execution phases with timeline"""
        profile_data = profile.get("profile_data", {})
        grade = profile_data.get("identity", {}).get("grade", 11)

        # Determine phase structure based on grade
        if grade <= 10:
            phases = [
                {"name": "Foundation Building", "duration": "Months 1-3", "focus": "Establish core activities"},
                {"name": "Skill Development", "duration": "Months 4-6", "focus": "Deepen expertise"},
                {"name": "Impact Creation", "duration": "Months 7-12", "focus": "Generate measurable results"}
            ]
        elif grade == 11:
            phases = [
                {"name": "Immediate Priorities", "duration": "Months 1-2", "focus": "Critical activities first"},
                {"name": "Building Momentum", "duration": "Months 3-6", "focus": "Scale impact"},
                {"name": "Application Prep", "duration": "Months 7-12", "focus": "Position for applications"}
            ]
        else:
            phases = [
                {"name": "Final Polish", "duration": "Months 1-2", "focus": "Complete ongoing work"},
                {"name": "Application Sprint", "duration": "Months 3-4", "focus": "Submit applications"}
            ]

        # Distribute activities across phases
        activities_per_phase = len(activities) // len(phases) if phases else len(activities)

        for i, phase in enumerate(phases):
            start_idx = i * activities_per_phase
            end_idx = start_idx + activities_per_phase if i < len(phases) - 1 else len(activities)
            phase["activities"] = activities[start_idx:end_idx]
            phase["activity_count"] = len(phase["activities"])

        return phases

    async def _save_game_plan(self, profile_id: str, game_plan: Dict):
        """Save game plan to database"""
        # Check for existing active plan
        existing = self.db.table("game_plans").select("id").eq(
            "user_id", profile_id
        ).eq("plan_status", "active").execute()

        if existing.data:
            # Archive existing plan
            self.db.table("game_plans").update({
                "plan_status": "archived",
                "updated_at": datetime.now().isoformat()
            }).eq("id", existing.data[0]["id"]).execute()

        # Insert new plan
        self.db.table("game_plans").insert({
            "user_id": profile_id,
            "plan_data": game_plan,
            "plan_status": "active",
            "current_phase": game_plan.get("phases", [{}])[0].get("name", "Phase 1"),
            "current_week": 1,
            "completion_percentage": 0,
            "created_at": datetime.now().isoformat()
        }).execute()

    async def _get_profile(self, profile_id: str) -> Optional[Dict]:
        """Get profile with assessment data"""
        result = self.db.table("profiles").select("*").eq("id", profile_id).single().execute()
        if result.data:
            # Get latest assessment
            assessment = self.db.table("assessments").select("profile_data, scores").eq(
                "user_id", profile_id
            ).order("completed_at", desc=True).limit(1).execute()

            if assessment.data:
                result.data["profile_data"] = assessment.data[0].get("profile_data", {})

            return result.data
        return None

    def _extract_raw_components(
        self,
        profile: Dict,
        assessment_data: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Extract raw narrative components from profile for synthesis

        This mirrors the TypeScript assessmentExtractor.ts but in Python.
        The raw components are what Game Plan Agent synthesizes into Master Narrative.

        Returns:
            Dict with raw_identity, raw_aptitude, raw_passion, raw_service
        """
        profile_data = profile.get("profile_data", {})

        # If assessment_data is provided and already has raw components, use them
        if assessment_data:
            if all(key in assessment_data for key in ['raw_identity', 'raw_aptitude', 'raw_passion', 'raw_service']):
                return assessment_data

        # Otherwise, extract from profile_data
        demographics = profile_data.get("demographics", {})
        aptitude = profile_data.get("aptitude", {})
        passion = profile_data.get("passion", {})
        community = profile_data.get("community", {})
        assessment_intelligence = profile_data.get("assessment_intelligence", {})

        # Extract raw identity
        self_described = []
        brag_text = passion.get("brag_text", "") or ""
        identity_keywords = ['quiet', 'introverted', 'shy', 'outgoing', 'leader',
                            'builder', 'creator', 'helper', 'advocate', 'first-gen', 'immigrant']
        for kw in identity_keywords:
            if kw in brag_text.lower():
                self_described.append(kw)

        raw_identity = {
            "ethnicity": demographics.get("ethnicity"),
            "religion": None,
            "first_gen": demographics.get("first_gen", False),
            "family_structure": [],
            "geographic_origin": profile_data.get("high_school", {}).get("region"),
            "socioeconomic": self._infer_socioeconomic(demographics.get("income_band")),
            "introversion_score": assessment_intelligence.get("psychometrics", {}).get("introversion_extroversion"),
            "self_described_identity": self_described,
        }

        # Extract raw aptitude
        mentioned_skills = []
        major = profile_data.get("intended_major", "") or ""
        skill_map = {
            'computer': ['coding', 'technology'],
            'cs': ['coding', 'technology'],
            'bio': ['research', 'science'],
            'engineer': ['engineering', 'problem-solving'],
            'business': ['entrepreneurship', 'leadership'],
        }
        for keyword, skills in skill_map.items():
            if keyword in major.lower():
                mentioned_skills.extend(skills)

        raw_aptitude = {
            "gpa_weighted": aptitude.get("gpa_weighted"),
            "gpa_unweighted": aptitude.get("gpa_unweighted"),
            "sat_total": aptitude.get("sat_total"),
            "ap_count": aptitude.get("ap_count", 0),
            "rigor_level": self._infer_rigor_level(aptitude.get("rigor_normalized")),
            "academic_awards": aptitude.get("academic_awards", []),
            "competitions_entered": [],
            "intended_major": profile_data.get("intended_major"),
            "mentioned_skills": list(set(mentioned_skills)),
        }

        # Extract raw passion
        passion_keywords = []
        all_text = ' '.join([
            passion.get("brag_text", "") or "",
            passion.get("leadership_description", "") or "",
            passion.get("project_description", "") or "",
        ]).lower()

        keywords = ['game', 'film', 'music', 'art', 'code', 'build', 'create',
                   'research', 'discover', 'help', 'teach', 'lead', 'write', 'design']
        for kw in keywords:
            if kw in all_text:
                passion_keywords.append(kw)

        raw_passion = {
            "spike_category": passion.get("spike_category"),
            "spike_description": passion.get("leadership_description"),
            "brag_text": passion.get("brag_text"),
            "activities": [],
            "projects": [],
            "passion_keywords": passion_keywords,
        }

        # Extract raw service
        communities_served = []
        service_desc = (community.get("service_description", "") or "").lower()
        community_map = {
            'underrepresented': 'underrepresented communities',
            'minority': 'minority communities',
            'youth': 'youth/students',
            'women': 'women/girls',
            'girl': 'women/girls',
            'immigrant': 'immigrant communities',
        }
        for keyword, comm in community_map.items():
            if keyword in service_desc:
                communities_served.append(comm)

        raw_service = {
            "service_hours": community.get("service_hours", 0),
            "service_leadership": community.get("service_leadership"),
            "service_description": community.get("service_description"),
            "service_cause": None,
            "communities_served": list(set(communities_served)),
        }

        return {
            "raw_identity": raw_identity,
            "raw_aptitude": raw_aptitude,
            "raw_passion": raw_passion,
            "raw_service": raw_service,
            "scores": assessment_data.get("scores", {}) if assessment_data else {},
            "gaps": assessment_data.get("gaps", []) if assessment_data else [],
            "archetype": profile.get("archetype", "GENERIC"),
            "archetype_confidence": profile.get("archetype_confidence", 0.5),
        }

    def _infer_socioeconomic(self, income_band: Optional[str]) -> Optional[str]:
        """Infer socioeconomic status from income band"""
        if not income_band:
            return None
        socio_map = {
            'BELOW_75K': 'working class',
            '75K_150K': 'middle class',
            '150K_300K': 'upper middle class',
            'ABOVE_300K': 'affluent',
            'TOP_1_PERCENT': 'top 1%',
            'PREFER_NOT_SAY': None,
        }
        return socio_map.get(income_band)

    def _infer_rigor_level(self, rigor_normalized: Optional[float]) -> str:
        """Infer rigor level from normalized score"""
        if rigor_normalized is None:
            return 'MEDIUM'
        if rigor_normalized >= 0.9:
            return 'MAXIMUM'
        if rigor_normalized >= 0.7:
            return 'HIGH'
        if rigor_normalized >= 0.4:
            return 'MEDIUM'
        return 'LOW'

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
gameplan_agent = GamePlanAgent()

# Also export the class for backward compatibility with existing main.py
GamePlanAgent = GamePlanAgent
