#!/usr/bin/env python3
"""
Strategic Intelligence Enrichment Script v1.0

Purpose: Enrich awards and programs data with strategic intelligence (IQ layer)
Author: IvyLevel Engineering
Date: January 2026

Usage:
    python enrich_strategic_intelligence.py --mode top20      # Start with top 20
    python enrich_strategic_intelligence.py --mode all        # Process all items
    python enrich_strategic_intelligence.py --mode remaining  # Continue from checkpoint
    python enrich_strategic_intelligence.py --mode single --id "ncwit-aic"  # Single item
    python enrich_strategic_intelligence.py --validate        # Validate enriched data

Prerequisites:
    - OPENAI_API_KEY environment variable set
    - awards_data.py and opportunities_data.py in agents/seeds/
"""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal
from dataclasses import dataclass, asdict
import hashlib

# ==============================================================================
# CONFIGURATION
# ==============================================================================

CONFIG = {
    "llm_model": "gpt-4o",
    "llm_temperature": 0.3,
    "batch_size": 5,
    "max_retries": 3,
    "checkpoint_frequency": 5,  # Save after every N items
    "output_dir": Path("agents/seeds/enriched"),
    "checkpoint_dir": Path(".enrichment_checkpoints"),
    "version": "1.0.0",
}

# Paths - adjust based on your project structure
PROJECT_ROOT = Path(__file__).parent.parent
SEEDS_DIR = PROJECT_ROOT / "agents" / "seeds"
DOCS_DIR = PROJECT_ROOT / "docs"

# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class ArchetypeFit:
    academic_powerhouse: float = 0.0
    stem_innovator: float = 0.0
    creative_visionary: float = 0.0
    community_changemaker: float = 0.0
    entrepreneurial_leader: float = 0.0
    humanities_scholar: float = 0.0
    athletic_scholar: float = 0.0
    multi_hyphenate: float = 0.0


@dataclass
class WinCascade:
    position: Literal["entry", "building", "capstone"]
    prerequisites: list[str]
    enables: list[str]


@dataclass
class Timing:
    ideal_grades: list[int]
    prep_weeks: int
    deadline_strategy: str = ""
    application_intensity: str = ""  # For programs


@dataclass
class Synergies:
    pairs_well_with: list[str]
    leads_to: list[str]


@dataclass
class AwardIntelligence:
    """Strategic intelligence for an award."""
    id: str
    strategic_tier: int
    strategic_tier_rationale: str
    strategic_notes: str
    success_patterns: list[str]
    common_mistakes: list[str]
    archetype_fit: dict
    win_cascade: dict
    timing: dict
    differentiation_factor: str
    enrichment_version: str = CONFIG["version"]
    enrichment_date: str = ""

    def __post_init__(self):
        if not self.enrichment_date:
            self.enrichment_date = datetime.now().isoformat()


@dataclass
class ProgramIntelligence:
    """Strategic intelligence for a program."""
    id: str
    strategic_tier: int
    strategic_tier_rationale: str
    strategic_notes: str
    success_patterns: list[str]
    common_mistakes: list[str]
    archetype_fit: dict
    hidden_value: list[str]
    synergies: dict
    timing: dict
    differentiation_factor: str
    enrichment_version: str = CONFIG["version"]
    enrichment_date: str = ""

    def __post_init__(self):
        if not self.enrichment_date:
            self.enrichment_date = datetime.now().isoformat()


# ==============================================================================
# PROMPT TEMPLATES
# ==============================================================================

