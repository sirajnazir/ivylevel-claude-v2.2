"""
Intelligence Assets - Pre-built coaching assets from expert coaches.

Submodules:
- jenny_duan: Hardcoded techniques from master coach Jenny Duan
- loader: Data-driven YAML asset loader
- cli: Command-line interface for asset operations
"""

from .jenny_duan import (
    JENNY_TECHNIQUES,
    seed_jenny_assets,
    JENNY_ASSET_NAMES,
    get_jenny_asset_by_name,
)

from .loader import (
    AssetLoader,
    AssetLoadError,
    AssetValidationError,
    load_coach_assets,
    list_available_coaches,
    validate_asset_file,
    DATA_PATH,
)

__all__ = [
    # Hardcoded assets
    "JENNY_TECHNIQUES",
    "seed_jenny_assets",
    "JENNY_ASSET_NAMES",
    "get_jenny_asset_by_name",
    # Data-driven loader
    "AssetLoader",
    "AssetLoadError",
    "AssetValidationError",
    "load_coach_assets",
    "list_available_coaches",
    "validate_asset_file",
    "DATA_PATH",
]
