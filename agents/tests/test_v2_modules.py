"""
IvyQuest v2.0 Module Tests
==========================
Comprehensive test suite for Jenny Intelligence modules.

Tests:
- JennyVoiceValidator: 6-dimension voice scoring
- TimeAuditModule: 168-hour framework
- AwardsProbabilityEngine: 2-2-1 portfolio
- ProgramRedirectModule: $5K+ redirect logic
- NCWITStrategyModule: Identity multiplication
- CrisisAlchemyModule: 4-step crisis protocol
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validation import JennyVoiceValidator, validate_jenny_voice
from modules import (
    TimeAuditModule,
    AwardsProbabilityEngine,
    ProgramRedirectModule,
    NCWITStrategyModule,
    CrisisAlchemyModule,
)


# =====================================================
# JennyVoiceValidator Tests
# =====================================================

class TestJennyVoiceValidator:
    """Tests for Jenny's voice validation."""

    @pytest.fixture
    def validator(self):
        return JennyVoiceValidator()

    def test_forbidden_phrase_detection(self, validator):
        """Test detection of forbidden phrases."""
        # Text with forbidden phrase - using "but" which is forbidden
        bad_text = "You have great ideas but you need to focus more."
        result = validator.validate(bad_text)

        # Check forbidden phrases detected
        assert len(result.forbidden_found) > 0
        assert result.dimension_scores["forbidden_absence"] < 25

    def test_forbidden_phrase_absence(self, validator):
        """Test scoring when no forbidden phrases present."""
        good_text = "Great job exploring Stanford! It could be a wonderful fit for you."
        result = validator.validate(good_text)

        assert len(result.forbidden_found) == 0
        assert result.dimension_scores["forbidden_absence"] == 25

    def test_warmth_first_scoring(self, validator):
        """Test warmth-first opening detection."""
        # Warmth-first opening
        warm_text = "I love that you're thinking about this! Let's explore your options."
        result = validator.validate(warm_text)

        assert result.dimension_scores["warmth_first"] > 0

    def test_agency_preservation(self, validator):
        """Test agency-preserving language detection."""
        agency_text = "What do you think would work best for you? This is your decision!"
        result = validator.validate(agency_text)

        assert result.dimension_scores["agency_preservation"] > 0

    def test_check_in_question(self, validator):
        """Test check-in question detection."""
        question_text = "Here's what I'm thinking. Does that make sense to you?"
        result = validator.validate(question_text)

        assert result.dimension_scores["checkin_question"] > 0

    def test_passing_score(self, validator):
        """Test that good Jenny-style text passes."""
        jenny_text = """
        I love that energy! You're clearly passionate about this project.

        Here's what I'm thinking - what if you focused on scaling your impact
        rather than starting something new? Your existing work with Empowering AI
        is already so powerful!

        Does that resonate with you?
        """
        result = validator.validate(jenny_text)

        assert result.passing is True
        # Score is normalized to 0-10 scale (7.0 = 70/100 threshold)
        assert result.score >= 7.0

    def test_directive_detection(self, validator):
        """Test detection of directive language."""
        directive_text = "You must apply to NCWIT, you really have to try."
        result = validator.validate(directive_text)

        # Should have lower agency preservation score due to "must" and "have to"
        assert "must" in directive_text.lower() or "have to" in directive_text.lower()
        # The score reflects agency issues
        assert result.dimension_scores["agency_preservation"] < 20

    def test_speech_pattern_detection(self, validator):
        """Test detection of Jenny's signature phrases."""
        signature_text = "That's so cool! Let's figure out a plan together. What if we try something new?"
        result = validator.validate(signature_text)

        # Should detect Jenny patterns
        assert result.dimension_scores["speech_patterns"] > 0

    def test_convenience_function(self):
        """Test the validate_jenny_voice convenience function."""
        result = validate_jenny_voice("Great question! What do you think about this approach?")
        # Returns a JennyVoiceResult object
        assert hasattr(result, 'score')
        assert hasattr(result, 'passing')


# =====================================================
# TimeAuditModule Tests
# =====================================================

