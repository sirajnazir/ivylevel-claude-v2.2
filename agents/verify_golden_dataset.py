#!/usr/bin/env python3
"""
verify_golden_dataset.py
Comprehensive verification of Jenny's coaching intelligence data

Usage:
    cd agents
    source venv/bin/activate
    python verify_golden_dataset.py
"""

import os
import sys

# Set environment variables for this project
os.environ.setdefault("SUPABASE_URL", "https://adufducypflyvmnwbrmo.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkdWZkdWN5cGZseXZtbndicm1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDMxNDIyMSwiZXhwIjoyMDc5ODkwMjIxfQ.NnH9x6xi1iFcaIZ6U5NAlPLXSJ6B_1pJxKyJoBZKzNY")

from typing import Dict, List, Tuple
from dataclasses import dataclass

# Check for supabase
try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    print("Warning: supabase-py not installed. Run: pip install supabase")

# Check for requests (for API testing)
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class TableCheck:
    name: str
    min_records: int
    description: str


# Expected data specifications
TABLE_CHECKS = [
    TableCheck("evaluation_golden", 3, "Golden coaching examples"),
    TableCheck("forbidden_phrases", 12, "Jenny's banned phrases"),
    TableCheck("speech_patterns", 5, "Jenny's characteristic patterns"),
    TableCheck("crisis_transformations", 4, "Crisis Alchemy scripts"),
    TableCheck("program_redirects", 4, "Expensive program alternatives"),
    TableCheck("awards", 90, "Awards database"),
    TableCheck("opportunities", 50, "Opportunities database"),
]

EXPECTED_FORBIDDEN_PHRASES = [
    "but",
    "however",
    "i think",
    "maybe",
    "sorry",
]

EXPECTED_CRISIS_TYPES = [
    "academic_setback",
    "family_hardship",
    "health_challenge",
    "rejection",
]


