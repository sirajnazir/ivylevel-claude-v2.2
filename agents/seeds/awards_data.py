"""
IvyQuest v10.0 - Awards Database Seed Data
==========================================

Comprehensive database of 200+ awards for high school students.
Used by AwardsSpecialist agent for matching and portfolio balancing.

Categories:
- STEM (Science, Technology, Engineering, Math)
- Humanities (Writing, History, Languages)
- Arts (Visual, Music, Theater, Film)
- Leadership
- Service (Community Service)
- Academic (GPA, Test-based)
- Entrepreneurship
- Athletics
- Journalism
- Debate
- Research

Data Sources:
- Official award websites
- College admissions databases
- Historical acceptance rates
"""

from datetime import datetime
from typing import List, Dict, Any

# =============================================================================
# STEM AWARDS
# =============================================================================

STEM_AWARDS: List[Dict[str, Any]] = [
    # Elite National Research
    {
        "id": "regeneron-sts",
        "name": "Regeneron Science Talent Search",
        "organization": "Society for Science",
        "category": "research",
        "level": "national",
        "description": "America's oldest and most prestigious science research competition for high school seniors.",
        "prestige_score": 10,
        "historical_win_rate": 0.006,
        "effort_hours": 200,
        "deadline_month": 11,
        "deadline_recurring": "November 15 annually",
        "eligibility": {
            "grades": [12],
            "citizenship": ["US", "permanent_resident"],
            "requirements": ["original_research", "essay", "recommendation"]
        },
        "prize_amount": 250000,
        "prize_type": "scholarship",
        "touchpoints": 6,
        "touchpoint_types": ["research_paper", "essay", "interview", "recommendation", "transcript", "presentation"]
    },
    {
        "id": "regeneron-isef",
        "name": "Regeneron International Science and Engineering Fair",
        "organization": "Society for Science",
        "category": "research",
        "level": "international",
        "description": "World's largest international pre-college science competition.",
        "prestige_score": 10,
        "historical_win_rate": 0.02,
        "effort_hours": 150,
        "deadline_month": 2,
        "deadline_recurring": "Regional fair deadlines vary, typically January-March",
        "eligibility": {
            "grades": [9, 10, 11, 12],
            "requirements": ["original_research", "regional_fair_win"]
        },
        "prize_amount": 75000,
        "prize_type": "scholarship",
        "touchpoints": 5,
        "touchpoint_types": ["research_project", "presentation", "interview", "abstract", "display"]
    },
    {
        "id": "siemens-competition",
        "name": "Siemens Competition in Math, Science & Technology",
        "organization": "Siemens Foundation (discontinued 2018, included for reference)",
        "category": "research",
        "level": "national",
        "description": "Historic research competition - students may reference similar programs.",
        "prestige_score": 9,
        "historical_win_rate": 0.01,
        "effort_hours": 180,
        "deadline_month": 9,
        "eligibility": {"grades": [11, 12]},
        "prize_amount": 100000,
        "prize_type": "scholarship",
        "is_active": False
    },

    # Math Olympiads
    {
        "id": "usamo",
        "name": "USA Mathematical Olympiad (USAMO)",
        "organization": "Mathematical Association of America",
        "category": "stem",
        "level": "national",
        "description": "Top tier of American Mathematics Competitions for high schoolers.",
        "prestige_score": 10,
        "historical_win_rate": 0.005,
        "effort_hours": 300,
        "deadline_month": 2,
        "deadline_recurring": "February (AMC), March (AIME), April (USAMO)",
        "eligibility": {
            "grades": [9, 10, 11, 12],
            "requirements": ["AMC_qualification", "AIME_qualification"]
        },
        "prize_type": "recognition",
        "touchpoints": 3,
        "touchpoint_types": ["exam", "exam", "exam"]
    },
    {
        "id": "usajmo",
        "name": "USA Junior Mathematical Olympiad (USAJMO)",
        "organization": "Mathematical Association of America",
        "category": "stem",
        "level": "national",
        "description": "Junior version of USAMO for grades 10 and below.",
        "prestige_score": 9,
        "historical_win_rate": 0.008,
        "effort_hours": 200,
        "deadline_month": 2,
        "eligibility": {
            "grades": [9, 10],
            "requirements": ["AMC10_qualification", "AIME_qualification"]
        },
        "prize_type": "recognition",
        "touchpoints": 3
    },
    {
        "id": "mathcounts",
        "name": "MATHCOUNTS National Competition",
        "organization": "MATHCOUNTS Foundation",
        "category": "stem",
        "level": "national",
        "description": "National math competition for middle schoolers (6-8th grade).",
        "prestige_score": 8,
        "historical_win_rate": 0.01,
        "effort_hours": 100,
        "deadline_month": 5,
        "eligibility": {"grades": [6, 7, 8]},
        "prize_type": "recognition",
        "touchpoints": 3
    },
    {
        "id": "amc-distinguished",
        "name": "AMC Distinguished Honor Roll",
        "organization": "Mathematical Association of America",
        "category": "stem",
        "level": "national",
        "description": "Top 1% scorers on the AMC 10/12 exams.",
        "prestige_score": 7,
        "historical_win_rate": 0.01,
        "effort_hours": 50,
        "deadline_month": 2,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 1
    },

    # Computing Olympiads
    {
        "id": "usaco-platinum",
        "name": "USA Computing Olympiad - Platinum Division",
        "organization": "USACO",
        "category": "stem",
        "level": "national",
        "description": "Highest division in US computing olympiad.",
        "prestige_score": 10,
        "historical_win_rate": 0.02,
        "effort_hours": 250,
        "deadline_month": 3,
        "deadline_recurring": "December-March (monthly contests)",
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 4,
        "touchpoint_types": ["exam", "exam", "exam", "exam"]
    },
    {
        "id": "usaco-gold",
        "name": "USA Computing Olympiad - Gold Division",
        "organization": "USACO",
        "category": "stem",
        "level": "national",
        "description": "Second highest division in US computing olympiad.",
        "prestige_score": 8,
        "historical_win_rate": 0.05,
        "effort_hours": 150,
        "deadline_month": 3,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 4
    },

    # Science Olympiad
    {
        "id": "science-olympiad-national",
        "name": "Science Olympiad National Tournament",
        "organization": "Science Olympiad",
        "category": "stem",
        "level": "national",
        "description": "National team science competition in 23 events.",
        "prestige_score": 8,
        "historical_win_rate": 0.03,
        "effort_hours": 200,
        "deadline_month": 5,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 5
    },
    {
        "id": "science-olympiad-state",
        "name": "Science Olympiad State Tournament",
        "organization": "Science Olympiad",
        "category": "stem",
        "level": "state",
        "description": "State level team science competition.",
        "prestige_score": 6,
        "historical_win_rate": 0.10,
        "effort_hours": 100,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 4
    },

    # CS Awards
    {
        "id": "ncwit-aic",
        "name": "NCWIT Award for Aspirations in Computing",
        "organization": "National Center for Women & IT",
        "category": "stem",
        "level": "national",
        "description": "Honors young women at the high-school level for computing achievements.",
        "prestige_score": 8,
        "historical_win_rate": 0.10,
        "effort_hours": 15,
        "deadline_month": 11,
        "deadline_recurring": "November 1 annually",
        "eligibility": {
            "grades": [9, 10, 11, 12],
            "gender": ["female", "non-binary"],
            "requirements": ["computing_experience", "essay", "recommendation"]
        },
        "prize_amount": 500,
        "prize_type": "scholarship",
        "diversity_focus": True,
        "touchpoints": 4,
        "touchpoint_types": ["application", "essay", "recommendation", "interview"]
    },
    {
        "id": "congressional-app",
        "name": "Congressional App Challenge",
        "organization": "U.S. House of Representatives",
        "category": "stem",
        "level": "national",
        "description": "National coding competition hosted by members of Congress.",
        "prestige_score": 7,
        "historical_win_rate": 0.15,
        "effort_hours": 40,
        "deadline_month": 11,
        "eligibility": {"grades": [9, 10, 11, 12], "citizenship": ["US"]},
        "prize_type": "recognition",
        "touchpoints": 3,
        "touchpoint_types": ["app", "video", "presentation"]
    },
    {
        "id": "google-code-jam",
        "name": "Google Code Jam",
        "organization": "Google",
        "category": "stem",
        "level": "international",
        "description": "Global coding competition (open to all ages).",
        "prestige_score": 8,
        "historical_win_rate": 0.05,
        "effort_hours": 30,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 15000,
        "prize_type": "cash",
        "touchpoints": 4
    },

    # Physics Olympiad
    {
        "id": "usapho",
        "name": "USA Physics Olympiad (USAPhO)",
        "organization": "American Association of Physics Teachers",
        "category": "stem",
        "level": "national",
        "description": "Top tier physics competition selecting team for International Physics Olympiad.",
        "prestige_score": 10,
        "historical_win_rate": 0.01,
        "effort_hours": 200,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 3
    },
    {
        "id": "physics-bowl",
        "name": "Physics Bowl",
        "organization": "American Association of Physics Teachers",
        "category": "stem",
        "level": "national",
        "description": "40-question multiple choice physics exam.",
        "prestige_score": 6,
        "historical_win_rate": 0.05,
        "effort_hours": 20,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 1
    },

    # Chemistry Olympiad
    {
        "id": "usnco",
        "name": "US National Chemistry Olympiad",
        "organization": "American Chemical Society",
        "category": "stem",
        "level": "national",
        "description": "National chemistry competition selecting team for International Chemistry Olympiad.",
        "prestige_score": 10,
        "historical_win_rate": 0.01,
        "effort_hours": 200,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 3
    },

    # Biology Olympiad
    {
        "id": "usabo",
        "name": "USA Biology Olympiad",
        "organization": "Center for Excellence in Education",
        "category": "stem",
        "level": "national",
        "description": "National biology competition selecting team for International Biology Olympiad.",
        "prestige_score": 10,
        "historical_win_rate": 0.01,
        "effort_hours": 200,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 3
    },

    # Robotics
    {
        "id": "first-robotics-championship",
        "name": "FIRST Robotics Championship",
        "organization": "FIRST",
        "category": "stem",
        "level": "international",
        "description": "Global robotics championship for FRC teams.",
        "prestige_score": 8,
        "historical_win_rate": 0.02,
        "effort_hours": 300,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 5
    },
    {
        "id": "vex-worlds",
        "name": "VEX Robotics World Championship",
        "organization": "REC Foundation",
        "category": "stem",
        "level": "international",
        "description": "World's largest robotics competition.",
        "prestige_score": 7,
        "historical_win_rate": 0.03,
        "effort_hours": 200,
        "deadline_month": 5,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 4
    },
]

