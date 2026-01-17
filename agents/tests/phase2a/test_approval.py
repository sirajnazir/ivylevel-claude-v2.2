"""
Tests for G2: Approval Gates Pattern
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.approval import (
    ApprovalGateManager,
    ApprovalCategory,
    ApprovalUrgency,
    ApprovalStatus,
    ApprovalRequest,
    ApprovalDecision,
    ApprovalRule,
    DEFAULT_APPROVAL_RULES,
)


class TestApprovalTypes:
    """Tests for approval type definitions."""

    def test_approval_category_values(self):
        """Test ApprovalCategory enum values."""
        assert ApprovalCategory.STRATEGIC == "strategic"
        assert ApprovalCategory.CONTENT == "content"
        assert ApprovalCategory.FINANCIAL == "financial"
        assert ApprovalCategory.CRISIS == "crisis"
        assert ApprovalCategory.DEADLINE == "deadline"

    def test_approval_urgency_values(self):
        """Test ApprovalUrgency enum values."""
        assert ApprovalUrgency.IMMEDIATE == "immediate"
        assert ApprovalUrgency.SAME_DAY == "same_day"
        assert ApprovalUrgency.STANDARD == "standard"
        assert ApprovalUrgency.ADVISORY == "advisory"

    def test_approval_status_values(self):
        """Test ApprovalStatus enum values."""
        assert ApprovalStatus.PENDING == "pending"
        assert ApprovalStatus.APPROVED == "approved"
        assert ApprovalStatus.REJECTED == "rejected"
        assert ApprovalStatus.EXPIRED == "expired"
        assert ApprovalStatus.WITHDRAWN == "withdrawn"

    def test_approval_request_creation(self):
        """Test ApprovalRequest model creation."""
        request = ApprovalRequest(
            request_id="test-123",
            profile_id="profile-456",
            agent_name="test_agent",
            category=ApprovalCategory.STRATEGIC,
            action_type="change_college_list",
            action_description="Add Stanford to list",
            reason="Strategic action",
            agent_confidence=0.7,
        )
        assert request.request_id == "test-123"
        assert request.status == ApprovalStatus.PENDING
        assert request.agent_confidence == 0.7

    def test_approval_decision_creation(self):
        """Test ApprovalDecision model creation."""
        decision = ApprovalDecision(
            request_id="test-123",
            status=ApprovalStatus.APPROVED,
            reviewer_id="coach-1",
            reviewer_role="coach",
            decision_reason="Looks good",
        )
        assert decision.status == ApprovalStatus.APPROVED
        assert decision.reviewer_id == "coach-1"

    def test_approval_rule_creation(self):
        """Test ApprovalRule model creation."""
        rule = ApprovalRule(
            rule_id="test-rule",
            action_pattern="submit_*",
            category=ApprovalCategory.CONTENT,
            urgency=ApprovalUrgency.IMMEDIATE,
            description="Test rule",
        )
        assert rule.min_confidence_bypass == 1.0
        assert rule.enabled == True


class TestApprovalGateManager:
    """Tests for ApprovalGateManager."""

    @pytest.fixture
    def manager(self):
        return ApprovalGateManager()

    def test_manager_creation(self, manager):
        """Test manager creation with default rules."""
        assert manager is not None
        assert len(manager.rules) > 0

    def test_default_rules_exist(self):
        """Test default approval rules are defined."""
        assert len(DEFAULT_APPROVAL_RULES) >= 5
        rule_ids = [r.rule_id for r in DEFAULT_APPROVAL_RULES]
        assert "strategic_college_list" in rule_ids
        assert "crisis_mental_health" in rule_ids

    def test_check_requires_approval_strategic(self, manager):
        """Strategic actions require approval."""
        rule = manager.check_requires_approval("change_college_list")
        assert rule is not None
        assert rule.category == ApprovalCategory.STRATEGIC

    def test_check_requires_approval_crisis(self, manager):
        """Crisis actions require immediate approval."""
        rule = manager.check_requires_approval("crisis_response")
        assert rule is not None
        assert rule.category == ApprovalCategory.CRISIS
        assert rule.urgency == ApprovalUrgency.IMMEDIATE

    def test_check_requires_approval_high_confidence_bypass(self, manager):
        """High confidence can bypass approval."""
        # change_spike has min_confidence_bypass=0.95
        rule = manager.check_requires_approval(
            "change_spike",
            agent_confidence=0.98,
        )
        # Should bypass because confidence > 0.95
        assert rule is None

    def test_check_requires_approval_low_confidence_needs_approval(self, manager):
        """Low confidence needs approval."""
        rule = manager.check_requires_approval(
            "change_spike",
            agent_confidence=0.7,
        )
        assert rule is not None

    def test_check_requires_approval_unknown_action(self, manager):
        """Unknown actions don't require approval."""
        rule = manager.check_requires_approval("some_random_action")
        assert rule is None

    @pytest.mark.asyncio
    async def test_request_approval_creates_request(self, manager):
        """Request approval creates pending request."""
        rule = manager.check_requires_approval("change_college_list")

        request = await manager.request_approval(
            profile_id="test-profile",
            agent_name="test_agent",
            action_type="change_college_list",
            action_description="Add Stanford to list",
            action_payload={"school": "Stanford"},
            rule=rule,
            agent_confidence=0.7,
        )

        assert request.status == ApprovalStatus.PENDING
        assert request.profile_id == "test-profile"
        assert request.category == ApprovalCategory.STRATEGIC
        assert request.expires_at is not None

    @pytest.mark.asyncio
    async def test_submit_decision_updates_status(self, manager):
        """Submitting decision updates request status."""
        rule = manager.check_requires_approval("change_college_list")
        request = await manager.request_approval(
            profile_id="test-profile",
            agent_name="test_agent",
            action_type="change_college_list",
            action_description="Test",
            action_payload={},
            rule=rule,
        )

        decision = await manager.submit_decision(
            request_id=request.request_id,
            approved=True,
            reviewer_id="coach-1",
            reviewer_role="coach",
            reason="Looks good",
        )

        assert decision.status == ApprovalStatus.APPROVED
        assert decision.reviewer_id == "coach-1"

    @pytest.mark.asyncio
    async def test_submit_decision_rejected(self, manager):
        """Submitting rejected decision."""
        rule = manager.check_requires_approval("submit_application")
        request = await manager.request_approval(
            profile_id="test-profile",
            agent_name="test_agent",
            action_type="submit_application",
            action_description="Submit app",
            action_payload={},
            rule=rule,
        )

        decision = await manager.submit_decision(
            request_id=request.request_id,
            approved=False,
            reviewer_id="coach-1",
            reviewer_role="coach",
            reason="Not ready yet",
        )

        assert decision.status == ApprovalStatus.REJECTED

    def test_get_pending_requests_empty(self, manager):
        """Get pending requests returns empty initially."""
        requests = manager.get_pending_requests()
        assert requests == []

    @pytest.mark.asyncio
    async def test_get_pending_requests_with_filter(self, manager):
        """Get pending requests with filters."""
        rule = manager.check_requires_approval("change_college_list")
        await manager.request_approval(
            profile_id="test-profile",
            agent_name="test_agent",
            action_type="change_college_list",
            action_description="Test",
            action_payload={},
            rule=rule,
        )

        requests = manager.get_pending_requests(profile_id="test-profile")
        assert len(requests) == 1

        requests = manager.get_pending_requests(profile_id="other-profile")
        assert len(requests) == 0

    def test_evaluate_condition_simple(self, manager):
        """Test simple condition evaluation."""
        assert manager._evaluate_condition("key=value", {"key": "value"}) == True
        assert manager._evaluate_condition("key=value", {"key": "other"}) == False
        assert manager._evaluate_condition("key=value", {}) == False
