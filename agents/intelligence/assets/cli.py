#!/usr/bin/env python3
"""
Asset CLI - Command-line interface for coaching asset operations.

Commands:
- validate: Validate a YAML file against the schema
- load: Load assets from a file and optionally seed to database
- list: List available coach asset libraries
- summary: Show summary of assets in a file
- seed: Seed all assets from a coach to the database

Usage:
    python -m intelligence.assets.cli validate path/to/file.yaml
    python -m intelligence.assets.cli load jenny_duan --dry-run
    python -m intelligence.assets.cli seed jenny_duan --overwrite
    python -m intelligence.assets.cli list
    python -m intelligence.assets.cli summary jenny_duan
"""

import argparse
import asyncio
import sys
import json
from pathlib import Path
from typing import Optional

from .loader import (
    AssetLoader,
    AssetLoadError,
    AssetValidationError,
    load_coach_assets,
    list_available_coaches,
    validate_asset_file,
    DATA_PATH,
)


def cmd_validate(args):
    """Validate a YAML file against the schema."""
    yaml_path = Path(args.file)

    if not yaml_path.exists():
        print(f"Error: File not found: {yaml_path}")
        return 1

    print(f"Validating: {yaml_path}")

    is_valid, errors = validate_asset_file(yaml_path)

    if is_valid:
        print("Validation PASSED")
        return 0
    else:
        print("Validation FAILED")
        print("\nErrors:")
        for error in errors[:20]:  # Limit to first 20 errors
            print(f"  - {error}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors")
        return 1


def cmd_load(args):
    """Load assets from a file or coach directory."""
    coach_id = args.coach_id

    print(f"Loading assets for coach: {coach_id}")

    assets = load_coach_assets(coach_id, validate=not args.skip_validation)

    if not assets:
        print("No assets loaded.")
        return 1

    print(f"Loaded {len(assets)} assets")

    # Show summary
    loader = AssetLoader()
    summary = loader.get_asset_summary(assets)

    print("\nSummary:")
    print(f"  Total: {summary['total']}")
    print(f"  By Type: {dict(summary['by_type'])}")
    print(f"  By Domain: {dict(summary['by_domain'])}")

    if args.verbose:
        print("\nAssets:")
        for asset in assets:
            print(f"  - {asset.name} ({asset.asset_type}, {asset.domain})")

    # Seed if requested
    if args.seed:
        return asyncio.run(_seed_assets(assets, args.dry_run, args.overwrite))

    return 0


async def _seed_assets(assets, dry_run: bool, overwrite: bool):
    """Seed assets to database."""
    from tools.database import get_supabase_client
    from ..registry import AssetRegistry

    try:
        client = get_supabase_client()
        registry = AssetRegistry(client)

        loader = AssetLoader()
        summary = await loader.seed_to_database(
            registry,
            assets,
            overwrite=overwrite,
            dry_run=dry_run,
        )

        print("\nSeed Results:")
        print(f"  Created: {summary['created']}")
        print(f"  Updated: {summary['updated']}")
        print(f"  Skipped: {summary['skipped']}")
        print(f"  Errors: {summary['errors']}")
        if dry_run:
            print("  (DRY RUN - no changes made)")

        return 0 if summary['errors'] == 0 else 1

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_list(args):
    """List available coach asset libraries."""
    coaches = list_available_coaches()

    if not coaches:
        print("No coach asset libraries found.")
        print(f"Add YAML files to: {DATA_PATH}")
        return 0

    print("Available coach asset libraries:")
    for coach in coaches:
        coach_dir = DATA_PATH / coach
        yaml_files = list(coach_dir.glob("**/*.yaml"))
        print(f"  - {coach} ({len(yaml_files)} YAML files)")

    return 0


def cmd_summary(args):
    """Show summary of assets for a coach."""
    coach_id = args.coach_id

    assets = load_coach_assets(coach_id, validate=False)

    if not assets:
        print(f"No assets found for coach: {coach_id}")
        return 1

    loader = AssetLoader()
    summary = loader.get_asset_summary(assets)

    print(f"\nAsset Summary for {coach_id}")
    print("=" * 40)
    print(f"Total Assets: {summary['total']}")

    print("\nBy Type:")
    for type_key, count in sorted(summary['by_type'].items()):
        print(f"  {type_key}: {count}")

    print("\nBy Domain:")
    for domain_key, count in sorted(summary['by_domain'].items()):
        print(f"  {domain_key}: {count}")

    print("\nTop Tags:")
    for tag, count in summary['top_tags'][:15]:
        print(f"  {tag}: {count}")

    if args.json:
        print("\nJSON Output:")
        print(json.dumps(summary, indent=2, default=str))

    return 0


def cmd_seed(args):
    """Seed all assets from a coach to the database."""
    coach_id = args.coach_id

    print(f"Seeding assets for coach: {coach_id}")

    assets = load_coach_assets(coach_id, validate=not args.skip_validation)

    if not assets:
        print("No assets to seed.")
        return 1

    print(f"Found {len(assets)} assets to seed")

    return asyncio.run(_seed_assets(assets, args.dry_run, args.overwrite))


def cmd_export(args):
    """Export assets to JSON format."""
    coach_id = args.coach_id
    output_path = Path(args.output) if args.output else None

    assets = load_coach_assets(coach_id, validate=False)

    if not assets:
        print(f"No assets found for coach: {coach_id}")
        return 1

    # Convert to dict format
    export_data = {
        "coach_id": coach_id,
        "exported_at": str(asyncio.get_event_loop().time()),
        "total": len(assets),
        "assets": [asset.to_db_dict() for asset in assets],
    }

    json_output = json.dumps(export_data, indent=2, default=str)

    if output_path:
        with open(output_path, "w") as f:
            f.write(json_output)
        print(f"Exported {len(assets)} assets to {output_path}")
    else:
        print(json_output)

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Coaching Asset CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a YAML file")
    validate_parser.add_argument("file", help="Path to YAML file")

    # load command
    load_parser = subparsers.add_parser("load", help="Load assets from coach directory")
    load_parser.add_argument("coach_id", help="Coach identifier (e.g., jenny_duan)")
    load_parser.add_argument("--seed", action="store_true", help="Seed to database")
    load_parser.add_argument("--dry-run", action="store_true", help="Dry run (no database writes)")
    load_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing assets")
    load_parser.add_argument("--skip-validation", action="store_true", help="Skip schema validation")
    load_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # list command
    list_parser = subparsers.add_parser("list", help="List available coach libraries")

    # summary command
    summary_parser = subparsers.add_parser("summary", help="Show asset summary")
    summary_parser.add_argument("coach_id", help="Coach identifier")
    summary_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # seed command
    seed_parser = subparsers.add_parser("seed", help="Seed assets to database")
    seed_parser.add_argument("coach_id", help="Coach identifier")
    seed_parser.add_argument("--dry-run", action="store_true", help="Dry run (no database writes)")
    seed_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing assets")
    seed_parser.add_argument("--skip-validation", action="store_true", help="Skip schema validation")

    # export command
    export_parser = subparsers.add_parser("export", help="Export assets to JSON")
    export_parser.add_argument("coach_id", help="Coach identifier")
    export_parser.add_argument("-o", "--output", help="Output file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Dispatch to command handler
    commands = {
        "validate": cmd_validate,
        "load": cmd_load,
        "list": cmd_list,
        "summary": cmd_summary,
        "seed": cmd_seed,
        "export": cmd_export,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
