"""
Awards Specialist Agent
=======================

The Awards Specialist handles:
- Scholarship and award recommendations
- Competition strategies
- Recognition opportunities
- Award application guidance

Uses techniques from the Awards domain (D1-D20).
"""

from typing import Dict, Any

from ..config import AgentType, AgentStatus


# System prompt for the Awards Specialist
AWARDS_SYSTEM_PROMPT = """You are the IvyLevel Awards Specialist - an expert in scholarships, awards, and recognition opportunities.

## Your Expertise

You specialize in:
1. **Scholarship Matching** - Finding scholarships that fit the student's profile
2. **Award Strategy** - Identifying awards that strengthen applications
3. **Competition Guidance** - Recommending competitions aligned with interests
4. **Application Coaching** - Helping students win awards they apply for
5. **Recognition Opportunities** - Finding ways to get student work recognized

## Awards Philosophy

### The IvyLevel Approach
- Quality over quantity - better to win a few than apply to many
- Strategic alignment - awards should reinforce narrative
- Fit matters - match opportunities to actual strengths
- Timing is crucial - deadlines and preparation time

### Award Categories
- **National/International**: Highest impact, most competitive
- **Regional/State**: Strong impact, more attainable
- **School-based**: Good foundation, stepping stones
- **Niche/Interest-specific**: Can be highly valuable if relevant

## Your Tools

### search_techniques
Search for award recommendation techniques from the 139-technique library.
Use domain="awards" for D1-D20 techniques.

### get_student_profile
Understand student's interests, achievements, and goals for matching.

### match_opportunities
Find relevant scholarships, programs, and competitions.

### check_upcoming_deadlines
Track award application deadlines.

### request_approval
For major financial decisions (like paid competitions).

## Communication Style

When discussing awards:
- Be realistic about competitiveness
- Highlight why specific awards match this student
- Provide concrete application tips
- Note deadlines prominently
- Celebrate wins and encourage after rejections

## Critical Rules

1. Never recommend awards without checking student profile
2. Always note deadlines clearly
3. Be honest about competitiveness levels
4. For paid applications, check with student first
5. Track what student has already applied to

## Response Format

When recommending awards:
1. Explain why this award matches the student
2. Note eligibility requirements
3. Highlight deadline
4. Provide application tips specific to this student
5. Estimate competitiveness (high/medium/attainable)
"""


# Awards Specialist configuration
AWARDS_AGENT_CONFIG: Dict[str, Any] = {
    "name": "Awards Specialist",
    "status": AgentStatus.ACTIVE.value,
    "agent_type": AgentType.AWARDS.value,
    "system_prompt": AWARDS_SYSTEM_PROMPT,
    "model": "gpt-4o",
    "tags": ["specialist", "awards", "scholarships"],
    "tools": [
        # Memory tools
        "core_memory_get",
        "core_memory_replace",
        # Custom IvyLevel tools
        "search_techniques",
        "get_student_profile",
        "match_opportunities",
        "check_upcoming_deadlines",
        "get_goal_progress",
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


class AwardsSpecialist:
    """
    Awards Specialist wrapper for IvyLevel.

    Provides helper methods for award recommendations.
    The actual Letta agent is created using AWARDS_AGENT_CONFIG.
    """

    def __init__(self, letta_client, agent_id: str):
        """
        Initialize the Awards Specialist wrapper.

        Args:
            letta_client: Letta client instance
            agent_id: The Letta agent ID
        """
        self.client = letta_client
        self.agent_id = agent_id

    async def find_opportunities(
        self,
        profile_id: str,
        focus: str = None,
    ) -> Dict[str, Any]:
        """
        Find award opportunities for a student.

        Args:
            profile_id: Student profile ID
            focus: Optional specific focus (scholarships, competitions, etc.)

        Returns:
            Matched opportunities with recommendations
        """
        message = f"""Please find award opportunities for this student.

Focus: {focus or 'All types - scholarships, competitions, awards'}

Please:
1. Review the student's profile and interests
2. Search for matching opportunities
3. Rank by fit and attainability
4. Note deadlines and requirements
5. Provide application tips
"""

        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": message}],
        )

        return {
            "success": True,
            "opportunities": response.messages[-1].content if response.messages else "",
            "profile_id": profile_id,
        }

    async def prepare_application(
        self,
        profile_id: str,
        award_name: str,
    ) -> Dict[str, Any]:
        """
        Help prepare for a specific award application.

        Args:
            profile_id: Student profile ID
            award_name: Name of the award

        Returns:
            Application preparation guidance
        """
        message = f"""Please help this student prepare for: "{award_name}"

Please:
1. Review the award requirements
2. Identify how student's profile matches
3. Search for relevant techniques
4. Provide specific application tips
5. Note timeline and deadline
"""

        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": message}],
        )

        return {
            "success": True,
            "preparation": response.messages[-1].content if response.messages else "",
            "profile_id": profile_id,
            "award_name": award_name,
        }
