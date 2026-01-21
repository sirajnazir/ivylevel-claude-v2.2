"""
AutonomousMonitorService - The orchestration service for autonomous coaching.

This service:
1. Initializes all intelligence components
2. Runs reasoning cycles on schedule or on-demand
3. Handles notifications and actions
4. Records outcomes for learning

This is the main entry point for the autonomous intelligence layer.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
import logging
from datetime import datetime, timedelta
import asyncio

from intelligence.primitives import CoachingAsset, OutcomeDrivenGoal, GoalType
from intelligence.student import StudentIntelligenceProfile
from intelligence.registry import (
    AssetRegistry,
    AssetSelector,
    StudentIntelligenceManager,
    GoalManager,
)
from intelligence.graphs import AutonomousReasoningGraph
from intelligence.assets import seed_jenny_assets

logger = logging.getLogger(__name__)


class AutonomousMonitorService:
    """
    Main service for autonomous coaching intelligence.

    This service coordinates all the intelligence components:
    - Asset registry and selection
    - Student profile management
    - Goal tracking
    - Autonomous reasoning loop

    Usage:
        service = AutonomousMonitorService(supabase_client)
        await service.initialize()

        # Run reasoning for a student
        result = await service.run_reasoning_cycle("profile-uuid")

        # Or schedule periodic monitoring
        await service.start_periodic_monitoring(interval_minutes=60)
    """

    def __init__(self, supabase_client, notification_callback=None):
        """
        Initialize the autonomous monitor service.

        Args:
            supabase_client: Initialized Supabase client
            notification_callback: Optional async callback for sending notifications
        """
        self.db = supabase_client
        self.notification_callback = notification_callback

        # Initialize components
        self.asset_registry = AssetRegistry(supabase_client)
        self.student_manager = StudentIntelligenceManager(supabase_client)
        self.goal_manager = GoalManager(supabase_client)

        # Asset selector (needs registry)
        self.asset_selector = AssetSelector(self.asset_registry)

        # Reasoning graph (needs all components)
        self.reasoning_graph = AutonomousReasoningGraph(
            asset_selector=self.asset_selector,
            student_manager=self.student_manager,
            goal_manager=self.goal_manager,
            notification_service=self,  # Use self for notifications
        )

        self._initialized = False
        self._monitoring_task = None

    async def initialize(self, seed_assets: bool = True) -> bool:
        """
        Initialize the service and optionally seed coaching assets.

        Args:
            seed_assets: Whether to seed Jenny's coaching assets

        Returns:
            True if initialization successful
        """
        try:
            logger.info("Initializing AutonomousMonitorService...")

            # Seed Jenny's assets if requested
            if seed_assets:
                count = await seed_jenny_assets(self.asset_registry, overwrite=False)
                logger.info(f"Seeded {count} coaching assets")

            self._initialized = True
            logger.info("AutonomousMonitorService initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize AutonomousMonitorService: {e}")
            return False

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    async def run_reasoning_cycle(
        self,
        profile_id: str,
        trigger_event: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a complete autonomous reasoning cycle for a student.

        Args:
            profile_id: The student's profile ID
            trigger_event: What triggered this cycle (e.g., "scheduled", "activity", "request")

        Returns:
            Result of the reasoning cycle
        """
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")

        try:
            logger.info(f"Running reasoning cycle for profile {profile_id}")

            result = await self.reasoning_graph.run_cycle(
                profile_id=profile_id,
                trigger_event=trigger_event or "manual",
            )

            # Handle any errors
            if result.get("errors"):
                logger.warning(f"Reasoning cycle had errors: {result['errors']}")

            # Save the cycle to database
            await self._save_reasoning_cycle(result)

            return {
                "success": not bool(result.get("errors")),
                "cycle_id": result.get("cycle_id"),
                "action_taken": result.get("selected_action"),
                "notification_sent": result.get("notification_sent", False),
                "predictions": result.get("predictions", []),
                "reasoning": result.get("decision_reasoning", []),
            }

        except Exception as e:
            logger.error(f"Reasoning cycle failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def _save_reasoning_cycle(self, cycle_data: Dict[str, Any]) -> None:
        """Save reasoning cycle to database for learning and debugging."""
        try:
            record = {
                "id": cycle_data.get("cycle_id"),
                "profile_id": cycle_data.get("profile_id"),
                "agent_name": "autonomous_monitor",
                "monitoring_state": cycle_data.get("student_state"),
                "predictions": cycle_data.get("predictions"),
                "decisions": {
                    "action": cycle_data.get("selected_action"),
                    "asset_id": cycle_data.get("selected_asset_id"),
                    "reasoning": cycle_data.get("decision_reasoning"),
                    "requires_hitl": cycle_data.get("requires_hitl"),
                },
                "actions_taken": cycle_data.get("action_result"),
                "learnings": {
                    "outcome_recorded": cycle_data.get("outcome_recorded"),
                    "effectiveness_updated": cycle_data.get("effectiveness_updated"),
                },
                "cycle_start": cycle_data.get("cycle_start"),
                "cycle_end": datetime.utcnow().isoformat(),
            }

            self.db.table("autonomous_reasoning_cycles").insert(record).execute()

        except Exception as e:
            logger.error(f"Failed to save reasoning cycle: {e}")

    async def send_notification(
        self,
        profile_id: str,
        title: str,
        message: str,
        urgency: str = "normal",
        related_asset_id: Optional[str] = None,
        related_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a proactive notification to a student.

        Args:
            profile_id: The student's profile ID
            title: Notification title
            message: Notification message
            urgency: Urgency level (low, normal, high, critical)
            related_asset_id: Optional related coaching asset ID
            related_data: Optional additional data

        Returns:
            Notification record
        """
        try:
            notification = {
                "profile_id": profile_id,
                "agent_name": "autonomous_monitor",
                "notification_type": "proactive",
                "title": title,
                "message": message,
                "urgency": urgency,
                "related_asset_id": related_asset_id,
                "related_data": related_data,
                "status": "pending",
            }

            result = self.db.table("proactive_notifications").insert(notification).execute()

            # Call external notification callback if provided
            if self.notification_callback:
                await self.notification_callback(notification)

            logger.info(f"Sent notification to profile {profile_id}: {title}")

            return result.data[0] if result.data else notification

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return {"error": str(e)}

    async def get_pending_notifications(
        self,
        profile_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get pending notifications for a student."""
        try:
            result = self.db.table("proactive_notifications").select("*").eq("profile_id", profile_id).eq("status", "pending").order("created_at", desc=True).limit(limit).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get pending notifications: {e}")
            return []

    async def mark_notification_viewed(
        self,
        notification_id: str,
    ) -> bool:
        """Mark a notification as viewed."""
        try:
            self.db.table("proactive_notifications").update({"status": "viewed", "viewed_at": datetime.utcnow().isoformat()}).eq("id", notification_id).execute()
            return True

        except Exception as e:
            logger.error(f"Failed to mark notification viewed: {e}")
            return False

    async def create_goal(
        self,
        profile_id: str,
        primary_outcome: str,
        goal_type: GoalType,
        agent_name: str = "autonomous_monitor",
        not_goal: Optional[List[str]] = None,
        target_date: Optional[datetime] = None,
    ) -> OutcomeDrivenGoal:
        """Create a new outcome-driven goal for a student."""
        goal = OutcomeDrivenGoal(
            profile_id=UUID(profile_id),
            agent_name=agent_name,
            primary_outcome=primary_outcome,
            goal_type=goal_type,
            not_goal=not_goal or [],
            target_date=target_date,
        )

        return await self.goal_manager.create(goal)

    async def get_student_summary(
        self,
        profile_id: str,
    ) -> Dict[str, Any]:
        """Get a comprehensive summary of a student's state."""
        profile = await self.student_manager.get_profile_summary(UUID(profile_id))
        goals = await self.goal_manager.get_summary(UUID(profile_id))
        notifications = await self.get_pending_notifications(profile_id, limit=5)

        return {
            "profile": profile,
            "goals": goals,
            "pending_notifications": len(notifications),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def record_outcome(
        self,
        profile_id: str,
        outcome_type: str,
        outcome_data: Dict[str, Any],
        related_asset_ids: Optional[List[str]] = None,
    ) -> bool:
        """Record an actual outcome (win, completion, etc.)."""
        try:
            record = {
                "profile_id": profile_id,
                "outcome_type": outcome_type,
                "outcome_data": outcome_data,
                "related_asset_ids": related_asset_ids or [],
            }

            self.db.table("student_outcomes").insert(record).execute()
            logger.info(f"Recorded outcome for profile {profile_id}: {outcome_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to record outcome: {e}")
            return False

    async def start_periodic_monitoring(
        self,
        interval_minutes: int = 60,
        profile_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Start periodic monitoring for students.

        Args:
            interval_minutes: How often to run reasoning cycles
            profile_ids: Specific profiles to monitor. If None, monitors all active profiles.
        """
        if self._monitoring_task:
            logger.warning("Periodic monitoring already running")
            return

        async def monitoring_loop():
            while True:
                try:
                    if profile_ids:
                        profiles_to_check = profile_ids
                    else:
                        # Get active profiles (would need to query profiles table)
                        profiles_to_check = []  # Placeholder

                    for profile_id in profiles_to_check:
                        await self.run_reasoning_cycle(profile_id, trigger_event="scheduled")

                    await asyncio.sleep(interval_minutes * 60)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(60)  # Wait a minute before retrying

        self._monitoring_task = asyncio.create_task(monitoring_loop())
        logger.info(f"Started periodic monitoring (interval: {interval_minutes} minutes)")

    async def stop_periodic_monitoring(self) -> None:
        """Stop periodic monitoring."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
            logger.info("Stopped periodic monitoring")

    async def handle_event(
        self,
        event_type: str,
        profile_id: str,
        event_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Handle an external event that might trigger reasoning.

        Args:
            event_type: Type of event (e.g., "task_completed", "deadline_approaching", "crisis")
            profile_id: The student's profile ID
            event_data: Additional event data

        Returns:
            Result of handling the event
        """
        logger.info(f"Handling event '{event_type}' for profile {profile_id}")

        # For high-priority events, run reasoning immediately
        high_priority_events = ["crisis", "deadline_approaching", "goal_at_risk"]

        if event_type in high_priority_events:
            return await self.run_reasoning_cycle(
                profile_id=profile_id,
                trigger_event=event_type,
            )

        # For other events, just record them for the next scheduled cycle
        # In a real implementation, this would queue the event
        return {
            "event_type": event_type,
            "profile_id": profile_id,
            "action": "queued",
        }
