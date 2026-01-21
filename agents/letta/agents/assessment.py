"""
Assessment Specialist Agent
===========================

DORMANT - Phase 2 Future Implementation

Current: Pass-through only, does nothing

Future Purpose (Phase 2):
- Quarterly reassessment triggered by Execution Agent
- Deep psycho-behavioral pattern analysis
- Passion/interest evolution tracking
- Dynamic Ivy Score recalculation
- Called BY other agents, not for initial onboarding

NOTE: Initial onboarding (Assessment Frames 1-6) is handled by the existing
AssessmentAgent at agents/agents/assessment.py. This Letta agent is for
POST-onboarding reassessment cycles.
"""

from typing import Dict, Any

from ..config import AgentType, AgentStatus


# System prompt for the Assessment Specialist (DORMANT)
ASSESSMENT_SYSTEM_PROMPT = """You are the IvyLevel Assessment Specialist.

## CURRENT STATUS: DORMANT

This agent is currently dormant. All requests should be routed to the existing
assessment system.

If you receive a message, respond with:
"The Assessment Specialist is currently dormant. For initial assessments, please
use the main IvyLevel assessment flow. This agent will be activated in Phase 2
for quarterly reassessments."

## FUTURE PURPOSE (Phase 2)

When activated, this agent will handle:
1. **Quarterly Reassessment** - Periodic re-evaluation of student profile
2. **Pattern Analysis** - Deep psycho-behavioral pattern recognition
3. **Evolution Tracking** - How passions and interests have changed
4. **Score Recalculation** - Updated CRI and Ivy Scores
5. **Agent Coordination** - Triggered by Execution Agent on milestones

## Activation Criteria (Phase 2)

This agent will activate when:
- 90+ days since last assessment
- Major milestone completed (from Execution Agent)
- Significant profile changes detected
- Student explicitly requests reassessment
- Pre-application season check (junior fall, senior summer)

## Tools (Future)

### search_techniques
Domain="assessment" for A1-A12 techniques.

### get_student_profile
Current profile for comparison.

### get_goal_progress
To assess outcome achievement.

### request_approval
For archetype changes or significant score adjustments.
"""


# Assessment Specialist configuration (DORMANT)
ASSESSMENT_AGENT_CONFIG: Dict[str, Any] = {
    "name": "Assessment Specialist",
    "status": "DORMANT",  # Explicitly marked as dormant
    "agent_type": AgentType.ASSESSMENT.value,
    "system_prompt": ASSESSMENT_SYSTEM_PROMPT,
    "model": "gpt-4o",
    "tags": ["specialist", "assessment", "dormant"],
    "tools": [
        # Minimal tools for dormant state
        "core_memory_get",
    ],
    "memory_blocks": [
        "student_profile",
        "coaching_history",
    ],
    # Dormant-specific configuration
    "dormant": True,
    "activation_phase": "Phase 2",
    "activation_conditions": [
        "90+ days since last assessment",
        "Major milestone completed",
        "Significant profile changes",
        "Student request",
        "Pre-application season",
    ],
    "future_tools": [
        "search_techniques",
        "get_student_profile",
        "get_goal_progress",
        "get_recent_interactions",
        "request_approval",
    ],
}


class AssessmentSpecialist:
    """
    Assessment Specialist wrapper for IvyLevel.

    DORMANT - Phase 2 Future Implementation

    This class exists as a placeholder for future Phase 2 implementation.
    Currently, it does nothing except return dormant status messages.

    Future Purpose:
    - Quarterly reassessment cycles
    - Deep pattern analysis
    - Passion/interest evolution tracking
    - Dynamic score recalculation

    The existing AssessmentAgent (agents/agents/assessment.py) handles
    initial onboarding (Assessment Frames 1-6).
    """

    def __init__(self, letta_client=None, agent_id: str = None):
        """
        Initialize the Assessment Specialist wrapper.

        Args:
            letta_client: Letta client instance (unused in dormant state)
            agent_id: The Letta agent ID (unused in dormant state)
        """
        self.client = letta_client
        self.agent_id = agent_id
        self.is_dormant = True

    async def handle_request(self, profile_id: str, request: str) -> Dict[str, Any]:
        """
        Handle any request to this dormant agent.

        Always returns dormant status message.

        Args:
            profile_id: Student profile ID
            request: The request message

        Returns:
            Dormant status response
        """
        return {
            "success": False,
            "dormant": True,
            "message": (
                "The Assessment Specialist is currently dormant. "
                "For initial assessments, please use the main IvyLevel assessment flow "
                "(Assessment Frames 1-6). "
                "This agent will be activated in Phase 2 for quarterly reassessments."
            ),
            "redirect_to": "existing_assessment_agent",
            "profile_id": profile_id,
            "phase": "Phase 2",
        }

    async def check_activation_criteria(self, profile_id: str) -> Dict[str, Any]:
        """
        Check if this agent should be activated (Phase 2 future).

        Currently always returns False.

        Args:
            profile_id: Student profile ID

        Returns:
            Activation status (always False in Phase 1)
        """
        return {
            "should_activate": False,
            "reason": "Phase 2 not yet implemented",
            "current_phase": "Phase 1",
            "activation_criteria": ASSESSMENT_AGENT_CONFIG["activation_conditions"],
        }

    # ==========================================================================
    # Phase 2 Future Methods (Placeholders)
    # ==========================================================================

    async def run_quarterly_reassessment(self, profile_id: str) -> Dict[str, Any]:
        """
        FUTURE: Run a quarterly reassessment cycle.

        Phase 2 Implementation Notes:
        - Compare current profile to last assessment
        - Identify changes in interests/activities
        - Update archetype if significantly changed
        - Recalculate CRI and Ivy Scores
        - Generate reassessment narrative
        """
        return await self.handle_request(profile_id, "quarterly_reassessment")

    async def analyze_evolution(self, profile_id: str) -> Dict[str, Any]:
        """
        FUTURE: Analyze how student has evolved since last assessment.

        Phase 2 Implementation Notes:
        - Track passion/interest evolution
        - Identify new strengths developed
        - Note completed milestones
        - Assess growth trajectory
        """
        return await self.handle_request(profile_id, "analyze_evolution")

    async def recalculate_scores(self, profile_id: str) -> Dict[str, Any]:
        """
        FUTURE: Recalculate assessment scores.

        Phase 2 Implementation Notes:
        - Update CRI (Competitive Readiness Index)
        - Recalculate hidden probabilities
        - Adjust archetype weights
        - Request approval for major changes
        """
        return await self.handle_request(profile_id, "recalculate_scores")