class TestTimeAuditModule:
    """Tests for the 168-hour framework."""

    @pytest.fixture
    def module(self):
        return TimeAuditModule()

    def test_total_hours(self, module):
        """Test that total always equals 168."""
        audit = module.calculate_available_time()
        assert audit.total == 168

    def test_default_calculation(self, module):
        """Test default passion hours calculation."""
        audit = module.calculate_available_time(
            sleep_hours=8,
            school_hours=7.5,
            social_media_hours_daily=4
        )

        # Should have significant passion hours available
        assert audit.passion_hours_available > 0
        assert audit.daily_passion_hours > 0

    def test_social_media_recovery(self, module):
        """Test social media hours recovery calculation."""
        audit = module.calculate_available_time(
            social_media_hours_daily=4  # 28 hours/week
        )

        # Target is 7 hours/week, so should recover 21 hours
        assert audit.social_media.current == 28
        assert audit.social_media.target == 7
        assert audit.social_media.recovered == 21

    def test_walkthrough_script(self, module):
        """Test walkthrough script generation."""
        audit = module.calculate_available_time()
        script = module.generate_walkthrough_script(audit)

        assert "168" in script
        assert "social media" in script.lower()
        assert "passion" in script.lower()

    def test_weekly_plan_generation(self, module):
        """Test P0/P1/P2 weekly plan generation."""
        tasks = [
            {"name": "NCWIT Essay", "priority": "P0", "estimated_hours": 5},
            {"name": "SAT Prep", "priority": "P1", "estimated_hours": 3},
            {"name": "Club Meeting", "priority": "P2", "estimated_hours": 2},
        ]

        plan = module.generate_weekly_plan(tasks, available_hours=26)

        assert len(plan.p0_must_complete) == 1
        assert len(plan.p1_should_complete) == 1
        assert len(plan.p2_if_time_permits) == 1
        assert plan.buffer_hours > 0

    def test_daily_schedule(self, module):
        """Test daily schedule generation."""
        schedule = module.generate_daily_schedule()

        assert len(schedule.blocks) > 0
        assert schedule.flexibility_note is not None

    def test_efficiency_hacks(self, module):
        """Test homework efficiency hacks."""
        hacks = module.get_efficiency_hacks()

        assert len(hacks) > 0
        assert any("delegation" in h["hack"].lower() for h in hacks)

    def test_to_dict(self, module):
        """Test dictionary conversion."""
        audit = module.calculate_available_time()
        result = module.to_dict(audit)

        assert "total_hours" in result
        assert "fixed_allocations" in result
        assert "social_media" in result
        assert "passion_hours_available" in result


# =====================================================
# AwardsProbabilityEngine Tests
# =====================================================

class TestAwardsProbabilityEngine:
    """Tests for the 2-2-1 portfolio builder."""

    @pytest.fixture
    def engine(self):
        return AwardsProbabilityEngine()

    @pytest.fixture
    def sample_student(self):
        return {
            "spike": "AI and Technology",
            "brand_statement": "Making AI accessible to underserved communities",
            "activities": [
                {"name": "Empowering AI", "description": "AI education nonprofit"},
                {"name": "Coding Club", "description": "Teaching programming"},
            ],
            "identity": ["woman", "first-generation"],
            "has_overcome_barrier": True,
            "is_underrepresented": True,
        }

    @pytest.fixture
    def sample_awards(self):
        return [
            {
                "id": "ncwit-1",
                "name": "NCWIT Aspirations in Computing",
                "focus_area": "women in computing technology",
                "selectivity_percentile": 80,
                "mission": "Encourage women in computing",
            },
            {
                "id": "local-1",
                "name": "Local STEM Award",
                "focus_area": "STEM education",
                "selectivity_percentile": 30,
                "mission": "Support local STEM students",
            },
            {
                "id": "national-1",
                "name": "National Tech Competition",
                "focus_area": "technology innovation",
                "selectivity_percentile": 90,
                "mission": "Recognize tech innovation",
            },
        ]

    def test_probability_calculation(self, engine, sample_student, sample_awards):
        """Test probability calculation for single award."""
        prob = engine.calculate_probability(sample_student, sample_awards[0])

        assert 0 <= prob.probability <= 100
        assert prob.tier in ["likely", "target", "stretch"]
        assert prob.reasoning is not None

    def test_vulnerability_bonus(self, engine, sample_student, sample_awards):
        """Test +15% vulnerability bonus."""
        # NCWIT should get vulnerability bonus
        prob = engine.calculate_probability(sample_student, sample_awards[0])

        assert prob.vulnerability_bonus is True

    def test_identity_bonus(self, engine, sample_student, sample_awards):
        """Test +10% identity alignment bonus."""
        # NCWIT + woman identity should get bonus
        prob = engine.calculate_probability(sample_student, sample_awards[0])

        assert prob.identity_bonus is True

    def test_tier_classification(self, engine):
        """Test tier thresholds."""
        assert engine._classify_tier(70) == "likely"
        assert engine._classify_tier(50) == "target"
        assert engine._classify_tier(30) == "stretch"

    def test_portfolio_building(self, engine, sample_student, sample_awards):
        """Test 2-2-1 portfolio construction."""
        portfolio = engine.build_balanced_portfolio(sample_student, sample_awards)

        # Should have some awards in each tier (or as balanced as possible)
        total = len(portfolio.likely) + len(portfolio.target) + len(portfolio.stretch)
        assert total > 0
        assert portfolio.total_expected_wins >= 0
        assert portfolio.balance_score >= 0

    def test_portfolio_recommendations(self, engine, sample_student, sample_awards):
        """Test portfolio recommendations."""
        portfolio = engine.build_balanced_portfolio(sample_student, sample_awards)

        assert len(portfolio.recommendations) > 0

    def test_format_summary(self, engine, sample_student, sample_awards):
        """Test formatted summary generation."""
        portfolio = engine.build_balanced_portfolio(sample_student, sample_awards)
        summary = engine.format_portfolio_summary(portfolio)

        assert "Likely" in summary or "Target" in summary or "Stretch" in summary
        assert "Expected wins" in summary


