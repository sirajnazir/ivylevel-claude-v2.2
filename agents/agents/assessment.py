# Assessment Agent - Complete Implementation
# File: agents/agents/assessment.py
#
# This replaces the stub implementation with full LLM-powered narrative synthesis

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import asyncio

from langchain_openai import ChatOpenAI

from tools.database import get_supabase_client, get_profile_with_assessment
from tools.cri import compute_cri, get_chetty_baseline


class AssessmentAgent:
    """
    Assessment Agent: Diagnoses student state and generates strategic intelligence

    Primitives Used:
    - ACP-001: Hidden Probability Matrix
    - ACP-002: Identity Synthesis Framework

    Autonomy: HIGH (synthesis), handoff if confidence < 0.7
    """

    def __init__(self):
        self.name = "Assessment"
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        self.db = get_supabase_client()

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """Main processing entry point."""
        return await self.enhance(profile_id, kwargs.get("data"))

    async def enhance(self, profile_id: str, data: Optional[Dict] = None) -> Dict:
        """
        Run full assessment enhancement pipeline

        Steps:
        1. Synthesize Narrative DNA (ACP-002)
        2. Detect Archetype with confidence
        3. Compute CRI (Context Relativity Index)
        4. Calculate Hidden Probabilities (ACP-001)
        5. Identify Hidden Target
        """
        try:
            # Get current profile
            profile = await self._get_profile(profile_id)
            if not profile:
                return {"success": False, "error": "Profile not found"}

            # Merge with any new data
            if data:
                profile = {**profile, **data}

            # Step 1: Synthesize Narrative DNA
            narrative = await self.synthesize_narrative_dna(profile)

            # Step 2: Detect Archetype
            archetype = await self.detect_archetype(profile, narrative)

            # Step 3: Compute CRI
            cri = await compute_cri(profile)

            # Step 4: Calculate Hidden Probabilities
            probabilities = await self.calculate_hidden_probabilities(profile, cri)

            # Step 5: Identify Hidden Target
            hidden_target = self._identify_hidden_target(probabilities)

            # Step 6: Reframe Constraints (ACP-010 partial)
            constraint_reframes = await self.reframe_constraints(profile, narrative)

            # Build update payload
            update = {
                "narrative_dna": narrative["dna"],
                "archetype_id": archetype["id"],
                "archetype_confidence": archetype["confidence"],
                "archetype_rationale": archetype["rationale"],
                "cri": cri,
                "hidden_probabilities": probabilities,
                "hidden_target": hidden_target,
                "constraint_reframes": constraint_reframes,
                "updated_at": datetime.now().isoformat()
            }

            # Update profile in database
            self.db.table("profiles").update(update).eq("id", profile_id).execute()

            # Version state
            await self._version_state(profile_id, "assessment_enhanced", {
                "narrative": narrative,
                "archetype": archetype,
                "cri": cri,
                "hidden_target": hidden_target
            })

            # Publish event
            await self._publish_event("ASSESSMENT_COMPLETED", {
                "profileId": profile_id,
                "narrativeDna": narrative["dna"],
                "cri": cri,
                "archetype": archetype["label"]
            })

            # Also publish narrative DNA event
            await self._publish_event("NARRATIVE_DNA_SYNTHESIZED", {
                "profileId": profile_id,
                "dna": narrative["dna"],
                "confidence": narrative["confidence"],
                "themes": narrative["themes"]
            })

            return {
                "success": True,
                "narrative_dna": narrative,
                "archetype": archetype,
                "cri": cri,
                "hidden_target": hidden_target,
                "constraint_reframes": constraint_reframes,
                "requires_handoff": archetype["confidence"] < 0.7
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def synthesize_narrative_dna(self, profile: Dict) -> Dict:
        """
        ACP-002: Identity Synthesis Framework

        The "12-second moment" where scattered interests crystallize into a
        single narrative DNA sentence that threads through all activities.

        Returns:
        {
            "dna": "Single crystallized narrative sentence",
            "themes": ["theme1", "theme2", "theme3"],
            "confidence": 0.85,
            "rationale": "Why this narrative fits",
            "identity_markers": ["marker1", "marker2"]
        }
        """
        # Extract relevant profile data
        passion = profile.get("passion", profile.get("profile_data", {}).get("passion", {}))
        operating = profile.get("operating", profile.get("profile_data", {}).get("operating", {}))
        identity = profile.get("identity", profile.get("profile_data", {}).get("identity", {}))
        demographics = profile.get("demographics", profile.get("profile_data", {}).get("demographics", {}))

        spike_category = passion.get("spike_category", "GENERAL")
        brag_text = passion.get("brag_text", "")
        project_description = passion.get("project_description", "")
        leadership_level = passion.get("leadership_level", "")
        research_level = passion.get("research_level", "")

        strengths = operating.get("strengths", [])
        career_direction = operating.get("careerDirection", "")
        favorite_subject = operating.get("favoriteSubject", "")

        intended_major = profile.get("intended_major",
                         profile.get("profile_data", {}).get("intended_major", ""))

        # Build constraints list
        constraints = []
        if demographics.get("first_gen"):
            constraints.append("first-generation college student")
        if operating.get("firstGeneration"):
            constraints.append("first-generation")
        if demographics.get("underrepresented") or demographics.get("ethnicity") not in [None, "PREFER_NOT_SAY", "WHITE", "ASIAN"]:
            constraints.append("underrepresented background")
        # Add family responsibilities if mentioned
        if "family" in str(brag_text).lower() or "work" in str(operating).lower():
            constraints.append("family responsibilities")

        prompt = f"""You are an elite college admissions coach with 20+ years of experience at top programs.

Analyze this student profile and synthesize their Narrative DNA - the single crystallized sentence that captures their unique identity and mission.

## STUDENT PROFILE

**Spike Category:** {spike_category}
**Intended Major:** {intended_major}
**Favorite Subject:** {favorite_subject}
**Career Direction:** {career_direction}

**Strengths:** {', '.join(strengths) if strengths else 'Not specified'}
**Leadership Level:** {leadership_level}
**Research Level:** {research_level}

**Brag Text (student's own words):**
{brag_text if brag_text else 'Not provided'}

**Project Description:**
{project_description if project_description else 'Not provided'}

**Constraints/Challenges:**
{', '.join(constraints) if constraints else 'None identified'}

## YOUR TASK

Create a Narrative DNA that:
1. Captures their UNIQUE identity in ONE powerful sentence (15-25 words)
2. Can thread through ALL their activities coherently
3. Transforms any constraints into STRENGTHS
4. Would make an admissions officer remember this student

## EXAMPLES OF EXCELLENT NARRATIVE DNA

- "Bridging algorithmic justice with Muslim identity through community tech education"
- "Transforming family restaurant struggles into data-driven solutions for immigrant small businesses"
- "Using competitive debate skills to amplify underrepresented voices in environmental policy"
- "Turning childhood asthma into a mission to democratize health information for low-income communities"

## OUTPUT FORMAT

Return ONLY valid JSON:
{{
    "dna": "Your synthesized narrative DNA sentence (15-25 words)",
    "themes": ["primary_theme", "secondary_theme", "tertiary_theme"],
    "confidence": 0.85,
    "rationale": "2-3 sentences explaining why this narrative fits and how it threads activities",
    "identity_markers": ["unique_identifier_1", "unique_identifier_2", "unique_identifier_3"]
}}

Focus on AUTHENTICITY and DIFFERENTIATION. Avoid generic statements."""

        try:
            response = await self.llm.ainvoke(prompt)
            result = json.loads(response.content)

            # Validate required fields
            if not result.get("dna") or result["dna"] == "Student narrative DNA placeholder":
                raise ValueError("Invalid narrative DNA generated")

            # Ensure confidence is reasonable
            result["confidence"] = min(max(result.get("confidence", 0.7), 0.3), 0.95)

            return result

        except json.JSONDecodeError:
            # Try to extract from non-JSON response
            return {
                "dna": response.content[:200] if response else "Narrative synthesis failed",
                "themes": [spike_category, intended_major],
                "confidence": 0.5,
                "rationale": "Fallback narrative - manual review recommended",
                "identity_markers": strengths[:3] if strengths else []
            }
        except Exception as e:
            return {
                "dna": f"Error synthesizing narrative: {str(e)}",
                "themes": [],
                "confidence": 0.0,
                "rationale": "Error occurred during synthesis",
                "identity_markers": []
            }

    async def detect_archetype(self, profile: Dict, narrative: Dict) -> Dict:
        """
        Detect student archetype with confidence and explainable rationale

        Archetypes:
        - Constrained Gritty: Overcomes significant barriers
        - Academic Achiever: Research/academic excellence focus
        - Creative Innovator: Entrepreneurial/artistic
        - Community Leader: Service/advocacy focus
        """
        # Get available archetypes from database (with fallback if table doesn't exist)
        try:
            archetypes_result = self.db.table("archetypes").select("*").execute()
            archetypes = archetypes_result.data if archetypes_result.data else []
        except Exception:
            archetypes = []

        if not archetypes:
            # Default archetypes if table is empty
            archetypes = [
                {"id": "constrained-gritty", "label": "Constrained Gritty",
                 "patterns": {"constraints": ["family_duties", "low_ses", "first_gen"], "spikes": ["leadership", "service"]}},
                {"id": "academic-achiever", "label": "Academic Achiever",
                 "patterns": {"constraints": [], "spikes": ["research", "academics", "stem"]}},
                {"id": "creative-innovator", "label": "Creative Innovator",
                 "patterns": {"constraints": ["non_traditional"], "spikes": ["arts", "entrepreneurship", "business"]}},
                {"id": "community-leader", "label": "Community Leader",
                 "patterns": {"constraints": ["underrepresented"], "spikes": ["service", "advocacy", "leadership"]}}
            ]

        # Extract profile signals
        passion = profile.get("passion", profile.get("profile_data", {}).get("passion", {}))
        demographics = profile.get("demographics", profile.get("profile_data", {}).get("demographics", {}))
        operating = profile.get("operating", profile.get("profile_data", {}).get("operating", {}))

        spike = passion.get("spike_category", "GENERAL")
        first_gen = demographics.get("first_gen", False) or operating.get("firstGeneration", False)
        service_hours = profile.get("community", profile.get("profile_data", {}).get("community", {})).get("service_hours", 0)

        prompt = f"""Analyze this student and match them to the best archetype.

## STUDENT SIGNALS

**Narrative DNA:** {narrative.get('dna', 'Unknown')}
**Themes:** {narrative.get('themes', [])}
**Spike Category:** {spike}
**First Generation:** {first_gen}
**Service Hours:** {service_hours}
**Identity Markers:** {narrative.get('identity_markers', [])}

## AVAILABLE ARCHETYPES

{json.dumps(archetypes, indent=2)}

## OUTPUT FORMAT

Return ONLY valid JSON:
{{
    "id": "archetype-id-from-list",
    "label": "Archetype Label",
    "confidence": 0.85,
    "rationale": "2-3 sentences explaining why this archetype fits best",
    "secondary_archetype": "second-best-archetype-id"
}}

Choose the archetype that BEST captures this student's core identity."""

        try:
            response = await self.llm.ainvoke(prompt)
            result = json.loads(response.content)

            # Ensure confidence is reasonable
            result["confidence"] = min(max(result.get("confidence", 0.7), 0.3), 0.95)

            return result

        except Exception as e:
            # Fallback to rule-based detection
            if first_gen or service_hours > 200:
                return {
                    "id": "constrained-gritty",
                    "label": "Constrained Gritty",
                    "confidence": 0.6,
                    "rationale": "Fallback detection based on constraints/service"
                }
            elif spike in ["STEM", "RESEARCH", "ACADEMIC"]:
                return {
                    "id": "academic-achiever",
                    "label": "Academic Achiever",
                    "confidence": 0.6,
                    "rationale": "Fallback detection based on spike category"
                }
            else:
                return {
                    "id": "creative-innovator",
                    "label": "Creative Innovator",
                    "confidence": 0.5,
                    "rationale": "Default fallback archetype"
                }

    async def calculate_hidden_probabilities(self, profile: Dict, cri: float) -> Dict:
        """
        ACP-001: Hidden Probability Matrix

        Calculate admission probabilities for target schools.
        CRITICAL: These are NEVER shown to the user.
        """
        target_schools = profile.get("target_schools",
                         profile.get("profile_data", {}).get("target_schools", []))

        if not target_schools:
            return {}

        probabilities = {}

        # Get profile strength signals
        aptitude = profile.get("aptitude", profile.get("profile_data", {}).get("aptitude", {}))
        sat_score = aptitude.get("sat_total", 1200)
        gpa = aptitude.get("gpa_weighted", 3.5)

        passion = profile.get("passion", profile.get("profile_data", {}).get("passion", {}))
        leadership = passion.get("leadership_level", "MEMBER")

        intended_major = profile.get("intended_major",
                         profile.get("profile_data", {}).get("intended_major", "Undeclared"))

        # School base rates (simplified - should come from database)
        base_rates = {
            "HARVARD": 0.032, "YALE": 0.045, "PRINCETON": 0.040,
            "STANFORD": 0.037, "MIT": 0.033, "COLUMBIA": 0.037,
            "BROWN": 0.051, "PENN": 0.055, "DARTMOUTH": 0.062,
            "CORNELL": 0.079, "CALTECH": 0.027, "DUKE": 0.060,
            "CHICAGO": 0.059, "NORTHWESTERN": 0.070, "JHU": 0.071
        }

        # Major competitiveness multipliers
        competitive_majors = ["Computer Science", "Engineering", "Business", "Economics"]

        for school in target_schools:
            school_id = school.upper() if isinstance(school, str) else school.get("id", "").upper()
            base_rate = base_rates.get(school_id, 0.15)

            # Profile strength factor (0.5 - 1.5)
            strength = 0.8
            if sat_score > 1500:
                strength += 0.2
            elif sat_score > 1400:
                strength += 0.1

            if gpa > 4.5:
                strength += 0.2
            elif gpa > 4.0:
                strength += 0.1

            if leadership in ["FOUNDER_NATIONAL", "FOUNDER_STATE", "NATIONAL_PRES"]:
                strength += 0.2
            elif leadership in ["STATE_PRES", "SCHOOL_PRES"]:
                strength += 0.1

            # Major competitiveness factor
            major_factor = 0.8 if intended_major in competitive_majors else 1.0

            # Apply CRI boost
            cri_factor = cri if cri > 1.0 else 1.0

            # Calculate probability
            probability = base_rate * strength * major_factor * cri_factor
            probability = min(0.50, max(0.01, probability))  # Cap between 1% and 50%

            probabilities[school_id] = round(probability, 4)

        return probabilities

    def _identify_hidden_target(self, probabilities: Dict) -> Optional[str]:
        """
        Identify the school to optimize for (hidden from user)

        Strategy: Pick the second-best probability school as hidden target.
        The best is often a reach; second-best is strategic.
        """
        if not probabilities:
            return None

        sorted_schools = sorted(
            probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return second-best if exists, otherwise best
        if len(sorted_schools) >= 2:
            return sorted_schools[1][0]
        return sorted_schools[0][0] if sorted_schools else None

    async def reframe_constraints(self, profile: Dict, narrative: Dict) -> List[Dict]:
        """
        ACP-010 (Partial): Reframe constraints as strengths with SFFA rubric mapping
        """
        demographics = profile.get("demographics", profile.get("profile_data", {}).get("demographics", {}))
        operating = profile.get("operating", profile.get("profile_data", {}).get("operating", {}))

        constraints = []
        if demographics.get("first_gen") or operating.get("firstGeneration"):
            constraints.append("first-generation college student")
        if demographics.get("income_band") in ["LOW", "LOWER_MIDDLE"]:
            constraints.append("limited financial resources")
        if operating.get("availableHoursPerWeek", 20) < 10:
            constraints.append("significant time constraints")

        if not constraints:
            return []

        prompt = f"""Reframe these constraints as strengths for college applications.

## CONSTRAINTS
{json.dumps(constraints)}

## NARRATIVE DNA
{narrative.get('dna', 'Unknown')}

## SFFA RUBRIC CONTEXT
- Overcoming barriers scores 4/5 on SFFA rubric
- Talent alone scores 3/5
- Demonstrating resilience is highly valued

## OUTPUT FORMAT

Return ONLY valid JSON array:
[
    {{
        "constraint": "original constraint",
        "reframed_as": "how this is actually a strength",
        "narrative_angle": "how to present in essays",
        "rubric_score": 4
    }}
]"""

        try:
            response = await self.llm.ainvoke(prompt)
            return json.loads(response.content)
        except:
            return [{"constraint": c, "reframed_as": f"Demonstrates resilience: {c}",
                    "narrative_angle": "Overcame challenges", "rubric_score": 4}
                   for c in constraints]

    async def _get_profile(self, profile_id: str) -> Optional[Dict]:
        """Get profile with assessment data using centralized function."""
        return await get_profile_with_assessment(profile_id)

    async def _version_state(self, profile_id: str, event: str, state: Dict, created_by: str = "agent"):
        """Version state change for rollback capability"""
        try:
            version_result = self.db.rpc("get_next_version", {
                "p_profile_id": profile_id,
                "p_agent": self.name
            }).execute()

            version = version_result.data if version_result.data else 1

            self.db.table("agent_state_versions").insert({
                "profile_id": profile_id,
                "agent": self.name,
                "state": state,
                "version": version,
                "event_type": event,
                "created_by": created_by,
                "created_at": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Warning: State versioning failed: {e}")

    async def _publish_event(self, event_type: str, payload: Dict):
        """Publish event to event bus"""
        try:
            self.db.table("events").insert({
                "type": event_type,
                "payload": payload,
                "created_at": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Warning: Event publishing failed: {e}")


# Export for use
assessment_agent = AssessmentAgent()

# Also export the class for backward compatibility with existing main.py
AssessmentAgent = AssessmentAgent
