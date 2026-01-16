"""
Golden Examples Database for True ReAct Framework
==================================================

This module contains successful student profile examples that serve as
benchmarks for quality comparison. Golden examples are profiles that
achieved target outcomes (college admissions) and represent high-quality
outputs from our agents.

Each golden example includes:
- Input profile (activities, demographics, interests)
- Expected agent output (spike, archetype, recommendations)
- Quality metrics (specificity, confidence, coherence)
- College outcomes (where they got in)

Usage:
    from agents.core.golden_examples_db import GoldenExamplesDB

    db = GoldenExamplesDB()
    examples = db.get_examples_by_archetype("stem_innovator")
    benchmark = db.get_benchmark_metrics("stem_innovator")
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class GoldenProfile:
    """A successful student profile that serves as a benchmark."""
    id: str
    name: str  # Anonymized name
    archetype: str
    spike: str
    spike_specificity: float  # 0-1 how specific the spike is
    archetype_confidence: float  # 0-1 how clear the archetype is

    # Profile details
    grade: int
    gpa: float
    test_scores: Dict[str, int]
    activities: List[Dict[str, Any]]
    pillars: List[str]
    themes: List[str]

    # Outcomes
    colleges_applied: List[str]
    colleges_accepted: List[str]
    college_attended: str

    # Quality metrics that made this profile successful
    success_factors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "archetype": self.archetype,
            "spike": self.spike,
            "spike_specificity": self.spike_specificity,
            "archetype_confidence": self.archetype_confidence,
            "pillars": self.pillars,
            "themes": self.themes,
            "college_attended": self.college_attended,
            "success_factors": self.success_factors,
        }


@dataclass
class BenchmarkMetrics:
    """Target metrics for a given archetype based on golden examples."""
    archetype: str
    spike_specificity_min: float
    spike_specificity_target: float
    archetype_confidence_min: float
    archetype_confidence_target: float
    activity_count_min: int
    activity_count_target: int
    pillars_min: int
    pillars_target: int
    leadership_positions_target: int
    example_spikes: List[str]
    common_success_factors: List[str]
    target_colleges: List[str]


# =============================================================================
# GOLDEN EXAMPLES DATABASE
# =============================================================================

class GoldenExamplesDB:
    """
    Database of golden examples for quality benchmarking.

    Provides access to successful student profiles organized by archetype.
    """

    def __init__(self):
        """Initialize with hardcoded golden examples."""
        self._profiles: Dict[str, List[GoldenProfile]] = {}
        self._benchmarks: Dict[str, BenchmarkMetrics] = {}
        self._load_golden_examples()
        self._compute_benchmarks()

    def _load_golden_examples(self):
        """Load all golden examples into memory."""

        # =====================================================================
        # STEM INNOVATOR PROFILES
        # =====================================================================
        self._profiles["stem_innovator"] = [
            GoldenProfile(
                id="stem-001",
                name="Alex T.",
                archetype="stem_innovator",
                spike="Building AI-powered coding education tools for underserved K-12 students in rural areas",
                spike_specificity=0.92,
                archetype_confidence=0.88,
                grade=12,
                gpa=3.95,
                test_scores={"SAT": 1560, "SAT_Math": 800},
                activities=[
                    {
                        "name": "CodeBridge Nonprofit",
                        "description": "Founded nonprofit teaching Python to 500+ students in rural Oklahoma schools",
                        "category": "Technology",
                        "position": "Founder & CEO",
                        "hours_per_week": 15,
                        "impact_score": 95,
                        "tags": ["coding", "education", "nonprofit", "leadership"],
                    },
                    {
                        "name": "AI Research - Stanford Lab",
                        "description": "Research intern developing ML models for educational content personalization",
                        "category": "Research",
                        "position": "Research Intern",
                        "hours_per_week": 12,
                        "impact_score": 85,
                        "tags": ["AI", "research", "machine learning"],
                    },
                    {
                        "name": "USACO Platinum",
                        "description": "Achieved Platinum division in USA Computing Olympiad",
                        "category": "Competition",
                        "position": "Competitor",
                        "hours_per_week": 10,
                        "impact_score": 90,
                        "tags": ["programming", "competition", "algorithms"],
                    },
                    {
                        "name": "CS Teaching Assistant",
                        "description": "TA for AP Computer Science, mentored 30 students",
                        "category": "Teaching",
                        "position": "Teaching Assistant",
                        "hours_per_week": 5,
                        "impact_score": 70,
                        "tags": ["teaching", "mentorship", "computer science"],
                    },
                    {
                        "name": "Open Source Contributor",
                        "description": "Maintained educational Python libraries with 1000+ GitHub stars",
                        "category": "Technology",
                        "position": "Contributor",
                        "hours_per_week": 8,
                        "impact_score": 80,
                        "tags": ["open source", "programming", "community"],
                    },
                ],
                pillars=["Technology", "Education", "Research"],
                themes=["Democratizing tech education", "AI for social good", "Leadership"],
                colleges_applied=["MIT", "Stanford", "Harvard", "CMU", "Caltech"],
                colleges_accepted=["MIT", "Stanford", "CMU", "Caltech"],
                college_attended="MIT",
                success_factors=[
                    "Highly specific spike combining AI + education + underserved communities",
                    "Founded organization with measurable impact (500+ students)",
                    "National-level competition achievement (USACO Platinum)",
                    "Research experience at prestigious lab",
                    "Clear narrative thread connecting all activities",
                ],
            ),
            GoldenProfile(
                id="stem-002",
                name="Priya M.",
                archetype="stem_innovator",
                spike="Developing machine learning algorithms for early detection of skin cancer in diverse populations",
                spike_specificity=0.95,
                archetype_confidence=0.91,
                grade=12,
                gpa=4.0,
                test_scores={"SAT": 1580, "SAT_Math": 800},
                activities=[
                    {
                        "name": "Cancer Detection Research",
                        "description": "Published paper on ML skin cancer detection for skin of color, presented at AAAI",
                        "category": "Research",
                        "position": "Lead Researcher",
                        "hours_per_week": 20,
                        "impact_score": 98,
                        "tags": ["research", "machine learning", "healthcare", "publication"],
                    },
                    {
                        "name": "Science Olympiad Captain",
                        "description": "Led team to state championship, placed 2nd nationally in Disease Detectives",
                        "category": "Competition",
                        "position": "Captain",
                        "hours_per_week": 10,
                        "impact_score": 88,
                        "tags": ["science", "competition", "leadership", "team"],
                    },
                    {
                        "name": "Hospital Volunteer",
                        "description": "200+ hours in oncology ward, observed disparities in care",
                        "category": "Healthcare",
                        "position": "Volunteer",
                        "hours_per_week": 5,
                        "impact_score": 75,
                        "tags": ["healthcare", "volunteer", "community"],
                    },
                    {
                        "name": "Girls Who Code Chapter",
                        "description": "Founded chapter teaching ML to 100+ girls from underrepresented backgrounds",
                        "category": "Technology",
                        "position": "Founder",
                        "hours_per_week": 8,
                        "impact_score": 85,
                        "tags": ["coding", "women in tech", "education", "leadership"],
                    },
                ],
                pillars=["Research", "Healthcare", "Technology"],
                themes=["Health equity through technology", "Women in STEM", "Scientific leadership"],
                colleges_applied=["Stanford", "MIT", "Harvard", "Yale", "Princeton"],
                colleges_accepted=["Stanford", "MIT", "Harvard", "Princeton"],
                college_attended="Stanford",
                success_factors=[
                    "Publication at top AI conference (AAAI)",
                    "Spike addresses real healthcare disparity",
                    "Personal motivation connected to research",
                    "Balance of research excellence and community impact",
                    "Strong leadership in multiple contexts",
                ],
            ),
        ]

        # =====================================================================
        # COMMUNITY CHANGEMAKER PROFILES
        # =====================================================================
        self._profiles["community_changemaker"] = [
            GoldenProfile(
                id="community-001",
                name="Marcus J.",
                archetype="community_changemaker",
                spike="Addressing food insecurity in immigrant communities through culturally responsive mutual aid networks",
                spike_specificity=0.90,
                archetype_confidence=0.85,
                grade=12,
                gpa=3.85,
                test_scores={"SAT": 1480, "ACT": 33},
                activities=[
                    {
                        "name": "Community Kitchen Collective",
                        "description": "Founded mutual aid org serving 300 families/month with culturally appropriate food",
                        "category": "Nonprofit",
                        "position": "Founder & Director",
                        "hours_per_week": 20,
                        "impact_score": 95,
                        "tags": ["nonprofit", "food security", "community", "leadership"],
                    },
                    {
                        "name": "City Youth Council",
                        "description": "Elected representative advocating for youth food access programs",
                        "category": "Government",
                        "position": "Council Member",
                        "hours_per_week": 8,
                        "impact_score": 80,
                        "tags": ["government", "advocacy", "policy", "youth"],
                    },
                    {
                        "name": "Immigration Rights Volunteer",
                        "description": "Translated for 50+ families at legal clinics, helped 15 gain asylum",
                        "category": "Advocacy",
                        "position": "Volunteer Translator",
                        "hours_per_week": 6,
                        "impact_score": 85,
                        "tags": ["immigration", "translation", "legal", "volunteer"],
                    },
                    {
                        "name": "School Diversity Committee",
                        "description": "Led initiative to add ethnic foods to school cafeteria, passed district-wide",
                        "category": "Leadership",
                        "position": "Committee Chair",
                        "hours_per_week": 5,
                        "impact_score": 70,
                        "tags": ["leadership", "diversity", "food", "policy"],
                    },
                ],
                pillars=["Community Service", "Advocacy", "Policy"],
                themes=["Food justice", "Immigration support", "Systemic change"],
                colleges_applied=["Harvard", "Yale", "Stanford", "Brown", "Columbia"],
                colleges_accepted=["Yale", "Brown", "Columbia"],
                college_attended="Yale",
                success_factors=[
                    "Spike addresses specific community need with cultural competence",
                    "Measurable impact (300 families/month)",
                    "Connected personal identity to cause",
                    "Demonstrated policy-level change (district initiative)",
                    "Multiple leadership positions with clear progression",
                ],
            ),
            GoldenProfile(
                id="community-002",
                name="Aisha K.",
                archetype="community_changemaker",
                spike="Building mental health support systems for Muslim-American youth through peer counseling networks",
                spike_specificity=0.88,
                archetype_confidence=0.83,
                grade=12,
                gpa=3.90,
                test_scores={"ACT": 34},
                activities=[
                    {
                        "name": "Noor Peer Counseling",
                        "description": "Created peer counseling program for Muslim youth, trained 40 counselors across 10 mosques",
                        "category": "Mental Health",
                        "position": "Founder",
                        "hours_per_week": 15,
                        "impact_score": 92,
                        "tags": ["mental health", "nonprofit", "counseling", "faith"],
                    },
                    {
                        "name": "National Council on Muslim Affairs - Youth",
                        "description": "Youth liaison addressing mental health stigma in Muslim communities",
                        "category": "Advocacy",
                        "position": "Youth Liaison",
                        "hours_per_week": 8,
                        "impact_score": 78,
                        "tags": ["advocacy", "national", "mental health", "community"],
                    },
                    {
                        "name": "Crisis Text Line Counselor",
                        "description": "Certified counselor, completed 200+ conversations supporting youth in crisis",
                        "category": "Counseling",
                        "position": "Volunteer Counselor",
                        "hours_per_week": 6,
                        "impact_score": 80,
                        "tags": ["mental health", "crisis", "volunteer", "counseling"],
                    },
                    {
                        "name": "Interfaith Youth Council",
                        "description": "Bridge-builder between faith communities, organized mental health awareness events",
                        "category": "Community",
                        "position": "Council Member",
                        "hours_per_week": 4,
                        "impact_score": 65,
                        "tags": ["interfaith", "community", "events", "awareness"],
                    },
                ],
                pillars=["Mental Health", "Faith Community", "Advocacy"],
                themes=["Breaking stigma", "Cultural competence in care", "Youth empowerment"],
                colleges_applied=["Harvard", "Princeton", "Penn", "Duke", "Northwestern"],
                colleges_accepted=["Harvard", "Penn", "Duke"],
                college_attended="Harvard",
                success_factors=[
                    "Spike addresses underserved community need",
                    "Built scalable model (trained 40 counselors)",
                    "Professional certification shows commitment",
                    "National-level advocacy experience",
                    "Strong personal connection to cause",
                ],
            ),
        ]

        # =====================================================================
        # CREATIVE VISIONARY PROFILES
        # =====================================================================
        self._profiles["creative_visionary"] = [
            GoldenProfile(
                id="creative-001",
                name="Jordan W.",
                archetype="creative_visionary",
                spike="Creating interactive documentary films that amplify stories of climate refugees",
                spike_specificity=0.87,
                archetype_confidence=0.82,
                grade=12,
                gpa=3.75,
                test_scores={"SAT": 1450},
                activities=[
                    {
                        "name": "Climate Stories Project",
                        "description": "Directed 3 interactive documentaries on climate refugees, 100K+ views, featured at Sundance",
                        "category": "Film",
                        "position": "Director",
                        "hours_per_week": 18,
                        "impact_score": 95,
                        "tags": ["film", "documentary", "climate", "storytelling"],
                    },
                    {
                        "name": "School Film Club",
                        "description": "President, taught filmmaking to 50 students, launched annual festival",
                        "category": "Arts",
                        "position": "President",
                        "hours_per_week": 8,
                        "impact_score": 75,
                        "tags": ["film", "teaching", "leadership", "festival"],
                    },
                    {
                        "name": "Local News Internship",
                        "description": "Produced environmental segments, 2 won regional Emmy student award",
                        "category": "Media",
                        "position": "Intern Producer",
                        "hours_per_week": 10,
                        "impact_score": 85,
                        "tags": ["journalism", "media", "environment", "award"],
                    },
                    {
                        "name": "Sunrise Movement",
                        "description": "Created viral campaign videos with 500K+ combined views",
                        "category": "Activism",
                        "position": "Media Lead",
                        "hours_per_week": 6,
                        "impact_score": 80,
                        "tags": ["climate", "activism", "video", "social media"],
                    },
                ],
                pillars=["Film/Media", "Climate Activism", "Storytelling"],
                themes=["Visual storytelling for impact", "Climate justice", "Amplifying marginalized voices"],
                colleges_applied=["USC Film", "NYU Tisch", "Wesleyan", "Brown", "Northwestern"],
                colleges_accepted=["USC Film", "NYU Tisch", "Brown"],
                college_attended="USC Film",
                success_factors=[
                    "Major recognition (Sundance, Emmy)",
                    "Spike combines art form with social cause",
                    "Demonstrated reach (100K+ views)",
                    "Technical skill + social impact",
                    "Clear artistic voice and perspective",
                ],
            ),
        ]

        # =====================================================================
        # ENTREPRENEURIAL LEADER PROFILES
        # =====================================================================
        self._profiles["entrepreneurial_leader"] = [
            GoldenProfile(
                id="entrepreneur-001",
                name="David L.",
                archetype="entrepreneurial_leader",
                spike="Building sustainable fashion technology that helps small designers reduce waste by 60%",
                spike_specificity=0.89,
                archetype_confidence=0.86,
                grade=12,
                gpa=3.80,
                test_scores={"SAT": 1520},
                activities=[
                    {
                        "name": "EcoThread (Startup)",
                        "description": "Founded B2B SaaS for sustainable fashion, $50K revenue, 30 designer clients",
                        "category": "Business",
                        "position": "Founder & CEO",
                        "hours_per_week": 25,
                        "impact_score": 95,
                        "tags": ["startup", "sustainability", "fashion", "technology"],
                    },
                    {
                        "name": "DECA",
                        "description": "State champion in Business Services Marketing, ICDC qualifier",
                        "category": "Competition",
                        "position": "Competitor",
                        "hours_per_week": 8,
                        "impact_score": 82,
                        "tags": ["business", "competition", "marketing"],
                    },
                    {
                        "name": "Junior Achievement Company",
                        "description": "Led team of 12 to create and sell sustainable products, $8K profit donated",
                        "category": "Business",
                        "position": "CEO",
                        "hours_per_week": 6,
                        "impact_score": 75,
                        "tags": ["business", "leadership", "team", "nonprofit"],
                    },
                    {
                        "name": "Sustainability Council",
                        "description": "Led school initiative reducing waste by 40%, saved district $15K annually",
                        "category": "Leadership",
                        "position": "Chair",
                        "hours_per_week": 5,
                        "impact_score": 70,
                        "tags": ["sustainability", "leadership", "school"],
                    },
                ],
                pillars=["Entrepreneurship", "Sustainability", "Technology"],
                themes=["Tech for sustainable business", "Youth entrepreneurship", "Environmental impact"],
                colleges_applied=["Wharton", "MIT", "Stanford", "Berkeley Haas", "Babson"],
                colleges_accepted=["Wharton", "MIT", "Berkeley Haas", "Babson"],
                college_attended="Wharton",
                success_factors=[
                    "Real business with real revenue ($50K)",
                    "Measurable environmental impact (60% waste reduction)",
                    "Spike at intersection of tech + sustainability + business",
                    "Competition success validates business acumen",
                    "Pattern of leadership at increasing scale",
                ],
            ),
        ]

        # =====================================================================
        # RESEARCH SCHOLAR PROFILES
        # =====================================================================
        self._profiles["research_scholar"] = [
            GoldenProfile(
                id="scholar-001",
                name="Emily C.",
                archetype="research_scholar",
                spike="Investigating novel approaches to Alzheimer's detection through biomarker analysis in cerebrospinal fluid",
                spike_specificity=0.93,
                archetype_confidence=0.90,
                grade=12,
                gpa=4.0,
                test_scores={"SAT": 1570},
                activities=[
                    {
                        "name": "Neuroscience Research - University Lab",
                        "description": "Co-authored paper in Journal of Neurochemistry, 3rd author",
                        "category": "Research",
                        "position": "Research Assistant",
                        "hours_per_week": 15,
                        "impact_score": 95,
                        "tags": ["research", "neuroscience", "publication", "lab"],
                    },
                    {
                        "name": "Regeneron STS Semifinalist",
                        "description": "Top 300 nationally for Alzheimer's biomarker research project",
                        "category": "Competition",
                        "position": "Semifinalist",
                        "hours_per_week": 12,
                        "impact_score": 90,
                        "tags": ["research", "competition", "national", "science"],
                    },
                    {
                        "name": "Science Research Club",
                        "description": "President, mentored 20 students on research methodology",
                        "category": "Leadership",
                        "position": "President",
                        "hours_per_week": 6,
                        "impact_score": 72,
                        "tags": ["leadership", "mentorship", "research", "teaching"],
                    },
                    {
                        "name": "Hospital Volunteer - Memory Care",
                        "description": "150 hours with Alzheimer's patients, deepened research motivation",
                        "category": "Volunteer",
                        "position": "Volunteer",
                        "hours_per_week": 4,
                        "impact_score": 68,
                        "tags": ["healthcare", "volunteer", "Alzheimer's", "community"],
                    },
                ],
                pillars=["Research", "Neuroscience", "Healthcare"],
                themes=["Deep scientific inquiry", "Translational research", "Mentorship"],
                colleges_applied=["Harvard", "MIT", "Princeton", "Johns Hopkins", "Duke"],
                colleges_accepted=["Harvard", "MIT", "Princeton", "Johns Hopkins"],
                college_attended="Harvard",
                success_factors=[
                    "Peer-reviewed publication (Journal of Neurochemistry)",
                    "National research recognition (Regeneron STS)",
                    "Clear research focus with depth",
                    "Personal connection to research area",
                    "Mentorship showing commitment to field",
                ],
            ),
        ]

        # =====================================================================
        # UNDISCOVERED TALENT PROFILES (for testing edge cases)
        # =====================================================================
        self._profiles["undiscovered_talent"] = [
            GoldenProfile(
                id="undiscovered-001",
                name="Sarah M.",
                archetype="community_changemaker",  # Discovered archetype
                spike="Creating financial literacy programs for first-generation college-bound students in Title I schools",
                spike_specificity=0.82,
                archetype_confidence=0.75,
                grade=11,
                gpa=3.60,
                test_scores={"PSAT": 1280},
                activities=[
                    {
                        "name": "Part-time Job - Retail",
                        "description": "20 hrs/week to support family, developed financial management skills",
                        "category": "Work",
                        "position": "Sales Associate",
                        "hours_per_week": 20,
                        "impact_score": 60,
                        "tags": ["work", "responsibility", "financial"],
                    },
                    {
                        "name": "Sibling Caregiver",
                        "description": "Primary caregiver for 2 younger siblings after school",
                        "category": "Family",
                        "position": "Caregiver",
                        "hours_per_week": 15,
                        "impact_score": 55,
                        "tags": ["family", "responsibility", "leadership"],
                    },
                    {
                        "name": "Financial Literacy Club",
                        "description": "Started club teaching budgeting to 25 classmates",
                        "category": "Education",
                        "position": "Founder",
                        "hours_per_week": 3,
                        "impact_score": 70,
                        "tags": ["finance", "education", "leadership", "teaching"],
                    },
                ],
                pillars=["Financial Literacy", "Family Responsibility", "Education"],
                themes=["First-gen experience", "Financial empowerment", "Community teaching"],
                colleges_applied=["QuestBridge", "State University"],
                colleges_accepted=["QuestBridge Match - Princeton"],
                college_attended="Princeton (QuestBridge)",
                success_factors=[
                    "Authentic story of overcoming circumstances",
                    "Leadership emerged from constraints",
                    "Turned personal challenge into community impact",
                    "Clear potential despite limited resources",
                    "Spike developed from lived experience",
                ],
            ),
        ]

    def _compute_benchmarks(self):
        """Compute benchmark metrics from golden examples."""
        for archetype, profiles in self._profiles.items():
            if not profiles:
                continue

            # Calculate averages and targets
            specificities = [p.spike_specificity for p in profiles]
            confidences = [p.archetype_confidence for p in profiles]
            activity_counts = [len(p.activities) for p in profiles]
            pillar_counts = [len(p.pillars) for p in profiles]

            avg_specificity = sum(specificities) / len(specificities)
            avg_confidence = sum(confidences) / len(confidences)
            avg_activities = sum(activity_counts) / len(activity_counts)
            avg_pillars = sum(pillar_counts) / len(pillar_counts)

            # Collect all example spikes and success factors
            all_spikes = [p.spike for p in profiles]
            all_factors = []
            for p in profiles:
                all_factors.extend(p.success_factors)
            all_colleges = []
            for p in profiles:
                all_colleges.append(p.college_attended)

            self._benchmarks[archetype] = BenchmarkMetrics(
                archetype=archetype,
                spike_specificity_min=0.70,
                spike_specificity_target=max(0.85, avg_specificity),
                archetype_confidence_min=0.65,
                archetype_confidence_target=max(0.80, avg_confidence),
                activity_count_min=4,
                activity_count_target=max(6, int(avg_activities)),
                pillars_min=2,
                pillars_target=max(3, int(avg_pillars)),
                leadership_positions_target=3,
                example_spikes=all_spikes[:3],
                common_success_factors=list(set(all_factors))[:5],
                target_colleges=list(set(all_colleges)),
            )

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def get_all_archetypes(self) -> List[str]:
        """Get list of all archetypes with golden examples."""
        return list(self._profiles.keys())

    def get_examples_by_archetype(self, archetype: str) -> List[GoldenProfile]:
        """
        Get golden examples for a specific archetype.

        Args:
            archetype: The archetype to get examples for

        Returns:
            List of GoldenProfile objects
        """
        archetype_key = archetype.lower().replace(" ", "_")
        return self._profiles.get(archetype_key, [])

    def get_benchmark_metrics(self, archetype: str) -> Optional[BenchmarkMetrics]:
        """
        Get benchmark metrics for a specific archetype.

        Args:
            archetype: The archetype to get benchmarks for

        Returns:
            BenchmarkMetrics object or None
        """
        archetype_key = archetype.lower().replace(" ", "_")
        return self._benchmarks.get(archetype_key)

    def get_example_spikes(self, archetype: str, limit: int = 3) -> List[str]:
        """
        Get example spikes for an archetype.

        Args:
            archetype: The archetype
            limit: Maximum number of spikes to return

        Returns:
            List of example spike strings
        """
        profiles = self.get_examples_by_archetype(archetype)
        return [p.spike for p in profiles[:limit]]

    def get_success_factors(self, archetype: str) -> List[str]:
        """
        Get common success factors for an archetype.

        Args:
            archetype: The archetype

        Returns:
            List of success factor strings
        """
        benchmark = self.get_benchmark_metrics(archetype)
        if benchmark:
            return benchmark.common_success_factors
        return []

    def compare_to_benchmark(
        self,
        profile: Dict[str, Any],
        archetype: str,
    ) -> Dict[str, Any]:
        """
        Compare a profile to benchmark metrics.

        Args:
            profile: The profile to compare
            archetype: The archetype to compare against

        Returns:
            Dict with gap analysis and recommendations
        """
        benchmark = self.get_benchmark_metrics(archetype)
        if not benchmark:
            return {
                "success": False,
                "error": f"No benchmark found for archetype: {archetype}",
            }

        # Calculate gaps
        gaps = {}

        # Spike specificity
        current_specificity = profile.get("spike_specificity", 0.5)
        gaps["spike_specificity"] = {
            "current": current_specificity,
            "target": benchmark.spike_specificity_target,
            "min": benchmark.spike_specificity_min,
            "gap": benchmark.spike_specificity_target - current_specificity,
            "meets_min": current_specificity >= benchmark.spike_specificity_min,
            "meets_target": current_specificity >= benchmark.spike_specificity_target,
        }

        # Archetype confidence
        current_confidence = profile.get("archetype_confidence", 0.5)
        gaps["archetype_confidence"] = {
            "current": current_confidence,
            "target": benchmark.archetype_confidence_target,
            "min": benchmark.archetype_confidence_min,
            "gap": benchmark.archetype_confidence_target - current_confidence,
            "meets_min": current_confidence >= benchmark.archetype_confidence_min,
            "meets_target": current_confidence >= benchmark.archetype_confidence_target,
        }

        # Activity count
        current_activities = len(profile.get("activities", []))
        gaps["activity_count"] = {
            "current": current_activities,
            "target": benchmark.activity_count_target,
            "min": benchmark.activity_count_min,
            "gap": benchmark.activity_count_target - current_activities,
            "meets_min": current_activities >= benchmark.activity_count_min,
            "meets_target": current_activities >= benchmark.activity_count_target,
        }

        # Pillars
        current_pillars = len(profile.get("pillars", []))
        gaps["pillars"] = {
            "current": current_pillars,
            "target": benchmark.pillars_target,
            "min": benchmark.pillars_min,
            "gap": benchmark.pillars_target - current_pillars,
            "meets_min": current_pillars >= benchmark.pillars_min,
            "meets_target": current_pillars >= benchmark.pillars_target,
        }

        # Calculate overall score
        met_targets = sum(1 for g in gaps.values() if g.get("meets_target", False))
        met_mins = sum(1 for g in gaps.values() if g.get("meets_min", False))
        total = len(gaps)

        overall_score = (met_targets / total * 0.6) + (met_mins / total * 0.4)

        # Generate recommendations
        recommendations = []
        for metric, gap_data in gaps.items():
            if not gap_data.get("meets_target", False):
                rec = self._generate_recommendation(metric, gap_data, benchmark)
                if rec:
                    recommendations.append(rec)

        return {
            "success": True,
            "overall_score": overall_score,
            "gaps": gaps,
            "recommendations": recommendations,
            "benchmark_spikes": benchmark.example_spikes,
            "success_factors": benchmark.common_success_factors,
            "target_colleges": benchmark.target_colleges,
        }

    def _generate_recommendation(
        self,
        metric: str,
        gap_data: Dict[str, Any],
        benchmark: BenchmarkMetrics,
    ) -> Optional[str]:
        """Generate a specific recommendation for a gap."""
        current = gap_data.get("current", 0)
        target = gap_data.get("target", 0)
        gap = gap_data.get("gap", 0)

        if metric == "spike_specificity":
            if gap > 0.15:
                return (
                    f"CRITICAL: Spike specificity ({current:.0%}) is significantly below target ({target:.0%}). "
                    f"Example successful spike: '{benchmark.example_spikes[0]}'. "
                    "Narrow your spike to a specific domain, population, and approach."
                )
            elif gap > 0:
                return (
                    f"Spike specificity ({current:.0%}) below target ({target:.0%}). "
                    "Consider adding specifics about WHO you serve, WHAT exactly you do, and WHY it matters."
                )

        elif metric == "archetype_confidence":
            if gap > 0.15:
                return (
                    f"CRITICAL: Archetype confidence ({current:.0%}) is low. "
                    "Activities don't clearly signal a coherent narrative. "
                    "Add 2-3 activities that strongly align with your primary archetype."
                )
            elif gap > 0:
                return (
                    f"Archetype confidence ({current:.0%}) could be stronger. "
                    "Consider deepening involvement in activities that align with your primary archetype."
                )

        elif metric == "activity_count":
            if gap > 2:
                return (
                    f"Activity count ({int(current)}) is below target ({int(target)}). "
                    f"Add {int(gap)} more activities aligned with your spike and archetype."
                )
            elif gap > 0:
                return (
                    f"Consider adding {int(gap)} more aligned activities to strengthen your profile."
                )

        elif metric == "pillars":
            if gap > 0:
                return (
                    f"Profile has {int(current)} pillars (target: {int(target)}). "
                    "Develop activities in a complementary area to create another strong pillar."
                )

        return None

    def get_hint_template(
        self,
        gap_type: str,
        gap_severity: str,  # "mild", "moderate", "severe"
        archetype: str,
    ) -> str:
        """
        Get a specific hint template for a gap type and severity.

        Args:
            gap_type: Type of gap (spike_specificity, archetype_confidence, etc.)
            gap_severity: Severity level
            archetype: Student archetype for context

        Returns:
            Formatted hint string
        """
        benchmark = self.get_benchmark_metrics(archetype)
        example_spike = benchmark.example_spikes[0] if benchmark and benchmark.example_spikes else ""

        templates = {
            "spike_specificity": {
                "mild": f"Spike specificity slightly below target. Add more specific details about your approach.",
                "moderate": f"Spike needs more specificity. Consider: WHO do you serve? WHAT exactly? Example: '{example_spike[:50]}...'",
                "severe": f"CRITICAL: Spike too generic. Replace with specific focus. Example: '{example_spike}'",
            },
            "archetype_confidence": {
                "mild": "Archetype signal could be stronger. Consider deepening top 2-3 activities.",
                "moderate": "Archetype unclear. Add activities that clearly align with your primary focus.",
                "severe": "CRITICAL: No clear archetype. Profile reads as scattered. Focus activities around one theme.",
            },
            "activity_count": {
                "mild": "Consider 1-2 more aligned activities.",
                "moderate": "Add 3-4 more activities aligned with your spike.",
                "severe": "CRITICAL: Insufficient activities. Need 4+ more to demonstrate commitment.",
            },
            "pillars": {
                "mild": "Consider developing one more distinct pillar.",
                "moderate": "Profile needs another strong pillar. Find complementary area.",
                "severe": "CRITICAL: No clear pillars. Group activities into 3 distinct areas.",
            },
        }

        return templates.get(gap_type, {}).get(gap_severity, "Improve this area of your profile.")


# =============================================================================
# MODULE SINGLETON
# =============================================================================

# Create singleton instance
_golden_db: Optional[GoldenExamplesDB] = None


def get_golden_examples_db() -> GoldenExamplesDB:
    """Get the singleton golden examples database."""
    global _golden_db
    if _golden_db is None:
        _golden_db = GoldenExamplesDB()
    return _golden_db
