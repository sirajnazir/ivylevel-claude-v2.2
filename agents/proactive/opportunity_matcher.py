"""
Proactive Opportunity Matcher v10.0
===================================

Hourly job that matches students to relevant opportunities based on:
- Profile archetype and interests
- Deadlines approaching
- Previously recommended but not applied opportunities
- New opportunities matching their spike

Creates nudges in nudge_queue for delivery.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import structlog

from .config import is_feature_enabled

logger = structlog.get_logger()


async def match_opportunities_for_profile(
    supabase_client,
    profile_id: str,
    max_matches: int = 3,
) -> List[Dict[str, Any]]:
    """
    Match opportunities to a student profile.

    Args:
        supabase_client: Supabase client instance
        profile_id: Student profile ID
        max_matches: Maximum number of matches to return

    Returns:
        List of matched opportunities with relevance scores
    """
    matches = []

    try:
        # Get student profile
        profile_result = supabase_client.table("profiles").select(
            "id, first_name, grade, archetype, target_major, intended_major, target_schools"
        ).eq("id", profile_id).single().execute()

        if not profile_result.data:
            return []

        profile = profile_result.data
        archetype = profile.get("archetype")
        major = profile.get("target_major") or profile.get("intended_major")
        grade = profile.get("grade")

        # Get opportunities with upcoming deadlines (next 30 days)
        deadline_cutoff = (datetime.now() + timedelta(days=30)).isoformat()

        opportunities_result = supabase_client.table("opportunities").select(
            "id, name, type, deadline, tags, requirements, prestige_level"
        ).lte("deadline", deadline_cutoff).gte("deadline", datetime.now().isoformat()).order("deadline").limit(50).execute()

        if not opportunities_result.data:
            return []

        # Score each opportunity
        for opp in opportunities_result.data:
            score = _calculate_match_score(profile, opp)

            if score > 0.3:  # Only include reasonably good matches
                matches.append({
                    "opportunity_id": opp["id"],
                    "opportunity_name": opp["name"],
                    "opportunity_type": opp.get("type"),
                    "deadline": opp.get("deadline"),
                    "prestige_level": opp.get("prestige_level"),
                    "match_score": score,
                    "match_reasons": _get_match_reasons(profile, opp),
                })

        # Sort by score and limit
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:max_matches]

    except Exception as e:
        logger.error(
            "opportunity_match_error",
            profile_id=profile_id,
            error=str(e),
        )
        return []


def _calculate_match_score(profile: Dict[str, Any], opportunity: Dict[str, Any]) -> float:
    """Calculate a match score between profile and opportunity."""
    score = 0.0

    # Base score for having an upcoming deadline
    score += 0.2

    # Archetype matching (if tags include archetype indicators)
    archetype = profile.get("archetype", "").lower()
    tags = [t.lower() for t in (opportunity.get("tags") or [])]

    archetype_keywords = {
        "academic_perfectionist": ["academic", "research", "scholarship"],
        "future_founder": ["entrepreneurship", "startup", "business", "leadership"],
        "stem_innovator": ["stem", "science", "technology", "engineering", "math", "research"],
        "creative_storyteller": ["arts", "writing", "creative", "media", "journalism"],
        "global_changemaker": ["social", "community", "international", "volunteer"],
        "athletic_scholar": ["sports", "athletic", "ncaa"],
    }

    for keyword in archetype_keywords.get(archetype, []):
        if any(keyword in tag for tag in tags):
            score += 0.2
            break

    # Major matching
    major = (profile.get("target_major") or profile.get("intended_major") or "").lower()
    if major:
        for tag in tags:
            if major in tag or tag in major:
                score += 0.15
                break

    # Grade matching (check requirements)
    grade = profile.get("grade")
    requirements = opportunity.get("requirements") or {}
    req_grades = requirements.get("grades", [])
    if grade and req_grades and grade in req_grades:
        score += 0.15

    # Prestige boost for high-prestige opportunities
    prestige = opportunity.get("prestige_level", "").lower()
    if prestige in ["high", "very_high"]:
        score += 0.1

    return min(score, 1.0)  # Cap at 1.0


def _get_match_reasons(profile: Dict[str, Any], opportunity: Dict[str, Any]) -> List[str]:
    """Generate human-readable match reasons."""
    reasons = []

    deadline = opportunity.get("deadline")
    if deadline:
        try:
            deadline_dt = datetime.fromisoformat(deadline.replace("Z", ""))
            days_until = (deadline_dt - datetime.now()).days
            if days_until <= 7:
                reasons.append(f"Deadline in {days_until} days")
            elif days_until <= 14:
                reasons.append(f"Deadline in {days_until} days - good timing")
        except Exception:
            pass

    archetype = profile.get("archetype", "").replace("_", " ").title()
    if archetype:
        reasons.append(f"Matches your {archetype} profile")

    prestige = opportunity.get("prestige_level", "").lower()
    if prestige in ["high", "very_high"]:
        reasons.append("Prestigious opportunity")

    return reasons


async def job_opportunity_match(supabase_client) -> Dict[str, Any]:
    """
    Scheduled job: Match opportunities for all active students.

    Creates nudges in nudge_queue for matched opportunities.
    """
    if not is_feature_enabled("opportunity_match"):
        logger.info("opportunity_match_job_skipped", reason="Feature disabled")
        return {"skipped": True, "reason": "Feature disabled"}

    logger.info("opportunity_match_job_started")

    results = {
        "profiles_checked": 0,
        "matches_found": 0,
        "nudges_created": 0,
        "errors": [],
    }

    try:
        # Get all active profiles
        profiles_result = supabase_client.table("profiles").select(
            "id"
        ).eq("is_active", True).execute()

        profiles = profiles_result.data or []
        results["profiles_checked"] = len(profiles)

        for profile in profiles:
            profile_id = profile["id"]

            try:
                # Get matches
                matches = await match_opportunities_for_profile(
                    supabase_client,
                    profile_id,
                    max_matches=3,
                )

                if not matches:
                    continue

                results["matches_found"] += len(matches)

                # Create nudges for matches
                for match in matches:
                    # Check if similar nudge exists in last 24 hours
                    existing = supabase_client.table("nudge_queue").select("id").eq(
                        "profile_id", profile_id
                    ).eq("nudge_type", "opportunity_match").eq(
                        "metadata->>opportunity_id", match["opportunity_id"]
                    ).gte(
                        "created_at", (datetime.now() - timedelta(hours=24)).isoformat()
                    ).execute()

                    if existing.data:
                        continue  # Skip duplicate

                    # Create nudge
                    nudge = {
                        "profile_id": profile_id,
                        "nudge_type": "opportunity_match",
                        "priority": "medium" if match["match_score"] > 0.6 else "low",
                        "message_draft": _generate_opportunity_nudge(match),
                        "metadata": {
                            "opportunity_id": match["opportunity_id"],
                            "opportunity_name": match["opportunity_name"],
                            "match_score": match["match_score"],
                            "match_reasons": match["match_reasons"],
                        },
                        "status": "pending",
                        "created_at": datetime.now().isoformat(),
                    }

                    supabase_client.table("nudge_queue").insert(nudge).execute()
                    results["nudges_created"] += 1

            except Exception as e:
                logger.error(
                    "opportunity_match_profile_error",
                    profile_id=profile_id,
                    error=str(e),
                )
                results["errors"].append(f"{profile_id}: {str(e)}")

    except Exception as e:
        logger.error("opportunity_match_job_error", error=str(e))
        results["errors"].append(str(e))

    logger.info("opportunity_match_job_completed", **results)
    return results


def _generate_opportunity_nudge(match: Dict[str, Any]) -> str:
    """Generate a personalized nudge message for an opportunity match."""
    name = match["opportunity_name"]
    reasons = match.get("match_reasons", [])
    deadline = match.get("deadline", "")

    # Build message
    msg = f"Found a great opportunity for you: {name}!"

    if reasons:
        msg += f" {reasons[0]}."

    if deadline:
        try:
            deadline_dt = datetime.fromisoformat(deadline.replace("Z", ""))
            days_until = (deadline_dt - datetime.now()).days
            if days_until <= 7:
                msg += f" Deadline is in just {days_until} days!"
            else:
                msg += f" Deadline: {deadline_dt.strftime('%B %d')}."
        except Exception:
            pass

    msg += " Want me to help you prepare your application?"

    return msg
