"""
Agentic Tools Registry for True ReAct Framework
================================================

This module provides a registry of intelligent tools that agents can use
during the ACT phase of the ReAct loop. Each tool is designed to perform
specific analysis tasks that contribute to quality improvements.

Tools Available:
- archetype_classifier: Classify student into one of 8 archetypes
- spike_generator: Generate specific spike candidates
- theme_extractor: Extract dominant themes from activities
- golden_benchmark: Compare against successful profiles
- profile_inferencer: Infer missing profile data
- awards_matcher: Find archetype-fit awards
- programs_matcher: Find archetype-fit programs

Usage:
    from agents.core.agentic_tools import ToolRegistry

    registry = ToolRegistry()
    result = await registry.execute("archetype_classifier", profile_data)
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


# =============================================================================
# ARCHETYPES - The 8 Core Student Archetypes
# =============================================================================

class Archetype(Enum):
    """The 8 core student archetypes in IvyQuest."""
    STEM_INNOVATOR = "stem_innovator"
    COMMUNITY_CHANGEMAKER = "community_changemaker"
    CREATIVE_VISIONARY = "creative_visionary"
    POLICY_ADVOCATE = "policy_advocate"
    ENTREPRENEURIAL_LEADER = "entrepreneurial_leader"
    RESEARCH_SCHOLAR = "research_scholar"
    GLOBAL_CITIZEN = "global_citizen"
    ARTISTIC_VIRTUOSO = "artistic_virtuoso"


ARCHETYPE_KEYWORDS = {
    Archetype.STEM_INNOVATOR: [
        "coding", "programming", "robotics", "science", "math", "technology",
        "AI", "machine learning", "engineering", "research", "computer",
        "physics", "chemistry", "biology", "data", "algorithms", "hackathon",
        "olympiad", "competition", "lab", "experiment", "invention"
    ],
    Archetype.COMMUNITY_CHANGEMAKER: [
        "community", "service", "volunteer", "nonprofit", "social", "impact",
        "justice", "equity", "advocacy", "fundraising", "organize", "help",
        "mentor", "tutor", "underserved", "marginalized", "homeless", "food",
        "environment", "sustainability", "climate", "activism"
    ],
    Archetype.CREATIVE_VISIONARY: [
        "creative", "design", "art", "visual", "media", "film", "photography",
        "graphic", "animation", "UX", "UI", "product", "innovation", "startup",
        "app", "platform", "solution", "disrupt", "vision", "idea"
    ],
    Archetype.POLICY_ADVOCATE: [
        "policy", "government", "politics", "debate", "model UN", "law",
        "legislation", "advocacy", "rights", "democracy", "civic", "campaign",
        "election", "congress", "senate", "diplomacy", "international"
    ],
    Archetype.ENTREPRENEURIAL_LEADER: [
        "business", "entrepreneur", "startup", "company", "founder", "CEO",
        "revenue", "profit", "market", "customer", "product", "sales",
        "marketing", "leadership", "team", "management", "venture", "pitch"
    ],
    Archetype.RESEARCH_SCHOLAR: [
        "research", "paper", "publication", "journal", "academic", "professor",
        "PhD", "thesis", "hypothesis", "analysis", "study", "literature",
        "methodology", "peer-review", "conference", "symposium", "grant"
    ],
    Archetype.GLOBAL_CITIZEN: [
        "international", "global", "cultural", "exchange", "language", "abroad",
        "foreign", "diverse", "multicultural", "travel", "ambassador",
        "diplomatic", "cross-cultural", "UN", "NGO", "humanitarian"
    ],
    Archetype.ARTISTIC_VIRTUOSO: [
        "music", "instrument", "orchestra", "band", "choir", "performance",
        "recital", "composition", "theater", "drama", "dance", "ballet",
        "acting", "voice", "piano", "violin", "conservatory", "arts"
    ],
}

ARCHETYPE_DESCRIPTIONS = {
    Archetype.STEM_INNOVATOR: "Builds technical solutions to real problems. Shows depth in STEM through research, competitions, and original projects.",
    Archetype.COMMUNITY_CHANGEMAKER: "Drives measurable social impact. Demonstrates sustained commitment to a cause with leadership and scale.",
    Archetype.CREATIVE_VISIONARY: "Combines creativity with execution. Creates original work that reaches audiences and solves problems.",
    Archetype.POLICY_ADVOCATE: "Influences systems and policy. Shows civic engagement, debate skills, and understanding of governance.",
    Archetype.ENTREPRENEURIAL_LEADER: "Builds organizations and leads teams. Shows business acumen and ability to execute at scale.",
    Archetype.RESEARCH_SCHOLAR: "Pursues deep academic inquiry. Demonstrates intellectual curiosity through original research and publications.",
    Archetype.GLOBAL_CITIZEN: "Bridges cultures and perspectives. Shows international engagement and cross-cultural competence.",
    Archetype.ARTISTIC_VIRTUOSO: "Achieves excellence in performing/visual arts. Shows dedication, skill, and artistic growth.",
}


# =============================================================================
# TOOL RESULT DATACLASS
# =============================================================================

@dataclass
class ToolResult:
    """Result from executing an agentic tool."""
    tool_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    reasoning: str = ""
    suggestions: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "data": self.data,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "suggestions": self.suggestions,
            "error": self.error,
        }


# =============================================================================
# INDIVIDUAL TOOLS
# =============================================================================

class ArchetypeClassifierTool:
    """
    Classifies a student profile into one of the 8 archetypes.

    Uses keyword matching and activity analysis to determine the
    best-fit archetype with confidence scoring.
    """

    name = "archetype_classifier"
    description = "Classify student into one of 8 archetypes based on activities and interests"

    async def execute(self, profile: Dict[str, Any]) -> ToolResult:
        """
        Classify the student's archetype.

        Args:
            profile: Student profile with activities, interests, etc.

        Returns:
            ToolResult with archetype classification
        """
        activities = profile.get("activities", [])
        interests = profile.get("interests", [])
        academics = profile.get("academics", {})

        # Build text corpus from profile
        corpus = self._build_corpus(activities, interests, academics)

        # Score each archetype
        scores = {}
        for archetype, keywords in ARCHETYPE_KEYWORDS.items():
            score = self._calculate_match_score(corpus, keywords)
            scores[archetype] = score

        # Find top archetypes
        sorted_archetypes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_archetype = sorted_archetypes[0]
        secondary_archetype = sorted_archetypes[1] if len(sorted_archetypes) > 1 else None

        # Calculate confidence
        confidence = self._calculate_confidence(sorted_archetypes)

        # Build reasoning
        reasoning = self._build_reasoning(
            corpus, top_archetype, secondary_archetype, activities
        )

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "archetype": top_archetype[0].value,
                "archetype_confidence": confidence,
                "archetype_description": ARCHETYPE_DESCRIPTIONS[top_archetype[0]],
                "secondary_archetype": secondary_archetype[0].value if secondary_archetype else None,
                "secondary_confidence": secondary_archetype[1] / 100 if secondary_archetype else 0,
                "all_scores": {k.value: v for k, v in scores.items()},
            },
            confidence=confidence,
            reasoning=reasoning,
            suggestions=self._generate_suggestions(
                top_archetype[0], confidence, activities
            ),
        )

    def _build_corpus(
        self,
        activities: List[Dict],
        interests: List[str],
        academics: Dict,
    ) -> str:
        """Build text corpus from profile data."""
        parts = []

        # Activities
        for activity in activities:
            parts.append(activity.get("name", ""))
            parts.append(activity.get("description", ""))
            parts.append(activity.get("category", ""))
            parts.append(" ".join(activity.get("tags", [])))

        # Interests
        parts.extend(interests)

        # Academics
        if academics:
            parts.append(" ".join(academics.get("favorite_subjects", [])))
            parts.append(academics.get("academic_interest", ""))

        return " ".join(parts).lower()

    def _calculate_match_score(self, corpus: str, keywords: List[str]) -> float:
        """Calculate keyword match score."""
        matches = sum(1 for kw in keywords if kw.lower() in corpus)
        return (matches / len(keywords)) * 100 if keywords else 0

    def _calculate_confidence(
        self,
        sorted_archetypes: List[Tuple[Archetype, float]],
    ) -> float:
        """
        Calculate confidence based on score distribution.

        High confidence when top archetype clearly dominates.
        """
        if not sorted_archetypes:
            return 0.0

        top_score = sorted_archetypes[0][1]
        if len(sorted_archetypes) > 1:
            second_score = sorted_archetypes[1][1]
            # Larger gap = higher confidence
            gap = top_score - second_score
            base_confidence = min(top_score / 100, 1.0)
            gap_bonus = min(gap / 50, 0.3)  # Up to 30% bonus for large gap
            return min(base_confidence + gap_bonus, 1.0)

        return min(top_score / 100, 1.0)

    def _build_reasoning(
        self,
        corpus: str,
        top_archetype: Tuple[Archetype, float],
        secondary_archetype: Optional[Tuple[Archetype, float]],
        activities: List[Dict],
    ) -> str:
        """Build reasoning explanation."""
        arch_name = top_archetype[0].value.replace("_", " ").title()
        score = top_archetype[1]

        # Count activity types
        activity_count = len(activities)

        reasoning = f"Profile shows strongest alignment with {arch_name} archetype "
        reasoning += f"(score: {score:.1f}/100). "
        reasoning += f"Analysis based on {activity_count} activities. "

        if secondary_archetype and secondary_archetype[1] > 20:
            sec_name = secondary_archetype[0].value.replace("_", " ").title()
            reasoning += f"Secondary archetype: {sec_name} ({secondary_archetype[1]:.1f}/100)."

        return reasoning

    def _generate_suggestions(
        self,
        archetype: Archetype,
        confidence: float,
        activities: List[Dict],
    ) -> List[str]:
        """Generate suggestions based on classification."""
        suggestions = []

        if confidence < 0.7:
            suggestions.append(
                f"Archetype confidence is {confidence:.0%}. Consider adding more "
                f"activities that clearly align with {archetype.value.replace('_', ' ')}."
            )

        if confidence < 0.85:
            suggestions.append(
                "Consider deepening involvement in top 2-3 activities to "
                "strengthen archetype signal."
            )

        if len(activities) < 5:
            suggestions.append(
                "Profile has fewer than 5 activities. More activities would "
                "strengthen archetype classification."
            )

        return suggestions


class SpikeGeneratorTool:
    """
    Generates specific spike candidates for a student profile.

    A spike is a highly specific area of demonstrated excellence that
    differentiates the student. Good spikes are narrow, specific, and
    supported by evidence in the profile.
    """

    name = "spike_generator"
    description = "Generate specific spike candidates based on profile activities"

    # Templates for spike generation by archetype
    SPIKE_TEMPLATES = {
        Archetype.STEM_INNOVATOR: [
            "Building {tech} solutions for {problem} in {domain}",
            "Developing AI-powered {application} to help {beneficiary}",
            "Creating open-source {tool_type} for {use_case}",
            "Researching {tech_area} applications in {field}",
        ],
        Archetype.COMMUNITY_CHANGEMAKER: [
            "Addressing {issue} in {community} through {approach}",
            "Creating sustainable {solution_type} for {beneficiary}",
            "Mobilizing {group} to tackle {problem}",
            "Building bridges between {group1} and {group2}",
        ],
        Archetype.CREATIVE_VISIONARY: [
            "Designing {medium} experiences for {audience}",
            "Creating {art_form} that explores {theme}",
            "Building platforms that connect {group1} with {group2}",
            "Innovating in {field} through {approach}",
        ],
        Archetype.POLICY_ADVOCATE: [
            "Advocating for {policy_area} reform in {context}",
            "Building youth coalitions for {cause}",
            "Researching {policy_topic} impact on {population}",
            "Creating civic engagement initiatives for {group}",
        ],
        Archetype.ENTREPRENEURIAL_LEADER: [
            "Building ventures that solve {problem} for {market}",
            "Scaling {solution_type} to reach {scale}",
            "Creating sustainable business models for {cause}",
            "Leading teams to deliver {outcome}",
        ],
        Archetype.RESEARCH_SCHOLAR: [
            "Investigating {phenomenon} in {field}",
            "Developing novel approaches to {problem}",
            "Publishing research on {topic} implications",
            "Conducting experiments in {domain}",
        ],
        Archetype.GLOBAL_CITIZEN: [
            "Bridging {culture1} and {culture2} through {medium}",
            "Creating international initiatives for {cause}",
            "Developing cross-cultural {project_type}",
            "Addressing global {issue} at local scale",
        ],
        Archetype.ARTISTIC_VIRTUOSO: [
            "Performing {genre} that explores {theme}",
            "Composing {art_form} inspired by {influence}",
            "Teaching {skill} to {community}",
            "Creating original {medium} about {subject}",
        ],
    }

    async def execute(self, profile: Dict[str, Any]) -> ToolResult:
        """
        Generate spike candidates.

        Args:
            profile: Student profile with activities, archetype, etc.

        Returns:
            ToolResult with spike candidates
        """
        activities = profile.get("activities", [])
        archetype = profile.get("archetype", "stem_innovator")

        # Normalize archetype
        try:
            arch_enum = Archetype(archetype.lower().replace(" ", "_"))
        except ValueError:
            arch_enum = Archetype.STEM_INNOVATOR

        # Extract themes from activities
        themes = self._extract_themes(activities)

        # Generate spike candidates
        candidates = self._generate_candidates(arch_enum, activities, themes)

        # Score candidates
        scored_candidates = self._score_candidates(candidates, activities)

        # Select best spike
        if scored_candidates:
            best_spike = scored_candidates[0]
            specificity = best_spike["specificity_score"]
        else:
            best_spike = {"spike": "Exploring diverse interests across multiple domains", "specificity_score": 0.3}
            specificity = 0.3

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "spike": best_spike["spike"],
                "spike_specificity": specificity,
                "spike_candidates": scored_candidates[:3],
                "themes_extracted": themes,
                "supporting_activities": self._find_supporting_activities(
                    best_spike["spike"], activities
                ),
            },
            confidence=specificity,
            reasoning=self._build_reasoning(best_spike, themes, activities),
            suggestions=self._generate_suggestions(specificity, themes),
        )

    def _extract_themes(self, activities: List[Dict]) -> List[str]:
        """Extract dominant themes from activities."""
        theme_counts = {}

        for activity in activities:
            # Get category/tags
            category = activity.get("category", "")
            tags = activity.get("tags", [])

            if category:
                theme_counts[category] = theme_counts.get(category, 0) + 1

            for tag in tags:
                theme_counts[tag] = theme_counts.get(tag, 0) + 1

        # Sort by frequency
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, _ in sorted_themes[:5]]

    def _generate_candidates(
        self,
        archetype: Archetype,
        activities: List[Dict],
        themes: List[str],
    ) -> List[str]:
        """Generate spike candidates from templates and activities."""
        candidates = []

        # Extract specific elements from activities
        elements = self._extract_activity_elements(activities)

        # Generate from templates
        templates = self.SPIKE_TEMPLATES.get(archetype, [])
        for template in templates:
            try:
                # Simple placeholder filling
                spike = template
                for key, values in elements.items():
                    if values and f"{{{key}}}" in spike:
                        spike = spike.replace(f"{{{key}}}", values[0])

                # Only add if all placeholders filled
                if "{" not in spike:
                    candidates.append(spike)
            except Exception:
                continue

        # Generate activity-specific spikes
        for activity in activities[:3]:  # Top 3 activities
            name = activity.get("name", "")
            desc = activity.get("description", "")
            if name and desc:
                # Create specific spike from activity
                spike = f"{name}: {desc[:100]}"
                if len(spike) > 50:
                    candidates.append(spike)

        # Add theme-based spikes
        if themes:
            primary_theme = themes[0]
            secondary_theme = themes[1] if len(themes) > 1 else primary_theme
            candidates.append(
                f"Integrating {primary_theme} with {secondary_theme} "
                f"to create meaningful impact"
            )

        return candidates

    def _extract_activity_elements(self, activities: List[Dict]) -> Dict[str, List[str]]:
        """Extract reusable elements from activities."""
        elements = {
            "tech": [],
            "problem": [],
            "domain": [],
            "beneficiary": [],
            "community": [],
            "approach": [],
            "issue": [],
        }

        # Common mappings
        tech_words = ["app", "AI", "platform", "software", "algorithm", "data", "code"]
        problem_words = ["access", "inequality", "gap", "challenge", "need"]

        for activity in activities:
            desc = (activity.get("description", "") + " " + activity.get("name", "")).lower()

            # Extract tech elements
            for word in tech_words:
                if word.lower() in desc:
                    elements["tech"].append(word)

            # Extract problem elements
            for word in problem_words:
                if word.lower() in desc:
                    elements["problem"].append(word)

            # Extract beneficiaries (common patterns)
            if "student" in desc:
                elements["beneficiary"].append("students")
            if "youth" in desc or "teen" in desc:
                elements["beneficiary"].append("youth")
            if "underserved" in desc or "low-income" in desc:
                elements["beneficiary"].append("underserved communities")

        return elements

    def _score_candidates(
        self,
        candidates: List[str],
        activities: List[Dict],
    ) -> List[Dict]:
        """Score spike candidates by specificity and evidence."""
        scored = []

        for spike in candidates:
            # Calculate specificity score
            specificity = self._calculate_specificity(spike)

            # Calculate evidence score (how well supported by activities)
            evidence = self._calculate_evidence(spike, activities)

            # Combined score
            total = (specificity * 0.6) + (evidence * 0.4)

            scored.append({
                "spike": spike,
                "specificity_score": specificity,
                "evidence_score": evidence,
                "total_score": total,
            })

        # Sort by total score
        scored.sort(key=lambda x: x["total_score"], reverse=True)
        return scored

    def _calculate_specificity(self, spike: str) -> float:
        """
        Calculate how specific a spike is.

        Generic words reduce specificity. Specific details increase it.
        """
        generic_words = [
            "various", "multiple", "different", "many", "several",
            "exploring", "interested", "passionate", "diverse", "general"
        ]

        specific_indicators = [
            "AI", "K-12", "underserved", "low-income", "rural", "urban",
            "specific", "focused", "dedicated", "specialized", "targeted"
        ]

        # Base score
        score = 0.5

        # Penalize generic words
        spike_lower = spike.lower()
        for word in generic_words:
            if word in spike_lower:
                score -= 0.1

        # Reward specific indicators
        for word in specific_indicators:
            if word.lower() in spike_lower:
                score += 0.1

        # Reward specific numbers/metrics
        if any(char.isdigit() for char in spike):
            score += 0.1

        # Reward appropriate length (not too short, not too long)
        words = spike.split()
        if 8 <= len(words) <= 20:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _calculate_evidence(self, spike: str, activities: List[Dict]) -> float:
        """Calculate how well spike is supported by activities."""
        spike_words = set(spike.lower().split())

        max_overlap = 0
        for activity in activities:
            activity_text = (
                activity.get("name", "") + " " +
                activity.get("description", "") + " " +
                " ".join(activity.get("tags", []))
            ).lower()
            activity_words = set(activity_text.split())

            overlap = len(spike_words & activity_words)
            max_overlap = max(max_overlap, overlap)

        # Normalize
        return min(max_overlap / 5, 1.0)

    def _find_supporting_activities(
        self,
        spike: str,
        activities: List[Dict],
    ) -> List[str]:
        """Find activities that support the spike."""
        spike_words = set(spike.lower().split())
        supporting = []

        for activity in activities:
            activity_text = (activity.get("name", "") + " " + activity.get("description", "")).lower()
            activity_words = set(activity_text.split())

            if len(spike_words & activity_words) >= 2:
                supporting.append(activity.get("name", "Unknown"))

        return supporting[:3]

    def _build_reasoning(
        self,
        best_spike: Dict,
        themes: List[str],
        activities: List[Dict],
    ) -> str:
        """Build reasoning explanation."""
        specificity = best_spike.get("specificity_score", 0)
        spike = best_spike.get("spike", "")

        reasoning = f"Generated spike with {specificity:.0%} specificity. "
        reasoning += f"Primary themes: {', '.join(themes[:3])}. "
        reasoning += f"Based on {len(activities)} activities."

        if specificity < 0.7:
            reasoning += " Spike could be more specific."
        elif specificity >= 0.85:
            reasoning += " Spike is highly specific and differentiated."

        return reasoning

    def _generate_suggestions(
        self,
        specificity: float,
        themes: List[str],
    ) -> List[str]:
        """Generate suggestions for improving spike."""
        suggestions = []

        if specificity < 0.85:
            suggestions.append(
                f"Spike specificity is {specificity:.0%} (target: 85%). "
                "Consider narrowing to a more specific domain or population."
            )

        if len(themes) < 3:
            suggestions.append(
                "Profile shows limited thematic diversity. "
                "Adding 1-2 more theme-aligned activities could strengthen spike."
            )

        return suggestions


class ThemeExtractorTool:
    """
    Extracts dominant themes and pillars from a student profile.

    Pillars are the 3-5 main areas that define a student's profile.
    Themes are the underlying patterns that connect activities.
    """

    name = "theme_extractor"
    description = "Extract dominant themes and pillars from profile activities"

    async def execute(self, profile: Dict[str, Any]) -> ToolResult:
        """
        Extract themes and pillars.

        Args:
            profile: Student profile with activities

        Returns:
            ToolResult with themes and pillars
        """
        activities = profile.get("activities", [])

        # Extract categories and tags
        categories = self._extract_categories(activities)
        tags = self._extract_tags(activities)

        # Identify pillars (top 3-5 categories)
        pillars = self._identify_pillars(categories, activities)

        # Extract connecting themes
        themes = self._extract_themes(activities, pillars)

        # Calculate coherence
        coherence = self._calculate_coherence(pillars, themes)

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "pillars": pillars,
                "themes": themes,
                "coherence_score": coherence,
                "category_distribution": dict(categories),
                "tag_cloud": dict(tags),
            },
            confidence=coherence,
            reasoning=self._build_reasoning(pillars, themes, coherence),
            suggestions=self._generate_suggestions(pillars, coherence),
        )

    def _extract_categories(self, activities: List[Dict]) -> Dict[str, int]:
        """Extract category counts from activities."""
        categories = {}
        for activity in activities:
            cat = activity.get("category", "Other")
            categories[cat] = categories.get(cat, 0) + 1
        return categories

    def _extract_tags(self, activities: List[Dict]) -> Dict[str, int]:
        """Extract tag counts from activities."""
        tags = {}
        for activity in activities:
            for tag in activity.get("tags", []):
                tags[tag] = tags.get(tag, 0) + 1
        return tags

    def _identify_pillars(
        self,
        categories: Dict[str, int],
        activities: List[Dict],
    ) -> List[Dict]:
        """Identify top 3-5 pillars."""
        # Sort categories by count
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)

        pillars = []
        for cat, count in sorted_cats[:5]:
            # Find activities in this category
            cat_activities = [a for a in activities if a.get("category") == cat]

            # Calculate pillar strength
            strength = count / len(activities) if activities else 0

            pillars.append({
                "name": cat,
                "activity_count": count,
                "strength": strength,
                "activities": [a.get("name", "") for a in cat_activities[:3]],
            })

        return pillars

    def _extract_themes(
        self,
        activities: List[Dict],
        pillars: List[Dict],
    ) -> List[str]:
        """Extract connecting themes from activities."""
        themes = []

        # Theme: Leadership
        leadership_indicators = ["president", "founder", "captain", "leader", "director"]
        if any(
            any(ind in (a.get("name", "") + a.get("description", "")).lower() for ind in leadership_indicators)
            for a in activities
        ):
            themes.append("Leadership")

        # Theme: Social Impact
        impact_indicators = ["community", "service", "volunteer", "nonprofit", "help"]
        if any(
            any(ind in (a.get("name", "") + a.get("description", "")).lower() for ind in impact_indicators)
            for a in activities
        ):
            themes.append("Social Impact")

        # Theme: Innovation
        innovation_indicators = ["created", "built", "developed", "founded", "launched"]
        if any(
            any(ind in (a.get("name", "") + a.get("description", "")).lower() for ind in innovation_indicators)
            for a in activities
        ):
            themes.append("Innovation")

        # Theme: Academic Excellence
        academic_indicators = ["research", "olympiad", "competition", "award", "publication"]
        if any(
            any(ind in (a.get("name", "") + a.get("description", "")).lower() for ind in academic_indicators)
            for a in activities
        ):
            themes.append("Academic Excellence")

        return themes or ["Exploration"]

    def _calculate_coherence(
        self,
        pillars: List[Dict],
        themes: List[str],
    ) -> float:
        """Calculate profile coherence score."""
        if not pillars:
            return 0.3

        # Base coherence from pillar concentration
        top_pillar_strength = pillars[0]["strength"] if pillars else 0

        # Bonus for connecting themes
        theme_bonus = min(len(themes) * 0.1, 0.3)

        # Penalty for too many weak pillars
        weak_pillars = sum(1 for p in pillars if p["strength"] < 0.15)
        weak_penalty = weak_pillars * 0.05

        coherence = top_pillar_strength + theme_bonus - weak_penalty
        return max(0.3, min(1.0, coherence))

    def _build_reasoning(
        self,
        pillars: List[Dict],
        themes: List[str],
        coherence: float,
    ) -> str:
        """Build reasoning explanation."""
        pillar_names = [p["name"] for p in pillars[:3]]
        reasoning = f"Identified {len(pillars)} pillars: {', '.join(pillar_names)}. "
        reasoning += f"Connecting themes: {', '.join(themes)}. "
        reasoning += f"Profile coherence: {coherence:.0%}."

        if coherence < 0.6:
            reasoning += " Profile shows scattered focus."
        elif coherence >= 0.8:
            reasoning += " Profile shows strong thematic coherence."

        return reasoning

    def _generate_suggestions(
        self,
        pillars: List[Dict],
        coherence: float,
    ) -> List[str]:
        """Generate suggestions for improving themes."""
        suggestions = []

        if coherence < 0.7:
            suggestions.append(
                "Profile coherence is below target. Consider reducing "
                "breadth and increasing depth in top 2-3 pillars."
            )

        if len(pillars) < 3:
            suggestions.append(
                "Fewer than 3 distinct pillars identified. "
                "Consider developing activities in a complementary area."
            )

        if pillars and pillars[0]["strength"] < 0.3:
            suggestions.append(
                "No dominant pillar emerged. Consider concentrating "
                "more activities in primary interest area."
            )

        return suggestions


class GoldenBenchmarkTool:
    """
    Compares profile against successful student profiles (golden examples).

    Uses pattern matching to identify gaps between the current profile
    and profiles of students who achieved target outcomes.
    """

    name = "golden_benchmark"
    description = "Compare profile against successful student benchmarks"

    # Golden examples - these would typically come from a database
    # Inline here for the framework
    GOLDEN_PROFILES = {
        "stem_innovator": {
            "spike_specificity_target": 0.85,
            "archetype_confidence_target": 0.80,
            "pillars_target": 3,
            "activity_count_target": 8,
            "leadership_positions_target": 3,
            "example_spikes": [
                "Building AI-powered coding education tools for underserved K-12 students",
                "Developing machine learning solutions for early disease detection",
                "Creating robotics curriculum for rural schools",
            ],
            "success_indicators": [
                "Published research or patent",
                "National STEM competition placement",
                "Open source project with users",
                "Internship at tech company",
            ],
            "colleges": ["MIT", "Stanford", "Caltech", "CMU"],
        },
        "community_changemaker": {
            "spike_specificity_target": 0.85,
            "archetype_confidence_target": 0.80,
            "pillars_target": 3,
            "activity_count_target": 7,
            "leadership_positions_target": 4,
            "example_spikes": [
                "Addressing food insecurity in immigrant communities through mutual aid networks",
                "Building mental health support systems for LGBTQ+ youth",
                "Creating pathways for first-gen students to access college resources",
            ],
            "success_indicators": [
                "Nonprofit founded or led",
                "Measurable community impact (people served)",
                "Policy or systemic change achieved",
                "Recognition from established organizations",
            ],
            "colleges": ["Harvard", "Yale", "Princeton", "Brown"],
        },
    }

    async def execute(self, profile: Dict[str, Any]) -> ToolResult:
        """
        Benchmark profile against golden examples.

        Args:
            profile: Student profile to benchmark

        Returns:
            ToolResult with gap analysis
        """
        archetype = profile.get("archetype", "stem_innovator")
        golden = self.GOLDEN_PROFILES.get(archetype, self.GOLDEN_PROFILES["stem_innovator"])

        # Calculate gaps
        gaps = self._calculate_gaps(profile, golden)

        # Calculate overall similarity
        similarity = self._calculate_similarity(gaps)

        # Generate specific recommendations
        recommendations = self._generate_recommendations(gaps, golden)

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "similarity_score": similarity,
                "gaps": gaps,
                "golden_targets": {
                    "spike_specificity": golden["spike_specificity_target"],
                    "archetype_confidence": golden["archetype_confidence_target"],
                    "pillars": golden["pillars_target"],
                    "activity_count": golden["activity_count_target"],
                },
                "example_spikes": golden["example_spikes"],
                "success_indicators": golden["success_indicators"],
                "target_colleges": golden["colleges"],
            },
            confidence=similarity,
            reasoning=self._build_reasoning(similarity, gaps),
            suggestions=recommendations,
        )

    def _calculate_gaps(self, profile: Dict[str, Any], golden: Dict) -> Dict[str, Dict]:
        """Calculate gaps between profile and golden benchmark."""
        gaps = {}

        # Spike specificity gap
        current_specificity = profile.get("spike_specificity", 0.5)
        target_specificity = golden["spike_specificity_target"]
        gaps["spike_specificity"] = {
            "current": current_specificity,
            "target": target_specificity,
            "gap": target_specificity - current_specificity,
            "met": current_specificity >= target_specificity,
        }

        # Archetype confidence gap
        current_confidence = profile.get("archetype_confidence", 0.5)
        target_confidence = golden["archetype_confidence_target"]
        gaps["archetype_confidence"] = {
            "current": current_confidence,
            "target": target_confidence,
            "gap": target_confidence - current_confidence,
            "met": current_confidence >= target_confidence,
        }

        # Activity count gap
        current_activities = len(profile.get("activities", []))
        target_activities = golden["activity_count_target"]
        gaps["activity_count"] = {
            "current": current_activities,
            "target": target_activities,
            "gap": target_activities - current_activities,
            "met": current_activities >= target_activities,
        }

        # Pillars gap
        current_pillars = len(profile.get("pillars", []))
        target_pillars = golden["pillars_target"]
        gaps["pillars"] = {
            "current": current_pillars,
            "target": target_pillars,
            "gap": target_pillars - current_pillars,
            "met": current_pillars >= target_pillars,
        }

        return gaps

    def _calculate_similarity(self, gaps: Dict[str, Dict]) -> float:
        """Calculate overall similarity score."""
        if not gaps:
            return 0.5

        met_count = sum(1 for g in gaps.values() if g.get("met", False))
        total = len(gaps)

        # Base score from met criteria
        base_score = met_count / total if total else 0.5

        # Adjust based on gap severity
        total_gap = sum(abs(g.get("gap", 0)) for g in gaps.values())
        gap_penalty = min(total_gap * 0.1, 0.3)

        return max(0.3, min(1.0, base_score - gap_penalty + 0.3))

    def _generate_recommendations(
        self,
        gaps: Dict[str, Dict],
        golden: Dict,
    ) -> List[str]:
        """Generate specific recommendations based on gaps."""
        recommendations = []

        for metric, gap_data in gaps.items():
            if not gap_data.get("met", False):
                gap = gap_data.get("gap", 0)
                current = gap_data.get("current", 0)
                target = gap_data.get("target", 0)

                if metric == "spike_specificity":
                    recommendations.append(
                        f"Spike specificity is {current:.0%} (target: {target:.0%}). "
                        f"Consider: {golden['example_spikes'][0]}"
                    )
                elif metric == "archetype_confidence":
                    recommendations.append(
                        f"Archetype confidence is {current:.0%} (target: {target:.0%}). "
                        "Add 2-3 activities that strongly align with archetype."
                    )
                elif metric == "activity_count":
                    recommendations.append(
                        f"Activity count is {current} (target: {target}). "
                        f"Add {int(gap)} more aligned activities."
                    )
                elif metric == "pillars":
                    recommendations.append(
                        f"Pillar count is {current} (target: {target}). "
                        "Develop activities in a complementary area."
                    )

        return recommendations

    def _build_reasoning(self, similarity: float, gaps: Dict[str, Dict]) -> str:
        """Build reasoning explanation."""
        met_count = sum(1 for g in gaps.values() if g.get("met", False))
        total = len(gaps)

        reasoning = f"Profile similarity to golden benchmark: {similarity:.0%}. "
        reasoning += f"Meeting {met_count}/{total} target metrics. "

        unmet = [k for k, v in gaps.items() if not v.get("met", False)]
        if unmet:
            reasoning += f"Gaps in: {', '.join(unmet)}."
        else:
            reasoning += "All target metrics met."

        return reasoning


# =============================================================================
# v5.0: NEW TOOLS - Awards DB Search, Programs DB Search, Profile Inferencer
# =============================================================================

class AwardsDBSearchTool:
    """
    Searches awards database for archetype-fit awards.

    v5.0: Added for Awards Agent support.
    """

    name = "awards_db_search"
    description = "Search awards database for awards matching archetype and spike"

    # Award database (simplified - would come from real DB)
    AWARDS_DB = {
        "stem_innovator": [
            {"name": "Regeneron Science Talent Search", "tier": "reach", "alignment": 0.95},
            {"name": "USACO Platinum", "tier": "reach", "alignment": 0.90},
            {"name": "Google Science Fair", "tier": "reach", "alignment": 0.88},
            {"name": "National Science Bowl", "tier": "target", "alignment": 0.85},
            {"name": "AMC/AIME Qualifier", "tier": "target", "alignment": 0.80},
            {"name": "Regional STEM Competition", "tier": "safety", "alignment": 0.75},
        ],
        "community_changemaker": [
            {"name": "Presidential Volunteer Service Award Gold", "tier": "target", "alignment": 0.90},
            {"name": "Prudential Spirit of Community Award", "tier": "reach", "alignment": 0.88},
            {"name": "JFK Profile in Courage Essay Contest", "tier": "reach", "alignment": 0.85},
            {"name": "Local Community Service Award", "tier": "safety", "alignment": 0.80},
            {"name": "Nonprofit Board Recognition", "tier": "target", "alignment": 0.82},
        ],
        "creative_visionary": [
            {"name": "Scholastic Art & Writing Awards - Gold Key", "tier": "reach", "alignment": 0.92},
            {"name": "YoungArts Foundation Award", "tier": "reach", "alignment": 0.90},
            {"name": "Regional Portfolio Competition", "tier": "target", "alignment": 0.85},
            {"name": "School Art Show Award", "tier": "safety", "alignment": 0.75},
        ],
        "entrepreneurial_leader": [
            {"name": "DECA International Competition", "tier": "reach", "alignment": 0.90},
            {"name": "Diamond Challenge", "tier": "reach", "alignment": 0.88},
            {"name": "FBLA National Leadership Conference", "tier": "target", "alignment": 0.85},
            {"name": "Local Business Plan Competition", "tier": "safety", "alignment": 0.78},
        ],
    }

    async def execute(self, profile: Dict[str, Any]) -> ToolResult:
        """Search awards for profile."""
        archetype = profile.get("archetype", "stem_innovator")
        spike = profile.get("spike", "")

        # Get awards for archetype
        awards = self.AWARDS_DB.get(archetype, self.AWARDS_DB["stem_innovator"])

        # Adjust alignment based on spike match
        scored_awards = []
        for award in awards:
            alignment = award["alignment"]

            # Boost if spike keywords match award name
            if spike:
                spike_words = spike.lower().split()
                award_name = award["name"].lower()
                matches = sum(1 for word in spike_words if word in award_name)
                if matches > 0:
                    alignment = min(1.0, alignment + 0.05 * matches)

            scored_awards.append({
                **award,
                "adjusted_alignment": alignment,
            })

        # Sort by alignment
        scored_awards.sort(key=lambda x: x["adjusted_alignment"], reverse=True)

        # Organize by tier
        reach = [a for a in scored_awards if a["tier"] == "reach"][:2]
        target = [a for a in scored_awards if a["tier"] == "target"][:2]
        safety = [a for a in scored_awards if a["tier"] == "safety"][:1]

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "reach_awards": reach,
                "target_awards": target,
                "safety_awards": safety,
                "total_found": len(scored_awards),
                "archetype_used": archetype,
            },
            confidence=0.85,
            reasoning=f"Found {len(scored_awards)} awards for {archetype} archetype",
            suggestions=[
                f"Top reach award: {reach[0]['name']}" if reach else "No reach awards found",
                "Apply to 2-2-1 portfolio (2 reach, 2 target, 1 safety)",
            ],
        )


class ProgramsDBSearchTool:
    """
    Searches programs database for archetype-fit programs.

    v5.0: Added for Programs Agent support.
    """

    name = "programs_db_search"
    description = "Search programs database for programs matching archetype and constraints"

    # Programs database (simplified - would come from real DB)
    PROGRAMS_DB = {
        "stem_innovator": [
            {"name": "MIT PRIMES", "type": "research", "cost": 0, "selectivity": "reach", "duration": "year-long"},
            {"name": "RSI (Research Science Institute)", "type": "research", "cost": 0, "selectivity": "reach", "duration": "6 weeks"},
            {"name": "Stanford SIMR", "type": "research", "cost": 0, "selectivity": "target", "duration": "8 weeks"},
            {"name": "CMU Pre-College", "type": "academic", "cost": 8000, "selectivity": "safety", "duration": "6 weeks"},
        ],
        "community_changemaker": [
            {"name": "TASP (Telluride Association)", "type": "seminar", "cost": 0, "selectivity": "reach", "duration": "6 weeks"},
            {"name": "Bank of America Student Leaders", "type": "leadership", "cost": 0, "selectivity": "target", "duration": "8 weeks"},
            {"name": "Local Community Foundation Fellowship", "type": "service", "cost": 0, "selectivity": "safety", "duration": "summer"},
        ],
        "entrepreneurial_leader": [
            {"name": "LaunchX", "type": "entrepreneurship", "cost": 5000, "selectivity": "target", "duration": "4 weeks"},
            {"name": "NSLC Business", "type": "leadership", "cost": 3500, "selectivity": "safety", "duration": "10 days"},
        ],
    }

    async def execute(self, profile: Dict[str, Any]) -> ToolResult:
        """Search programs for profile."""
        archetype = profile.get("archetype", "stem_innovator")
        constraints = profile.get("constraints", {})

        # Get budget constraint
        max_budget = constraints.get("budget", 10000)
        require_free = constraints.get("require_free", False)

        # Get programs for archetype
        programs = self.PROGRAMS_DB.get(archetype, self.PROGRAMS_DB["stem_innovator"])

        # Filter by constraints
        filtered = []
        for prog in programs:
            cost = prog["cost"]
            if require_free and cost > 0:
                continue
            if cost > max_budget:
                continue
            filtered.append(prog)

        # Sort by selectivity (reach first)
        selectivity_order = {"reach": 0, "target": 1, "safety": 2}
        filtered.sort(key=lambda x: selectivity_order.get(x["selectivity"], 3))

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "programs": filtered,
                "total_found": len(filtered),
                "archetype_used": archetype,
                "constraints_applied": {
                    "max_budget": max_budget,
                    "require_free": require_free,
                },
            },
            confidence=0.85,
            reasoning=f"Found {len(filtered)} programs matching constraints for {archetype}",
            suggestions=[
                f"Top program: {filtered[0]['name']}" if filtered else "No programs match constraints",
                "Consider mix of selectivity levels for balanced application strategy",
            ],
        )


class ProfileInferencerTool:
    """
    Infers missing profile data from available signals.

    v5.0: Added for handling sparse profiles.
    """

    name = "profile_inferencer"
    description = "Infer missing profile data from available signals"

    # Inference rules
    MAJOR_TO_ARCHETYPE = {
        "computer science": "stem_innovator",
        "engineering": "stem_innovator",
        "biology": "stem_innovator",
        "physics": "stem_innovator",
        "business": "entrepreneurial_leader",
        "economics": "entrepreneurial_leader",
        "art": "creative_visionary",
        "music": "creative_visionary",
        "political science": "community_changemaker",
        "sociology": "community_changemaker",
    }

    INTEREST_TO_ARCHETYPE = {
        "coding": "stem_innovator",
        "robotics": "stem_innovator",
        "research": "stem_innovator",
        "volunteering": "community_changemaker",
        "nonprofit": "community_changemaker",
        "startup": "entrepreneurial_leader",
        "design": "creative_visionary",
    }

    async def execute(self, profile: Dict[str, Any]) -> ToolResult:
        """Infer missing profile data."""
        inferred = {}
        confidence = 0.5

        # Get available signals
        major = profile.get("intended_major", "").lower()
        interests = [i.lower() for i in profile.get("interests", [])]
        activities = profile.get("activities", [])

        # Infer archetype from major
        if not profile.get("archetype"):
            for keyword, archetype in self.MAJOR_TO_ARCHETYPE.items():
                if keyword in major:
                    inferred["archetype"] = archetype
                    confidence += 0.2
                    break

            # Try interests if major didn't work
            if "archetype" not in inferred:
                for interest in interests:
                    for keyword, archetype in self.INTEREST_TO_ARCHETYPE.items():
                        if keyword in interest:
                            inferred["archetype"] = archetype
                            confidence += 0.15
                            break
                    if "archetype" in inferred:
                        break

        # Infer spike from activities
        if not profile.get("spike") and activities:
            top_activity = activities[0]
            name = top_activity.get("name", "")
            desc = top_activity.get("description", "")
            if name or desc:
                inferred["spike"] = f"{name}: {desc[:50]}" if desc else name
                confidence += 0.1

        # Infer pillars from activity categories
        if not profile.get("pillars") and activities:
            categories = [a.get("category", "general") for a in activities]
            unique_cats = list(set(categories))[:3]
            if unique_cats:
                inferred["pillars"] = unique_cats
                confidence += 0.1

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "inferred_fields": inferred,
                "fields_inferred": list(inferred.keys()),
                "inference_sources": {
                    "major": major,
                    "interests": interests,
                    "activities_count": len(activities),
                },
            },
            confidence=min(confidence, 0.85),
            reasoning=f"Inferred {len(inferred)} fields from profile signals",
            suggestions=[
                "Inferred data should be validated by user",
                "Add more activities for better inference",
            ] if inferred else ["Profile has sufficient data"],
        )


# =============================================================================
# TOOL REGISTRY
# =============================================================================

class ToolRegistry:
    """
    Registry of all available agentic tools.

    Provides tool discovery, selection, and execution.
    """

    def __init__(self):
        """Initialize tool registry with available tools."""
        self._tools: Dict[str, Any] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register all default tools."""
        self.register(ArchetypeClassifierTool())
        self.register(SpikeGeneratorTool())
        self.register(ThemeExtractorTool())
        self.register(GoldenBenchmarkTool())
        # v5.0: New tools for Awards, Programs, and Profile Inference
        self.register(AwardsDBSearchTool())
        self.register(ProgramsDBSearchTool())
        self.register(ProfileInferencerTool())

    def register(self, tool: Any):
        """Register a tool."""
        name = getattr(tool, "name", tool.__class__.__name__)
        self._tools[name] = tool
        logger.info(f"Registered tool: {name}")

    def get(self, name: str) -> Optional[Any]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools."""
        return [
            {
                "name": name,
                "description": getattr(tool, "description", "No description"),
            }
            for name, tool in self._tools.items()
        ]

    async def execute(self, tool_name: str, input_data: Dict[str, Any]) -> ToolResult:
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute
            input_data: Input data for the tool

        Returns:
            ToolResult from the tool
        """
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool '{tool_name}' not found",
            )

        try:
            result = await tool.execute(input_data)
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} - {e}")
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=str(e),
            )

    async def execute_multiple(
        self,
        tool_names: List[str],
        input_data: Dict[str, Any],
    ) -> List[ToolResult]:
        """
        v5.0: Execute multiple tools in sequence.

        Args:
            tool_names: List of tool names to execute
            input_data: Input data for all tools

        Returns:
            List of ToolResults from each tool
        """
        results = []
        accumulated_data = input_data.copy()

        for tool_name in tool_names:
            result = await self.execute(tool_name, accumulated_data)
            results.append(result)

            # Accumulate results for next tool
            if result.success and result.data:
                accumulated_data.update(result.data)

        return results

    def select_tools(
        self,
        agent_type: str,
        profile: Dict[str, Any],
    ) -> List[str]:
        """
        Select appropriate tools for an agent and profile.

        Args:
            agent_type: Type of agent (EC, Awards, Programs, GamePlan)
            profile: Student profile for context

        Returns:
            List of tool names to use
        """
        # v5.0: Updated tool selection with new tools
        tool_map = {
            "Extracurriculars": [
                "archetype_classifier",
                "spike_generator",
                "theme_extractor",
                "profile_inferencer",
            ],
            "Awards": [
                "archetype_classifier",
                "golden_benchmark",
                "awards_db_search",
            ],
            "Programs": [
                "archetype_classifier",
                "golden_benchmark",
                "programs_db_search",
            ],
            "GamePlan": [
                "archetype_classifier",
                "spike_generator",
                "theme_extractor",
                "golden_benchmark",
                "awards_db_search",
                "programs_db_search",
            ],
        }

        return tool_map.get(agent_type, ["archetype_classifier"])


# =============================================================================
# MODULE EXPORTS
# =============================================================================

# Create default registry instance
default_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the default tool registry."""
    return default_registry


async def execute_tool(tool_name: str, input_data: Dict[str, Any]) -> ToolResult:
    """Execute a tool using the default registry."""
    return await default_registry.execute(tool_name, input_data)
