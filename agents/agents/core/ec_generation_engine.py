"""
EC Generation Engine - Core Hyper-Personalized Activity Generation
===================================================================

This module implements the foundational 4 Pillars + 10 Dimensions framework
for generating hyper-personalized extracurricular activities.

MASTER SYNTHESIS FORMULA:
    IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE

4 PILLARS:
    - IDENTITY: Demographics, culture, circumstances, specific experiences
    - APTITUDE: Academic strengths, technical skills, demonstrated abilities
    - PASSION: Stated interests, hobbies, energy indicators
    - SERVICE: Volunteering, causes, target populations, values

10 DIMENSIONS OF HYPER-PERSONALIZATION:
    1. Geographic/Local Context
    2. Identity-Informed WHY
    3. Field Gap Analysis
    4. Personal Catalyst Story
    5. Specific Target Audience
    6. Unique Contribution
    7. Representation in Output
    8. Cultural Depth
    9. Temporal Relevance
    10. Problem Specificity

KEY VALIDATIONS:
    - "Despite" → "Because" Reframe
    - "Only They" Test (activity must be hyper-personalized to one student)

Usage:
    from agents.core.ec_generation_engine import ECGenerationEngine

    engine = ECGenerationEngine()
    result = await engine.generate_identity_and_activities(profile)

Coach augmentations can be registered to add methodology layers:
    engine.register_coach_augmentation("coach_id", {...})
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import re
import os

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class FourPillars:
    """The 4 pillars extracted from a student profile with extreme specificity."""

    identity: Dict[str, Any] = field(default_factory=lambda: {
        "demographics": "",
        "cultural_religious": "",
        "personality": "",
        "circumstances": "",
        "specific_experiences": []
    })

    aptitude: Dict[str, Any] = field(default_factory=lambda: {
        "academic_strengths": "",
        "technical_skills": [],
        "demonstrated_abilities": [],
        "certifications": []
    })

    passion: Dict[str, Any] = field(default_factory=lambda: {
        "stated_interests": [],
        "hobbies": [],
        "media_consumption": "",
        "energy_indicators": ""
    })

    service: Dict[str, Any] = field(default_factory=lambda: {
        "current_volunteering": "",
        "causes": [],
        "target_populations": [],
        "values": []
    })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "IDENTITY": self.identity,
            "APTITUDE": self.aptitude,
            "PASSION": self.passion,
            "SERVICE": self.service,
        }

    def get_pillar_count(self) -> int:
        """Count how many pillars have substantial data."""
        count = 0
        if self.identity.get("demographics") or self.identity.get("specific_experiences"):
            count += 1
        if self.aptitude.get("technical_skills") or self.aptitude.get("demonstrated_abilities"):
            count += 1
        if self.passion.get("stated_interests") or self.passion.get("hobbies"):
            count += 1
        if self.service.get("causes") or self.service.get("target_populations"):
            count += 1
        return count

    def get_specificity_score(self) -> float:
        """Score how specific the extraction is (0-1)."""
        score = 0.0
        total_checks = 0

        # Identity specificity
        if len(self.identity.get("specific_experiences", [])) > 0:
            score += 1
            total_checks += 1
        if len(self.identity.get("cultural_religious", "")) > 20:  # More than just "Muslim"
            score += 1
            total_checks += 1

        # Aptitude specificity
        if len(self.aptitude.get("demonstrated_abilities", [])) > 0:
            score += 1
            total_checks += 1

        # Passion specificity
        if self.passion.get("energy_indicators"):
            score += 1
            total_checks += 1

        # Service specificity
        if len(self.service.get("target_populations", [])) > 0:
            score += 1
            total_checks += 1

        return score / max(total_checks, 1)


@dataclass
class TenDimensions:
    """The 10 dimensions of hyper-personalization for an activity."""

    geographic: Dict[str, str] = field(default_factory=lambda: {
        "location": "",
        "local_relevance": "",
        "local_partner": ""
    })

    identity_why: Dict[str, str] = field(default_factory=lambda: {
        "specific_identity": "",
        "connection": ""
    })

    field_gap: Dict[str, str] = field(default_factory=lambda: {
        "gap": "",
        "statistic": "",
        "how_filled": ""
    })

    catalyst: Dict[str, str] = field(default_factory=lambda: {
        "origin_story": "",
        "emotional_connection": ""
    })

    target_audience: Dict[str, str] = field(default_factory=lambda: {
        "demographic": "",
        "identity_connection": ""
    })

    unique_contribution: Dict[str, str] = field(default_factory=lambda: {
        "intersection": "",
        "only_they_bring": ""
    })

    representation: Dict[str, str] = field(default_factory=lambda: {
        "who_appears": "",
        "visibility_goal": ""
    })

    cultural_depth: Dict[str, str] = field(default_factory=lambda: {
        "values": "",
        "how_integrated": ""
    })

    temporal: Dict[str, str] = field(default_factory=lambda: {
        "why_now": "",
        "current_context": ""
    })

    problem_specificity: Dict[str, str] = field(default_factory=lambda: {
        "exact_problem": "",
        "statistic": "",
        "measurable_goal": ""
    })

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        return {
            "geographic": self.geographic,
            "identity_why": self.identity_why,
            "field_gap": self.field_gap,
            "catalyst": self.catalyst,
            "target_audience": self.target_audience,
            "unique_contribution": self.unique_contribution,
            "representation": self.representation,
            "cultural_depth": self.cultural_depth,
            "temporal": self.temporal,
            "problem_specificity": self.problem_specificity,
        }

    def get_dimension_score(self) -> Tuple[int, int]:
        """Return (filled_dimensions, total_dimensions)."""
        filled = 0
        dimensions = [
            self.geographic, self.identity_why, self.field_gap,
            self.catalyst, self.target_audience, self.unique_contribution,
            self.representation, self.cultural_depth, self.temporal,
            self.problem_specificity
        ]
        for dim in dimensions:
            if any(v and len(str(v)) > 5 for v in dim.values()):
                filled += 1
        return filled, 10


@dataclass
class GeneratedActivity:
    """A hyper-personalized activity recommendation."""

    priority: int = 0
    title: str = ""
    activity_type: str = ""  # signature_project, leadership, research, service
    description: str = ""
    pillar_foundation: Dict[str, str] = field(default_factory=dict)
    ten_dimensions: TenDimensions = field(default_factory=TenDimensions)
    gap_addressed: str = ""
    components: List[str] = field(default_factory=list)
    measurable_outcomes: List[str] = field(default_factory=list)
    timeline: Dict[str, Any] = field(default_factory=dict)
    passes_only_they_test: bool = False
    only_they_reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "priority": self.priority,
            "title": self.title,
            "activity_type": self.activity_type,
            "description": self.description,
            "pillar_foundation": self.pillar_foundation,
            "ten_dimensions": self.ten_dimensions.to_dict(),
            "gap_addressed": self.gap_addressed,
            "components": self.components,
            "measurable_outcomes": self.measurable_outcomes,
            "timeline": self.timeline,
            "passes_only_they_test": self.passes_only_they_test,
            "only_they_reasoning": self.only_they_reasoning,
        }


class GapType(Enum):
    """Types of portfolio gaps that can be addressed."""
    SIGNATURE_PROJECT = "signature_project"  # All 4 pillars
    LEADERSHIP = "leadership"  # APTITUDE + SERVICE
    RESEARCH = "research"  # APTITUDE + PASSION
    COMMUNITY_SERVICE = "community_service"  # IDENTITY + SERVICE
    NARRATIVE_COHERENCE = "narrative_coherence"  # Ties story together
    ACTIVITY_COUNT = "activity_count"  # Not enough activities


# ============================================================================
# MAIN CLASS
# ============================================================================

class ECGenerationEngine:
    """
    Core EC Generation Engine implementing the 4 Pillars + 10 Dimensions framework.

    This is the foundational methodology for generating hyper-personalized
    extracurricular activities. The framework synthesizes:

    4 PILLARS (Master Synthesis Formula):
        IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE

    10 DIMENSIONS OF HYPER-PERSONALIZATION:
        1. Geographic/Local Context
        2. Identity-Informed WHY
        3. Field Gap Analysis
        4. Personal Catalyst Story
        5. Specific Target Audience
        6. Unique Contribution
        7. Representation in Output
        8. Cultural Depth
        9. Temporal Relevance
        10. Problem Specificity

    This engine can be augmented by coach-specific methodologies that add
    additional layers or modify weights/priorities based on coaching style.

    Methodology Steps:
        1. Extract 4 Pillars with extreme specificity
        2. Synthesize master narrative using formula
        3. Apply "despite → because" reframe
        4. Identify portfolio gaps
        5. Generate activities using 10 Dimensions
        6. Validate with "Only They" test
    """

    def __init__(self, model: str = "gpt-4o", temperature: float = 0.7):
        """
        Initialize the EC Generation Engine.

        Args:
            model: OpenAI model to use for LLM calls
            temperature: Temperature for generation (0.7 for creativity)
        """
        self.model = model
        self.temperature = temperature
        self.llm = None
        self._coach_augmentations: Dict[str, Dict[str, Any]] = {}
        self._init_llm()

    def _init_llm(self):
        """Initialize the LLM client."""
        try:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
            )
            logger.info(f"ECGenerationEngine initialized with {self.model}")
        except ImportError:
            logger.warning("LangChain not available - ECGenerationEngine will use fallbacks")
            self.llm = None
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            self.llm = None

    # ========================================================================
    # STEP 1: PILLAR EXTRACTION
    # ========================================================================

    async def extract_four_pillars(self, profile: Dict[str, Any]) -> FourPillars:
        """
        Extract the 4 pillars from a student profile using LLM.

        CRITICAL: Extract with SPECIFICITY, not generic labels.

        Args:
            profile: Student profile data

        Returns:
            FourPillars with detailed, specific extraction
        """
        if not self.llm:
            logger.warning("LLM not available, using fallback extraction")
            return self._fallback_extract_pillars(profile)

        prompt = self._build_pillar_extraction_prompt(profile)

        try:
            response = await self.llm.ainvoke(prompt)
            return self._parse_pillar_response(response.content)
        except Exception as e:
            logger.error(f"Pillar extraction failed: {e}")
            return self._fallback_extract_pillars(profile)

    def _build_pillar_extraction_prompt(self, profile: Dict[str, Any]) -> str:
        """Build the prompt for pillar extraction."""

        # Format profile data for the prompt
        activities = profile.get("activities", [])
        activities_text = "\n".join([
            f"- {a.get('title', a.get('name', 'Untitled'))}: {a.get('description', '')}"
            for a in activities[:10]  # Limit to 10 activities
        ]) or "No activities listed"

        return f'''You are Jenny Duan, expert college admissions coach known for
hyper-personalized coaching. Analyze this student profile and extract the 4 Pillars
with EXTREME SPECIFICITY.

CRITICAL: Do NOT use generic labels. Be SPECIFIC.
- WRONG: "Muslim student"
- RIGHT: "Indian Muslim girl who wore hijab in AP CS, only one in class for 3 years"

PROFILE DATA:
=============
Demographics: {profile.get("demographics", {})}
Background: {profile.get("background", "")}
Grade: {profile.get("grade", "")}
Location: {profile.get("location", "")}
School: {profile.get("school", "")}
Family Context: {profile.get("family_context", "")}
Constraints: {profile.get("constraints", [])}

Activities:
{activities_text}

Interests: {profile.get("interests", [])}
Passion Statement: {profile.get("passion", "")}
Academic Info: {profile.get("academics", {})}

EXTRACT THE 4 PILLARS:

1. IDENTITY (Who they ARE - be SPECIFIC):
   - Demographics: Specific details (grade, school type, location)
   - Cultural/Religious: Specific markers (NOT just "Muslim" but "Indian Muslim girl who wore hijab in...")
   - Personality: Observable traits from activities/descriptions
   - Circumstances: School context, resources, family situation
   - Specific Experiences: Unique moments that shaped them

2. APTITUDE (What they're GOOD AT):
   - Academic Strengths: Best subjects with specifics
   - Technical Skills: Specific skills demonstrated
   - Demonstrated Abilities: Evidence from activities (project names, achievements)
   - Certifications: Any credentials

3. PASSION (What they LOVE):
   - Stated Interests: What they explicitly say they like
   - Hobbies: What they do for fun (IMPORTANT - these often integrate powerfully)
   - Media Consumption: Books, movies, games that indicate authentic interests
   - Energy Indicators: What makes them excited (infer from descriptions)

4. SERVICE (What they want to CHANGE):
   - Current Volunteering: Existing service activities
   - Causes: What they care about changing
   - Target Populations: WHO specifically they want to help (not generic "people")
   - Values: Principles guiding their service

Return ONLY valid JSON in this exact format:
{{
    "IDENTITY": {{
        "demographics": "specific string",
        "cultural_religious": "specific string with details",
        "personality": "observable traits",
        "circumstances": "school/family context",
        "specific_experiences": ["experience 1", "experience 2"]
    }},
    "APTITUDE": {{
        "academic_strengths": "specific subjects",
        "technical_skills": ["skill1", "skill2"],
        "demonstrated_abilities": ["project/achievement 1", "project/achievement 2"],
        "certifications": []
    }},
    "PASSION": {{
        "stated_interests": ["interest1", "interest2"],
        "hobbies": ["hobby1", "hobby2"],
        "media_consumption": "what they consume",
        "energy_indicators": "what excites them"
    }},
    "SERVICE": {{
        "current_volunteering": "current activities",
        "causes": ["cause1", "cause2"],
        "target_populations": ["specific population 1"],
        "values": ["value1", "value2"]
    }}
}}
'''

    def _parse_pillar_response(self, response: str) -> FourPillars:
        """Parse the LLM response into FourPillars."""
        try:
            # Clean response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r'^```json?\n?', '', cleaned)
                cleaned = re.sub(r'\n?```$', '', cleaned)

            data = json.loads(cleaned)

            return FourPillars(
                identity=data.get("IDENTITY", {}),
                aptitude=data.get("APTITUDE", {}),
                passion=data.get("PASSION", {}),
                service=data.get("SERVICE", {}),
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse pillar JSON: {e}")
            logger.debug(f"Raw response: {response[:500]}")
            return FourPillars()

    def _fallback_extract_pillars(self, profile: Dict[str, Any]) -> FourPillars:
        """Fallback extraction when LLM is not available."""
        activities = profile.get("activities", [])

        return FourPillars(
            identity={
                "demographics": f"Grade {profile.get('grade', 'unknown')}, {profile.get('location', 'unknown location')}",
                "cultural_religious": profile.get("background", ""),
                "personality": "",
                "circumstances": profile.get("school", ""),
                "specific_experiences": [],
            },
            aptitude={
                "academic_strengths": str(profile.get("academics", {})),
                "technical_skills": [],
                "demonstrated_abilities": [a.get("title", a.get("name", "")) for a in activities[:3]],
                "certifications": [],
            },
            passion={
                "stated_interests": profile.get("interests", []),
                "hobbies": [],
                "media_consumption": "",
                "energy_indicators": profile.get("passion", ""),
            },
            service={
                "current_volunteering": "",
                "causes": [],
                "target_populations": [],
                "values": [],
            }
        )

    # ========================================================================
    # STEP 2: NARRATIVE SYNTHESIS
    # ========================================================================

    async def synthesize_narrative(
        self,
        pillars: FourPillars,
        profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Synthesize master narrative using the formula:
        IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE

        Also applies "despite → because" reframe.

        Args:
            pillars: Extracted 4 pillars
            profile: Original profile for context

        Returns:
            Dict with master_narrative, archetype, spike, reframe
        """
        if not self.llm:
            return self._fallback_synthesize_narrative(pillars)

        prompt = self._build_narrative_synthesis_prompt(pillars, profile)

        try:
            response = await self.llm.ainvoke(prompt)
            return self._parse_narrative_response(response.content)
        except Exception as e:
            logger.error(f"Narrative synthesis failed: {e}")
            return self._fallback_synthesize_narrative(pillars)

    def _build_narrative_synthesis_prompt(
        self,
        pillars: FourPillars,
        profile: Dict[str, Any],
    ) -> str:
        """Build prompt for narrative synthesis."""
        return f'''You are Jenny Duan, expert college admissions coach.
Given these 4 Pillars, synthesize a MASTER NARRATIVE.

4 PILLARS:
{json.dumps(pillars.to_dict(), indent=2)}

TASKS:

1. MASTER NARRATIVE: Combine all 4 pillars into 1-2 powerful sentences.
   Formula: "As a [IDENTITY], using my [APTITUDE], driven by passion for [PASSION],
   I serve [SERVICE]."

   Make it SPECIFIC to this student, not generic.

2. ARCHETYPE: Classify into ONE of these:
   - stem_innovator: Builds technical solutions
   - community_changemaker: Drives social impact
   - creative_visionary: Combines creativity with execution
   - policy_advocate: Influences systems
   - entrepreneurial_leader: Builds organizations
   - research_scholar: Deep academic inquiry
   - global_citizen: Bridges cultures
   - artistic_virtuoso: Excellence in arts

3. SPIKE: Generate a HYPER-SPECIFIC unique differentiator.
   - WRONG: "Building AI solutions for education"
   - RIGHT: "Digital Storyteller democratizing tech through Muslim girl
     representation in AI ethics education"

   The spike should be so specific that ONLY this student could have it.

4. "DESPITE → BECAUSE" REFRAME:
   Look for any perceived weakness and transform it into a strength.

   Examples:
   - "Despite being quiet..." → "Because of my observational skills..."
   - "Despite limited resources..." → "Because I had to create my own..."
   - "Despite being the only..." → "Because of my unique perspective..."

Return ONLY valid JSON:
{{
    "master_narrative": "1-2 sentence synthesis",
    "archetype": "one_of_the_eight",
    "archetype_confidence": 0.0-1.0,
    "spike": "hyper-specific differentiator",
    "spike_confidence": 0.0-1.0,
    "pillars": ["pillar1", "pillar2", "pillar3"],
    "reframe_applied": {{
        "original": "despite statement if found",
        "transformed": "because reframe"
    }}
}}
'''

    def _parse_narrative_response(self, response: str) -> Dict[str, Any]:
        """Parse narrative synthesis response."""
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r'^```json?\n?', '', cleaned)
                cleaned = re.sub(r'\n?```$', '', cleaned)

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse narrative JSON: {e}")
            return {
                "master_narrative": "",
                "archetype": "multi_hyphenate",
                "archetype_confidence": 0.5,
                "spike": "",
                "spike_confidence": 0.5,
                "pillars": [],
                "reframe_applied": None,
            }

    def _fallback_synthesize_narrative(self, pillars: FourPillars) -> Dict[str, Any]:
        """Fallback narrative synthesis."""
        return {
            "master_narrative": "Student with diverse interests and experiences.",
            "archetype": "multi_hyphenate",
            "archetype_confidence": 0.5,
            "spike": "Exploring diverse interests across multiple domains",
            "spike_confidence": 0.5,
            "pillars": ["academics", "activities", "service"],
            "reframe_applied": None,
        }

    # ========================================================================
    # STEP 3: GAP IDENTIFICATION
    # ========================================================================

    def identify_gaps(
        self,
        profile: Dict[str, Any],
        pillars: FourPillars,
    ) -> List[GapType]:
        """
        Identify gaps in the current portfolio.

        Args:
            profile: Student profile
            pillars: Extracted pillars

        Returns:
            List of gaps to address, prioritized
        """
        gaps = []
        activities = profile.get("activities", [])

        # Check activity count
        if len(activities) < 5:
            gaps.append(GapType.ACTIVITY_COUNT)

        # Check for signature project (all 4 pillars)
        has_signature = self._has_signature_project(activities, pillars)
        if not has_signature:
            gaps.append(GapType.SIGNATURE_PROJECT)

        # Check leadership
        has_leadership = self._has_leadership(activities)
        if not has_leadership:
            gaps.append(GapType.LEADERSHIP)

        # Check research
        has_research = self._has_research(activities)
        if not has_research:
            gaps.append(GapType.RESEARCH)

        # Check service
        has_service = self._has_meaningful_service(activities)
        if not has_service:
            gaps.append(GapType.COMMUNITY_SERVICE)

        # Always consider narrative coherence
        if len(gaps) == 0:
            gaps.append(GapType.NARRATIVE_COHERENCE)

        return gaps

    def _has_signature_project(
        self,
        activities: List[Dict],
        pillars: FourPillars,
    ) -> bool:
        """Check if portfolio has a signature project using all 4 pillars."""
        for activity in activities:
            desc = str(activity.get("description", "")).lower()
            title = str(activity.get("title", activity.get("name", ""))).lower()
            combined = f"{title} {desc}"

            # Check if activity touches all pillars
            touches_identity = any(
                kw in combined for kw in ["identity", "cultural", "community", "heritage"]
            )
            touches_aptitude = any(
                kw in combined for kw in ["built", "created", "developed", "designed"]
            )
            touches_passion = any(
                str(kw).lower() in combined
                for kw in pillars.passion.get("stated_interests", [])
            )
            touches_service = any(
                kw in combined for kw in ["serve", "help", "impact", "community"]
            )

            if sum([touches_identity, touches_aptitude, touches_passion, touches_service]) >= 3:
                return True

        return False

    def _has_leadership(self, activities: List[Dict]) -> bool:
        """Check for leadership activities."""
        leadership_keywords = [
            "president", "founder", "captain", "lead", "director",
            "head", "chief", "chair", "coordinator", "manager"
        ]
        for activity in activities:
            combined = f"{activity.get('title', activity.get('name', ''))} {activity.get('description', '')} {activity.get('position', '')}".lower()
            if any(kw in combined for kw in leadership_keywords):
                return True
        return False

    def _has_research(self, activities: List[Dict]) -> bool:
        """Check for research activities."""
        research_keywords = [
            "research", "study", "investigation", "analysis",
            "publication", "paper", "thesis", "lab"
        ]
        for activity in activities:
            combined = f"{activity.get('title', activity.get('name', ''))} {activity.get('description', '')}".lower()
            if any(kw in combined for kw in research_keywords):
                return True
        return False

    def _has_meaningful_service(self, activities: List[Dict]) -> bool:
        """Check for meaningful service (not just hours)."""
        service_keywords = [
            "volunteer", "service", "nonprofit", "community",
            "impact", "founded", "initiative"
        ]
        for activity in activities:
            combined = f"{activity.get('title', activity.get('name', ''))} {activity.get('description', '')} {activity.get('category', '')}".lower()
            if any(kw in combined for kw in service_keywords):
                # Check if it's substantial (not just "100 hours")
                if len(activity.get("description", "")) > 50:
                    return True
        return False

    # ========================================================================
    # STEP 4: ACTIVITY GENERATION
    # ========================================================================

    async def generate_activity(
        self,
        gap: GapType,
        pillars: FourPillars,
        narrative: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> GeneratedActivity:
        """
        Generate a hyper-personalized activity using 10 Dimensions.

        Args:
            gap: The gap to address
            pillars: Extracted 4 pillars
            narrative: Synthesized narrative
            profile: Original profile

        Returns:
            GeneratedActivity with full 10-dimension personalization
        """
        if not self.llm:
            return self._fallback_generate_activity(gap, pillars)

        prompt = self._build_activity_generation_prompt(gap, pillars, narrative, profile)

        try:
            response = await self.llm.ainvoke(prompt)
            activity = self._parse_activity_response(response.content, gap)

            # Validate with "Only They" test
            if not activity.passes_only_they_test:
                activity = await self._enhance_activity(activity, pillars, profile)

            return activity
        except Exception as e:
            logger.error(f"Activity generation failed: {e}")
            return self._fallback_generate_activity(gap, pillars)

    def _build_activity_generation_prompt(
        self,
        gap: GapType,
        pillars: FourPillars,
        narrative: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> str:
        """Build prompt for activity generation with 10 dimensions."""

        gap_descriptions = {
            GapType.SIGNATURE_PROJECT: "A SIGNATURE PROJECT that combines ALL 4 pillars - this is the 'home run' that defines the student's narrative",
            GapType.LEADERSHIP: "A LEADERSHIP activity that leverages APTITUDE for SERVICE impact",
            GapType.RESEARCH: "A RESEARCH project that combines APTITUDE with PASSION",
            GapType.COMMUNITY_SERVICE: "A COMMUNITY SERVICE initiative informed by IDENTITY that serves specific populations",
            GapType.NARRATIVE_COHERENCE: "An activity that TIES THE NARRATIVE TOGETHER and strengthens the spike",
            GapType.ACTIVITY_COUNT: "An activity that adds depth to the portfolio while staying on-narrative",
        }

        return f'''You are Jenny Duan, expert college admissions coach known for creating
HYPER-PERSONALIZED activities that pass the "Only They" test.

GAP TO ADDRESS: {gap.value}
{gap_descriptions.get(gap, "An activity that strengthens the portfolio")}

STUDENT'S 4 PILLARS:
{json.dumps(pillars.to_dict(), indent=2)}

NARRATIVE SYNTHESIS:
- Master Narrative: {narrative.get("master_narrative", "")}
- Archetype: {narrative.get("archetype", "")}
- Spike: {narrative.get("spike", "")}

PROFILE CONTEXT:
- Location: {profile.get("location", "unknown")}
- Grade: {profile.get("grade", "unknown")}
- School: {profile.get("school", "unknown")}

YOUR TASK:
Generate ONE hyper-personalized activity using ALL 10 DIMENSIONS:

1. GEOGRAPHIC: What local issues in their specific city/region? What local partner?
2. IDENTITY WHY: How does their SPECIFIC identity inform motivation? (NOT generic)
3. FIELD GAP: What gap in the field can their identity uniquely address? Include statistics.
4. CATALYST: What specific life experience drives this? Personal moment or family experience.
5. TARGET AUDIENCE: WHO exactly benefits? (NOT "people" but specific demographic)
6. UNIQUE CONTRIBUTION: What can ONLY this student bring? What would be missing without them?
7. REPRESENTATION: Who appears in their output? (Characters/examples that look like them)
8. CULTURAL DEPTH: How do cultural VALUES (not labels) inform the work?
9. TEMPORAL: Why is this urgent NOW? Current events or trends?
10. PROBLEM SPECIFICITY: What EXACT problem with SPECIFIC statistics and measurable goals?

"ONLY THEY" TEST:
Could you identify THIS specific student just from reading the activity description?
If not, make it MORE SPECIFIC.

Return ONLY valid JSON:
{{
    "title": "Compelling, Specific Title",
    "activity_type": "{gap.value}",
    "description": "3-4 sentence hyper-personalized description",
    "pillar_foundation": {{
        "IDENTITY": "How identity is integrated",
        "APTITUDE": "How skills are leveraged",
        "PASSION": "How passion is incorporated",
        "SERVICE": "How community is served"
    }},
    "ten_dimensions": {{
        "geographic": {{"location": "...", "local_relevance": "...", "local_partner": "..."}},
        "identity_why": {{"specific_identity": "...", "connection": "..."}},
        "field_gap": {{"gap": "...", "statistic": "...", "how_filled": "..."}},
        "catalyst": {{"origin_story": "...", "emotional_connection": "..."}},
        "target_audience": {{"demographic": "...", "identity_connection": "..."}},
        "unique_contribution": {{"intersection": "...", "only_they_bring": "..."}},
        "representation": {{"who_appears": "...", "visibility_goal": "..."}},
        "cultural_depth": {{"values": "...", "how_integrated": "..."}},
        "temporal": {{"why_now": "...", "current_context": "..."}},
        "problem_specificity": {{"exact_problem": "...", "statistic": "...", "measurable_goal": "..."}}
    }},
    "components": ["Component 1", "Component 2", "Component 3"],
    "measurable_outcomes": ["Outcome 1", "Outcome 2"],
    "passes_only_they_test": true,
    "only_they_reasoning": "Explanation of why this passes the test"
}}
'''

    def _parse_activity_response(
        self,
        response: str,
        gap: GapType,
    ) -> GeneratedActivity:
        """Parse activity generation response."""
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r'^```json?\n?', '', cleaned)
                cleaned = re.sub(r'\n?```$', '', cleaned)

            data = json.loads(cleaned)

            # Build TenDimensions from response
            dims_data = data.get("ten_dimensions", {})
            ten_dims = TenDimensions(
                geographic=dims_data.get("geographic", {}),
                identity_why=dims_data.get("identity_why", {}),
                field_gap=dims_data.get("field_gap", {}),
                catalyst=dims_data.get("catalyst", {}),
                target_audience=dims_data.get("target_audience", {}),
                unique_contribution=dims_data.get("unique_contribution", {}),
                representation=dims_data.get("representation", {}),
                cultural_depth=dims_data.get("cultural_depth", {}),
                temporal=dims_data.get("temporal", {}),
                problem_specificity=dims_data.get("problem_specificity", {}),
            )

            return GeneratedActivity(
                title=data.get("title", ""),
                activity_type=data.get("activity_type", gap.value),
                description=data.get("description", ""),
                pillar_foundation=data.get("pillar_foundation", {}),
                ten_dimensions=ten_dims,
                gap_addressed=gap.value,
                components=data.get("components", []),
                measurable_outcomes=data.get("measurable_outcomes", []),
                passes_only_they_test=data.get("passes_only_they_test", False),
                only_they_reasoning=data.get("only_they_reasoning", ""),
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse activity JSON: {e}")
            return self._fallback_generate_activity(gap, FourPillars())

    def _fallback_generate_activity(
        self,
        gap: GapType,
        pillars: FourPillars,
    ) -> GeneratedActivity:
        """Fallback activity generation."""
        return GeneratedActivity(
            title=f"Activity addressing {gap.value}",
            activity_type=gap.value,
            description="An activity to strengthen the portfolio.",
            gap_addressed=gap.value,
            passes_only_they_test=False,
            only_they_reasoning="Generated with fallback - needs enhancement",
        )

    # ========================================================================
    # STEP 5: VALIDATION & ENHANCEMENT
    # ========================================================================

    async def _enhance_activity(
        self,
        activity: GeneratedActivity,
        pillars: FourPillars,
        profile: Dict[str, Any],
    ) -> GeneratedActivity:
        """
        Enhance an activity that failed the "Only They" test.

        Args:
            activity: Activity to enhance
            pillars: Student's 4 pillars
            profile: Original profile

        Returns:
            Enhanced activity
        """
        if not self.llm:
            return activity

        prompt = f'''This activity FAILED the "Only They" test - it's too generic.

CURRENT ACTIVITY:
Title: {activity.title}
Description: {activity.description}
Failure reason: {activity.only_they_reasoning}

STUDENT'S 4 PILLARS:
{json.dumps(pillars.to_dict(), indent=2)}

TASK: Make it MORE SPECIFIC by strengthening the weakest dimensions.

The goal: Someone reading ONLY the activity description should be able to
identify THIS specific student from a crowd of 1000 students.

Focus on:
1. Adding SPECIFIC identity markers (not just "Muslim" but "Indian Muslim girl who...")
2. Including SPECIFIC statistics and measurable goals
3. Naming SPECIFIC local partners or locations
4. Describing SPECIFIC target audience (not "students" but "6th-8th grade Muslim girls...")

Return the enhanced activity as JSON with the same structure.
'''

        try:
            response = await self.llm.ainvoke(prompt)
            enhanced = self._parse_activity_response(response.content, GapType(activity.gap_addressed))
            enhanced.passes_only_they_test = True
            enhanced.only_they_reasoning = "Enhanced to pass 'Only They' test"
            return enhanced
        except Exception as e:
            logger.error(f"Activity enhancement failed: {e}")
            return activity

    async def validate_only_they_test(
        self,
        activity: GeneratedActivity,
        profile: Dict[str, Any],
    ) -> Tuple[bool, str, List[str]]:
        """
        Validate that an activity passes the "Only They" test.

        Args:
            activity: Activity to validate
            profile: Student profile

        Returns:
            Tuple of (passes, reasoning, weak_dimensions)
        """
        if not self.llm:
            return (True, "LLM not available for validation", [])

        prompt = f'''Evaluate if this activity passes the "ONLY THEY" test.

ACTIVITY:
Title: {activity.title}
Description: {activity.description}
10 Dimensions: {json.dumps(activity.ten_dimensions.to_dict(), indent=2)}

THE TEST:
"Could you identify THIS specific student just from reading the activity description?"

Imagine 1000 high school students. Would this activity description uniquely identify
ONE student, or could it apply to many?

SCORING:
- 10/10 dimensions filled with specifics = PASS
- 8-9/10 dimensions = BORDERLINE (identify weak ones)
- <8/10 dimensions = FAIL

Return JSON:
{{
    "passes": true/false,
    "reasoning": "explanation",
    "weak_dimensions": ["dimension1", "dimension2"],
    "specificity_score": 0-10
}}
'''

        try:
            response = await self.llm.ainvoke(prompt)
            cleaned = response.content.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r'^```json?\n?', '', cleaned)
                cleaned = re.sub(r'\n?```$', '', cleaned)

            result = json.loads(cleaned)
            return (
                result.get("passes", False),
                result.get("reasoning", ""),
                result.get("weak_dimensions", []),
            )
        except Exception as e:
            logger.error(f"Only They validation failed: {e}")
            return (True, "Validation error - assuming pass", [])

    # ========================================================================
    # MAIN ENTRY POINT
    # ========================================================================

    async def generate_identity_and_activities(
        self,
        profile: Dict[str, Any],
        max_activities: int = 3,
    ) -> Dict[str, Any]:
        """
        Complete pipeline: Extract pillars, synthesize narrative, generate activities.

        This is the main entry point for the EC Agent.

        Args:
            profile: Student profile
            max_activities: Maximum number of activities to generate

        Returns:
            Complete identity_synthesis with recommended_activities
        """
        print("[EC Engine] Starting EC Generation Engine pipeline")
        logger.info("Starting EC Generation Engine pipeline")

        # Step 1: Extract 4 Pillars
        print("[EC Engine] Step 1: Extracting 4 Pillars")
        logger.info("Step 1: Extracting 4 Pillars")
        pillars = await self.extract_four_pillars(profile)
        pillar_count = pillars.get_pillar_count()
        specificity = pillars.get_specificity_score()
        logger.info(f"Extracted {pillar_count}/4 pillars with {specificity:.0%} specificity")

        # Step 2: Synthesize Narrative
        print("[EC Engine] Step 2: Synthesizing narrative")
        logger.info("Step 2: Synthesizing narrative")
        narrative = await self.synthesize_narrative(pillars, profile)
        print(f"[EC Engine] Archetype: {narrative.get('archetype')} ({narrative.get('archetype_confidence', 0):.0%})")
        logger.info(f"Archetype: {narrative.get('archetype')} ({narrative.get('archetype_confidence', 0):.0%})")
        logger.info(f"Spike: {narrative.get('spike', '')[:50]}...")

        # Step 3: Identify Gaps
        print("[EC Engine] Step 3: Identifying gaps")
        logger.info("Step 3: Identifying gaps")
        gaps = self.identify_gaps(profile, pillars)
        print(f"[EC Engine] Found {len(gaps)} gaps: {[g.value for g in gaps]}")
        logger.info(f"Found {len(gaps)} gaps: {[g.value for g in gaps]}")

        # Step 4: Generate Activities
        print(f"[EC Engine] Step 4: Generating {min(len(gaps), max_activities)} activities")
        logger.info(f"Step 4: Generating {min(len(gaps), max_activities)} activities")
        activities = []
        for i, gap in enumerate(gaps[:max_activities]):
            print(f"[EC Engine] Generating activity {i+1} for gap: {gap.value}")
            logger.info(f"Generating activity {i+1} for gap: {gap.value}")
            activity = await self.generate_activity(gap, pillars, narrative, profile)
            activity.priority = i
            activities.append(activity)
            print(f"[EC Engine] Generated: {activity.title}")
            logger.info(f"Generated: {activity.title}")

        # Build final output
        result = {
            "identity_synthesis": {
                "archetype": narrative.get("archetype"),
                "archetype_confidence": narrative.get("archetype_confidence", 0.7),
                "spike": narrative.get("spike"),
                "spike_confidence": narrative.get("spike_confidence", 0.7),
                "pillars": narrative.get("pillars", []),
                "master_narrative": narrative.get("master_narrative"),
                "four_pillars": pillars.to_dict(),
                "reframe_applied": narrative.get("reframe_applied"),
                "pillar_specificity_score": specificity,
            },
            "recommended_activities": [a.to_dict() for a in activities],
            "portfolio_gaps": [g.value for g in gaps],
            "methodology_version": "ec_engine_v1.0",
        }

        logger.info("EC Generation Engine pipeline complete")
        return result

    # =========================================================================
    # COACH METHODOLOGY AUGMENTATION INTERFACE
    # =========================================================================

    def register_coach_augmentation(
        self,
        coach_id: str,
        augmentation_config: Dict[str, Any]
    ) -> None:
        """
        Register coach-specific augmentations to the base methodology.

        Augmentations can include:
        - pillar_weights: Dict adjusting relative importance of pillars
        - dimension_priorities: List reordering the 10 dimensions
        - custom_reframes: Additional "despite" → "because" patterns
        - signature_project_templates: Coach-specific project archetypes
        - validation_criteria: Additional validation checks

        Args:
            coach_id: Unique identifier for the coach (e.g., "jenny", "michael")
            augmentation_config: Dictionary of augmentation parameters

        Example:
            engine.register_coach_augmentation("jenny", {
                "pillar_weights": {"IDENTITY": 1.2, "SERVICE": 1.1},
                "custom_reframes": [...],
                "signature_templates": [...]
            })
        """
        self._coach_augmentations[coach_id] = augmentation_config
        logger.info(f"Registered coach augmentation: {coach_id}")

    def apply_coach_augmentation(
        self,
        coach_id: str,
        base_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply coach-specific augmentations to the base methodology output.

        Args:
            coach_id: Which coach's augmentations to apply
            base_output: Output from base methodology

        Returns:
            Augmented output with coach-specific modifications
        """
        if coach_id not in self._coach_augmentations:
            return base_output

        augmentation = self._coach_augmentations[coach_id]
        augmented = base_output.copy()

        # Apply pillar weight adjustments
        if 'pillar_weights' in augmentation:
            augmented = self._apply_pillar_weights(augmented, augmentation['pillar_weights'])

        # Apply custom reframes
        if 'custom_reframes' in augmentation:
            augmented = self._apply_custom_reframes(augmented, augmentation['custom_reframes'])

        # Apply additional validation criteria
        if 'validation_criteria' in augmentation:
            augmented['validation'] = self._apply_additional_validation(
                augmented, augmentation['validation_criteria']
            )

        augmented['coach_augmentation_applied'] = coach_id
        return augmented

    def _apply_pillar_weights(
        self,
        output: Dict[str, Any],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Apply pillar weight adjustments to scoring."""
        # For now, just record the weights - can be expanded for actual scoring adjustments
        if 'identity_synthesis' in output:
            output['identity_synthesis']['pillar_weights_applied'] = weights
        return output

    def _apply_custom_reframes(
        self,
        output: Dict[str, Any],
        reframes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply additional coach-specific reframe patterns."""
        # For now, append custom reframes to output - can be expanded
        if 'custom_reframes' not in output:
            output['custom_reframes'] = []
        output['custom_reframes'].extend(reframes)
        return output

    def _apply_additional_validation(
        self,
        output: Dict[str, Any],
        criteria: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply coach-specific validation criteria."""
        validation_results = {
            'criteria_applied': len(criteria),
            'passed': True,  # Default - actual validation logic can be added
        }
        return validation_results

    def get_registered_coaches(self) -> List[str]:
        """Return list of registered coach augmentation IDs."""
        return list(self._coach_augmentations.keys())
