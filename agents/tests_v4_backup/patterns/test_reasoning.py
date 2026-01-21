# tests/patterns/test_reasoning.py
"""
Tests for Reasoning patterns: A4 Chain-of-Thought, A10 Agent Routing
CORRECTED to match actual implementation
"""

import pytest


class TestIntentClassifier:
    """Tests for IntentClassifier (A10)."""
    
    def test_classifier_importable(self):
        """Test IntentClassifier can be imported."""
        from reasoning.routing import IntentClassifier
        assert IntentClassifier is not None
    
    def test_classifier_initialization(self):
        """Test IntentClassifier can be initialized."""
        from reasoning.routing import IntentClassifier
        classifier = IntentClassifier()
        assert classifier is not None
    
    def test_classify_returns_tuple(self):
        """Test classify returns tuple of (Intent, float)."""
        from reasoning.routing import IntentClassifier, Intent
        
        classifier = IntentClassifier()
        result = classifier.classify("Help me with my essay")
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], Intent)
        assert isinstance(result[1], float)
    
    def test_classify_essay_help(self):
        """Test classify detects essay help intent."""
        from reasoning.routing import IntentClassifier, Intent
        
        classifier = IntentClassifier()
        intent, confidence = classifier.classify("Can you help me write my college essay?")
        
        assert intent == Intent.ESSAY_HELP
    
    def test_classify_award_search(self):
        """Test classify detects award search intent."""
        from reasoning.routing import IntentClassifier, Intent
        
        classifier = IntentClassifier()
        intent, confidence = classifier.classify("What awards should I apply for?")
        
        assert intent == Intent.AWARD_SEARCH
    
    def test_classify_program_search(self):
        """Test classify detects program search intent."""
        from reasoning.routing import IntentClassifier, Intent
        
        classifier = IntentClassifier()
        intent, confidence = classifier.classify("What summer programs should I consider?")
        
        assert intent == Intent.PROGRAM_SEARCH
    
    def test_classify_crisis(self):
        """Test classify detects crisis intent."""
        from reasoning.routing import IntentClassifier, Intent
        
        classifier = IntentClassifier()
        intent, confidence = classifier.classify("I'm so stressed I can't do this anymore")
        
        assert intent == Intent.CRISIS
        assert confidence >= 0.9  # High confidence for crisis
    
    def test_classify_general_chat_default(self):
        """Test classify defaults to general chat."""
        from reasoning.routing import IntentClassifier, Intent
        
        classifier = IntentClassifier()
        intent, confidence = classifier.classify("Hello, how are you?")
        
        assert intent == Intent.GENERAL_CHAT
    
    def test_classify_with_context(self):
        """Test classify uses context to boost intents."""
        from reasoning.routing import IntentClassifier, Intent
        
        classifier = IntentClassifier()
        intent, confidence = classifier.classify(
            "What should I do next?",
            context={"current_task": "gameplan"},
        )
        
        # Should boost gameplan intent
        assert intent == Intent.GAMEPLAN or confidence > 0.5


class TestAgentRouter:
    """Tests for AgentRouter (A10)."""
    
    def test_router_importable(self):
        """Test AgentRouter can be imported."""
        from reasoning.routing import AgentRouter
        assert AgentRouter is not None
    
    def test_router_initialization(self):
        """Test AgentRouter can be initialized."""
        from reasoning.routing import AgentRouter
        router = AgentRouter()
        assert router is not None
    
    def test_route_returns_route_decision(self):
        """Test route returns RouteDecision."""
        from reasoning.routing import AgentRouter, RouteDecision
        
        router = AgentRouter()
        decision = router.route("Help me with my essay")
        
        assert isinstance(decision, RouteDecision)
    
    def test_route_decision_has_expected_fields(self):
        """Test RouteDecision has all expected fields."""
        from reasoning.routing import AgentRouter
        
        router = AgentRouter()
        decision = router.route("Help me with my essay")
        
        assert hasattr(decision, 'intent')
        assert hasattr(decision, 'confidence')
        assert hasattr(decision, 'target_agent')
        assert hasattr(decision, 'reasoning')
        assert hasattr(decision, 'context_to_pass')
        assert hasattr(decision, 'fallback_agent')
    
    def test_route_essay_to_essay_agent(self):
        """Test essay requests route to essay_agent."""
        from reasoning.routing import AgentRouter
        
        router = AgentRouter()
        decision = router.route("Help me with my college essay")
        
        assert decision.target_agent == "essay_agent"
    
    def test_route_awards_to_awards_agent(self):
        """Test award requests route to awards_agent."""
        from reasoning.routing import AgentRouter
        
        router = AgentRouter()
        decision = router.route("What awards should I apply for?")
        
        assert decision.target_agent == "awards_agent"
    
    def test_route_programs_to_programs_agent(self):
        """Test program requests route to programs_agent."""
        from reasoning.routing import AgentRouter
        
        router = AgentRouter()
        decision = router.route("Tell me about summer research programs")
        
        assert decision.target_agent == "programs_agent"
    
    def test_route_crisis_to_crisis_handler(self):
        """Test crisis messages route to crisis_handler."""
        from reasoning.routing import AgentRouter
        
        router = AgentRouter()
        decision = router.route("I feel hopeless and can't go on")
        
        assert decision.target_agent == "crisis_handler"
    
    def test_route_includes_fallback(self):
        """Test route includes fallback agent."""
        from reasoning.routing import AgentRouter
        
        router = AgentRouter()
        decision = router.route("Help me with awards")
        
        # Non-coaching agents should have coaching_agent as fallback
        if decision.target_agent != "coaching_agent":
            assert decision.fallback_agent == "coaching_agent"
    
    def test_register_agent(self):
        """Test registering an agent."""
        from reasoning.routing import AgentRouter
        from unittest.mock import Mock
        
        router = AgentRouter()
        mock_agent = Mock()
        
        router.register_agent("test_agent", mock_agent)
        
        assert "test_agent" in router._agents


