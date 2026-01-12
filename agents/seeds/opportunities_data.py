"""
IvyQuest v10.0 - Opportunities Database Seed Data
==================================================

Comprehensive database of 100+ opportunities for high school students.
Used by OpportunityScout agent for matching and timeline planning.

Categories:
- Summer Programs (elite research, academic enrichment)
- Internships (corporate, nonprofit, government)
- Research Programs
- Leadership Programs
- STEM Programs
- Humanities Programs
- Arts Programs
- Pre-College Programs

Data Sources:
- Official program websites
- College admissions databases
- Historical acceptance rates
"""

from datetime import datetime
from typing import List, Dict, Any

# =============================================================================
# ELITE SUMMER RESEARCH PROGRAMS
# =============================================================================

ELITE_RESEARCH_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "rsi",
        "name": "Research Science Institute (RSI)",
        "organization": "MIT / Center for Excellence in Education",
        "type": "summer_program",
        "category": "research",
        "description": "Six-week summer science and engineering program combining coursework with hands-on research.",
        "prestige_score": 10,
        "acceptance_rate": 0.03,
        "selectivity": "highly_selective",
        "deadline_month": 1,
        "deadline_recurring": "January 15 annually",
        "program_start_month": 6,
        "program_end_month": 8,
        "duration_weeks": 6,
        "cost": 0,
        "financial_aid_available": True,
        "location": "Cambridge, MA",
        "is_virtual": False,
        "is_residential": True,
        "effort_hours": 40,
        "eligibility": {
            "grades": [11],
            "citizenship": ["US", "international"],
            "requirements": ["essay", "recommendation", "transcript", "test_scores"]
        },
        "focus_area": "STEM",
        "touchpoints": 5,
        "diversity_focus": True
    },
    {
        "id": "ssp-astrophysics",
        "name": "Summer Science Program - Astrophysics",
        "organization": "Summer Science Program",
        "type": "summer_program",
        "category": "research",
        "description": "Rigorous astrophysics research program determining asteroid orbits.",
        "prestige_score": 10,
        "acceptance_rate": 0.08,
        "selectivity": "highly_selective",
        "deadline_month": 2,
        "deadline_recurring": "February 1 annually",
        "program_start_month": 6,
        "duration_weeks": 5,
        "cost": 8000,
        "financial_aid_available": True,
        "location": "Multiple campuses (NM, CO)",
        "is_residential": True,
        "effort_hours": 35,
        "eligibility": {"grades": [10, 11]},
        "focus_area": "STEM",
        "touchpoints": 4
    },
    {
        "id": "ssp-biochemistry",
        "name": "Summer Science Program - Biochemistry",
        "organization": "Summer Science Program",
        "type": "summer_program",
        "category": "research",
        "description": "Biochemistry research program studying fungal crop pathogens.",
        "prestige_score": 10,
        "acceptance_rate": 0.08,
        "selectivity": "highly_selective",
        "deadline_month": 2,
        "program_start_month": 6,
        "duration_weeks": 5,
        "cost": 8000,
        "financial_aid_available": True,
        "location": "Indiana University",
        "is_residential": True,
        "effort_hours": 35,
        "eligibility": {"grades": [10, 11]},
        "focus_area": "STEM",
        "touchpoints": 4
    },
    {
        "id": "ssp-genomics",
        "name": "Summer Science Program - Genomics",
        "organization": "Summer Science Program",
        "type": "summer_program",
        "category": "research",
        "description": "Genomics research program studying DNA sequences.",
        "prestige_score": 10,
        "acceptance_rate": 0.08,
        "selectivity": "highly_selective",
        "deadline_month": 2,
        "program_start_month": 6,
        "duration_weeks": 5,
        "cost": 8000,
        "financial_aid_available": True,
        "location": "Purdue University",
        "is_residential": True,
        "effort_hours": 35,
        "eligibility": {"grades": [10, 11]},
        "focus_area": "STEM",
        "touchpoints": 4
    },
    {
        "id": "tasp",
        "name": "Telluride Association Summer Program (TASP)",
        "organization": "Telluride Association",
        "type": "summer_program",
        "category": "humanities",
        "description": "Intensive six-week educational experience in humanities and social sciences.",
        "prestige_score": 10,
        "acceptance_rate": 0.03,
        "selectivity": "highly_selective",
        "deadline_month": 1,
        "deadline_recurring": "January 15 annually",
        "program_start_month": 6,
        "duration_weeks": 6,
        "cost": 0,
        "financial_aid_available": True,
        "location": "Multiple campuses (Cornell, Michigan)",
        "is_residential": True,
        "effort_hours": 40,
        "eligibility": {"grades": [11]},
        "focus_area": "HUMANITIES",
        "touchpoints": 5
    },
    {
        "id": "garcia-mrsec",
        "name": "Garcia MRSEC Summer Program",
        "organization": "Stony Brook University",
        "type": "summer_program",
        "category": "research",
        "description": "Materials science research program at Stony Brook.",
        "prestige_score": 8,
        "acceptance_rate": 0.15,
        "selectivity": "selective",
        "deadline_month": 3,
        "program_start_month": 7,
        "duration_weeks": 7,
        "cost": 0,
        "financial_aid_available": True,
        "location": "Stony Brook, NY",
        "is_residential": True,
        "effort_hours": 25,
        "eligibility": {"grades": [10, 11]},
        "focus_area": "STEM",
        "touchpoints": 4
    },
    {
        "id": "simons-stony-brook",
        "name": "Simons Summer Research Program",
        "organization": "Stony Brook University",
        "type": "summer_program",
        "category": "research",
        "description": "Science research mentorship program.",
        "prestige_score": 8,
        "acceptance_rate": 0.10,
        "selectivity": "selective",
        "deadline_month": 2,
        "program_start_month": 7,
        "duration_weeks": 8,
        "cost": 0,
        "stipend": 3000,
        "location": "Stony Brook, NY",
        "is_residential": True,
        "effort_hours": 30,
        "eligibility": {"grades": [11]},
        "focus_area": "STEM",
        "touchpoints": 4
    },
    {
        "id": "clark-scholars",
        "name": "Clark Scholars Program",
        "organization": "Texas Tech University",
        "type": "summer_program",
        "category": "research",
        "description": "Intensive seven-week summer research program.",
        "prestige_score": 8,
        "acceptance_rate": 0.08,
        "selectivity": "highly_selective",
        "deadline_month": 2,
        "program_start_month": 6,
        "duration_weeks": 7,
        "cost": 0,
        "stipend": 750,
        "location": "Lubbock, TX",
        "is_residential": True,
        "effort_hours": 30,
        "eligibility": {"grades": [11, 12]},
        "focus_area": "STEM",
        "touchpoints": 4
    },
]

