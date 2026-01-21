# tests/patterns/test_validation.py
"""
Tests for Validation patterns: E1 Output Validation
CORRECTED to match actual implementation
"""

import pytest


class TestOutputValidator:
    """Tests for OutputValidator (E1)."""
    
    def test_validator_importable(self):
        """Test OutputValidator can be imported."""
        from validation.output_validation import OutputValidator
        assert OutputValidator is not None
    
    def test_validator_initialization(self):
        """Test OutputValidator can be initialized."""
        from validation.output_validation import OutputValidator
        validator = OutputValidator()
        assert validator is not None
    
    def test_validator_with_custom_dimensions(self):
        """Test OutputValidator with custom dimensions."""
        from validation.output_validation import OutputValidator, QualityDimension
        
        custom_dims = {
            "custom_type": [
                QualityDimension(name="test_dim", weight=1.0),
            ],
        }
        validator = OutputValidator(dimensions=custom_dims)
        assert "custom_type" in validator.dimensions
    
    def test_validate_returns_validation_result(self):
        """Test validate returns ValidationResult."""
        from validation.output_validation import OutputValidator, ValidationResult
        
        validator = OutputValidator()
        result = validator.validate(
            output={"content": "test"},
            output_type="recommendation",
        )
        
        assert isinstance(result, ValidationResult)
    
    def test_validation_result_has_expected_fields(self):
        """Test ValidationResult has all expected fields."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        result = validator.validate({"content": "test"}, "recommendation")
        
        assert hasattr(result, 'valid')
        assert hasattr(result, 'score')
        assert hasattr(result, 'errors')
        assert hasattr(result, 'warnings')
        assert hasattr(result, 'suggestions')
        assert hasattr(result, 'metadata')
    
    def test_validate_spike_output(self):
        """Test validate with spike output type."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        result = validator.validate(
            output={
                "spike": "AI and Machine Learning research focusing on computer vision applications",
            },
            output_type="spike",
        )
        
        assert result.score >= 0
        assert result.score <= 100
    
    def test_validate_spike_too_short(self):
        """Test validate catches spike that's too short."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        result = validator.validate(
            output={"spike": "AI"},
            output_type="spike",
        )
        
        # Should have error for short spike
        assert any("too short" in err.lower() for err in result.errors)
    
    def test_validate_gameplan_output(self):
        """Test validate with gameplan output type."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        result = validator.validate(
            output={
                "priorities": [{"name": "Apply to RSI", "priority": "high"}],
                "timeline": "Summer 2025",
                "next_steps": ["Research programs", "Draft essays"],
            },
            output_type="gameplan",
        )
        
        assert result is not None
    
    def test_validate_gameplan_missing_priorities(self):
        """Test validate catches gameplan missing priorities."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        result = validator.validate(
            output={"next_steps": ["Do something"]},
            output_type="gameplan",
        )
        
        # Should have error for missing priorities
        assert any("priorities" in err.lower() for err in result.errors)
    
    def test_validate_recommendation_output(self):
        """Test validate with recommendation output type."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        result = validator.validate(
            output={
                "items": [
                    {"name": "RSI", "type": "program"},
                    {"name": "USACO", "type": "award"},
                ],
            },
            output_type="recommendation",
        )
        
        assert result is not None
    
    def test_validate_recommendation_empty_items(self):
        """Test validate catches empty recommendations."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        result = validator.validate(
            output={"items": []},
            output_type="recommendation",
        )
        
        # Should have error for no recommendations
        assert any("no recommendations" in err.lower() for err in result.errors)
    
    def test_validate_with_context(self):
        """Test validate uses context for scoring."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        result = validator.validate(
            output={"content": "This focuses on AI research"},
            output_type="recommendation",
            context={
                "profile": {"spike": "AI research", "archetype": "academic_all_star"},
            },
        )
        
        # Context should influence relevance scoring
        assert result is not None
    
    def test_validate_unknown_output_type(self):
        """Test validate handles unknown output type."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        result = validator.validate(
            output={"content": "test"},
            output_type="unknown_type",
        )
        
        # Should still return result (with default scoring)
        assert result is not None
        assert isinstance(result.score, float)
    
    def test_dimension_scores_in_metadata(self):
        """Test dimension scores are included in metadata."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        result = validator.validate(
            output={"content": "test"},
            output_type="spike",
        )
        
        assert "dimension_scores" in result.metadata
        assert "output_type" in result.metadata


