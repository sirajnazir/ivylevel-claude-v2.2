# agents/agents/core/profile_snapshot.py
"""
IvyQuest v13.2 - Profile Snapshot Manager

This module tracks profile evolution over time by creating immutable
snapshots of profile state at significant moments:
- After assessments
- At milestones
- Quarterly reviews
- Manual triggers

Profile snapshots enable:
- JTBD-1: Building comprehensive identity picture
- Evolution tracking for coaching recommendations
- Handoff context preservation
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProfileSnapshot:
    """
    Immutable snapshot of profile state at a point in time.
    Used for tracking evolution and handoffs.
    """
    profile_id: str
    snapshot_type: str  # 'assessment', 'milestone', 'quarterly', 'manual', 'agent_interaction'

    # Identity
    narrative_dna: Optional[str] = None
    brand_statement: Optional[str] = None
    archetype: Optional[str] = None
    archetype_confidence: Optional[float] = None

    # Scores
    cri_score: Optional[float] = None
    eds_score: Optional[float] = None
    spike_score: Optional[float] = None

    # Counts
    activities_count: int = 0
    projects_count: int = 0
    awards_count: int = 0

    # Change tracking
    change_summary: Optional[str] = None
    changed_fields: Optional[Dict[str, Any]] = None
    trigger_event: Optional[str] = None

    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Ensure created_at is set."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for database storage."""
        data = {
            "profile_id": self.profile_id,
            "snapshot_type": self.snapshot_type,
            "narrative_dna": self.narrative_dna,
            "brand_statement": self.brand_statement,
            "archetype": self.archetype,
            "archetype_confidence": self.archetype_confidence,
            "cri_score": self.cri_score,
            "eds_score": self.eds_score,
            "spike_score": self.spike_score,
            "activities_count": self.activities_count,
            "projects_count": self.projects_count,
            "awards_count": self.awards_count,
            "change_summary": self.change_summary,
            "changed_fields": self.changed_fields,
            "trigger_event": self.trigger_event,
            "created_at": self.created_at.isoformat(),
        }
        return data

    @classmethod
    def from_profile(
        cls,
        profile_id: str,
        profile_data: Dict[str, Any],
        snapshot_type: str = "assessment",
        trigger_event: Optional[str] = None,
        previous_snapshot: Optional["ProfileSnapshot"] = None,
    ) -> "ProfileSnapshot":
        """
        Create snapshot from current profile state.
        
        Automatically calculates change_summary if previous_snapshot provided.
        
        Args:
            profile_id: Profile ID
            profile_data: Current profile data dict
            snapshot_type: Type of snapshot
            trigger_event: What triggered this snapshot
            previous_snapshot: Previous snapshot for change detection
            
        Returns:
            New ProfileSnapshot
        """
        snapshot = cls(
            profile_id=profile_id,
            snapshot_type=snapshot_type,
            narrative_dna=profile_data.get("narrative_dna"),
            brand_statement=profile_data.get("brand_statement"),
            archetype=profile_data.get("archetype"),
            archetype_confidence=profile_data.get("archetype_confidence"),
            cri_score=profile_data.get("cri_score"),
            eds_score=profile_data.get("eds_score"),
            spike_score=profile_data.get("spike_score"),
            activities_count=len(profile_data.get("activities", [])),
            projects_count=len(profile_data.get("projects", [])),
            awards_count=len(profile_data.get("awards", [])),
            trigger_event=trigger_event,
        )

        # Calculate changes from previous snapshot
        if previous_snapshot:
            changes = {}
            compare_fields = [
                "archetype", "archetype_confidence",
                "cri_score", "eds_score", "spike_score",
                "activities_count", "projects_count", "awards_count",
            ]
            
            for field_name in compare_fields:
                old_val = getattr(previous_snapshot, field_name)
                new_val = getattr(snapshot, field_name)
                if old_val != new_val:
                    changes[field_name] = {"from": old_val, "to": new_val}

            if changes:
                snapshot.changed_fields = changes
                change_names = list(changes.keys())
                snapshot.change_summary = f"Changed: {', '.join(change_names)}"

        return snapshot

    @property
    def has_identity(self) -> bool:
        """Check if snapshot has identity information."""
        return bool(self.narrative_dna or self.brand_statement or self.archetype)

    @property
    def has_scores(self) -> bool:
        """Check if snapshot has score information."""
        return any([
            self.cri_score is not None,
            self.eds_score is not None,
            self.spike_score is not None,
        ])

    @property
    def total_items(self) -> int:
        """Total count of activities, projects, and awards."""
        return self.activities_count + self.projects_count + self.awards_count

    def __repr__(self) -> str:
        return (
            f"ProfileSnapshot(profile={self.profile_id}, "
            f"type={self.snapshot_type}, "
            f"archetype={self.archetype}, "
            f"created={self.created_at.date()})"
        )