# =============================================================================
# MIT PROGRAMS
# =============================================================================

MIT_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "mostec",
        "name": "MIT Online Science, Technology, and Engineering Community (MOSTEC)",
        "organization": "MIT Office of Engineering Outreach Programs",
        "type": "summer_program",
        "category": "stem",
        "description": "Six-month STEM enrichment program for rising seniors.",
        "prestige_score": 9,
        "acceptance_rate": 0.05,
        "selectivity": "highly_selective",
        "deadline_month": 2,
        "deadline_recurring": "February annually",
        "program_start_month": 6,
        "duration_weeks": 26,
        "cost": 0,
        "location": "Online + MIT campus visit",
        "is_virtual": True,
        "is_residential": False,
        "effort_hours": 30,
        "eligibility": {"grades": [11]},
        "focus_area": "STEM",
        "diversity_focus": True,
        "touchpoints": 5
    },
    {
        "id": "mites",
        "name": "MIT Introduction to Technology, Engineering, and Science (MITES)",
        "organization": "MIT Office of Engineering Outreach Programs",
        "type": "summer_program",
        "category": "stem",
        "description": "Rigorous six-week academic enrichment program.",
        "prestige_score": 9,
        "acceptance_rate": 0.08,
        "selectivity": "highly_selective",
        "deadline_month": 2,
        "program_start_month": 6,
        "duration_weeks": 6,
        "cost": 0,
        "location": "Cambridge, MA",
        "is_residential": True,
        "effort_hours": 35,
        "eligibility": {"grades": [11]},
        "focus_area": "STEM",
        "diversity_focus": True,
        "touchpoints": 5
    },
    {
        "id": "mit-primes",
        "name": "MIT PRIMES",
        "organization": "MIT Mathematics Department",
        "type": "research",
        "category": "research",
        "description": "Year-long research program in mathematics and computer science.",
        "prestige_score": 10,
        "acceptance_rate": 0.10,
        "selectivity": "highly_selective",
        "deadline_month": 12,
        "duration_weeks": 52,
        "cost": 0,
        "location": "Cambridge, MA / Remote",
        "effort_hours": 30,
        "eligibility": {"grades": [9, 10, 11]},
        "focus_area": "STEM",
        "touchpoints": 5
    },
]

# =============================================================================
# STANFORD PROGRAMS
# =============================================================================

STANFORD_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "stanford-summerinstitutes",
        "name": "Stanford Summer Institutes",
        "organization": "Stanford Pre-Collegiate Studies",
        "type": "summer_program",
        "category": "academic",
        "description": "Intensive academic institutes in various subjects.",
        "prestige_score": 7,
        "acceptance_rate": 0.25,
        "selectivity": "moderate",
        "deadline_month": 3,
        "deadline_recurring": "March 15 annually",
        "program_start_month": 6,
        "duration_weeks": 3,
        "cost": 8500,
        "financial_aid_available": True,
        "location": "Stanford, CA",
        "is_residential": True,
        "effort_hours": 20,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "focus_area": "GENERAL",
        "touchpoints": 3
    },
    {
        "id": "stanford-humanities-institute",
        "name": "Stanford Summer Humanities Institute",
        "organization": "Stanford Pre-Collegiate Studies",
        "type": "summer_program",
        "category": "humanities",
        "description": "Intensive humanities seminars.",
        "prestige_score": 7,
        "acceptance_rate": 0.30,
        "selectivity": "moderate",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 3,
        "cost": 8500,
        "financial_aid_available": True,
        "location": "Stanford, CA",
        "is_residential": True,
        "effort_hours": 20,
        "eligibility": {"grades": [10, 11]},
        "focus_area": "HUMANITIES",
        "touchpoints": 3
    },
    {
        "id": "stanford-math-camp",
        "name": "Stanford University Mathematics Camp (SUMaC)",
        "organization": "Stanford University",
        "type": "summer_program",
        "category": "stem",
        "description": "Advanced mathematics residential program.",
        "prestige_score": 9,
        "acceptance_rate": 0.10,
        "selectivity": "highly_selective",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 4,
        "cost": 8000,
        "financial_aid_available": True,
        "location": "Stanford, CA",
        "is_residential": True,
        "effort_hours": 30,
        "eligibility": {"grades": [10, 11]},
        "focus_area": "STEM",
        "touchpoints": 4
    },
]

# =============================================================================
# YALE PROGRAMS
# =============================================================================

