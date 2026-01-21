"""
Orchestrator Agent
==================

The Orchestrator is the supervisor agent that:
- Routes conversations to appropriate specialist agents
- Maintains conversation context across specialists
- Handles general inquiries that don't fit a specific domain
- Coordinates multi-step coaching workflows

The Orchestrator uses Letta's agent-to-agent communication:
- send_message_to_agent_and_wait_for_reply (sync)
- send_message_to_agent_async (async)
- send_message_to_agents_matching_all_tags (broadcast)
"""

from typing import Dict, Any, List

from ..config import AgentType, AgentStatus


# System prompt for the Orchestrator
ORCHESTRATOR_SYSTEM_PROMPT = """You are the IvyLevel Orchestrator - a master coach coordinator for college admissions.

## Your Role
You are the central coordinator for a team of specialist coaches. Your job is to:
1. Understand what the student needs
2. Route to the right specialist (or handle it yourself for general questions)
3. Synthesize responses when multiple specialists are involved
4. Maintain coaching continuity across conversations

## Your Team of Specialists

### GamePlan Specialist
- Strategic planning and goal setting
- Creating application timelines
- Setting milestones and priorities
- When to route: Questions about "what should I do", long-term planning, strategy

### Execution Specialist
- Task tracking and completion
- Deadline management
- Nudges and accountability
- When to route: Questions about tasks, deadlines, "what's next", progress tracking

### Awards Specialist
- Scholarship and award recommendations
- Competition strategies
- Recognition opportunities
- When to route: Questions about awards, scholarships, competitions, honors

### Essay Specialist
- Personal narrative development
- Essay feedback and coaching
- Story refinement
- When to route: Essay questions, personal statements, writing help

### Assessment Specialist (DORMANT)
- Not currently active
- Future: Quarterly reassessment

## Routing Guidelines

ALWAYS route to a specialist when the query clearly fits their domain.

DO NOT route when:
- The student is just saying hello or making small talk
- The question is about how IvyLevel works
- The question requires information from multiple specialists (you synthesize)

## Communication Style

You are warm but professional. You:
- Acknowledge the student's feelings and concerns
- Provide clear, actionable guidance
- Celebrate wins and progress
- Never shame or criticize
- Use the student's name when available

## Memory Blocks

You have access to these memory blocks:
- student_profile: Core student attributes
- coaching_history: Recent interactions
- active_gameplan: Current strategic plan
- outcome_tracker: Goal progress
- deadline_state: Upcoming deadlines

Use these to personalize your responses and maintain context.

## Critical Rules

1. ALWAYS check deadlines before responding - alert on urgent items
2. NEVER make promises about admission outcomes
3. For critical actions, USE request_approval tool
4. When unsure, ASK for clarification rather than assuming
"""


# Orchestrator configuration for Letta agent creation
ORCHESTRATOR_CONFIG: Dict[str, Any] = {
    "name": "Orchestrator",
    "status": AgentStatus.ACTIVE.value,
    "agent_type": AgentType.ORCHESTRATOR.value,
    "system_prompt": ORCHESTRATOR_SYSTEM_PROMPT,
    "model": "gpt-4o",
    "tags": ["supervisor", "router", "orchestrator"],
    "tools": [
        # Routing tools (A2A communication)
        "send_message_to_agent_and_wait_for_reply",
        "send_message_to_agent_async",
        # Memory tools
        "core_memory_get",
        "core_memory_replace",
        # Custom IvyLevel tools
        "get_student_profile",
        "check_upcoming_deadlines",
        "get_execution_state",
        "request_approval",
        "search_techniques",
    ],
    "memory_blocks": [
        "student_profile",
        "coaching_history",
        "active_gameplan",
        "outcome_tracker",
        "deadline_state",
    ],
    "routing_config": {
        "gameplan": {
            "keywords": ["plan", "strategy", "goal", "timeline", "milestone", "priority"],
            "agent_type": AgentType.GAMEPLAN.value,
        },
        "execution": {
            "keywords": ["task", "deadline", "progress", "complete", "next", "do"],
            "agent_type": AgentType.EXECUTION.value,
        },
        "awards": {
            "keywords": ["award", "scholarship", "competition", "honor", "recognition"],
            "agent_type": AgentType.AWARDS.value,
        },
        "essay": {
            "keywords": ["essay", "write", "story", "narrative", "personal statement"],
            "agent_type": AgentType.ESSAY.value,
        },
    },
}


class OrchestratorAgent:
    """
    Orchestrator agent wrapper for IvyLevel.

    This class provides helper methods for routing and coordination.
    The actual Letta agent is created using ORCHESTRATOR_CONFIG.
    """

    def __init__(self, letta_client, agent_id: str):
        """
        Initialize the Orchestrator wrapper.

        Args:
            letta_client: Letta client instance
            agent_id: The Letta agent ID for this orchestrator
        """
        self.client = letta_client
        self.agent_id = agent_id
        self.specialist_ids: Dict[AgentType, str] = {}

    def register_specialist(self, agent_type: AgentType, agent_id: str) -> None:
        """Register a specialist agent for routing."""
        self.specialist_ids[agent_type] = agent_id

    def determine_route(self, message: str) -> AgentType:
        """
        Determine which specialist to route to based on message content.

        Args:
            message: The user's message

        Returns:
            AgentType for the appropriate specialist, or ORCHESTRATOR for self-handling
        """
        message_lower = message.lower()
        routing_config = ORCHESTRATOR_CONFIG["routing_config"]

        # Check each specialist's keywords
        for domain, config in routing_config.items():
            for keyword in config["keywords"]:
                if keyword in message_lower:
                    return AgentType(config["agent_type"])

        # Default to self (Orchestrator handles it)
        return AgentType.ORCHESTRATOR

    async def route_message(
        self,
        message: str,
        target_agent_type: AgentType,
        wait_for_reply: bool = True,
    ) -> Dict[str, Any]:
        """
        Route a message to a specialist agent.

        Args:
            message: The message to send
            target_agent_type: The specialist to route to
            wait_for_reply: Whether to wait for the response

        Returns:
            Response from the specialist
        """
        if target_agent_type not in self.specialist_ids:
            return {
                "success": False,
                "error": f"Specialist {target_agent_type.value} not registered",
            }

        target_id = self.specialist_ids[target_agent_type]

        try:
            if wait_for_reply:
                # Synchronous routing
                response = self.client.agents.messages.send_to_agent(
                    agent_id=self.agent_id,
                    target_agent_id=target_id,
                    message=message,
                    wait_for_reply=True,
                )
            else:
                # Asynchronous routing
                response = self.client.agents.messages.send_to_agent(
                    agent_id=self.agent_id,
                    target_agent_id=target_id,
                    message=message,
                    wait_for_reply=False,
                )

            return {
                "success": True,
                "response": response,
                "routed_to": target_agent_type.value,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def broadcast_to_specialists(
        self,
        message: str,
        tags: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Broadcast a message to multiple specialists.

        Useful for updates that affect multiple domains.

        Args:
            message: The message to broadcast
            tags: Tags to match specialists (default: ["specialist"])

        Returns:
            Results from all specialists
        """
        if tags is None:
            tags = ["specialist"]

        try:
            response = self.client.agents.messages.send_to_agents_by_tags(
                agent_id=self.agent_id,
                tags=tags,
                message=message,
            )

            return {
                "success": True,
                "responses": response,
                "broadcast_tags": tags,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