class ProfileSnapshotManager:
    """
    Manages profile snapshots in Supabase.
    
    Usage:
        manager = ProfileSnapshotManager(supabase_client)
        
        # Create snapshot
        snapshot = await manager.create_snapshot(
            profile_id="abc123",
            profile_data={...},
            snapshot_type="milestone",
            trigger_event="assessment_agent_complete",
        )
        
        # Get evolution timeline
        timeline = await manager.get_evolution_timeline("abc123", limit=10)
    """

    def __init__(self, supabase_client):
        """
        Initialize ProfileSnapshotManager.
        
        Args:
            supabase_client: Async Supabase client
        """
        self.supabase = supabase_client

    async def create_snapshot(
        self,
        profile_id: str,
        profile_data: Dict[str, Any],
        snapshot_type: str = "assessment",
        trigger_event: Optional[str] = None,
    ) -> Optional[ProfileSnapshot]:
        """
        Create and store a new profile snapshot.
        
        Args:
            profile_id: Profile ID
            profile_data: Current profile data
            snapshot_type: Type of snapshot (assessment/milestone/quarterly/manual)
            trigger_event: What triggered this snapshot
            
        Returns:
            Created ProfileSnapshot or None on error
        """
        if not self.supabase:
            logger.warning("No Supabase client - snapshots disabled")
            return None

        try:
            # Get previous snapshot for change detection
            previous = await self.get_latest_snapshot(profile_id)

            snapshot = ProfileSnapshot.from_profile(
                profile_id=profile_id,
                profile_data=profile_data,
                snapshot_type=snapshot_type,
                trigger_event=trigger_event,
                previous_snapshot=previous,
            )

            result = await self.supabase.table("profile_snapshots").insert(
                snapshot.to_dict()
            ).execute()

            if result.data:
                logger.info(
                    f"Created {snapshot_type} snapshot for profile {profile_id}"
                    f"{' with changes: ' + snapshot.change_summary if snapshot.change_summary else ''}"
                )
                return snapshot

            return None

        except Exception as e:
            logger.error(f"Failed to create snapshot: {e}")
            return None

    async def get_latest_snapshot(
        self,
        profile_id: str,
    ) -> Optional[ProfileSnapshot]:
        """
        Get the most recent snapshot for a profile.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Most recent ProfileSnapshot or None
        """
        if not self.supabase:
            return None

        try:
            result = await self.supabase.table("profile_snapshots")\
                .select("*")\
                .eq("profile_id", profile_id)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()

            if result.data:
                return self._row_to_snapshot(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get latest snapshot: {e}")
            return None

    async def get_evolution_timeline(
        self,
        profile_id: str,
        limit: int = 10,
    ) -> List[ProfileSnapshot]:
        """
        Get snapshot history showing profile evolution.
        
        Args:
            profile_id: Profile ID
            limit: Maximum number of snapshots to return
            
        Returns:
            List of snapshots, newest first
        """
        if not self.supabase:
            return []

        try:
            result = await self.supabase.table("profile_snapshots")\
                .select("*")\
                .eq("profile_id", profile_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            return [self._row_to_snapshot(row) for row in result.data or []]
        except Exception as e:
            logger.error(f"Failed to get evolution timeline: {e}")
            return []

    async def get_snapshots_by_type(
        self,
        profile_id: str,
        snapshot_type: str,
        limit: int = 10,
    ) -> List[ProfileSnapshot]:
        """
        Get snapshots of a specific type.
        
        Args:
            profile_id: Profile ID
            snapshot_type: Type to filter by
            limit: Maximum number to return
            
        Returns:
            List of matching snapshots
        """
        if not self.supabase:
            return []

        try:
            result = await self.supabase.table("profile_snapshots")\
                .select("*")\
                .eq("profile_id", profile_id)\
                .eq("snapshot_type", snapshot_type)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            return [self._row_to_snapshot(row) for row in result.data or []]
        except Exception as e:
            logger.error(f"Failed to get snapshots by type: {e}")
            return []

    async def get_archetype_history(
        self,
        profile_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get history of archetype changes.
        
        Returns list of archetype changes with timestamps.
        """
        if not self.supabase:
            return []

        try:
            result = await self.supabase.table("profile_snapshots")\
                .select("archetype, archetype_confidence, created_at")\
                .eq("profile_id", profile_id)\
                .not_.is_("archetype", "null")\
                .order("created_at", desc=True)\
                .execute()

            history = []
            seen_archetypes = set()
            
            for row in result.data or []:
                archetype = row.get("archetype")
                if archetype and archetype not in seen_archetypes:
                    history.append({
                        "archetype": archetype,
                        "confidence": row.get("archetype_confidence"),
                        "date": row.get("created_at"),
                    })
                    seen_archetypes.add(archetype)

            return history
        except Exception as e:
            logger.error(f"Failed to get archetype history: {e}")
            return []

    async def calculate_score_trends(
        self,
        profile_id: str,
        days: int = 90,
    ) -> Dict[str, Any]:
        """
        Calculate score trends over time.
        
        Returns trends for CRI, EDS, and Spike scores.
        """
        if not self.supabase:
            return {}

        try:
            result = await self.supabase.rpc(
                "get_profile_evolution",
                {
                    "target_profile_id": profile_id,
                    "lookback_days": days,
                }
            ).execute()

            if not result.data:
                return {}

            # Calculate trends
            scores = {
                "cri": [],
                "eds": [],
                "spike": [],
            }

            for row in result.data:
                if row.get("cri_score") is not None:
                    scores["cri"].append(row["cri_score"])
                if row.get("eds_score") is not None:
                    scores["eds"].append(row["eds_score"])
                if row.get("spike_score") is not None:
                    scores["spike"].append(row["spike_score"])

            trends = {}
            for score_type, values in scores.items():
                if len(values) >= 2:
                    trends[score_type] = {
                        "current": values[0],
                        "previous": values[-1],
                        "change": values[0] - values[-1],
                        "trend": "up" if values[0] > values[-1] else "down" if values[0] < values[-1] else "stable",
                    }

            return trends
        except Exception as e:
            logger.error(f"Failed to calculate score trends: {e}")
            return {}

    def _row_to_snapshot(self, row: Dict[str, Any]) -> ProfileSnapshot:
        """Convert database row to ProfileSnapshot."""
        created_at = row.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        return ProfileSnapshot(
            profile_id=row["profile_id"],
            snapshot_type=row["snapshot_type"],
            narrative_dna=row.get("narrative_dna"),
            brand_statement=row.get("brand_statement"),
            archetype=row.get("archetype"),
            archetype_confidence=row.get("archetype_confidence"),
            cri_score=row.get("cri_score"),
            eds_score=row.get("eds_score"),
            spike_score=row.get("spike_score"),
            activities_count=row.get("activities_count", 0),
            projects_count=row.get("projects_count", 0),
            awards_count=row.get("awards_count", 0),
            change_summary=row.get("change_summary"),
            changed_fields=row.get("changed_fields"),
            trigger_event=row.get("trigger_event"),
            created_at=created_at,
        )