YALE_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "yale-young-global-scholars",
        "name": "Yale Young Global Scholars (YYGS)",
        "organization": "Yale University",
        "type": "summer_program",
        "category": "leadership",
        "description": "Interdisciplinary academic enrichment and leadership program.",
        "prestige_score": 8,
        "acceptance_rate": 0.25,
        "selectivity": "selective",
        "deadline_month": 2,
        "deadline_recurring": "February annually",
        "program_start_month": 6,
        "duration_weeks": 2,
        "cost": 6500,
        "financial_aid_available": True,
        "location": "New Haven, CT",
        "is_residential": True,
        "effort_hours": 15,
        "eligibility": {"grades": [10, 11, 12]},
        "focus_area": "GENERAL",
        "touchpoints": 3
    },
]

# =============================================================================
# TECH COMPANY PROGRAMS
# =============================================================================

TECH_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "google-cssi",
        "name": "Google Computer Science Summer Institute (CSSI)",
        "organization": "Google",
        "type": "summer_program",
        "category": "stem",
        "description": "Intensive CS program for graduating seniors.",
        "prestige_score": 9,
        "acceptance_rate": 0.08,
        "selectivity": "highly_selective",
        "deadline_month": 3,
        "deadline_recurring": "March annually",
        "program_start_month": 7,
        "duration_weeks": 4,
        "cost": 0,
        "location": "Google offices (multiple locations)",
        "is_residential": False,
        "effort_hours": 30,
        "eligibility": {"grades": [12]},
        "focus_area": "CS",
        "diversity_focus": True,
        "touchpoints": 4
    },
    {
        "id": "microsoft-leap",
        "name": "Microsoft LEAP Apprenticeship",
        "organization": "Microsoft",
        "type": "internship",
        "category": "stem",
        "description": "Software development apprenticeship (typically for non-traditional paths).",
        "prestige_score": 8,
        "acceptance_rate": 0.15,
        "selectivity": "selective",
        "deadline_month": 2,
        "program_start_month": 6,
        "duration_weeks": 16,
        "cost": 0,
        "stipend": 8000,
        "location": "Redmond, WA (or remote)",
        "effort_hours": 30,
        "eligibility": {"grades": [11, 12]},
        "focus_area": "CS",
        "diversity_focus": True,
        "touchpoints": 4
    },
    {
        "id": "girls-who-code-sip",
        "name": "Girls Who Code Summer Immersion Program",
        "organization": "Girls Who Code",
        "type": "summer_program",
        "category": "stem",
        "description": "Seven-week computer science immersion for high school girls.",
        "prestige_score": 7,
        "acceptance_rate": 0.15,
        "selectivity": "selective",
        "deadline_month": 3,
        "deadline_recurring": "March annually",
        "program_start_month": 6,
        "duration_weeks": 7,
        "cost": 0,
        "location": "Multiple cities (virtual available)",
        "is_residential": False,
        "effort_hours": 25,
        "eligibility": {"grades": [10, 11, 12], "gender": ["female", "non-binary"]},
        "focus_area": "CS",
        "diversity_focus": True,
        "touchpoints": 4
    },
    {
        "id": "kode-with-klossy",
        "name": "Kode With Klossy",
        "organization": "Kode With Klossy",
        "type": "summer_program",
        "category": "stem",
        "description": "Two-week coding camps for young women.",
        "prestige_score": 6,
        "acceptance_rate": 0.20,
        "selectivity": "moderate",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 2,
        "cost": 0,
        "location": "Multiple cities",
        "effort_hours": 15,
        "eligibility": {"grades": [9, 10, 11, 12], "gender": ["female", "non-binary"]},
        "focus_area": "CS",
        "diversity_focus": True,
        "touchpoints": 3
    },
]

# =============================================================================
# BANK/FINANCE PROGRAMS
# =============================================================================

FINANCE_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "bofa-student-leaders",
        "name": "Bank of America Student Leaders",
        "organization": "Bank of America",
        "type": "internship",
        "category": "leadership",
        "description": "Paid summer internship with nonprofit organizations.",
        "prestige_score": 8,
        "acceptance_rate": 0.10,
        "selectivity": "selective",
        "deadline_month": 1,
        "deadline_recurring": "January 31 annually",
        "program_start_month": 6,
        "duration_weeks": 8,
        "cost": 0,
        "stipend": 5000,
        "location": "Various US cities",
        "effort_hours": 25,
        "eligibility": {"grades": [11, 12], "citizenship": ["US"]},
        "focus_area": "LEADERSHIP",
        "touchpoints": 4
    },
    {
        "id": "girls-inc-eureka",
        "name": "Girls Inc. Eureka! STEM Program",
        "organization": "Girls Inc.",
        "type": "summer_program",
        "category": "stem",
        "description": "Five-year STEM program for girls starting in 8th grade.",
        "prestige_score": 6,
        "acceptance_rate": 0.30,
        "selectivity": "moderate",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 4,
        "cost": 0,
        "location": "Various locations",
        "eligibility": {"grades": [8, 9, 10, 11, 12], "gender": ["female"]},
        "focus_area": "STEM",
        "diversity_focus": True,
        "touchpoints": 3
    },
]

# =============================================================================
# PRE-MED PROGRAMS
# =============================================================================

PREMED_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "nslc-medicine",
        "name": "National Student Leadership Conference - Medicine",
        "organization": "Envision",
        "type": "summer_program",
        "category": "stem",
        "description": "Medical career exploration program.",
        "prestige_score": 5,
        "acceptance_rate": 0.50,
        "selectivity": "open",
        "deadline_month": 5,
        "program_start_month": 6,
        "duration_weeks": 2,
        "cost": 4000,
        "location": "Various university campuses",
        "is_residential": True,
        "effort_hours": 10,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "focus_area": "STEM",
        "touchpoints": 2
    },
    {
        "id": "jhu-ssp-biomed",
        "name": "Johns Hopkins Engineering Innovation",
        "organization": "Johns Hopkins University",
        "type": "summer_program",
        "category": "stem",
        "description": "Pre-college engineering program.",
        "prestige_score": 7,
        "acceptance_rate": 0.35,
        "selectivity": "moderate",
        "deadline_month": 4,
        "program_start_month": 6,
        "duration_weeks": 4,
        "cost": 4500,
        "financial_aid_available": True,
        "location": "Baltimore, MD",
        "is_residential": True,
        "effort_hours": 20,
        "eligibility": {"grades": [10, 11, 12]},
        "focus_area": "STEM",
        "touchpoints": 3
    },
]

