"""
Seed Jenny Duan's coaching assets into the database.

Run this once to populate the coaching_assets table with Jenny's techniques.
"""

import asyncio
import logging
from typing import List

from .techniques import JENNY_TECHNIQUES
from ...primitives import CoachingAsset
from ...registry import AssetRegistry

logger = logging.getLogger(__name__)


async def seed_jenny_assets(registry: AssetRegistry, overwrite: bool = False) -> int:
    """
    Seed Jenny Duan's coaching assets into the database.

    Args:
        registry: The asset registry to use
        overwrite: If True, update existing assets. If False, skip existing.

    Returns:
        Number of assets seeded
    """
    seeded_count = 0

    for asset in JENNY_TECHNIQUES:
        try:
            # Check if asset already exists
            existing = await registry.get_by_name(asset.name)

            if existing:
                if overwrite:
                    # Update the existing asset
                    asset.id = existing.id
                    asset.version = existing.version + 1
                    await registry.update(asset)
                    logger.info(f"Updated asset: {asset.name} (v{asset.version})")
                    seeded_count += 1
                else:
                    logger.info(f"Skipped existing asset: {asset.name}")
            else:
                # Create new asset
                await registry.create(asset)
                logger.info(f"Created asset: {asset.name}")
                seeded_count += 1

        except Exception as e:
            logger.error(f"Failed to seed asset '{asset.name}': {e}")

    return seeded_count


async def get_jenny_asset_names() -> List[str]:
    """Get the names of all Jenny Duan assets."""
    return [asset.name for asset in JENNY_TECHNIQUES]


def get_jenny_asset_by_name(name: str) -> CoachingAsset:
    """Get a specific Jenny asset by name (without database)."""
    for asset in JENNY_TECHNIQUES:
        if asset.name == name:
            return asset
    raise ValueError(f"Unknown Jenny asset: {name}")


# Quick reference for asset names
JENNY_ASSET_NAMES = {
    "time_buffer": "3x Time Buffer",
    "celebration": "Celebration Calibration",
    "silence": "Silence Detection",
    "crisis": "Crisis Alchemy Protocol",
    "overwhelm": "Strategic Overwhelm",
    "talk_first": "Talk-First-Write-Second",
    "huda": "Huda Benchmark",
}


if __name__ == "__main__":
    # For manual seeding from command line
    from tools.database import get_supabase_client

    async def main():
        client = get_supabase_client()
        registry = AssetRegistry(client)
        count = await seed_jenny_assets(registry, overwrite=False)
        print(f"Seeded {count} Jenny Duan coaching assets")

    asyncio.run(main())
