"""
Tests for G5: Human Shadow Mode Pattern
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.shadow import (
    HumanShadowManager,
    ShadowMode,
    ShadowProposal,
    ShadowReview,
    ShadowConfig,
    DEFAULT_SHADOW_CONFIGS,
)


class TestShadowTypes:
    """Tests for shadow type definitions."""

    def test_shadow_mode_values(self):
        """Test ShadowMode enum values."""
        assert ShadowMode.OFF == "off"
        assert ShadowMode.ADVISORY == "advisory"
        assert ShadowMode.REVIEW == "review"
        assert ShadowMode.APPROVAL == "approval"

    def test_shadow_proposal_creation(self):
        """Test ShadowProposal model creation."""
        proposal = ShadowProposal(
            proposal_id="test-123",
            profile_id="profile-456",
            agent_name="test_agent",
            proposal_type="message",
            proposed_content="Test content",
            shadow_mode=ShadowMode.ADVISORY,
            confidence_score=0.8,
        )
        assert proposal.proposal_id == "test-123"
        assert proposal.shadow_mode == ShadowMode.ADVISORY
        assert proposal.confidence_score == 0.8
        assert proposal.final_content is None

    def test_shadow_review_creation(self):
        """Test ShadowReview model creation."""
        review = ShadowReview(
            proposal_id="test-123",
            reviewer_id="coach-1",
            action="approve",
        )
        assert review.action == "approve"
        assert review.quality_rating is None

    def test_shadow_config_defaults(self):
        """Test ShadowConfig default values."""
        config = ShadowConfig()
        assert config.shadow_mode == ShadowMode.ADVISORY
        assert config.review_timeout_minutes == 60
        assert config.auto_proceed_on_timeout == True


class TestHumanShadowManager:
    """Tests for HumanShadowManager."""

    @pytest.fixture
    def manager(self):
        return HumanShadowManager()

    def test_manager_creation(self, manager):
        """Test manager creation with default configs."""
        assert manager is not None
        assert len(manager.configs) > 0

    def test_default_configs_exist(self):
        """Test default shadow configs are defined."""
        assert len(DEFAULT_SHADOW_CONFIGS) >= 1

    def test_get_shadow_mode_default(self, manager):
        """Get shadow mode returns default ADVISORY."""
        mode = manager.get_shadow_mode("profile-123", "test_agent")
        assert mode == ShadowMode.ADVISORY

    def test_get_shadow_mode_upgrade_to_review_new_student(self, manager):
        """Shadow mode upgrades to REVIEW for new students."""
        mode = manager.get_shadow_mode(
            "profile-123",
            "test_agent",
            {"session_count": 1},
        )
        assert mode == ShadowMode.REVIEW

    def test_get_shadow_mode_upgrade_to_review_low_confidence(self, manager):
        """Shadow mode upgrades to REVIEW for low confidence."""
        mode = manager.get_shadow_mode(
            "profile-123",
            "test_agent",
            {"confidence": 0.4},
        )
        assert mode == ShadowMode.REVIEW

    def test_get_shadow_mode_upgrade_to_approval_crisis(self, manager):
        """Shadow mode upgrades to APPROVAL for crisis."""
        mode = manager.get_shadow_mode(
            "profile-123",
            "test_agent",
            {"crisis_detected": True},
        )
        assert mode == ShadowMode.APPROVAL

    @pytest.mark.asyncio
    async def test_submit_proposal_creates_proposal(self, manager):
        """Submit proposal creates pending proposal."""
        proposal = await manager.submit_proposal(
            profile_id="test-profile",
            agent_name="test_agent",
            proposal_type="message",
            proposed_content="Hello, let me help you with your essay.",
            confidence_score=0.8,
        )

        assert proposal.proposal_id is not None
        assert proposal.profile_id == "test-profile"
        assert proposal.shadow_mode == ShadowMode.ADVISORY

    @pytest.mark.asyncio
    async def test_submit_proposal_with_context(self, manager):
        """Submit proposal with additional context."""
        proposal = await manager.submit_proposal(
            profile_id="test-profile",
            agent_name="test_agent",
            proposal_type="action",
            proposed_content="Update college list",
            student_message="I want to add MIT",
            relevant_context={"deadline": "2026-01-15"},
            agent_reasoning="MIT fits student's STEM profile",
            confidence_score=0.85,
        )

        assert proposal.student_message == "I want to add MIT"
        assert proposal.agent_reasoning == "MIT fits student's STEM profile"

    @pytest.mark.asyncio
    async def test_await_review_off_mode_returns_immediately(self, manager):
        """OFF mode returns immediately with original content."""
        proposal = ShadowProposal(
            proposal_id="test-123",
            profile_id="profile-456",
            agent_name="test_agent",
            proposal_type="message",
            proposed_content="Test content",
            shadow_mode=ShadowMode.OFF,
        )

        result = await manager.await_review(proposal)
        assert result.final_content == "Test content"

    @pytest.mark.asyncio
    async def test_await_review_advisory_mode_returns_immediately(self, manager):
        """ADVISORY mode returns immediately with original content."""
        proposal = ShadowProposal(
            proposal_id="test-123",
            profile_id="profile-456",
            agent_name="test_agent",
            proposal_type="message",
            proposed_content="Test content",
            shadow_mode=ShadowMode.ADVISORY,
        )

        result = await manager.await_review(proposal)
        assert result.final_content == "Test content"

    @pytest.mark.asyncio
    async def test_submit_review_approve(self, manager):
        """Submit review with approve action."""
        review = await manager.submit_review(
            proposal_id="test-123",
            reviewer_id="coach-1",
            action="approve",
        )

        assert review.action == "approve"
        assert review.reviewer_id == "coach-1"

    @pytest.mark.asyncio
    async def test_submit_review_modify(self, manager):
        """Submit review with modify action."""
        review = await manager.submit_review(
            proposal_id="test-123",
            reviewer_id="coach-1",
            action="modify",
            modified_content="Improved version of the message",
            modifications_description=["Fixed tone", "Added encouragement"],
            quality_rating=4,
            feedback_for_agent="Good start, but tone was too formal",
        )

        assert review.action == "modify"
        assert review.modified_content == "Improved version of the message"
        assert review.quality_rating == 4

    def test_find_config_global_default(self, manager):
        """Find config returns global default."""
        config = manager._find_config("any-profile", "any-agent")
        assert config is not None

    def test_check_condition_student_is_new(self, manager):
        """Check condition for new student."""
        assert manager._check_condition("student_is_new", {"session_count": 1}) == True
        assert manager._check_condition("student_is_new", {"session_count": 10}) == False

    def test_check_condition_high_stakes_action(self, manager):
        """Check condition for high stakes action."""
        assert manager._check_condition(
            "high_stakes_action",
            {"proposal_type": "submit_application"}
        ) == True
        assert manager._check_condition(
            "high_stakes_action",
            {"proposal_type": "general_chat"}
        ) == False

    def test_check_condition_low_confidence(self, manager):
        """Check condition for low confidence."""
        assert manager._check_condition("low_agent_confidence", {"confidence": 0.4}) == True
        assert manager._check_condition("low_agent_confidence", {"confidence": 0.8}) == False

    def test_apply_review_approve(self, manager):
        """Apply review with approve action."""
        proposal = ShadowProposal(
            proposal_id="test-123",
            profile_id="profile-456",
            agent_name="test_agent",
            proposal_type="message",
            proposed_content="Original content",
            shadow_mode=ShadowMode.REVIEW,
        )
        review = ShadowReview(
            proposal_id="test-123",
            reviewer_id="coach-1",
            action="approve",
        )

        result = manager._apply_review(proposal, review)
        assert result.final_content == "Original content"

    def test_apply_review_modify(self, manager):
        """Apply review with modify action."""
        proposal = ShadowProposal(
            proposal_id="test-123",
            profile_id="profile-456",
            agent_name="test_agent",
            proposal_type="message",
            proposed_content="Original content",
            shadow_mode=ShadowMode.REVIEW,
        )
        review = ShadowReview(
            proposal_id="test-123",
            reviewer_id="coach-1",
            action="modify",
            modified_content="Modified content",
        )

        result = manager._apply_review(proposal, review)
        assert result.final_content == "Modified content"

    def test_apply_review_reject(self, manager):
        """Apply review with reject action."""
        proposal = ShadowProposal(
            proposal_id="test-123",
            profile_id="profile-456",
            agent_name="test_agent",
            proposal_type="message",
            proposed_content="Original content",
            shadow_mode=ShadowMode.REVIEW,
        )
        review = ShadowReview(
            proposal_id="test-123",
            reviewer_id="coach-1",
            action="reject",
        )

        result = manager._apply_review(proposal, review)
        assert result.final_content is None
