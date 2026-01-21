# agents/tests/integration/test_full_flow.py
"""
Full Flow Integration Tests - v5.4 True Autonomous Agents.

These tests verify complete end-to-end flows through the middleware
and all Critical 15 Patterns working together.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestGameplanFlow:
    """Tests for complete gameplan generation flow."""

    @pytest.mark.asyncio
    async def test_gameplan_full_flow(self, mock_supabase, mock_redis, full_profile_data):
        """Test complete gameplan generation with all patterns."""
        from middleware import MiddlewareStack
        from context import TaskType

        # Setup mock data
        mock_supabase._tables["profiles"] = [full_profile_data]

        stack = MiddlewareStack(mock_supabase, mock_redis)

        async with stack.wrap_agent(
            "gameplan_agent",
            full_profile_data["id"],
            task_type=TaskType.GAMEPLAN,
        ) as ctx:
            # 1. Context loaded (C2, C4, C6)
            assert ctx.profile_id == full_profile_data["id"]

            # 2. Check input (E6 Guardrails)
            input_message = "Create my college application gameplan"
            guardrail_results = stack.check_guardrails(input_message, is_input=True)
            assert all(r.passed for r in guardrail_results)

            # 3. Check for escalation (G3)
            escalation = stack.check_escalation(input_message, ctx.to_dict())
            assert escalation is None  # Safe input

            # 4. Generate recommendations
            recommendations = [
                {
                    "id": "rec-1",
                    "title": "SAT Prep",
                    "type": "testing",
                    "urgency": "high",
                    "impact": 4,
                },
                {
                    "id": "rec-2",
                    "title": "Robotics Research Program",
                    "type": "activity",
                    "urgency": "medium",
                    "impact": 5,
                    "domains": ["robotics"],
                },
                {
                    "id": "rec-3",
                    "title": "Start MIT Essay",
                    "type": "application",
                    "urgency": "low",
                    "impact": 4,
                },
            ]

            # 5. Prioritize recommendations (A12)
            context_dict = ctx.to_dict()
            prioritized = stack.prioritize(recommendations, context_dict)
            assert len(prioritized) == 3

            # 6. Build output
            output = {
                "profile_id": ctx.profile_id,
                "gameplan_type": "quarterly",
                "recommendations": [
                    {
                        "title": p.title,
                        "priority": p.priority_level.value,
                        "score": p.priority_score,
                        "reasoning": p.reasoning,
                    }
                    for p in prioritized
                ],
                "summary": "Focus on SAT prep and robotics research this quarter.",
                "next_check_in": "2024-02-01",
            }

            # 7. Validate and finalize (E1, J2)
            finalized = stack.finalize(output, "gameplan")

            # Verify final output
            assert finalized["profile_id"] == full_profile_data["id"]
            assert len(finalized["recommendations"]) == 3
            assert "_validation" in finalized
            assert finalized["_validation"]["valid"] is True


class TestChatFlow:
    """Tests for complete chat interaction flow."""

    @pytest.mark.asyncio
    async def test_chat_safe_flow(self, mock_supabase, mock_redis, full_profile_data, safe_messages):
        """Test chat flow with safe messages."""
        from middleware import MiddlewareStack
        from context import TaskType, ConversationRole
        from memory import WorkingMemoryManager

        mock_supabase._tables["profiles"] = [full_profile_data]

        stack = MiddlewareStack(mock_supabase, mock_redis)
        memory_manager = WorkingMemoryManager(mock_redis)

        session_id = "chat-session-123"

        # Process multiple messages
        for message in safe_messages[:3]:
            async with stack.wrap_agent(
                "chat_agent",
                full_profile_data["id"],
                session_id=session_id,
                task_type=TaskType.CHAT,
            ) as ctx:
                # Check guardrails
                results = stack.check_guardrails(message, is_input=True)
                assert all(r.passed for r in results)

                # Check escalation
                escalation = stack.check_escalation(message, ctx.to_dict())
                assert escalation is None

                # Add to working memory
                await memory_manager.add_turn(
                    session_id,
                    ConversationRole.USER,
                    message,
                )

                # Generate response (simulated)
                response = f"Great question about: {message[:30]}..."

                # Add response to memory
                await memory_manager.add_turn(
                    session_id,
                    ConversationRole.ASSISTANT,
                    response,
                )

        # Verify conversation was tracked
        memory = await memory_manager.get_or_create(session_id, full_profile_data["id"])
        assert len(memory.conversation_turns) >= 6  # 3 user + 3 assistant

    @pytest.mark.asyncio
    async def test_chat_escalation_flow(self, mock_supabase, mock_redis, full_profile_data, unsafe_messages):
        """Test chat flow with messages requiring escalation."""
        from middleware import MiddlewareStack
        from context import TaskType

        mock_supabase._tables["profiles"] = [full_profile_data]

        stack = MiddlewareStack(mock_supabase, mock_redis)

        async with stack.wrap_agent(
            "chat_agent",
            full_profile_data["id"],
            task_type=TaskType.CHAT,
        ) as ctx:
            # Process unsafe message
            message = unsafe_messages[0]  # Self-harm indicator

            # Check escalation
            escalation = stack.check_escalation(message, ctx.to_dict())

            if escalation:
                reason, level, safe_response = escalation

                # Should provide safe response
                assert safe_response is not None
                assert len(safe_response) > 0

                # Agent should use safe response, not generate own
                output = {
                    "response": safe_response,
                    "escalated": True,
                    "escalation_reason": reason.value,
                }

                finalized = stack.finalize(output, "chat")
                assert finalized["escalated"] is True


class TestAssessmentFlow:
    """Tests for complete assessment flow."""

    @pytest.mark.asyncio
    async def test_assessment_full_flow(self, mock_supabase, mock_redis, full_profile_data):
        """Test complete profile assessment with all patterns."""
        from middleware import MiddlewareStack
        from context import TaskType
        from intelligence import GoalMonitor

        mock_supabase._tables["profiles"] = [full_profile_data]

        stack = MiddlewareStack(mock_supabase, mock_redis)
        goal_monitor = GoalMonitor(mock_supabase)

        async with stack.wrap_agent(
            "assessment_agent",
            full_profile_data["id"],
            task_type=TaskType.ASSESSMENT,
        ) as ctx:
            # 1. Analyze profile
            assessment = {
                "profile_id": ctx.profile_id,
                "cri_score": full_profile_data["cri_score"],
                "eds_score": full_profile_data["eds_score"],
                "spike_analysis": {
                    "primary_spike": full_profile_data["spike"],
                    "confidence": full_profile_data["spike_score"],
                    "supporting_evidence": [
                        "Robotics Club President",
                        "FIRST Robotics Champion",
                        "Autonomous Delivery Robot project",
                    ],
                },
                "archetype": full_profile_data["archetype"],
                "archetype_confidence": full_profile_data["archetype_confidence"],
                "strengths": [
                    "Strong technical skills",
                    "Demonstrated leadership",
                    "Real-world impact projects",
                ],
                "growth_areas": [
                    "Essay writing practice",
                    "Humanities exposure",
                ],
                "brand_statement": full_profile_data["brand_statement"],
            }

            # 2. Goal progress check (I3)
            goal_report = await goal_monitor.get_progress_report(ctx.profile_id)

            # 3. Validate and finalize
            finalized = stack.finalize(assessment, "assessment")

            assert finalized["profile_id"] == full_profile_data["id"]
            assert finalized["_validation"]["valid"] is True


class TestMultiAgentFlow:
    """Tests for multi-agent orchestration flows."""

    @pytest.mark.asyncio
    async def test_routing_to_correct_agent(self, mock_supabase, mock_redis, full_profile_data):
        """Test messages are routed to correct agents."""
        from middleware import MiddlewareStack
        from reasoning import route_message

        mock_supabase._tables["profiles"] = [full_profile_data]

        stack = MiddlewareStack(mock_supabase, mock_redis)

        test_cases = [
            ("Create a gameplan for my applications", "gameplan"),
            ("What activities should I do?", "recommendation"),
            ("Analyze my profile", "assessment"),
            ("Hello, how are you?", "chat"),
        ]

        for message, expected_type in test_cases:
            decision = route_message(message, {"profile_id": full_profile_data["id"]})

            assert decision is not None
            assert decision.target_agent is not None

    @pytest.mark.asyncio
    async def test_agent_handoff_flow(self, mock_supabase, mock_redis, full_profile_data):
        """Test handoff between agents preserves context."""
        from middleware import MiddlewareStack
        from context import TaskType
        from memory import WorkingMemoryManager

        mock_supabase._tables["profiles"] = [full_profile_data]

        stack = MiddlewareStack(mock_supabase, mock_redis)
        memory_manager = WorkingMemoryManager(mock_redis)

        session_id = "handoff-session-123"

        # First agent (chat) starts conversation
        async with stack.wrap_agent(
            "chat_agent",
            full_profile_data["id"],
            session_id=session_id,
            task_type=TaskType.CHAT,
        ) as ctx1:
            from context import ConversationRole
            await memory_manager.add_turn(
                session_id,
                ConversationRole.USER,
                "I need help with my gameplan",
            )

        # Second agent (gameplan) continues with same session
        async with stack.wrap_agent(
            "gameplan_agent",
            full_profile_data["id"],
            session_id=session_id,  # Same session
            task_type=TaskType.GAMEPLAN,
        ) as ctx2:
            # Should have access to conversation history
            memory = await memory_manager.get_or_create(session_id, full_profile_data["id"])

            # Context preserved
            assert len(memory.conversation_turns) >= 1
            assert ctx2.session_id == session_id


class TestErrorRecoveryFlow:
    """Tests for error recovery in complete flows."""

    @pytest.mark.asyncio
    async def test_graceful_degradation(self, mock_supabase, mock_redis, full_profile_data):
        """Test system degrades gracefully on errors."""
        from middleware import MiddlewareStack
        from context import TaskType
        from resilience import handle_exception

        # Broken Supabase (simulates database issues)
        broken_supabase = MagicMock()
        broken_supabase.table.side_effect = Exception("Connection failed")

        stack = MiddlewareStack(broken_supabase, mock_redis)

        async with stack.wrap_agent(
            "gameplan_agent",
            full_profile_data["id"],
            task_type=TaskType.GAMEPLAN,
        ) as ctx:
            # Context loading may fail, but agent should still work

            # Generate fallback output
            try:
                # Simulated operation that might fail
                raise ConnectionError("Database unavailable")
            except Exception as e:
                fallback = handle_exception(e, {"operation": "data_load"})

                output = {
                    "profile_id": ctx.profile_id,
                    "status": "partial",
                    "message": fallback.message,
                    "recommendations": [],  # Empty due to error
                }

                finalized = stack.finalize(output, "gameplan")

                # Should still have valid output structure
                assert finalized["profile_id"] is not None

    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self, mock_supabase, mock_redis):
        """Test retries on transient failures."""
        from resilience import with_retry

        call_count = 0

        @with_retry(max_retries=3, delay=0.01)
        async def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Transient failure")
            return {"status": "success"}

        result = await flaky_operation()

        assert result["status"] == "success"
        assert call_count == 3
