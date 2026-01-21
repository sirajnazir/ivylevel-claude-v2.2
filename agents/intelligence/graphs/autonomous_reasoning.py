"""
Autonomous Reasoning Graph - LangGraph orchestration for MONITOR → PREDICT → DECIDE → ACT → LEARN.

This is the core intelligence loop that runs continuously to provide proactive coaching.

The loop:
1. MONITOR: Observe student state, progress, and context
2. PREDICT: Forecast what's about to happen (risks, opportunities)
3. DECIDE: Choose the best action/intervention
4. ACT: Execute the chosen action (may involve existing agents)
5. LEARN: Record outcomes and update effectiveness
"""

from typing import TypedDict, Optional, List, Dict, Any, Annotated
from uuid import UUID
from datetime import datetime
import logging
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)


class ReasoningState(TypedDict):
    """State for the autonomous reasoning graph."""
    # Input
    profile_id: str
    trigger_event: Optional[str]  # What triggered this cycle

    # MONITOR phase
    student_state: Optional[Dict[str, Any]]
    progress_snapshot: Optional[Dict[str, Any]]
    recent_activity: Optional[List[Dict[str, Any]]]

    # PREDICT phase
    predictions: Optional[List[Dict[str, Any]]]
    risk_level: Optional[str]  # low, medium, high, critical
    opportunity_detected: Optional[bool]

    # DECIDE phase
    selected_action: Optional[str]
    selected_asset_id: Optional[str]
    decision_reasoning: Optional[List[str]]
    requires_hitl: Optional[bool]

    # ACT phase
    action_result: Optional[Dict[str, Any]]
    notification_sent: Optional[bool]

    # LEARN phase
    outcome_recorded: Optional[bool]
    effectiveness_updated: Optional[bool]

    # Meta
    cycle_id: str
    cycle_start: str
    errors: Annotated[List[str], operator.add]  # Accumulate errors


