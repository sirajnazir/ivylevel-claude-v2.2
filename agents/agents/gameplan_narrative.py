"""
Game Plan Agent - Narrative Synthesis Module
=============================================

Jenny's Core Insight: "Identity grounds everything - it's not what you do,
but who you are doing it"

This module is the PRESCRIPTION phase - it takes raw components extracted
during DIAGNOSIS (Assessment) and synthesizes them into the Master Narrative.

The Master Formula:
IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE

Example (Huda):
- Identity: Indian Muslim girl, quiet, minority in tech
- Aptitude: Technology, CS, AI
- Passion: Games, Film, Storytelling (First Principle: "BUILDER")
- Service: Education for underrepresented groups
- Narrative: "A builder and storyteller who creates games that make technology
              accessible for minorities like her"

This module:
1. Takes RAW components from Assessment (identity, aptitude, passion, service)
2. SYNTHESIZES them into Master Narrative (the brand statement)
3. Provides narrative-based filtering for all recommendations
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class FirstPrinciplePassion(str, Enum):
    """
    Jenny's "First Principles" - What the student fundamentally IS
    Not what they DO, but WHO they ARE at their core

    Example: Huda does CS, games, film - but fundamentally she's a BUILDER
    """
    BUILDER = "builder"           # Creates things, makes stuff work
    STORYTELLER = "storyteller"   # Communicates, shares narratives
    DISCOVERER = "discoverer"     # Researches, finds new knowledge
    ADVOCATE = "advocate"         # Fights for causes, speaks up
    CONNECTOR = "connector"       # Brings people together
    HEALER = "healer"            # Helps, cares for others
    LEADER = "leader"            # Organizes, directs, inspires
    ARTIST = "artist"            # Expresses through creative medium
    ENTREPRENEUR = "entrepreneur" # Starts things, takes risks
    SCHOLAR = "scholar"          # Loves learning for its own sake


@dataclass
class NarrativeScores:
    """Quality scores using Jenny's assessment framework"""
    identity_clarity: int = 0       # 1-10: How clear is their identity?
    aptitude_alignment: int = 0     # 1-10: Skills match direction?
    passion_authenticity: int = 0   # 1-10: Is passion genuine/deep?
    service_relevance: int = 0      # 1-10: Service connects to identity?
    narrative_power: int = 0        # 1-10: Overall story strength

    @property
    def total(self) -> int:
        """40+ = Transformative application"""
        return (
            self.identity_clarity +
            self.aptitude_alignment +
            self.passion_authenticity +
            self.service_relevance +
            self.narrative_power
        )

    def to_dict(self) -> Dict[str, int]:
        return {
            "identity_clarity": self.identity_clarity,
            "aptitude_alignment": self.aptitude_alignment,
            "passion_authenticity": self.passion_authenticity,
            "service_relevance": self.service_relevance,
            "narrative_power": self.narrative_power,
        }


