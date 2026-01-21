"""
Jenny Duan Coaching Assets - Proven techniques from master coach Jenny Duan.

Provides:
- JENNY_TECHNIQUES: List of all coaching assets
- seed_jenny_assets: Function to seed assets to database
- JENNY_ASSET_NAMES: Quick reference for asset names
"""

from .techniques import JENNY_TECHNIQUES, create_jenny_techniques
from .seed import seed_jenny_assets, get_jenny_asset_names, get_jenny_asset_by_name, JENNY_ASSET_NAMES

__all__ = [
    "JENNY_TECHNIQUES",
    "create_jenny_techniques",
    "seed_jenny_assets",
    "get_jenny_asset_names",
    "get_jenny_asset_by_name",
    "JENNY_ASSET_NAMES",
]
