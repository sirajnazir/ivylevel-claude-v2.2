"""
IvyQuest v10.0 Assessment Agent
===============================
Synthesizes identity & computes readiness.

Primitives:
- ACP-001: Hidden Probability Matrix (NEVER shown to user)
- ACP-002: Identity Synthesis Framework (Narrative DNA)

Autonomy: HIGH (synthesis with context), handoff if confidence <70%
"""

from typing import Dict, Any, Optional, List
from .base import BaseAgent
from config import AutonomyLevel, settings
from tools.cri import compute_cri, compute_performance
from tools.database import get_profile, update_profile, get_archetypes

import structlog

logger = structlog.get_logger()


class AssessmentAgent(BaseAgent):
    """
    Assessment Agent: Synthesizes identity & computes readiness.

    Key Responsibilities:
    1. Narrative DNA Synthesis - Extract and synthesize identity themes
    2. Archetype Detection - Match student to coaching archetype
    3. CRI Computation - Calculate Context Relativity Index
    4. Hidden Probability Matrix - Calculate admission probabilities (internal)
    """

    def __init__(self):
        super().__init__(
            name="Assessment",
            autonomy_level=AutonomyLevel.HIGH
        )

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """Main processing entry point."""
        return await self.enhance(profile_id, kwargs.get("data"))

    async def enhance(self, profile_id: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Run full assessment enhancement.

        Steps:
        1. Synthesize Narrative DNA
        2. Detect Archetype
        3. Compute CRI
        4. Calculate Hidden Probabilities
        5. Identify Hidden Target
        """
        self._log_start("enhance_assessment", profile_id=profile_id)

        profile = await self._get_profile(profile_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}

        # Step 1: Synthesize Narrative DNA
        narrative = await self.synthesize_narrative_dna(profile)

        # Step 2: Detect Archetype
        archetype = await self.detect_archetype(profile)

        # Step 3: Compute CRI
        cri = await compute_cri(profile)

        # Step 4: Calculate Hidden Probabilities
        probabilities = await self.calculate_hidden_probabilities(profile, cri)

        # Step 5: Identify Hidden Target
        hidden_target = self._identify_hidden_target(probabilities)

        # Update profile
        updates = {
            "narrative_dna": narrative.get("dna"),
            "narrative_themes": narrative.get("themes", []),
            "narrative_confidence": narrative.get("confidence", 0),
            "archetype_id": archetype.get("id"),
            "archetype_confidence": archetype.get("confidence", 0),
            "archetype_rationale": archetype.get("rationale"),
            "cri": cri,
            "hidden_probabilities": probabilities,
            "hidden_target": hidden_target,
        }

        await self._update_profile(profile_id, updates)

        # Version state
        await self._version_state(profile_id, "assessment_enhanced", updates)

        # Publish event
        await self._publish_event("ASSESSMENT_COMPLETED", {
            "profileId": profile_id,
            "narrativeDna": narrative.get("dna"),
            "cri": cri,
            "archetypeId": archetype.get("id"),
        })

        self._log_complete("enhance_assessment", profile_id=profile_id)

        return {
            "success": True,
            "narrative_dna": narrative,
            "archetype": archetype,
            "cri": cri,
            "hidden_target": hidden_target,
            "requires_handoff": archetype.get("confidence", 0) < 0.7,
        }

    async def synthesize_narrative_dna(self, profile: Dict) -> Dict:
        """
        ACP-002: Identity Synthesis Framework.

        Synthesize scattered interests into a single narrative DNA sentence.
        """
        # TODO: Implement with LLM
        # For now, return placeholder
        return {
            "dna": "Bridging technology and community impact through innovative solutions",
            "themes": ["technology", "community", "innovation"],
            "confidence": 0.75,
        }

    async def detect_archetype(self, profile: Dict) -> Dict:
        """
        Detect student archetype with confidence and explainable rationale.

        Per v9.1: Must include confidence + rationale fields.
        """
        archetypes = await get_archetypes()

        # TODO: Implement matching logic with LLM
        # For now, return best match based on constraints
        constraints = profile.get("constraints", [])

        if constraints:
            # Default to Constrained Gritty if constraints present
            for arch in archetypes:
                if arch.get("label") == "Constrained Gritty":
                    return {
                        "id": arch["id"],
                        "label": arch["label"],
                        "confidence": 0.8,
                        "rationale": f"Student has {len(constraints)} constraints indicating Constrained Gritty archetype",
                    }

        # Default to Academic Achiever
        for arch in archetypes:
            if arch.get("label") == "Academic Achiever":
                return {
                    "id": arch["id"],
                    "label": arch["label"],
                    "confidence": 0.6,
                    "rationale": "Default archetype based on academic focus",
                }

        return {
            "id": None,
            "label": "Unknown",
            "confidence": 0.3,
            "rationale": "Unable to determine archetype with confidence",
        }

    async def calculate_hidden_probabilities(self, profile: Dict, cri: float) -> Dict:
        """
        ACP-001: Hidden Probability Matrix (NEVER shown to user).

        Calculate admission probabilities for target schools.
        """
        schools = profile.get("target_schools", [])
        probabilities = {}

        # TODO: Implement full probability calculation
        # For now, return placeholder probabilities
        for school in schools[:5]:  # Limit to 5 schools
            school_name = school if isinstance(school, str) else school.get("name", "Unknown")
            base_prob = 0.15  # Default base probability
            adjusted_prob = min(base_prob * cri, 0.95)  # Cap at 95%
            probabilities[school_name] = round(adjusted_prob, 3)

        return probabilities

    def _identify_hidden_target(self, probabilities: Dict) -> Optional[str]:
        """
        Identify school to optimize for (hidden from user).

        Strategy: Target second-best probability school (strategic reach).
        """
        if not probabilities:
            return None

        sorted_schools = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)

        # Return second-best if available, otherwise best
        if len(sorted_schools) >= 2:
            return sorted_schools[1][0]
        return sorted_schools[0][0] if sorted_schools else None