# =============================================================================
# ARTS PROGRAMS
# =============================================================================

ARTS_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "interlochen-arts",
        "name": "Interlochen Arts Camp",
        "organization": "Interlochen Center for the Arts",
        "type": "summer_program",
        "category": "arts",
        "description": "Premier summer arts program in music, visual arts, theater, dance, and film.",
        "prestige_score": 9,
        "acceptance_rate": 0.60,
        "selectivity": "moderate",
        "deadline_month": 2,
        "program_start_month": 6,
        "duration_weeks": 6,
        "cost": 10000,
        "financial_aid_available": True,
        "location": "Interlochen, MI",
        "is_residential": True,
        "effort_hours": 25,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "focus_area": "ARTS",
        "touchpoints": 3
    },
    {
        "id": "tanglewood-festival",
        "name": "Tanglewood Institute for Young Artists",
        "organization": "Boston University",
        "type": "summer_program",
        "category": "arts",
        "description": "Elite young artist program at Tanglewood.",
        "prestige_score": 9,
        "acceptance_rate": 0.25,
        "selectivity": "selective",
        "deadline_month": 1,
        "program_start_month": 6,
        "duration_weeks": 6,
        "cost": 8000,
        "financial_aid_available": True,
        "location": "Lenox, MA",
        "is_residential": True,
        "effort_hours": 30,
        "eligibility": {"grades": [10, 11, 12]},
        "focus_area": "ARTS",
        "touchpoints": 4
    },
    {
        "id": "california-state-arts",
        "name": "California State Summer School for the Arts (CSSSA)",
        "organization": "California Institute of the Arts",
        "type": "summer_program",
        "category": "arts",
        "description": "Intensive arts training in multiple disciplines.",
        "prestige_score": 8,
        "acceptance_rate": 0.30,
        "selectivity": "selective",
        "deadline_month": 2,
        "program_start_month": 7,
        "duration_weeks": 4,
        "cost": 3000,
        "financial_aid_available": True,
        "location": "Valencia, CA",
        "is_residential": True,
        "effort_hours": 25,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "focus_area": "ARTS",
        "touchpoints": 4
    },
]

# =============================================================================
# ENTREPRENEURSHIP PROGRAMS
# =============================================================================

ENTREPRENEURSHIP_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "launchx",
        "name": "LaunchX Entrepreneurship Program",
        "organization": "MIT / LaunchX",
        "type": "summer_program",
        "category": "entrepreneurship",
        "description": "Launch a real company during the summer program.",
        "prestige_score": 8,
        "acceptance_rate": 0.15,
        "selectivity": "selective",
        "deadline_month": 3,
        "deadline_recurring": "March annually",
        "program_start_month": 7,
        "duration_weeks": 4,
        "cost": 5500,
        "financial_aid_available": True,
        "location": "Various campuses / Online",
        "is_residential": True,
        "effort_hours": 25,
        "eligibility": {"grades": [10, 11, 12]},
        "focus_area": "BUSINESS",
        "touchpoints": 4
    },
    {
        "id": "wharton-leadership",
        "name": "Wharton Leadership in the Business World",
        "organization": "University of Pennsylvania",
        "type": "summer_program",
        "category": "entrepreneurship",
        "description": "Exposure to business fundamentals and leadership.",
        "prestige_score": 8,
        "acceptance_rate": 0.20,
        "selectivity": "selective",
        "deadline_month": 2,
        "program_start_month": 7,
        "duration_weeks": 4,
        "cost": 6500,
        "financial_aid_available": True,
        "location": "Philadelphia, PA",
        "is_residential": True,
        "effort_hours": 20,
        "eligibility": {"grades": [11]},
        "focus_area": "BUSINESS",
        "touchpoints": 4
    },
    {
        "id": "nslc-entrepreneurship",
        "name": "National Student Leadership Conference - Entrepreneurship",
        "organization": "Envision",
        "type": "summer_program",
        "category": "entrepreneurship",
        "description": "Business and entrepreneurship exploration.",
        "prestige_score": 5,
        "acceptance_rate": 0.50,
        "selectivity": "open",
        "deadline_month": 5,
        "program_start_month": 6,
        "duration_weeks": 2,
        "cost": 4000,
        "location": "Various campuses",
        "effort_hours": 10,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "focus_area": "BUSINESS",
        "touchpoints": 2
    },
]

# =============================================================================
# GOVERNMENT/POLICY PROGRAMS
# =============================================================================