@dataclass
class MasterNarrative:
    """
    The synthesized brand statement that filters all recommendations

    This is the PRESCRIPTION - the strategic identity that every
    activity, award, and program must serve.
    """
    # The 4 components (synthesized, not raw)
    identity_statement: str = ""      # "Indian Muslim girl who felt unseen in tech"
    aptitude_statement: str = ""      # "with technology and CS skills"
    passion_statement: str = ""       # "who is fundamentally a builder and storyteller"
    service_statement: str = ""       # "serving underrepresented girls in tech"

    # The first-principles passion (Jenny's extraction)
    first_principle: FirstPrinciplePassion = FirstPrinciplePassion.SCHOLAR
    first_principle_evidence: List[str] = field(default_factory=list)

    # The synthesized outputs
    brand_statement: str = ""         # One-sentence identity brand
    unique_positioning: str = ""      # What makes this combination unique

    # Filtering keywords (for matching recommendations)
    identity_keywords: List[str] = field(default_factory=list)
    aptitude_keywords: List[str] = field(default_factory=list)
    passion_keywords: List[str] = field(default_factory=list)
    service_keywords: List[str] = field(default_factory=list)

    # Quality scores (Jenny's assessment framework)
    scores: NarrativeScores = field(default_factory=NarrativeScores)

    @property
    def total_score(self) -> int:
        """40+ = Transformative application"""
        return self.scores.total

    @property
    def all_keywords(self) -> List[str]:
        """All keywords for filtering"""
        return (
            self.identity_keywords +
            self.aptitude_keywords +
            self.passion_keywords +
            self.service_keywords
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "identity_statement": self.identity_statement,
            "aptitude_statement": self.aptitude_statement,
            "passion_statement": self.passion_statement,
            "service_statement": self.service_statement,
            "first_principle": self.first_principle.value,
            "first_principle_evidence": self.first_principle_evidence,
            "brand_statement": self.brand_statement,
            "unique_positioning": self.unique_positioning,
            "identity_keywords": self.identity_keywords,
            "aptitude_keywords": self.aptitude_keywords,
            "passion_keywords": self.passion_keywords,
            "service_keywords": self.service_keywords,
            "scores": self.scores.to_dict(),
            "total_score": self.total_score,
        }


