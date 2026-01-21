"""
Execution Specialist Agent
==========================

The Execution Specialist handles:
- Task tracking and completion
- Deadline management
- Nudges and accountability
- Progress monitoring
- Stall detection and intervention

Uses techniques from the Execution domain (E1-E22).
"""

from typing import Dict, Any

from ..config import AgentType, AgentStatus


# System prompt for the Execution Specialist
EXECUTION_SYSTEM_PROMPT = """You are the IvyLevel Execution Specialist - an expert in helping students execute their plans.

## Your Expertise

You specialize in:
1. **Task Management** - Tracking tasks, marking completions, creating new tasks
2. **Deadline Management** - Monitoring deadlines, sending reminders, managing urgency
3. **Accountability** - Gentle nudges, progress check-ins, celebration of wins
4. **Stall Detection** - Identifying when students are stuck and intervening
5. **Momentum Building** - Helping students build and maintain progress streaks

## Execution Philosophy

### The IvyLevel Approach
- Progress over perfection
- Small wins compound into big results
- Accountability with compassion
- Remove blockers, don't add pressure

### Execution States
- **Healthy**: On track, good momentum
- **Moderate**: Some delays, needs attention
- **Warning**: Significant delays, intervention needed
- **Critical**: Major backlog, crisis mode

### EDS (Execution Debt Score)
Higher EDS = More execution debt (bad)
- 0-30: Healthy
- 30-50: Moderate
- 50-70: Warning
- 70+: Critical

## Your Tools

### search_techniques
Search for execution techniques from the 139-technique library.
Use domain="execution" for E1-E22 techniques.

### get_execution_state
Get current execution metrics (EDS, momentum, stall detection).

### check_upcoming_deadlines
See what's due soon and what's overdue.

### get_active_gameplan
See tasks and their status.

### get_student_profile
Understand student context for personalized nudges.

## Communication Style

When discussing execution:
- Be encouraging, not nagging
- Celebrate progress, no matter how small
- Acknowledge struggles with empathy
- Offer concrete help, not just reminders
- Break down overwhelming tasks

## Nudge Types

1. **Gentle Reminder**: "Hey, just checking in on [task]..."
2. **Progress Celebration**: "Amazing! You completed [task]! 🎉"
3. **Stall Intervention**: "I noticed you haven't worked on [task]. What's blocking you?"
4. **Deadline Alert**: "Heads up - [task] is due in [X] days"
5. **Momentum Boost**: "You're on a streak! Keep it going!"

## Critical Rules

1. NEVER shame or criticize the student
2. Always check execution state before suggesting actions
3. Celebrate wins - this builds motivation
4. When student is overwhelmed, help prioritize, don't add tasks
5. For repeated stalls, dig into root causes

## Response Format

When discussing execution:
1. Acknowledge current state
2. Highlight any urgent items
3. Provide specific, actionable guidance
4. Offer support for blockers
5. End with encouragement
"""


# Execution Specialist configuration
EXECUTION_AGENT_CONFIG: Dict[str, Any] = {
    "name": "Execution Specialist",
    "status": AgentStatus.ACTIVE.value,
    "agent_type": AgentType.EXECUTION.value,
    "system_prompt": EXECUTION_SYSTEM_PROMPT,
    "model": "gpt-4o",
    "tags": ["specialist", "execution", "tasks"],
    "tools": [
        # Memory tools
        "core_memory_get",
        "core_memory_replace",
        # Custom IvyLevel tools
        "search_techniques",
        "get_execution_state",
        "check_upcoming_deadlines",
        "get_active_gameplan",
        "get_student_profile",
        "get_recent_interactions",
    ],
    "memory_blocks": [
        "student_profile",
        "coaching_history",
        "active_gameplan",
        "outcome_tracker",
        "deadline_state",
    ],
}


class ExecutionSpecialist:
    """
    Execution Specialist wrapper for IvyLevel.

    Provides helper methods for execution management.
    The actual Letta agent is created using EXECUTION_AGENT_CONFIG.
    """

    def __init__(self, letta_client, agent_id: str):
        """
        Initialize the Execution Specialist wrapper.

        Args:
            letta_client: Letta client instance
            agent_id: The Letta agent ID
        """
        self.client = letta_client
        self.agent_id = agent_id

    async def check_in(self, profile_id: str) -> Dict[str, Any]:
        """
        Perform a progress check-in.

        Args:
            profile_id: Student profile ID

        Returns:
            Check-in response with status and recommendations
        """
        message = """Please check on this student's execution status.

1. Review their execution state (EDS, momentum)
2. Check for overdue or urgent deadlines
3. Identify any stalls
4. Provide appropriate nudge or celebration
"""

        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": message}],
        )

        return {
            "success": True,
            "check_in": response.messages[-1].content if response.messages else "",
            "profile_id": profile_id,
        }

    async def handle_stall(
        self,
        profile_id: str,
        stalled_task: str,
    ) -> Dict[str, Any]:
        """
        Handle a detected stall on a specific task.

        Args:
            profile_id: Student profile ID
            stalled_task: The task that's stalled

        Returns:
            Intervention response
        """
        message = f"""The student appears to be stalled on: "{stalled_task}"

Please:
1. Acknowledge the struggle without judgment
2. Search for relevant execution techniques
3. Offer to break down the task
4. Identify potential blockers
5. Provide encouragement
"""

        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": message}],
        )

        return {
            "success": True,
            "intervention": response.messages[-1].content if response.messages else "",
            "profile_id": profile_id,
            "stalled_task": stalled_task,
        }

    async def celebrate_completion(
        self,
        profile_id: str,
        completed_task: str,
    ) -> Dict[str, Any]:
        """
        Celebrate a task completion.

        Args:
            profile_id: Student profile ID
            completed_task: The task that was completed

        Returns:
            Celebration message
        """
        message = f"""The student just completed: "{completed_task}"

Please:
1. Celebrate this win!
2. Note the progress in coaching history
3. Suggest what's next
4. Build momentum
"""

        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": message}],
        )

        return {
            "success": True,
            "celebration": response.messages[-1].content if response.messages else "",
            "profile_id": profile_id,
            "completed_task": completed_task,
        }
