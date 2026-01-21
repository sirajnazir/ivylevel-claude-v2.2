"""
Sync game plan items to projects table.
Extracts actionable items from game_plans.plan_data and creates project records.

This module provides the bridge between GamePlanAgent's strategic planning
and ExecutionChatAgent's execution tracking.

Pattern: When a game plan is generated, this syncs actionable items
to the projects table so the Execution Agent has concrete work to track.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


async def sync_gameplan_to_projects(
    supabase_client,
    profile_id: str,
    plan_data: dict,
) -> List[Dict[str, Any]]:
    """
    Extract actionable items from game_plan.plan_data and create project records.

    This function is the bridge between strategy (GamePlan) and execution (EC Agent).
    It extracts:
    - Awards as projects
    - Summer programs as projects
    - EC goals/activities as projects
    - Essays as projects
    - Academic goals (SAT, etc.) as projects

    Args:
        supabase_client: Supabase client instance
        profile_id: Student's profile UUID
        plan_data: The plan_data dict from game_plans table

    Returns:
        List of created/updated project records

    Plan data structure (typical):
    {
        "phases": [...],
        "academics": {"sat_target": 1550, "ap_courses": [...]},
        "extracurriculars": [
            {"name": "Film Club", "goals": ["Scale to 50 members"], "timeline": "Fall 2024"}
        ],
        "awards": {
            "portfolio": {
                "reach": [...], "target": [...], "safety": [...]
            },
            "top_recommendations": [...]
        },
        "programs": {
            "top_recommendations": [...]
        },
        "essays": [...]
    }
    """
    if not plan_data:
        logger.warning(f"No plan_data provided for profile {profile_id}")
        return []

    # Detailed logging for debugging
    logger.info(f"[GamePlanSync] Starting sync for profile {profile_id}")
    logger.info(f"[GamePlanSync] Plan data keys: {list(plan_data.keys()) if isinstance(plan_data, dict) else 'not a dict'}")

    # Log key arrays that should contain projects
    quick_wins_count = len(plan_data.get("quickWins", []))
    long_term_count = len(plan_data.get("longTermGoals", []))
    phases_count = len(plan_data.get("phases", []))
    logger.info(f"[GamePlanSync] Found: quickWins={quick_wins_count}, longTermGoals={long_term_count}, phases={phases_count}")

    projects_to_create = []
    timestamp = datetime.now().isoformat()

    # Helper function to create project dict with correct column names
    # Note: Existing projects table uses 'title' not 'name', 'target_end_date' not 'deadline'
    def make_project(title: str, category: str, deadline: str = None, description: str = None, metadata: dict = None):
        return {
            "profile_id": profile_id,
            "title": title,  # projects table uses 'title' not 'name'
            "description": description or f"{category}: {title}",
            "category": category,
            "target_end_date": _parse_deadline(deadline) if deadline else None,  # Use target_end_date
            "status": "active",
        }

    # =====================================================
    # Extract Awards as Projects
    # =====================================================
    awards_data = plan_data.get("awards", {})

    # Handle both nested and flat award structures
    if isinstance(awards_data, dict):
        portfolio = awards_data.get("portfolio", {})
        top_awards = awards_data.get("top_recommendations", [])

        # Combine from portfolio categories
        all_awards = (
            portfolio.get("reach", []) +
            portfolio.get("target", []) +
            portfolio.get("safety", []) +
            portfolio.get("likely", []) +
            portfolio.get("stretch", []) +
            top_awards
        )
    elif isinstance(awards_data, list):
        all_awards = awards_data
    else:
        all_awards = []

    for award in all_awards:
        if not isinstance(award, dict):
            continue
        award_name = award.get("name", award.get("title", "Unnamed Award"))
        projects_to_create.append(make_project(
            title=award_name,
            category="award",
            deadline=award.get("deadline"),
            description=award.get("description", f"Award application: {award_name}"),
        ))

    # =====================================================
    # Extract Summer Programs as Projects
    # =====================================================
    programs_data = plan_data.get("programs", {})

    if isinstance(programs_data, dict):
        all_programs = programs_data.get("top_recommendations", [])
    elif isinstance(programs_data, list):
        all_programs = programs_data
    else:
        all_programs = []

    # Also check for summer_programs key
    all_programs += plan_data.get("summer_programs", [])

    for program in all_programs:
        if not isinstance(program, dict):
            continue
        program_name = program.get("name", program.get("title", "Unnamed Program"))
        projects_to_create.append(make_project(
            title=program_name,
            category="summer_program",
            deadline=program.get("deadline") or program.get("application_deadline"),
            description=program.get("description", f"Summer program application: {program_name}"),
        ))

    # =====================================================
    # Extract ECs with Specific Goals as Projects
    # =====================================================
    ec_data = plan_data.get("extracurriculars", [])
    if isinstance(ec_data, list):
        for ec in ec_data:
            if not isinstance(ec, dict):
                continue

            ec_name = ec.get("name", ec.get("title", "Unnamed EC"))
            goals = ec.get("goals", [])

            if goals and isinstance(goals, list):
                # Create a project for each goal
                for goal in goals:
                    goal_text = goal if isinstance(goal, str) else goal.get("text", str(goal))
                    projects_to_create.append(make_project(
                        title=f"{ec_name}: {goal_text}",
                        category="ec_goal",
                        deadline=ec.get("timeline"),
                        description=f"EC goal for {ec_name}: {goal_text}",
                    ))
            else:
                # EC without specific goals - still track it
                projects_to_create.append(make_project(
                    title=ec_name,
                    category="ec",
                    deadline=ec.get("timeline"),
                    description=f"Extracurricular activity: {ec_name}",
                ))

    # Also handle ec_generation data if present
    ec_gen = plan_data.get("ec_generation", {})
    if isinstance(ec_gen, dict):
        recommended_activities = ec_gen.get("recommended_activities", [])
        for activity in recommended_activities:
            if not isinstance(activity, dict):
                continue
            activity_name = activity.get("title") or activity.get("name", "New Activity")
            projects_to_create.append(make_project(
                title=activity_name,
                category="ec_goal",
                deadline=None,
                description=activity.get("description", f"Recommended activity: {activity_name}"),
            ))

    # =====================================================
    # Extract Essays as Projects (if defined)
    # =====================================================
    essays = plan_data.get("essays", [])
    if isinstance(essays, list):
        for essay in essays:
            if not isinstance(essay, dict):
                continue
            essay_name = essay.get("name", essay.get("type", essay.get("title", "Essay")))
            projects_to_create.append(make_project(
                title=essay_name,
                category="essay",
                deadline=essay.get("deadline"),
                description=essay.get("prompt", f"Essay: {essay_name}"),
            ))

    # =====================================================
    # Extract Academic Goals as Projects
    # =====================================================
    academics = plan_data.get("academics", {})
    if isinstance(academics, dict):
        # SAT target
        sat_target = academics.get("sat_target")
        if sat_target:
            projects_to_create.append(make_project(
                title=f"SAT Target: {sat_target}",
                category="academic",
                deadline=academics.get("test_date"),
                description=f"Achieve SAT score of {sat_target}",
            ))

        # ACT target
        act_target = academics.get("act_target")
        if act_target:
            projects_to_create.append(make_project(
                title=f"ACT Target: {act_target}",
                category="academic",
                deadline=academics.get("test_date"),
                description=f"Achieve ACT score of {act_target}",
            ))

    # =====================================================
    # Extract Phase Activities as Projects
    # =====================================================
    phases = plan_data.get("phases", [])
    if isinstance(phases, list):
        for phase in phases:
            if not isinstance(phase, dict):
                continue
            phase_activities = phase.get("activities", [])
            for activity in phase_activities:
                if not isinstance(activity, dict):
                    continue
                # Only create if not already covered by above categories
                activity_type = activity.get("type", "")
                if activity_type not in ["award", "program", "ec", "essay"]:
                    activity_name = activity.get("name", activity.get("action", "Phase Activity"))
                    phase_name = phase.get("name", "")
                    projects_to_create.append(make_project(
                        title=activity_name,
                        category=activity_type or "phase_task",
                        deadline=activity.get("deadline"),
                        description=f"{phase_name}: {activity_name}" if phase_name else activity_name,
                    ))

    # =====================================================
    # Extract Quick Wins from Frontend Game Plan (fallback)
    # =====================================================
    quick_wins = plan_data.get("quickWins", [])
    logger.info(f"[GamePlanSync] Processing {len(quick_wins) if isinstance(quick_wins, list) else 0} quickWins")
    if isinstance(quick_wins, list):
        for i, qw in enumerate(quick_wins):
            if not isinstance(qw, dict):
                logger.warning(f"[GamePlanSync] quickWins[{i}] is not a dict: {type(qw)}")
                continue
            qw_title = qw.get("title", "Quick Win")
            qw_category = qw.get("category", "quick_win")
            logger.info(f"[GamePlanSync] Adding quickWin: {qw_title}")
            projects_to_create.append(make_project(
                title=qw_title,
                category=qw_category,
                deadline=qw.get("deadline"),
                description=qw.get("description", f"Quick win: {qw_title}"),
            ))

    # =====================================================
    # Extract Long Term Goals from Frontend Game Plan (fallback)
    # =====================================================
    long_term_goals = plan_data.get("longTermGoals", [])
    logger.info(f"[GamePlanSync] Processing {len(long_term_goals) if isinstance(long_term_goals, list) else 0} longTermGoals")
    if isinstance(long_term_goals, list):
        for i, ltg in enumerate(long_term_goals):
            if not isinstance(ltg, dict):
                logger.warning(f"[GamePlanSync] longTermGoals[{i}] is not a dict: {type(ltg)}")
                continue
            ltg_title = ltg.get("title", "Long Term Goal")
            ltg_category = ltg.get("category", "long_term")
            logger.info(f"[GamePlanSync] Adding longTermGoal: {ltg_title}")
            projects_to_create.append(make_project(
                title=ltg_title,
                category=ltg_category,
                deadline=ltg.get("deadline"),
                description=ltg.get("description", f"Long term goal: {ltg_title}"),
            ))

    # =====================================================
    # Deduplicate and Upsert
    # =====================================================
    if not projects_to_create:
        logger.warning(f"No projects extracted from game plan for profile {profile_id}")
        return []

    # Deduplicate by title
    seen_titles = set()
    unique_projects = []
    for project in projects_to_create:
        title = project.get("title", "")
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_projects.append(project)

    logger.info(f"Extracted {len(unique_projects)} unique projects from game plan for profile {profile_id}")

    # Upsert to projects table (avoid duplicates)
    created = []
    for project in unique_projects:
        try:
            # Check if project already exists by title
            existing = supabase_client.table("projects").select("id").eq(
                "profile_id", profile_id
            ).eq("title", project["title"]).execute()

            if existing.data:
                # Update existing
                result = supabase_client.table("projects").update({
                    "target_end_date": project.get("target_end_date"),
                    "description": project.get("description"),
                    "updated_at": timestamp,
                }).eq("id", existing.data[0]["id"]).execute()
                if result.data:
                    logger.debug(f"Updated existing project: {project['title']}")
                    created.append(result.data[0])
            else:
                # Insert new
                result = supabase_client.table("projects").insert(project).execute()
                if result.data:
                    logger.info(f"Created new project: {project['title']}")
                    created.append(result.data[0])

        except Exception as e:
            logger.error(f"Failed to upsert project '{project.get('title', 'unknown')}': {e}")

    logger.info(f"Synced {len(created)} projects for profile {profile_id}")
    return created


def _parse_deadline(deadline_str: Optional[str]) -> Optional[str]:
    """
    Parse various deadline formats to ISO timestamp.

    Handles:
    - ISO format strings
    - Common date formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
    - Natural language ("Fall 2024", "March 2025")
    - None/empty values

    Returns:
        ISO format timestamp string or None
    """
    if not deadline_str:
        return None

    # If already ISO format, return as-is
    try:
        if "T" in str(deadline_str):
            # Already ISO format
            return str(deadline_str)
    except Exception:
        pass

    # Try dateutil parser for flexible parsing
    try:
        from dateutil import parser
        parsed = parser.parse(str(deadline_str), fuzzy=True)
        return parsed.isoformat()
    except Exception:
        pass

    # Handle season-based dates
    try:
        deadline_lower = str(deadline_str).lower()
        current_year = datetime.now().year

        # Extract year if present
        import re
        year_match = re.search(r'20\d{2}', deadline_lower)
        year = int(year_match.group()) if year_match else current_year

        if "spring" in deadline_lower:
            return datetime(year, 4, 1).isoformat()
        elif "summer" in deadline_lower:
            return datetime(year, 7, 1).isoformat()
        elif "fall" in deadline_lower:
            return datetime(year, 10, 1).isoformat()
        elif "winter" in deadline_lower:
            return datetime(year, 1, 1).isoformat()
    except Exception:
        pass

    # Return None if parsing fails
    logger.debug(f"Could not parse deadline: {deadline_str}")
    return None


async def get_synced_projects_count(supabase_client, profile_id: str) -> int:
    """
    Get count of projects synced from game plan for a profile.

    Useful for verification after sync.
    """
    try:
        result = supabase_client.table("projects").select(
            "id", count="exact"
        ).eq("profile_id", profile_id).execute()
        return result.count or 0
    except Exception as e:
        logger.error(f"Failed to count synced projects for {profile_id}: {e}")
        return 0
