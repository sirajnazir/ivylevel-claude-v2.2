"""
IvyQuest v10.0 Narrative Synthesis Agent
========================================
Synthesizes personalized narratives using Jenny's Formula:
IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE

"Because I am [IDENTITY], I use [APTITUDE] and [PASSION] to [SERVICE],
becoming [UNIQUE ROLE]"

Example Output for Huda:
"An Indian Muslim builder who creates tech to empower underrepresented girls in STEM"
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os

# Try Google Gemini first (more reliable), fallback to OpenAI
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_API_KEY = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    USE_GEMINI = bool(GOOGLE_API_KEY)
except ImportError:
    USE_GEMINI = False
    GOOGLE_API_KEY = None

from langchain_openai import ChatOpenAI

from tools.database import get_supabase_client
from config import settings

# v8: Middleware Integration (40 patterns)
from .mixins import MiddlewareIntegrationMixin

# v11: Coaching Asset Integration (139 techniques)
try:
    from intelligence.registry import AssetRegistry, AssetSelector
    from intelligence.primitives import AssetDomain
    from intelligence.student import StudentIntelligenceProfile
    COACHING_ASSETS_AVAILABLE = True
except ImportError:
    COACHING_ASSETS_AVAILABLE = False
    AssetRegistry = None
    AssetSelector = None
    AssetDomain = None
    StudentIntelligenceProfile = None

import logging
mw_logger = logging.getLogger(__name__)


class NarrativeSynthesisAgent(MiddlewareIntegrationMixin):
    """
    Narrative Synthesis Agent: Transforms four pillar scores into a personalized narrative.

    Uses Jenny's Formula to create:
    - brand_statement: One powerful sentence capturing unique identity
    - narrative_dna: 2-3 paragraph personalized narrative
    - first_principle: The core "why" driving the student
    - themes: Key recurring themes that tie activities together

    Autonomy: HIGH (synthesis), handoff if confidence < 0.7

    v8: Integrated with MiddlewareStackV8 (40 patterns) for:
    - J1: Reasoning Traces
    - J3: Audit Trail
    - E4: Quality Scoring (narrative quality)
    - H3: Retry Logic
    """

    def __init__(self):
        self.name = "NarrativeSynthesis"
        # Prefer Google Gemini for reliability
        if USE_GEMINI:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=GOOGLE_API_KEY,
                temperature=0.7
            )
            print(f"[NarrativeSynthesis] Using Google Gemini")
        else:
            self.llm = ChatOpenAI(model=settings.agent_primary_model, temperature=0.7)
            print(f"[NarrativeSynthesis] Using OpenAI {settings.agent_primary_model}")
        self.db = get_supabase_client()

        # v8: Initialize middleware integration (40 patterns)
        try:
            self.init_middleware(
                supabase_client=self.db,
                llm_client=self.llm,
            )
        except Exception as e:
            mw_logger.warning(f"Middleware init failed (non-fatal): {e}")

        # v11: Initialize coaching asset selector (139 techniques)
        self.asset_selector = None
        self.asset_registry = None
        if COACHING_ASSETS_AVAILABLE:
            try:
                self.asset_registry = AssetRegistry(self.db)
                self.asset_selector = AssetSelector(self.asset_registry)
                mw_logger.info(f"[NarrativeSynthesis] Coaching assets enabled (139 techniques)")
            except Exception as e:
                mw_logger.warning(f"Coaching asset init failed (non-fatal): {e}")

    async def _select_narrative_technique(
        self,
        profile_id: str,
        identity_context: Dict[str, Any],
        archetype: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Select the best coaching technique for narrative synthesis.

        Uses the 139-technique library to find techniques relevant to:
        - Identity (C19: Hyphen Identity, H4: Cultural Gem Mining)
        - Essays (C1-C25 essay techniques)
        - Content optimization (I1-I10)

        Returns:
            Selected technique with content or None if unavailable
        """
        if not self.asset_selector:
            return None

        try:
            # Build context for technique selection
            context = {
                "event_type": "narrative_synthesis",
                "keywords": ["identity", "narrative", "brand", "story"],
                "tags": ["identity", "essays", "authenticity"],
            }

            # Add identity-specific keywords
            identity_summary = identity_context.get("summary", "")
            if "immigrant" in identity_summary.lower():
                context["keywords"].append("immigrant")
            if "first-generation" in identity_summary.lower():
                context["keywords"].append("first-gen")
            if identity_context.get("cultural_background"):
                context["keywords"].append("cultural")

            # Create minimal student profile for selection
            # In production, this would use the actual StudentIntelligenceProfile
            class MinimalProfile:
                def __init__(self, archetype_name):
                    self.pressure_response = "balanced"
                    self.risk_tolerance = "medium"
                    self.motivation_style = "intrinsic"
                    self.feedback_reception = "direct"
                    self.celebration_preference = "private"
                    self.task_approach = "sequential"
                    self.failure_recovery = "moderate"
                    self.overwhelm_threshold = 0.7
                    self.communication_style = "direct"

                def get_coaching_adaptations(self):
                    return {}

            profile = MinimalProfile(archetype)

            # Select technique focused on essays domain
            result = await self.asset_selector.select(
                context=context,
                student_profile=profile,
                domain=AssetDomain.ESSAYS,
            )

            if result.success:
                technique = result.asset
                return {
                    "id": str(technique.id),
                    "name": technique.name,
                    "content": technique.content,
                    "score": result.score,
                    "reasoning": result.reasoning,
                }

            return None

        except Exception as e:
            mw_logger.warning(f"Technique selection failed (non-fatal): {e}")
            return None

    async def _track_technique_usage(
        self,
        profile_id: str,
        technique_id: str,
        outcome: Dict[str, Any],
    ) -> None:
        """Track technique usage for effectiveness learning."""
        if not self.asset_registry:
            return

        try:
            from uuid import UUID
            await self.asset_registry.record_usage(
                asset_id=UUID(technique_id),
                profile_id=UUID(profile_id),
                agent_name=self.name,
                trigger_context="narrative_synthesis",
                outcome=outcome,
            )
        except Exception as e:
            mw_logger.warning(f"Technique usage tracking failed (non-fatal): {e}")

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Main processing entry point.

        v8: Wrapped with MiddlewareStackV8 (40 patterns):
        - J1: Reasoning traces for observability
        - J3: Audit trail for compliance
        - E4: Quality scoring (narrative quality)
        """
        # v8: Generate session context
        session_id = kwargs.get("session_id") or f"narrative_{profile_id}"
        trace_id = self.start_reasoning_trace(profile_id, session_id, "narrative_synthesis")

        try:
            async with self.with_middleware_context(profile_id, session_id, "narrative_synthesis") as ctx:
                self.add_thought(trace_id, f"Starting narrative synthesis for profile {profile_id}")

                self.add_action(trace_id, "synthesize", {
                    "has_assessment_contract": bool(kwargs.get("assessment_contract"))
                })

                # Call the core synthesis logic
                result = await self.synthesize(profile_id, kwargs.get("assessment_contract"))

                # v8: Score quality (E4) - especially important for narratives
                if result.get("success") and result.get("narrative_dna"):
                    narrative_str = str(result.get("narrative_dna", ""))[:1000]
                    quality = await self.score_quality(narrative_str, "narrative_synthesis")
                    if quality:
                        result["_quality_score"] = quality.overall_score

                # v8: Finalize with middleware
                result = self.middleware_finalize(result, output_type="narrative_synthesis")

                # v8: Audit trail (J3)
                await self.audit_action(
                    action="narrative_synthesis",
                    resource_type="narrative",
                    resource_id=profile_id,
                    details={
                        "confidence": result.get("confidence", 0),
                        "requires_handoff": result.get("requires_handoff", False),
                        "themes_count": len(result.get("themes", [])),
                    },
                    success=result.get("success", False),
                )

                await self.end_reasoning_trace(trace_id, success=True)
                return result

        except Exception as e:
            await self.end_reasoning_trace(trace_id, success=False, error=str(e))
            raise

    async def synthesize(
        self,
        profile_id: str,
        assessment_contract: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Synthesize a personalized narrative from assessment data.

        Args:
            profile_id: Profile UUID
            assessment_contract: Optional pre-computed assessment data

        Returns:
            {
                "success": True,
                "brand_statement": "One powerful sentence",
                "narrative_dna": "2-3 paragraph story",
                "first_principle": "Core driving why",
                "themes": ["theme1", "theme2", "theme3"],
                "confidence": 0.85,
                "requires_handoff": False
            }
        """
        try:
            # Get assessment contract (scores + profile data)
            if not assessment_contract:
                assessment_contract = await self._get_assessment_contract(profile_id)

            if not assessment_contract:
                # Return placeholder data instead of error for graceful frontend handling
                return {
                    "success": True,
                    "brand_statement": "Complete your assessment to unlock your unique narrative",
                    "narrative_dna": "Your personalized narrative will be generated once you complete the IvyQuest assessment. This will synthesize your identity, aptitude, passion, and service into a compelling story.",
                    "first_principle": "Discover your driving purpose",
                    "themes": ["Identity", "Potential", "Growth"],
                    "confidence": 0.0,
                    "requires_handoff": False,
                    "placeholder": True
                }

            # Extract the four pillars
            identity = self._extract_identity(assessment_contract)
            aptitude = self._extract_aptitude(assessment_contract)
            passion = self._extract_passion(assessment_contract)
            service = self._extract_service(assessment_contract)

            # v11: Select relevant coaching technique (139-technique library)
            archetype_info = assessment_contract.get("archetype")
            archetype_name = archetype_info.get("id") if isinstance(archetype_info, dict) else archetype_info
            selected_technique = await self._select_narrative_technique(
                profile_id=profile_id,
                identity_context=identity,
                archetype=archetype_name,
            )

            # Build the synthesis prompt (with optional technique guidance)
            prompt = self._build_synthesis_prompt(
                identity=identity,
                aptitude=aptitude,
                passion=passion,
                service=service,
                scores=assessment_contract.get("scores", {}),
                archetype=assessment_contract.get("archetype"),
                technique=selected_technique,  # v11: Pass selected technique
            )

            # Generate narrative via LLM
            response = await self.llm.ainvoke(prompt)
            result = self._parse_response(response.content)

            # Validate confidence
            confidence = result.get("confidence", 0.7)
            confidence = min(max(confidence, 0.3), 0.95)

            # Build output
            output = {
                "success": True,
                "brand_statement": result.get("brand_statement", ""),
                "narrative_dna": result.get("narrative_dna", ""),
                "first_principle": result.get("first_principle", ""),
                "themes": result.get("themes", []),
                "confidence": confidence,
                "requires_handoff": confidence < 0.7,
                "synthesis_inputs": {
                    "identity": identity,
                    "aptitude": aptitude,
                    "passion": passion,
                    "service": service
                }
            }

            # v11: Add technique info to output
            if selected_technique:
                output["_coaching_technique"] = {
                    "id": selected_technique["id"],
                    "name": selected_technique["name"],
                    "score": selected_technique["score"],
                }

            # Store in database
            await self._store_narrative(profile_id, output)

            # Version state
            await self._version_state(profile_id, "narrative_synthesized", output)

            # v11: Track technique usage for effectiveness learning
            if selected_technique:
                await self._track_technique_usage(
                    profile_id=profile_id,
                    technique_id=selected_technique["id"],
                    outcome={
                        "confidence": confidence,
                        "themes_generated": len(result.get("themes", [])),
                        "requires_handoff": confidence < 0.7,
                    },
                )

            return output

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_identity(self, contract: Dict) -> Dict[str, Any]:
        """Extract identity components from assessment contract."""
        profile_data = contract.get("profile_data", {})
        operating = profile_data.get("operating", {})

        # Background fields (newly added)
        gender = operating.get("gender", "PREFER_NOT_SAY")
        cultural_background = operating.get("culturalBackground", [])
        immigration_status = operating.get("immigrationStatus", "PREFER_NOT_SAY")
        religion = operating.get("religion")

        # Existing identity fields
        first_gen = operating.get("firstGeneration", False)
        recruited_athlete = operating.get("recruitedAthlete", False)

        # Demographics if available
        demographics = profile_data.get("demographics", {})
        ethnicity = demographics.get("ethnicity", cultural_background[0] if cultural_background else None)

        # Score
        identity_score = contract.get("scores", {}).get("identity", 0.5)

        return {
            "gender": gender,
            "cultural_background": cultural_background,
            "ethnicity": ethnicity,
            "immigration_status": immigration_status,
            "religion": religion,
            "first_generation": first_gen,
            "recruited_athlete": recruited_athlete,
            "identity_score": identity_score,
            # Human-readable summary
            "summary": self._summarize_identity(
                gender, cultural_background, ethnicity,
                immigration_status, religion, first_gen
            )
        }

    def _summarize_identity(
        self,
        gender: str,
        cultural_background: List[str],
        ethnicity: Optional[str],
        immigration_status: str,
        religion: Optional[str],
        first_gen: bool
    ) -> str:
        """Create human-readable identity summary."""
        parts = []

        # Cultural/ethnic identity
        ethnicity_map = {
            "SOUTH_ASIAN": "South Asian",
            "SOUTHEAST_ASIAN": "Southeast Asian",
            "ASIAN": "East Asian",
            "MIDDLE_EASTERN": "Middle Eastern",
            "BLACK": "Black",
            "HISPANIC": "Hispanic/Latino",
            "WHITE": "White",
            "NATIVE": "Native American",
            "PACIFIC_ISLANDER": "Pacific Islander",
            "MULTIRACIAL": "Multiracial"
        }

        if cultural_background:
            cultural_str = ", ".join([ethnicity_map.get(c, c) for c in cultural_background[:2]])
            parts.append(cultural_str)
        elif ethnicity and ethnicity not in ["PREFER_NOT_SAY", "OTHER"]:
            parts.append(ethnicity_map.get(ethnicity, ethnicity))

        # Religion (if specified)
        if religion and religion.strip():
            parts.append(religion)

        # Immigration
        if immigration_status == "FIRST_GEN_IMMIGRANT":
            parts.append("first-generation immigrant")
        elif immigration_status == "PARENTS_IMMIGRATED":
            parts.append("child of immigrants")

        # First-gen college
        if first_gen:
            parts.append("first-generation college student")

        if not parts:
            return "unique background"

        return " ".join(parts) if len(parts) <= 2 else f"{parts[0]} {parts[1]}" + (f" ({parts[2]})" if len(parts) > 2 else "")

    def _extract_aptitude(self, contract: Dict) -> Dict[str, Any]:
        """Extract aptitude components from assessment contract."""
        profile_data = contract.get("profile_data", {})
        aptitude_data = profile_data.get("aptitude", {})

        gpa = aptitude_data.get("gpa_weighted", aptitude_data.get("gpaWeighted"))
        sat = aptitude_data.get("sat_total", aptitude_data.get("satTotal"))
        ap_count = aptitude_data.get("ap_count", aptitude_data.get("apCount", 0))
        awards = aptitude_data.get("awards", [])

        # Score
        aptitude_score = contract.get("scores", {}).get("aptitude", 0.5)

        # Intended major (key for narrative)
        intended_major = profile_data.get("intended_major",
                         profile_data.get("operating", {}).get("intendedMajor", "Undeclared"))

        return {
            "gpa": gpa,
            "sat": sat,
            "ap_count": ap_count,
            "awards": awards,
            "intended_major": intended_major,
            "aptitude_score": aptitude_score,
            "summary": self._summarize_aptitude(gpa, sat, ap_count, intended_major)
        }

    def _summarize_aptitude(
        self,
        gpa: Optional[float],
        sat: Optional[int],
        ap_count: int,
        intended_major: str
    ) -> str:
        """Create human-readable aptitude summary."""
        parts = []

        if sat and sat >= 1500:
            parts.append("exceptional test scores")
        elif sat and sat >= 1400:
            parts.append("strong test scores")

        if gpa and gpa >= 4.0:
            parts.append("outstanding academics")
        elif gpa and gpa >= 3.7:
            parts.append("strong academics")

        if ap_count >= 8:
            parts.append("rigorous coursework")

        if intended_major and intended_major != "Undeclared":
            parts.append(f"pursuing {intended_major}")

        if not parts:
            return "developing academic foundation"

        return ", ".join(parts)

    def _extract_passion(self, contract: Dict) -> Dict[str, Any]:
        """Extract passion components from assessment contract."""
        profile_data = contract.get("profile_data", {})
        passion_data = profile_data.get("passion", {})

        spike_category = passion_data.get("spike_category", passion_data.get("spikeCategory", "GENERAL"))
        leadership_level = passion_data.get("leadership_level", passion_data.get("leadershipLevel", "MEMBER"))
        research_level = passion_data.get("research_level", passion_data.get("researchLevel"))
        brag_text = passion_data.get("brag_text", passion_data.get("bragText", ""))
        project_description = passion_data.get("project_description", passion_data.get("projectDescription", ""))
        ec_commitment = passion_data.get("ec_commitment", passion_data.get("ecCommitment", 0))

        # Score
        passion_score = contract.get("scores", {}).get("passion", 0.5)

        return {
            "spike_category": spike_category,
            "leadership_level": leadership_level,
            "research_level": research_level,
            "brag_text": brag_text,
            "project_description": project_description,
            "ec_commitment": ec_commitment,
            "passion_score": passion_score,
            "summary": self._summarize_passion(spike_category, leadership_level, brag_text)
        }

    def _summarize_passion(
        self,
        spike_category: str,
        leadership_level: str,
        brag_text: str
    ) -> str:
        """Create human-readable passion summary."""
        spike_map = {
            "STEM": "STEM and technology",
            "ARTS": "arts and creativity",
            "SERVICE": "community service",
            "LEADERSHIP": "leadership",
            "ATHLETICS": "athletics",
            "ENTREPRENEURSHIP": "entrepreneurship",
            "RESEARCH": "research",
            "GENERAL": "diverse interests"
        }

        leadership_map = {
            "FOUNDER_NATIONAL": "national organization founder",
            "FOUNDER_STATE": "state organization founder",
            "FOUNDER_LOCAL": "local organization founder",
            "NATIONAL_PRES": "national leadership",
            "STATE_PRES": "state leadership",
            "SCHOOL_PRES": "school leadership",
            "MEMBER": "active participant"
        }

        spike_str = spike_map.get(spike_category, spike_category)
        leadership_str = leadership_map.get(leadership_level, "participant")

        return f"{spike_str} with {leadership_str}"

    def _extract_service(self, contract: Dict) -> Dict[str, Any]:
        """Extract service/community components from assessment contract."""
        profile_data = contract.get("profile_data", {})
        community_data = profile_data.get("community", {})

        service_hours = community_data.get("service_hours", community_data.get("serviceHours", 0))
        community_impact = community_data.get("community_impact", community_data.get("communityImpact", ""))
        service_leadership = community_data.get("service_leadership", community_data.get("serviceLeadership", ""))
        description = community_data.get("description", "")

        # Score
        service_score = contract.get("scores", {}).get("community", 0.5)

        return {
            "service_hours": service_hours,
            "community_impact": community_impact,
            "service_leadership": service_leadership,
            "description": description,
            "service_score": service_score,
            "summary": self._summarize_service(service_hours, community_impact, service_leadership)
        }

    def _summarize_service(
        self,
        service_hours: int,
        community_impact: str,
        service_leadership: str
    ) -> str:
        """Create human-readable service summary."""
        parts = []

        if service_hours >= 500:
            parts.append("exceptional community commitment")
        elif service_hours >= 200:
            parts.append("significant community involvement")
        elif service_hours >= 100:
            parts.append("community engagement")
        else:
            parts.append("developing community connection")

        if service_leadership in ["LEADER", "ORGANIZER", "FOUNDER"]:
            parts.append("service leadership")

        return ", ".join(parts) if parts else "community participation"

    def _build_synthesis_prompt(
        self,
        identity: Dict,
        aptitude: Dict,
        passion: Dict,
        service: Dict,
        scores: Dict,
        archetype: Optional[Dict],
        technique: Optional[Dict] = None,  # v11: Coaching technique from 139-asset library
    ) -> str:
        """Build the LLM prompt for narrative synthesis."""

        archetype_label = archetype.get("label", "Scholar") if archetype else "Scholar"
        archetype_rationale = archetype.get("rationale", "") if archetype else ""

        # v11: Build technique guidance section if a coaching technique was selected
        technique_guidance = ""
        if technique:
            technique_guidance = f"""
## COACHING TECHNIQUE (from IvyLevel KB)
Apply this expert coaching technique in your narrative synthesis:

**{technique.get('name', 'Coaching Technique')}** ({technique.get('id', 'TECH')})
Category: {technique.get('category', 'General')}
{technique.get('description', '')}

Trigger Conditions: {technique.get('trigger_conditions', 'Apply when relevant to student profile')}
Expected Outcome: {technique.get('expected_outcome', 'Enhanced narrative clarity and impact')}

IMPORTANT: Subtly incorporate this technique's principles into the narrative. Do not mention the technique by name - let it shape how you frame the student's story.
"""

        return f"""You are an elite college admissions strategist with 20+ years of experience placing students at top universities. Your task is to synthesize a powerful, authentic narrative for this student.
{technique_guidance}

CRITICAL: Do NOT use any names like "Jenny", "John", or any made-up names in the narrative. Refer to the student as "this student", "they", or write in a way that describes their journey without using a specific name. The narrative should be written about the student in third person without naming them.

## THE IVYLEVEL NARRATIVE FORMULA
Create a narrative using this proven formula:
"Because I am [IDENTITY], I use [APTITUDE] and [PASSION] to [SERVICE], becoming [UNIQUE ROLE]"

## STUDENT PROFILE

### Identity ({scores.get('identity', 0.5)*100:.0f}% score)
{identity['summary']}
- Cultural Background: {identity.get('cultural_background', [])}
- Religion/Traditions: {identity.get('religion', 'Not specified')}
- Immigration: {identity.get('immigration_status', 'Not specified')}
- First-Generation: {identity.get('first_generation', False)}

### Aptitude ({scores.get('aptitude', 0.5)*100:.0f}% score)
{aptitude['summary']}
- GPA: {aptitude.get('gpa', 'Not specified')}
- SAT: {aptitude.get('sat', 'Not specified')}
- AP Courses: {aptitude.get('ap_count', 0)}
- Intended Major: {aptitude.get('intended_major', 'Undeclared')}
- Awards: {', '.join(aptitude.get('awards', [])) if aptitude.get('awards') else 'None listed'}

### Passion ({scores.get('passion', 0.5)*100:.0f}% score)
{passion['summary']}
- Spike Category: {passion.get('spike_category', 'GENERAL')}
- Leadership Level: {passion.get('leadership_level', 'MEMBER')}
- Research Level: {passion.get('research_level', 'None')}
- Student's Own Words: "{passion.get('brag_text', 'Not provided')}"
- Project Description: "{passion.get('project_description', 'Not provided')}"

### Service ({scores.get('community', 0.5)*100:.0f}% score)
{service['summary']}
- Service Hours: {service.get('service_hours', 0)}
- Impact Level: {service.get('community_impact', 'Not specified')}
- Service Leadership: {service.get('service_leadership', 'Not specified')}

### Detected Archetype
{archetype_label}
{archetype_rationale}

## YOUR TASK

1. **Brand Statement** (15-25 words): One powerful sentence that captures this student's unique identity and mission. It should be memorable and specific enough that an admissions officer would remember it.

2. **Narrative DNA** (2-3 paragraphs): A compelling narrative that:
   - Threads through all their activities coherently
   - Transforms any constraints into strengths
   - Shows authentic self-discovery and growth
   - Demonstrates impact and future potential
   - IMPORTANT: Do NOT use any names. Write about "this student", "they", or describe their journey in third person without a name.

3. **First Principle**: The core "why" that drives this student (1 sentence)

4. **Themes** (3-5 themes): Key recurring themes that tie their story together

## EXAMPLES

Brand Statement: "An Indian Muslim builder who creates tech to empower underrepresented girls in STEM"
Brand Statement: "A first-generation Latina artist using data visualization to make climate change tangible for her community"
Brand Statement: "A Vietnamese refugee's son transforming family restaurant struggles into AI solutions for immigrant small businesses"

## OUTPUT FORMAT

Return ONLY valid JSON:
{{
    "brand_statement": "One powerful 15-25 word sentence",
    "narrative_dna": "2-3 paragraph compelling narrative",
    "first_principle": "The core why in one sentence",
    "themes": ["theme1", "theme2", "theme3", "theme4"],
    "confidence": 0.85
}}

Focus on AUTHENTICITY, SPECIFICITY, and IMPACT. Avoid generic statements."""

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response, handling potential JSON errors."""
        try:
            # Try to find JSON in response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())
        except json.JSONDecodeError:
            # Fallback: extract what we can
            return {
                "brand_statement": content[:200] if len(content) > 200 else content,
                "narrative_dna": content,
                "first_principle": "Manual review required",
                "themes": [],
                "confidence": 0.4
            }

    async def _get_assessment_contract(self, profile_id: str) -> Optional[Dict]:
        """Get assessment contract from database."""
        try:
            # Get profile
            profile_result = self.db.table("profiles").select("*").eq("id", profile_id).single().execute()

            if not profile_result.data:
                return None

            # Get latest assessment
            assessment_result = self.db.table("assessments").select(
                "profile_data, scores, archetype, archetype_confidence"
            ).eq("user_id", profile_id).order("completed_at", desc=True).limit(1).execute()

            assessment = assessment_result.data[0] if assessment_result.data else {}

            return {
                "profile": profile_result.data,
                "profile_data": assessment.get("profile_data", {}),
                "scores": assessment.get("scores", {}),
                "archetype": {
                    "id": assessment.get("archetype"),
                    "confidence": assessment.get("archetype_confidence"),
                } if assessment.get("archetype") else None
            }
        except Exception as e:
            print(f"Error getting assessment contract: {e}")
            return None

    async def _store_narrative(self, profile_id: str, narrative: Dict) -> bool:
        """Store synthesized narrative in database."""
        try:
            # Update profile with narrative
            self.db.table("profiles").update({
                "narrative_brand_statement": narrative.get("brand_statement"),
                "narrative_dna": narrative.get("narrative_dna"),
                "narrative_first_principle": narrative.get("first_principle"),
                "narrative_themes": narrative.get("themes"),
                "narrative_confidence": narrative.get("confidence"),
                "narrative_updated_at": datetime.now().isoformat()
            }).eq("id", profile_id).execute()

            return True
        except Exception as e:
            print(f"Warning: Could not store narrative: {e}")
            return False

    async def _version_state(self, profile_id: str, event: str, state: Dict):
        """Version state change for rollback capability."""
        try:
            self.db.table("agent_state_versions").insert({
                "profile_id": profile_id,
                "agent": self.name,
                "state": state,
                "event_type": event,
                "created_by": "agent",
                "created_at": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Warning: State versioning failed: {e}")


# Export singleton instance
narrative_synthesis_agent = NarrativeSynthesisAgent()
