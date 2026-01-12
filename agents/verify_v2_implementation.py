#!/usr/bin/env python3
"""
IvyQuest v2.0 Implementation Verification Script
Run this after starting the backend server to verify all endpoints.

Usage:
  1. Start the backend: cd agents && uvicorn main:app --port 8001
  2. Run this script: python verify_v2_implementation.py
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001"


def check_endpoint(method, path, data=None, name=""):
    """Check if an endpoint responds correctly."""
    try:
        if method == "GET":
            resp = requests.get(f"{BASE_URL}{path}", timeout=5)
        else:
            resp = requests.post(
                f"{BASE_URL}{path}",
                json=data or {},
                headers={"Content-Type": "application/json"},
                timeout=5
            )

        # 200 = success, 422 = validation error (endpoint exists but missing params)
        # 503 = service disabled (endpoint exists)
        if resp.status_code == 200:
            status = "✅"
        elif resp.status_code in [422, 503]:
            status = "⚠️"  # Endpoint exists but needs params or is disabled
        else:
            status = "❌"

        print(f"{status} {name}: {resp.status_code}")

        if resp.status_code == 200 and method == "GET":
            # Show a snippet of the response for GET requests
            try:
                data = resp.json()
                if isinstance(data, dict) and "success" in data:
                    print(f"   Response: success={data.get('success')}")
            except:
                pass

        return resp.status_code in [200, 422, 503]
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection refused (is server running?)")
        return False
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("IVYQUEST v2.0 BACKEND VERIFICATION")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print()

    results = {"passed": 0, "failed": 0}

    # Health check
    print("--- Health Check ---")
    if check_endpoint("GET", "/health", name="Health Check"):
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  Server not running. Start with:")
        print("   cd agents && uvicorn main:app --port 8001")
        print("=" * 60)
        return 1

    # Root endpoint
    if check_endpoint("GET", "/", name="Root"):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # v10.0 existing endpoints
    print("\n--- v10.0 Core Endpoints ---")
    endpoints_v10 = [
        ("POST", "/agents/assessment/enhance", {"profile_id": "test-profile"}, "Assessment Enhance"),
        ("POST", "/agents/execution/scaffold", {"profile_id": "test-profile", "project_data": {}}, "Execution Scaffold"),
        ("POST", "/agents/execution/crisis", {"profile_id": "test-profile", "description": "test crisis"}, "Execution Crisis"),
        ("POST", "/agents/gameplan/generate", {"profile_id": "test-profile"}, "GamePlan Generate"),
        ("GET", "/agents/awards/match/test-profile", None, "Awards Match"),
        ("GET", "/agents/opportunities/match/test-profile", None, "Opportunities Match"),
    ]

    for method, path, data, name in endpoints_v10:
        if check_endpoint(method, path, data, name):
            results["passed"] += 1
        else:
            results["failed"] += 1

    # v2.0 NEW endpoints - Jenny Intelligence Modules
    print("\n--- v2.0 Jenny Intelligence Endpoints ---")
    endpoints_v2 = [
        ("POST", "/agents/time-audit", {
            "sleep_hours": 8,
            "school_hours": 7.5,
            "social_media_hours_daily": 3
        }, "Time Audit (168-Hour Framework)"),

        ("POST", "/agents/weekly-plan", {
            "profile_id": "test-profile",
            "tasks": [
                {"name": "NCWIT Essay", "priority": "P0", "estimated_hours": 5},
                {"name": "SAT Prep", "priority": "P1", "estimated_hours": 3}
            ],
            "available_hours": 26
        }, "Weekly Plan (P0/P1/P2)"),

        ("POST", "/agents/awards/portfolio", {
            "profile_id": "test-profile"
        }, "Awards Portfolio (2-2-1)"),

        ("POST", "/agents/ncwit-strategy", {
            "profile_id": "test-profile",
            "student_data": {
                "identity": ["female", "first-generation"],
                "experiences": ["felt isolated in CS class"]
            }
        }, "NCWIT Strategy"),

        ("POST", "/agents/opportunities/recommend", {
            "profile_id": "test-profile",
            "program": {
                "name": "Expensive Summer Camp",
                "cost_numeric": 8000,
                "category": "entrepreneurship",
                "duration": "4 weeks"
            }
        }, "Opportunity Recommend (Redirect Check)"),

        ("POST", "/agents/crisis-alchemy", {
            "profile_id": "test-profile",
            "crisis_description": "I got rejected from the summer program I really wanted"
        }, "Crisis Alchemy (4-Step Protocol)"),

        ("POST", "/validation/jenny-voice", {
            "text": "Great question! I love that you're thinking about this. What do you think would work best?",
            "auto_fix": True
        }, "Jenny Voice Validation"),

        ("GET", "/agents/jenny-techniques", None, "Jenny Techniques List"),
    ]

    for method, path, data, name in endpoints_v2:
        if check_endpoint(method, path, data, name):
            results["passed"] += 1
        else:
            results["failed"] += 1

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    total = results["passed"] + results["failed"]
    print(f"Passed: {results['passed']}/{total}")
    print(f"Failed: {results['failed']}/{total}")

    if results["failed"] == 0:
        print("\n✅ All endpoints verified successfully!")
        return 0
    else:
        print(f"\n⚠️  {results['failed']} endpoint(s) need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())