AWARD_ENRICHMENT_PROMPT = """You are a strategic college admissions research assistant. Your task is to add strategic intelligence to award data.

IMPORTANT: Focus only on IQ (strategy, tactics, what works) - NOT on tone, voice, or communication style.

## Award to Enrich

ID: {id}
Name: {name}
Organization: {organization}
Category: {category}
Level: {level}
Description: {description}
Prestige Score: {prestige_score}/10
Historical Win Rate: {historical_win_rate}
Effort Hours: {effort_hours}
Eligibility: {eligibility}
Diversity Focus: {diversity_focus}

## Classification Rules

**Strategic Tier:**
- Tier 1: Acceptance < 5% AND prestige >= 9, OR nationally recognized gold standard
- Tier 2: Acceptance 5-15% AND prestige >= 7, OR strong regional/national recognition
- Tier 3: Acceptance 15-40% AND prestige >= 5, OR solid resume builder
- Tier 4: Acceptance > 40% OR prestige < 5, situational value

**Win Cascade Position:**
- "entry": First award in domain, lower barrier, teaches fundamentals
- "building": Requires prior achievement, regional/state level, bridges to capstone
- "capstone": Highest achievement, requires prior wins, strong admissions signal

## Your Task

Provide strategic intelligence as JSON:

```json
{{
  "id": "{id}",
  "strategic_tier": <1-4>,
  "strategic_tier_rationale": "<one sentence explaining tier choice>",
  "strategic_notes": "<3-4 sentences: what admissions officers think, selection criteria insights, strategic value>",
  "success_patterns": [
    "<specific actionable pattern 1>",
    "<specific actionable pattern 2>",
    "<specific actionable pattern 3>",
    "<specific actionable pattern 4>",
    "<specific actionable pattern 5>"
  ],
  "common_mistakes": [
    "<specific mistake 1>",
    "<specific mistake 2>",
    "<specific mistake 3>",
    "<specific mistake 4>",
    "<specific mistake 5>"
  ],
  "archetype_fit": {{
    "academic_powerhouse": <0.0-1.0>,
    "stem_innovator": <0.0-1.0>,
    "creative_visionary": <0.0-1.0>,
    "community_changemaker": <0.0-1.0>,
    "entrepreneurial_leader": <0.0-1.0>,
    "humanities_scholar": <0.0-1.0>,
    "athletic_scholar": <0.0-1.0>,
    "multi_hyphenate": <0.0-1.0>
  }},
  "win_cascade": {{
    "position": "<entry|building|capstone>",
    "prerequisites": ["<award_id or description>", ...],
    "enables": ["<award_id or description>", ...]
  }},
  "timing": {{
    "ideal_grades": [<grade numbers>],
    "prep_weeks": <number>,
    "deadline_strategy": "<one sentence>"
  }},
  "differentiation_factor": "<one sentence: what makes winners stand out>"
}}
```

Return ONLY valid JSON, no additional text."""