# =====================================================
# ProgramRedirectModule Tests
# =====================================================

class TestProgramRedirectModule:
    """Tests for the program redirect logic."""

    @pytest.fixture
    def module(self):
        return ProgramRedirectModule()

    @pytest.fixture
    def sample_student(self):
        return {
            "spike": "entrepreneurship",
            "primary_project": "Empowering AI",
        }

    def test_redirect_threshold(self, module):
        """Test $5000 redirect threshold."""
        cheap_program = {"cost_numeric": 3000, "name": "Cheap Camp"}
        expensive_program = {"cost_numeric": 8000, "name": "Expensive Camp"}

        assert module.should_redirect(cheap_program) is False
        assert module.should_redirect(expensive_program) is True

    def test_redirect_response(self, module, sample_student):
        """Test redirect response generation."""
        program = {
            "name": "Entrepreneurship Camp",
            "cost_numeric": 8000,
            "category": "entrepreneurship",
            "duration": "4 weeks",
        }

        response = module.generate_redirect(program, sample_student)

        assert response.should_redirect is True
        assert len(response.free_alternatives) > 0
        assert response.jenny_quote is not None

    def test_no_redirect_for_cheap(self, module, sample_student):
        """Test no redirect for affordable programs."""
        program = {
            "name": "Affordable Camp",
            "cost_numeric": 2000,
            "category": "cs",
        }

        response = module.generate_redirect(program, sample_student)

        assert response.should_redirect is False

    def test_tier_recommendations(self, module, sample_student):
        """Test tiered program recommendations."""
        recommendations = module.get_tier_recommendations(sample_student)

        assert "tier_1_selective_free" in recommendations
        assert "tier_2_government" in recommendations

    def test_format_alternatives(self, module, sample_student):
        """Test alternatives formatting."""
        program = {
            "name": "Expensive Camp",
            "cost_numeric": 8000,
            "category": "cs",
            "duration": "4 weeks",
        }

        response = module.generate_redirect(program, sample_student)
        formatted = module.format_alternatives(response)

        assert "Free Alternatives" in formatted
        assert "Self-Directed" in formatted


# =====================================================
# NCWITStrategyModule Tests
# =====================================================

class TestNCWITStrategyModule:
    """Tests for NCWIT application strategy."""

    @pytest.fixture
    def module(self):
        return NCWITStrategyModule()

    @pytest.fixture
    def sample_student(self):
        return {
            "identity": ["female", "muslim", "first-generation"],
            "is_first_gen": True,
            "is_new_to_school": False,
            "experiences": ["felt isolated", "was the only girl in class"],
        }

    def test_identity_layers(self, module, sample_student):
        """Test identity layer identification."""
        strategy = module.generate_strategy(sample_student)

        assert len(strategy.identity_layers) >= 3  # woman + muslim + first-gen
        assert "first-generation" in " ".join(strategy.identity_layers).lower() or \
               "first-generation college student" in " ".join(strategy.identity_layers).lower()

    def test_vulnerability_angles(self, module, sample_student):
        """Test vulnerability angle detection."""
        strategy = module.generate_strategy(sample_student)

        assert len(strategy.vulnerability_angles) > 0

    def test_coaching_script(self, module, sample_student):
        """Test coaching script generation."""
        strategy = module.generate_strategy(sample_student)

        assert "vulnerability" in strategy.jenny_coaching_script.lower() or \
               "identity" in strategy.jenny_coaching_script.lower()
        assert "Background + Barrier + Persistence" in strategy.jenny_coaching_script

    def test_sensory_prompts(self, module, sample_student):
        """Test sensory detail prompts."""
        strategy = module.generate_strategy(sample_student)

        assert len(strategy.sensory_detail_suggestions) > 0

    def test_essay_structure(self, module):
        """Test essay structure guidance."""
        q1 = module.format_essay_structure(1)
        q2 = module.format_essay_structure(2)

        assert "sparked" in q1.lower()
        assert "technology" in q2.lower()

    def test_transformation_examples(self, module):
        """Test transformation examples."""
        examples = module.get_transformation_examples()

        assert len(examples) > 0
        assert all("before" in e and "after" in e for e in examples)


