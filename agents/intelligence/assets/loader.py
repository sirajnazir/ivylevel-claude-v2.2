"""
Asset Loader - Data-driven loading of coaching assets from YAML files.

Provides:
- YAML file loading and validation
- Schema validation using JSON Schema
- Conversion to CoachingAsset objects
- Batch loading and seeding to database
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import yaml

# Optional jsonschema import for validation
try:
    from jsonschema import validate, ValidationError, Draft202012Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    validate = None
    ValidationError = Exception
    Draft202012Validator = None

from ..primitives import (
    CoachingAsset,
    AssetType,
    AssetDomain,
    TriggerCondition,
    Applicability,
    Provenance,
    Effectiveness,
)
from ..registry import AssetRegistry

logger = logging.getLogger(__name__)

# Path to schema file
SCHEMA_PATH = Path(__file__).parent / "schemas" / "coaching_asset_schema.json"

# Path to data directory
DATA_PATH = Path(__file__).parent / "data"


class AssetLoadError(Exception):
    """Error during asset loading."""
    pass


class AssetValidationError(Exception):
    """Error during asset validation."""
    pass


class AssetLoader:
    """
    Loads coaching assets from YAML files.

    Features:
    - Schema validation
    - Conversion to CoachingAsset objects
    - Batch database seeding
    - Dry-run mode for testing
    """

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize the loader.

        Args:
            schema_path: Path to JSON schema file (uses default if not provided)
        """
        self.schema_path = schema_path or SCHEMA_PATH
        self._schema = None
        self._validator = None

    @property
    def schema(self) -> Dict[str, Any]:
        """Lazy-load and cache the schema."""
        if self._schema is None:
            with open(self.schema_path) as f:
                self._schema = json.load(f)
        return self._schema

    @property
    def validator(self):
        """Get JSON Schema validator (returns None if jsonschema not available)."""
        if not JSONSCHEMA_AVAILABLE:
            return None
        if self._validator is None:
            self._validator = Draft202012Validator(self.schema)
        return self._validator

    def load_yaml(self, yaml_path: Path) -> Dict[str, Any]:
        """
        Load a YAML file.

        Args:
            yaml_path: Path to YAML file

        Returns:
            Parsed YAML content

        Raises:
            AssetLoadError: If file cannot be loaded
        """
        try:
            with open(yaml_path) as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise AssetLoadError(f"Invalid YAML in {yaml_path}: {e}")
        except FileNotFoundError:
            raise AssetLoadError(f"File not found: {yaml_path}")

    def validate_yaml(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate YAML data against schema.

        Args:
            data: Parsed YAML data

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        if not JSONSCHEMA_AVAILABLE:
            # Skip validation if jsonschema not available, do basic checks
            logger.warning("jsonschema not installed, skipping full validation")
            if not isinstance(data, dict):
                return False, ["Data must be a dictionary"]
            if "metadata" not in data:
                return False, ["Missing required field: metadata"]
            if "techniques" not in data:
                return False, ["Missing required field: techniques"]
            return True, []

        errors = []
        try:
            validate(instance=data, schema=self.schema)
            return True, []
        except ValidationError:
            # Collect all validation errors
            for error in self.validator.iter_errors(data):
                path = ".".join(str(p) for p in error.absolute_path)
                errors.append(f"{path}: {error.message}")
            return False, errors

    def convert_technique_to_asset(
        self,
        technique: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> CoachingAsset:
        """
        Convert a technique dict from YAML to a CoachingAsset.

        Args:
            technique: Technique dictionary from YAML
            metadata: Library metadata (coach info, version)

        Returns:
            CoachingAsset instance
        """
        # Map domain strings to enum
        domain_map = {
            "assessment": AssetDomain.ASSESSMENT,
            "execution": AssetDomain.EXECUTION,
            "awards": AssetDomain.AWARDS,
            "programs": AssetDomain.PROGRAMS,
            "essays": AssetDomain.ESSAYS,
            "activities": AssetDomain.ACTIVITIES,
            "emotional": AssetDomain.EMOTIONAL,
            "strategy": AssetDomain.STRATEGY,
            "general": AssetDomain.GENERAL,
            # Extended domains map to closest match
            "time_management": AssetDomain.EXECUTION,
            "relationships": AssetDomain.GENERAL,
            "coaching": AssetDomain.GENERAL,
            "crisis": AssetDomain.EMOTIONAL,
            "motivation": AssetDomain.EMOTIONAL,
            "content_optimization": AssetDomain.ESSAYS,
            "positioning": AssetDomain.STRATEGY,
            "emotional_calibration": AssetDomain.EMOTIONAL,
            "decision_making": AssetDomain.STRATEGY,
            "opportunities": AssetDomain.PROGRAMS,
            "research": AssetDomain.GENERAL,
        }

        # Map asset type strings to enum
        type_map = {
            "technique": AssetType.TECHNIQUE,
            "framework": AssetType.FRAMEWORK,
            "protocol": AssetType.TECHNIQUE,  # Protocol is a specialized technique
            "strategy": AssetType.TECHNIQUE,
            "principle": AssetType.REFERENCE,
            "rule": AssetType.REFERENCE,
            "template": AssetType.TEMPLATE,
            "reference": AssetType.REFERENCE,
            "checklist": AssetType.CHECKLIST,
            "prompt": AssetType.PROMPT,
            "example": AssetType.EXAMPLE,
        }

        # Extract trigger configuration
        trigger_data = technique.get("trigger", {})
        trigger_config = TriggerCondition(
            event_types=trigger_data.get("events", []) + trigger_data.get("situations", []),
            lifecycle_stages=trigger_data.get("lifecycle_stages", []),
            emotional_states=trigger_data.get("student_states", []),
            custom_conditions={
                "keywords": trigger_data.get("keywords", []),
                "phrases": trigger_data.get("phrases", []),
            },
        )

        # Extract applicability
        app_data = technique.get("applicability", {})
        applicability = Applicability(
            grade_levels=app_data.get("grade_levels", [9, 10, 11, 12]),
            archetypes=app_data.get("archetypes", []),
            exclude_conditions=app_data.get("contraindications", []),
        )

        # Extract effectiveness benchmarks
        eff_data = technique.get("effectiveness", {})
        effectiveness = Effectiveness(
            global_success_rate=eff_data.get("success_rate_benchmark", 0.0),
            confidence_level=eff_data.get("confidence_score", 0.0),
        )

        # Build provenance
        provenance = Provenance(
            source=metadata.get("coach_id", "unknown"),
            author=metadata.get("coach_name", "Unknown"),
            version_notes=f"v{metadata.get('version', '1.0')} - {technique.get('id', 'unknown')}",
        )

        # Build content dict
        content = technique.get("content", {})
        content["technique_id"] = technique.get("id", "")
        content["category"] = technique.get("category", "")

        # Map domain
        domain_str = technique.get("domain", "general")
        domain = domain_map.get(domain_str, AssetDomain.GENERAL)

        # Map secondary domains
        secondary = []
        for sec_domain in technique.get("secondary_domains", []):
            if sec_domain in domain_map:
                mapped = domain_map[sec_domain]
                if mapped != domain:  # Don't duplicate primary
                    secondary.append(mapped)

        # Map asset type
        type_str = technique.get("asset_type", "technique")
        asset_type = type_map.get(type_str, AssetType.TECHNIQUE)

        # Build tags - include original domain if it was mapped
        tags = list(technique.get("tags", []))
        if domain_str not in [d.value for d in AssetDomain]:
            tags.append(domain_str)  # Preserve original domain as tag
        tags.append(metadata.get("coach_id", ""))  # Add coach ID as tag

        return CoachingAsset(
            name=technique.get("name", "Unnamed Technique"),
            asset_type=asset_type,
            domain=domain,
            secondary_domains=secondary,
            tags=tags,
            content=content,
            trigger_config=trigger_config,
            applicability=applicability,
            provenance=provenance,
            effectiveness=effectiveness,
        )

    def load_file(
        self,
        yaml_path: Path,
        validate_schema: bool = True,
    ) -> Tuple[List[CoachingAsset], Dict[str, Any]]:
        """
        Load a YAML file and convert to CoachingAssets.

        Args:
            yaml_path: Path to YAML file
            validate_schema: Whether to validate against schema

        Returns:
            Tuple of (list of CoachingAssets, metadata dict)

        Raises:
            AssetLoadError: If file cannot be loaded
            AssetValidationError: If validation fails
        """
        # Load YAML
        data = self.load_yaml(yaml_path)

        # Validate if requested
        if validate_schema:
            is_valid, errors = self.validate_yaml(data)
            if not is_valid:
                raise AssetValidationError(
                    f"Validation failed for {yaml_path}:\n" + "\n".join(errors[:10])
                )

        # Extract metadata
        metadata = data.get("metadata", {})

        # Convert techniques
        assets = []
        techniques = data.get("techniques", [])

        for technique in techniques:
            try:
                asset = self.convert_technique_to_asset(technique, metadata)
                assets.append(asset)
            except Exception as e:
                logger.warning(f"Failed to convert technique {technique.get('id', 'unknown')}: {e}")

        logger.info(f"Loaded {len(assets)} assets from {yaml_path}")

        return assets, metadata

    def load_directory(
        self,
        directory: Path,
        recursive: bool = True,
        validate_schema: bool = True,
    ) -> Dict[str, List[CoachingAsset]]:
        """
        Load all YAML files from a directory.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories
            validate_schema: Whether to validate against schema

        Returns:
            Dict mapping file paths to lists of assets
        """
        results = {}

        pattern = "**/*.yaml" if recursive else "*.yaml"

        for yaml_file in directory.glob(pattern):
            try:
                assets, _ = self.load_file(yaml_file, validate_schema)
                results[str(yaml_file)] = assets
            except (AssetLoadError, AssetValidationError) as e:
                logger.error(f"Error loading {yaml_file}: {e}")
                results[str(yaml_file)] = []

        return results

    async def seed_to_database(
        self,
        registry: AssetRegistry,
        assets: List[CoachingAsset],
        overwrite: bool = False,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Seed assets to the database.

        Args:
            registry: AssetRegistry instance
            assets: List of assets to seed
            overwrite: Whether to update existing assets
            dry_run: If True, don't actually write to database

        Returns:
            Summary dict with counts
        """
        summary = {
            "total": len(assets),
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "dry_run": dry_run,
        }

        for asset in assets:
            try:
                # Check if exists
                existing = await registry.get_by_name(asset.name)

                if existing:
                    if overwrite:
                        if not dry_run:
                            asset.id = existing.id
                            asset.version = existing.version + 1
                            await registry.update(asset)
                        summary["updated"] += 1
                        logger.debug(f"Updated: {asset.name}")
                    else:
                        summary["skipped"] += 1
                        logger.debug(f"Skipped existing: {asset.name}")
                else:
                    if not dry_run:
                        await registry.create(asset)
                    summary["created"] += 1
                    logger.debug(f"Created: {asset.name}")

            except Exception as e:
                summary["errors"] += 1
                logger.error(f"Error seeding {asset.name}: {e}")

        logger.info(
            f"Seed complete: {summary['created']} created, "
            f"{summary['updated']} updated, {summary['skipped']} skipped, "
            f"{summary['errors']} errors"
        )

        return summary

    def get_asset_summary(
        self,
        assets: List[CoachingAsset],
    ) -> Dict[str, Any]:
        """
        Get a summary of loaded assets.

        Args:
            assets: List of assets

        Returns:
            Summary dict
        """
        by_type = {}
        by_domain = {}
        by_tag = {}

        for asset in assets:
            # Count by type
            type_key = asset.asset_type
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # Count by domain
            domain_key = asset.domain
            by_domain[domain_key] = by_domain.get(domain_key, 0) + 1

            # Count by tag
            for tag in asset.tags:
                by_tag[tag] = by_tag.get(tag, 0) + 1

        return {
            "total": len(assets),
            "by_type": by_type,
            "by_domain": by_domain,
            "top_tags": sorted(by_tag.items(), key=lambda x: x[1], reverse=True)[:20],
        }


# Convenience functions

def load_coach_assets(
    coach_id: str,
    validate: bool = True,
) -> List[CoachingAsset]:
    """
    Load all assets for a specific coach.

    Args:
        coach_id: Coach identifier (e.g., "jenny_duan")
        validate: Whether to validate against schema

    Returns:
        List of CoachingAssets
    """
    coach_dir = DATA_PATH / coach_id

    if not coach_dir.exists():
        logger.warning(f"Coach directory not found: {coach_dir}")
        return []

    loader = AssetLoader()
    all_assets = []

    results = loader.load_directory(coach_dir, validate_schema=validate)

    for file_path, assets in results.items():
        all_assets.extend(assets)

    return all_assets


def list_available_coaches() -> List[str]:
    """List all available coach asset libraries."""
    if not DATA_PATH.exists():
        return []

    return [
        d.name for d in DATA_PATH.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]


def validate_asset_file(yaml_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate a YAML asset file against the schema.

    Args:
        yaml_path: Path to YAML file

    Returns:
        Tuple of (is_valid, list of errors)
    """
    loader = AssetLoader()

    try:
        data = loader.load_yaml(yaml_path)
        return loader.validate_yaml(data)
    except AssetLoadError as e:
        return False, [str(e)]
