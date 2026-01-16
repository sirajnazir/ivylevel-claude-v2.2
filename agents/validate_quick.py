#!/usr/bin/env python3
"""
Quick Validation Script for Agentic ReAct v5.0
==============================================

Simpler validation that checks the 3 critical behaviors.

Usage:
    cd /path/to/ivyquest/agents
    python validate_quick.py
"""

import asyncio
import sys
import os

# Add agents directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# =============================================================================
# MINIMAL TEST PROFILE
# =============================================================================

TEST_PROFILE = {
    "profile_id": "test-validation",
    "name": "Test Student",
    "grade": 11,
    "profile_data": {
        "activities": [
            {"name": "Robotics Club", "role": "Founder", "level": "state", "years": 3,
             "hours_per_week": 10, "weeks_per_year": 40, "description": "Founded robotics program"},
            {"name": "AI Research", "role": "Research Assistant", "level": "national", "years": 1,
             "hours_per_week": 15, "weeks_per_year": 12, "description": "ML research at Stanford"},
            {"name": "Code for Good", "role": "Founder", "level": "regional", "years": 2,
             "hours_per_week": 6, "weeks_per_year": 35, "description": "Free coding for underserved youth"},
        ],
        "passion": {
            "spike_category": "STEM",
            "brag_text": "Democratizing AI education",
        },
    },
    "intended_major": "Computer Science",
}


async def main():
    print("=" * 60)
    print("AGENTIC REACT v5.0 - QUICK VALIDATION")
    print("=" * 60)

    # Import components
    print("\n1. Importing components...")

    try:
        from agents.extracurriculars import ExtracurricularsAgent
        from agents.core.react_wrapper import ReActWrapper
        from config import FEATURE_FLAGS
        print("   ✓ Imports successful")
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        return False

    # Enable ReAct
    FEATURE_FLAGS["enable_react"] = True
    FEATURE_FLAGS["react_verbose_logging"] = True
    FEATURE_FLAGS["react_ab_test_enabled"] = False  # Force treatment group

    # Create components
    print("\n2. Creating engine...")

    agent = ExtracurricularsAgent()
    engine = ReActWrapper(
        agent=agent,
        max_cycles=3,
        min_confidence=0.70,
        enable_agentic=True,
        enable_logging=True,
    )
    print("   ✓ Engine created")

    # Mock the profile fetch to return our test profile
    original_get_profile = agent._get_profile
    async def mock_get_profile(profile_id):
        if profile_id == "test-validation":
            return TEST_PROFILE
        return await original_get_profile(profile_id)
    agent._get_profile = mock_get_profile

    # Run test
    print("\n3. Running agentic ReAct cycle...")
    print("-" * 60)

    result = await engine.process("test-validation", profile_data=TEST_PROFILE)

    print("-" * 60)

    # Validate results
    print("\n4. Validating results...")

    # Extract data from result
    react_meta = result.get("_react", {})
    trajectory = react_meta.get("improvement_trajectory", [])
    cycles = react_meta.get("cycles_executed", len(trajectory))

    identity = result.get("identity_synthesis", {})

    # Check 1: Improvement
    print(f"\n   TRAJECTORY: {' → '.join([f'{s:.0f}' for s in trajectory])}")

    if len(trajectory) >= 2:
        improvement = trajectory[-1] - trajectory[0]
        print(f"   IMPROVEMENT: {improvement:+.0f} points")
        check1 = improvement > 0
    elif len(trajectory) == 1:
        improvement = 0
        check1 = trajectory[0] >= 70  # Passed on first try
        print(f"   First cycle quality: {trajectory[0]:.0f} (passed immediately)")
    else:
        improvement = 0
        check1 = False

    # Check 2: Archetype confidence
    confidence = identity.get("archetype_confidence", 0)
    print(f"   ARCHETYPE: {identity.get('archetype', 'N/A')}")
    print(f"   ARCHETYPE CONFIDENCE: {confidence:.2f}")
    check2 = confidence >= 0.5

    # Check 3: Spike specificity
    spike = identity.get("spike", "")
    generic = ["exploring", "diverse", "emerging", "various", "general"]
    is_specific = not any(g in spike.lower() for g in generic)
    print(f"   SPIKE: {spike[:80]}{'...' if len(spike) > 80 else ''}")
    print(f"   SPIKE SPECIFIC: {is_specific}")
    check3 = is_specific and len(spike) > 10

    # Check 4: Unique pillars
    pillars = identity.get("pillars", [])
    unique = len(set(str(p).lower() for p in pillars))
    print(f"   PILLARS: {pillars}")
    print(f"   UNIQUE PILLARS: {unique}")
    check4 = unique >= 3

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    all_passed = True

    if len(trajectory) >= 2:
        print(f"\n   {'✓' if check1 else '✗'} Improvement trajectory: {improvement:+.0f} (expected: >0)")
    else:
        print(f"\n   {'✓' if check1 else '✗'} Single cycle quality: {trajectory[0] if trajectory else 0:.0f} (expected: ≥70)")
    if not check1:
        all_passed = False
        print("      → FIX: Check is_correction_cycle pattern in extracurriculars.py")

    print(f"   {'✓' if check2 else '✗'} Archetype confidence: {confidence:.2f} (expected: ≥0.5)")
    if not check2:
        all_passed = False
        print("      → FIX: Check _apply_archetype_hints() confidence boosts")

    print(f"   {'✓' if check3 else '✗'} Spike specificity: {is_specific} (expected: True)")
    if not check3:
        all_passed = False
        print("      → FIX: Check _apply_spike_hints() correction logic")

    print(f"   {'✓' if check4 else '✗'} Unique pillars: {unique} (expected: ≥3)")
    if not check4:
        all_passed = False
        print("      → FIX: Check pillar deduplication in correction cycles")

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Integration working correctly!")
    else:
        print("✗ SOME CHECKS FAILED - See fixes above")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
