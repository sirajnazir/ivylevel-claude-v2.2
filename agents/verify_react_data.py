#!/usr/bin/env python3
"""
Verify ReAct Data Structure
============================

This script checks what fields actually exist in the _react metadata
to verify if the frontend will receive the expected data.
"""

import asyncio
import sys
import os

# Add agents directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test profile
TEST_PROFILE = {
    "profile_id": "test-verify",
    "name": "Test Student",
    "grade": 11,
    "profile_data": {
        "activities": [
            {"name": "Robotics Club", "role": "Founder", "level": "state", "years": 3,
             "hours_per_week": 10, "weeks_per_year": 40, "description": "Founded robotics program"},
            {"name": "AI Research", "role": "Research Assistant", "level": "national", "years": 1,
             "hours_per_week": 15, "weeks_per_year": 12, "description": "ML research at Stanford"},
        ],
        "passion": {
            "spike_category": "STEM",
            "brag_text": "Democratizing AI education",
        },
    },
    "intended_major": "Computer Science",
}


async def main():
    print("=" * 70)
    print("REACT DATA STRUCTURE VERIFICATION")
    print("=" * 70)

    # Step 1: Import components
    print("\n1. Importing components...")
    try:
        from agents.extracurriculars import ExtracurricularsAgent
        from agents.core.react_wrapper import ReActWrapper
        from config import FEATURE_FLAGS
        print("   ✓ Imports successful")
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        return

    # Step 2: Enable agentic mode
    FEATURE_FLAGS["enable_react"] = True
    FEATURE_FLAGS["react_verbose_logging"] = True
    FEATURE_FLAGS["react_ab_test_enabled"] = False
    FEATURE_FLAGS["enable_agentic"] = True
    print("\n2. Feature flags set (enable_agentic=True)")

    # Step 3: Create engine
    print("\n3. Creating ReAct engine...")
    agent = ExtracurricularsAgent()
    engine = ReActWrapper(
        agent=agent,
        max_cycles=2,  # Limit to 2 cycles for faster testing
        min_confidence=0.70,
        enable_agentic=True,  # Critical: must be True for full data
        enable_logging=True,
    )
    print(f"   ✓ Engine created (enable_agentic={engine.enable_agentic})")
    print(f"   - Has reasoner: {engine._reasoner is not None}")

    # Step 4: Mock profile fetch
    original_get_profile = agent._get_profile
    async def mock_get_profile(profile_id):
        if profile_id == "test-verify":
            return TEST_PROFILE
        return await original_get_profile(profile_id)
    agent._get_profile = mock_get_profile

    # Step 5: Execute
    print("\n4. Executing ReAct cycle...")
    print("-" * 70)

    result = await engine.process("test-verify", profile_data=TEST_PROFILE)

    print("-" * 70)

    # Step 6: Analyze the _react data
    print("\n5. REACT DATA STRUCTURE ANALYSIS")
    print("=" * 70)

    react_data = result.get("_react", {})

    if not react_data:
        print("   ✗ ERROR: No _react data found!")
        return

    print(f"\nTop-level keys: {list(react_data.keys())}")
    print(f"Version: {react_data.get('version', 'N/A')}")
    print(f"Agentic enabled: {react_data.get('agentic_enabled', 'N/A')}")
    print(f"Cycles executed: {react_data.get('cycles_executed', 0)}")
    print(f"Improvement trajectory: {react_data.get('improvement_trajectory', [])}")

    cycle_summary = react_data.get("cycle_summary", [])
    if not cycle_summary:
        print("\n   ✗ ERROR: No cycle_summary found!")
        return

    print(f"\nAnalyzing {len(cycle_summary)} cycles...")

    issues = []

    for i, cycle in enumerate(cycle_summary):
        print(f"\n--- Cycle {i + 1} ---")
        print(f"Cycle keys: {list(cycle.keys())}")

        # THINK phase
        think = cycle.get("think", {})
        print(f"\nTHINK keys: {list(think.keys())}")

        has_reasoning = bool(think.get("reasoning"))
        has_planned_actions = bool(think.get("planned_actions"))
        has_focus_areas = bool(think.get("focus_areas"))
        has_gap_analysis = bool(think.get("gap_analysis"))
        has_tools_selected = bool(think.get("tools_selected"))

        print(f"  - reasoning: {'✓ Present' if has_reasoning else '✗ MISSING/EMPTY'}")
        print(f"  - planned_actions: {'✓ Present' if has_planned_actions else '○ Empty list (OK if non-agentic)'}")
        print(f"  - focus_areas: {'✓ Present' if has_focus_areas else '○ Empty list (OK if non-agentic)'}")
        print(f"  - gap_analysis: {'✓ Present' if has_gap_analysis else '○ Empty dict (OK if non-agentic)'}")
        print(f"  - tools_selected: {'✓ Present' if has_tools_selected else '○ Empty list (OK if non-agentic)'}")

        if has_reasoning:
            print(f"  - reasoning preview: \"{str(think.get('reasoning', ''))[:80]}...\"")

        # ACT phase
        act = cycle.get("act", {})
        print(f"\nACT keys: {list(act.keys())}")
        print(f"  - action: {act.get('action', 'MISSING')}")
        print(f"  - tools_executed: {len(act.get('tools_executed', []))} tools")
        print(f"  - hints_applied: {act.get('hints_applied', 'MISSING')}")

        # OBSERVE phase
        observe = cycle.get("observe", {})
        print(f"\nOBSERVE keys: {list(observe.keys())}")
        print(f"  - quality_score: {observe.get('quality_score', 'MISSING')}")
        print(f"  - voice_score: {observe.get('voice_score', 'MISSING')}")
        print(f"  - golden_similarity: {observe.get('golden_similarity', 'MISSING')}")
        print(f"  - passed: {observe.get('passed', 'MISSING')}")
        print(f"  - issues_found: {observe.get('issues_found', 'MISSING')}")
        print(f"  - strengths_found: {observe.get('strengths_found', 'MISSING')}")

        # LEARN phase
        learn = cycle.get("learn", {})
        print(f"\nLEARN keys: {list(learn.keys())}")
        print(f"  - reasoning: {'✓ Present' if learn.get('reasoning') else '○ Empty string (OK)'}")
        print(f"  - what_worked: {learn.get('what_worked', 'MISSING')}")
        print(f"  - what_failed: {learn.get('what_failed', 'MISSING')}")
        print(f"  - quality_delta: {learn.get('quality_delta', 'MISSING')}")
        print(f"  - corrections_to_apply: {learn.get('corrections_to_apply', 'MISSING')}")
        print(f"  - should_continue: {learn.get('should_continue', 'MISSING')}")

        # Track issues
        if not think.get("tools_selected"):
            issues.append(f"Cycle {i+1}: tools_selected is empty")
        if not observe.get("issues_found") and observe.get("quality_score", 100) < 70:
            issues.append(f"Cycle {i+1}: issues_found is empty but quality < 70")

    # Check input_data_flow
    data_flow = react_data.get("input_data_flow", {})
    print(f"\n\nINPUT_DATA_FLOW: {list(data_flow.keys()) if data_flow else 'MISSING'}")
    if data_flow:
        print(f"  - from_profile: {data_flow.get('from_profile', 'MISSING')}")
        print(f"  - to_downstream_agents: {data_flow.get('to_downstream_agents', 'MISSING')}")

    # Final verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    if issues:
        print("\n⚠️  POTENTIAL ISSUES (may show empty sections in frontend):")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✓ All critical fields are present")

    # Check if agentic data is populated
    think_first = cycle_summary[0].get("think", {}) if cycle_summary else {}
    if think_first.get("planned_actions") or think_first.get("focus_areas") or think_first.get("gap_analysis"):
        print("\n✓ AGENTIC DATA IS POPULATED - Full visualization will work")
    else:
        print("\n⚠️  AGENTIC DATA IS EMPTY - May be running in non-agentic mode")
        print("   Check if enable_agentic=True and _reasoner is initialized")
        print(f"   Current: enable_agentic={engine.enable_agentic}, _reasoner={engine._reasoner is not None}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
