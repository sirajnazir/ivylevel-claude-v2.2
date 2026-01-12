"""
IvyQuest v10.0 - Database Seed Script
=====================================

Populates the database with:
- 80+ awards
- 50+ opportunities
- Golden evaluation examples (initial set)

Run with:
    python -m scripts.seed_database

Or from agents directory:
    python scripts/seed_database.py
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seeds.awards_data import get_all_awards, get_active_awards
from seeds.opportunities_data import get_all_opportunities
from tools.database import get_supabase_client


def transform_award_for_db(award: Dict[str, Any]) -> Dict[str, Any]:
    """Transform award data for database insertion."""
    # Map category to enum value
    category_map = {
        "stem": "stem",
        "humanities": "humanities",
        "arts": "arts",
        "leadership": "leadership",
        "service": "service",
        "academic": "academic",
        "entrepreneurship": "entrepreneurship",
        "journalism": "journalism",
        "debate": "debate",
        "research": "research",
    }

    # Map level to enum value
    level_map = {
        "school": "school",
        "local": "local",
        "regional": "regional",
        "state": "state",
        "national": "national",
        "international": "international",
    }

    # Calculate deadline date for this year
    deadline_date = None
    if award.get("deadline_month"):
        year = datetime.now().year
        # If deadline month has passed, use next year
        if award["deadline_month"] < datetime.now().month:
            year += 1
        deadline_date = datetime(year, award["deadline_month"], 15).date().isoformat()

    return {
        # Note: omit id to let database auto-generate UUID
        "name": award["name"],
        "organization": award.get("organization"),
        "description": award.get("description"),
        "category": category_map.get(award.get("category", "academic"), "academic"),
        "level": level_map.get(award.get("level", "national"), "national"),
        "deadline": deadline_date,
        "deadline_recurring": award.get("deadline_recurring"),
        "prestige_score": award.get("prestige_score", 5),
        "historical_win_rate": award.get("historical_win_rate"),
        "effort_hours": award.get("effort_hours"),
        "eligibility": award.get("eligibility", {}),
        "requirements": award.get("touchpoint_types", []),
        "prize_amount": award.get("prize_amount"),
        "prize_type": award.get("prize_type"),
        "touchpoints": award.get("touchpoints", 1),
        "touchpoint_types": award.get("touchpoint_types", []),
        "is_active": award.get("is_active", True),
    }


def transform_opportunity_for_db(opp: Dict[str, Any]) -> Dict[str, Any]:
    """Transform opportunity data for database insertion."""
    # Map type to enum value
    type_map = {
        "summer_program": "summer_program",
        "internship": "internship",
        "research": "research",
        "competition": "competition",
        "conference": "conference",
        "fellowship": "fellowship",
        "scholarship": "scholarship",
        "mentorship": "mentorship",
        "leadership": "leadership",
        "study_abroad": "study_abroad",
    }

    # Map category
    category_map = {
        "stem": "stem",
        "humanities": "humanities",
        "arts": "arts",
        "leadership": "leadership",
        "service": "service",
        "academic": "academic",
        "entrepreneurship": "entrepreneurship",
        "journalism": "journalism",
        "research": "research",
    }

    # Calculate deadline date
    deadline_date = None
    if opp.get("deadline_month"):
        year = datetime.now().year
        if opp["deadline_month"] < datetime.now().month:
            year += 1
        deadline_date = datetime(year, opp["deadline_month"], 15).date().isoformat()

    # Calculate program dates
    program_start = None
    program_end = None
    if opp.get("program_start_month"):
        year = datetime.now().year
        if opp["program_start_month"] < datetime.now().month:
            year += 1
        program_start = datetime(year, opp["program_start_month"], 1).date().isoformat()
        if opp.get("duration_weeks"):
            program_end = (datetime(year, opp["program_start_month"], 1) +
                         timedelta(weeks=opp["duration_weeks"])).date().isoformat()

    return {
        # Note: omit id to let database auto-generate UUID
        "name": opp["name"],
        "organization": opp.get("organization"),
        "description": opp.get("description"),
        "type": type_map.get(opp.get("type", "summer_program"), "summer_program"),
        "category": category_map.get(opp.get("category"), None),
        "application_deadline": deadline_date,
        "deadline_recurring": opp.get("deadline_recurring"),
        "program_start_date": program_start,
        "program_end_date": program_end,
        "duration_weeks": opp.get("duration_weeks"),
        "acceptance_rate": opp.get("acceptance_rate"),
        "prestige_score": opp.get("prestige_score", 5),
        "effort_hours": opp.get("effort_hours"),
        "touchpoints": opp.get("touchpoints", 1),
        "eligibility": opp.get("eligibility", {}),
        "requirements": opp.get("touchpoint_types", []),
        "cost": opp.get("cost"),
        "stipend": opp.get("stipend"),
        "financial_aid_available": opp.get("financial_aid_available", False),
        "location": opp.get("location"),
        "is_virtual": opp.get("is_virtual", False),
        "is_residential": opp.get("is_residential", False),
        "is_active": opp.get("is_active", True),
    }


async def seed_awards(db) -> int:
    """Seed awards table with data."""
    awards = get_active_awards()
    print(f"Seeding {len(awards)} awards...")

    seeded = 0
    for award in awards:
        try:
            db_award = transform_award_for_db(award)
            # Use insert (database auto-generates UUID)
            result = db.table("awards").insert(db_award).execute()
            seeded += 1
        except Exception as e:
            # Skip duplicates (name already exists)
            if "duplicate" in str(e).lower():
                seeded += 1  # Count as success if already exists
            else:
                print(f"  Error seeding award {award.get('name')}: {e}")

    print(f"  Seeded {seeded} awards successfully")
    return seeded


async def seed_opportunities(db) -> int:
    """Seed opportunities table with data."""
    opportunities = get_all_opportunities()
    print(f"Seeding {len(opportunities)} opportunities...")

    seeded = 0
    for opp in opportunities:
        try:
            db_opp = transform_opportunity_for_db(opp)
            # Use insert (database auto-generates UUID)
            result = db.table("opportunities").insert(db_opp).execute()
            seeded += 1
        except Exception as e:
            # Skip duplicates (name already exists)
            if "duplicate" in str(e).lower():
                seeded += 1  # Count as success if already exists
            else:
                print(f"  Error seeding opportunity {opp.get('name')}: {e}")

    print(f"  Seeded {seeded} opportunities successfully")
    return seeded


async def seed_golden_examples(db) -> int:
    """Seed evaluation golden examples."""
    print("Seeding golden evaluation examples...")

    # Initial golden examples from Jenny Duan coaching
    golden_examples = [
        {
            "profile_id": "golden-huda-001",
            "input_profile": {
                "identity": {"first_name": "Huda", "grade": 10},
                "operating": {
                    "gender": "FEMALE",
                    "culturalBackground": ["SOUTH_ASIAN"],
                    "religion": "Muslim",
                    "firstGeneration": True
                },
                "aptitude": {
                    "gpa_weighted": 3.9,
                    "sat_total": 1570,
                    "ap_count": 8
                },
                "passion": {
                    "spike_category": "STEM",
                    "leadership_level": "FOUNDER_LOCAL",
                    "brag_text": "Building apps to help underrepresented girls learn coding"
                },
                "community": {"service_hours": 350}
            },
            "expected_outputs": {
                "brand_statement": "A South Asian Muslim innovator empowering girls through code, building pathways to STEM equity in her community and beyond.",
                "themes": ["STEM Equity", "Community Empowerment", "Cultural Bridge-Building", "First-Generation Success", "Impact through Innovation"],
                "first_principle": "To dismantle barriers and create equitable access to STEM education for underrepresented girls, empowering them to become innovators.",
                "archetype": {"id": "CHANGEMAKER", "label": "Impact-Driven Innovator"}
            },
            "jenny_annotations": {
                "brand_statement_quality": 5,
                "theme_coherence": 5,
                "activity_alignment": 5,
                "notes": "Strong identity synthesis with clear spike. Model example."
            },
            "difficulty_tier": "medium",
            "tags": ["stem", "first-gen", "female", "south-asian"]
        },
        {
            "profile_id": "golden-hiba-001",
            "input_profile": {
                "identity": {"first_name": "Hiba", "grade": 11},
                "operating": {
                    "gender": "FEMALE",
                    "culturalBackground": ["MIDDLE_EASTERN"],
                    "firstGeneration": False
                },
                "aptitude": {
                    "gpa_weighted": 4.2,
                    "sat_total": 1520,
                    "ap_count": 10
                },
                "passion": {
                    "spike_category": "SERVICE",
                    "leadership_level": "FOUNDER_STATE",
                    "brag_text": "Founded mental health awareness organization reaching 5000+ students"
                },
                "community": {"service_hours": 500, "service_leadership": "FOUNDER_STATE"}
            },
            "expected_outputs": {
                "brand_statement": "A mental health advocate transforming student wellness culture through peer education and destigmatization initiatives.",
                "themes": ["Mental Health Advocacy", "Peer Leadership", "Wellness Education", "Community Building", "Destigmatization"],
                "first_principle": "To create safe spaces where young people can openly discuss mental health and access the support they need.",
                "archetype": {"id": "ADVOCATE", "label": "Wellness Advocate"}
            },
            "jenny_annotations": {
                "brand_statement_quality": 5,
                "theme_coherence": 5,
                "activity_alignment": 5,
                "notes": "Clear service spike with measurable impact."
            },
            "difficulty_tier": "medium",
            "tags": ["service", "leadership", "mental-health"]
        },
        {
            "profile_id": "golden-academic-001",
            "input_profile": {
                "identity": {"first_name": "Alex", "grade": 11},
                "operating": {
                    "gender": "MALE",
                    "culturalBackground": ["ASIAN"],
                    "firstGeneration": False
                },
                "aptitude": {
                    "gpa_weighted": 4.5,
                    "sat_total": 1580,
                    "ap_count": 12,
                    "academic_awards": ["USAMO", "USACO_PLATINUM"]
                },
                "passion": {
                    "spike_category": "RESEARCH",
                    "leadership_level": "NATIONAL_PRES",
                    "brag_text": "Published research in computational biology"
                },
                "community": {"service_hours": 150}
            },
            "expected_outputs": {
                "brand_statement": "A computational biologist merging algorithmic thinking with biological discovery to advance personalized medicine.",
                "themes": ["Computational Biology", "Research Excellence", "Interdisciplinary Innovation", "Academic Leadership"],
                "first_principle": "To harness the power of computation to decode biological complexity and improve human health.",
                "archetype": {"id": "RESEARCHER", "label": "Computational Scientist"}
            },
            "jenny_annotations": {
                "brand_statement_quality": 4,
                "theme_coherence": 5,
                "activity_alignment": 5,
                "notes": "Strong academic profile, narrative could be more distinctive."
            },
            "difficulty_tier": "easy",
            "tags": ["stem", "research", "competitive", "male"]
        },
    ]

    seeded = 0
    for example in golden_examples:
        try:
            result = db.table("evaluation_golden").upsert(
                example,
                on_conflict="profile_id"
            ).execute()
            seeded += 1
        except Exception as e:
            print(f"  Error seeding golden example {example['profile_id']}: {e}")

    print(f"  Seeded {seeded} golden examples successfully")
    return seeded


async def main():
    """Main seed function."""
    print("=" * 60)
    print("IvyQuest v10.0 Database Seeder")
    print("=" * 60)

    try:
        db = get_supabase_client()
        print("Connected to Supabase")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("Make sure SUPABASE_URL and SUPABASE_SERVICE_KEY are set")
        return

    # Seed awards
    awards_count = await seed_awards(db)

    # Seed opportunities
    opps_count = await seed_opportunities(db)

    # Seed golden examples
    golden_count = await seed_golden_examples(db)

    print("=" * 60)
    print("Seeding complete!")
    print(f"  Awards: {awards_count}")
    print(f"  Opportunities: {opps_count}")
    print(f"  Golden Examples: {golden_count}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