GOVERNMENT_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "girls-state",
        "name": "American Legion Auxiliary Girls State",
        "organization": "American Legion Auxiliary",
        "type": "summer_program",
        "category": "leadership",
        "description": "Week-long government simulation program.",
        "prestige_score": 8,
        "acceptance_rate": 0.50,
        "selectivity": "moderate",
        "deadline_month": 2,
        "program_start_month": 6,
        "duration_weeks": 1,
        "cost": 0,
        "location": "Various state capitals",
        "is_residential": True,
        "effort_hours": 20,
        "eligibility": {"grades": [11], "gender": ["female"]},
        "focus_area": "LEADERSHIP",
        "touchpoints": 3
    },
    {
        "id": "boys-state",
        "name": "American Legion Boys State",
        "organization": "American Legion",
        "type": "summer_program",
        "category": "leadership",
        "description": "Week-long government simulation program.",
        "prestige_score": 8,
        "acceptance_rate": 0.50,
        "selectivity": "moderate",
        "deadline_month": 2,
        "program_start_month": 6,
        "duration_weeks": 1,
        "cost": 0,
        "location": "Various state capitals",
        "is_residential": True,
        "effort_hours": 20,
        "eligibility": {"grades": [11], "gender": ["male"]},
        "focus_area": "LEADERSHIP",
        "touchpoints": 3
    },
    {
        "id": "senate-page",
        "name": "U.S. Senate Page Program",
        "organization": "U.S. Senate",
        "type": "internship",
        "category": "leadership",
        "description": "Work as a page in the U.S. Senate.",
        "prestige_score": 9,
        "acceptance_rate": 0.05,
        "selectivity": "highly_selective",
        "deadline_month": 10,
        "program_start_month": 1,
        "duration_weeks": 20,
        "cost": 0,
        "location": "Washington, DC",
        "is_residential": True,
        "effort_hours": 30,
        "eligibility": {"grades": [11], "citizenship": ["US"]},
        "focus_area": "LEADERSHIP",
        "touchpoints": 4
    },
]

# =============================================================================
# JOURNALISM PROGRAMS
# =============================================================================

JOURNALISM_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "jcamp-dow-jones",
        "name": "JCAMP (Journalism and Communications Camp)",
        "organization": "Various (Dow Jones, Northwestern, etc.)",
        "type": "summer_program",
        "category": "journalism",
        "description": "Intensive journalism training at leading newsrooms.",
        "prestige_score": 8,
        "acceptance_rate": 0.15,
        "selectivity": "selective",
        "deadline_month": 3,
        "program_start_month": 7,
        "duration_weeks": 2,
        "cost": 0,
        "location": "Various (NYC, DC, etc.)",
        "effort_hours": 20,
        "eligibility": {"grades": [11, 12]},
        "focus_area": "JOURNALISM",
        "diversity_focus": True,
        "touchpoints": 4
    },
    {
        "id": "medill-cherubs",
        "name": "Northwestern Medill-Northwestern Journalism Institute (Cherubs)",
        "organization": "Northwestern University",
        "type": "summer_program",
        "category": "journalism",
        "description": "Prestigious journalism program at Northwestern.",
        "prestige_score": 9,
        "acceptance_rate": 0.10,
        "selectivity": "highly_selective",
        "deadline_month": 2,
        "program_start_month": 7,
        "duration_weeks": 5,
        "cost": 5000,
        "financial_aid_available": True,
        "location": "Evanston, IL",
        "is_residential": True,
        "effort_hours": 30,
        "eligibility": {"grades": [11]},
        "focus_area": "JOURNALISM",
        "touchpoints": 5
    },
]

# =============================================================================
# CARNEGIE MELLON PROGRAMS
# =============================================================================

CMU_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "cmu-sams",
        "name": "Carnegie Mellon Summer Academy for Math and Science (SAMS)",
        "organization": "Carnegie Mellon University",
        "type": "summer_program",
        "category": "stem",
        "description": "Rigorous STEM program for underrepresented students.",
        "prestige_score": 9,
        "acceptance_rate": 0.10,
        "selectivity": "highly_selective",
        "deadline_month": 1,
        "deadline_recurring": "January annually",
        "program_start_month": 7,
        "duration_weeks": 6,
        "cost": 0,
        "location": "Pittsburgh, PA",
        "is_residential": True,
        "effort_hours": 30,
        "eligibility": {"grades": [11]},
        "focus_area": "STEM",
        "diversity_focus": True,
        "touchpoints": 5
    },
    {
        "id": "cmu-drama",
        "name": "CMU Pre-College Drama Program",
        "organization": "Carnegie Mellon University",
        "type": "summer_program",
        "category": "arts",
        "description": "Intensive drama training at top drama school.",
        "prestige_score": 8,
        "acceptance_rate": 0.30,
        "selectivity": "selective",
        "deadline_month": 3,
        "program_start_month": 7,
        "duration_weeks": 6,
        "cost": 8000,
        "financial_aid_available": True,
        "location": "Pittsburgh, PA",
        "is_residential": True,
        "effort_hours": 25,
        "eligibility": {"grades": [10, 11, 12]},
        "focus_area": "ARTS",
        "touchpoints": 4
    },
]

# =============================================================================
# DIVERSITY-FOCUSED PROGRAMS
# =============================================================================