class NarrativeSynthesizer:
    """
    Synthesizes Master Narrative from raw assessment components

    This is Jenny's core intelligence - taking scattered facts and
    weaving them into a compelling, unique identity.
    """

    # Mapping from passion keywords to first principles
    FIRST_PRINCIPLE_SIGNALS: Dict[FirstPrinciplePassion, List[str]] = {
        FirstPrinciplePassion.BUILDER: [
            'build', 'create', 'make', 'code', 'develop', 'design',
            'construct', 'program', 'app', 'website', 'robot', 'game'
        ],
        FirstPrinciplePassion.STORYTELLER: [
            'story', 'film', 'write', 'narrative', 'communicate', 'share',
            'video', 'media', 'journalism', 'blog', 'publish'
        ],
        FirstPrinciplePassion.DISCOVERER: [
            'research', 'discover', 'explore', 'investigate', 'study',
            'analyze', 'experiment', 'lab', 'theory', 'hypothesis'
        ],
        FirstPrinciplePassion.ADVOCATE: [
            'advocate', 'fight', 'change', 'justice', 'rights', 'speak',
            'voice', 'protest', 'policy', 'activism', 'campaign'
        ],
        FirstPrinciplePassion.CONNECTOR: [
            'connect', 'community', 'bring together', 'network', 'unite',
            'bridge', 'organize', 'coordinate', 'collaborate'
        ],
        FirstPrinciplePassion.HEALER: [
            'help', 'care', 'heal', 'support', 'nurture', 'comfort',
            'patient', 'medical', 'health', 'therapy', 'counsel'
        ],
        FirstPrinciplePassion.LEADER: [
            'lead', 'direct', 'manage', 'inspire', 'guide',
            'president', 'captain', 'founded', 'chair'
        ],
        FirstPrinciplePassion.ARTIST: [
            'art', 'music', 'perform', 'express', 'creative', 'aesthetic',
            'paint', 'dance', 'theater', 'compose', 'sculpture'
        ],
        FirstPrinciplePassion.ENTREPRENEUR: [
            'start', 'launch', 'business', 'venture', 'innovate', 'risk',
            'startup', 'company', 'profit', 'market', 'sell'
        ],
        FirstPrinciplePassion.SCHOLAR: [
            'learn', 'study', 'academic', 'intellectual', 'knowledge',
            'curious', 'philosophy', 'theory', 'literature', 'history'
        ],
    }

    def synthesize(self, raw_extraction: Dict[str, Any]) -> MasterNarrative:
        """
        Main synthesis function - takes raw assessment output,
        returns Master Narrative

        This is the PRESCRIPTION phase - creating the strategic identity.

        Args:
            raw_extraction: Output from Assessment phase (diagnosis)

        Returns:
            MasterNarrative: The synthesized brand statement and filtering keywords
        """
        # Use 'or {}' to handle explicit None values
        raw_identity = raw_extraction.get('raw_identity') or {}
        raw_aptitude = raw_extraction.get('raw_aptitude') or {}
        raw_passion = raw_extraction.get('raw_passion') or {}
        raw_service = raw_extraction.get('raw_service') or {}

        # Step 1: Find the First Principle passion (Jenny's core extraction)
        first_principle, evidence = self._extract_first_principle(raw_passion)

        # Step 2: Synthesize identity statement
        identity_statement = self._synthesize_identity(raw_identity)
        identity_keywords = self._extract_identity_keywords(raw_identity)

        # Step 3: Synthesize aptitude statement
        aptitude_statement = self._synthesize_aptitude(raw_aptitude)
        aptitude_keywords = raw_aptitude.get('mentioned_skills') or []

        # Step 4: Synthesize passion statement (using first principle)
        passion_statement = self._synthesize_passion(raw_passion, first_principle)
        passion_keywords = raw_passion.get('passion_keywords') or []

        # Step 5: Synthesize service statement
        service_statement = self._synthesize_service(raw_service, raw_identity)
        service_keywords = raw_service.get('communities_served') or []

        # Step 6: Create brand statement using Jenny's formula
        brand_statement = self._create_brand_statement(
            identity_statement, aptitude_statement,
            passion_statement, service_statement
        )

        # Step 7: Create unique positioning
        unique_positioning = self._create_unique_positioning(
            identity_keywords, aptitude_keywords,
            passion_keywords, service_keywords
        )

        # Step 8: Score the narrative
        scores = self._score_narrative(
            raw_identity, raw_aptitude, raw_passion, raw_service,
            first_principle, evidence
        )

        return MasterNarrative(
            identity_statement=identity_statement,
            aptitude_statement=aptitude_statement,
            passion_statement=passion_statement,
            service_statement=service_statement,
            first_principle=first_principle,
            first_principle_evidence=evidence,
            brand_statement=brand_statement,
            unique_positioning=unique_positioning,
            identity_keywords=identity_keywords,
            aptitude_keywords=aptitude_keywords,
            passion_keywords=passion_keywords,
            service_keywords=service_keywords,
            scores=scores,
        )

    def _extract_first_principle(
        self,
        raw_passion: Dict[str, Any]
    ) -> Tuple[FirstPrinciplePassion, List[str]]:
        """
        Jenny's core insight: Find what the student fundamentally IS

        Huda example: She does CS, games, film - but fundamentally she's a BUILDER
        """
        all_text = ' '.join([
            raw_passion.get('brag_text') or '',
            raw_passion.get('spike_description') or '',
            ' '.join(raw_passion.get('passion_keywords') or []),
        ]).lower()

        scores: Dict[FirstPrinciplePassion, int] = {}
        evidence: Dict[FirstPrinciplePassion, List[str]] = {}

        for principle, signals in self.FIRST_PRINCIPLE_SIGNALS.items():
            score = 0
            matches = []
            for signal in signals:
                if signal in all_text:
                    score += 1
                    matches.append(signal)
            scores[principle] = score
            evidence[principle] = matches

        # Get the highest scoring principle
        if not scores or max(scores.values()) == 0:
            return FirstPrinciplePassion.SCHOLAR, ["Default: intellectual curiosity assumed"]

        best_principle = max(scores, key=lambda x: scores[x])
        return best_principle, evidence[best_principle]

    def _synthesize_identity(self, raw_identity: Dict[str, Any]) -> str:
        """Create identity statement from raw data"""
        parts = []

        ethnicity = raw_identity.get('ethnicity')
        if ethnicity and ethnicity != 'PREFER_NOT_SAY':
            parts.append(ethnicity.lower().replace('_', ' '))

        if raw_identity.get('first_gen'):
            parts.append('first-generation')

        origin = raw_identity.get('geographic_origin')
        if origin:
            if origin == 'INTERNATIONAL':
                parts.append('international')
            elif origin == 'BAY_AREA':
                parts.append('Bay Area')
            elif origin:
                parts.append(origin)

        # Add self-described characteristics
        for desc in (raw_identity.get('self_described_identity') or [])[:2]:
            if desc and desc not in parts:
                parts.append(desc)

        if parts:
            return f"{', '.join(parts)} student"
        return "student with unique background"

    def _extract_identity_keywords(self, raw_identity: Dict[str, Any]) -> List[str]:
        """Extract keywords for filtering"""
        keywords = []

        ethnicity = raw_identity.get('ethnicity')
        if ethnicity:
            keywords.append(ethnicity.lower())

        religion = raw_identity.get('religion')
        if religion:
            keywords.append(religion.lower())

        if raw_identity.get('first_gen'):
            keywords.extend(['first-gen', 'first-generation'])

        keywords.extend(raw_identity.get('self_described_identity') or [])
        keywords.extend(raw_identity.get('communities_served') or [])

        return list(set(keywords))

    def _synthesize_aptitude(self, raw_aptitude: Dict[str, Any]) -> str:
        """Create aptitude statement from raw data"""
        skills = raw_aptitude.get('mentioned_skills') or []
        major = raw_aptitude.get('intended_major', '')

        if skills:
            return f"with skills in {', '.join(skills[:3])}"
        elif major:
            return f"pursuing {major}"
        return "with developing academic strengths"

    def _synthesize_passion(
        self,
        raw_passion: Dict[str, Any],
        first_principle: FirstPrinciplePassion
    ) -> str:
        """Create passion statement using first principle"""
        keywords = raw_passion.get('passion_keywords') or []

        # Use the first principle as the core
        statement = f"who is fundamentally a {first_principle.value}"

        # Add specific manifestations
        if keywords:
            manifestations = [kw for kw in keywords[:2] if kw != first_principle.value]
            if manifestations:
                statement += f" (expressed through {', '.join(manifestations)})"

        return statement

    def _synthesize_service(
        self,
        raw_service: Dict[str, Any],
        raw_identity: Dict[str, Any]
    ) -> str:
        """Create service statement, connecting to identity"""
        communities = raw_service.get('communities_served') or []
        description = raw_service.get('service_description', '')

        if communities:
            return f"serving {communities[0]}"
        elif description:
            truncated = description[:50] + '...' if len(description) > 50 else description
            return f"committed to {truncated}"

        # Default: connect to identity
        identity_keywords = raw_identity.get('self_described_identity') or []
        if identity_keywords:
            return "supporting others like them"

        return "contributing to community"

    def _create_brand_statement(
        self,
        identity: str,
        aptitude: str,
        passion: str,
        service: str
    ) -> str:
        """
        Create the Master Narrative brand statement

        Jenny's Formula:
        "As a [IDENTITY] [APTITUDE], I [PASSION] to [SERVICE]"

        Or: "A [first_principle] who uses [aptitude] to [service]"
        """
        # Clean up the statements
        identity = identity.rstrip(',. ')
        aptitude = aptitude.lstrip('with ').rstrip(',. ')
        passion = passion.lstrip('who is fundamentally a ').rstrip(',. ')
        service = service.lstrip('serving ').lstrip('committed to ').rstrip(',. ')

        # Construct the brand statement
        return f"A {identity} and {passion} who uses {aptitude} to serve {service}"

    def _create_unique_positioning(
        self,
        identity_kw: List[str],
        aptitude_kw: List[str],
        passion_kw: List[str],
        service_kw: List[str]
    ) -> str:
        """
        Jenny's Insight: "Only she can authentically bridge these specific gaps"
        """
        unique_elements = []

        if identity_kw:
            unique_elements.append(identity_kw[0])
        if aptitude_kw:
            unique_elements.append(aptitude_kw[0])
        if passion_kw:
            unique_elements.append(passion_kw[0])
        if service_kw:
            unique_elements.append(f"service to {service_kw[0]}")

        if len(unique_elements) >= 3:
            return (
                f"The intersection of {', '.join(unique_elements[:3])} creates "
                f"a unique positioning that no other applicant can authentically claim."
            )

        return "A distinctive combination of background, skills, and mission."

    def _score_narrative(
        self,
        raw_identity: Dict[str, Any],
        raw_aptitude: Dict[str, Any],
        raw_passion: Dict[str, Any],
        raw_service: Dict[str, Any],
        first_principle: FirstPrinciplePassion,
        evidence: List[str]
    ) -> NarrativeScores:
        """
        Score the narrative using Jenny's assessment framework
        Each dimension 1-10, total 40+ = transformative
        """
        scores = NarrativeScores()

        # Identity clarity (1-10)
        identity_score = 0
        if raw_identity.get('ethnicity'):
            identity_score += 2
        if raw_identity.get('first_gen'):
            identity_score += 2
        if raw_identity.get('geographic_origin'):
            identity_score += 2
        if raw_identity.get('self_described_identity'):
            identity_score += 2
        identity_score += min(2, len(raw_identity.get('family_structure') or []))
        scores.identity_clarity = min(10, identity_score)

        # Aptitude alignment (1-10)
        aptitude_score = 0
        if raw_aptitude.get('mentioned_skills'):
            aptitude_score += 3
        if raw_aptitude.get('intended_major'):
            aptitude_score += 2
        if raw_aptitude.get('academic_awards'):
            aptitude_score += 3
        aptitude_score += min(2, len(raw_aptitude.get('competitions_entered') or []))
        scores.aptitude_alignment = min(10, aptitude_score)

        # Passion authenticity (1-10)
        passion_score = 0
        if first_principle != FirstPrinciplePassion.SCHOLAR:
            passion_score += 3  # Has clear principle beyond default
        passion_score += min(4, len(evidence) * 2)  # Evidence strength
        if raw_passion.get('passion_keywords'):
            passion_score += 3
        scores.passion_authenticity = min(10, passion_score)

        # Service relevance (1-10)
        service_score = 0
        if raw_service.get('communities_served'):
            service_score += 4
        if raw_service.get('service_description'):
            service_score += 3
        service_leadership = raw_service.get('service_leadership')
        if service_leadership in ['REGIONAL', 'NATIONAL']:
            service_score += 3
        scores.service_relevance = min(10, service_score)

        # Narrative power (average of others, adjusted)
        base_power = (
            scores.identity_clarity +
            scores.aptitude_alignment +
            scores.passion_authenticity +
            scores.service_relevance
        ) / 4

        # Bonus if components connect well
        if (raw_identity.get('self_described_identity') and
                any(kw in str(raw_service) for kw in raw_identity['self_described_identity'])):
            base_power += 2

        scores.narrative_power = min(10, int(base_power))

        return scores


