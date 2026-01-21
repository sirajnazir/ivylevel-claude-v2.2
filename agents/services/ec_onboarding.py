"""
EC Agent Onboarding - Proactive First Session Setup
====================================================

Triggered when a new student's game plan is generated.
Sets up the first coaching session automatically.

Flow:
1. Game Plan Generated →
2. Sync to Projects →
3. Create First Session Agenda →
4. Queue Proactive Welcome Message →
5. Student sees "Your coach is ready" notification

This replaces the passive "empty dashboard" with an active
"Here's your plan, let's get started" experience.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# First session structure based on Jenny's Week 1-3 patterns
FIRST_SESSION_AGENDA = {
    "title": "Welcome to Your Coaching Journey",
    "duration_minutes": 30,
    "sections": [
        {
            "name": "Game Plan Overview",
            "duration": 5,
            "description": "Walk through your personalized game plan and key milestones",
            "talking_points": [
                "Your spike and narrative positioning",
                "Key outcomes we're targeting",
                "Timeline and major deadlines"
            ]
        },
        {
            "name": "168-Hour Framework",
            "duration": 10,
            "description": "Map out how you'll allocate your time each week",
            "talking_points": [
                "Current time allocation audit",
                "Identify time leaks and inefficiencies",
                "Design your ideal weekly schedule",
                "Balance: school, ECs, test prep, rest"
            ]
        },
        {
            "name": "Priority Projects",
            "duration": 10,
            "description": "Identify your P0 priorities for the next 2 weeks",
            "talking_points": [
                "What's the ONE thing that matters most right now?",
                "Upcoming deadlines to be aware of",
                "Quick wins we can get this week"
            ]
        },
        {
            "name": "Working Style & Support",
            "duration": 5,
            "description": "Understand how you work best so I can support you effectively",
            "talking_points": [
                "When do you do your best work?",
                "What motivates you? What blocks you?",
                "How often do you want to check in?"
            ]
        }
    ]
}


async def trigger_ec_onboarding(
    supabase_client,
    profile_id: str,
    plan_data: Dict[str, Any],
    profile_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Trigger EC Agent onboarding when game plan is generated.

    This is the main entry point called after GamePlanAgent completes.

    Args:
        supabase_client: Supabase client
        profile_id: Student's profile UUID
        plan_data: The generated game plan data
        profile_data: Optional profile data (will fetch if not provided)

    Returns:
        Summary of onboarding setup
    """
    results = {
        "profile_id": profile_id,
        "projects_created": 0,
        "welcome_nudge_created": False,
        "first_session_agenda": None,
        "errors": []
    }

    try:
        # Get profile data if not provided
        if not profile_data:
            try:
                # Use .execute() instead of .maybeSingle() for sync client compatibility
                profile_result = supabase_client.table("profiles").select(
                    "first_name, last_name, grade, archetype, spike"
                ).eq("id", profile_id).limit(1).execute()
                profile_data = profile_result.data[0] if profile_result.data else {}
            except Exception as profile_err:
                logger.warning(f"Could not fetch profile for {profile_id}: {profile_err}")
                profile_data = {}

        # If no profile, try to get name from assessment
        if not profile_data.get("first_name"):
            try:
                assessment = supabase_client.table("assessments").select(
                    "profile_data"
                ).eq("user_id", profile_id).order("created_at", desc=True).limit(1).execute()
                if assessment.data:
                    assessment_profile = assessment.data[0].get("profile_data", {})
                    identity = assessment_profile.get("identity", {})
                    profile_data["first_name"] = identity.get("name", "").split()[0] if identity.get("name") else "there"
            except Exception:
                pass

        student_name = profile_data.get("first_name", "there")

        # Step 1: Sync game plan to projects
        from services.gameplan_sync import sync_gameplan_to_projects
        projects = await sync_gameplan_to_projects(supabase_client, profile_id, plan_data)
        results["projects_created"] = len(projects)
        logger.info(f"EC Onboarding: Created {len(projects)} projects for {profile_id}")

        # Step 2: Build first session agenda with personalization
        first_session = _build_first_session_agenda(
            profile_data=profile_data,
            plan_data=plan_data,
            projects=projects
        )
        results["first_session_agenda"] = first_session

        # Step 3: Create welcome nudge with proactive message
        welcome_message = _generate_welcome_message(
            student_name=student_name,
            projects=projects,
            plan_data=plan_data
        )

        try:
            supabase_client.table("nudge_queue").insert({
                "profile_id": profile_id,
                "nudge_type": "welcome_onboarding",
                "project_id": None,
                "priority": "high",
                "message_draft": welcome_message,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            }).execute()
            results["welcome_nudge_created"] = True
            logger.info(f"EC Onboarding: Created welcome nudge for {profile_id}")
        except Exception as e:
            results["errors"].append(f"Welcome nudge creation failed: {e}")

        # Step 4: Create proactive conversation entry (so it shows in chat)
        try:
            supabase_client.table("conversations").insert({
                "profile_id": profile_id,
                "agent_type": "execution",
                "role": "assistant",
                "content": welcome_message,
                "is_proactive": True,
                "context_type": "onboarding",
                "created_at": datetime.now().isoformat(),
            }).execute()
            logger.info(f"EC Onboarding: Created proactive conversation for {profile_id}")
        except Exception as e:
            # Non-critical - might fail if conversations table has different schema
            logger.warning(f"Could not create proactive conversation: {e}")

        logger.info(f"EC Onboarding complete for {profile_id}: {results}")

    except Exception as e:
        logger.error(f"EC Onboarding failed for {profile_id}: {e}")
        results["errors"].append(str(e))

    return results