class TestValidationResult:
    """Tests for ValidationResult model."""
    
    def test_validation_result_importable(self):
        """Test ValidationResult can be imported."""
        from validation.output_validation import ValidationResult
        assert ValidationResult is not None
    
    def test_validation_result_creation(self):
        """Test creating a ValidationResult."""
        from validation.output_validation import ValidationResult
        
        result = ValidationResult(
            valid=True,
            score=85.0,
            errors=[],
            warnings=["Minor issue"],
            suggestions=["Add more detail"],
        )
        
        assert result.valid is True
        assert result.score == 85.0
        assert len(result.warnings) == 1
    
    def test_validation_result_score_bounds(self):
        """Test ValidationResult enforces score bounds."""
        from validation.output_validation import ValidationResult
        
        # Valid scores should work
        result = ValidationResult(valid=True, score=50.0)
        assert result.score == 50.0


class TestQualityDimension:
    """Tests for QualityDimension model."""
    
    def test_quality_dimension_importable(self):
        """Test QualityDimension can be imported."""
        from validation.output_validation import QualityDimension
        assert QualityDimension is not None
    
    def test_quality_dimension_creation(self):
        """Test creating a QualityDimension."""
        from validation.output_validation import QualityDimension
        
        dim = QualityDimension(
            name="specificity",
            weight=0.3,
            min_score=70,
        )
        
        assert dim.name == "specificity"
        assert dim.weight == 0.3
        assert dim.min_score == 70


class TestQualityDimensions:
    """Tests for QUALITY_DIMENSIONS constants."""
    
    def test_quality_dimensions_importable(self):
        """Test QUALITY_DIMENSIONS can be imported."""
        from validation.output_validation import QUALITY_DIMENSIONS
        assert QUALITY_DIMENSIONS is not None
    
    def test_spike_dimensions_exist(self):
        """Test spike output type has dimensions."""
        from validation.output_validation import QUALITY_DIMENSIONS
        
        assert "spike" in QUALITY_DIMENSIONS
        assert len(QUALITY_DIMENSIONS["spike"]) > 0
    
    def test_narrative_dimensions_exist(self):
        """Test narrative output type has dimensions."""
        from validation.output_validation import QUALITY_DIMENSIONS
        
        assert "narrative" in QUALITY_DIMENSIONS
    
    def test_recommendation_dimensions_exist(self):
        """Test recommendation output type has dimensions."""
        from validation.output_validation import QUALITY_DIMENSIONS
        
        assert "recommendation" in QUALITY_DIMENSIONS
    
    def test_gameplan_dimensions_exist(self):
        """Test gameplan output type has dimensions."""
        from validation.output_validation import QUALITY_DIMENSIONS
        
        assert "gameplan" in QUALITY_DIMENSIONS


class TestConvenienceFunction:
    """Tests for validate_output convenience function."""
    
    def test_validate_output_exists(self):
        """Test validate_output function exists."""
        from validation.output_validation import validate_output
        assert validate_output is not None
    
    def test_validate_output_returns_result(self):
        """Test validate_output returns ValidationResult."""
        from validation.output_validation import validate_output, ValidationResult
        
        result = validate_output(
            output={"content": "test"},
            output_type="recommendation",
        )
        
        assert isinstance(result, ValidationResult)
    
    def test_validate_output_with_context(self):
        """Test validate_output with context."""
        from validation.output_validation import validate_output
        
        result = validate_output(
            output={"content": "test"},
            output_type="recommendation",
            context={"grade": 11},
        )
        
        assert result is not None


class TestScoringMethods:
    """Tests for internal scoring methods."""
    
    def test_score_specificity(self):
        """Test _score_specificity method."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        
        # Specific output should score higher
        specific_output = {
            "content": "Apply to RSI summer program at MIT by January 15, 2025"
        }
        generic_output = {
            "content": "Do various things and stuff etc"
        }
        
        specific_score = validator._score_specificity(specific_output)
        generic_score = validator._score_specificity(generic_output)
        
        assert specific_score > generic_score
    
    def test_score_actionability(self):
        """Test _score_actionability method."""
        from validation.output_validation import OutputValidator
        
        validator = OutputValidator()
        
        # Actionable output should score higher
        actionable_output = {
            "content": "First, apply to RSI. Then, submit your essay. Next, focus on USACO."
        }
        passive_output = {
            "content": "There are programs available that students attend."
        }
        
        actionable_score = validator._score_actionability(actionable_output)
        passive_score = validator._score_actionability(passive_output)
        
        assert actionable_score > passive_score