PROGRAM_ENRICHMENT_PROMPT = """You are a strategic college admissions research assistant. Your task is to add strategic intelligence to summer program data.

IMPORTANT: Focus only on IQ (strategy, tactics, what works) - NOT on tone, voice, or communication style.

## Program to Enrich

ID: {id}
Name: {name}
Organization: {organization}
Type: {type}
Category: {category}
Description: {description}
Prestige Score: {prestige_score}/10
Acceptance Rate: {acceptance_rate}
Selectivity: {selectivity}
Cost: ${cost}
Duration: {duration_weeks} weeks
Location: {location}
Is Residential: {is_residential}
Eligibility: {eligibility}
Diversity Focus: {diversity_focus}

## Classification Rules

**Strategic Tier:**
- Tier 1: Acceptance < 5% AND prestige >= 9, OR nationally recognized (RSI, TASP, MOSTEC, etc.)
- Tier 2: Acceptance 5-15% AND prestige >= 7, OR strong institutional backing
- Tier 3: Acceptance 15-40% AND prestige >= 5, OR solid experience builder
- Tier 4: Acceptance > 40% OR prestige < 5, situational value

**Application Intensity:**
- "light": < 5 hours total, simple application
- "moderate": 5-15 hours, essays + recommendations
- "heavy": > 15 hours, multiple essays, portfolio, interviews

## Your Task

Provide strategic intelligence as JSON:

```json
{{
  "id": "{id}",
  "strategic_tier": <1-4>,
  "strategic_tier_rationale": "<one sentence explaining tier choice>",
  "strategic_notes": "<3-4 sentences: what admissions officers think, selection insights, strategic value>",
  "success_patterns": [
    "<specific actionable pattern 1>",
    "<specific actionable pattern 2>",
    "<specific actionable pattern 3>",
    "<specific actionable pattern 4>",
    "<specific actionable pattern 5>"
  ],
  "common_mistakes": [
    "<specific mistake 1>",
    "<specific mistake 2>",
    "<specific mistake 3>",
    "<specific mistake 4>",
    "<specific mistake 5>"
  ],
  "archetype_fit": {{
    "academic_powerhouse": <0.0-1.0>,
    "stem_innovator": <0.0-1.0>,
    "creative_visionary": <0.0-1.0>,
    "community_changemaker": <0.0-1.0>,
    "entrepreneurial_leader": <0.0-1.0>,
    "humanities_scholar": <0.0-1.0>,
    "athletic_scholar": <0.0-1.0>,
    "multi_hyphenate": <0.0-1.0>
  }},
  "hidden_value": [
    "<non-obvious benefit 1>",
    "<non-obvious benefit 2>",
    "<non-obvious benefit 3>"
  ],
  "synergies": {{
    "pairs_well_with": ["<program_id or description>", ...],
    "leads_to": ["<opportunity description>", ...]
  }},
  "timing": {{
    "ideal_grades": [<grade numbers>],
    "prep_weeks": <number>,
    "application_intensity": "<light|moderate|heavy>"
  }},
  "differentiation_factor": "<one sentence: what makes accepted students stand out>"
}}
```

Return ONLY valid JSON, no additional text."""


# ==============================================================================
# ENRICHMENT ENGINE
# ==============================================================================

