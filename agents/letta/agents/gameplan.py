"""
GamePlan Specialist Agent
=========================

The GamePlan Specialist handles:
- Strategic planning and goal setting
- Application timeline creation
- Milestone and priority management
- Long-term strategy development

Uses techniques from the Strategy domain.
"""

from typing import Dict, Any

from ..config import AgentType, AgentStatus


# System prompt for the GamePlan Specialist
GAMEPLAN_SYSTEM_PROMPT = """You are the IvyLevel GamePlan Specialist - an expert in college admissions strategy.

## Your Expertise

You specialize in:
1. **Strategic Planning** - Creating comprehensive application strategies
2. **Timeline Management** - Building realistic timelines for applications
3. **Goal Setting** - Helping students define and refine their goals
4. **Priority Management** - Organizing tasks into P0/P1/P2 priorities
5. **Milestone Tracking** - Setting and monitoring key milestones

## Planning Philosophy

### The IvyLevel Approach
- Start with the end in mind (target schools, outcomes)
- Work backwards to create actionable steps
- Balance ambition with realism
- Account for the whole student, not just academics

### Priority Framework
- **P0 (Critical)**: Must be done immediately, blockers for everything else
- **P1 (Important)**: Significant impact, should be done this week
- **P2 (Nice-to-have)**: Valuable but can be deferred if needed

## Your Tools

### search_techniques
Search for strategic planning techniques from the 139-technique library.
Use domain="strategy" for planning techniques.

### get_student_profile
Get the student's complete profile to inform planning.

### get_active_gameplan
See what plans already exist to avoid duplication.

### get_goal_progress
Check progress on existing goals.

### request_approval
Request approval for major plan changes.

## Communication Style

When creating or discussing plans:
- Be specific and actionable, not vague
- Explain WHY each element is important
- Connect actions to outcomes
- Acknowledge constraints (time, resources)
- Offer alternatives when possible

## Critical Rules

1. Never create a plan without understanding the student's profile first
2. Always check existing gameplan before creating new one
3. For major plan changes, USE request_approval tool
4. Set realistic timelines - don't overpromise
5. Include buffer time for unexpected challenges

## Response Format

When presenting a plan or strategy:
1. Start with context (what we know about the student)
2. Present the strategic recommendation
3. Break down into specific actions
4. Assign priorities (P0/P1/P2)
5. Note any dependencies or risks
"""


# GamePlan Specialist configuration
GAMEPLAN_AGENT_CONFIG: Dict[str, Any] = {
    "name": "GamePlan Specialist",
    "status": AgentStatus.ACTIVE.value,
    "agent_type": AgentType.GAMEPLAN.value,
    "system_prompt": GAMEPLAN_SYSTEM_PROMPT,
    "model": "gpt-4o",
    "tags": ["specialist", "strategy", "gameplan"],
    "tools": [
        # Memory tools
        "core_memory_get",
        "core_memory_replace",
        # Custom IvyLevel tools
        "search_techniques",
        "get_student_profile",
        "get_active_gameplan",
        "get_goal_progress",
        "check_upcoming_deadlines",
        "request_approval",
    ],
    "memory_blocks": [
        "student_profile",
        "coaching_history",
        "active_gameplan",
        "outcome_tracker",
        "deadline_state",
    ],
}


class GamePlanSpecialist:
    """
    GamePlan Specialist wrapper for IvyLevel.

    Provides helper methods for strategic planning.
    The actual Letta agent is created using GAMEPLAN_AGENT_CONFIG.
    """

    def __init__(self, letta_client, agent_id: str):
        """
        Initialize the GamePlan Specialist wrapper.

        Args:
            letta_client: Letta client instance
            agent_id: The Letta agent ID
        """
        self.client = letta_client
        self.agent_id = agent_id

    async def create_strategic_plan(
        self,
        profile_id: str,
        focus_areas: list = None,
    ) -> Dict[str, Any]:
        """
        Create a strategic plan for a student.

        Args:
            profile_id: Student profile ID
            focus_areas: Optional specific areas to focus on

        Returns:
            Strategic plan with priorities
        """
        message = f"""Please create a strategic plan for this student.

Focus areas: {focus_areas or 'General - all domains'}

Please:
1. Review the student's profile
2. Check existing gameplan
3. Identify gaps and opportunities
4. Create actionable recommendations with P0/P1/P2 priorities
"""

        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": message}],
        )

        return {
            "success": True,
            "plan": response.messages[-1].content if response.messages else "",
            "profile_id": profile_id,
        }

    async def review_and_adjust(
        self,
        profile_id: str,
        feedback: str,
    ) -> Dict[str, Any]:
        """
        Review and adjust an existing plan based on feedback.

        Args:
            profile_id: Student profile ID
            feedback: User feedback on current plan

        Returns:
            Adjusted plan
        """
        message = f"""The student has provided feedback on their current plan:

"{feedback}"

Please:
1. Review the current gameplan
2. Consider this feedback
3. Suggest adjustments
4. If major changes, request approval
"""

        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": message}],
        )

        return {
            "success": True,
            "adjustments": response.messages[-1].content if response.messages else "",
            "profile_id": profile_id,
        }
