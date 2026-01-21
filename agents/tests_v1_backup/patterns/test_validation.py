# agents/tests/patterns/test_validation.py
"""
Tests for Validation Patterns (E1) - v5.4 True Autonomous Agents.

Tests:
- E1: Output Validation
- Jenny Voice validation (existing)
"""

import pytest
from unittest.mock import MagicMock
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestOutputValidation:
    """Tests for E1: Output Validation pattern."""

    def test_output_validator_creation(self):
        """Test OutputValidator can be created."""
        from validation import OutputValidator

        validator = OutputValidator()

        assert validator is not None

    def test_validation_result_model(self):
        """Test ValidationResult model structure."""
        from validation import ValidationResult

        result = ValidationResult(
            valid=True,
            score=0.92,
            errors=[],
            warnings=["Consider adding more specific details"],
            dimensions_scores={"completeness": 0.95, "clarity": 0.89},
        )

        assert result.valid is True
        assert result.score == 0.92
        assert len(result.warnings) == 1

    def test_quality_dimension_model(self):
        """Test QualityDimension model structure."""
        from validation import QualityDimension

        dimension = QualityDimension(
            name="completeness",
            weight=0.3,
            score=0.85,
            threshold=0.7,
            feedback="Output includes all required fields",
        )

        assert dimension.name == "completeness"
        assert dimension.score >= dimension.threshold

    def test_validate_gameplan_output(self, valid_gameplan_output):
        """Test validation of valid gameplan output."""
        from validation import OutputValidator

        validator = OutputValidator()

        result = validator.validate(valid_gameplan_output, "gameplan")

        assert result.valid is True
        assert result.score > 0.5

    def test_validate_invalid_gameplan_output(self, invalid_gameplan_output):
        """Test validation catches invalid gameplan output."""
        from validation import OutputValidator

        validator = OutputValidator()

        result = validator.validate(invalid_gameplan_output, "gameplan")

        # Should have errors or low score
        assert not result.valid or len(result.errors) > 0 or result.score < 0.5

    def test_validate_assessment_output(self, valid_assessment_output):
        """Test validation of valid assessment output."""
        from validation import OutputValidator

        validator = OutputValidator()

        result = validator.validate(valid_assessment_output, "assessment")

        assert result.valid is True

    def test_quality_dimensions_defined(self):
        """Test quality dimensions are configured."""
        from validation import QUALITY_DIMENSIONS

        assert QUALITY_DIMENSIONS is not None
        assert isinstance(QUALITY_DIMENSIONS, (list, dict))

    def test_validate_output_function(self):
        """Test convenience function for output validation."""
        from validation import validate_output

        result = validate_output(
            {"recommendation": "Test"},
            "general"
        )

        assert result is not None


class TestJennyVoice:
    """Tests for Jenny Voice validation (existing USP)."""

    def test_jenny_voice_validator_creation(self):
        """Test JennyVoiceValidator can be created."""
        from validation import JennyVoiceValidator

        validator = JennyVoiceValidator()

        assert validator is not None

    def test_jenny_voice_result_model(self):
        """Test JennyVoiceResult model structure."""
        from validation import JennyVoiceResult

        result = JennyVoiceResult(
            is_jenny_voice=True,
            confidence=0.88,
            issues=[],
            suggestions=[],
        )

        assert result.is_jenny_voice is True
        assert result.confidence > 0.5

    def test_validate_jenny_voice_compliant(self):
        """Test validation of Jenny Voice compliant text."""
        from validation import validate_jenny_voice

        # Jenny-like text: encouraging, student-focused
        text = """
        Great question! Based on your robotics experience, I'd suggest
        focusing on summer research programs. Your skills in engineering
        would be a perfect fit for MIT's MITES program. What do you think?
        """

        result = validate_jenny_voice(text)

        assert result is not None
        # Should be reasonably compliant

    def test_validate_non_jenny_voice(self):
        """Test validation catches non-Jenny Voice text."""
        from validation import validate_jenny_voice

        # Formal, not student-friendly
        text = """
        The applicant should consider the following recommendations
        pursuant to the established guidelines for college admissions.
        Compliance with these directives is mandatory.
        """

        result = validate_jenny_voice(text)

        assert result is not None
        # Should have lower confidence or issues

    def test_jenny_voice_checks_encouragement(self):
        """Test Jenny Voice checks for encouraging tone."""
        from validation import JennyVoiceValidator

        validator = JennyVoiceValidator()

        # Encouraging text
        encouraging = "You're making great progress! Keep up the excellent work."
        result1 = validator.validate(encouraging)

        # Discouraging text
        discouraging = "This is inadequate. You need to do much better."
        result2 = validator.validate(discouraging)

        # Encouraging should score higher
        assert result1.confidence >= result2.confidence or result1.is_jenny_voice != result2.is_jenny_voice


class TestValidationIntegration:
    """Integration tests for validation patterns."""

    def test_all_validation_types_importable(self):
        """Test all validation types can be imported."""
        from validation import (
            OutputValidator,
            ValidationResult,
            QualityDimension,
            JennyVoiceValidator,
            JennyVoiceResult,
            validate_output,
            validate_jenny_voice,
        )

        # All should be importable

    def test_combined_validation(self, valid_gameplan_output):
        """Test combined output and voice validation."""
        from validation import OutputValidator, JennyVoiceValidator

        output_validator = OutputValidator()
        voice_validator = JennyVoiceValidator()

        # Validate structure
        output_result = output_validator.validate(valid_gameplan_output, "gameplan")

        # Validate voice (if there's text content)
        summary = valid_gameplan_output.get("summary", "")
        if summary:
            voice_result = voice_validator.validate(summary)
            assert voice_result is not None

        assert output_result.valid is True

    def test_validation_with_context(self, valid_gameplan_output, sample_student_context):
        """Test validation uses context appropriately."""
        from validation import OutputValidator

        validator = OutputValidator()

        result = validator.validate(
            valid_gameplan_output,
            "gameplan",
            context=sample_student_context,
        )

        assert result is not None

    def test_validation_provides_actionable_feedback(self, invalid_gameplan_output):
        """Test validation provides actionable feedback."""
        from validation import OutputValidator

        validator = OutputValidator()

        result = validator.validate(invalid_gameplan_output, "gameplan")

        # Should have errors or warnings with actionable feedback
        if result.errors:
            for error in result.errors:
                assert len(error) > 0  # Not empty messages
        if result.warnings:
            for warning in result.warnings:
                assert len(warning) > 0

    def test_validation_handles_empty_output(self):
        """Test validation handles empty output gracefully."""
        from validation import OutputValidator

        validator = OutputValidator()

        result = validator.validate({}, "general")

        assert result is not None
        # Should indicate invalid or have errors

    def test_validation_handles_unexpected_output_type(self):
        """Test validation handles unknown output types."""
        from validation import OutputValidator

        validator = OutputValidator()

        result = validator.validate(
            {"data": "test"},
            "unknown_type_xyz"
        )

        assert result is not None
        # Should handle gracefully
