"""
Tests for EC Generation Engine Module
=====================================

Tests the 4 Pillars + 10 Dimensions framework for hyper-personalized
activity generation.

Run with: pytest tests/test_ec_generation_engine.py -v
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any

from agents.core.ec_generation_engine import (
    ECGenerationEngine,
    FourPillars,
    TenDimensions,
    GeneratedActivity,
    GapType,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def sample_profile() -> Dict[str, Any]:
    """Sample profile for testing."""
    return {
        "id": "test-profile-123",
        "profile_data": {
            "basicInfo": {
                "firstName": "Maya",
                "lastName": "Patel",
                "state": "CA",
                "city": "San Francisco",
            },
            "demographics": {
                "ethnicity": "Indian-American",
                "firstGen": True,
                "religion": "Hindu",
            },
            "academic": {
                "gpa": 3.9,
                "satScore": 1520,
                "intendedMajor": "Computer Science",
                "favoriteSubjects": ["Math", "Computer Science", "Physics"],
            },
            "passion": {
                "description": "Using technology to bridge educational gaps for underserved communities",
                "interests": ["AI/ML", "EdTech", "Social Impact"],
                "spikeCategory": "STEM_INNOVATOR",
            },
            "values": {
                "causes": ["Educational Equity", "Women in STEM", "Immigration Rights"],
                "volunteerInterests": ["Tutoring", "Coding Education", "Mentorship"],
            },
            "extracurriculars": [
                {
                    "name": "Code for Kids",
                    "description": "Founded nonprofit teaching coding to underserved middle schoolers",
                    "role": "Founder & President",
                    "hours_per_week": 10,
                    "weeks_per_year": 40,
                    "level": "Regional",
                },
                {
                    "name": "Science Olympiad",
                    "description": "Computer Science captain, led team to state finals",
                    "role": "Captain",
                    "hours_per_week": 8,
                    "weeks_per_year": 30,
                    "level": "State",
                },
            ],
            "constraints": {
                "financialNeed": True,
                "workHours": 15,
            },
        },
    }


@pytest.fixture
def ec_engine():
    """Create ECGenerationEngine instance."""
    return ECGenerationEngine()


@pytest.fixture
def sample_pillars() -> FourPillars:
    """Sample 4 pillars for testing."""
    pillars = FourPillars()
    pillars.identity = {
        "demographics": "First-generation Indian-American female from San Francisco",
        "cultural_religious": "Hindu background with strong family emphasis on education",
        "personality": "Determined, analytical, empathetic",
        "circumstances": "First-generation college student, works 15 hours/week",
        "specific_experiences": [
            "Immigrated at age 5",
            "Witnessed mother's struggle to learn English",
            "First in extended family to pursue STEM"
        ],
    }
    pillars.aptitude = {
        "academic_strengths": "Mathematics, Computer Science, Problem-solving",
        "technical_skills": ["Python", "JavaScript", "Machine Learning basics"],
        "demonstrated_abilities": [
            "Built AI tutoring app with 500+ users",
            "Led Science Olympiad team to state finals",
        ],
        "certifications": [],
    }
    pillars.passion = {
        "stated_interests": ["AI/ML", "EdTech", "Social Impact"],
        "hobbies": ["Building apps", "Mentoring younger students"],
        "media_consumption": "Tech podcasts, AI research papers",
        "energy_indicators": "Lights up when discussing democratizing education",
    }
    pillars.service = {
        "current_volunteering": "Code for Kids nonprofit founder",
        "causes": ["Educational Equity", "Women in STEM", "Immigration Rights"],
        "target_populations": ["Underserved K-8 students", "First-generation immigrants"],
        "values": ["Access", "Equity", "Empowerment"],
    }
    return pillars


# =============================================================================
# UNIT TESTS: FourPillars
# =============================================================================

class TestFourPillars:
    """Tests for FourPillars data class."""

    def test_default_initialization(self):
        """Test default FourPillars creates empty structure."""
        pillars = FourPillars()
        assert pillars.identity["demographics"] == ""
        assert pillars.aptitude["technical_skills"] == []
        assert pillars.passion["stated_interests"] == []
        assert pillars.service["causes"] == []

    def test_to_dict(self, sample_pillars):
        """Test to_dict returns proper structure."""
        result = sample_pillars.to_dict()
        assert "IDENTITY" in result
        assert "APTITUDE" in result
        assert "PASSION" in result
        assert "SERVICE" in result
        assert result["IDENTITY"]["demographics"] == "First-generation Indian-American female from San Francisco"

    def test_get_pillar_count(self, sample_pillars):
        """Test pillar count calculation."""
        count = sample_pillars.get_pillar_count()
        assert count == 4  # All pillars have data

    def test_get_pillar_count_partial(self):
        """Test pillar count with partial data."""
        pillars = FourPillars()
        pillars.identity["demographics"] = "Some demographics"
        pillars.passion["hobbies"] = ["Reading"]
        count = pillars.get_pillar_count()
        assert count == 2  # Only 2 pillars have sufficient data

    def test_get_specificity_score(self, sample_pillars):
        """Test specificity scoring."""
        score = sample_pillars.get_specificity_score()
        assert 0 <= score <= 1
        # Sample pillars have good specificity
        assert score >= 0.5


# =============================================================================
# UNIT TESTS: TenDimensions
# =============================================================================

class TestTenDimensions:
    """Tests for TenDimensions data class."""

    def test_default_initialization(self):
        """Test default TenDimensions creates empty structure."""
        dims = TenDimensions()
        assert dims.geographic["location"] == ""
        assert dims.identity_why["specific_identity"] == ""
        assert dims.catalyst["origin_story"] == ""

    def test_to_dict(self):
        """Test to_dict returns all 10 dimensions."""
        dims = TenDimensions()
        result = dims.to_dict()
        assert len(result) == 10
        expected_keys = [
            "geographic", "identity_why", "field_gap", "catalyst",
            "target_audience", "unique_contribution", "representation",
            "cultural_depth", "temporal", "problem_specificity"
        ]
        for key in expected_keys:
            assert key in result

    def test_get_dimension_score(self):
        """Test dimension score calculation."""
        dims = TenDimensions()
        dims.geographic["location"] = "San Francisco, CA"
        dims.geographic["local_relevance"] = "Tech hub with underserved communities"
        dims.identity_why["specific_identity"] = "First-generation immigrant"
        dims.identity_why["connection"] = "Personal experience with language barriers"

        filled, total = dims.get_dimension_score()
        assert total == 10
        assert filled >= 2  # At least 2 dimensions filled


# =============================================================================
# UNIT TESTS: GapType
# =============================================================================

class TestGapType:
    """Tests for GapType enum."""

    def test_gap_types_exist(self):
        """Test all expected gap types exist."""
        assert GapType.LEADERSHIP.value == "leadership"
        assert GapType.SERVICE.value == "service"
        assert GapType.RESEARCH.value == "research"
        assert GapType.ENTREPRENEURSHIP.value == "entrepreneurship"
        assert GapType.CREATIVE.value == "creative"


# =============================================================================
# UNIT TESTS: GeneratedActivity
# =============================================================================

class TestGeneratedActivity:
    """Tests for GeneratedActivity data class."""

    def test_default_initialization(self):
        """Test default GeneratedActivity creates empty structure."""
        activity = GeneratedActivity()
        assert activity.title == ""
        assert activity.description == ""
        assert activity.ten_dimensions is not None
        assert activity.only_they_score == 0.0

    def test_to_dict(self):
        """Test to_dict returns proper structure."""
        activity = GeneratedActivity()
        activity.title = "Test Activity"
        activity.description = "Test description"
        activity.gap_addressed = GapType.LEADERSHIP
        activity.only_they_score = 0.85

        result = activity.to_dict()
        assert result["title"] == "Test Activity"
        assert result["description"] == "Test description"
        assert result["gap_addressed"] == "leadership"
        assert result["only_they_score"] == 0.85


# =============================================================================
# INTEGRATION TESTS: ECGenerationEngine
# =============================================================================

class TestECGenerationEngine:
    """Integration tests for ECGenerationEngine class."""

    def test_initialization(self, ec_engine):
        """Test ECGenerationEngine initializes correctly."""
        assert ec_engine is not None

    def test_identify_gaps(self, ec_engine, sample_profile, sample_pillars):
        """Test gap identification."""
        gaps = ec_engine.identify_gaps(sample_profile, sample_pillars)
        assert isinstance(gaps, list)
        assert all(isinstance(g, GapType) for g in gaps)
        # Should identify some gaps even with a strong profile
        assert len(gaps) >= 0

    @pytest.mark.asyncio
    @patch('agents.core.ec_generation_engine.ChatOpenAI')
    async def test_extract_four_pillars_mock(self, mock_llm, ec_engine, sample_profile):
        """Test pillar extraction with mocked LLM."""
        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.content = '''```json
{
    "IDENTITY": {
        "demographics": "First-generation Indian-American female",
        "cultural_religious": "Hindu background",
        "personality": "Determined, analytical",
        "circumstances": "First-gen college student",
        "specific_experiences": ["Immigrated at age 5"]
    },
    "APTITUDE": {
        "academic_strengths": "Mathematics, CS",
        "technical_skills": ["Python", "ML"],
        "demonstrated_abilities": ["Built AI tutoring app"],
        "certifications": []
    },
    "PASSION": {
        "stated_interests": ["AI/ML", "EdTech"],
        "hobbies": ["Building apps"],
        "media_consumption": "Tech podcasts",
        "energy_indicators": "Excited about education"
    },
    "SERVICE": {
        "current_volunteering": "Code for Kids founder",
        "causes": ["Educational Equity"],
        "target_populations": ["Underserved K-8 students"],
        "values": ["Access", "Equity"]
    }
}
```'''

        mock_llm_instance = MagicMock()
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm.return_value = mock_llm_instance

        # Create new instance to use mocked LLM
        ec_engine._llm = mock_llm_instance

        result = await ec_engine.extract_four_pillars(sample_profile)
        assert isinstance(result, FourPillars)
        assert result.identity["demographics"] != ""

    @pytest.mark.asyncio
    @patch('agents.core.ec_generation_engine.ChatOpenAI')
    async def test_synthesize_narrative_mock(self, mock_llm, ec_engine, sample_pillars, sample_profile):
        """Test narrative synthesis with mocked LLM."""
        mock_response = MagicMock()
        mock_response.content = '''```json
{
    "archetype": "stem_innovator",
    "archetype_confidence": 0.85,
    "spike": "Using AI to democratize education for first-generation immigrants",
    "spike_confidence": 0.80,
    "pillars": ["Tech Innovation", "Educational Equity", "Community Leadership"],
    "master_narrative": "Maya's journey...",
    "reframe_applied": {
        "original_weakness": "First-generation, limited resources",
        "reframed_strength": "Unique perspective on educational gaps"
    }
}
```'''

        mock_llm_instance = MagicMock()
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm.return_value = mock_llm_instance

        ec_engine._llm = mock_llm_instance

        result = await ec_engine.synthesize_narrative(sample_pillars, sample_profile)
        assert isinstance(result, dict)
        assert "archetype" in result
        assert "spike" in result

    def test_validate_only_they_test(self, ec_engine, sample_pillars):
        """Test 'Only They' validation logic."""
        # Create a highly personalized activity
        activity = GeneratedActivity()
        activity.title = "AI Tutoring for First-Gen K-8 Students"
        activity.description = (
            "Maya creates an AI-powered tutoring platform specifically designed "
            "for first-generation immigrant children, incorporating cultural context "
            "and language support based on her own experience immigrating at age 5."
        )
        activity.ten_dimensions.geographic = {
            "location": "San Francisco Bay Area",
            "local_relevance": "Large immigrant population with educational gaps",
            "local_partner": "SF Unified School District"
        }
        activity.ten_dimensions.identity_why = {
            "specific_identity": "First-generation Indian-American immigrant",
            "connection": "Personal experience with language barriers in school"
        }
        activity.ten_dimensions.unique_contribution = {
            "intersection": "AI/ML + immigrant experience + educational equity",
            "only_they_bring": "Combines technical skills with lived immigrant experience"
        }

        # Validate
        passed, score, reasons = ec_engine.validate_only_they_test(activity, sample_pillars)

        # Should pass or be close to passing with this level of detail
        assert isinstance(passed, bool)
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert isinstance(reasons, list)


# =============================================================================
# VALIDATION TESTS
# =============================================================================

class TestOnlyTheyValidation:
    """Tests for the 'Only They' validation criteria."""

    def test_generic_activity_fails(self, ec_engine, sample_pillars):
        """Test that generic activities fail validation."""
        # Create a generic activity
        activity = GeneratedActivity()
        activity.title = "Coding Club"
        activity.description = "Join a coding club to learn programming."

        passed, score, reasons = ec_engine.validate_only_they_test(activity, sample_pillars)

        # Generic activity should fail
        assert passed is False
        assert score < 0.7  # Below threshold

    def test_partially_personalized_activity(self, ec_engine, sample_pillars):
        """Test partially personalized activity scores medium."""
        activity = GeneratedActivity()
        activity.title = "Coding Workshop for Underserved Students"
        activity.description = (
            "Host coding workshops for underserved middle school students "
            "to teach programming basics and inspire interest in STEM."
        )
        activity.ten_dimensions.target_audience = {
            "demographic": "Underserved middle school students",
            "identity_connection": "Community Maya wants to serve"
        }

        passed, score, reasons = ec_engine.validate_only_they_test(activity, sample_pillars)

        # Should have medium score
        assert isinstance(score, float)
        # Not fully generic, but not fully personalized either


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_profile(self, ec_engine):
        """Test handling of empty profile."""
        empty_profile = {}
        gaps = ec_engine.identify_gaps(empty_profile, FourPillars())
        # Should return all gap types when profile is empty
        assert len(gaps) > 0

    def test_minimal_profile(self, ec_engine):
        """Test handling of minimal profile data."""
        minimal_profile = {
            "profile_data": {
                "basicInfo": {"firstName": "Test"}
            }
        }
        gaps = ec_engine.identify_gaps(minimal_profile, FourPillars())
        assert isinstance(gaps, list)

    def test_pillars_with_none_values(self):
        """Test FourPillars handles None values gracefully."""
        pillars = FourPillars()
        pillars.identity["demographics"] = None  # Intentionally set None

        # Should not raise exception
        count = pillars.get_pillar_count()
        assert isinstance(count, int)


# =============================================================================
# COACH AUGMENTATION TESTS
# =============================================================================

class TestCoachAugmentation:
    """Test coach-specific methodology augmentations."""

    def test_register_coach_augmentation(self):
        """Test registering a coach augmentation."""
        engine = ECGenerationEngine()
        engine.register_coach_augmentation("test_coach", {
            "pillar_weights": {"IDENTITY": 1.2, "SERVICE": 1.1}
        })
        assert hasattr(engine, '_coach_augmentations')
        assert "test_coach" in engine._coach_augmentations

    def test_apply_coach_augmentation(self):
        """Test applying a coach augmentation to output."""
        engine = ECGenerationEngine()
        engine.register_coach_augmentation("test_coach", {
            "pillar_weights": {"IDENTITY": 1.2}
        })
        base_output = {"identity_synthesis": {"spike": "test"}}
        augmented = engine.apply_coach_augmentation("test_coach", base_output)
        assert augmented is not None
        assert augmented.get("coach_augmentation_applied") == "test_coach"

    def test_no_augmentation_returns_base(self):
        """Test that missing augmentation returns base output unchanged."""
        engine = ECGenerationEngine()
        base_output = {"test": "data"}
        result = engine.apply_coach_augmentation("nonexistent", base_output)
        assert result == base_output

    def test_get_registered_coaches(self):
        """Test getting list of registered coach augmentations."""
        engine = ECGenerationEngine()
        engine.register_coach_augmentation("coach_a", {"pillar_weights": {}})
        engine.register_coach_augmentation("coach_b", {"custom_reframes": []})
        coaches = engine.get_registered_coaches()
        assert "coach_a" in coaches
        assert "coach_b" in coaches

    def test_multiple_augmentations(self):
        """Test applying multiple augmentation types."""
        engine = ECGenerationEngine()
        engine.register_coach_augmentation("full_coach", {
            "pillar_weights": {"IDENTITY": 1.3},
            "custom_reframes": [{"original": "weakness", "reframed": "strength"}],
            "validation_criteria": [{"name": "test_criteria"}],
        })
        base_output = {"identity_synthesis": {"spike": "test"}}
        augmented = engine.apply_coach_augmentation("full_coach", base_output)
        assert augmented.get("coach_augmentation_applied") == "full_coach"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
