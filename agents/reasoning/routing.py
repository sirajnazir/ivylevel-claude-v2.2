"""
Pattern A10: Agent Routing
v5.4 True Autonomous Agents

3P: LangGraph for routing logic
USP: Intent-aware routing to specialist agents
"""

from typing import Dict, Any, List, Optional, Callable, Type
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import logging
import re

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    """User intents that drive routing."""
    ASSESSMENT = "assessment"           # Evaluate profile
    GAMEPLAN = "gameplan"              # Create plan
    ACTIVITY_HELP = "activity_help"    # Help with activities
    AWARD_SEARCH = "award_search"      # Find awards
    PROGRAM_SEARCH = "program_search"  # Find programs
    ESSAY_HELP = "essay_help"          # Essay assistance
    SCHOOL_RESEARCH = "school_research" # School information
    DEADLINE_CHECK = "deadline_check"   # Check deadlines
    GENERAL_CHAT = "general_chat"       # General conversation
    CRISIS = "crisis"                   # Distress/crisis


class RouteDecision(BaseModel):
    """A routing decision."""
    intent: Intent
    confidence: float = Field(ge=0.0, le=1.0)
    target_agent: str
    reasoning: str = ""
    context_to_pass: Dict[str, Any] = Field(default_factory=dict)
    fallback_agent: Optional[str] = None


# Intent detection patterns (USP: admissions-specific)
INTENT_PATTERNS = {
    Intent.ASSESSMENT: [
        r"\b(assess|evaluate|analyze|review)\b.*\b(profile|activities|portfolio)\b",
        r"\b(how\s+(am\s+)?i\s+doing|where\s+do\s+i\s+stand)\b",
        r"\b(my\s+chances|competitive|strong)\b",
    ],
    Intent.GAMEPLAN: [
        r"\b(plan|gameplan|strategy|roadmap|next\s+steps)\b",
        r"\b(what\s+should\s+i\s+do|what\s+now|help\s+me\s+plan)\b",
        r"\b(prioritize|focus\s+on)\b",
    ],
    Intent.ACTIVITY_HELP: [
        r"\b(activity|activities|extracurricular|ec|club)\b",
        r"\b(start|join|create|found)\b.*\b(club|organization|initiative)\b",
        r"\b(leadership|impact|hours)\b",
    ],
    Intent.AWARD_SEARCH: [
        r"\b(award|awards|competition|scholarship|olympiad)\b",
        r"\b(win|apply|enter)\b.*\b(contest|competition)\b",
        r"\b(recognition|honor|achievement)\b",
    ],
    Intent.PROGRAM_SEARCH: [
        r"\b(program|programs|summer|internship|research)\b",
        r"\b(rsi|ssp|simons|tasp|telluride)\b",
        r"\b(selective|prestigious)\b.*\b(opportunity|experience)\b",
    ],
    Intent.ESSAY_HELP: [
        r"\b(essay|essays|personal\s+statement|supplement|common\s+app)\b",
        r"\b(write|writing|draft|edit|brainstorm)\b.*\b(story|topic)\b",
        r"\b(college\s+essay|application\s+essay)\b",
    ],
    Intent.SCHOOL_RESEARCH: [
        r"\b(school|college|university)\b.*\b(research|learn|info)\b",
        r"\b(harvard|yale|stanford|mit|princeton)\b",
        r"\b(campus|program|major|culture)\b.*\b(what|tell\s+me)\b",
    ],
    Intent.DEADLINE_CHECK: [
        r"\b(deadline|due\s+date|when)\b",
        r"\b(submit|application|apply)\b.*\b(by|before)\b",
        r"\b(early\s+decision|early\s+action|regular\s+decision)\b",
    ],
    Intent.CRISIS: [
        r"\b(stressed|overwhelmed|anxious|depressed|hopeless)\b",
        r"\b(can't\s+do\s+this|give\s+up|too\s+much)\b",
        r"\b(help|sos|urgent|emergency)\b",
    ],
}

