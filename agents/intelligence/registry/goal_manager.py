"""
GoalManager - Manages outcome-driven goals for students.

This is separate from the existing GoalMonitor which tracks PROGRESS.
This manager tracks WINS and OUTCOMES.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

from ..primitives import OutcomeDrivenGoal, GoalType, GoalStatus, GOAL_TEMPLATES

logger = logging.getLogger(__name__)


class GoalManager:
    """
    Manages outcome-driven goals in the database.

    Key distinction from GoalMonitor:
    - GoalMonitor tracks progress (% complete, milestones)
    - GoalManager tracks outcomes (wins, acceptances, achievements)
    """

    def __init__(self, supabase_client):
        """
        Initialize the manager with a Supabase client.

        Args:
            supabase_client: Initialized Supabase client
        """
        self.db = supabase_client
        self.table = "autonomous_goals"

    async def create(self, goal: OutcomeDrivenGoal) -> OutcomeDrivenGoal:
        """Create a new outcome-driven goal."""
        try:
            data = goal.to_db_dict()
            result = self.db.table(self.table).insert(data).execute()

            if result.data:
                logger.info(f"Created goal: {goal.primary_outcome} (id={goal.id})")
                return OutcomeDrivenGoal.from_db_row(result.data[0])
            else:
                raise Exception("Failed to create goal - no data returned")

        except Exception as e:
            logger.error(f"Failed to create goal: {e}")
            raise

    async def get(self, goal_id: UUID) -> Optional[OutcomeDrivenGoal]:
        """Get a goal by ID."""
        try:
            result = self.db.table(self.table).select("*").eq("id", str(goal_id)).single().execute()

            if result.data:
                return OutcomeDrivenGoal.from_db_row(result.data)
            return None

        except Exception as e:
            logger.warning(f"Failed to get goal {goal_id}: {e}")
            return None

    async def update(self, goal: OutcomeDrivenGoal) -> OutcomeDrivenGoal:
        """Update an existing goal."""
        try:
            goal.updated_at = datetime.utcnow()
            data = goal.to_db_dict()

            result = self.db.table(self.table).update(data).eq("id", str(goal.id)).execute()

            if result.data:
                logger.info(f"Updated goal: {goal.primary_outcome}")
                return OutcomeDrivenGoal.from_db_row(result.data[0])
            else:
                raise Exception("Failed to update goal - no data returned")

        except Exception as e:
            logger.error(f"Failed to update goal: {e}")
            raise

    async def delete(self, goal_id: UUID) -> bool:
        """Delete a goal."""
        try:
            self.db.table(self.table).delete().eq("id", str(goal_id)).execute()
            logger.info(f"Deleted goal: {goal_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete goal {goal_id}: {e}")
            return False

    async def get_active_goals(
        self,
        profile_id: UUID,
        agent_name: Optional[str] = None,
    ) -> List[OutcomeDrivenGoal]:
        """Get all active goals for a student."""
        try:
            query = self.db.table(self.table).select("*").eq("profile_id", str(profile_id)).eq("status", GoalStatus.ACTIVE)

            if agent_name:
                query = query.eq("agent_name", agent_name)

            result = query.execute()

            return [OutcomeDrivenGoal.from_db_row(row) for row in result.data] if result.data else []

        except Exception as e:
            logger.error(f"Failed to get active goals: {e}")
            return []

    async def get_goals_at_risk(
        self,
        profile_id: UUID,
    ) -> List[OutcomeDrivenGoal]:
        """Get goals that are at risk of missing their deadline."""
        active_goals = await self.get_active_goals(profile_id)
        return [g for g in active_goals if g.is_at_risk]

    async def get_achieved_goals(
        self,
        profile_id: UUID,
        limit: int = 10,
    ) -> List[OutcomeDrivenGoal]:
        """Get recently achieved goals for a student."""
        try:
            result = self.db.table(self.table).select("*").eq("profile_id", str(profile_id)).eq("status", GoalStatus.ACHIEVED).order("achieved_at", desc=True).limit(limit).execute()

            return [OutcomeDrivenGoal.from_db_row(row) for row in result.data] if result.data else []

        except Exception as e:
            logger.error(f"Failed to get achieved goals: {e}")
            return []

    async def update_progress(
        self,
        goal_id: UUID,
        new_value: float,
    ) -> Optional[OutcomeDrivenGoal]:
        """Update progress on a goal."""
        goal = await self.get(goal_id)
        if not goal:
            return None

        goal.update_progress(new_value)
        return await self.update(goal)

    async def mark_achieved(
        self,
        goal_id: UUID,
    ) -> Optional[OutcomeDrivenGoal]:
        """Mark a goal as achieved."""
        goal = await self.get(goal_id)
        if not goal:
            return None

        goal.mark_achieved()
        return await self.update(goal)

    async def mark_failed(
        self,
        goal_id: UUID,
    ) -> Optional[OutcomeDrivenGoal]:
        """Mark a goal as failed."""
        goal = await self.get(goal_id)
        if not goal:
            return None

        goal.mark_failed()
        return await self.update(goal)

    async def create_from_template(
        self,
        profile_id: UUID,
        template_name: str,
        target_date: Optional[datetime] = None,
    ) -> Optional[OutcomeDrivenGoal]:
        """Create a goal from a predefined template."""
        if template_name not in GOAL_TEMPLATES:
            logger.warning(f"Unknown template: {template_name}")
            return None

        template = GOAL_TEMPLATES[template_name]

        # Create new goal based on template
        goal = OutcomeDrivenGoal(
            profile_id=profile_id,
            agent_name=template.agent_name,
            primary_outcome=template.primary_outcome,
            goal_type=template.goal_type,
            not_goal=template.not_goal.copy(),
            primary_metric=template.primary_metric,
            target_value=template.target_value,
            secondary_metrics={k: v.model_copy() for k, v in template.secondary_metrics.items()},
            target_date=target_date,
        )

        return await self.create(goal)

    async def get_goals_by_type(
        self,
        profile_id: UUID,
        goal_type: GoalType,
    ) -> List[OutcomeDrivenGoal]:
        """Get goals of a specific type."""
        try:
            result = self.db.table(self.table).select("*").eq("profile_id", str(profile_id)).eq("goal_type", goal_type).execute()

            return [OutcomeDrivenGoal.from_db_row(row) for row in result.data] if result.data else []

        except Exception as e:
            logger.error(f"Failed to get goals by type: {e}")
            return []

    async def get_win_rate(
        self,
        profile_id: UUID,
    ) -> Dict[str, Any]:
        """Calculate the win rate for a student's goals."""
        try:
            # Get all non-active goals
            result = self.db.table(self.table).select("*").eq("profile_id", str(profile_id)).in_("status", [GoalStatus.ACHIEVED, GoalStatus.FAILED]).execute()

            goals = [OutcomeDrivenGoal.from_db_row(row) for row in result.data] if result.data else []

            total = len(goals)
            achieved = sum(1 for g in goals if g.status == GoalStatus.ACHIEVED)

            return {
                "total_completed": total,
                "achieved": achieved,
                "failed": total - achieved,
                "win_rate": achieved / total if total > 0 else 0,
            }

        except Exception as e:
            logger.error(f"Failed to get win rate: {e}")
            return {"total_completed": 0, "achieved": 0, "failed": 0, "win_rate": 0}

    async def get_summary(
        self,
        profile_id: UUID,
    ) -> Dict[str, Any]:
        """Get a summary of goals for a student."""
        active = await self.get_active_goals(profile_id)
        at_risk = [g for g in active if g.is_at_risk]
        achieved = await self.get_achieved_goals(profile_id, limit=5)
        win_rate = await self.get_win_rate(profile_id)

        return {
            "active_goals": len(active),
            "at_risk_goals": len(at_risk),
            "recently_achieved": len(achieved),
            "average_progress": sum(g.progress_percentage for g in active) / len(active) if active else 0,
            "win_rate": win_rate["win_rate"],
            "total_wins": win_rate["achieved"],
        }
