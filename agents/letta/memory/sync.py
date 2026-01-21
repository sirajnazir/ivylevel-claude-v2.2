"""
Memory Sync Service
===================

Synchronizes data from Supabase tables to Letta memory blocks.

This service:
- Reads data from existing Supabase tables
- Transforms it into Letta memory block format
- Does NOT modify any existing tables
- Stores snapshots in letta_memory_snapshots table
"""

import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uuid import UUID

from .blocks import MEMORY_BLOCKS, MemoryBlock, get_memory_block
from ..config import LETTA_TABLES, LETTA_CONFIG

logger = structlog.get_logger()


class MemorySyncService:
    """
    Service to sync Supabase data to Letta memory blocks.

    This service reads from existing tables and builds memory blocks
    without modifying any existing data structures.
    """

    def __init__(self, supabase_client):
        """
        Initialize the sync service.

        Args:
            supabase_client: Supabase client for database operations
        """
        self.supabase = supabase_client

    async def build_memory_blocks(self, profile_id: str) -> Dict[str, str]:
        """
        Build all memory blocks for a student.

        Args:
            profile_id: Student profile ID

        Returns:
            Dictionary mapping block names to block content strings
        """
        blocks = {}

        # Gather all source data
        source_data = await self._gather_source_data(profile_id)

        # Build each memory block
        for block_name, block in MEMORY_BLOCKS.items():
            try:
                content = block.build(source_data.get(block_name, {}))
                blocks[block_name] = content

                logger.debug(
                    "memory_block_built",
                    profile_id=profile_id,
                    block_name=block_name,
                    content_length=len(content),
                )

            except Exception as e:
                logger.error(
                    "memory_block_build_error",
                    profile_id=profile_id,
                    block_name=block_name,
                    error=str(e),
                )
                blocks[block_name] = f"# {block_name}\n\nError building block: {str(e)}"

        return blocks

    async def _gather_source_data(self, profile_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Gather all source data needed for memory blocks.

        Reads from existing tables without modification.
        """
        data = {
            "student_profile": {},
            "coaching_history": {},
            "active_gameplan": {},
            "outcome_tracker": {},
            "deadline_state": {},
        }

        try:
            # Fetch profile data
            data["student_profile"] = await self._fetch_student_profile(profile_id)

            # Fetch coaching history
            data["coaching_history"] = await self._fetch_coaching_history(profile_id)

            # Fetch active gameplan
            data["active_gameplan"] = await self._fetch_active_gameplan(profile_id)

            # Fetch outcome data
            data["outcome_tracker"] = await self._fetch_outcome_data(profile_id)

            # Fetch deadline data
            data["deadline_state"] = await self._fetch_deadline_data(profile_id)

        except Exception as e:
            logger.error(
                "gather_source_data_error",
                profile_id=profile_id,
                error=str(e),
            )

        return data

    async def _fetch_student_profile(self, profile_id: str) -> Dict[str, Any]:
        """Fetch student profile data from profiles table.

        FIX: Builds profile data directly from profiles columns instead of
        looking for non-existent assessment_data column or assessment_narratives table.
        """
        try:
            # Fetch profile
            profile_result = self.supabase.table("profiles") \
                .select("*") \
                .eq("id", profile_id) \
                .single() \
                .execute()

            profile = profile_result.data or {}

            # FIX: Build name from first_name + last_name (no "name" column exists)
            name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or "Unknown"

            # FIX: Build test_scores from individual columns (no "test_scores" dict exists)
            test_scores = {}
            if profile.get('sat_score'):
                test_scores['sat'] = profile['sat_score']
            if profile.get('act_score'):
                test_scores['act'] = profile['act_score']

            # Build profile data with correct field mappings
            profile_data = {
                "name": name,
                "grade": profile.get('grade'),
                "school_type": profile.get('school_type'),
                "gpa": profile.get('gpa'),
                "test_scores": test_scores,
                "target_schools": profile.get('target_schools') or [],
                "intended_major": profile.get('intended_major') or profile.get('target_major'),
            }

            # FIX: Build assessment data from profile's narrative_* columns
            # (assessment_narratives table doesn't exist - data is in profiles table)
            assessment_data = {
                "archetype": profile.get('archetype'),
                "cri_score": profile.get('cri_score'),
                "narrative_dna": profile.get('narrative_dna'),
                "narrative_brand_statement": profile.get('narrative_brand_statement'),
                "strengths": profile.get('narrative_themes') or [],
            }

            return {
                "profile": profile_data,
                "assessment": assessment_data,
            }

        except Exception as e:
            logger.error("fetch_student_profile_error", profile_id=profile_id, error=str(e))
            return {}

    async def _fetch_coaching_history(self, profile_id: str) -> Dict[str, Any]:
        """Fetch coaching history from various tables."""
        try:
            # Fetch recent interactions from proactive_notifications
            interactions = []
            try:
                result = self.supabase.table("proactive_notifications") \
                    .select("*") \
                    .eq("profile_id", profile_id) \
                    .order("created_at", desc=True) \
                    .limit(10) \
                    .execute()

                for row in result.data or []:
                    interactions.append({
                        "date": row.get("created_at", "")[:10],
                        "topic": row.get("notification_type", "Coaching"),
                        "outcome": "Delivered",
                        "summary": row.get("message", "")[:150],
                    })
            except Exception:
                pass

            # TODO: student_intelligence table doesn't exist yet
            # When created, fetch learned patterns here
            patterns = []
            logger.debug("letta_student_intelligence_skipped", reason="table not yet created")

            # TODO: execution_logs table doesn't exist yet
            # When created, fetch techniques used here
            techniques = []
            logger.debug("letta_execution_logs_skipped", reason="table not yet created")

            return {
                "recent_interactions": interactions,
                "learned_patterns": patterns,
                "techniques_used": techniques,
            }

        except Exception as e:
            logger.error("fetch_coaching_history_error", profile_id=profile_id, error=str(e))
            return {}

    async def _fetch_active_gameplan(self, profile_id: str) -> Dict[str, Any]:
        """Fetch active gameplan and tasks."""
        try:
            # Fetch active gameplan
            gameplan = {}
            # FIX: Table is "game_plans" not "gameplans", column is "plan_status" not "status"
            try:
                result = self.supabase.table("game_plans") \
                    .select("*") \
                    .eq("profile_id", profile_id) \
                    .eq("plan_status", "active") \
                    .order("created_at", desc=True) \
                    .limit(1) \
                    .execute()

                if result.data:
                    gp = result.data[0]
                    # Map to expected field names
                    gameplan = {
                        "id": gp.get("id"),
                        "phase": gp.get("current_phase"),  # FIX: was "phase"
                        "status": gp.get("plan_status"),   # FIX: was "status"
                        "created_at": gp.get("created_at"),
                        "strategic_focus": (gp.get("plan_data") or {}).get("strategic_focus", ""),
                        "milestones": (gp.get("plan_data") or {}).get("milestones", []),
                    }
            except Exception:
                pass

            # TODO: tasks table doesn't exist yet
            # When created, fetch tasks for this gameplan here
            tasks = []
            logger.debug("letta_tasks_skipped", reason="table not yet created")

            return {
                "gameplan": gameplan,
                "tasks": tasks,
            }

        except Exception as e:
            logger.error("fetch_active_gameplan_error", profile_id=profile_id, error=str(e))
            return {}

    async def _fetch_outcome_data(self, profile_id: str) -> Dict[str, Any]:
        """Fetch goals and achievements.

        TODO: outcome_driven_goals table doesn't exist yet.
        Returns empty defaults until table is created.
        """
        logger.debug("letta_outcome_driven_goals_skipped", reason="table not yet created")

        # Return sensible defaults
        return {
            "goals": [],
            "achievements": [],
            "at_risk_goals": [],
            "goals_completed": 0,
            "tasks_completed_month": 0,
            "completion_rate": 0,
        }

    async def _fetch_deadline_data(self, profile_id: str) -> Dict[str, Any]:
        """Fetch deadlines and time-sensitive items.

        FIX: tasks table doesn't exist yet. Returns empty task deadlines.
        FIX: assessment_data column doesn't exist - use target_schools directly.
        """
        try:
            deadlines = []
            overdue = []
            upcoming_7_days = []

            # TODO: tasks table doesn't exist yet
            # When created, fetch tasks with due dates here
            logger.debug("letta_tasks_deadlines_skipped", reason="table not yet created")

            # FIX: Fetch target_schools directly from profile (no assessment_data column)
            try:
                profile_result = self.supabase.table("profiles") \
                    .select("target_schools") \
                    .eq("id", profile_id) \
                    .single() \
                    .execute()

                if profile_result.data:
                    # FIX: target_schools is a direct column, not nested in assessment_data
                    target_schools = profile_result.data.get("target_schools") or []

                    # Add placeholder application deadlines
                    for school in target_schools[:5]:
                        if isinstance(school, str):
                            deadlines.append({
                                "title": f"{school} Application",
                                "school": school,
                                "type": "application",
                                "round": "Regular Decision",
                                "deadline": "2026-01-01",  # Placeholder
                            })

            except Exception:
                pass

            return {
                "deadlines": deadlines,
                "overdue_tasks": overdue,
                "upcoming_7_days": upcoming_7_days,
            }

        except Exception as e:
            logger.error("fetch_deadline_data_error", profile_id=profile_id, error=str(e))
            return {}

    async def save_snapshot(self, profile_id: str, blocks: Dict[str, str]) -> bool:
        """
        Save memory block snapshots to letta_memory_snapshots table.

        Args:
            profile_id: Student profile ID
            blocks: Dictionary of block names to content

        Returns:
            True if successful
        """
        try:
            records = [
                {
                    "profile_id": profile_id,
                    "block_name": block_name,
                    "block_content": content,
                    "snapshot_at": datetime.now().isoformat(),
                }
                for block_name, content in blocks.items()
            ]

            self.supabase.table(LETTA_TABLES["memory_snapshots"]) \
                .upsert(records, on_conflict="profile_id,block_name") \
                .execute()

            logger.info(
                "memory_snapshot_saved",
                profile_id=profile_id,
                block_count=len(blocks),
            )
            return True

        except Exception as e:
            logger.error(
                "memory_snapshot_save_error",
                profile_id=profile_id,
                error=str(e),
            )
            return False

    async def load_snapshot(self, profile_id: str) -> Optional[Dict[str, str]]:
        """
        Load memory block snapshots from letta_memory_snapshots table.

        Args:
            profile_id: Student profile ID

        Returns:
            Dictionary of block names to content, or None if not found
        """
        try:
            result = self.supabase.table(LETTA_TABLES["memory_snapshots"]) \
                .select("block_name, block_content") \
                .eq("profile_id", profile_id) \
                .execute()

            if not result.data:
                return None

            return {
                row["block_name"]: row["block_content"]
                for row in result.data
            }

        except Exception as e:
            logger.error(
                "memory_snapshot_load_error",
                profile_id=profile_id,
                error=str(e),
            )
            return None