class NarrativeFilter:
    """
    Filters recommendations through the Master Narrative lens

    Jenny's Principle: "Every action must serve the narrative"
    """

    def __init__(self, narrative: MasterNarrative):
        self.narrative = narrative

    def filter_recommendation(
        self,
        recommendation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if a recommendation serves the narrative

        Returns:
        - alignment_score: 0-10 (how well it serves the narrative)
        - serves_narrative: True if score >= 3
        - alignment_reasons: Why it aligns (or doesn't)
        - serves_components: Which narrative components it serves
        """
        rec_text = f"{recommendation.get('name', '')} {recommendation.get('description', '')}".lower()

        score = 0
        reasons = []
        serves = {
            'identity': False,
            'aptitude': False,
            'passion': False,
            'service': False,
        }

        # Check identity alignment
        for kw in self.narrative.identity_keywords:
            if kw.lower() in rec_text:
                score += 2
                serves['identity'] = True
                reasons.append(f"Connects to {kw} identity")
                break

        # Check aptitude alignment
        for kw in self.narrative.aptitude_keywords:
            if kw.lower() in rec_text:
                score += 2
                serves['aptitude'] = True
                reasons.append(f"Uses {kw} skills")
                break

        # Check passion alignment (first principle is most important)
        if self.narrative.first_principle.value in rec_text:
            score += 3
            serves['passion'] = True
            reasons.append(f"Reinforces '{self.narrative.first_principle.value}' core identity")
        else:
            for kw in self.narrative.passion_keywords:
                if kw.lower() in rec_text:
                    score += 2
                    serves['passion'] = True
                    reasons.append(f"Aligns with {kw} passion")
                    break

        # Check service alignment
        for kw in self.narrative.service_keywords:
            if kw.lower() in rec_text:
                score += 3
                serves['service'] = True
                reasons.append(f"Serves {kw}")
                break

        # Bonus for serving multiple components
        components_served = sum(serves.values())
        if components_served >= 3:
            score += 2
            reasons.append("Strong multi-component alignment")

        return {
            'alignment_score': min(10, score),
            'serves_narrative': score >= 3,
            'alignment_reasons': reasons if reasons else ['No clear narrative connection'],
            'serves_components': serves,
            'components_served_count': components_served,
        }

    def filter_recommendations(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter and sort a list of recommendations by narrative alignment
        Only returns those that serve the narrative (score >= 3)
        """
        filtered = []

        for rec in recommendations:
            alignment = self.filter_recommendation(rec)

            if alignment['serves_narrative']:
                filtered.append({
                    **rec,
                    'narrative_alignment': alignment,
                })

        # Sort by alignment score (highest first)
        filtered.sort(
            key=lambda x: x['narrative_alignment']['alignment_score'],
            reverse=True
        )

        return filtered

    def validate_gameplan_coherence(
        self,
        activities: List[Dict[str, Any]],
        awards: List[Dict[str, Any]],
        programs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate that the entire game plan coheres around the narrative

        Jenny's Check: "Does every recommendation serve the brand?"
        """
        all_recs = activities + awards + programs

        aligned = 0
        strongly_aligned = 0
        weak_recs = []

        for rec in all_recs:
            alignment = self.filter_recommendation(rec)
            if alignment['serves_narrative']:
                aligned += 1
                if alignment['alignment_score'] >= 6:
                    strongly_aligned += 1
            else:
                weak_recs.append({
                    'name': rec.get('name', 'Unknown'),
                    'issue': 'Does not serve the master narrative',
                    'score': alignment['alignment_score'],
                })

        total = len(all_recs) if all_recs else 1
        coherence_score = (aligned / total) * 100

        return {
            'coherence_score': round(coherence_score, 1),
            'total_recommendations': len(all_recs),
            'aligned_count': aligned,
            'strongly_aligned_count': strongly_aligned,
            'weak_recommendations': weak_recs[:5],  # Top 5 weakest
            'verdict': self._get_coherence_verdict(coherence_score),
            'master_narrative': self.narrative.brand_statement,
        }

    def _get_coherence_verdict(self, score: float) -> str:
        if score >= 90:
            return "Excellent - All recommendations reinforce the narrative"
        elif score >= 75:
            return "Good - Strong narrative coherence"
        elif score >= 60:
            return "Fair - Some recommendations don't serve the narrative"
        else:
            return "Weak - Game plan lacks narrative coherence"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'FirstPrinciplePassion',
    'NarrativeScores',
    'MasterNarrative',
    'NarrativeSynthesizer',
    'NarrativeFilter',
]