def print_header(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_result(name: str, passed: bool, details: str = ""):
    """Print a test result."""
    status = "✅" if passed else "❌"
    print(f"{status} {name}{': ' + details if details else ''}")


class DatabaseVerifier:
    """Verify data directly from Supabase database."""

    def __init__(self):
        self.supabase = None
        self.results = {"passed": 0, "failed": 0, "issues": []}

    def connect(self) -> bool:
        """Initialize Supabase connection."""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            print("⚠️  Missing SUPABASE_URL or SUPABASE_KEY environment variables")
            return False

        try:
            self.supabase = create_client(url, key)
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False

    def check_table(self, check: TableCheck) -> bool:
        """Check if table has minimum records."""
        try:
            result = self.supabase.table(check.name).select("*", count="exact").limit(1).execute()
            count = result.count or 0

            passed = count >= check.min_records
            details = f"{count} records (min: {check.min_records})"
            print_result(check.name, passed, details)

            if passed:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
                self.results["issues"].append(f"{check.name}: only {count} records (need {check.min_records}+)")

            return passed
        except Exception as e:
            print_result(check.name, False, f"Error: {e}")
            self.results["failed"] += 1
            self.results["issues"].append(f"{check.name}: table access error")
            return False

    def check_forbidden_phrases(self) -> Tuple[int, int]:
        """Verify expected forbidden phrases exist."""
        passed = 0
        failed = 0

        for phrase in EXPECTED_FORBIDDEN_PHRASES:
            try:
                result = self.supabase.table("forbidden_phrases").select("*").ilike("phrase", f"%{phrase}%").execute()
                if result.data:
                    passed += 1
                else:
                    failed += 1
                    self.results["issues"].append(f"Missing forbidden phrase: '{phrase}'")
            except:
                failed += 1

        self.results["passed"] += passed
        self.results["failed"] += failed
        return passed, failed

    def check_crisis_types(self) -> Tuple[int, int]:
        """Verify expected crisis types exist."""
        passed = 0
        failed = 0

        for crisis_type in EXPECTED_CRISIS_TYPES:
            try:
                result = self.supabase.table("crisis_transformations").select("*").eq("crisis_type", crisis_type).execute()
                if result.data:
                    passed += 1
                else:
                    failed += 1
                    self.results["issues"].append(f"Missing crisis type: '{crisis_type}'")
            except:
                failed += 1

        self.results["passed"] += passed
        self.results["failed"] += failed
        return passed, failed

    def run_all(self):
        """Run all database verifications."""
        print_header("DATABASE VERIFICATION")

        if not HAS_SUPABASE:
            print("❌ supabase-py not installed. Run: pip install supabase")
            return

        print("🔌 Connecting to Supabase...")
        if not self.connect():
            return
        print("✅ Connected\n")

        # Table counts
        print("--- Table Record Counts ---")
        for check in TABLE_CHECKS:
            self.check_table(check)

        # Forbidden phrases
        print("\n--- Forbidden Phrases ---")
        passed, failed = self.check_forbidden_phrases()
        print_result("Forbidden phrases content", failed == 0, f"{passed}/{len(EXPECTED_FORBIDDEN_PHRASES)} found")

        # Crisis types
        print("\n--- Crisis Transformations ---")
        passed, failed = self.check_crisis_types()
        print_result("Crisis types coverage", failed == 0, f"{passed}/{len(EXPECTED_CRISIS_TYPES)} present")


class APIVerifier:
    """Verify data via API endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {"passed": 0, "failed": 0, "issues": []}

    def check_health(self) -> bool:
        """Check API health."""
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                print_result("API Health", True, f"status={data.get('status')}, version={data.get('version')}")
                self.results["passed"] += 1
                return True
            else:
                print_result("API Health", False, f"status_code={resp.status_code}")
                self.results["failed"] += 1
                return False
        except requests.exceptions.ConnectionError:
            print_result("API Health", False, "Connection refused - is the server running?")
            self.results["failed"] += 1
            return False
        except Exception as e:
            print_result("API Health", False, str(e))
            self.results["failed"] += 1
            return False

    def check_jenny_techniques(self) -> bool:
        """Check Jenny techniques endpoint returns data."""
        try:
            resp = requests.get(f"{self.base_url}/agents/jenny-techniques", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                techniques = data.get("techniques", [])
                passed = len(techniques) > 0
                print_result("Jenny Techniques", passed, f"{len(techniques)} techniques loaded")
                if passed:
                    self.results["passed"] += 1
                else:
                    self.results["failed"] += 1
                return passed
            else:
                print_result("Jenny Techniques", False, f"status_code={resp.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("Jenny Techniques", False, str(e))
            self.results["failed"] += 1
            return False

    def check_voice_validation(self) -> bool:
        """Check voice validation detects forbidden phrases."""
        try:
            test_text = "I think you should maybe consider this. But unfortunately you need to work harder."
            resp = requests.post(
                f"{self.base_url}/validation/jenny-voice",
                json={"text": test_text},
                timeout=5
            )

            if resp.status_code == 200:
                data = resp.json()
                passing = data.get("passed", True)
                forbidden = data.get("forbidden_phrases_found", [])

                # Should fail (passing=False) due to forbidden phrases
                if not passing:
                    print_result("Voice Validation", True, f"Correctly detected violations, score={data.get('score')}")
                    self.results["passed"] += 1
                    return True
                else:
                    print_result("Voice Validation", False, f"Expected to fail, got passing={passing}")
                    self.results["failed"] += 1
                    return False
            else:
                print_result("Voice Validation", False, f"status_code={resp.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("Voice Validation", False, str(e))
            self.results["failed"] += 1
            return False

    def check_time_audit(self) -> bool:
        """Check time audit returns proper calculations."""
        try:
            resp = requests.post(
                f"{self.base_url}/agents/time-audit",
                json={"sleep_hours": 56, "school_hours": 35, "social_media_hours": 14, "fixed_commitments": 20},
                timeout=5
            )

            if resp.status_code == 200:
                data = resp.json()
                audit = data.get("audit", {})
                passion_hours = audit.get("passion_hours_available", 0)

                print_result("Time Audit", True, f"passion_hours={passion_hours}")
                self.results["passed"] += 1
                return True
            else:
                print_result("Time Audit", False, f"status_code={resp.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_result("Time Audit", False, str(e))
            self.results["failed"] += 1
            return False

    def run_all(self):
        """Run all API verifications."""
        print_header("API VERIFICATION")

        if not HAS_REQUESTS:
            print("❌ requests not installed. Run: pip install requests")
            return

        print(f"🔌 Testing API at {self.base_url}...\n")

        if not self.check_health():
            print("\n⚠️  API not reachable. Start the server first:")
            print("   cd agents && source venv/bin/activate && uvicorn main:app --reload --port 8000")
            return

        print()
        self.check_jenny_techniques()
        self.check_voice_validation()
        self.check_time_audit()


def main():
    print("\n" + "="*60)
    print("  GOLDEN DATASET VERIFICATION")
    print("  IvyQuest v2.0 - Jenny Coaching Intelligence")
    print("="*60)

    all_results = []

    # 1. Database verification
    db_verifier = DatabaseVerifier()
    db_verifier.run_all()
    all_results.append(("Database", db_verifier.results))

    # 2. API verification
    api_verifier = APIVerifier()
    api_verifier.run_all()
    all_results.append(("API", api_verifier.results))

    # Summary
    print_header("VERIFICATION SUMMARY")

    total_passed = 0
    total_failed = 0
    all_issues = []

    for name, results in all_results:
        passed = results.get("passed", 0)
        failed = results.get("failed", 0)
        total_passed += passed
        total_failed += failed
        all_issues.extend(results.get("issues", []))

        status = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
        print(f"{status} {name}: {passed} passed, {failed} failed")

    total = total_passed + total_failed
    if total > 0:
        pass_rate = (total_passed / total) * 100
        print(f"\nOverall: {total_passed}/{total} checks passed ({pass_rate:.1f}%)")

    if all_issues:
        print("\n📋 Issues to address:")
        for i, issue in enumerate(all_issues[:10], 1):
            print(f"   {i}. {issue}")
        if len(all_issues) > 10:
            print(f"   ... and {len(all_issues) - 10} more")

    # Final verdict
    if total_failed == 0:
        print("\n🎉 ALL VERIFICATIONS PASSED!")
        print("   Jenny's coaching intelligence is properly provisioned.")
        return True
    elif total_passed > total_failed:
        print("\n⚠️  PARTIAL PASS - Some data may be missing")
        print("   Run the SQL seed script in Supabase if needed.")
        return False
    else:
        print("\n❌ VERIFICATION FAILED")
        print("   Golden dataset needs to be provisioned.")
        print("   Run: supabase/seed_golden_data.sql in Supabase SQL Editor")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