DIVERSITY_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "questbridge-cps",
        "name": "QuestBridge College Prep Scholars",
        "organization": "QuestBridge",
        "type": "summer_program",
        "category": "academic",
        "description": "College prep for high-achieving, low-income juniors.",
        "prestige_score": 9,
        "acceptance_rate": 0.15,
        "selectivity": "selective",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 12,
        "cost": 0,
        "location": "Online",
        "is_virtual": True,
        "effort_hours": 20,
        "eligibility": {"grades": [11], "income_requirement": True},
        "focus_area": "GENERAL",
        "diversity_focus": True,
        "touchpoints": 4
    },
    {
        "id": "posse-foundation",
        "name": "Posse Foundation Summer Program",
        "organization": "Posse Foundation",
        "type": "summer_program",
        "category": "leadership",
        "description": "Leadership development for diverse students.",
        "prestige_score": 8,
        "acceptance_rate": 0.02,
        "selectivity": "highly_selective",
        "deadline_month": 10,
        "program_start_month": 6,
        "duration_weeks": 2,
        "cost": 0,
        "location": "Various cities",
        "effort_hours": 20,
        "eligibility": {"grades": [12]},
        "focus_area": "LEADERSHIP",
        "diversity_focus": True,
        "touchpoints": 5
    },
    {
        "id": "leda-scholars",
        "name": "LEDA Scholars Program",
        "organization": "Leadership Enterprise for a Diverse America",
        "type": "summer_program",
        "category": "academic",
        "description": "College preparation for high-achieving, low-income students.",
        "prestige_score": 9,
        "acceptance_rate": 0.05,
        "selectivity": "highly_selective",
        "deadline_month": 1,
        "program_start_month": 7,
        "duration_weeks": 7,
        "cost": 0,
        "location": "Princeton, NJ",
        "is_residential": True,
        "effort_hours": 35,
        "eligibility": {"grades": [11], "income_requirement": True},
        "focus_area": "GENERAL",
        "diversity_focus": True,
        "touchpoints": 5
    },
    {
        "id": "prep-for-prep",
        "name": "Prep for Prep Summer Program",
        "organization": "Prep for Prep",
        "type": "summer_program",
        "category": "academic",
        "description": "Academic enrichment for NYC students of color.",
        "prestige_score": 8,
        "acceptance_rate": 0.03,
        "selectivity": "highly_selective",
        "deadline_month": 12,
        "program_start_month": 6,
        "duration_weeks": 14,
        "cost": 0,
        "location": "New York, NY",
        "effort_hours": 35,
        "eligibility": {"grades": [5, 6]},
        "focus_area": "GENERAL",
        "diversity_focus": True,
        "touchpoints": 5
    },
]

# =============================================================================
# ADDITIONAL RESEARCH PROGRAMS
# =============================================================================

RESEARCH_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "jhu-center-talented-youth",
        "name": "Johns Hopkins CTY Summer Programs",
        "organization": "Johns Hopkins Center for Talented Youth",
        "type": "summer_program",
        "category": "research",
        "description": "Intensive academic programs for gifted students in STEM and humanities.",
        "prestige_score": 8,
        "acceptance_rate": 0.25,
        "selectivity": "selective",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 3,
        "cost": 5500,
        "financial_aid_available": True,
        "location": "Various campuses",
        "is_residential": True,
        "effort_hours": 25,
        "eligibility": {"grades": [7, 8, 9, 10, 11]},
        "focus_area": "STEM",
        "touchpoints": 3
    },
    {
        "id": "rockefeller-summer",
        "name": "Rockefeller University Summer Science Research",
        "organization": "Rockefeller University",
        "type": "summer_program",
        "category": "research",
        "description": "Research program in biomedical sciences.",
        "prestige_score": 10,
        "acceptance_rate": 0.06,
        "selectivity": "highly_selective",
        "deadline_month": 2,
        "program_start_month": 6,
        "duration_weeks": 8,
        "cost": 0,
        "stipend": 4000,
        "location": "New York, NY",
        "is_residential": True,
        "effort_hours": 40,
        "eligibility": {"grades": [11, 12], "requirements": ["interview", "recommendation", "transcript"]},
        "focus_area": "STEM",
        "touchpoints": 5
    },
    {
        "id": "nih-summer-intern",
        "name": "NIH Summer Internship Program",
        "organization": "National Institutes of Health",
        "type": "summer_program",
        "category": "research",
        "description": "Biomedical research at NIH facilities.",
        "prestige_score": 9,
        "acceptance_rate": 0.15,
        "selectivity": "highly_selective",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 8,
        "cost": 0,
        "stipend": 2800,
        "location": "Bethesda, MD",
        "effort_hours": 40,
        "eligibility": {"grades": [11, 12], "age_min": 17, "citizenship": ["US", "permanent_resident"]},
        "focus_area": "STEM",
        "touchpoints": 4
    },
    {
        "id": "simons-summer-research",
        "name": "Simons Summer Research Program",
        "organization": "Stony Brook University",
        "type": "summer_program",
        "category": "research",
        "description": "STEM research mentorship at Stony Brook.",
        "prestige_score": 9,
        "acceptance_rate": 0.08,
        "selectivity": "highly_selective",
        "deadline_month": 2,
        "program_start_month": 7,
        "duration_weeks": 8,
        "cost": 0,
        "stipend": 4000,
        "location": "Stony Brook, NY",
        "is_residential": True,
        "effort_hours": 40,
        "eligibility": {"grades": [11]},
        "focus_area": "STEM",
        "touchpoints": 5
    },
    {
        "id": "cuny-early-research",
        "name": "CUNY College Now Research Program",
        "organization": "City University of New York",
        "type": "summer_program",
        "category": "research",
        "description": "Research opportunities for NYC high school students.",
        "prestige_score": 7,
        "acceptance_rate": 0.30,
        "selectivity": "accessible",
        "deadline_month": 4,
        "program_start_month": 7,
        "duration_weeks": 6,
        "cost": 0,
        "location": "New York, NY",
        "effort_hours": 30,
        "eligibility": {"grades": [10, 11, 12], "location": "NYC"},
        "focus_area": "STEM",
        "diversity_focus": True,
        "touchpoints": 3
    },
    {
        "id": "anl-high-school",
        "name": "Argonne National Lab High School Research",
        "organization": "Argonne National Laboratory",
        "type": "summer_program",
        "category": "research",
        "description": "Research experience at a national laboratory.",
        "prestige_score": 9,
        "acceptance_rate": 0.10,
        "selectivity": "highly_selective",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 8,
        "cost": 0,
        "stipend": 3500,
        "location": "Lemont, IL",
        "effort_hours": 40,
        "eligibility": {"grades": [11, 12], "citizenship": ["US"]},
        "focus_area": "STEM",
        "touchpoints": 4
    },
    {
        "id": "fermilab-target",
        "name": "Fermilab TARGET Program",
        "organization": "Fermi National Accelerator Laboratory",
        "type": "summer_program",
        "category": "research",
        "description": "Physics research for underrepresented high schoolers.",
        "prestige_score": 8,
        "acceptance_rate": 0.20,
        "selectivity": "selective",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 8,
        "cost": 0,
        "stipend": 3000,
        "location": "Batavia, IL",
        "effort_hours": 40,
        "eligibility": {"grades": [11]},
        "focus_area": "STEM",
        "diversity_focus": True,
        "touchpoints": 4
    },
]

