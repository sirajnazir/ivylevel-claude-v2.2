"""
LangGraph Workflow for Proactive Execution Management v5.3
==========================================================

Follows the pattern established by CrisisAlchemy graph.

Workflow:
  assess → route_by_situation →
      ├── nudge (mild/moderate stalls)
      ├── escalate (severe stalls) → nudge
      ├── critical_eds (EDS > 50) → nudge
      └── celebrate (all good!)
  → finalize → END
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, List, Dict, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class ExecutionState(TypedDict):
    """State for execution workflow."""
    profile_id: str
    trigger: str  # 'scheduled' | 'manual' | 'threshold'

    # Assessment data
    eds: Optional[Dict[str, Any]]
    stalled_projects: List[Dict[str, Any]]
    weekly_plan: Optional[Dict[str, Any]]

    # Actions taken
    nudges_sent: List[Dict[str, Any]]
    crises_created: List[Dict[str, Any]]
    celebrations: List[str]

    # Metadata
    started_at: str
    completed_at: Optional[str]
    error: Optional[str]


# =========================================================================
# NODE FUNCTIONS
# =========================================================================

async def assess_state(state: ExecutionState) -> ExecutionState:
    """Assess current execution state."""
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    profile_id = state["profile_id"]

    logger.info("execution_workflow_assess", profile_id=profile_id)

    try:
        # Gather data
        eds = await agent.tool_calculate_eds(profile_id)
        stalled = await agent.tool_detect_stalls(profile_id, threshold_days=5)
        weekly = await agent._get_current_weekly_plan(profile_id)

        return {
            **state,
            "eds": eds,
            "stalled_projects": stalled,
            "weekly_plan": weekly,
        }
    except Exception as e:
        logger.error("assess_state_error", error=str(e), profile_id=profile_id)
        return {
            **state,
            "eds": {"eds_score": 0, "status": "unknown"},
            "stalled_projects": [],
            "weekly_plan": {},
            "error": str(e),
        }


async def send_nudges(state: ExecutionState) -> ExecutionState:
    """Send nudges for mild/moderate stalls."""
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    nudges = []

    logger.info("execution_workflow_nudge", profile_id=state["profile_id"])

    for project in state.get("stalled_projects", []):
        if project.get("severity") in ["mild", "moderate"]:
            days = project.get("days_since_activity", 0)
            title = project.get("title", "Untitled")

            # Customize message based on severity
            if project.get("severity") == "moderate":
                message = f"🟡 '{title}' has been quiet for {days} days. This is a priority item - let's get it moving! What's the smallest next step you can take?"
            else:
                message = f"Hey! Just checking in on '{title}'. It's been {days} days since you worked on it. Need any help getting unstuck?"

            try:
                nudge = await agent.tool_create_nudge(
                    profile_id=state["profile_id"],
                    message=message,
                    nudge_type="stall_detected",
                    project_id=project.get("id"),
                    priority="high" if project.get("severity") == "moderate" else "medium",
                )
                nudges.append(nudge)
            except Exception as e:
                logger.warning("nudge_send_failed", error=str(e), project_id=project.get("id"))

    return {**state, "nudges_sent": nudges}


async def escalate_crises(state: ExecutionState) -> ExecutionState:
    """Escalate severe stalls to Crisis Alchemy."""
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    crises = []

    logger.info("execution_workflow_escalate", profile_id=state["profile_id"])

    for project in state.get("stalled_projects", []):
        if project.get("severity") == "severe":
            days = project.get("days_since_activity", 0)

            try:
                crisis = await agent.tool_escalate_to_crisis(
                    project_id=project.get("id"),
                    reason=f"Project stalled for {days} days - needs Crisis Alchemy intervention",
                    severity="high" if days >= 21 else "medium",
                )
                crises.append(crisis)
            except Exception as e:
                logger.warning("crisis_escalation_failed", error=str(e), project_id=project.get("id"))

    return {**state, "crises_created": crises}


async def celebrate_progress(state: ExecutionState) -> ExecutionState:
    """Celebrate completions and good EDS status."""
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    celebrations = []

    eds = state.get("eds", {})

    logger.info("execution_workflow_celebrate", profile_id=state["profile_id"])

    if eds.get("status") == "healthy" and not state.get("stalled_projects"):
        message = f"🎉 Great job! Your EDS is {eds.get('eds_score', 0)} (healthy) and no projects are stalled. Keep up the momentum!"
        try:
            await agent.tool_create_nudge(
                profile_id=state["profile_id"],
                message=message,
                nudge_type="celebration",
                priority="low",
            )
            celebrations.append(message)
        except Exception as e:
            logger.warning("celebration_failed", error=str(e))

    return {**state, "celebrations": celebrations}


async def handle_critical_eds(state: ExecutionState) -> ExecutionState:
    """Handle critical EDS situation."""
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    eds = state.get("eds", {})

    logger.info("execution_workflow_critical_eds", profile_id=state["profile_id"], eds_score=eds.get("eds_score"))

    if eds.get("status") == "critical":
        message = f"""⚠️ Your Execution Debt Score is {eds.get('eds_score', 0)} (critical).