class EnrichmentEngine:
    """Handles the enrichment process with checkpointing and validation."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.checkpoint_dir = PROJECT_ROOT / CONFIG["checkpoint_dir"]
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Load existing data
        self.awards_data = self._load_awards()
        self.programs_data = self._load_programs()

        # Track enrichment state
        self.enriched_awards = {}
        self.enriched_programs = {}
        self.errors = []

        # Load any existing checkpoints
        self._load_checkpoints()

    def _load_awards(self) -> list[dict]:
        """Load awards from seed file."""
        # Try multiple possible locations
        possible_paths = [
            SEEDS_DIR / "awards_data.py",
            PROJECT_ROOT / "agents" / "seeds" / "awards_data.py",
            Path("agents/seeds/awards_data.py"),
        ]

        for path in possible_paths:
            if path.exists():
                # Execute the Python file to get the data
                namespace = {}
                exec(path.read_text(), namespace)
                # Look for get_all_awards function first
                if "get_all_awards" in namespace:
                    awards = namespace["get_all_awards"]()
                    print(f"  Loaded {len(awards)} awards from {path}")
                    return awards
                # Fallback to common variable names
                for var_name in ["AWARDS_DATA", "AWARDS", "awards_data", "awards"]:
                    if var_name in namespace:
                        print(f"  Loaded {len(namespace[var_name])} awards from {path}")
                        return namespace[var_name]

        print("  Could not load awards data - check path")
        return []

    def _load_programs(self) -> list[dict]:
        """Load programs/opportunities from seed file."""
        possible_paths = [
            SEEDS_DIR / "opportunities_data.py",
            PROJECT_ROOT / "agents" / "seeds" / "opportunities_data.py",
            Path("agents/seeds/opportunities_data.py"),
        ]

        for path in possible_paths:
            if path.exists():
                namespace = {}
                exec(path.read_text(), namespace)
                # Look for get_all_opportunities function first
                if "get_all_opportunities" in namespace:
                    programs = namespace["get_all_opportunities"]()
                    print(f"  Loaded {len(programs)} programs from {path}")
                    return programs
                # Fallback to common variable names
                for var_name in ["OPPORTUNITIES_DATA", "PROGRAMS_DATA", "OPPORTUNITIES", "opportunities_data"]:
                    if var_name in namespace:
                        print(f"  Loaded {len(namespace[var_name])} programs from {path}")
                        return namespace[var_name]

        print("  Could not load programs data - check path")
        return []

    def _load_checkpoints(self):
        """Load any existing checkpoint files."""
        awards_checkpoint = self.checkpoint_dir / "awards_checkpoint.json"
        programs_checkpoint = self.checkpoint_dir / "programs_checkpoint.json"

        if awards_checkpoint.exists():
            self.enriched_awards = json.loads(awards_checkpoint.read_text())
            print(f"  Loaded checkpoint: {len(self.enriched_awards)} awards already enriched")

        if programs_checkpoint.exists():
            self.enriched_programs = json.loads(programs_checkpoint.read_text())
            print(f"  Loaded checkpoint: {len(self.enriched_programs)} programs already enriched")

    def _save_checkpoint(self):
        """Save current progress to checkpoint files."""
        awards_checkpoint = self.checkpoint_dir / "awards_checkpoint.json"
        programs_checkpoint = self.checkpoint_dir / "programs_checkpoint.json"

        awards_checkpoint.write_text(json.dumps(self.enriched_awards, indent=2))
        programs_checkpoint.write_text(json.dumps(self.enriched_programs, indent=2))

    def get_top_items(self, n: int = 20) -> tuple[list[dict], list[dict]]:
        """Get top N items by prestige/selectivity for initial enrichment."""
        # Top awards by prestige score
        sorted_awards = sorted(
            self.awards_data,
            key=lambda x: (-x.get("prestige_score", 0), x.get("historical_win_rate", 1))
        )
        top_awards = sorted_awards[:n]

        # Top programs by selectivity (lowest acceptance rate)
        sorted_programs = sorted(
            self.programs_data,
            key=lambda x: (x.get("acceptance_rate", 1), -x.get("prestige_score", 0))
        )
        top_programs = sorted_programs[:n]

        return top_awards, top_programs

    def get_remaining_items(self) -> tuple[list[dict], list[dict]]:
        """Get items not yet enriched."""
        remaining_awards = [
            a for a in self.awards_data
            if a.get("id") not in self.enriched_awards
        ]
        remaining_programs = [
            p for p in self.programs_data
            if p.get("id") not in self.enriched_programs
        ]
        return remaining_awards, remaining_programs

    async def enrich_award(self, award: dict) -> Optional[dict]:
        """Enrich a single award with strategic intelligence."""
        award_id = award.get("id", "unknown")

        # Skip if already enriched
        if award_id in self.enriched_awards:
            print(f"    Skipping {award_id} (already enriched)")
            return self.enriched_awards[award_id]

        # Format prompt
        prompt = AWARD_ENRICHMENT_PROMPT.format(
            id=award.get("id", ""),
            name=award.get("name", ""),
            organization=award.get("organization", ""),
            category=award.get("category", ""),
            level=award.get("level", ""),
            description=award.get("description", ""),
            prestige_score=award.get("prestige_score", 5),
            historical_win_rate=award.get("historical_win_rate", 0.5),
            effort_hours=award.get("effort_hours", 10),
            eligibility=json.dumps(award.get("eligibility", {})),
            diversity_focus=award.get("diversity_focus", False),
        )

        # Call LLM with retries
        for attempt in range(CONFIG["max_retries"]):
            try:
                response = await self._call_llm(prompt)
                intelligence = self._parse_json_response(response)

                if intelligence:
                    # Add metadata
                    intelligence["enrichment_version"] = CONFIG["version"]
                    intelligence["enrichment_date"] = datetime.now().isoformat()

                    # Merge with original data
                    enriched = {**award, **intelligence}
                    self.enriched_awards[award_id] = enriched

                    print(f"    Enriched award: {award_id} (Tier {intelligence.get('strategic_tier', '?')})")
                    return enriched

            except Exception as e:
                print(f"    Attempt {attempt + 1} failed for {award_id}: {e}")
                await asyncio.sleep(1)

        self.errors.append({"type": "award", "id": award_id, "error": "Max retries exceeded"})
        return None

    async def enrich_program(self, program: dict) -> Optional[dict]:
        """Enrich a single program with strategic intelligence."""
        program_id = program.get("id", "unknown")

        # Skip if already enriched
        if program_id in self.enriched_programs:
            print(f"    Skipping {program_id} (already enriched)")
            return self.enriched_programs[program_id]

        # Format prompt
        prompt = PROGRAM_ENRICHMENT_PROMPT.format(
            id=program.get("id", ""),
            name=program.get("name", ""),
            organization=program.get("organization", ""),
            type=program.get("type", ""),
            category=program.get("category", ""),
            description=program.get("description", ""),
            prestige_score=program.get("prestige_score", 5),
            acceptance_rate=program.get("acceptance_rate", 0.5),
            selectivity=program.get("selectivity", "moderate"),
            cost=program.get("cost", 0),
            duration_weeks=program.get("duration_weeks", 4),
            location=program.get("location", ""),
            is_residential=program.get("is_residential", False),
            eligibility=json.dumps(program.get("eligibility", {})),
            diversity_focus=program.get("diversity_focus", False),
        )

        # Call LLM with retries
        for attempt in range(CONFIG["max_retries"]):
            try:
                response = await self._call_llm(prompt)
                intelligence = self._parse_json_response(response)

                if intelligence:
                    # Add metadata
                    intelligence["enrichment_version"] = CONFIG["version"]
                    intelligence["enrichment_date"] = datetime.now().isoformat()

                    # Merge with original data
                    enriched = {**program, **intelligence}
                    self.enriched_programs[program_id] = enriched

                    print(f"    Enriched program: {program_id} (Tier {intelligence.get('strategic_tier', '?')})")
                    return enriched

            except Exception as e:
                print(f"    Attempt {attempt + 1} failed for {program_id}: {e}")
                await asyncio.sleep(1)

        self.errors.append({"type": "program", "id": program_id, "error": "Max retries exceeded"})
        return None

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM and return response text."""
        if self.llm_client is None:
            # Initialize client on first use
            try:
                from langchain_openai import ChatOpenAI
                self.llm_client = ChatOpenAI(
                    model=CONFIG["llm_model"],
                    temperature=CONFIG["llm_temperature"],
                )
            except ImportError:
                raise RuntimeError("langchain_openai not installed. Run: pip install langchain-openai")

        response = await self.llm_client.ainvoke(prompt)
        return response.content

    def _parse_json_response(self, response: str) -> Optional[dict]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        # Strip markdown code blocks if present
        text = response.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            print(f"    JSON parse error: {e}")
            return None

    async def run_batch(
        self,
        awards: list[dict],
        programs: list[dict],
        progress_callback=None
    ):
        """Run enrichment on a batch of items."""
        total = len(awards) + len(programs)
        processed = 0

        print(f"\n{'='*60}")
        print(f"ENRICHMENT RUN - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Awards: {len(awards)}, Programs: {len(programs)}")
        print(f"{'='*60}\n")

        # Process awards
        print("Processing Awards...")
        for i, award in enumerate(awards):
            await self.enrich_award(award)
            processed += 1

            # Checkpoint
            if processed % CONFIG["checkpoint_frequency"] == 0:
                self._save_checkpoint()
                print(f"  Checkpoint saved ({processed}/{total})")

            if progress_callback:
                progress_callback(processed, total)

        # Process programs
        print("\nProcessing Programs...")
        for i, program in enumerate(programs):
            await self.enrich_program(program)
            processed += 1

            # Checkpoint
            if processed % CONFIG["checkpoint_frequency"] == 0:
                self._save_checkpoint()
                print(f"  Checkpoint saved ({processed}/{total})")

            if progress_callback:
                progress_callback(processed, total)

        # Final save
        self._save_checkpoint()

        print(f"\n{'='*60}")
        print(f"ENRICHMENT COMPLETE")
        print(f"Awards enriched: {len(self.enriched_awards)}")
        print(f"Programs enriched: {len(self.enriched_programs)}")
        print(f"Errors: {len(self.errors)}")
        print(f"{'='*60}\n")

    def export_results(self, output_dir: Path = None):
        """Export enriched data to files."""
        output_dir = output_dir or (PROJECT_ROOT / CONFIG["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export enriched awards
        awards_path = output_dir / "awards_enriched.json"
        awards_path.write_text(json.dumps(list(self.enriched_awards.values()), indent=2))
        print(f"Exported {len(self.enriched_awards)} awards to {awards_path}")

        # Export enriched programs
        programs_path = output_dir / "programs_enriched.json"
        programs_path.write_text(json.dumps(list(self.enriched_programs.values()), indent=2))
        print(f"Exported {len(self.enriched_programs)} programs to {programs_path}")

        # Export metadata
        metadata = self._generate_metadata()
        metadata_path = output_dir / "enrichment_metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))
        print(f"Exported metadata to {metadata_path}")

        # Export errors if any
        if self.errors:
            errors_path = output_dir / "enrichment_errors.json"
            errors_path.write_text(json.dumps(self.errors, indent=2))
            print(f"Exported {len(self.errors)} errors to {errors_path}")

        return output_dir

    def _generate_metadata(self) -> dict:
        """Generate enrichment metadata for tracking."""
        awards_list = list(self.enriched_awards.values())
        programs_list = list(self.enriched_programs.values())

        # Calculate tier distributions
        award_tiers = {}
        for a in awards_list:
            tier = a.get("strategic_tier", 0)
            award_tiers[tier] = award_tiers.get(tier, 0) + 1

        program_tiers = {}
        for p in programs_list:
            tier = p.get("strategic_tier", 0)
            program_tiers[tier] = program_tiers.get(tier, 0) + 1

        return {
            "version": CONFIG["version"],
            "enrichment_date": datetime.now().isoformat(),
            "awards": {
                "total_in_database": len(self.awards_data),
                "enriched": len(self.enriched_awards),
                "tier_distribution": award_tiers,
            },
            "programs": {
                "total_in_database": len(self.programs_data),
                "enriched": len(self.enriched_programs),
                "tier_distribution": program_tiers,
            },
            "errors": len(self.errors),
            "llm_model": CONFIG["llm_model"],
        }


# ==============================================================================
# VALIDATION
# ==============================================================================

class EnrichmentValidator:
    """Validates enriched data for quality and completeness."""

    def __init__(self, enriched_awards: list[dict], enriched_programs: list[dict]):
        self.awards = enriched_awards
        self.programs = enriched_programs
        self.issues = []

    def validate_all(self) -> dict:
        """Run all validation checks."""
        results = {
            "tier_distribution": self._check_tier_distribution(),
            "archetype_coverage": self._check_archetype_coverage(),
            "cascade_integrity": self._check_cascade_integrity(),
            "required_fields": self._check_required_fields(),
            "data_quality": self._check_data_quality(),
        }

        results["overall_valid"] = all(
            r.get("valid", False) for r in results.values()
        )
        results["issues"] = self.issues

        return results

    def _check_tier_distribution(self) -> dict:
        """Check if tier distribution is reasonable."""
        # Expected: ~15% T1, ~25% T2, ~35% T3, ~25% T4
        expected = {1: (0.05, 0.25), 2: (0.15, 0.40), 3: (0.20, 0.50), 4: (0.10, 0.40)}

        results = {"awards": {}, "programs": {}, "valid": True}

        for data_type, items in [("awards", self.awards), ("programs", self.programs)]:
            if not items:
                continue

            tier_counts = {}
            for item in items:
                tier = item.get("strategic_tier", 0)
                tier_counts[tier] = tier_counts.get(tier, 0) + 1

            total = len(items)
            for tier, count in tier_counts.items():
                pct = count / total
                results[data_type][tier] = {"count": count, "percentage": round(pct * 100, 1)}

                if tier in expected:
                    min_pct, max_pct = expected[tier]
                    if not (min_pct <= pct <= max_pct):
                        self.issues.append(
                            f"{data_type} Tier {tier} distribution ({pct:.1%}) outside expected range ({min_pct:.0%}-{max_pct:.0%})"
                        )
                        # Don't fail validation for distribution - just warn

        return results

    def _check_archetype_coverage(self) -> dict:
        """Check if all archetypes have sufficient coverage."""
        archetypes = [
            "academic_powerhouse", "stem_innovator", "creative_visionary",
            "community_changemaker", "entrepreneurial_leader", "humanities_scholar",
            "athletic_scholar", "multi_hyphenate"
        ]

        min_high_fit = 2  # At least 2 items with fit >= 0.7 per archetype
        results = {"awards": {}, "programs": {}, "valid": True}

        for data_type, items in [("awards", self.awards), ("programs", self.programs)]:
            if not items:
                continue

            for archetype in archetypes:
                high_fit_count = sum(
                    1 for item in items
                    if item.get("archetype_fit", {}).get(archetype, 0) >= 0.7
                )
                results[data_type][archetype] = high_fit_count

                if high_fit_count < min_high_fit:
                    self.issues.append(
                        f"{data_type}: {archetype} has only {high_fit_count} items with fit >= 0.7 (need {min_high_fit})"
                    )
                    # Don't fail - just warn

        return results

    def _check_cascade_integrity(self) -> dict:
        """Check win cascade relationships are valid."""
        results = {"valid": True, "issues": []}

        all_award_ids = {a.get("id") for a in self.awards}

        for award in self.awards:
            cascade = award.get("win_cascade", {})
            position = cascade.get("position", "")
            prerequisites = cascade.get("prerequisites", [])

            # Building/capstone should have prerequisites
            if position in ["building", "capstone"] and not prerequisites:
                issue = f"Award {award.get('id')} is {position} but has no prerequisites"
                self.issues.append(issue)
                results["issues"].append(issue)

        return results

    def _check_required_fields(self) -> dict:
        """Check all required intelligence fields are present."""
        award_required = [
            "strategic_tier", "strategic_notes", "success_patterns",
            "common_mistakes", "archetype_fit", "win_cascade", "timing",
            "differentiation_factor"
        ]

        program_required = [
            "strategic_tier", "strategic_notes", "success_patterns",
            "common_mistakes", "archetype_fit", "hidden_value", "synergies",
            "timing", "differentiation_factor"
        ]

        results = {"awards_missing": [], "programs_missing": [], "valid": True}

        for award in self.awards:
            missing = [f for f in award_required if f not in award or not award[f]]
            if missing:
                results["awards_missing"].append({"id": award.get("id"), "missing": missing})
                results["valid"] = False

        for program in self.programs:
            missing = [f for f in program_required if f not in program or not program[f]]
            if missing:
                results["programs_missing"].append({"id": program.get("id"), "missing": missing})
                results["valid"] = False

        return results

    def _check_data_quality(self) -> dict:
        """Check data quality indicators."""
        results = {"valid": True, "issues": []}

        for award in self.awards:
            # Check success_patterns has enough items
            patterns = award.get("success_patterns", [])
            if len(patterns) < 3:
                issue = f"Award {award.get('id')} has only {len(patterns)} success patterns (need 3+)"
                self.issues.append(issue)
                results["valid"] = False

            # Check strategic_notes is substantial
            notes = award.get("strategic_notes", "")
            if len(notes) < 50:
                issue = f"Award {award.get('id')} has very short strategic_notes ({len(notes)} chars)"
                self.issues.append(issue)

        for program in self.programs:
            patterns = program.get("success_patterns", [])
            if len(patterns) < 3:
                issue = f"Program {program.get('id')} has only {len(patterns)} success patterns (need 3+)"
                self.issues.append(issue)
                results["valid"] = False

        return results

    def print_report(self, results: dict):
        """Print a formatted validation report."""
        print("\n" + "="*60)
        print("ENRICHMENT VALIDATION REPORT")
        print("="*60)

        overall = "PASSED" if results["overall_valid"] else "NEEDS REVIEW"
        print(f"\nOVERALL: {overall}")

        print("\nTier Distribution:")
        for data_type in ["awards", "programs"]:
            dist = results.get("tier_distribution", {}).get(data_type, {})
            if dist:
                print(f"  {data_type.capitalize()}:")
                for tier, data in sorted(dist.items()):
                    print(f"    Tier {tier}: {data['count']} ({data['percentage']}%)")

        print("\nArchetype Coverage (items with fit >= 0.7):")
        for data_type in ["awards", "programs"]:
            coverage = results.get("archetype_coverage", {}).get(data_type, {})
            if coverage:
                print(f"  {data_type.capitalize()}:")
                for archetype, count in coverage.items():
                    status = "OK" if count >= 2 else "LOW"
                    print(f"    {status} {archetype}: {count}")

        if results.get("issues"):
            print("\nIssues Found:")
            for issue in results["issues"][:10]:  # Show first 10
                print(f"  - {issue}")
            if len(results["issues"]) > 10:
                print(f"  ... and {len(results['issues']) - 10} more")

        print("\n" + "="*60)


# ==============================================================================
# CLI ENTRY POINT
# ==============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Enrich awards and programs with strategic intelligence"
    )
    parser.add_argument(
        "--mode",
        choices=["top20", "all", "remaining", "single"],
        default="top20",
        help="Enrichment mode"
    )
    parser.add_argument(
        "--id",
        type=str,
        help="Specific item ID (for single mode)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validation on existing enriched data"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export results to files"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for exported files"
    )

    args = parser.parse_args()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY") and not args.validate:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY=your-key")
        sys.exit(1)

    engine = EnrichmentEngine()

    if args.validate:
        # Run validation on existing enriched data
        output_dir = Path(args.output_dir) if args.output_dir else (PROJECT_ROOT / CONFIG["output_dir"])

        awards_path = output_dir / "awards_enriched.json"
        programs_path = output_dir / "programs_enriched.json"

        if not awards_path.exists() or not programs_path.exists():
            print("ERROR: Enriched data files not found. Run enrichment first.")
            sys.exit(1)

        awards = json.loads(awards_path.read_text())
        programs = json.loads(programs_path.read_text())

        validator = EnrichmentValidator(awards, programs)
        results = validator.validate_all()
        validator.print_report(results)

        # Save validation results
        validation_path = output_dir / "validation_results.json"
        validation_path.write_text(json.dumps(results, indent=2))
        print(f"\nValidation results saved to {validation_path}")

        sys.exit(0 if results["overall_valid"] else 1)

    # Determine items to process
    if args.mode == "top20":
        awards, programs = engine.get_top_items(20)
        print(f"Mode: Top 20 items")
    elif args.mode == "remaining":
        awards, programs = engine.get_remaining_items()
        print(f"Mode: Remaining items")
    elif args.mode == "single" and args.id:
        awards = [a for a in engine.awards_data if a.get("id") == args.id]
        programs = [p for p in engine.programs_data if p.get("id") == args.id]
        if not awards and not programs:
            print(f"ERROR: Item with ID '{args.id}' not found")
            sys.exit(1)
        print(f"Mode: Single item ({args.id})")
    else:  # all
        awards = engine.awards_data
        programs = engine.programs_data
        print(f"Mode: All items")

    # Run enrichment
    await engine.run_batch(awards, programs)

    # Export if requested or by default
    if args.export or True:  # Always export for now
        output_dir = Path(args.output_dir) if args.output_dir else None
        engine.export_results(output_dir)

    # Run validation
    validator = EnrichmentValidator(
        list(engine.enriched_awards.values()),
        list(engine.enriched_programs.values())
    )
    results = validator.validate_all()
    validator.print_report(results)


if __name__ == "__main__":
    asyncio.run(main())