def _build_first_session_agenda(
    profile_data: Dict[str, Any],
    plan_data: Dict[str, Any],
    projects: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Build personalized first session agenda based on student's game plan.
    """
    student_name = profile_data.get("first_name", "Student")
    archetype = profile_data.get("archetype", "SCHOLAR")
    spike = profile_data.get("spike", "")
    grade = profile_data.get("grade", 11)

    # Count project types
    project_categories = {}
    upcoming_deadlines = []

    for project in projects:
        cat = project.get("category", "other")
        project_categories[cat] = project_categories.get(cat, 0) + 1

        deadline = project.get("target_end_date")
        if deadline:
            upcoming_deadlines.append({
                "title": project.get("title", "Unnamed"),
                "deadline": deadline,
                "category": cat
            })

    # Sort deadlines
    upcoming_deadlines.sort(key=lambda x: x["deadline"] or "9999")

    # Build personalized agenda
    agenda = {
        **FIRST_SESSION_AGENDA,
        "personalization": {
            "student_name": student_name,
            "archetype": archetype,
            "spike": spike,
            "grade": grade,
            "total_projects": len(projects),
            "project_breakdown": project_categories,
            "nearest_deadlines": upcoming_deadlines[:3],  # Top 3 soonest
        },
        "recommended_focus": _determine_initial_focus(
            archetype=archetype,
            projects=projects,
            grade=grade
        )
    }

    return agenda


def _determine_initial_focus(
    archetype: str,
    projects: List[Dict[str, Any]],
    grade: int
) -> Dict[str, Any]:
    """
    Determine what to focus on first based on archetype and situation.
    """
    # Find nearest deadline
    nearest_deadline = None
    nearest_project = None
    now = datetime.now()

    for project in projects:
        deadline_str = project.get("target_end_date")
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str.replace("Z", "").replace("+00:00", ""))
                days_until = (deadline - now).days
                if days_until > 0 and (nearest_deadline is None or days_until < nearest_deadline):
                    nearest_deadline = days_until
                    nearest_project = project
            except:
                pass

    focus = {
        "immediate_priority": None,
        "reason": "",
        "suggested_first_action": ""
    }

    # If deadline within 14 days, that's the focus
    if nearest_deadline and nearest_deadline <= 14:
        focus["immediate_priority"] = nearest_project.get("title")
        focus["reason"] = f"Due in {nearest_deadline} days"
        focus["suggested_first_action"] = f"Let's map out the steps to complete {nearest_project.get('title')} and create a timeline"

    # Otherwise, focus based on archetype
    elif archetype == "SCHOLAR":
        focus["immediate_priority"] = "Academic Foundation"
        focus["reason"] = "Scholars thrive when academics are solid"
        focus["suggested_first_action"] = "Let's review your course load and test prep timeline"

    elif archetype == "BUILDER":
        focus["immediate_priority"] = "EC Impact Projects"
        focus["reason"] = "Builders need tangible projects to drive"
        focus["suggested_first_action"] = "Let's identify your highest-impact EC and set scaling goals"

    elif archetype == "CONNECTOR":
        focus["immediate_priority"] = "Community Initiatives"
        focus["reason"] = "Connectors excel through people and impact"
        focus["suggested_first_action"] = "Let's map your community involvement and find leadership opportunities"

    else:
        focus["immediate_priority"] = "168-Hour Framework"
        focus["reason"] = "Start with time management foundation"
        focus["suggested_first_action"] = "Let's audit how you're spending your time and optimize"

    return focus


def _generate_welcome_message(
    student_name: str,
    projects: List[Dict[str, Any]],
    plan_data: Dict[str, Any]
) -> str:
    """
    Generate the proactive welcome message for the student.

    This is what the student sees when they first open the Execution tab
    after their game plan is generated.
    """
    # Count projects by category
    awards = sum(1 for p in projects if p.get("category") == "award")
    programs = sum(1 for p in projects if p.get("category") == "summer_program")
    ecs = sum(1 for p in projects if p.get("category") in ("ec", "ec_goal"))
    academics = sum(1 for p in projects if p.get("category") == "academic")

    # Find nearest deadline
    nearest = None
    nearest_days = None
    now = datetime.now()

    for project in projects:
        deadline_str = project.get("target_end_date")
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str.replace("Z", "").replace("+00:00", ""))
                days = (deadline - now).days
                if days > 0 and (nearest_days is None or days < nearest_days):
                    nearest_days = days
                    nearest = project.get("title")
            except:
                pass

    # Build message
    message = f"""Hey {student_name}! 🎯

Your game plan is ready and I've set up everything we need to get started.

**What I've prepared for you:**
"""

    if awards:
        message += f"• {awards} award application{'s' if awards > 1 else ''} to track\n"
    if programs:
        message += f"• {programs} summer program{'s' if programs > 1 else ''} on your radar\n"
    if ecs:
        message += f"• {ecs} EC goal{'s' if ecs > 1 else ''} to work toward\n"
    if academics:
        message += f"• {academics} academic target{'s' if academics > 1 else ''} to hit\n"

    if nearest and nearest_days:
        message += f"\n**First up:** {nearest} is coming up in {nearest_days} days.\n"

    message += """
**For our first session, I'd like to:**
1. Walk through your game plan together
2. Set up your 168-hour weekly schedule
3. Identify your P0 priority for this week

When you're ready, just say "Let's get started" and we'll dive in!

I'm here 24/7 whenever you need help. Let's get you into your dream school. 💪
"""

    return message.strip()


async def check_and_trigger_onboarding(supabase_client, profile_id: str) -> bool:
    """
    Check if a profile needs onboarding and trigger it if so.

    Called when:
    - Student first visits Execution tab
    - Game plan is detected but no projects exist

    Returns True if onboarding was triggered.
    """
    try:
        # Check if projects already exist
        projects_result = supabase_client.table("projects").select(
            "id"
        ).eq("profile_id", profile_id).limit(1).execute()

        if projects_result.data:
            # Projects exist, no need for onboarding
            return False

        # Check if game plan exists (use user_id, not profile_id for game_plans table)
        gameplan_result = supabase_client.table("game_plans").select(
            "plan_data"
        ).eq("user_id", profile_id).eq("plan_status", "active").limit(1).execute()

        if not gameplan_result.data or not gameplan_result.data[0].get("plan_data"):
            # No game plan yet
            return False

        # Trigger onboarding
        plan_data = gameplan_result.data[0]["plan_data"]
        await trigger_ec_onboarding(supabase_client, profile_id, plan_data)
        return True

    except Exception as e:
        logger.error(f"Onboarding check failed for {profile_id}: {e}")
        return False
