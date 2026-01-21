#!/usr/bin/env python3
"""
Apply Migration 041: Fix Safe Date Parsing
==========================================

This script reads the migration SQL and provides instructions for applying it.
The migration fixes the error:
  "invalid input syntax for type date: 'February-March for formal programs'"

Usage:
  python scripts/apply_migration_041.py

Options:
  - Prints the SQL to apply
  - Optionally copy to clipboard (if pyperclip is available)
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

MIGRATION_FILE = project_root / "supabase" / "migrations" / "041_fix_safe_date_parsing.sql"


def main():
    print("=" * 60)
    print("Migration 041: Fix Safe Date Parsing")
    print("=" * 60)

    # Read the migration file
    if not MIGRATION_FILE.exists():
        print(f"ERROR: Migration file not found at {MIGRATION_FILE}")
        sys.exit(1)

    sql_content = MIGRATION_FILE.read_text()

    print("\nThis migration fixes the error:")
    print('  "invalid input syntax for type date: \'February-March for formal programs\'"')
    print("\nThe fix:")
    print("  1. Creates a safe_to_date() function that returns NULL for invalid dates")
    print("  2. Updates the extract_goals_from_gameplan trigger to use safe_to_date()")

    print("\n" + "=" * 60)
    print("HOW TO APPLY THIS MIGRATION")
    print("=" * 60)
    print("""
Option 1: Supabase Dashboard (Recommended)
------------------------------------------
1. Go to your Supabase project dashboard
2. Click "SQL Editor" in the left sidebar
3. Click "New query"
4. Paste the SQL below and click "Run"

Option 2: Supabase CLI
------------------------------------------
If you have supabase CLI configured:
  cd /Users/snazir/ivyquest-claude-v2.2
  supabase db push

Option 3: Direct PostgreSQL
------------------------------------------
If you have direct database access:
  psql $DATABASE_URL -f supabase/migrations/041_fix_safe_date_parsing.sql
""")

    print("\n" + "=" * 60)
    print("MIGRATION SQL (copy everything below)")
    print("=" * 60)
    print()
    print(sql_content)
    print()
    print("=" * 60)
    print("END OF MIGRATION SQL")
    print("=" * 60)

    # Try to copy to clipboard if pyperclip is available
    try:
        import pyperclip
        pyperclip.copy(sql_content)
        print("\n✅ SQL copied to clipboard!")
    except ImportError:
        print("\n📋 Tip: Install pyperclip to auto-copy: pip install pyperclip")

    print("\nAfter applying the migration:")
    print("1. Restart the backend server")
    print("2. Try the assessment flow again")
    print("3. Game plan save should now work!")


if __name__ == "__main__":
    main()
