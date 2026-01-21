"""
AssetRegistry - CRUD operations for coaching assets with vector search.

Provides:
- Create, read, update, delete operations for coaching assets
- Vector similarity search using pgvector
- Batch operations for seeding assets
- Effectiveness tracking updates
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

from ..primitives import CoachingAsset, AssetType, AssetDomain

logger = logging.getLogger(__name__)


class AssetRegistry:
    """
    Registry for managing coaching assets in the database.

    Uses Supabase for storage and pgvector for semantic search.
    """

    def __init__(self, supabase_client):
        """
        Initialize the registry with a Supabase client.

        Args:
            supabase_client: Initialized Supabase client
        """
        self.db = supabase_client
        self.table = "coaching_assets"
        self.usage_table = "asset_usage"

    async def create(self, asset: CoachingAsset) -> CoachingAsset:
        """Create a new coaching asset."""
        try:
            data = asset.to_db_dict()
            result = self.db.table(self.table).insert(data).execute()

            if result.data:
                logger.info(f"Created coaching asset: {asset.name} (id={asset.id})")
                return CoachingAsset.from_db_row(result.data[0])
            else:
                raise Exception("Failed to create asset - no data returned")

        except Exception as e:
            logger.error(f"Failed to create coaching asset: {e}")
            raise

    async def get(self, asset_id: UUID) -> Optional[CoachingAsset]:
        """Get a coaching asset by ID."""
        try:
            result = self.db.table(self.table).select("*").eq("id", str(asset_id)).single().execute()

            if result.data:
                return CoachingAsset.from_db_row(result.data)
            return None

        except Exception as e:
            logger.warning(f"Failed to get coaching asset {asset_id}: {e}")
            return None

    async def get_by_name(self, name: str) -> Optional[CoachingAsset]:
        """Get a coaching asset by name."""
        try:
            result = self.db.table(self.table).select("*").eq("name", name).eq("is_active", True).single().execute()

            if result.data:
                return CoachingAsset.from_db_row(result.data)
            return None

        except Exception as e:
            logger.warning(f"Failed to get coaching asset by name {name}: {e}")
            return None

    async def update(self, asset: CoachingAsset) -> CoachingAsset:
        """Update an existing coaching asset."""
        try:
            asset.updated_at = datetime.utcnow()
            data = asset.to_db_dict()

            result = self.db.table(self.table).update(data).eq("id", str(asset.id)).execute()

            if result.data:
                logger.info(f"Updated coaching asset: {asset.name}")
                return CoachingAsset.from_db_row(result.data[0])
            else:
                raise Exception("Failed to update asset - no data returned")

        except Exception as e:
            logger.error(f"Failed to update coaching asset: {e}")
            raise

    async def delete(self, asset_id: UUID, soft: bool = True) -> bool:
        """
        Delete a coaching asset.

        Args:
            asset_id: The asset ID to delete
            soft: If True, just set is_active=False. If False, hard delete.
        """
        try:
            if soft:
                result = self.db.table(self.table).update({"is_active": False, "updated_at": datetime.utcnow().isoformat()}).eq("id", str(asset_id)).execute()
            else:
                result = self.db.table(self.table).delete().eq("id", str(asset_id)).execute()

            logger.info(f"Deleted coaching asset: {asset_id} (soft={soft})")
            return True

        except Exception as e:
            logger.error(f"Failed to delete coaching asset {asset_id}: {e}")
            return False

    async def list_by_type(
        self,
        asset_type: AssetType,
        domain: Optional[AssetDomain] = None,
        limit: int = 50,
    ) -> List[CoachingAsset]:
        """List assets by type and optionally domain."""
        try:
            query = self.db.table(self.table).select("*").eq("asset_type", asset_type).eq("is_active", True)

            if domain:
                query = query.eq("domain", domain)

            result = query.limit(limit).execute()

            return [CoachingAsset.from_db_row(row) for row in result.data] if result.data else []

        except Exception as e:
            logger.error(f"Failed to list assets by type: {e}")
            return []

    async def list_by_domain(
        self,
        domain: AssetDomain,
        include_secondary: bool = True,
        limit: int = 50,
    ) -> List[CoachingAsset]:
        """List assets by domain."""
        try:
            # Primary domain - use domain.value to get string representation
            query = self.db.table(self.table).select("*").eq("domain", domain.value).eq("is_active", True)
            result = query.limit(limit).execute()

            assets = [CoachingAsset.from_db_row(row) for row in result.data] if result.data else []

            # Include secondary domains if requested
            if include_secondary:
                query2 = self.db.table(self.table).select("*").contains("secondary_domains", [domain.value]).eq("is_active", True)
                result2 = query2.limit(limit).execute()

                if result2.data:
                    existing_ids = {a.id for a in assets}
                    for row in result2.data:
                        asset = CoachingAsset.from_db_row(row)
                        if asset.id not in existing_ids:
                            assets.append(asset)

            return assets[:limit]

        except Exception as e:
            logger.error(f"Failed to list assets by domain: {e}")
            return []

    async def list_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        limit: int = 50,
    ) -> List[CoachingAsset]:
        """List assets by tags."""
        try:
            if match_all:
                # Must have all tags
                query = self.db.table(self.table).select("*").contains("tags", tags).eq("is_active", True)
            else:
                # Must have any of the tags (overlap)
                query = self.db.table(self.table).select("*").overlaps("tags", tags).eq("is_active", True)

            result = query.limit(limit).execute()

            return [CoachingAsset.from_db_row(row) for row in result.data] if result.data else []

        except Exception as e:
            logger.error(f"Failed to list assets by tags: {e}")
            return []

    async def search_semantic(
        self,
        query_embedding: List[float],
        match_threshold: float = 0.5,
        match_count: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search assets using vector similarity.

        Uses the match_coaching_assets function defined in the database.
        """
        try:
            result = self.db.rpc(
                "match_coaching_assets",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": match_threshold,
                    "match_count": match_count,
                },
            ).execute()

            if result.data:
                return [
                    {
                        "asset": CoachingAsset.from_db_row(row),
                        "similarity": row.get("similarity", 0),
                    }
                    for row in result.data
                ]
            return []

        except Exception as e:
            logger.error(f"Failed to search assets semantically: {e}")
            return []

    async def record_usage(
        self,
        asset_id: UUID,
        profile_id: UUID,
        agent_name: str,
        trigger_context: Optional[str] = None,
        lifecycle_stage: Optional[str] = None,
        outcome: Optional[Dict[str, Any]] = None,
        student_archetype: Optional[str] = None,
        student_phase: Optional[str] = None,
    ) -> bool:
        """Record usage of an asset for effectiveness tracking."""
        try:
            data = {
                "asset_id": str(asset_id),
                "profile_id": str(profile_id),
                "agent_name": agent_name,
                "trigger_context": trigger_context,
                "lifecycle_stage": lifecycle_stage,
                "outcome": outcome,
                "student_archetype": student_archetype,
                "student_phase": student_phase,
            }

            self.db.table(self.usage_table).insert(data).execute()
            logger.info(f"Recorded usage of asset {asset_id} for profile {profile_id}")

            # Note: The database trigger (update_asset_effectiveness) will
            # automatically update the asset's effectiveness stats
            return True

        except Exception as e:
            logger.error(f"Failed to record asset usage: {e}")
            return False

    async def get_top_effective(
        self,
        domain: Optional[AssetDomain] = None,
        asset_type: Optional[AssetType] = None,
        archetype: Optional[str] = None,
        min_usage: int = 5,
        limit: int = 10,
    ) -> List[CoachingAsset]:
        """Get the most effective assets based on tracked outcomes."""
        try:
            query = self.db.table(self.table).select("*").eq("is_active", True).gte("effectiveness->times_used", min_usage)

            if domain:
                query = query.eq("domain", domain)
            if asset_type:
                query = query.eq("asset_type", asset_type)

            # Order by global success rate
            result = query.order("effectiveness->global_success_rate", desc=True).limit(limit * 2).execute()

            assets = [CoachingAsset.from_db_row(row) for row in result.data] if result.data else []

            # If archetype specified, re-sort by archetype-specific effectiveness
            if archetype:
                assets.sort(
                    key=lambda a: a.get_effectiveness_for_archetype(archetype),
                    reverse=True,
                )

            return assets[:limit]

        except Exception as e:
            logger.error(f"Failed to get top effective assets: {e}")
            return []

    async def batch_create(self, assets: List[CoachingAsset]) -> int:
        """Create multiple assets in a batch."""
        try:
            data = [asset.to_db_dict() for asset in assets]
            result = self.db.table(self.table).insert(data).execute()

            count = len(result.data) if result.data else 0
            logger.info(f"Batch created {count} coaching assets")
            return count

        except Exception as e:
            logger.error(f"Failed to batch create assets: {e}")
            return 0

    async def set_embedding(
        self,
        asset_id: UUID,
        embedding: List[float],
    ) -> bool:
        """Set the embedding for an asset (for vector search)."""
        try:
            self.db.table(self.table).update({"embedding": embedding, "updated_at": datetime.utcnow().isoformat()}).eq("id", str(asset_id)).execute()

            logger.info(f"Set embedding for asset {asset_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to set embedding for asset {asset_id}: {e}")
            return False
