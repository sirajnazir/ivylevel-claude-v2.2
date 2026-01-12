"""
IvyQuest v10.0 - Golden Dataset Loader
======================================

Load and manage golden evaluation examples from the database.
Golden examples are benchmark cases from Jenny Duan's coaching.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import structlog

logger = structlog.get_logger()


@dataclass
class GoldenExample:
    """A single golden evaluation example."""
    id: str
    profile_id: str
    input_profile: Dict[str, Any]
    expected_outputs: Dict[str, Any]
    jenny_annotations: Dict[str, Any]
    difficulty_tier: str  # easy, medium, hard
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'input_profile': self.input_profile,
            'expected_outputs': self.expected_outputs,
            'jenny_annotations': self.jenny_annotations,
            'difficulty_tier': self.difficulty_tier,
            'tags': self.tags,
        }


class GoldenDatasetLoader:
    """Load and manage golden evaluation examples."""

    def __init__(self, db_client):
        """
        Initialize loader with database client.

        Args:
            db_client: Supabase client instance
        """
        self.db = db_client
        self.logger = logger.bind(component='golden_loader')

    async def load_all(self) -> List[GoldenExample]:
        """
        Load all golden examples.

        Returns:
            List of all golden examples
        """
        try:
            result = self.db.table('evaluation_golden').select('*').execute()
            examples = [self._to_example(row) for row in (result.data or [])]
            self.logger.info("loaded_all_golden", count=len(examples))
            return examples
        except Exception as e:
            self.logger.error("load_all_error", error=str(e))
            return []

    async def load_by_tags(self, tags: List[str]) -> List[GoldenExample]:
        """
        Load golden examples matching any of the tags.

        Args:
            tags: List of tags to filter by

        Returns:
            List of matching golden examples
        """
        try:
            result = self.db.table('evaluation_golden').select('*').execute()
            examples = []
            for row in (result.data or []):
                row_tags = row.get('tags', [])
                if any(tag in row_tags for tag in tags):
                    examples.append(self._to_example(row))

            self.logger.info("loaded_by_tags", tags=tags, count=len(examples))
            return examples
        except Exception as e:
            self.logger.error("load_by_tags_error", tags=tags, error=str(e))
            return []

    async def load_by_difficulty(self, tier: str) -> List[GoldenExample]:
        """
        Load golden examples by difficulty tier.

        Args:
            tier: Difficulty tier (easy, medium, hard)

        Returns:
            List of matching golden examples
        """
        try:
            result = self.db.table('evaluation_golden').select('*').eq(
                'difficulty_tier', tier
            ).execute()
            examples = [self._to_example(row) for row in (result.data or [])]
            self.logger.info("loaded_by_difficulty", tier=tier, count=len(examples))
            return examples
        except Exception as e:
            self.logger.error("load_by_difficulty_error", tier=tier, error=str(e))
            return []

    async def get_by_id(self, golden_id: str) -> Optional[GoldenExample]:
        """
        Get a single golden example by ID.

        Args:
            golden_id: The golden example UUID

        Returns:
            GoldenExample or None if not found
        """
        try:
            result = self.db.table('evaluation_golden').select('*').eq(
                'id', golden_id
            ).maybe_single().execute()

            if result.data:
                return self._to_example(result.data)
            return None
        except Exception as e:
            self.logger.error("get_by_id_error", golden_id=golden_id, error=str(e))
            return None

    async def get_by_profile_id(self, profile_id: str) -> Optional[GoldenExample]:
        """
        Get a golden example by profile ID.

        Args:
            profile_id: The profile identifier

        Returns:
            GoldenExample or None if not found
        """
        try:
            result = self.db.table('evaluation_golden').select('*').eq(
                'profile_id', profile_id
            ).maybe_single().execute()

            if result.data:
                return self._to_example(result.data)
            return None
        except Exception as e:
            self.logger.error("get_by_profile_id_error", profile_id=profile_id, error=str(e))
            return None

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the golden dataset.

        Returns:
            Dict with counts by difficulty and tags
        """
        try:
            result = self.db.table('evaluation_golden').select('*').execute()
            data = result.data or []

            # Count by difficulty
            difficulty_counts = {'easy': 0, 'medium': 0, 'hard': 0}
            tag_counts: Dict[str, int] = {}

            for row in data:
                tier = row.get('difficulty_tier', 'medium')
                if tier in difficulty_counts:
                    difficulty_counts[tier] += 1

                for tag in row.get('tags', []):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

            return {
                'total': len(data),
                'by_difficulty': difficulty_counts,
                'by_tag': tag_counts,
            }
        except Exception as e:
            self.logger.error("get_stats_error", error=str(e))
            return {'total': 0, 'by_difficulty': {}, 'by_tag': {}}

    def _to_example(self, row: Dict[str, Any]) -> GoldenExample:
        """
        Convert database row to GoldenExample.

        Args:
            row: Database row dict

        Returns:
            GoldenExample instance
        """
        return GoldenExample(
            id=row['id'],
            profile_id=row['profile_id'],
            input_profile=row.get('input_profile', {}),
            expected_outputs=row.get('expected_outputs', {}),
            jenny_annotations=row.get('jenny_annotations', {}),
            difficulty_tier=row.get('difficulty_tier', 'medium'),
            tags=row.get('tags', [])
        )