# Agent routing table
AGENT_ROUTING = {
    Intent.ASSESSMENT: "ec_agent",
    Intent.GAMEPLAN: "gameplan_agent",
    Intent.ACTIVITY_HELP: "ec_agent",
    Intent.AWARD_SEARCH: "awards_agent",
    Intent.PROGRAM_SEARCH: "programs_agent",
    Intent.ESSAY_HELP: "essay_agent",
    Intent.SCHOOL_RESEARCH: "school_agent",
    Intent.DEADLINE_CHECK: "temporal_agent",
    Intent.GENERAL_CHAT: "coaching_agent",
    Intent.CRISIS: "crisis_handler",
}


class IntentClassifier:
    """
    Classifies user intent from messages.

    USP: Admissions-specific intent detection.
    """

    def __init__(
        self,
        patterns: Optional[Dict[Intent, List[str]]] = None,
        llm_client=None,
    ):
        """
        Initialize classifier.

        Args:
            patterns: Custom intent patterns
            llm_client: Optional LLM for better classification
        """
        self.patterns = patterns or INTENT_PATTERNS
        self.llm = llm_client
        self._compiled: Dict[Intent, List[re.Pattern]] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns."""
        for intent, patterns in self.patterns.items():
            self._compiled[intent] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def classify(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> tuple[Intent, float]:
        """
        Classify message intent.

        Args:
            message: User's message
            context: Additional context

        Returns:
            Tuple of (Intent, confidence)
        """
        context = context or {}

        # Check for crisis first (highest priority)
        for pattern in self._compiled.get(Intent.CRISIS, []):
            if pattern.search(message):
                logger.warning("Crisis intent detected")
                return (Intent.CRISIS, 0.95)

        # Score each intent
        scores: Dict[Intent, float] = {}
        for intent, patterns in self._compiled.items():
            if intent == Intent.CRISIS:
                continue  # Already checked

            matches = sum(1 for p in patterns if p.search(message))
            if matches > 0:
                scores[intent] = min(0.5 + matches * 0.2, 0.95)

        # Use context to boost certain intents
        if context.get("current_task") == "gameplan":
            scores[Intent.GAMEPLAN] = scores.get(Intent.GAMEPLAN, 0) + 0.2

        if context.get("discussing_activities"):
            scores[Intent.ACTIVITY_HELP] = scores.get(Intent.ACTIVITY_HELP, 0) + 0.2

        # Return highest scoring intent
        if scores:
            best_intent = max(scores, key=scores.get)
            return (best_intent, scores[best_intent])

        # Default to general chat
        return (Intent.GENERAL_CHAT, 0.5)


class AgentRouter:
    """
    Routes requests to appropriate agents.

    Pattern A10: Agent Routing (3P: LangGraph patterns)

    Why this matters:
    1. Students get specialist help for each need
    2. Agents stay focused on their expertise
    3. Better quality responses
    4. Enables complex multi-agent workflows
    """

    def __init__(
        self,
        routing_table: Optional[Dict[Intent, str]] = None,
        classifier: Optional[IntentClassifier] = None,
    ):
        """
        Initialize router.

        Args:
            routing_table: Intent -> agent name mapping
            classifier: Intent classifier to use
        """
        self.routing_table = routing_table or AGENT_ROUTING
        self.classifier = classifier or IntentClassifier()
        self._agents: Dict[str, Any] = {}
        self._middleware: List[Callable] = []

    def register_agent(
        self,
        name: str,
        agent: Any,
    ) -> None:
        """Register an agent for routing."""
        self._agents[name] = agent
        logger.info(f"Registered agent: {name}")

    def add_middleware(
        self,
        middleware: Callable[[str, Dict], tuple[str, Dict]],
    ) -> None:
        """Add routing middleware for pre-processing."""
        self._middleware.append(middleware)

    def route(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> RouteDecision:
        """
        Route a message to the appropriate agent.

        Args:
            message: User's message
            context: Additional context

        Returns:
            RouteDecision with target agent
        """
        context = context or {}

        # Apply middleware
        for middleware in self._middleware:
            message, context = middleware(message, context)

        # Classify intent
        intent, confidence = self.classifier.classify(message, context)

        # Look up target agent
        target_agent = self.routing_table.get(intent, "coaching_agent")

        # Determine fallback
        fallback_agent = "coaching_agent" if target_agent != "coaching_agent" else None

        # Build reasoning
        reasoning = f"Detected intent '{intent.value}' with {confidence:.0%} confidence"

        # Context to pass to agent
        context_to_pass = {
            "original_message": message,
            "detected_intent": intent.value,
            "confidence": confidence,
            **context,
        }

        decision = RouteDecision(
            intent=intent,
            confidence=confidence,
            target_agent=target_agent,
            reasoning=reasoning,
            context_to_pass=context_to_pass,
            fallback_agent=fallback_agent,
        )

        logger.info(f"Routed to {target_agent}: {reasoning}")

        return decision

    async def execute_route(
        self,
        decision: RouteDecision,
    ) -> Any:
        """
        Execute routing decision by calling target agent.

        Args:
            decision: The routing decision

        Returns:
            Agent response
        """
        agent = self._agents.get(decision.target_agent)

        if not agent:
            logger.warning(f"Agent {decision.target_agent} not found")
            if decision.fallback_agent:
                agent = self._agents.get(decision.fallback_agent)

        if not agent:
            raise ValueError(f"No agent found for route: {decision.target_agent}")

        try:
            # Most agents will have a process method
            if hasattr(agent, "process"):
                return await agent.process(**decision.context_to_pass)
            elif hasattr(agent, "__call__"):
                return await agent(decision.context_to_pass)
            else:
                raise AttributeError(f"Agent {decision.target_agent} has no callable method")

        except Exception as e:
            logger.error(f"Error executing route to {decision.target_agent}: {e}")
            if decision.fallback_agent:
                fallback = self._agents.get(decision.fallback_agent)
                if fallback and hasattr(fallback, "process"):
                    return await fallback.process(**decision.context_to_pass)
            raise


class MultiAgentOrchestrator:
    """
    Orchestrates multi-agent workflows.

    USP: Complex routing for gameplan generation.
    """

    def __init__(self, router: AgentRouter):
        self.router = router
        self._workflows: Dict[str, List[str]] = {
            "full_gameplan": [
                "ec_agent",
                "awards_agent",
                "programs_agent",
                "gameplan_agent",
            ],
            "assessment": [
                "ec_agent",
            ],
            "opportunity_search": [
                "awards_agent",
                "programs_agent",
            ],
        }

    async def execute_workflow(
        self,
        workflow_name: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a multi-agent workflow.

        Args:
            workflow_name: Name of workflow to execute
            context: Initial context

        Returns:
            Combined results from all agents
        """
        agents = self._workflows.get(workflow_name, [])
        if not agents:
            raise ValueError(f"Unknown workflow: {workflow_name}")

        results = {}
        current_context = context.copy()

        for agent_name in agents:
            logger.info(f"Workflow {workflow_name}: executing {agent_name}")

            decision = RouteDecision(
                intent=Intent.GENERAL_CHAT,  # Workflow-driven
                confidence=1.0,
                target_agent=agent_name,
                context_to_pass=current_context,
            )

            result = await self.router.execute_route(decision)
            results[agent_name] = result

            # Pass results to next agent in chain
            current_context["previous_results"] = results

        return results


# Convenience functions
def detect_intent(
    message: str,
    context: Optional[Dict[str, Any]] = None,
) -> tuple[Intent, float]:
    """Quick helper to detect intent."""
    classifier = IntentClassifier()
    return classifier.classify(message, context)


def route_message(
    message: str,
    context: Optional[Dict[str, Any]] = None,
) -> RouteDecision:
    """Quick helper to route a message."""
    router = AgentRouter()
    return router.route(message, context)