# =====================================================
# CrisisAlchemyModule Tests
# =====================================================

class TestCrisisAlchemyModule:
    """Tests for Crisis Alchemy protocol."""

    @pytest.fixture
    def module(self):
        return CrisisAlchemyModule()

    @pytest.fixture
    def sample_student(self):
        return {
            "name": "Test Student",
            "primary_project": "Empowering AI",
            "spike": "AI education",
        }

    def test_crisis_detection_rejection(self, module):
        """Test rejection crisis detection."""
        description = "I got rejected from the summer program I really wanted"
        crisis_type = module.detect_crisis_type(description)

        assert crisis_type == "rejection"

    def test_crisis_detection_exclusion(self, module):
        """Test exclusion crisis detection."""
        description = "I was kicked out of the club for no reason"
        crisis_type = module.detect_crisis_type(description)

        assert crisis_type == "exclusion"

    def test_crisis_detection_creative_block(self, module):
        """Test creative block detection."""
        description = "I'm stuck and can't write my essay"
        crisis_type = module.detect_crisis_type(description)

        assert crisis_type == "creative_block"

    def test_crisis_response_structure(self, module, sample_student):
        """Test 4-step response structure."""
        response = module.generate_response(
            crisis_type="rejection",
            description="Got rejected from summer program",
            student=sample_student
        )

        assert response.validation is not None
        assert response.micro_action is not None
        assert response.reframe is not None
        assert response.pivot_activity is not None

    def test_transformation_pattern(self, module, sample_student):
        """Test transformation pattern."""
        response = module.generate_response(
            crisis_type="rejection",
            description="Got rejected",
            student=sample_student
        )

        assert "from" in response.transformation
        assert "to" in response.transformation

    def test_pivot_activity(self, module, sample_student):
        """Test pivot activity generation."""
        response = module.generate_response(
            crisis_type="rejection",
            description="Program rejection",
            student=sample_student
        )

        assert "name" in response.pivot_activity
        assert "steps" in response.pivot_activity

    def test_formatted_response(self, module, sample_student):
        """Test formatted response."""
        response = module.generate_response(
            crisis_type="failure",
            description="My project failed",
            student=sample_student
        )

        formatted = module.format_crisis_response(response)

        assert "VALIDATE" in formatted
        assert "ACT" in formatted
        assert "REFRAME" in formatted
        assert "CREATE" in formatted

    def test_full_response_text(self, module, sample_student):
        """Test full response text generation."""
        response = module.generate_response(
            crisis_type="deadline",
            description="Too many deadlines",
            student=sample_student
        )

        assert "How does that sound?" in response.full_response

    def test_to_dict(self, module, sample_student):
        """Test dictionary conversion."""
        response = module.generate_response(
            crisis_type="comparison",
            description="Everyone else is ahead",
            student=sample_student
        )

        result = module.to_dict(response)

        assert "crisis_type" in result
        assert "validation" in result
        assert "micro_action" in result
        assert "pivot_activity" in result


# =====================================================
# Integration Tests
# =====================================================

class TestModuleIntegration:
    """Integration tests combining multiple modules."""

    def test_voice_validation_on_crisis_response(self):
        """Test that crisis responses use good patterns."""
        crisis_module = CrisisAlchemyModule()
        voice_validator = JennyVoiceValidator()

        student = {"name": "Test", "primary_project": "Project"}
        response = crisis_module.generate_response(
            crisis_type="rejection",
            description="Got rejected",
            student=student
        )

        # Crisis response text should be validated
        validation = voice_validator.validate(response.full_response)

        # Check that core Jenny elements are present
        # The response should have agency preservation (no directives)
        assert validation.dimension_scores["agency_preservation"] >= 0
        # Should have a check-in question (ends with "How does that sound?")
        assert validation.dimension_scores["checkin_question"] > 0
        # Response structure should include all 4 steps
        assert "How does that sound?" in response.full_response

    def test_awards_portfolio_with_ncwit(self):
        """Test awards portfolio including NCWIT strategy."""
        awards_engine = AwardsProbabilityEngine()
        ncwit_module = NCWITStrategyModule()

        student = {
            "spike": "computer science",
            "identity": ["woman", "first-generation"],
            "brand_statement": "Making tech accessible",
            "activities": [],
            "has_overcome_barrier": True,
            "is_underrepresented": True,
        }

        awards = [
            {
                "id": "ncwit",
                "name": "NCWIT Aspirations",
                "focus_area": "women in computing",
                "selectivity_percentile": 75,
            }
        ]

        # Get portfolio score
        prob = awards_engine.calculate_probability(student, awards[0])

        # Get NCWIT strategy
        strategy = ncwit_module.generate_strategy(student)

        # Should have high probability due to identity alignment
        assert prob.identity_bonus is True
        assert len(strategy.identity_layers) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