class AutonomousReasoningGraph:
    """
    LangGraph-based autonomous reasoning loop.

    This graph runs the MONITOR → PREDICT → DECIDE → ACT → LEARN cycle,
    enabling proactive, outcome-driven coaching.
    """

    def __init__(
        self,
        asset_selector=None,
        student_manager=None,
        goal_manager=None,
        notification_service=None,
    ):
        """
        Initialize the reasoning graph with dependencies.

        Args:
            asset_selector: AssetSelector for choosing coaching assets
            student_manager: StudentIntelligenceManager for profile access
            goal_manager: Manager for outcome-driven goals
            notification_service: Service for sending notifications
        """
        self.asset_selector = asset_selector
        self.student_manager = student_manager
        self.goal_manager = goal_manager
        self.notification_service = notification_service

        # Build the graph
        self.graph = self._build_graph()
        self.checkpointer = MemorySaver()
        self.compiled = self.graph.compile(checkpointer=self.checkpointer)

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        graph = StateGraph(ReasoningState)

        # Add nodes
        graph.add_node("monitor", self._monitor_node)
        graph.add_node("predict", self._predict_node)
        graph.add_node("decide", self._decide_node)
        graph.add_node("act", self._act_node)
        graph.add_node("learn", self._learn_node)

        # Add edges
        graph.set_entry_point("monitor")
        graph.add_edge("monitor", "predict")
        graph.add_conditional_edges(
            "predict",
            self._should_act,
            {
                "act": "decide",
                "skip": "learn",  # Nothing to do, just learn from observation
            },
        )
        graph.add_conditional_edges(
            "decide",
            self._check_hitl,
            {
                "proceed": "act",
                "wait_for_approval": END,  # Pause for human approval
            },
        )
        graph.add_edge("act", "learn")
        graph.add_edge("learn", END)

        return graph

    async def _monitor_node(self, state: ReasoningState) -> Dict[str, Any]:
        """
        MONITOR: Observe student state, progress, and context.

        Gathers:
        - Current profile and psychobehavioral state
        - Progress toward goals
        - Recent activity and engagement
        """
        profile_id = state["profile_id"]
        updates = {}

        try:
            # Get student state
            if self.student_manager:
                profile_summary = await self.student_manager.get_profile_summary(
                    UUID(profile_id)
                )
                updates["student_state"] = profile_summary

            # Get progress snapshot
            if self.goal_manager:
                goals = await self.goal_manager.get_active_goals(UUID(profile_id))
                progress = {
                    "active_goals": len(goals),
                    "goals_at_risk": sum(1 for g in goals if g.is_at_risk),
                    "average_progress": sum(g.progress_percentage for g in goals) / len(goals) if goals else 0,
                }
                updates["progress_snapshot"] = progress

            # Get recent activity (placeholder - would come from activity tracking)
            updates["recent_activity"] = []

            logger.info(f"MONITOR: Gathered state for profile {profile_id}")

        except Exception as e:
            logger.error(f"MONITOR error: {e}")
            updates["errors"] = [f"Monitor error: {str(e)}"]

        return updates

    async def _predict_node(self, state: ReasoningState) -> Dict[str, Any]:
        """
        PREDICT: Forecast what's about to happen.

        Analyzes:
        - Risk of goal failure
        - Burnout indicators
        - Upcoming deadlines
        - Opportunity windows
        """
        updates = {"predictions": [], "risk_level": "low", "opportunity_detected": False}

        try:
            student_state = state.get("student_state", {})
            progress = state.get("progress_snapshot", {})

            predictions = []

            # Check for at-risk goals
            goals_at_risk = progress.get("goals_at_risk", 0)
            if goals_at_risk > 0:
                predictions.append({
                    "type": "goal_risk",
                    "severity": "high" if goals_at_risk > 1 else "medium",
                    "message": f"{goals_at_risk} goal(s) at risk of missing deadline",
                })
                updates["risk_level"] = "high"

            # Check for low progress
            avg_progress = progress.get("average_progress", 50)
            if avg_progress < 30:
                predictions.append({
                    "type": "low_progress",
                    "severity": "medium",
                    "message": "Overall progress below expected pace",
                })
                if updates["risk_level"] == "low":
                    updates["risk_level"] = "medium"

            # Check for overwhelm threshold
            overwhelm = student_state.get("work_patterns", {}).get("overwhelm_threshold", 0.7)
            if overwhelm < 0.5:
                predictions.append({
                    "type": "overwhelm_risk",
                    "severity": "medium",
                    "message": "Student may be approaching overwhelm threshold",
                })

            # Check for opportunity (high momentum)
            if avg_progress > 70:
                predictions.append({
                    "type": "momentum",
                    "severity": "positive",
                    "message": "Student has strong momentum - opportunity for stretch goals",
                })
                updates["opportunity_detected"] = True

            updates["predictions"] = predictions
            logger.info(f"PREDICT: Generated {len(predictions)} predictions, risk={updates['risk_level']}")

        except Exception as e:
            logger.error(f"PREDICT error: {e}")
            updates["errors"] = [f"Predict error: {str(e)}"]

        return updates

    def _should_act(self, state: ReasoningState) -> str:
        """Determine if action is needed based on predictions."""
        risk = state.get("risk_level", "low")
        opportunity = state.get("opportunity_detected", False)
        predictions = state.get("predictions", [])

        # Act if there's risk, opportunity, or predictions
        if risk in ["medium", "high", "critical"] or opportunity or len(predictions) > 0:
            return "act"
        return "skip"

    async def _decide_node(self, state: ReasoningState) -> Dict[str, Any]:
        """
        DECIDE: Choose the best action/intervention.

        Uses:
        - Asset selector to find appropriate coaching asset
        - Student profile to personalize the approach
        - Risk level to determine urgency
        """
        updates = {
            "selected_action": None,
            "selected_asset_id": None,
            "decision_reasoning": [],
            "requires_hitl": False,
        }

        try:
            profile_id = state["profile_id"]
            risk_level = state.get("risk_level", "low")
            predictions = state.get("predictions", [])

            reasoning = []

            # Determine action type based on predictions
            if any(p["type"] == "goal_risk" for p in predictions):
                action = "intervention_nudge"
                reasoning.append("Goal at risk detected - intervention needed")
            elif any(p["type"] == "overwhelm_risk" for p in predictions):
                action = "support_check_in"
                reasoning.append("Overwhelm risk detected - supportive check-in needed")
            elif any(p["type"] == "momentum" for p in predictions):
                action = "stretch_suggestion"
                reasoning.append("Momentum detected - suggest stretch goal")
            elif any(p["type"] == "low_progress" for p in predictions):
                action = "progress_nudge"
                reasoning.append("Low progress detected - gentle nudge needed")
            else:
                action = "observation"
                reasoning.append("No immediate action required - continue monitoring")

            updates["selected_action"] = action
            updates["decision_reasoning"] = reasoning

            # Select appropriate coaching asset
            if self.asset_selector and self.student_manager:
                student_profile = await self.student_manager.get_or_create(UUID(profile_id))

                context = {
                    "event_type": action,
                    "risk_level": risk_level,
                    "predictions": [p["type"] for p in predictions],
                }

                from ..primitives import AssetDomain
                selection = await self.asset_selector.select(
                    context=context,
                    student_profile=student_profile,
                    domain=AssetDomain.EMOTIONAL if action == "support_check_in" else AssetDomain.EXECUTION,
                )

                if selection.success:
                    updates["selected_asset_id"] = str(selection.asset.id)
                    reasoning.append(f"Selected asset: {selection.asset.name}")
                    reasoning.extend(selection.reasoning)

            # Check if HITL is required
            if risk_level == "critical" or action == "intervention_nudge":
                updates["requires_hitl"] = True
                reasoning.append("High-stakes action - requires human approval")

            updates["decision_reasoning"] = reasoning
            logger.info(f"DECIDE: Action={action}, HITL={updates['requires_hitl']}")

        except Exception as e:
            logger.error(f"DECIDE error: {e}")
            updates["errors"] = [f"Decide error: {str(e)}"]

        return updates

    def _check_hitl(self, state: ReasoningState) -> str:
        """Check if human-in-the-loop approval is required."""
        if state.get("requires_hitl", False):
            return "wait_for_approval"
        return "proceed"

    async def _act_node(self, state: ReasoningState) -> Dict[str, Any]:
        """
        ACT: Execute the chosen action.

        May:
        - Send a notification
        - Create a task
        - Trigger another agent
        - Update goals
        """
        updates = {
            "action_result": None,
            "notification_sent": False,
        }

        try:
            action = state.get("selected_action")
            profile_id = state["profile_id"]
            reasoning = state.get("decision_reasoning", [])

            if action == "observation":
                updates["action_result"] = {"type": "observation", "message": "No action taken"}
                logger.info("ACT: Observation only, no action taken")
                return updates

            # Send notification if we have a notification service
            if self.notification_service:
                notification = await self._create_notification(
                    profile_id=profile_id,
                    action=action,
                    reasoning=reasoning,
                )
                updates["notification_sent"] = True
                updates["action_result"] = {
                    "type": "notification",
                    "notification_id": notification.get("id"),
                    "message": notification.get("message"),
                }
            else:
                # Log the intended action
                updates["action_result"] = {
                    "type": action,
                    "message": f"Would have executed: {action}",
                    "reasoning": reasoning,
                }

            logger.info(f"ACT: Executed {action}")

        except Exception as e:
            logger.error(f"ACT error: {e}")
            updates["errors"] = [f"Act error: {str(e)}"]

        return updates

    async def _learn_node(self, state: ReasoningState) -> Dict[str, Any]:
        """
        LEARN: Record outcomes and update effectiveness.

        Records:
        - Cycle completion
        - Action outcomes (when known)
        - Asset effectiveness updates
        """
        updates = {
            "outcome_recorded": False,
            "effectiveness_updated": False,
        }

        try:
            # Record reasoning cycle (would save to autonomous_reasoning_cycles table)
            cycle_data = {
                "cycle_id": state.get("cycle_id"),
                "profile_id": state.get("profile_id"),
                "monitoring_state": state.get("student_state"),
                "predictions": state.get("predictions"),
                "decisions": {
                    "action": state.get("selected_action"),
                    "asset_id": state.get("selected_asset_id"),
                    "reasoning": state.get("decision_reasoning"),
                },
                "actions_taken": state.get("action_result"),
                "cycle_end": datetime.utcnow().isoformat(),
            }

            # In a real implementation, this would save to the database
            updates["outcome_recorded"] = True

            logger.info(f"LEARN: Cycle {state.get('cycle_id')} recorded")

        except Exception as e:
            logger.error(f"LEARN error: {e}")
            updates["errors"] = [f"Learn error: {str(e)}"]

        return updates

    async def _create_notification(
        self,
        profile_id: str,
        action: str,
        reasoning: List[str],
    ) -> Dict[str, Any]:
        """Create a notification for the student."""
        notification_templates = {
            "intervention_nudge": {
                "title": "Quick Check-in",
                "message": "I noticed one of your goals might need some attention. Let's chat about how I can help!",
                "urgency": "high",
            },
            "support_check_in": {
                "title": "How are you doing?",
                "message": "Just wanted to check in. Remember, it's okay to take things one step at a time.",
                "urgency": "normal",
            },
            "stretch_suggestion": {
                "title": "You're on fire!",
                "message": "Your progress is impressive! Ready for a stretch goal?",
                "urgency": "low",
            },
            "progress_nudge": {
                "title": "Small step today?",
                "message": "What's one small thing you could do today to move forward?",
                "urgency": "normal",
            },
        }

        template = notification_templates.get(action, {
            "title": "Update",
            "message": "I have some thoughts to share with you.",
            "urgency": "normal",
        })

        return {
            "id": f"notif_{datetime.utcnow().timestamp()}",
            "profile_id": profile_id,
            "title": template["title"],
            "message": template["message"],
            "urgency": template["urgency"],
            "reasoning": reasoning,
        }

    async def run_cycle(
        self,
        profile_id: str,
        trigger_event: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a complete reasoning cycle for a student.

        Args:
            profile_id: The student's profile ID
            trigger_event: What triggered this cycle (e.g., "scheduled", "activity", "request")

        Returns:
            Final state after the cycle completes
        """
        from uuid import uuid4

        initial_state: ReasoningState = {
            "profile_id": profile_id,
            "trigger_event": trigger_event,
            "student_state": None,
            "progress_snapshot": None,
            "recent_activity": None,
            "predictions": None,
            "risk_level": None,
            "opportunity_detected": None,
            "selected_action": None,
            "selected_asset_id": None,
            "decision_reasoning": None,
            "requires_hitl": None,
            "action_result": None,
            "notification_sent": None,
            "outcome_recorded": None,
            "effectiveness_updated": None,
            "cycle_id": str(uuid4()),
            "cycle_start": datetime.utcnow().isoformat(),
            "errors": [],
        }

        config = {"configurable": {"thread_id": f"reasoning_{profile_id}"}}

        try:
            final_state = await self.compiled.ainvoke(initial_state, config)
            logger.info(f"Reasoning cycle completed for profile {profile_id}")
            return dict(final_state)

        except Exception as e:
            logger.error(f"Reasoning cycle failed: {e}")
            return {
                **initial_state,
                "errors": [str(e)],
            }

    async def resume_after_hitl(
        self,
        thread_id: str,
        approved: bool,
    ) -> Dict[str, Any]:
        """
        Resume a paused cycle after human approval.

        Args:
            thread_id: The thread ID of the paused cycle
            approved: Whether the human approved the action

        Returns:
            Final state after resuming
        """
        config = {"configurable": {"thread_id": thread_id}}

        if approved:
            # Continue from the decide node to act
            # In a real implementation, this would resume from checkpoint
            pass

        return {}