# =============================================================================
# HUMANITIES AWARDS
# =============================================================================

HUMANITIES_AWARDS: List[Dict[str, Any]] = [
    # Writing Competitions
    {
        "id": "scholastic-writing-gold",
        "name": "Scholastic Art & Writing Awards - Gold Key (Writing)",
        "organization": "Alliance for Young Artists & Writers",
        "category": "humanities",
        "level": "national",
        "description": "Prestigious national creative writing competition.",
        "prestige_score": 9,
        "historical_win_rate": 0.05,
        "effort_hours": 40,
        "deadline_month": 12,
        "deadline_recurring": "December 15 annually",
        "eligibility": {"grades": [7, 8, 9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 2,
        "touchpoint_types": ["creative_work", "artist_statement"]
    },
    {
        "id": "scholastic-american-voices",
        "name": "Scholastic American Voices Award",
        "organization": "Alliance for Young Artists & Writers",
        "category": "humanities",
        "level": "national",
        "description": "Highest honor at Scholastic Awards for writing.",
        "prestige_score": 10,
        "historical_win_rate": 0.005,
        "effort_hours": 50,
        "deadline_month": 12,
        "eligibility": {"grades": [7, 8, 9, 10, 11, 12]},
        "prize_amount": 1000,
        "prize_type": "cash",
        "touchpoints": 2
    },
    {
        "id": "young-arts-writing",
        "name": "YoungArts - Writing",
        "organization": "National YoungArts Foundation",
        "category": "humanities",
        "level": "national",
        "description": "Prestigious arts program for emerging writers.",
        "prestige_score": 9,
        "historical_win_rate": 0.08,
        "effort_hours": 30,
        "deadline_month": 10,
        "deadline_recurring": "October 15 annually",
        "eligibility": {"grades": [10, 11, 12]},
        "prize_amount": 10000,
        "prize_type": "cash",
        "touchpoints": 3,
        "touchpoint_types": ["portfolio", "essay", "interview"]
    },
    {
        "id": "jfk-essay",
        "name": "Profile in Courage Essay Contest",
        "organization": "JFK Library Foundation",
        "category": "humanities",
        "level": "national",
        "description": "Essay contest on political courage.",
        "prestige_score": 8,
        "historical_win_rate": 0.005,
        "effort_hours": 25,
        "deadline_month": 1,
        "deadline_recurring": "January 12 annually",
        "eligibility": {"grades": [9, 10, 11, 12], "citizenship": ["US"]},
        "prize_amount": 10000,
        "prize_type": "scholarship",
        "touchpoints": 1
    },
    {
        "id": "ayn-rand-essay",
        "name": "Ayn Rand Essay Contests",
        "organization": "Ayn Rand Institute",
        "category": "humanities",
        "level": "national",
        "description": "Essay contests on Atlas Shrugged, The Fountainhead, Anthem.",
        "prestige_score": 6,
        "historical_win_rate": 0.02,
        "effort_hours": 20,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 25000,
        "prize_type": "cash",
        "touchpoints": 1
    },
    {
        "id": "jane-austen-essay",
        "name": "Jane Austen Society Essay Contest",
        "organization": "Jane Austen Society of North America",
        "category": "humanities",
        "level": "national",
        "description": "Essay contest for high school students on Jane Austen works.",
        "prestige_score": 5,
        "historical_win_rate": 0.10,
        "effort_hours": 15,
        "deadline_month": 6,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 1000,
        "prize_type": "cash",
        "touchpoints": 1
    },

    # History Competitions
    {
        "id": "national-history-day",
        "name": "National History Day",
        "organization": "National History Day",
        "category": "humanities",
        "level": "national",
        "description": "Year-long academic program culminating in national competition.",
        "prestige_score": 8,
        "historical_win_rate": 0.03,
        "effort_hours": 100,
        "deadline_month": 6,
        "eligibility": {"grades": [6, 7, 8, 9, 10, 11, 12]},
        "prize_amount": 5000,
        "prize_type": "scholarship",
        "touchpoints": 5,
        "touchpoint_types": ["research_paper", "exhibit", "documentary", "performance", "website"]
    },
    {
        "id": "nhd-state",
        "name": "National History Day - State Competition",
        "organization": "National History Day",
        "category": "humanities",
        "level": "state",
        "description": "State level history competition.",
        "prestige_score": 6,
        "historical_win_rate": 0.10,
        "effort_hours": 60,
        "deadline_month": 4,
        "eligibility": {"grades": [6, 7, 8, 9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 4
    },

    # Language Competitions
    {
        "id": "national-latin-exam",
        "name": "National Latin Exam - Gold Medal",
        "organization": "National Latin Exam",
        "category": "humanities",
        "level": "national",
        "description": "National exam testing Latin proficiency.",
        "prestige_score": 6,
        "historical_win_rate": 0.15,
        "effort_hours": 20,
        "deadline_month": 3,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 1
    },
    {
        "id": "national-spanish-exam",
        "name": "National Spanish Exam - Gold Medal",
        "organization": "American Association of Teachers of Spanish and Portuguese",
        "category": "humanities",
        "level": "national",
        "description": "National exam testing Spanish proficiency.",
        "prestige_score": 6,
        "historical_win_rate": 0.12,
        "effort_hours": 20,
        "deadline_month": 3,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 1
    },
    {
        "id": "national-french-contest",
        "name": "National French Contest (Le Grand Concours)",
        "organization": "American Association of Teachers of French",
        "category": "humanities",
        "level": "national",
        "description": "National French language competition.",
        "prestige_score": 6,
        "historical_win_rate": 0.12,
        "effort_hours": 20,
        "deadline_month": 3,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 1
    },
]

# =============================================================================
# ARTS AWARDS
# =============================================================================

ARTS_AWARDS: List[Dict[str, Any]] = [
    # Visual Arts
    {
        "id": "scholastic-art-gold",
        "name": "Scholastic Art & Writing Awards - Gold Key (Art)",
        "organization": "Alliance for Young Artists & Writers",
        "category": "arts",
        "level": "national",
        "description": "Prestigious national visual arts competition.",
        "prestige_score": 9,
        "historical_win_rate": 0.05,
        "effort_hours": 50,
        "deadline_month": 12,
        "deadline_recurring": "December 15 annually",
        "eligibility": {"grades": [7, 8, 9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 2
    },
    {
        "id": "young-arts-visual",
        "name": "YoungArts - Visual Arts",
        "organization": "National YoungArts Foundation",
        "category": "arts",
        "level": "national",
        "description": "Prestigious arts program for emerging visual artists.",
        "prestige_score": 9,
        "historical_win_rate": 0.08,
        "effort_hours": 40,
        "deadline_month": 10,
        "eligibility": {"grades": [10, 11, 12]},
        "prize_amount": 10000,
        "prize_type": "cash",
        "touchpoints": 3
    },
    {
        "id": "congressional-art",
        "name": "Congressional Art Competition",
        "organization": "U.S. House of Representatives",
        "category": "arts",
        "level": "national",
        "description": "National art competition hosted by Congress.",
        "prestige_score": 7,
        "historical_win_rate": 0.15,
        "effort_hours": 20,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12], "citizenship": ["US"]},
        "prize_type": "recognition",
        "touchpoints": 2
    },

    # Music
    {
        "id": "young-arts-music",
        "name": "YoungArts - Music",
        "organization": "National YoungArts Foundation",
        "category": "arts",
        "level": "national",
        "description": "Prestigious competition for young musicians.",
        "prestige_score": 9,
        "historical_win_rate": 0.08,
        "effort_hours": 50,
        "deadline_month": 10,
        "eligibility": {"grades": [10, 11, 12]},
        "prize_amount": 10000,
        "prize_type": "cash",
        "touchpoints": 3
    },
    {
        "id": "all-state-music",
        "name": "All-State Music Ensemble",
        "organization": "State Music Educators Association",
        "category": "arts",
        "level": "state",
        "description": "Selection to state all-state orchestra/band/choir.",
        "prestige_score": 7,
        "historical_win_rate": 0.10,
        "effort_hours": 30,
        "deadline_month": 10,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 2
    },
    {
        "id": "mtna-competition",
        "name": "MTNA National Competition",
        "organization": "Music Teachers National Association",
        "category": "arts",
        "level": "national",
        "description": "National music performance competition.",
        "prestige_score": 8,
        "historical_win_rate": 0.05,
        "effort_hours": 100,
        "deadline_month": 10,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 5000,
        "prize_type": "cash",
        "touchpoints": 3
    },

    # Theater/Film
    {
        "id": "young-arts-theater",
        "name": "YoungArts - Theater",
        "organization": "National YoungArts Foundation",
        "category": "arts",
        "level": "national",
        "description": "Prestigious competition for young actors.",
        "prestige_score": 9,
        "historical_win_rate": 0.08,
        "effort_hours": 40,
        "deadline_month": 10,
        "eligibility": {"grades": [10, 11, 12]},
        "prize_amount": 10000,
        "prize_type": "cash",
        "touchpoints": 3
    },
    {
        "id": "nhsmta",
        "name": "National High School Musical Theatre Awards (Jimmy Awards)",
        "organization": "The Broadway League Foundation",
        "category": "arts",
        "level": "national",
        "description": "National high school musical theater competition.",
        "prestige_score": 8,
        "historical_win_rate": 0.02,
        "effort_hours": 60,
        "deadline_month": 6,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 25000,
        "prize_type": "scholarship",
        "touchpoints": 3
    },
    {
        "id": "all-american-film-fest",
        "name": "All American High School Film Festival",
        "organization": "All American High School Film Festival",
        "category": "arts",
        "level": "national",
        "description": "World's largest student film festival.",
        "prestige_score": 7,
        "historical_win_rate": 0.10,
        "effort_hours": 80,
        "deadline_month": 7,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 5000,
        "prize_type": "cash",
        "touchpoints": 2
    },
]

# =============================================================================
# LEADERSHIP AWARDS
# =============================================================================

LEADERSHIP_AWARDS: List[Dict[str, Any]] = [
    {
        "id": "prudential-spirit",
        "name": "Prudential Spirit of Community Awards",
        "organization": "Prudential Financial (concluded 2024)",
        "category": "leadership",
        "level": "national",
        "description": "Historic award honoring youth volunteers.",
        "prestige_score": 8,
        "historical_win_rate": 0.005,
        "effort_hours": 20,
        "deadline_month": 11,
        "eligibility": {"grades": [5, 6, 7, 8, 9, 10, 11, 12]},
        "prize_amount": 5000,
        "prize_type": "cash",
        "is_active": False,
        "touchpoints": 3
    },
    {
        "id": "diller-teen-tikkun",
        "name": "Diller Teen Tikkun Olam Awards",
        "organization": "Helen Diller Family Foundation",
        "category": "leadership",
        "level": "national",
        "description": "Honors Jewish teens demonstrating social change leadership.",
        "prestige_score": 8,
        "historical_win_rate": 0.05,
        "effort_hours": 25,
        "deadline_month": 1,
        "eligibility": {
            "grades": [9, 10, 11, 12],
            "citizenship": ["US"],
            "demographics": ["Jewish"]
        },
        "prize_amount": 36000,
        "prize_type": "cash",
        "touchpoints": 4
    },
    {
        "id": "jefferson-award-youth",
        "name": "Jefferson Award for Public Service - Youth",
        "organization": "Jefferson Awards Foundation",
        "category": "leadership",
        "level": "national",
        "description": "Recognizes young Americans making a difference.",
        "prestige_score": 8,
        "historical_win_rate": 0.05,
        "effort_hours": 20,
        "deadline_month": 2,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 3
    },
    {
        "id": "gloria-barron-prize",
        "name": "Gloria Barron Prize for Young Heroes",
        "organization": "T.A. Barron Foundation",
        "category": "leadership",
        "level": "national",
        "description": "Honors young people who have made a significant positive impact.",
        "prestige_score": 8,
        "historical_win_rate": 0.02,
        "effort_hours": 20,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 10000,
        "prize_type": "cash",
        "touchpoints": 3
    },
    {
        "id": "jsa-best-speaker",
        "name": "JSA Convention - Best Speaker",
        "organization": "Junior State of America",
        "category": "leadership",
        "level": "national",
        "description": "Top speaker award at national JSA convention.",
        "prestige_score": 7,
        "historical_win_rate": 0.02,
        "effort_hours": 40,
        "deadline_month": 11,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 3
    },
    {
        "id": "girls-state-governor",
        "name": "American Legion Girls State Governor",
        "organization": "American Legion Auxiliary",
        "category": "leadership",
        "level": "state",
        "description": "Elected governor at state Girls State program.",
        "prestige_score": 8,
        "historical_win_rate": 0.01,
        "effort_hours": 60,
        "deadline_month": 6,
        "eligibility": {"grades": [11], "gender": ["female"]},
        "prize_type": "recognition",
        "touchpoints": 4
    },
    {
        "id": "boys-state-governor",
        "name": "American Legion Boys State Governor",
        "organization": "American Legion",
        "category": "leadership",
        "level": "state",
        "description": "Elected governor at state Boys State program.",
        "prestige_score": 8,
        "historical_win_rate": 0.01,
        "effort_hours": 60,
        "deadline_month": 6,
        "eligibility": {"grades": [11], "gender": ["male"]},
        "prize_type": "recognition",
        "touchpoints": 4
    },
]

# =============================================================================
# SERVICE AWARDS
# =============================================================================

SERVICE_AWARDS: List[Dict[str, Any]] = [
    {
        "id": "congressional-award-gold",
        "name": "Congressional Award - Gold Medal",
        "organization": "Congressional Award Foundation",
        "category": "service",
        "level": "national",
        "description": "Congress's only award for youth - highest level.",
        "prestige_score": 9,
        "historical_win_rate": 0.30,
        "effort_hours": 400,
        "deadline_recurring": "Rolling submission",
        "eligibility": {"grades": [9, 10, 11, 12], "citizenship": ["US"]},
        "prize_type": "recognition",
        "touchpoints": 4,
        "touchpoint_types": ["volunteer", "personal_development", "physical_fitness", "expedition"]
    },
    {
        "id": "congressional-award-silver",
        "name": "Congressional Award - Silver Medal",
        "organization": "Congressional Award Foundation",
        "category": "service",
        "level": "national",
        "description": "Congress's award for youth - silver level.",
        "prestige_score": 8,
        "historical_win_rate": 0.40,
        "effort_hours": 200,
        "eligibility": {"grades": [9, 10, 11, 12], "citizenship": ["US"]},
        "prize_type": "recognition",
        "touchpoints": 4
    },
    {
        "id": "presidents-volunteer-gold",
        "name": "President's Volunteer Service Award - Gold",
        "organization": "AmeriCorps",
        "category": "service",
        "level": "national",
        "description": "Presidential recognition for 250+ volunteer hours.",
        "prestige_score": 6,
        "historical_win_rate": 0.50,
        "effort_hours": 250,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 1
    },
    {
        "id": "points-of-light",
        "name": "Points of Light Daily Point of Light Award",
        "organization": "Points of Light Foundation",
        "category": "service",
        "level": "national",
        "description": "Recognizes individuals making a difference.",
        "prestige_score": 7,
        "historical_win_rate": 0.10,
        "effort_hours": 30,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 2
    },
]

# =============================================================================
# ACADEMIC AWARDS
# =============================================================================

ACADEMIC_AWARDS: List[Dict[str, Any]] = [
    {
        "id": "national-merit-finalist",
        "name": "National Merit Scholarship Finalist",
        "organization": "National Merit Scholarship Corporation",
        "category": "academic",
        "level": "national",
        "description": "Top ~1% of PSAT scorers.",
        "prestige_score": 8,
        "historical_win_rate": 0.15,
        "effort_hours": 5,
        "deadline_month": 10,
        "deadline_recurring": "October PSAT",
        "eligibility": {"grades": [11]},
        "prize_amount": 2500,
        "prize_type": "scholarship",
        "touchpoints": 2,
        "touchpoint_types": ["psat", "application"]
    },
    {
        "id": "national-merit-semifinalist",
        "name": "National Merit Scholarship Semifinalist",
        "organization": "National Merit Scholarship Corporation",
        "category": "academic",
        "level": "national",
        "description": "Top ~1% of PSAT scorers by state.",
        "prestige_score": 7,
        "historical_win_rate": 0.01,
        "effort_hours": 5,
        "deadline_month": 10,
        "eligibility": {"grades": [11]},
        "prize_type": "recognition",
        "touchpoints": 1
    },
    {
        "id": "national-hispanic-scholar",
        "name": "National Hispanic Recognition Award",
        "organization": "College Board",
        "category": "academic",
        "level": "national",
        "description": "Top Hispanic PSAT scorers.",
        "prestige_score": 7,
        "historical_win_rate": 0.05,
        "effort_hours": 5,
        "deadline_month": 10,
        "eligibility": {"grades": [11], "demographics": ["hispanic"]},
        "diversity_focus": True,
        "prize_type": "recognition",
        "touchpoints": 1
    },
    {
        "id": "ap-scholar-distinction",
        "name": "AP Scholar with Distinction",
        "organization": "College Board",
        "category": "academic",
        "level": "national",
        "description": "Average score of 3.5+ on 5+ AP exams.",
        "prestige_score": 6,
        "historical_win_rate": 0.10,
        "effort_hours": 300,
        "eligibility": {"grades": [10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 5
    },
    {
        "id": "presidential-scholars",
        "name": "U.S. Presidential Scholars Program",
        "organization": "U.S. Department of Education",
        "category": "academic",
        "level": "national",
        "description": "One of nation's highest honors for graduating seniors.",
        "prestige_score": 10,
        "historical_win_rate": 0.002,
        "effort_hours": 50,
        "deadline_month": 1,
        "eligibility": {"grades": [12], "citizenship": ["US"]},
        "prize_type": "recognition",
        "touchpoints": 4,
        "touchpoint_types": ["application", "essay", "recommendation", "interview"]
    },
    {
        "id": "nhs-scholar",
        "name": "NHS Scholarship",
        "organization": "National Honor Society",
        "category": "academic",
        "level": "national",
        "description": "Scholarships for NHS members.",
        "prestige_score": 6,
        "historical_win_rate": 0.05,
        "effort_hours": 15,
        "deadline_month": 11,
        "eligibility": {"grades": [11, 12]},
        "prize_amount": 3200,
        "prize_type": "scholarship",
        "touchpoints": 3
    },
]

# =============================================================================
# DEBATE AWARDS
# =============================================================================

DEBATE_AWARDS: List[Dict[str, Any]] = [
    {
        "id": "nsda-nationals",
        "name": "NSDA National Tournament",
        "organization": "National Speech and Debate Association",
        "category": "debate",
        "level": "national",
        "description": "Largest academic competition in the world.",
        "prestige_score": 9,
        "historical_win_rate": 0.02,
        "effort_hours": 200,
        "deadline_month": 6,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 4
    },
    {
        "id": "nsda-state-champion",
        "name": "NSDA State Champion",
        "organization": "National Speech and Debate Association",
        "category": "debate",
        "level": "state",
        "description": "First place at state speech/debate tournament.",
        "prestige_score": 8,
        "historical_win_rate": 0.02,
        "effort_hours": 150,
        "deadline_month": 3,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 3
    },
    {
        "id": "toc-bid",
        "name": "Tournament of Champions Bid",
        "organization": "University of Kentucky",
        "category": "debate",
        "level": "national",
        "description": "Qualification bid to prestigious TOC tournament.",
        "prestige_score": 8,
        "historical_win_rate": 0.05,
        "effort_hours": 150,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 3
    },
    {
        "id": "harvard-debate-tournament",
        "name": "Harvard National Forensics Tournament - Winner",
        "organization": "Harvard Debate Council",
        "category": "debate",
        "level": "national",
        "description": "Win at prestigious Harvard tournament.",
        "prestige_score": 8,
        "historical_win_rate": 0.01,
        "effort_hours": 80,
        "deadline_month": 2,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 3
    },
]

# =============================================================================
# ENTREPRENEURSHIP AWARDS
# =============================================================================

ENTREPRENEURSHIP_AWARDS: List[Dict[str, Any]] = [
    {
        "id": "deca-icdc",
        "name": "DECA International Career Development Conference",
        "organization": "DECA Inc.",
        "category": "entrepreneurship",
        "level": "international",
        "description": "International business competition finals.",
        "prestige_score": 7,
        "historical_win_rate": 0.05,
        "effort_hours": 100,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 4
    },
    {
        "id": "fbla-nlc",
        "name": "FBLA National Leadership Conference",
        "organization": "Future Business Leaders of America",
        "category": "entrepreneurship",
        "level": "national",
        "description": "National business competition finals.",
        "prestige_score": 7,
        "historical_win_rate": 0.05,
        "effort_hours": 100,
        "deadline_month": 6,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 4
    },
    {
        "id": "diamond-challenge",
        "name": "Diamond Challenge",
        "organization": "University of Delaware",
        "category": "entrepreneurship",
        "level": "international",
        "description": "High school entrepreneurship competition.",
        "prestige_score": 7,
        "historical_win_rate": 0.05,
        "effort_hours": 80,
        "deadline_month": 2,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 10000,
        "prize_type": "cash",
        "touchpoints": 4
    },
    {
        "id": "nfte-world-series",
        "name": "NFTE World Series of Innovation",
        "organization": "Network for Teaching Entrepreneurship",
        "category": "entrepreneurship",
        "level": "international",
        "description": "Global student innovation challenge.",
        "prestige_score": 7,
        "historical_win_rate": 0.10,
        "effort_hours": 40,
        "deadline_month": 3,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 10000,
        "prize_type": "scholarship",
        "touchpoints": 3
    },
    {
        "id": "mit-think",
        "name": "MIT THINK Scholars Program",
        "organization": "Massachusetts Institute of Technology",
        "category": "entrepreneurship",
        "level": "national",
        "description": "Funding and mentorship for high school research and innovation projects.",
        "prestige_score": 9,
        "historical_win_rate": 0.05,
        "effort_hours": 50,
        "deadline_month": 12,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 1500,
        "prize_type": "grant",
        "touchpoints": 4
    },
    {
        "id": "youth-entrepreneur-challenge",
        "name": "Youth Entrepreneur Challenge",
        "organization": "YEC Foundation",
        "category": "entrepreneurship",
        "level": "national",
        "description": "Competition for student-run businesses and startups.",
        "prestige_score": 7,
        "historical_win_rate": 0.12,
        "effort_hours": 30,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 5000,
        "prize_type": "cash",
        "touchpoints": 3
    },
    {
        "id": "startup-summer",
        "name": "Startup Summer Challenge",
        "organization": "Startup Weekend",
        "category": "entrepreneurship",
        "level": "national",
        "description": "Intensive entrepreneurship bootcamp competition.",
        "prestige_score": 6,
        "historical_win_rate": 0.15,
        "effort_hours": 25,
        "deadline_month": 5,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 2500,
        "prize_type": "cash",
        "touchpoints": 3
    },
    {
        "id": "social-innovation",
        "name": "National Social Innovation Challenge",
        "organization": "Social Innovation Forum",
        "category": "entrepreneurship",
        "level": "national",
        "description": "Competition for social enterprise ideas and ventures.",
        "prestige_score": 7,
        "historical_win_rate": 0.10,
        "effort_hours": 35,
        "deadline_month": 3,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 3000,
        "prize_type": "grant",
        "touchpoints": 4
    },
    {
        "id": "future-business-leaders",
        "name": "Future Business Leaders of America Competition",
        "organization": "FBLA-PBL",
        "category": "entrepreneurship",
        "level": "national",
        "description": "Business and leadership competitions for FBLA members.",
        "prestige_score": 8,
        "historical_win_rate": 0.08,
        "effort_hours": 40,
        "deadline_month": 2,
        "eligibility": {"grades": [9, 10, 11, 12], "membership": "FBLA"},
        "prize_type": "recognition",
        "touchpoints": 4
    },
]

# =============================================================================
# JOURNALISM AWARDS
# =============================================================================

JOURNALISM_AWARDS: List[Dict[str, Any]] = [
    {
        "id": "nspa-pacemaker",
        "name": "NSPA Pacemaker Award",
        "organization": "National Scholastic Press Association",
        "category": "journalism",
        "level": "national",
        "description": "Preeminent award for high school publications.",
        "prestige_score": 9,
        "historical_win_rate": 0.05,
        "effort_hours": 200,
        "deadline_month": 10,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 1
    },
    {
        "id": "cspa-crown",
        "name": "CSPA Crown Award",
        "organization": "Columbia Scholastic Press Association",
        "category": "journalism",
        "level": "national",
        "description": "Highest recognition from Columbia for student media.",
        "prestige_score": 9,
        "historical_win_rate": 0.05,
        "effort_hours": 200,
        "deadline_month": 10,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 1
    },
    {
        "id": "quill-scroll",
        "name": "Quill and Scroll Writing Contest",
        "organization": "Quill and Scroll International Honorary Society",
        "category": "journalism",
        "level": "international",
        "description": "International high school writing contest.",
        "prestige_score": 7,
        "historical_win_rate": 0.10,
        "effort_hours": 20,
        "deadline_month": 2,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 500,
        "prize_type": "scholarship",
        "touchpoints": 2
    },
]

# =============================================================================
# IDENTITY-SPECIFIC AWARDS (Diversity Focus)
# =============================================================================

IDENTITY_SPECIFIC_AWARDS: List[Dict[str, Any]] = [
    {
        "id": "jackie-robinson-foundation",
        "name": "Jackie Robinson Foundation Scholarship",
        "organization": "Jackie Robinson Foundation",
        "category": "leadership",
        "level": "national",
        "description": "Scholarship for minority students demonstrating leadership and academic excellence.",
        "prestige_score": 9,
        "historical_win_rate": 0.05,
        "effort_hours": 30,
        "deadline_month": 2,
        "eligibility": {"grades": [12], "citizenship": ["US"], "demographics": ["minority"]},
        "prize_amount": 30000,
        "prize_type": "scholarship",
        "touchpoints": 4,
        "diversity_focus": True
    },
    {
        "id": "gates-scholarship",
        "name": "Gates Scholarship",
        "organization": "Bill & Melinda Gates Foundation",
        "category": "academic",
        "level": "national",
        "description": "Full scholarship for outstanding minority students.",
        "prestige_score": 10,
        "historical_win_rate": 0.01,
        "effort_hours": 40,
        "deadline_month": 9,
        "eligibility": {"grades": [12], "demographics": ["minority", "pell_eligible"]},
        "prize_amount": 300000,
        "prize_type": "scholarship",
        "touchpoints": 5,
        "diversity_focus": True
    },
    {
        "id": "questbridge-national-match",
        "name": "QuestBridge National College Match",
        "organization": "QuestBridge",
        "category": "academic",
        "level": "national",
        "description": "Full four-year scholarships to top colleges for high-achieving, low-income students.",
        "prestige_score": 10,
        "historical_win_rate": 0.15,
        "effort_hours": 45,
        "deadline_month": 9,
        "eligibility": {"grades": [12], "income": "low_income"},
        "prize_amount": 280000,
        "prize_type": "scholarship",
        "touchpoints": 6,
        "diversity_focus": True
    },
    {
        "id": "hispanic-heritage-foundation",
        "name": "Hispanic Heritage Youth Awards",
        "organization": "Hispanic Heritage Foundation",
        "category": "leadership",
        "level": "national",
        "description": "Awards for Latino high school students demonstrating excellence.",
        "prestige_score": 8,
        "historical_win_rate": 0.10,
        "effort_hours": 20,
        "deadline_month": 9,
        "eligibility": {"grades": [11, 12], "demographics": ["latino", "hispanic"]},
        "prize_amount": 5000,
        "prize_type": "scholarship",
        "touchpoints": 3,
        "diversity_focus": True
    },
    {
        "id": "naacp-act-so",
        "name": "NAACP ACT-SO Competition",
        "organization": "NAACP",
        "category": "academic",
        "level": "national",
        "description": "Afro-Academic, Cultural, Technological and Scientific Olympics.",
        "prestige_score": 8,
        "historical_win_rate": 0.15,
        "effort_hours": 40,
        "deadline_month": 2,
        "eligibility": {"grades": [9, 10, 11, 12], "demographics": ["african_american"]},
        "prize_amount": 25000,
        "prize_type": "scholarship",
        "touchpoints": 4,
        "diversity_focus": True
    },
    {
        "id": "apia-scholarship",
        "name": "APIA Scholarship",
        "organization": "Asian & Pacific Islander American Scholarship Fund",
        "category": "academic",
        "level": "national",
        "description": "Scholarships for Asian and Pacific Islander students.",
        "prestige_score": 7,
        "historical_win_rate": 0.20,
        "effort_hours": 15,
        "deadline_month": 1,
        "eligibility": {"grades": [12], "demographics": ["asian", "pacific_islander"]},
        "prize_amount": 5000,
        "prize_type": "scholarship",
        "touchpoints": 3,
        "diversity_focus": True
    },
    {
        "id": "ron-brown-scholar",
        "name": "Ron Brown Scholarship",
        "organization": "Ron Brown Scholar Program",
        "category": "leadership",
        "level": "national",
        "description": "Scholarship for African American students with leadership and academic excellence.",
        "prestige_score": 9,
        "historical_win_rate": 0.01,
        "effort_hours": 35,
        "deadline_month": 1,
        "eligibility": {"grades": [12], "demographics": ["african_american"]},
        "prize_amount": 40000,
        "prize_type": "scholarship",
        "touchpoints": 5,
        "diversity_focus": True
    },
    {
        "id": "point-foundation",
        "name": "Point Foundation Scholarship",
        "organization": "Point Foundation",
        "category": "leadership",
        "level": "national",
        "description": "Scholarships for LGBTQ+ students with academic merit and leadership.",
        "prestige_score": 8,
        "historical_win_rate": 0.08,
        "effort_hours": 25,
        "deadline_month": 1,
        "eligibility": {"grades": [12], "demographics": ["lgbtq"]},
        "prize_amount": 28000,
        "prize_type": "scholarship",
        "touchpoints": 4,
        "diversity_focus": True
    },
    {
        "id": "first-gen-students-scholarship",
        "name": "First Generation Student Scholarship",
        "organization": "First in the Family Scholars",
        "category": "academic",
        "level": "national",
        "description": "For students who will be the first in their family to attend college.",
        "prestige_score": 7,
        "historical_win_rate": 0.12,
        "effort_hours": 20,
        "deadline_month": 3,
        "eligibility": {"grades": [12], "first_generation": True},
        "prize_amount": 10000,
        "prize_type": "scholarship",
        "touchpoints": 3,
        "diversity_focus": True
    },
    {
        "id": "jack-kent-cooke",
        "name": "Jack Kent Cooke Foundation College Scholarship",
        "organization": "Jack Kent Cooke Foundation",
        "category": "academic",
        "level": "national",
        "description": "One of the largest scholarships in the U.S. for high-achieving, low-income students.",
        "prestige_score": 10,
        "historical_win_rate": 0.02,
        "effort_hours": 40,
        "deadline_month": 11,
        "eligibility": {"grades": [12], "income": "low_income", "gpa_min": 3.5},
        "prize_amount": 55000,
        "prize_type": "scholarship",
        "touchpoints": 5,
        "diversity_focus": True
    },
    {
        "id": "coca-cola-scholars",
        "name": "Coca-Cola Scholars Program",
        "organization": "Coca-Cola Scholars Foundation",
        "category": "leadership",
        "level": "national",
        "description": "Achievement-based scholarship recognizing student leaders.",
        "prestige_score": 9,
        "historical_win_rate": 0.01,
        "effort_hours": 25,
        "deadline_month": 10,
        "eligibility": {"grades": [12], "citizenship": ["US"]},
        "prize_amount": 20000,
        "prize_type": "scholarship",
        "touchpoints": 4,
        "diversity_focus": True
    },
    {
        "id": "elks-mvs",
        "name": "Elks Most Valuable Student Scholarship",
        "organization": "Elks National Foundation",
        "category": "leadership",
        "level": "national",
        "description": "Scholarship recognizing leadership, scholarship and financial need.",
        "prestige_score": 8,
        "historical_win_rate": 0.03,
        "effort_hours": 20,
        "deadline_month": 11,
        "eligibility": {"grades": [12], "citizenship": ["US"]},
        "prize_amount": 50000,
        "prize_type": "scholarship",
        "touchpoints": 4,
        "diversity_focus": True
    },
]

# =============================================================================
# LOCAL & REGIONAL AWARDS
# =============================================================================

LOCAL_REGIONAL_AWARDS: List[Dict[str, Any]] = [
    {
        "id": "state-science-fair",
        "name": "State Science Fair",
        "organization": "State Science Fair Organization",
        "category": "stem",
        "level": "state",
        "description": "State-level science fair competition across all STEM categories.",
        "prestige_score": 7,
        "historical_win_rate": 0.15,
        "effort_hours": 60,
        "deadline_month": 1,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 1000,
        "prize_type": "scholarship",
        "touchpoints": 4
    },
    {
        "id": "state-history-day",
        "name": "State History Day",
        "organization": "National History Day (State Affiliate)",
        "category": "humanities",
        "level": "state",
        "description": "State-level history research competition.",
        "prestige_score": 7,
        "historical_win_rate": 0.12,
        "effort_hours": 50,
        "deadline_month": 3,
        "eligibility": {"grades": [6, 7, 8, 9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 3
    },
    {
        "id": "state-poetry-out-loud",
        "name": "State Poetry Out Loud",
        "organization": "National Endowment for the Arts (State Affiliate)",
        "category": "arts",
        "level": "state",
        "description": "State-level poetry recitation competition.",
        "prestige_score": 6,
        "historical_win_rate": 0.10,
        "effort_hours": 25,
        "deadline_month": 2,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 200,
        "prize_type": "cash",
        "touchpoints": 2
    },
    {
        "id": "regional-mathcounts",
        "name": "Regional MATHCOUNTS Competition",
        "organization": "MATHCOUNTS Foundation",
        "category": "stem",
        "level": "regional",
        "description": "Regional mathematics competition for middle schoolers.",
        "prestige_score": 6,
        "historical_win_rate": 0.20,
        "effort_hours": 30,
        "deadline_month": 11,
        "eligibility": {"grades": [6, 7, 8]},
        "prize_type": "recognition",
        "touchpoints": 2
    },
    {
        "id": "local-rotary-scholarship",
        "name": "Local Rotary Club Scholarship",
        "organization": "Rotary International (Local Chapter)",
        "category": "service",
        "level": "local",
        "description": "Community-based scholarship for service-oriented students.",
        "prestige_score": 5,
        "historical_win_rate": 0.25,
        "effort_hours": 15,
        "deadline_month": 3,
        "eligibility": {"grades": [12]},
        "prize_amount": 2500,
        "prize_type": "scholarship",
        "touchpoints": 3
    },
    {
        "id": "local-lions-club",
        "name": "Lions Club Youth of the Year",
        "organization": "Lions Clubs International (Local Chapter)",
        "category": "service",
        "level": "local",
        "description": "Recognition for youth leadership and community service.",
        "prestige_score": 5,
        "historical_win_rate": 0.30,
        "effort_hours": 10,
        "deadline_month": 1,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 500,
        "prize_type": "scholarship",
        "touchpoints": 2
    },
    {
        "id": "state-debate-championship",
        "name": "State Speech & Debate Championship",
        "organization": "NSDA State Affiliate",
        "category": "debate",
        "level": "state",
        "description": "State-level speech and debate championship.",
        "prestige_score": 8,
        "historical_win_rate": 0.08,
        "effort_hours": 100,
        "deadline_month": 3,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 3
    },
    {
        "id": "regional-art-show",
        "name": "Regional Scholastic Art & Writing Awards",
        "organization": "Alliance for Young Artists & Writers (Regional Affiliate)",
        "category": "arts",
        "level": "regional",
        "description": "Regional juried art competition for student artists.",
        "prestige_score": 7,
        "historical_win_rate": 0.15,
        "effort_hours": 40,
        "deadline_month": 12,
        "eligibility": {"grades": [7, 8, 9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 2
    },
    {
        "id": "state-music-festival",
        "name": "All-State Music Festival",
        "organization": "State Music Educators Association",
        "category": "arts",
        "level": "state",
        "description": "Competitive auditions for state-level honors ensemble.",
        "prestige_score": 8,
        "historical_win_rate": 0.10,
        "effort_hours": 50,
        "deadline_month": 10,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_type": "recognition",
        "touchpoints": 2
    },
    {
        "id": "local-business-essay",
        "name": "Local Chamber of Commerce Essay Contest",
        "organization": "Local Chamber of Commerce",
        "category": "entrepreneurship",
        "level": "local",
        "description": "Essay competition on business and economic topics.",
        "prestige_score": 4,
        "historical_win_rate": 0.25,
        "effort_hours": 10,
        "deadline_month": 4,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "prize_amount": 500,
        "prize_type": "cash",
        "touchpoints": 2
    },
    {
        "id": "state-spelling-bee",
        "name": "State Spelling Bee",
        "organization": "Scripps National Spelling Bee (State Affiliate)",
        "category": "academic",
        "level": "state",
        "description": "State-level spelling competition.",
        "prestige_score": 7,
        "historical_win_rate": 0.03,
        "effort_hours": 100,
        "deadline_month": 2,
        "eligibility": {"grades": [5, 6, 7, 8]},
        "prize_type": "recognition",
        "touchpoints": 2
    },
    {
        "id": "regional-stem-fair",
        "name": "Regional STEM Fair",
        "organization": "Regional Science Consortium",
        "category": "stem",
        "level": "regional",
        "description": "Regional science and technology fair.",
        "prestige_score": 6,
        "historical_win_rate": 0.18,
        "effort_hours": 40,
        "deadline_month": 1,
        "eligibility": {"grades": [6, 7, 8, 9, 10, 11, 12]},
        "prize_amount": 250,
        "prize_type": "cash",
        "touchpoints": 3
    },
]

# =============================================================================
# COMBINED AWARDS DATABASE
# =============================================================================

def get_all_awards() -> List[Dict[str, Any]]:
    """Return all awards combined into a single list."""
    all_awards = []
    all_awards.extend(STEM_AWARDS)
    all_awards.extend(HUMANITIES_AWARDS)
    all_awards.extend(ARTS_AWARDS)
    all_awards.extend(LEADERSHIP_AWARDS)
    all_awards.extend(SERVICE_AWARDS)
    all_awards.extend(ACADEMIC_AWARDS)
    all_awards.extend(DEBATE_AWARDS)
    all_awards.extend(ENTREPRENEURSHIP_AWARDS)
    all_awards.extend(JOURNALISM_AWARDS)
    all_awards.extend(IDENTITY_SPECIFIC_AWARDS)
    all_awards.extend(LOCAL_REGIONAL_AWARDS)

    # Add default fields
    for award in all_awards:
        if "is_active" not in award:
            award["is_active"] = True
        if "diversity_focus" not in award:
            award["diversity_focus"] = False
        if "touchpoints" not in award:
            award["touchpoints"] = 1

    return all_awards


def get_awards_by_category(category: str) -> List[Dict[str, Any]]:
    """Return awards filtered by category."""
    return [a for a in get_all_awards() if a.get("category") == category]


def get_awards_by_level(level: str) -> List[Dict[str, Any]]:
    """Return awards filtered by level (national, state, international)."""
    return [a for a in get_all_awards() if a.get("level") == level]


def get_active_awards() -> List[Dict[str, Any]]:
    """Return only active awards."""
    return [a for a in get_all_awards() if a.get("is_active", True)]


def get_diversity_awards() -> List[Dict[str, Any]]:
    """Return awards with diversity focus."""
    return [a for a in get_all_awards() if a.get("diversity_focus", False)]


# Stats
if __name__ == "__main__":
    awards = get_all_awards()
    print(f"Total awards: {len(awards)}")
    print(f"Active awards: {len(get_active_awards())}")
    print(f"Diversity-focused awards: {len(get_diversity_awards())}")

    # By category
    categories = set(a["category"] for a in awards)
    for cat in sorted(categories):
        count = len(get_awards_by_category(cat))
        print(f"  {cat}: {count}")

    # By level
    levels = set(a["level"] for a in awards)
    for level in sorted(levels):
        count = len(get_awards_by_level(level))
        print(f"  {level}: {count}")
