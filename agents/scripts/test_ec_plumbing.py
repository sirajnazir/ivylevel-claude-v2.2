"""
EC Agent Minimal Plumbing Test Script
=====================================

Tests the full integration loop:
1. Sync game plan to projects
2. Check for stalled projects and deadlines
3. Create nudges
4. Verify ExecutionChatAgent tools work

Usage:
    cd agents
    source venv/bin/activate
    python scripts/test_ec_plumbing.py [profile_id]
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

# Test profile ID (use Huda's or pass as arg)
DEFAULT_TEST_PROFILE = "4c4c94f9-a7df-4483-9dc6-7905dda36386"


async def test_gameplan_sync(supabase, profile_id: str):
    """Test syncing game plan to projects."""
    print("\n" + "=" * 60)
    print("TEST 1: GamePlan to Projects Sync")
    print("=" * 60)

    from services.gameplan_sync import sync_gameplan_to_projects, get_synced_projects_count

    # Get existing game plan
    game_plan_result = supabase.table("game_plans").select("*").eq(
        "profile_id", profile_id
    ).order("created_at", desc=True).limit(1).execute()

    if not game_plan_result.data:
        print(f"  [WARN] No game plan found for profile {profile_id}")
        print("  Skipping sync test - generate a game plan first")
        return False

    game_plan = game_plan_result.data[0]
    plan_data = game_plan.get("plan_data") or game_plan

    print(f"  Found game plan: {game_plan.get('id', 'N/A')[:8]}...")
    print(f"  Plan data keys: {list(plan_data.keys())[:5]}...")

    # Sync to projects
    try:
        projects = await sync_gameplan_to_projects(supabase, profile_id, plan_data)
        print(f"  [OK] Synced {len(projects)} projects")

        # Verify count
        count = await get_synced_projects_count(supabase, profile_id)
        print(f"  [OK] Total synced projects in DB: {count}")

        return True
    except Exception as e:
        print(f"  [FAIL] Sync error: {e}")
        return False


async def test_scheduler_checks(supabase, profile_id: str):
    """Test the daily scheduler checks."""
    print("\n" + "=" * 60)
    print("TEST 2: Scheduler Checks (Deadlines, Stalls, Inactivity)")
    print("=" * 60)

    from services.execution_scheduler import (
        _check_deadlines,
        _check_stalled_projects,
        _check_inactivity,
    )

    # Test deadline check
    print("\n  --- Deadline Check ---")
    deadline_nudges = await _check_deadlines(supabase, profile_id)
    print(f"  [OK] Found {len(deadline_nudges)} deadline nudges")
    for nudge in deadline_nudges[:3]:
        print(f"      - {nudge.get('message_draft', 'N/A')[:60]}...")

    # Test stall check
    print("\n  --- Stall Check ---")
    stall_nudges = await _check_stalled_projects(supabase, profile_id)
    print(f"  [OK] Found {len(stall_nudges)} stall nudges")
    for nudge in stall_nudges[:3]:
        print(f"      - {nudge.get('message_draft', 'N/A')[:60]}...")

    # Test inactivity check
    print("\n  --- Inactivity Check ---")
    inactivity_nudge = await _check_inactivity(supabase, profile_id)
    if inactivity_nudge:
        print(f"  [OK] Inactivity nudge: {inactivity_nudge.get('message_draft', 'N/A')[:60]}...")
    else:
        print("  [OK] No inactivity nudge (recent activity)")

    return True


async def test_execution_chat_tools(supabase, profile_id: str):
    """Test ExecutionChatAgent tools."""
    print("\n" + "=" * 60)
    print("TEST 3: ExecutionChatAgent Tools")
    print("=" * 60)

    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()

    # Test get active projects
    print("\n  --- Get Active Projects ---")
    projects = await agent.tool_get_active_projects(profile_id)
    print(f"  [OK] Found {len(projects)} active projects")
    for p in projects[:3]:
        print(f"      - {p.get('name', 'Untitled')[:40]}")

    # Test get upcoming deadlines
    print("\n  --- Get Upcoming Deadlines ---")
    deadlines = await agent.tool_get_upcoming_deadlines(profile_id)
    print(f"  [OK] Found {len(deadlines)} upcoming deadlines")
    for d in deadlines[:3]:
        print(f"      - {d.get('name', 'Untitled')[:30]} ({d.get('days_until')} days)")

    # Test get pending nudges
    print("\n  --- Get Pending Nudges ---")
    nudges = await agent.tool_get_pending_nudges(profile_id)
    print(f"  [OK] Found {len(nudges)} pending nudges")
    for n in nudges[:3]:
        print(f"      - [{n.get('priority')}] {n.get('nudge_type')}")

    # Test detect stalls
    print("\n  --- Detect Stalls ---")
    stalls = await agent.tool_detect_stalls(profile_id)
    print(f"  [OK] Found {len(stalls)} stalled projects")
    for s in stalls[:3]:
        print(f"      - {s.get('title', 'Untitled')[:30]} ({s.get('days_since_activity')} days)")

    # Test calculate EDS
    print("\n  --- Calculate EDS ---")
    eds = await agent.tool_calculate_eds(profile_id)
    print(f"  [OK] EDS Score: {eds.get('eds_score', 0)} ({eds.get('status', 'unknown')})")
    print(f"      Active: {eds.get('active_projects', 0)}, Overdue: {eds.get('overdue_projects', 0)}, Stalled: {eds.get('stalled_projects', 0)}")

    return True


async def test_full_daily_check(supabase):
    """Test the full daily execution check."""
    print("\n" + "=" * 60)
    print("TEST 4: Full Daily Execution Check")
    print("=" * 60)

    from services.execution_scheduler import daily_execution_check

    try:
        results = await daily_execution_check(supabase)
        print(f"  [OK] Daily check complete:")
        print(f"      Profiles checked: {results.get('profiles_checked', 0)}")
        print(f"      Nudges created: {results.get('nudges_created', 0)}")
        print(f"        - Deadline: {results.get('deadline_nudges', 0)}")
        print(f"        - Stall: {results.get('stall_nudges', 0)}")
        print(f"        - Inactivity: {results.get('inactivity_nudges', 0)}")
        if results.get('errors'):
            print(f"      Errors: {len(results['errors'])}")
            for err in results['errors'][:3]:
                print(f"        - {err[:80]}")
        return True
    except Exception as e:
        print(f"  [FAIL] Daily check error: {e}")
        return False


async def verify_database_tables(supabase):
    """Verify required tables exist."""
    print("\n" + "=" * 60)
    print("PRE-CHECK: Database Tables")
    print("=" * 60)

    tables = ["projects", "nudge_queue", "weekly_plans", "project_steps"]
    all_exist = True

    for table in tables:
        try:
            result = supabase.table(table).select("id").limit(1).execute()
            print(f"  [OK] Table '{table}' exists")
        except Exception as e:
            print(f"  [WARN] Table '{table}' may not exist: {e}")
            all_exist = False

    if not all_exist:
        print("\n  Run the migration first:")
        print("  supabase/migrations/039_ec_agent_projects_nudge.sql")

    return all_exist


async def main():
    # Get profile ID from args or use default
    profile_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEST_PROFILE

    print("=" * 60)
    print("EC Agent Minimal Plumbing Test")
    print("=" * 60)
    print(f"Profile ID: {profile_id}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Get Supabase client
    from tools.database import get_supabase_client
    supabase = get_supabase_client()

    # Verify tables exist
    tables_ok = await verify_database_tables(supabase)
    if not tables_ok:
        print("\n[ABORT] Missing required tables. Run migration first.")
        return

    # Run tests
    results = []

    results.append(("GamePlan Sync", await test_gameplan_sync(supabase, profile_id)))
    results.append(("Scheduler Checks", await test_scheduler_checks(supabase, profile_id)))
    results.append(("EC Chat Tools", await test_execution_chat_tools(supabase, profile_id)))
    results.append(("Full Daily Check", await test_full_daily_check(supabase)))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = 0
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
        if result:
            passed += 1

    print(f"\n  Total: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n  EC Agent plumbing is working!")
    else:
        print("\n  Some tests failed. Check output above.")


if __name__ == "__main__":
    asyncio.run(main())