This usually means too many things are piling up. Let's fix this:

1. **Incomplete steps:** {eds.get('incomplete_steps', 0)}
2. **Overdue projects:** {eds.get('overdue_projects', 0)}
3. **Stalled projects:** {eds.get('stalled_projects', 0)}

Reply to this message and let's prioritize together. What's the ONE thing we should focus on first?"""

        try:
            await agent.tool_create_nudge(
                profile_id=state["profile_id"],
                message=message,
                nudge_type="eds_critical",
                priority="high",
            )
        except Exception as e:
            logger.warning("critical_eds_nudge_failed", error=str(e))

    return state


async def finalize(state: ExecutionState) -> ExecutionState:
    """Finalize the workflow."""
    logger.info(
        "execution_workflow_completed",
        profile_id=state["profile_id"],
        nudges_sent=len(state.get("nudges_sent", [])),
        crises_created=len(state.get("crises_created", [])),
        celebrations=len(state.get("celebrations", [])),
    )

    return {
        **state,
        "completed_at": datetime.now().isoformat(),
    }


# =========================================================================
# ROUTING FUNCTION
# =========================================================================

def route_by_situation(state: ExecutionState) -> Literal["nudge", "escalate", "critical_eds", "celebrate"]:
    """Route based on current situation."""
    eds = state.get("eds", {})
    stalled = state.get("stalled_projects", [])

    # Check for critical EDS first
    if eds.get("status") == "critical":
        return "critical_eds"

    # Check for severe stalls (need escalation)
    severe_stalls = [p for p in stalled if p.get("severity") == "severe"]
    if severe_stalls:
        return "escalate"

    # Check for mild/moderate stalls (need nudge)
    if stalled:
        return "nudge"

    # All good - celebrate
    return "celebrate"


# =========================================================================
# BUILD GRAPH
# =========================================================================

def build_execution_graph() -> StateGraph:
    """Build the execution workflow graph."""
    graph = StateGraph(ExecutionState)

    # Add nodes
    graph.add_node("assess", assess_state)
    graph.add_node("nudge", send_nudges)
    graph.add_node("escalate", escalate_crises)
    graph.add_node("critical_eds", handle_critical_eds)
    graph.add_node("celebrate", celebrate_progress)
    graph.add_node("finalize", finalize)

    # Set entry point
    graph.set_entry_point("assess")

    # Add conditional edges from assess
    graph.add_conditional_edges(
        "assess",
        route_by_situation,
        {
            "nudge": "nudge",
            "escalate": "escalate",
            "critical_eds": "critical_eds",
            "celebrate": "celebrate",
        }
    )

    # All paths lead to celebrate then finalize
    graph.add_edge("nudge", "celebrate")  # After nudging, still celebrate what's good
    graph.add_edge("escalate", "nudge")   # After escalating severe, nudge moderate
    graph.add_edge("critical_eds", "nudge")  # After critical alert, still nudge
    graph.add_edge("celebrate", "finalize")
    graph.add_edge("finalize", END)

    return graph


# Compile the graph
execution_workflow = build_execution_graph().compile()


# =========================================================================
# WORKFLOW RUNNER
# =========================================================================

async def run_execution_workflow(
    profile_id: str,
    trigger: str = "scheduled",
) -> ExecutionState:
    """Run the execution workflow for a student."""
    initial_state: ExecutionState = {
        "profile_id": profile_id,
        "trigger": trigger,
        "eds": None,
        "stalled_projects": [],
        "weekly_plan": None,
        "nudges_sent": [],
        "crises_created": [],
        "celebrations": [],
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "error": None,
    }

    logger.info("execution_workflow_started", profile_id=profile_id, trigger=trigger)

    try:
        result = await execution_workflow.ainvoke(initial_state)
        return result
    except Exception as e:
        logger.error("execution_workflow_error", error=str(e), profile_id=profile_id)
        return {
            **initial_state,
            "error": str(e),
            "completed_at": datetime.now().isoformat(),
        }