class TestIntent:
    """Tests for Intent enum."""
    
    def test_intent_values(self):
        """Test Intent has all expected values."""
        from reasoning.routing import Intent
        
        assert Intent.ASSESSMENT.value == "assessment"
        assert Intent.GAMEPLAN.value == "gameplan"
        assert Intent.ACTIVITY_HELP.value == "activity_help"
        assert Intent.AWARD_SEARCH.value == "award_search"
        assert Intent.PROGRAM_SEARCH.value == "program_search"
        assert Intent.ESSAY_HELP.value == "essay_help"
        assert Intent.SCHOOL_RESEARCH.value == "school_research"
        assert Intent.DEADLINE_CHECK.value == "deadline_check"
        assert Intent.GENERAL_CHAT.value == "general_chat"
        assert Intent.CRISIS.value == "crisis"


class TestRouteDecision:
    """Tests for RouteDecision model."""
    
    def test_route_decision_importable(self):
        """Test RouteDecision can be imported."""
        from reasoning.routing import RouteDecision
        assert RouteDecision is not None
    
    def test_route_decision_creation(self):
        """Test creating a RouteDecision."""
        from reasoning.routing import RouteDecision, Intent
        
        decision = RouteDecision(
            intent=Intent.ESSAY_HELP,
            confidence=0.85,
            target_agent="essay_agent",
            reasoning="Detected essay help intent",
        )
        
        assert decision.intent == Intent.ESSAY_HELP
        assert decision.confidence == 0.85
        assert decision.target_agent == "essay_agent"


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_detect_intent_exists(self):
        """Test detect_intent convenience function exists."""
        from reasoning.routing import detect_intent
        assert detect_intent is not None
    
    def test_detect_intent_returns_tuple(self):
        """Test detect_intent returns tuple."""
        from reasoning.routing import detect_intent, Intent
        
        intent, confidence = detect_intent("Help me with my essay")
        
        assert isinstance(intent, Intent)
        assert isinstance(confidence, float)
    
    def test_route_message_exists(self):
        """Test route_message convenience function exists."""
        from reasoning.routing import route_message
        assert route_message is not None
    
    def test_route_message_returns_decision(self):
        """Test route_message returns RouteDecision."""
        from reasoning.routing import route_message, RouteDecision
        
        decision = route_message("Help me with my essay")
        
        assert isinstance(decision, RouteDecision)


class TestMultiAgentOrchestrator:
    """Tests for MultiAgentOrchestrator."""
    
    def test_orchestrator_importable(self):
        """Test MultiAgentOrchestrator can be imported."""
        from reasoning.routing import MultiAgentOrchestrator
        assert MultiAgentOrchestrator is not None
    
    def test_orchestrator_initialization(self):
        """Test MultiAgentOrchestrator can be initialized."""
        from reasoning.routing import MultiAgentOrchestrator, AgentRouter
        
        router = AgentRouter()
        orchestrator = MultiAgentOrchestrator(router)
        
        assert orchestrator is not None
    
    def test_orchestrator_has_workflows(self):
        """Test MultiAgentOrchestrator has predefined workflows."""
        from reasoning.routing import MultiAgentOrchestrator, AgentRouter
        
        router = AgentRouter()
        orchestrator = MultiAgentOrchestrator(router)
        
        assert "full_gameplan" in orchestrator._workflows
        assert "assessment" in orchestrator._workflows