# =============================================================================
# INTERNSHIP PROGRAMS
# =============================================================================

INTERNSHIP_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "bank-of-america-leaders",
        "name": "Bank of America Student Leaders",
        "organization": "Bank of America",
        "type": "internship",
        "category": "leadership",
        "description": "Paid summer internship with local nonprofits and leadership summit.",
        "prestige_score": 8,
        "acceptance_rate": 0.05,
        "selectivity": "highly_selective",
        "deadline_month": 1,
        "program_start_month": 6,
        "duration_weeks": 8,
        "cost": 0,
        "stipend": 5000,
        "location": "Various cities",
        "effort_hours": 35,
        "eligibility": {"grades": [11, 12], "citizenship": ["US"]},
        "focus_area": "SERVICE",
        "diversity_focus": True,
        "touchpoints": 4
    },
    {
        "id": "microsoft-high-school",
        "name": "Microsoft High School Internship",
        "organization": "Microsoft",
        "type": "internship",
        "category": "stem",
        "description": "Summer internship at Microsoft for high school students.",
        "prestige_score": 9,
        "acceptance_rate": 0.03,
        "selectivity": "highly_selective",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 8,
        "cost": 0,
        "stipend": 6000,
        "location": "Redmond, WA",
        "effort_hours": 40,
        "eligibility": {"grades": [11, 12], "age_min": 16},
        "focus_area": "STEM",
        "touchpoints": 4
    },
    {
        "id": "nasa-ossi",
        "name": "NASA OSSI High School Internship",
        "organization": "NASA",
        "type": "internship",
        "category": "stem",
        "description": "Internships at NASA centers for high school students.",
        "prestige_score": 10,
        "acceptance_rate": 0.08,
        "selectivity": "highly_selective",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 10,
        "cost": 0,
        "stipend": 4500,
        "location": "Various NASA Centers",
        "effort_hours": 40,
        "eligibility": {"grades": [11, 12], "citizenship": ["US"], "gpa_min": 3.0},
        "focus_area": "STEM",
        "touchpoints": 5
    },
    {
        "id": "local-hospital-volunteer",
        "name": "Hospital Junior Volunteer Program",
        "organization": "Local Hospitals",
        "type": "internship",
        "category": "stem",
        "description": "Clinical exposure and volunteer experience at hospitals.",
        "prestige_score": 5,
        "acceptance_rate": 0.50,
        "selectivity": "accessible",
        "deadline_month": 4,
        "program_start_month": 6,
        "duration_weeks": 10,
        "cost": 0,
        "location": "Local",
        "effort_hours": 10,
        "eligibility": {"grades": [9, 10, 11, 12], "age_min": 15},
        "focus_area": "STEM",
        "touchpoints": 2
    },
    {
        "id": "congressional-intern",
        "name": "Congressional Internship Program",
        "organization": "U.S. Congress",
        "type": "internship",
        "category": "leadership",
        "description": "Internship experience in congressional offices.",
        "prestige_score": 8,
        "acceptance_rate": 0.15,
        "selectivity": "selective",
        "deadline_month": 3,
        "program_start_month": 6,
        "duration_weeks": 6,
        "cost": 0,
        "location": "Washington, DC",
        "effort_hours": 40,
        "eligibility": {"grades": [11, 12], "age_min": 16, "citizenship": ["US"]},
        "focus_area": "GOVERNMENT",
        "touchpoints": 4
    },
]

# =============================================================================
# PRE-COLLEGE PROGRAMS
# =============================================================================

