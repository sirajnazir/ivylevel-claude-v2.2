# agents/tests/test_handoff.py
"""
IvyQuest v13.2 - Handoff Protocol Unit Tests

Tests for:
- AgentHandoff - Handoff dataclass
- HandoffManager - Redis operations (with mock)
"""

import pytest
from datetime import datetime, timedelta
import json

from agents.agents.core.handoff import AgentHandoff, HandoffManager


class TestAgentHandoff:
    """Test AgentHandoff dataclass."""

    def test_creation(self):
        """Test basic handoff creation."""
        handoff = AgentHandoff(
            from_agent="assessment",
            to_agent="gameplan",
            profile_id="test-profile-123",
            timestamp=datetime.utcnow(),
            context={"archetype": "DoubleDown"},
            task="Create game plan based on assessment",
            reason="Assessment complete",
        )
        
        assert handoff.from_agent == "assessment"
        assert handoff.to_agent == "gameplan"
        assert handoff.profile_id == "test-profile-123"
        assert handoff.context["archetype"] == "DoubleDown"
        assert handoff.priority == "normal"  # Default

    def test_expiry_auto_set(self):
        """Test expiry is auto-set to 24 hours."""
        now = datetime.utcnow()
        handoff = AgentHandoff(
            from_agent="a",
            to_agent="b",
            profile_id="p",
            timestamp=now,
            context={},
            task="task",
            reason="reason",
        )
        
        assert handoff.expires_at is not None
        expected = now + timedelta(hours=24)
        # Allow 1 second tolerance
        diff = abs((handoff.expires_at - expected).total_seconds())
        assert diff < 1

    def test_is_expired_false(self):
        """Test not expired when fresh."""
        handoff = AgentHandoff(
            from_agent="a",
            to_agent="b",
            profile_id="p",
            timestamp=datetime.utcnow(),
            context={},
            task="task",
            reason="reason",
        )
        
        assert handoff.is_expired() is False

    def test_is_expired_true(self):
        """Test expired when past expiry."""
        handoff = AgentHandoff(
            from_agent="a",
            to_agent="b",
            profile_id="p",
            timestamp=datetime.utcnow() - timedelta(hours=25),
            context={},
            task="task",
            reason="reason",
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        
        assert handoff.is_expired() is True

    def test_time_until_expiry(self):
        """Test time until expiry calculation."""
        handoff = AgentHandoff(
            from_agent="a",
            to_agent="b",
            profile_id="p",
            timestamp=datetime.utcnow(),
            context={},
            task="task",
            reason="reason",
        )
        
        remaining = handoff.time_until_expiry()
        assert remaining is not None
        assert remaining.total_seconds() > 0
        assert remaining.total_seconds() <= 24 * 3600

    def test_add_decision(self):
        """Test adding decisions."""
        handoff = AgentHandoff(
            from_agent="a",
            to_agent="b",
            profile_id="p",
            timestamp=datetime.utcnow(),
            context={},
            task="task",
            reason="reason",
        )
        
        handoff.add_decision(
            decision="Use DoubleDown archetype",
            rationale="High spike indicators",
            confidence=0.85,
        )
        
        assert len(handoff.decisions_made) == 1
        assert handoff.decisions_made[0]["decision"] == "Use DoubleDown archetype"
        assert handoff.decisions_made[0]["confidence"] == 0.85

    def test_add_pending_action(self):
        """Test adding pending actions."""
        handoff = AgentHandoff(
            from_agent="a",
            to_agent="b",
            profile_id="p",
            timestamp=datetime.utcnow(),
            context={},
            task="task",
            reason="reason",
        )
        
        handoff.add_pending_action("Generate narrative", priority="high")
        handoff.add_pending_action("Review awards")
        
        assert len(handoff.pending_actions) == 2
        assert handoff.pending_actions[0]["action"] == "Generate narrative"
        assert handoff.pending_actions[0]["priority"] == "high"
        assert handoff.pending_actions[1]["priority"] == "normal"

    def test_to_dict(self):
        """Test serialization."""
        now = datetime.utcnow()
        handoff = AgentHandoff(
            from_agent="assessment",
            to_agent="gameplan",
            profile_id="test-123",
            timestamp=now,
            context={"key": "value"},
            task="Create plan",
            reason="Assessment done",
            priority="high",
        )
        
        data = handoff.to_dict()
        
        assert data["from_agent"] == "assessment"
        assert data["to_agent"] == "gameplan"
        assert data["profile_id"] == "test-123"
        assert data["context"] == {"key": "value"}
        assert data["priority"] == "high"
        assert "timestamp" in data
        assert "expires_at" in data

    def test_from_dict(self):
        """Test deserialization."""
        now = datetime.utcnow()
        data = {
            "from_agent": "a",
            "to_agent": "b",
            "profile_id": "p",
            "timestamp": now.isoformat(),
            "context": {"x": 1},
            "task": "task",
            "reason": "reason",
            "profile_snapshot": {"arch": "DD"},
            "decisions_made": [{"d": 1}],
            "pending_actions": [{"a": 1}],
            "priority": "urgent",
            "expires_at": (now + timedelta(hours=12)).isoformat(),
        }
        
        handoff = AgentHandoff.from_dict(data)
        
        assert handoff.from_agent == "a"
        assert handoff.context["x"] == 1
        assert handoff.profile_snapshot["arch"] == "DD"
        assert len(handoff.decisions_made) == 1
        assert handoff.priority == "urgent"

    def test_repr(self):
        """Test string representation."""
        handoff = AgentHandoff(
            from_agent="assessment",
            to_agent="gameplan",
            profile_id="p",
            timestamp=datetime.utcnow(),
            context={},
            task="This is a very long task description that should be truncated",
            reason="reason",
        )
        
        repr_str = repr(handoff)
        assert "assessment" in repr_str
        assert "gameplan" in repr_str
        assert "expired=" in repr_str


class MockRedis:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self.data = {}
    
    async def setex(self, key, ttl, value):
        self.data[key] = value
        
    async def get(self, key):
        return self.data.get(key)
    
    async def delete(self, key):
        if key in self.data:
            del self.data[key]
            return 1
        return 0
    
    async def scan(self, cursor, match, count):
        import fnmatch
        matches = [k for k in self.data.keys() if fnmatch.fnmatch(k, match)]
        return 0, matches


class TestHandoffManager:
    """Test HandoffManager with mock Redis."""

    @pytest.fixture
    def mock_redis(self):
        return MockRedis()

    @pytest.fixture
    def manager(self, mock_redis):
        return HandoffManager(mock_redis)

    @pytest.mark.asyncio
    async def test_create_handoff(self, manager):
        """Test creating a handoff."""
        handoff = await manager.create_handoff(
            from_agent="assessment",
            to_agent="gameplan",
            profile_id="test-profile-123",
            context={"archetype": "DoubleDown"},
            task="Create game plan based on assessment",
            reason="Assessment complete, ready for planning",
        )
        
        assert handoff.from_agent == "assessment"
        assert handoff.to_agent == "gameplan"
        assert handoff.profile_id == "test-profile-123"
        assert handoff.context["archetype"] == "DoubleDown"

    @pytest.mark.asyncio
    async def test_get_handoff_specific(self, manager):
        """Test getting a specific handoff."""
        # Create handoff
        await manager.create_handoff(
            from_agent="assessment",
            to_agent="gameplan",
            profile_id="test-profile-123",
            context={},
            task="Test task",
            reason="Test reason",
        )
        
        # Retrieve handoff
        retrieved = await manager.get_handoff(
            profile_id="test-profile-123",
            to_agent="gameplan",
            from_agent="assessment",
        )
        
        assert retrieved is not None
        assert retrieved.task == "Test task"

    @pytest.mark.asyncio
    async def test_get_handoff_any_source(self, manager):
        """Test getting handoff without specifying source."""
        # Create handoff
        await manager.create_handoff(
            from_agent="assessment",
            to_agent="gameplan",
            profile_id="p123",
            context={},
            task="Task from assessment",
            reason="Reason",
        )
        
        # Retrieve without specifying from_agent
        retrieved = await manager.get_handoff(
            profile_id="p123",
            to_agent="gameplan",
        )
        
        assert retrieved is not None
        assert retrieved.from_agent == "assessment"

    @pytest.mark.asyncio
    async def test_get_handoff_not_found(self, manager):
        """Test getting non-existent handoff."""
        retrieved = await manager.get_handoff(
            profile_id="nonexistent",
            to_agent="gameplan",
        )
        
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_acknowledge_handoff(self, manager, mock_redis):
        """Test acknowledging (deleting) a handoff."""
        # Create handoff
        await manager.create_handoff(
            from_agent="assessment",
            to_agent="gameplan",
            profile_id="p123",
            context={},
            task="Task",
            reason="Reason",
        )
        
        # Acknowledge
        result = await manager.acknowledge_handoff(
            profile_id="p123",
            from_agent="assessment",
            to_agent="gameplan",
        )
        assert result is True
        
        # Verify gone
        retrieved = await manager.get_handoff(
            profile_id="p123",
            to_agent="gameplan",
        )
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_acknowledge_nonexistent(self, manager):
        """Test acknowledging non-existent handoff."""
        result = await manager.acknowledge_handoff(
            profile_id="fake",
            from_agent="a",
            to_agent="b",
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_get_pending_handoffs(self, manager):
        """Test getting all pending handoffs."""
        # Create multiple handoffs
        await manager.create_handoff(
            from_agent="assessment",
            to_agent="gameplan",
            profile_id="p123",
            context={},
            task="Task 1",
            reason="Reason 1",
        )
        await manager.create_handoff(
            from_agent="gameplan",
            to_agent="opportunity",
            profile_id="p123",
            context={},
            task="Task 2",
            reason="Reason 2",
        )
        
        # Get all pending
        pending = await manager.get_pending_handoffs("p123")
        
        assert len(pending) == 2

    @pytest.mark.asyncio
    async def test_get_handoffs_from_agent(self, manager):
        """Test getting handoffs from specific agent."""
        # Create handoffs from different agents
        await manager.create_handoff(
            from_agent="assessment",
            to_agent="gameplan",
            profile_id="p123",
            context={},
            task="From assessment 1",
            reason="Reason",
        )
        await manager.create_handoff(
            from_agent="assessment",
            to_agent="narrative",
            profile_id="p123",
            context={},
            task="From assessment 2",
            reason="Reason",
        )
        await manager.create_handoff(
            from_agent="gameplan",
            to_agent="opportunity",
            profile_id="p123",
            context={},
            task="From gameplan",
            reason="Reason",
        )
        
        # Get only from assessment
        from_assessment = await manager.get_handoffs_from_agent(
            "p123", "assessment"
        )
        
        assert len(from_assessment) == 2
        for h in from_assessment:
            assert h.from_agent == "assessment"

    @pytest.mark.asyncio
    async def test_handoff_round_trip(self, manager):
        """Test complete handoff round trip."""
        # 1. Create handoff
        original = await manager.create_handoff(
            from_agent="assessment",
            to_agent="gameplan",
            profile_id="profile-xyz",
            context={"archetype": "DoubleDown", "spike_score": 0.85},
            task="Create comprehensive game plan",
            reason="Assessment reveals high spike potential",
            profile_snapshot={"name": "Test Student"},
            decisions_made=[{"decision": "DoubleDown archetype", "confidence": 0.9}],
            pending_actions=[{"action": "Identify top 3 opportunities"}],
            priority="high",
        )
        
        # 2. Retrieve handoff
        retrieved = await manager.get_handoff(
            profile_id="profile-xyz",
            to_agent="gameplan",
        )
        
        # 3. Verify all data preserved
        assert retrieved.from_agent == "assessment"
        assert retrieved.to_agent == "gameplan"
        assert retrieved.context["spike_score"] == 0.85
        assert retrieved.profile_snapshot["name"] == "Test Student"
        assert len(retrieved.decisions_made) == 1
        assert retrieved.priority == "high"
        
        # 4. Acknowledge
        result = await manager.acknowledge_handoff(
            profile_id="profile-xyz",
            from_agent="assessment",
            to_agent="gameplan",
        )
        assert result is True
        
        # 5. Verify gone
        final = await manager.get_handoff(
            profile_id="profile-xyz",
            to_agent="gameplan",
        )
        assert final is None
