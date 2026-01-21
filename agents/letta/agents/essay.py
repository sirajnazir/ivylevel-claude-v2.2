"""
Essay Specialist Agent
======================

The Essay Specialist handles:
- Personal narrative development
- Essay feedback and coaching
- Story refinement
- Common App and supplemental essays

Uses techniques from the Essay domain (C1-C25).
"""

from typing import Dict, Any

from ..config import AgentType, AgentStatus


# System prompt for the Essay Specialist
ESSAY_SYSTEM_PROMPT = """You are the IvyLevel Essay Specialist - an expert in college application essays and personal narratives.

## Your Expertise

You specialize in:
1. **Narrative Development** - Helping students find and develop their unique story
2. **Essay Structure** - Building compelling essay architecture
3. **Voice Coaching** - Helping students write authentically
4. **Feedback & Revision** - Constructive critique that elevates writing
5. **Prompt Analysis** - Understanding what each school is really asking

## Essay Philosophy

### The IvyLevel Approach
- Authenticity over perfection
- Show, don't tell
- Specific > Generic
- The student's voice, not a polished-to-death version
- Essays reveal character, not just achievements

### Essay Types
- **Personal Statement (650 words)**: The big story, defines who you are
- **Supplemental Essays**: School-specific, show fit and research
- **Short Answers**: Concise insights into personality
- **Activity Descriptions (150 chars)**: Impact-focused brevity

## Your Tools

### search_techniques
Search for essay coaching techniques from the 139-technique library.
Use domain="essay" for C1-C25 techniques.

### get_student_profile
Understand student's story, experiences, and narrative DNA.

### get_active_gameplan
Check essay timeline and deadlines.

### request_approval
For final submission decisions.

## Communication Style

When coaching essays:
- Be encouraging but honest
- Point out what's working, not just what needs fixing
- Ask probing questions to draw out better material
- Respect the student's voice - don't rewrite for them
- Connect feedback to specific techniques

## Feedback Framework

1. **First Draft Feedback**
   - Celebrate the courage to start
   - Identify the core story/theme
   - Point to the strongest moments
   - Suggest one major revision focus

2. **Later Draft Feedback**
   - More specific line-level feedback
   - Check authenticity of voice
   - Verify the "so what" is clear
   - Polish without over-polishing

## Critical Rules

1. NEVER write the essay for the student
2. Always identify what's working before criticism
3. Ask questions rather than prescribe solutions
4. Protect the student's authentic voice
5. For Common App Personal Statement, ensure it stands alone

## Response Format

When giving essay feedback:
1. What's working well (specific examples)
2. The core story I'm hearing
3. Key revision suggestion (technique-backed)
4. Questions to consider
5. Next step recommendation
"""


# Essay Specialist configuration
ESSAY_AGENT_CONFIG: Dict[str, Any] = {
    "name": "Essay Specialist",
    "status": AgentStatus.ACTIVE.value,
    "agent_type": AgentType.ESSAY.value,
    "system_prompt": ESSAY_SYSTEM_PROMPT,
    "model": "gpt-4o",
    "tags": ["specialist", "essay", "writing"],
    "tools": [
        # Memory tools
        "core_memory_get",
        "core_memory_replace",
        # Custom IvyLevel tools
        "search_techniques",
        "get_student_profile",
        "get_active_gameplan",
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


class EssaySpecialist:
    """
    Essay Specialist wrapper for IvyLevel.

    Provides helper methods for essay coaching.
    The actual Letta agent is created using ESSAY_AGENT_CONFIG.
    """

    def __init__(self, letta_client, agent_id: str):
        """
        Initialize the Essay Specialist wrapper.

        Args:
            letta_client: Letta client instance
            agent_id: The Letta agent ID
        """
        self.client = letta_client
        self.agent_id = agent_id

    async def brainstorm_topics(
        self,
        profile_id: str,
        essay_type: str = "personal_statement",
    ) -> Dict[str, Any]:
        """
        Help brainstorm essay topics.

        Args:
            profile_id: Student profile ID
            essay_type: Type of essay (personal_statement, supplemental, etc.)

        Returns:
            Topic brainstorm with prompts
        """
        message = f"""Please help this student brainstorm essay topics.

Essay type: {essay_type}

Please:
1. Review the student's profile and narrative DNA
2. Search for relevant brainstorming techniques
3. Suggest 3-5 potential topics with brief rationale
4. Provide probing questions to develop each
5. Note which topics best match their authentic voice
"""

        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": message}],
        )

        return {
            "success": True,
            "brainstorm": response.messages[-1].content if response.messages else "",
            "profile_id": profile_id,
            "essay_type": essay_type,
        }

    async def provide_feedback(
        self,
        profile_id: str,
        essay_content: str,
        essay_type: str = "personal_statement",
        draft_number: int = 1,
    ) -> Dict[str, Any]:
        """
        Provide feedback on an essay draft.

        Args:
            profile_id: Student profile ID
            essay_content: The essay text
            essay_type: Type of essay
            draft_number: Which draft this is (affects feedback depth)

        Returns:
            Detailed feedback
        """
        message = f"""Please provide feedback on this essay.

Essay type: {essay_type}
Draft number: {draft_number}

---
{essay_content}
---

Please:
1. Identify what's working well (with specific examples)
2. Articulate the core story you're hearing
3. Search for relevant feedback techniques
4. Provide key revision suggestions
5. Ask probing questions
6. Recommend next steps
"""

        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": message}],
        )

        return {
            "success": True,
            "feedback": response.messages[-1].content if response.messages else "",
            "profile_id": profile_id,
            "essay_type": essay_type,
            "draft_number": draft_number,
        }

    async def analyze_prompt(
        self,
        profile_id: str,
        prompt_text: str,
        school_name: str = None,
    ) -> Dict[str, Any]:
        """
        Analyze an essay prompt.

        Args:
            profile_id: Student profile ID
            prompt_text: The essay prompt
            school_name: Optional school name for context

        Returns:
            Prompt analysis with approach suggestions
        """
        message = f"""Please analyze this essay prompt.

School: {school_name or 'Not specified'}
Prompt: {prompt_text}

Please:
1. Break down what the prompt is really asking
2. Identify key themes/values the school cares about
3. Review student profile for relevant material
4. Suggest 2-3 angles this student could take
5. Note any common pitfalls to avoid
"""

        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": message}],
        )

        return {
            "success": True,
            "analysis": response.messages[-1].content if response.messages else "",
            "profile_id": profile_id,
            "school_name": school_name,
        }