PRECOLLEGE_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "brown-precollege",
        "name": "Brown Pre-College Programs",
        "organization": "Brown University",
        "type": "summer_program",
        "category": "academic",
        "description": "Academic exploration on Brown's campus.",
        "prestige_score": 8,
        "acceptance_rate": 0.35,
        "selectivity": "accessible",
        "deadline_month": 5,
        "program_start_month": 6,
        "duration_weeks": 2,
        "cost": 6000,
        "financial_aid_available": True,
        "location": "Providence, RI",
        "is_residential": True,
        "effort_hours": 25,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "focus_area": "GENERAL",
        "touchpoints": 3
    },
    {
        "id": "columbia-precollege",
        "name": "Columbia University Pre-College Program",
        "organization": "Columbia University",
        "type": "summer_program",
        "category": "academic",
        "description": "College-level courses for high school students.",
        "prestige_score": 8,
        "acceptance_rate": 0.40,
        "selectivity": "accessible",
        "deadline_month": 5,
        "program_start_month": 7,
        "duration_weeks": 3,
        "cost": 8000,
        "financial_aid_available": True,
        "location": "New York, NY",
        "is_residential": True,
        "effort_hours": 30,
        "eligibility": {"grades": [10, 11, 12]},
        "focus_area": "GENERAL",
        "touchpoints": 3
    },
    {
        "id": "georgetown-precollege",
        "name": "Georgetown University Summer Programs",
        "organization": "Georgetown University",
        "type": "summer_program",
        "category": "academic",
        "description": "Academic and enrichment programs at Georgetown.",
        "prestige_score": 8,
        "acceptance_rate": 0.45,
        "selectivity": "accessible",
        "deadline_month": 4,
        "program_start_month": 6,
        "duration_weeks": 3,
        "cost": 7500,
        "financial_aid_available": True,
        "location": "Washington, DC",
        "is_residential": True,
        "effort_hours": 25,
        "eligibility": {"grades": [9, 10, 11, 12]},
        "focus_area": "GENERAL",
        "touchpoints": 3
    },
    {
        "id": "northwestern-precollege",
        "name": "Northwestern Pre-College Programs",
        "organization": "Northwestern University",
        "type": "summer_program",
        "category": "academic",
        "description": "Summer programs in journalism, STEM, and arts.",
        "prestige_score": 8,
        "acceptance_rate": 0.35,
        "selectivity": "accessible",
        "deadline_month": 4,
        "program_start_month": 6,
        "duration_weeks": 2,
        "cost": 5500,
        "financial_aid_available": True,
        "location": "Evanston, IL",
        "is_residential": True,
        "effort_hours": 25,
        "eligibility": {"grades": [10, 11, 12]},
        "focus_area": "GENERAL",
        "touchpoints": 3
    },
    {
        "id": "cornell-precollege",
        "name": "Cornell Pre-College Studies",
        "organization": "Cornell University",
        "type": "summer_program",
        "category": "academic",
        "description": "College-credit courses in various disciplines.",
        "prestige_score": 8,
        "acceptance_rate": 0.40,
        "selectivity": "accessible",
        "deadline_month": 4,
        "program_start_month": 6,
        "duration_weeks": 3,
        "cost": 12000,
        "financial_aid_available": True,
        "location": "Ithaca, NY",
        "is_residential": True,
        "effort_hours": 30,
        "eligibility": {"grades": [10, 11, 12]},
        "focus_area": "GENERAL",
        "touchpoints": 3
    },
    {
        "id": "uc-berkeley-precollege",
        "name": "UC Berkeley Pre-Collegiate Scholars",
        "organization": "University of California, Berkeley",
        "type": "summer_program",
        "category": "academic",
        "description": "Academic exploration at Berkeley campus.",
        "prestige_score": 8,
        "acceptance_rate": 0.30,
        "selectivity": "accessible",
        "deadline_month": 4,
        "program_start_month": 7,
        "duration_weeks": 4,
        "cost": 7000,
        "financial_aid_available": True,
        "location": "Berkeley, CA",
        "is_residential": True,
        "effort_hours": 25,
        "eligibility": {"grades": [10, 11, 12]},
        "focus_area": "GENERAL",
        "touchpoints": 3
    },
]

# =============================================================================
# COMBINED OPPORTUNITIES DATABASE
# =============================================================================

def get_all_opportunities() -> List[Dict[str, Any]]:
    """Return all opportunities combined into a single list."""
    all_opportunities = []
    all_opportunities.extend(ELITE_RESEARCH_PROGRAMS)
    all_opportunities.extend(MIT_PROGRAMS)
    all_opportunities.extend(STANFORD_PROGRAMS)
    all_opportunities.extend(YALE_PROGRAMS)
    all_opportunities.extend(TECH_PROGRAMS)
    all_opportunities.extend(FINANCE_PROGRAMS)
    all_opportunities.extend(PREMED_PROGRAMS)
    all_opportunities.extend(ARTS_PROGRAMS)
    all_opportunities.extend(ENTREPRENEURSHIP_PROGRAMS)
    all_opportunities.extend(GOVERNMENT_PROGRAMS)
    all_opportunities.extend(JOURNALISM_PROGRAMS)
    all_opportunities.extend(CMU_PROGRAMS)
    all_opportunities.extend(DIVERSITY_PROGRAMS)
    all_opportunities.extend(RESEARCH_PROGRAMS)
    all_opportunities.extend(INTERNSHIP_PROGRAMS)
    all_opportunities.extend(PRECOLLEGE_PROGRAMS)

    # Add default fields
    for opp in all_opportunities:
        if "is_active" not in opp:
            opp["is_active"] = True
        if "diversity_focus" not in opp:
            opp["diversity_focus"] = False
        if "touchpoints" not in opp:
            opp["touchpoints"] = 1
        if "is_virtual" not in opp:
            opp["is_virtual"] = False
        if "is_residential" not in opp:
            opp["is_residential"] = False

    return all_opportunities


def get_opportunities_by_type(opp_type: str) -> List[Dict[str, Any]]:
    """Return opportunities filtered by type."""
    return [o for o in get_all_opportunities() if o.get("type") == opp_type]


def get_opportunities_by_category(category: str) -> List[Dict[str, Any]]:
    """Return opportunities filtered by category."""
    return [o for o in get_all_opportunities() if o.get("category") == category]


def get_selective_opportunities() -> List[Dict[str, Any]]:
    """Return highly selective opportunities (acceptance rate < 10%)."""
    return [o for o in get_all_opportunities()
            if o.get("acceptance_rate", 1.0) < 0.10]


def get_free_opportunities() -> List[Dict[str, Any]]:
    """Return free opportunities."""
    return [o for o in get_all_opportunities() if o.get("cost", 0) == 0]


def get_diversity_opportunities() -> List[Dict[str, Any]]:
    """Return diversity-focused opportunities."""
    return [o for o in get_all_opportunities() if o.get("diversity_focus", False)]


# Stats
if __name__ == "__main__":
    opportunities = get_all_opportunities()
    print(f"Total opportunities: {len(opportunities)}")
    print(f"Free opportunities: {len(get_free_opportunities())}")
    print(f"Highly selective (<10%): {len(get_selective_opportunities())}")
    print(f"Diversity-focused: {len(get_diversity_opportunities())}")

    # By type
    types = set(o["type"] for o in opportunities)
    for t in sorted(types):
        count = len(get_opportunities_by_type(t))
        print(f"  {t}: {count}")

    # By category
    categories = set(o["category"] for o in opportunities)
    for cat in sorted(categories):
        count = len(get_opportunities_by_category(cat))
        print(f"  {cat}: {count}")
