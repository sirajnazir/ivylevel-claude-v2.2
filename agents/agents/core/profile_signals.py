"""
Profile Signals Extraction
==========================
Extracts signals from profile_data for inference when activities are empty.

Used by EC Agent to infer spike and archetype from:
- Passion: interests, dream_career, causes
- Aptitude: intended_major, favorite_subjects
- Identity: strengths, values, grade
- Service: volunteer_interests
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ProfileSignals:
    """
    Extracted signals from profile_data for identity inference.

    These signals allow the EC Agent to generate meaningful identity
    synthesis even when the student has no activities entered.
    """

    # Passion signals (primary for spike inference)
    interests: List[str] = field(default_factory=list)
    dream_career: str = ""
    causes: List[str] = field(default_factory=list)
    spike_category: Optional[str] = None

    # Academic signals (for archetype scoring)
    intended_major: str = ""
    favorite_subjects: List[str] = field(default_factory=list)
    gpa: Optional[float] = None
    sat_total: Optional[int] = None

    # Identity signals (for archetype and pillars)
    strengths: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    grade: int = 11

    # Service signals (for community archetype)
    volunteer_interests: List[str] = field(default_factory=list)
    community_focus: Optional[str] = None

    def has_passion_signals(self) -> bool:
        """Check if passion-related signals exist."""
        return bool(self.interests or self.dream_career or self.causes or self.spike_category)

    def has_academic_signals(self) -> bool:
        """Check if academic signals exist."""
        return bool(self.intended_major or self.favorite_subjects)

    def has_identity_signals(self) -> bool:
        """Check if identity signals exist."""
        return bool(self.strengths or self.values)

    def has_any_signals(self) -> bool:
        """Check if any signals exist for inference."""
        return self.has_passion_signals() or self.has_academic_signals() or self.has_identity_signals()

    def get_spike_components(self) -> List[str]:
        """Get components that can form a spike."""
        components = []

        if self.intended_major:
            components.append(self.intended_major)
        if self.interests:
            components.extend(self.interests[:2])
        if self.causes:
            components.append(self.causes[0])
        if self.dream_career:
            components.append(self.dream_career)

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for c in components:
            c_lower = c.lower()
            if c_lower not in seen and c:
                seen.add(c_lower)
                unique.append(c)

        return unique[:5]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            "interests": self.interests,
            "dream_career": self.dream_career,
            "causes": self.causes,
            "spike_category": self.spike_category,
            "intended_major": self.intended_major,
            "favorite_subjects": self.favorite_subjects,
            "strengths": self.strengths,
            "values": self.values,
            "grade": self.grade,
            "volunteer_interests": self.volunteer_interests,
            "has_signals": self.has_any_signals(),
        }


def extract_profile_signals(profile: Dict) -> ProfileSignals:
    """
    Extract ProfileSignals from a profile dictionary.

    Args:
        profile: Profile dict with profile_data from assessment

    Returns:
        ProfileSignals dataclass with extracted values
    """
    profile_data = profile.get("profile_data", {})

    # Extract from each section
    passion = profile_data.get("passion", {})
    aptitude = profile_data.get("aptitude", {})
    identity = profile_data.get("identity", {})
    service = profile_data.get("service", {})

    return ProfileSignals(
        # Passion
        interests=_ensure_list(passion.get("interests")),
        dream_career=passion.get("dream_career", "") or "",
        causes=_ensure_list(passion.get("causes") or passion.get("causes_care_about")),
        spike_category=passion.get("spike_category"),

        # Aptitude
        intended_major=aptitude.get("intended_major", "") or "",
        favorite_subjects=_ensure_list(aptitude.get("favorite_subjects")),
        gpa=_safe_float(aptitude.get("gpa_weighted") or aptitude.get("gpa")),
        sat_total=_safe_int(aptitude.get("sat_total")),

        # Identity
        strengths=_ensure_list(identity.get("strengths")),
        values=_ensure_list(identity.get("values")),
        grade=_safe_int(identity.get("grade")) or 11,

        # Service
        volunteer_interests=_ensure_list(service.get("volunteer_interests")),
        community_focus=service.get("community_focus"),
    )


def _ensure_list(value) -> List[str]:
    """Ensure value is a list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return []


def _safe_float(value) -> Optional[float]:
    """Safely convert to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_int(value) -> Optional[int]:
    """Safely convert to int."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
