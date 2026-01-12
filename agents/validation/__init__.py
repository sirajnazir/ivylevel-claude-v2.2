"""
Jenny Voice Validation Module
Validates agent outputs against Jenny Duan's speech patterns and rules.
"""

from .jenny_voice import JennyVoiceValidator, JennyVoiceResult, validate_jenny_voice

__all__ = ['JennyVoiceValidator', 'JennyVoiceResult', 'validate_jenny_voice']
