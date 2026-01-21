#!/usr/bin/env python3
"""
IvyQuest v10.0 - Mile Deep End-to-End Test
==========================================

Run this from your project's agents/ directory:
  cd /Users/snazir/ivyquest-claude-v2.2/agents
  source venv/bin/activate
  python tests/test_mile_deep_e2e.py

Tests the QUALITATIVE depth of each agent in sequence:
1. Assessment Agent → Narrative DNA, Archetype, CRI, Hidden Probabilities
2. Game Plan Agent → Activities (4+ touchpoints), Identity Seeds, Strategic Overwhelm
3. Awards Agent → Win Probability, Portfolio Balancing (Likely/Target/Stretch)
4. Opportunities Agent → Fit Score, 6-Month Alerts, Backup Cascades
5. Execution Agent → Project Scaffolding, EDS

Uses Huda benchmark profile for validation.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
from dotenv import load_dotenv
# Go up two levels from tests/ -> agents/ -> project_root/
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env.local')
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
    print(f"✓ Loaded environment from {env_path}")
else:
    print(f"⚠ No .env.local found at {env_path}")

# Verify API key
api_key = os.getenv("OPENAI_API_KEY", "")
if api_key and api_key.startswith("sk-"):
    print(f"✓ OpenAI API Key loaded: {api_key[:8]}...{api_key[-4:]}")
else:
    print("❌ OPENAI_API_KEY not found or invalid")
    sys.exit(1)


# =============================================================================
# HUDA BENCHMARK PROFILE - Real Student Archetype
# =============================================================================

HUDA_PROFILE = {
    "id": "huda-e2e-test-001",
    "user_id": "huda-e2e-user",
    "email": "huda@ivylevel.com",
    "first_name": "Huda",
    "grade": 10,
    "narrative_dna": None,
    "cri": None,
    "profile_data": {
        "identity": {
            "grade": 10,
            "school_type": "PUBLIC"
        },
        "passion": {
            "spike_category": "STEM",
            "brag_text": """Founded Empowering AI, a nonprofit teaching underserved communities
            about AI ethics and algorithmic justice. Reached 6,400 students across 12 countries
            and raised $23K in funding. Won 5 national awards including NCWIT Award for
            Aspirations in Computing and Congressional App Challenge. Created curriculum
            bridging my Muslim identity with tech education, showing how algorithmic bias
            disproportionately affects minority communities. Published op-ed in local newspaper
            about AI in college admissions. Featured speaker at 3 tech conferences.""",
            "project_description": """Empowering AI creates workshops and online curriculum
            teaching underserved high school students about artificial intelligence, machine
            learning ethics, and algorithmic bias. We partner with Title I schools and
            community centers to provide free education. Our flagship program 'AI for Justice'
            explores how AI systems perpetuate racial and socioeconomic inequities. We've
            developed a 12-module curriculum used by 50+ schools.""",
            "leadership_level": "FOUNDER_NATIONAL",
            "research_level": "PRESENTED_STATE"
        },
        "aptitude": {
            "gpa_weighted": 4.5,
            "gpa_unweighted": 3.95,
            "sat_total": 1520,
            "sat_math": 780,
            "sat_reading": 740,
            "ap_courses": 8,
            "ap_scores": {"CS_A": 5, "Calc_BC": 5, "Physics_1": 5, "US_History": 4}
        },
        "demographics": {
            "first_gen": True,
            "ethnicity": "SOUTH_ASIAN",
            "religion": "MUSLIM",
            "underrepresented": True,
            "income_band": "MIDDLE",
            "geographic": "SUBURBAN"
        },
        "operating": {
            "strengths": ["competitive", "hands-on", "teaching", "public-speaking", "writing"],
            "weaknesses": ["time-management", "perfectionism"],
            "availableHoursPerWeek": 15,
            "firstGeneration": True,
            "careerDirection": "AI Research / Tech Ethics / Policy",
            "favoriteSubject": "Computer Science"
        },
        "community": {
            "service_hours": 250,
            "students_impacted": 6400,
            "funds_raised": 23000,
            "countries_reached": 12
        },
        "achievements": [
            {"name": "NCWIT Award for Aspirations in Computing", "level": "national", "year": 2024},
            {"name": "Congressional App Challenge Winner", "level": "national", "year": 2024},
            {"name": "Diamond Challenge Semi-Finalist", "level": "national", "year": 2024},
            {"name": "State Science Fair - 1st Place CS", "level": "state", "year": 2024},
            {"name": "Presidential Volunteer Service Award - Gold", "level": "national", "year": 2023}
        ],
        "target_schools": ["STANFORD", "MIT", "COLUMBIA", "YALE", "PRINCETON", "HARVARD"],
        "intended_major": "Computer Science",
        "constraints": [
            "First-generation college student",
            "Family responsibilities - helps with younger siblings",
            "Limited access to paid programs/tutoring",
            "Public school with fewer AP options",
            "No legacy connections"
        ]
    },
    "target_schools": ["STANFORD", "MIT", "COLUMBIA", "YALE", "PRINCETON", "HARVARD"]
}


# =============================================================================
# QUALITY VALIDATOR
# =============================================================================

class QualityValidator:
    """Validates the qualitative depth of agent outputs"""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.current_section = ""

    def section(self, name: str):
        """Start a new section"""
        self.current_section = name
        print(f"\n{'─'*60}")
        print(f"  {name}")
        print(f"{'─'*60}")

    def check(self, name: str, condition: bool, details: str = ""):
        """Record a quality check"""
        status = "✅" if condition else "❌"
        self.results.append({
            "section": self.current_section,
            "name": name,
            "passed": condition,
            "details": details
        })
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        print(f"  {status} {name}")
        if details and not condition:
            print(f"      └─ {details[:80]}")

    def summary(self):
        """Print summary of all checks"""
        total = self.passed + self.failed
        pct = (self.passed / total * 100) if total > 0 else 0

        print(f"\n{'═'*60}")
        print(f"  QUALITY VALIDATION SUMMARY")
        print(f"{'═'*60}")
        print(f"  Passed: {self.passed}/{total} ({pct:.0f}%)")
        print(f"  Failed: {self.failed}/{total}")

        if self.failed > 0:
            print(f"\n  Failed checks:")
            for r in self.results:
                if not r['passed']:
                    print(f"    ❌ [{r['section']}] {r['name']}")
                    if r['details']:
                        print(f"       {r['details'][:60]}")

        print(f"{'═'*60}\n")
        return self.passed == total


# =============================================================================
# LEG 1: ASSESSMENT AGENT
# =============================================================================

async def test_assessment_agent(profile: Dict, validator: QualityValidator) -> Dict:
    """Test Assessment Agent - Mile Deep"""

    print("\n" + "═"*60)
    print("  LEG 1: ASSESSMENT AGENT")
    print("  Testing: Narrative DNA, Archetype, CRI, Hidden Probabilities")
    print("═"*60)

    from agents.assessment import AssessmentAgent
    agent = AssessmentAgent()
    results = {}

    # ─────────────────────────────────────────────────────────────
    # 1.1 NARRATIVE DNA SYNTHESIS
    # ─────────────────────────────────────────────────────────────
    validator.section("1.1 Narrative DNA Synthesis")

    print("\n  🔄 Calling GPT-4o for narrative synthesis...")
    narrative = await agent.synthesize_narrative_dna(profile)
    results["narrative_dna"] = narrative

    dna = narrative.get('dna', '')
    confidence = narrative.get('confidence', 0)
    themes = narrative.get('themes', [])

    print(f"\n  📝 DNA: \"{dna[:100]}...\"")
    print(f"  📊 Confidence: {confidence:.0%}")
    print(f"  🏷️  Themes: {themes}")

    # Quality checks
    validator.check(
        "DNA is substantive (>50 chars)",
        len(dna) > 50 and dna != "Student narrative DNA placeholder",
        f"Length: {len(dna)}"
    )

    validator.check(
        "Confidence is calibrated (50-95%)",
        0.5 <= confidence <= 0.95,
        f"Got {confidence:.0%}"
    )

    # Check for Huda's identity themes
    combined = (dna + ' ' + ' '.join(themes)).lower()

    tech_match = any(k in combined for k in ["ai", "tech", "algorithm", "computer", "digital", "machine learning"])
    validator.check("Captures TECH/AI identity", tech_match, "Keywords: ai, tech, algorithm, computer")

    education_match = any(k in combined for k in ["education", "teaching", "student", "learn", "curriculum"])
    validator.check("Captures EDUCATION identity", education_match, "Keywords: education, teaching, student")

    equity_match = any(k in combined for k in ["equity", "justice", "underserved", "community", "access", "empower"])
    validator.check("Captures EQUITY/JUSTICE identity", equity_match, "Keywords: equity, justice, underserved")

    validator.check("Has 3+ themes", len(themes) >= 3, f"Got {len(themes)} themes")

    # ─────────────────────────────────────────────────────────────
    # 1.2 ARCHETYPE DETECTION
    # ─────────────────────────────────────────────────────────────
    validator.section("1.2 Archetype Detection")

    print("\n  🔄 Detecting student archetype...")
    archetype = await agent.detect_archetype(profile, narrative)
    results["archetype"] = archetype

    label = archetype.get('label', 'Unknown')
    arch_confidence = archetype.get('confidence', 0)
    rationale = archetype.get('rationale', '')

    print(f"\n  🎭 Archetype: {label}")
    print(f"  📊 Confidence: {arch_confidence:.0%}")
    print(f"  💭 Rationale: {rationale[:100]}...")

    expected = ["Constrained Gritty", "Community Leader", "Creative Innovator", "Mission-Driven Leader"]
    validator.check(
        f"Archetype fits profile ({expected[:2]}...)",
        any(e.lower() in label.lower() for e in expected),
        f"Got: {label}"
    )

    validator.check("Archetype confidence >50%", arch_confidence > 0.5, f"Got {arch_confidence:.0%}")
    validator.check("Has substantive rationale", len(rationale) > 50, f"Length: {len(rationale)}")

    # ─────────────────────────────────────────────────────────────
    # 1.3 HIDDEN PROBABILITY MATRIX
    # ─────────────────────────────────────────────────────────────
    validator.section("1.3 Hidden Probability Matrix")

    cri = 1.25  # First-gen boost
    results["cri"] = cri

    print("\n  🔄 Calculating admission probabilities...")
    probabilities = await agent.calculate_hidden_probabilities(profile, cri=cri)
    results["hidden_probabilities"] = probabilities

    base_rates = {"STANFORD": 0.037, "MIT": 0.033, "COLUMBIA": 0.037, "YALE": 0.045, "PRINCETON": 0.040, "HARVARD": 0.032}

    print(f"\n  {'School':<12} {'Base':<8} {'Calculated':<10} {'Boost'}")
    print(f"  {'─'*44}")

    all_above = True
    for school in profile.get("target_schools", []):
        base = base_rates.get(school, 0.05)
        calc = probabilities.get(school, 0)
        boost = calc / base if base > 0 else 0
        status = "✓" if calc > base else "✗"
        print(f"  {school:<12} {base:.1%}     {calc:.1%}      {boost:.1f}x {status}")
        if calc <= base:
            all_above = False

    validator.check("All probabilities above base rates", all_above, "Strong profile should boost")
    validator.check("Probabilities realistic (<40%)", all(p < 0.40 for p in probabilities.values()), "No >40%")

    # ─────────────────────────────────────────────────────────────
    # 1.4 CONSTRAINT REFRAMING
    # ─────────────────────────────────────────────────────────────
    validator.section("1.4 Constraint Reframing")

    print("\n  🔄 Reframing constraints as strengths...")
    reframes = await agent.reframe_constraints(profile, narrative)
    results["constraint_reframes"] = reframes

    print(f"\n  Reframes: {len(reframes)}")
    for i, rf in enumerate(reframes[:3], 1):
        print(f"\n  {i}. \"{rf.get('constraint', '')}\"")
        print(f"     → \"{rf.get('reframed_as', '')[:80]}...\"")

    validator.check("Generated 2+ reframes", len(reframes) >= 2, f"Got {len(reframes)}")
    validator.check(
        "Reframes are substantive",
        all(len(rf.get('reframed_as', '')) > 30 for rf in reframes),
        "Each >30 chars"
    )

    # Check empowering language
    negative = ["despite", "unfortunately", "lack", "unable", "cannot", "disadvantage"]
    reframe_text = ' '.join([rf.get('reframed_as', '').lower() for rf in reframes])
    has_negative = any(w in reframe_text for w in negative)
    validator.check("Reframes use empowering language", not has_negative, f"Avoid: {negative[:3]}")

    return results


# =============================================================================
# LEG 2: GAME PLAN AGENT
# =============================================================================

async def test_gameplan_agent(profile: Dict, assessment: Dict, validator: QualityValidator) -> Dict:
    """Test Game Plan Agent - Mile Deep"""

    print("\n" + "═"*60)
    print("  LEG 2: GAME PLAN AGENT")
    print("  Testing: Activity Filtering, Identity Seeds, Strategic Overwhelm")
    print("═"*60)

    from agents.gameplan import GamePlanAgent
    agent = GamePlanAgent()
    results = {}

    # Inject narrative DNA
    profile_enhanced = profile.copy()
    profile_enhanced["narrative_dna"] = assessment.get("narrative_dna", {}).get("dna", "")

    # ─────────────────────────────────────────────────────────────
    # 2.1 ACTIVITY FILTERING (ACP-005)
    # ─────────────────────────────────────────────────────────────
    validator.section("2.1 Activity Filtering (ACP-005: ≥4 Touchpoints)")

    print("\n  🔄 Filtering activities by ROI and touchpoints...")
    activities = await agent.filter_activities_by_roi(profile_enhanced)
    results["activities"] = activities

    print(f"\n  Activities: {len(activities)}")
    print(f"\n  {'Activity':<40} {'Touch':<6} {'ROI':<6} {'Hours'}")
    print(f"  {'─'*60}")

    for act in activities[:6]:
        name = act.get('name', '')[:40]
        touch = act.get('touchpoint_count', 0)
        roi = act.get('roi', 0)
        hours = act.get('hours_required', 0)
        print(f"  {name:<40} {touch:<6} {roi:<6.2f} {hours}")

    validator.check("Generated 3+ activities", len(activities) >= 3, f"Got {len(activities)}")

    all_4_touch = all(a.get('touchpoint_count', 0) >= 4 for a in activities)
    validator.check("All have ≥4 touchpoints (ACP-005)", all_4_touch, "ACP-005 compliance")

    sorted_by_roi = activities == sorted(activities, key=lambda x: x.get('roi', 0), reverse=True)
    validator.check("Sorted by ROI (highest first)", sorted_by_roi or len(activities) < 2, "Descending ROI")

    # ─────────────────────────────────────────────────────────────
    # 2.2 IDENTITY SEED PLANTING (ACP-006)
    # ─────────────────────────────────────────────────────────────
    validator.section("2.2 Identity Seed Planting (ACP-006: 6-8 Mo Ahead)")

    deadlines = [
        {"name": "Stanford REA", "type": "early_application", "date": "2025-11-01"},
        {"name": "RSI Application", "type": "summer_program", "date": "2025-01-15"},
        {"name": "NCWIT Award", "type": "awards", "date": "2025-10-31"},
        {"name": "Regeneron STS", "type": "awards", "date": "2025-11-09"}
    ]

    print("\n  🔄 Planting identity seeds for major deadlines...")
    seeds = await agent.plant_identity_seeds(profile_enhanced, deadlines)
    results["identity_seeds"] = seeds

    print(f"\n  Seeds planted: {len(seeds)}")
    for seed in seeds[:3]:
        target = seed.get('target', 'Unknown')
        actions = seed.get('actions', [])
        months = seed.get('months_until_bloom', 0)
        print(f"\n  🌱 {target}")
        print(f"     Months until deadline: {months}")
        print(f"     Actions: {len(actions)}")
        for j, act in enumerate(actions[:3], 1):
            act_text = act.get('action', str(act)) if isinstance(act, dict) else str(act)
            print(f"       {j}. {act_text[:55]}...")

    validator.check("Planted 3+ seeds", len(seeds) >= 3, f"Got {len(seeds)}")

    all_have_actions = all(len(s.get('actions', [])) >= 3 for s in seeds)
    validator.check("Each seed has 3+ actions", all_have_actions, "Actionable next steps")

    # ─────────────────────────────────────────────────────────────
    # 2.3 STRATEGIC OVERWHELM (ACP-004)
    # ─────────────────────────────────────────────────────────────
    validator.section("2.3 Strategic Overwhelm (ACP-004: 1.4x)")

    base_count = len(activities)
    overwhelmed = agent.apply_strategic_overwhelm(activities)
    results["overwhelmed"] = overwhelmed

    ratio = len(overwhelmed) / base_count if base_count > 0 else 0
    stretch = len([a for a in overwhelmed if a.get('is_stretch')])

    print(f"\n  Base activities: {base_count}")
    print(f"  After overwhelm: {len(overwhelmed)}")
    print(f"  Stretch added: {stretch}")
    print(f"  Ratio: {ratio:.2f}x")

    validator.check("Overwhelm ratio 1.3-1.5x", 1.3 <= ratio <= 1.5, f"Got {ratio:.2f}x")
    validator.check("Added stretch activities", stretch > 0, f"Got {stretch}")

    # ─────────────────────────────────────────────────────────────
    # 2.4 NARRATIVE THREADING
    # ─────────────────────────────────────────────────────────────
    validator.section("2.4 Narrative Threading")

    print("\n  🔄 Threading activities to narrative DNA...")
    hidden_target = profile_enhanced.get("target_schools", ["STANFORD"])[0]  # Default to first target
    threaded = await agent.thread_narrative_dna(overwhelmed, profile_enhanced.get("narrative_dna", ""), hidden_target)
    results["threaded"] = threaded

    with_threads = [a for a in threaded if a.get('narrative_thread')]
    print(f"\n  Activities with threads: {len(with_threads)}/{len(threaded)}")

    for act in with_threads[:2]:
        print(f"\n  📌 {act.get('name', '')}")
        print(f"     Thread: \"{act.get('narrative_thread', '')[:70]}...\"")

    thread_pct = len(with_threads) / len(threaded) if threaded else 0
    validator.check("80%+ have narrative threads", thread_pct >= 0.8, f"Got {thread_pct:.0%}")

    return results


# =============================================================================
# LEG 3: AWARDS AGENT
# =============================================================================

async def test_awards_agent(profile: Dict, assessment: Dict, validator: QualityValidator) -> Dict:
    """Test Awards Agent - Mile Deep"""

    print("\n" + "═"*60)
    print("  LEG 3: AWARDS AGENT")
    print("  Testing: Win Probability, Portfolio Balancing")
    print("═"*60)

    from agents.awards import AwardsAgent
    agent = AwardsAgent()
    results = {}

    profile_enhanced = profile.copy()
    profile_enhanced["narrative_dna"] = assessment.get("narrative_dna", {}).get("dna", "")
    profile_enhanced["cri"] = assessment.get("cri", 1.0)

    # ─────────────────────────────────────────────────────────────
    # 3.1 WIN PROBABILITY CALCULATION
    # ─────────────────────────────────────────────────────────────
    validator.section("3.1 Win Probability (Multi-Factor Model)")

    test_awards = [
        {"id": "ncwit", "name": "NCWIT Aspirations", "category": "STEM", "historical_win_rate": 0.10, "effort_hours": 15, "considers_diversity": True},
        {"id": "cong-app", "name": "Congressional App Challenge", "category": "STEM", "historical_win_rate": 0.15, "effort_hours": 40, "considers_diversity": False},
        {"id": "coca-cola", "name": "Coca-Cola Scholars", "category": "LEADERSHIP", "historical_win_rate": 0.02, "effort_hours": 20, "considers_diversity": True},
        {"id": "regen-sts", "name": "Regeneron STS", "category": "STEM", "historical_win_rate": 0.003, "effort_hours": 100, "considers_diversity": False},
    ]

    print(f"\n  {'Award':<30} {'Base':<8} {'Calc':<8} {'Boost'}")
    print(f"  {'─'*54}")

    probs = {}
    for award in test_awards:
        prob = await agent.calculate_win_probability(profile_enhanced, award)
        base = award['historical_win_rate']
        boost = prob / base if base > 0 else 0
        probs[award['name']] = {"base": base, "calc": prob, "boost": boost}
        print(f"  {award['name']:<30} {base:.1%}     {prob:.1%}     {boost:.1f}x")

    results["probabilities"] = probs

    ncwit = probs.get("NCWIT Aspirations", {}).get("calc", 0)
    validator.check("NCWIT boosted significantly (Huda won this)", ncwit > 0.20, f"Got {ncwit:.0%}")

    all_boosted = all(p.get('boost', 0) > 1.0 for p in probs.values())
    validator.check("All awards boosted above base", all_boosted, "Strong profile")

    # ─────────────────────────────────────────────────────────────
    # 3.2 PORTFOLIO BALANCING
    # ─────────────────────────────────────────────────────────────
    validator.section("3.2 Portfolio Balancing (Likely/Target/Stretch)")

    matches = [
        {"name": "School CS Award", "win_probability": 0.80, "effort_hours": 5},
        {"name": "Regional Tech Prize", "win_probability": 0.60, "effort_hours": 15},
        {"name": "NCWIT Aspirations", "win_probability": ncwit, "effort_hours": 15},
        {"name": "Congressional App", "win_probability": 0.35, "effort_hours": 40},
        {"name": "Coca-Cola Scholars", "win_probability": 0.10, "effort_hours": 20},
        {"name": "Regeneron STS", "win_probability": 0.02, "effort_hours": 100},
    ]

    portfolio = agent.balance_portfolio(matches)
    results["portfolio"] = portfolio

    likely = portfolio.get('likely', [])
    target = portfolio.get('target', [])
    stretch = portfolio.get('stretch', [])

    print(f"\n  📗 Likely (>50%): {len(likely)}")
    for a in likely:
        print(f"     • {a['name']} ({a['win_probability']:.0%})")

    print(f"\n  📙 Target (25-50%): {len(target)}")
    for a in target:
        print(f"     • {a['name']} ({a['win_probability']:.0%})")

    print(f"\n  📕 Stretch (<25%): {len(stretch)}")
    for a in stretch:
        print(f"     • {a['name']} ({a['win_probability']:.0%})")

    print(f"\n  Expected wins: {portfolio.get('expected_wins', 0):.1f}")

    validator.check("Has all 3 categories", all(k in portfolio for k in ['likely', 'target', 'stretch']), "Balanced")
    validator.check("Likely >50%", all(a['win_probability'] > 0.5 for a in likely) if likely else True, ">50%")
    validator.check("Target 25-50%", all(0.25 <= a['win_probability'] <= 0.5 for a in target) if target else True, "25-50%")
    validator.check("Stretch <25%", all(a['win_probability'] < 0.25 for a in stretch) if stretch else True, "<25%")
    validator.check("Expected wins > 0", portfolio.get('expected_wins', 0) > 0, f"Got {portfolio.get('expected_wins', 0):.1f}")

    return results


# =============================================================================
# LEG 4: OPPORTUNITIES AGENT (ECs & Summer Programs)
# =============================================================================

async def test_opportunities_agent(profile: Dict, assessment: Dict, validator: QualityValidator) -> Dict:
    """Test Opportunities Agent - Mile Deep"""

    print("\n" + "═"*60)
    print("  LEG 4: OPPORTUNITIES AGENT")
    print("  Testing: Fit Score, Alerts, Backup Cascades")
    print("═"*60)

    from agents.opportunity import OpportunityAgent
    agent = OpportunityAgent()
    results = {}

    profile_enhanced = profile.copy()
    profile_enhanced["narrative_dna"] = assessment.get("narrative_dna", {}).get("dna", "")

    # ─────────────────────────────────────────────────────────────
    # 4.1 FIT SCORE CALCULATION
    # ─────────────────────────────────────────────────────────────
    validator.section("4.1 Fit Score (Multi-Factor)")

    opportunities = [
        {"id": "rsi", "name": "RSI (MIT)", "type": "research", "focus_area": "STEM", "deadline": "2025-01-15"},
        {"id": "ssp", "name": "Summer Science Program", "type": "research", "focus_area": "STEM", "deadline": "2025-02-01"},
        {"id": "tasp", "name": "TASP (Telluride)", "type": "academic", "focus_area": "HUMANITIES", "deadline": "2025-01-15"},
        {"id": "mostec", "name": "MOSTEC (MIT)", "type": "stem_enrichment", "focus_area": "STEM", "deadline": "2025-02-15"},
        {"id": "boa", "name": "Bank of America Leaders", "type": "leadership", "focus_area": "LEADERSHIP", "deadline": "2025-01-31"},
    ]

    print(f"\n  {'Opportunity':<30} {'Type':<15} {'Focus':<12} {'Fit'}")
    print(f"  {'─'*65}")

    fits = {}
    for opp in opportunities:
        fit = await agent.calculate_fit_score(profile_enhanced, opp)
        fits[opp['name']] = fit
        print(f"  {opp['name']:<30} {opp['type']:<15} {opp['focus_area']:<12} {fit:.0%}")

    results["fit_scores"] = fits

    rsi = fits.get("RSI (MIT)", 0)
    tasp = fits.get("TASP (Telluride)", 0)

    validator.check("RSI high fit for STEM student (>70%)", rsi > 0.7, f"Got {rsi:.0%}")
    validator.check("RSI > TASP (STEM > Humanities)", rsi > tasp, f"RSI {rsi:.0%} vs TASP {tasp:.0%}")
    validator.check("MOSTEC boosted (underrepresented)", fits.get("MOSTEC (MIT)", 0) > 0.7, "URM program")

    # ─────────────────────────────────────────────────────────────
    # 4.2 ADVANCE ALERTS (ACP-006)
    # ─────────────────────────────────────────────────────────────
    validator.section("4.2 Advance Alerts (6-Month Window)")

    print("\n  🔄 Generating deadline alerts...")
    alerts = await agent.send_advance_alerts(profile_enhanced, opportunities)
    results["alerts"] = alerts

    print(f"\n  Alerts: {len(alerts)}")
    for alert in alerts[:3]:
        print(f"\n  🔔 {alert.get('opportunity_name', 'Unknown')}")
        print(f"     Urgency: {alert.get('urgency', '?')}")
        print(f"     Months left: {alert.get('months_remaining', 0)}")
        actions = alert.get('recommended_actions', [])
        print(f"     Actions: {len(actions)}")
        for a in actions[:2]:
            print(f"       • {a[:50]}...")

    validator.check("Generated alerts", len(alerts) > 0, f"Got {len(alerts)}")

    all_have_actions = all(len(a.get('recommended_actions', [])) >= 3 for a in alerts)
    validator.check("Alerts have 3+ actions each", all_have_actions, "Actionable")

    # ─────────────────────────────────────────────────────────────
    # 4.3 BACKUP CASCADES
    # ─────────────────────────────────────────────────────────────
    validator.section("4.3 Backup Cascades (3+ Alternatives)")

    matches = [{"opportunity_id": o['id'], "name": o['name'], "fit_score": fits[o['name']]} for o in opportunities]
    primary = max(matches, key=lambda x: x['fit_score'])

    cascade = agent.create_backup_cascade(primary, matches)
    results["cascade"] = cascade

    print(f"\n  Primary: {cascade.get('primary', {}).get('name', '?')}")
    print(f"  Backups: {len(cascade.get('backups', []))}")
    for b in cascade.get('backups', []):
        print(f"    {b.get('priority', '?')}. {b.get('name', '?')} ({b.get('fit_score', 0):.0%})")
    print(f"  Strategy: {cascade.get('failover_strategy', 'N/A')[:60]}...")

    validator.check("Has 3+ backups", len(cascade.get('backups', [])) >= 3, f"Got {len(cascade.get('backups', []))}")
    validator.check("Has failover strategy", len(cascade.get('failover_strategy', '')) > 20, "Strategy defined")

    return results


# =============================================================================
# LEG 5: EXECUTION AGENT
# =============================================================================

async def test_execution_agent(profile: Dict, gameplan: Dict, validator: QualityValidator) -> Dict:
    """Test Execution Agent - Mile Deep"""

    print("\n" + "═"*60)
    print("  LEG 5: EXECUTION AGENT")
    print("  Testing: Project Scaffolding, EDS")
    print("═"*60)

    from agents.execution import ExecutionAgent
    agent = ExecutionAgent()
    results = {}

    # ─────────────────────────────────────────────────────────────
    # 5.1 PROJECT SCAFFOLDING
    # ─────────────────────────────────────────────────────────────
    validator.section("5.1 Project Scaffolding (Microsteps)")

    project = {
        "name": "AI Ethics Research Paper",
        "type": "research",
        "description": "Research algorithmic bias in college admissions AI",
        "deadline": "2025-03-15"
    }

    print(f"\n  🔄 Scaffolding project: {project['name']}...")

    try:
        scaffold = await agent.scaffold_project(profile.get("id", "test"), project)
        results["scaffold"] = scaffold

        steps = scaffold.get("microsteps", scaffold.get("steps", []))
        print(f"\n  Steps: {len(steps)}")
        print(f"  Est. hours: {scaffold.get('estimated_hours', 'N/A')}")

        for i, step in enumerate(steps[:5], 1):
            title = step.get('title', str(step)) if isinstance(step, dict) else str(step)
            mins = step.get('estimated_minutes', '?') if isinstance(step, dict) else '?'
            print(f"    {i}. {title[:50]}... ({mins} min)")

        validator.check("Generated 15+ microsteps", len(steps) >= 15, f"Got {len(steps)}")

        with_time = [s for s in steps if isinstance(s, dict) and s.get('estimated_minutes')]
        validator.check("Steps have time estimates", len(with_time) >= len(steps) * 0.7, "70%+ have times")

    except Exception as e:
        print(f"\n  ⚠ Scaffolding error: {e}")
        validator.check("Project scaffolding", False, str(e)[:50])

    # ─────────────────────────────────────────────────────────────
    # 5.2 EXECUTION DEBT SCORE
    # ─────────────────────────────────────────────────────────────
    validator.section("5.2 Execution Debt Score (EDS)")

    try:
        eds = await agent.calculate_execution_debt(profile.get("id", "test"))
        results["eds"] = eds

        print(f"\n  EDS: {eds.get('execution_debt_score', 0)}")
        print(f"  Status: {eds.get('status', 'Unknown')}")
        print(f"  Threshold: {eds.get('threshold', 50)}")

        validator.check(
            "EDS has valid status",
            eds.get('status') in ['healthy', 'at_risk', 'critical'],
            f"Got: {eds.get('status')}"
        )
    except Exception as e:
        print(f"\n  ⚠ EDS calculation (expected without DB): {e}")
        # Don't fail - EDS requires database state

    return results


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def run_mile_deep_test():
    """Run the complete mile-deep E2E test"""

    print("\n" + "═"*70)
    print("  IVYQUEST v10.0 - MILE DEEP END-TO-END TEST")
    print("═"*70)
    print(f"\n  Profile: Huda (10th grade, STEM spike, First-gen)")
    print(f"  Target Schools: {', '.join(HUDA_PROFILE['target_schools'][:4])}...")
    print(f"  Spike: AI Education Nonprofit (6,400 students, $23K raised)")
    print(f"  Awards: 5 national (NCWIT, Congressional App, etc.)")

    validator = QualityValidator()

    # Run all legs
    assessment = await test_assessment_agent(HUDA_PROFILE, validator)
    gameplan = await test_gameplan_agent(HUDA_PROFILE, assessment, validator)
    awards = await test_awards_agent(HUDA_PROFILE, assessment, validator)
    opportunities = await test_opportunities_agent(HUDA_PROFILE, assessment, validator)
    execution = await test_execution_agent(HUDA_PROFILE, gameplan, validator)

    # Summary
    all_passed = validator.summary()

    # Data flow visualization
    print("\n" + "═"*60)
    print("  DATA FLOW SUMMARY")
    print("═"*60)

    dna = assessment.get('narrative_dna', {}).get('dna', '')[:35]
    arch = assessment.get('archetype', {}).get('label', 'N/A')

    print(f"""
  ┌────────────────────────────────────────────────────────────┐
  │  ASSESSMENT → DNA: "{dna}..."
  │               Archetype: {arch}
  │               CRI: {assessment.get('cri', 'N/A')}
  └─────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
  ┌────────────────────────────────────────────────────────────┐
  │  GAME PLAN  → Activities: {len(gameplan.get('activities', []))} (≥4 touchpoints)
  │               Seeds: {len(gameplan.get('identity_seeds', []))} planted
  │               Overwhelm: {len(gameplan.get('overwhelmed', []))} total (1.4x)
  └─────────────────────────┬──────────────────────────────────┘
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
  ┌────────────────────────┐   ┌────────────────────────┐
  │  AWARDS                │   │  OPPORTUNITIES         │
  │  Likely: {len(awards.get('portfolio', {}).get('likely', []))}             │   │  Matches: {len(opportunities.get('fit_scores', {}))}            │
  │  Target: {len(awards.get('portfolio', {}).get('target', []))}             │   │  Alerts: {len(opportunities.get('alerts', []))}             │
  │  Stretch: {len(awards.get('portfolio', {}).get('stretch', []))}            │   │  Cascades: Ready        │
  │  Expected: {awards.get('portfolio', {}).get('expected_wins', 0):.1f}         │   └────────────────────────┘
  └────────────────────────┘
               │
               ▼
  ┌────────────────────────────────────────────────────────────┐
  │  EXECUTION → Project scaffolding ready
  │              EDS monitoring active
  └────────────────────────────────────────────────────────────┘
    """)

    return all_passed


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        success = asyncio.run(run_mile_deep_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
