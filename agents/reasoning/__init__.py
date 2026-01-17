"""
Reasoning Patterns - v5.4 True Autonomous Agents

Patterns implemented:
- A4: Chain-of-Thought (3P: OpenAI/Anthropic)
- A10: Agent Routing (3P: LangGraph patterns)

Intelligent reasoning and routing for agents.
"""

from .chain_of_thought import (
    ChainOfThoughtReasoner,
    ReasoningChain,
    ThoughtStep,
    think_step_by_step,
    REASONING_TEMPLATES,
)

from .routing import (
    AgentRouter,
    IntentClassifier,
    MultiAgentOrchestrator,
    RouteDecision,
    Intent,
    detect_intent,
    route_message,
    INTENT_PATTERNS,
    AGENT_ROUTING,
)

__all__ = [
    # Chain-of-Thought
    "ChainOfThoughtReasoner",
    "ReasoningChain",
    "ThoughtStep",
    "think_step_by_step",
    "REASONING_TEMPLATES",
    # Routing
    "AgentRouter",
    "IntentClassifier",
    "MultiAgentOrchestrator",
    "RouteDecision",
    "Intent",
    "detect_intent",
    "route_message",
    "INTENT_PATTERNS",
    "AGENT_ROUTING",
]
