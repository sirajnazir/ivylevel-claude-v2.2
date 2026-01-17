"""
Cycle Persistence Helper
========================

v5.1: Saves ReAct cycles to database for analytics.

This module provides utilities for:
- Saving individual cycles to react_cycles table
- Saving complete sessions with all cycles
- Retrieving cycle history for analysis
- Getting agent analytics and success rates
"""

import logging
from typing import Dict, Any, Optional, List
from uuid import uuid4
from datetime import datetime

logger = logging.getLogger(__name__)


class CyclePersistence:
    """
    Persists ReAct cycles to database for analytics and debugging.

    Usage:
        persistence = CyclePersistence(supabase_client)
        await persistence.save_cycle(session_id, profile_id, agent_id, cycle_data)

    The cycle_data should be a dict with the verbose cycle summary structure:
    {
        "cycle": 1,
        "think": {...},
        "act": {...},
        "observe": {...},
        "learn": {...},
        "combined_score": 66.5,
        "quality_delta": 0,
        "passed": False,
        "duration_ms": 1200
    }
    """

    def __init__(self, supabase_client):
        """
        Initialize CyclePersistence.

        Args:
            supabase_client: Async Supabase client instance
        """
        self.supabase = supabase_client

    async def save_cycle(
        self,
        session_id: str,
        profile_id: str,
        agent_id: str,
        cycle_data: Dict[str, Any],
        is_final: bool = False,
    ) -> Optional[str]:
        """
        Save a single cycle to the database.

        Args:
            session_id: Unique session identifier
            profile_id: Profile UUID
            agent_id: Agent name/ID (e.g., "Extracurriculars", "Awards")
            cycle_data: Verbose cycle summary dict
            is_final: Whether this is the final cycle in the session

        Returns:
            Cycle ID if successful, None otherwise.
        """
        try:
            # Extract phase data
            think = cycle_data.get("think", {})
            act = cycle_data.get("act", {})
            observe = cycle_data.get("observe", {})
            learn = cycle_data.get("learn", {})

            # Extract quality scores from observe phase
            quality_scores = observe.get("quality_scores", {})

            cycle_record = {
                "profile_id": profile_id,
                "session_id": session_id,
                "agent_id": agent_id,
                "cycle_number": cycle_data.get("cycle", 1),
                "max_cycles": 3,  # Default

                # Phase data as JSONB
                "think_data": think,
                "act_data": act,
                "observe_data": observe,
                "learn_data": learn,

                # Scores
                "combined_score": cycle_data.get("combined_score", 0),
                "quality_delta": cycle_data.get("quality_delta", 0),
                "guardrails_score": quality_scores.get("guardrails", observe.get("quality_score", 0)),
                "voice_score": quality_scores.get("voice", observe.get("voice_score", 0)),
                "golden_score": quality_scores.get("golden", observe.get("golden_similarity", 0) * 100),
                "only_they_score": quality_scores.get("only_they", 0),

                # Status
                "passed": cycle_data.get("passed", False),
                "is_final_cycle": is_final,

                # Timing
                "duration_ms": cycle_data.get("duration_ms", 0),
                "think_duration_ms": think.get("duration_ms", 0),
                "act_duration_ms": act.get("duration_ms", 0),
                "observe_duration_ms": observe.get("duration_ms", 0),
                "learn_duration_ms": learn.get("duration_ms", 0),

                # Tools
                "tools_selected": think.get("tools_selected", []),
                "tools_executed": act.get("tools_executed", []),
            }

            result = await self.supabase.table("react_cycles").insert(cycle_record).execute()

            if result.data:
                return result.data[0]["id"]
            return None

        except Exception as e:
            logger.error(f"Failed to save cycle: {e}")
            return None

    async def save_session(
        self,
        session_id: str,
        profile_id: str,
        agent_id: str,
        react_metadata: Dict[str, Any],
    ) -> bool:
        """
        Save all cycles from a ReAct session.

        Args:
            session_id: Unique session identifier
            profile_id: Profile UUID
            agent_id: Agent name/ID
            react_metadata: Complete _react metadata with cycle_summary array

        Returns:
            True if successful, False otherwise.
        """
        try:
            cycle_summaries = react_metadata.get("cycle_summary", [])

            for i, cycle in enumerate(cycle_summaries):
                is_final = (i == len(cycle_summaries) - 1)
                await self.save_cycle(
                    session_id=session_id,
                    profile_id=profile_id,
                    agent_id=agent_id,
                    cycle_data=cycle,
                    is_final=is_final,
                )

            logger.info(
                f"Saved {len(cycle_summaries)} cycles for session {session_id}, agent {agent_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    async def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """
        Get all cycles for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dict with session_id and cycles array
        """
        try:
            result = await self.supabase.table("react_cycles") \
                .select("*") \
                .eq("session_id", session_id) \
                .order("agent_id", desc=False) \
                .order("cycle_number", desc=False) \
                .execute()

            return {
                "session_id": session_id,
                "cycles": result.data or [],
            }

        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return {"session_id": session_id, "cycles": []}

    async def get_agent_analytics(
        self,
        agent_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get analytics for an agent over time.

        Args:
            agent_id: Agent name/ID
            days: Number of days to look back

        Returns:
            Dict with success rate, avg cycles, avg score
        """
        try:
            result = await self.supabase.rpc(
                "get_agent_success_rate",
                {"p_agent_id": agent_id, "p_days": days}
            ).execute()

            if result.data and len(result.data) > 0:
                return result.data[0]
            return {}

        except Exception as e:
            logger.error(f"Failed to get agent analytics: {e}")
            return {}

    async def get_profile_cycles(
        self,
        profile_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get recent cycles for a specific profile.

        Args:
            profile_id: Profile UUID
            limit: Max number of cycles to return

        Returns:
            List of cycle records
        """
        try:
            result = await self.supabase.table("react_cycles") \
                .select("*") \
                .eq("profile_id", profile_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()

            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get profile cycles: {e}")
            return []

    async def get_improvement_trajectory(
        self,
        session_id: str,
        agent_id: str,
    ) -> List[float]:
        """
        Get the improvement trajectory for an agent in a session.

        Args:
            session_id: Session identifier
            agent_id: Agent name/ID

        Returns:
            List of combined scores ordered by cycle number
        """
        try:
            result = await self.supabase.rpc(
                "get_agent_trajectory",
                {"p_session_id": session_id, "p_agent_id": agent_id}
            ).execute()

            if result.data:
                return [r["combined_score"] for r in result.data]
            return []

        except Exception as e:
            logger.error(f"Failed to get improvement trajectory: {e}")
            return []


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

_persistence_instance: Optional[CyclePersistence] = None


def get_cycle_persistence(supabase_client=None) -> Optional[CyclePersistence]:
    """
    Get or create the CyclePersistence singleton.

    Args:
        supabase_client: Optional Supabase client. If not provided,
                        tries to get from tools.database.

    Returns:
        CyclePersistence instance or None if client unavailable
    """
    global _persistence_instance

    if _persistence_instance is not None:
        return _persistence_instance

    if supabase_client is None:
        try:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()
        except ImportError:
            logger.warning("Could not import Supabase client")
            return None
        except Exception as e:
            logger.warning(f"Could not get Supabase client: {e}")
            return None

    if supabase_client:
        _persistence_instance = CyclePersistence(supabase_client)
        return _persistence_instance

    return None
