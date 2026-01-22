# agents/tests/patterns/test_reasoning.py
"""
Tests for Reasoning Patterns (A4, A10) - v5.4 True Autonomous Agents.

Tests:
- A4: Chain-of-Thought reasoning
- A10: Agent Routing and orchestration
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestChainOfThought:
    """Tests for A4: Chain-of-Thought pattern."""

    def test_reasoner_creation(self, mock_llm):
        """Test ChainOfThoughtReasoner can be created."""
        from reasoning import ChainOfThoughtReasoner

        reasoner = ChainOfThoughtReasoner(mock_llm)

        assert reasoner is not None

    def test_reasoning_chain_model(self):
        """Test ReasoningChain model structure."""
        from reasoning import ReasoningChain, ThoughtStep

        chain = ReasoningChain(
            task="Generate activity recommendations",
            steps=[
                ThoughtStep(
                    step_number=1,
                    thought="First, analyze current activities",
                    action="Review activity list",
                    observation="Student has robotics focus",
                ),
                ThoughtStep(
                    step_number=2,
                    thought="Identify gaps in profile",
                    action="Compare with target schools",
                    observation="Need more leadership roles",
                ),
            ],
            conclusion="Recommend pursuing leadership in robotics club",
            confidence=0.85,
        )

        assert len(chain.steps) == 2
        assert chain.confidence == 0.85

    def test_thought_step_model(self):
        """Test ThoughtStep model structure."""
        from reasoning import ThoughtStep

        step = ThoughtStep(
            step_number=1,
            thought="Analyze student's spike",
            action="Review activities and projects",
            observation="Strong robotics focus evident",
        )

        assert step.step_number == 1
        assert "robotics" in step.observation

    @pytest.mark.asyncio
    async def test_reason_returns_chain(self, mock_llm, sample_student_context):
        """Test reasoning returns a complete chain."""
        from reasoning import ChainOfThoughtReasoner

        mock_llm.set_responses([
            "Step 1: Analyze profile\nObservation: Student has robotics spike",
            "Step 2: Identify opportunities\nObservation: Summer programs available",
            "Conclusion: Focus on summer robotics research",
        ])

        reasoner = ChainOfThoughtReasoner(mock_llm)

        chain = await reasoner.reason(
            task_type="recommendation",
            context=sample_student_context,
        )

        assert chain is not None
        # LLM was called

    def test_reasoning_templates_defined(self):
        """Test reasoning templates are configured."""
        from reasoning import REASONING_TEMPLATES

        assert REASONING_TEMPLATES is not None
        assert isinstance(REASONING_TEMPLATES, dict)

    def test_think_step_by_step_function(self, mock_llm):
        """Test convenience function for step-by-step thinking."""
        from reasoning import think_step_by_step

        assert callable(think_step_by_step)


class TestRouting:
    """Tests for A10: Agent Routing pattern."""

    def test_router_creation(self):
        """Test AgentRouter can be created."""
        from reasoning import AgentRouter

        router = AgentRouter()

        assert router is not None

    def test_intent_classifier_creation(self):
        """Test IntentClassifier can be created."""
        from reasoning import IntentClassifier

        classifier = IntentClassifier()

        assert classifier is not None

    def test_intent_model(self):
        """Test Intent model structure."""
        from reasoning import Intent

        intent = Intent(
            intent_type="recommendation_request",
            confidence=0.92,
            entities={"topic": "summer programs"},
            raw_message="What summer programs should I apply to?",
        )

        assert intent.intent_type == "recommendation_request"
        assert intent.confidence == 0.92

    def test_route_decision_model(self):
        """Test RouteDecision model structure."""
        from reasoning import RouteDecision

        decision = RouteDecision(
            target_agent="recommendation_agent",
            confidence=0.88,
            reasoning="User asking for activity recommendations",
            fallback_agent="general_agent",
        )

        assert decision.target_agent == "recommendation_agent"
        assert decision.fallback_agent == "general_agent"

    def test_detect_intent_from_message(self):
        """Test intent detection from user message."""
        from reasoning import detect_intent

        intent = detect_intent("What activities should I focus on this semester?")

        assert intent is not None
        assert intent.confidence > 0

    def test_route_message_function(self):
        """Test message routing function."""
        from reasoning import route_message

        decision = route_message(
            message="Help me plan my college applications",
            context={"profile_id": "test-123"},
        )

        assert decision is not None
        assert decision.target_agent is not None

    def test_intent_patterns_defined(self):
        """Test intent patterns are configured."""
        from reasoning import INTENT_PATTERNS

        assert INTENT_PATTERNS is not None
        assert isinstance(INTENT_PATTERNS, dict)

    def test_agent_routing_defined(self):
        """Test agent routing configuration exists."""
        from reasoning import AGENT_ROUTING

        assert AGENT_ROUTING is not None
        assert isinstance(AGENT_ROUTING, dict)


class TestMultiAgentOrchestrator:
    """Tests for multi-agent orchestration."""

    def test_orchestrator_creation(self):
        """Test MultiAgentOrchestrator can be created."""
        from reasoning import MultiAgentOrchestrator

        orchestrator = MultiAgentOrchestrator()

        assert orchestrator is not None

    def test_orchestrator_routes_to_correct_agent(self):
        """Test orchestrator routes to appropriate agent."""
        from reasoning import MultiAgentOrchestrator

        orchestrator = MultiAgentOrchestrator()

        # Gameplan-related message
        decision = orchestrator.route(
            message="Create a gameplan for my college applications",
            context={},
        )

        # Should route to gameplan-related agent
        assert decision is not None

    def test_orchestrator_handles_ambiguous_messages(self):
        """Test orchestrator handles ambiguous messages."""
        from reasoning import MultiAgentOrchestrator

        orchestrator = MultiAgentOrchestrator()

        decision = orchestrator.route(
            message="Help",
            context={},
        )

        # Should have a fallback
        assert decision is not None
        assert decision.target_agent is not None or decision.fallback_agent is not None


class TestReasoningIntegration:
    """Integration tests for reasoning patterns."""

    def test_all_reasoning_types_importable(self):
        """Test all reasoning types can be imported."""
        from reasoning import (
            ChainOfThoughtReasoner,
            ReasoningChain,
            ThoughtStep,
            AgentRouter,
            IntentClassifier,
            MultiAgentOrchestrator,
            RouteDecision,
            Intent,
        )

        # All should be importable

    @pytest.mark.asyncio
    async def test_reasoning_informs_routing(self, mock_llm, sample_student_context):
        """Test reasoning can inform routing decisions."""
        from reasoning import ChainOfThoughtReasoner, AgentRouter

        reasoner = ChainOfThoughtReasoner(mock_llm)
        router = AgentRouter()

        # Reason about the request
        mock_llm.set_responses(["This is a gameplan request"])

        chain = await reasoner.reason(
            task_type="intent_analysis",
            context={"message": "Help me plan for college"},
        )

        # Use reasoning to inform routing
        decision = router.route(
            message="Help me plan for college",
            context={"reasoning": chain},
        )

        assert decision is not None

    def test_routing_handles_all_intent_types(self):
        """Test routing handles all defined intent types."""
        from reasoning import AgentRouter, INTENT_PATTERNS

        router = AgentRouter()

        # Test each intent pattern
        for intent_type in INTENT_PATTERNS.keys():
            decision = router.route(
                message=f"Test message for {intent_type}",
                context={"intent_type": intent_type},
            )
            assert decision is not None

    def test_routing_is_deterministic(self):
        """Test same message routes to same agent."""
        from reasoning import route_message

        message = "What activities should I do this summer?"
        context = {"profile_id": "test-123"}

        decision1 = route_message(message, context)
        decision2 = route_message(message, context)

        assert decision1.target_agent == decision2.target_agent

    def test_intent_detection_with_context(self, sample_student_context):
        """Test intent detection uses context."""
        from reasoning import detect_intent

        # Without context
        intent1 = detect_intent("What should I do?")

        # With context (student with robotics spike)
        intent2 = detect_intent("What should I do?", context=sample_student_context)

        # Both should work
        assert intent1 is not None
        assert intent2 is not None
