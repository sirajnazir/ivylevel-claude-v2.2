"""
Proactive Opportunity Matcher v10.0
===================================

Hourly job that matches students to relevant opportunities based on:
- Profile archetype and interests
- Deadlines approaching
- Previously recommended but not applied opportunities
- New opportunities matching their spike

Creates nudges in nudge_queue for delivery.

Tables queried:
- opportunities (uses 'application_deadline' column)
- awards (uses 'deadline' column)
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import structlog

from .config import is_feature_enabled

logger = structlog.get_logger()

# Centralized scoring configuration
MATCH_SCORING = {
    "base_deadline_score": 0.15,
    "archetype_match_bonus": 0.25,
    "major_match_bonus": 0.15,
    "grade_match_bonus": 0.15,
    "prestige_bonus": 0.15,
    "category_match_bonus": 0.15,
    "minimum_match_threshold": 0.3,
}

# Archetype to category/keyword mapping
ARCHETYPE_KEYWORDS = {
    "academic_perfectionist": ["academic", "research", "scholarship", "science", "stem", "math"],
    "future_founder": ["entrepreneurship", "startup", "business", "leadership", "innovation"],
    "stem_innovator": ["stem", "science", "technology", "engineering", "math", "research", "computer"],
    "creative_storyteller": ["arts", "writing", "creative", "media", "journalism", "film", "design"],
    "global_changemaker": ["social", "community", "international", "volunteer", "service", "global"],
    "athletic_scholar": ["sports", "athletic", "ncaa", "fitness"],
}

# Category to archetype affinity mapping
CATEGORY_ARCHETYPE_AFFINITY = {
    "Academic & STEM": ["academic_perfectionist", "stem_innovator"],
    "Leadership & Community": ["future_founder", "global_changemaker"],
    "Arts & Humanities": ["creative_storyteller"],
    "Athletics": ["athletic_scholar"],
    "Business": ["future_founder"],
    "Research": ["academic_perfectionist", "stem_innovator"],
    "Service": ["global_changemaker"],
}


async def match_opportunities_for_profile(
    supabase_client,
    profile_id: str,
    max_matches: int = 3,
) -> List[Dict[str, Any]]:
    """
    Match opportunities and awards to a student profile.

    Args:
        supabase_client: Supabase client instance
        profile_id: Student profile ID
        max_matches: Maximum number of matches to return

    Returns:
        List of matched items with relevance scores
    """
    matches = []

    try:
        # Get student profile
        profile_result = supabase_client.table("profiles").select(
            "id, first_name, grade, archetype, target_major, intended_major, "
            "target_schools, spike, pillars"
        ).eq("id", profile_id).single().execute()

        if not profile_result.data:
            logger.warning("profile_not_found", profile_id=profile_id)
            return []

        profile = profile_result.data

        # Get deadline cutoffs
        now = datetime.now()
        deadline_cutoff = (now + timedelta(days=30)).isoformat()
        now_iso = now.isoformat()

        # Query OPPORTUNITIES with upcoming deadlines
        try:
            opportunities_result = supabase_client.table("opportunities").select(
                "id, name, organization, type, category, application_deadline, "
                "eligibility, requirements, prestige_score, tier, jenny_note"
            ).lte(
                "application_deadline", deadline_cutoff
            ).gte(
                "application_deadline", now_iso
            ).eq(
                "is_active", True
            ).order(
                "application_deadline"
            ).limit(50).execute()

            opportunities = opportunities_result.data or []
            logger.debug("opportunities_fetched", count=len(opportunities))
        except Exception as e:
            logger.warning("opportunities_fetch_failed", error=str(e))
            opportunities = []

        # Query AWARDS with upcoming deadlines
        try:
            awards_result = supabase_client.table("awards").select(
                "id, name, organization, category, level, deadline, "
                "eligibility, requirements, prestige_score, ideal_candidate_profile, jenny_strategy"
            ).lte(
                "deadline", deadline_cutoff
            ).gte(
                "deadline", now_iso
            ).eq(
                "is_active", True
            ).order(
                "deadline"
            ).limit(50).execute()

            awards = awards_result.data or []
            logger.debug("awards_fetched", count=len(awards))
        except Exception as e:
            logger.warning("awards_fetch_failed", error=str(e))
            awards = []

        # Process opportunities
        for opp in opportunities:
            score = _calculate_match_score(profile, opp, source="opportunity")
            if score >= MATCH_SCORING["minimum_match_threshold"]:
                matches.append({
                    "source": "opportunity",
                    "source_id": opp["id"],
                    "opportunity_id": opp["id"],
                    "opportunity_name": opp["name"],
                    "opportunity_type": opp.get("type"),
                    "organization": opp.get("organization"),
                    "category": opp.get("category"),
                    "deadline": opp.get("application_deadline"),
                    "prestige_score": opp.get("prestige_score"),
                    "jenny_note": opp.get("jenny_note"),
                    "match_score": score,
                    "match_reasons": _get_match_reasons(profile, opp, source="opportunity"),
                })

        # Process awards
        for award in awards:
            score = _calculate_match_score(profile, award, source="award")
            if score >= MATCH_SCORING["minimum_match_threshold"]:
                matches.append({
                    "source": "award",
                    "source_id": award["id"],
                    "opportunity_id": award["id"],  # Keep for backward compatibility
                    "opportunity_name": award["name"],
                    "opportunity_type": "award",
                    "organization": award.get("organization"),
                    "category": award.get("category"),
                    "deadline": award.get("deadline"),
                    "prestige_score": award.get("prestige_score"),
                    "jenny_note": award.get("jenny_strategy"),
                    "match_score": score,
                    "match_reasons": _get_match_reasons(profile, award, source="award"),
                })

        # Sort by score and limit
        matches.sort(key=lambda x: x["match_score"], reverse=True)

        logger.info(
            "opportunity_matching_completed",
            profile_id=profile_id,
            opportunities_checked=len(opportunities),
            awards_checked=len(awards),
            matches_found=len(matches[:max_matches]),
        )

        return matches[:max_matches]

    except Exception as e:
        logger.error(
            "opportunity_match_error",
            profile_id=profile_id,
            error=str(e),
        )
        return []


def _calculate_match_score(
    profile: Dict[str, Any],
    item: Dict[str, Any],
    source: str = "opportunity"
) -> float:
    """
    Calculate a match score between profile and opportunity/award.

    Args:
        profile: Student profile data
        item: Opportunity or award data
        source: "opportunity" or "award"

    Returns:
        Float score between 0.0 and 1.0
    """
    score = 0.0
    archetype = (profile.get("archetype") or "").lower()
    major = (profile.get("target_major") or profile.get("intended_major") or "").lower()
    grade = profile.get("grade")
    spike = (profile.get("spike") or "").lower()
    pillars = profile.get("pillars") or []

    # Base score for having an upcoming deadline
    score += MATCH_SCORING["base_deadline_score"]

    # Category matching to archetype
    category = (item.get("category") or "").lower()
    if category and archetype:
        # Check direct category-archetype affinity
        for cat_name, archetypes in CATEGORY_ARCHETYPE_AFFINITY.items():
            if cat_name.lower() in category or category in cat_name.lower():
                if archetype in archetypes:
                    score += MATCH_SCORING["category_match_bonus"]
                    break

    # Archetype keyword matching
    archetype_kws = ARCHETYPE_KEYWORDS.get(archetype, [])
    item_text = " ".join([
        item.get("name", ""),
        item.get("organization", ""),
        item.get("category", ""),
        str(item.get("eligibility", "")),
    ]).lower()

    for keyword in archetype_kws:
        if keyword in item_text:
            score += MATCH_SCORING["archetype_match_bonus"]
            break

    # Major matching
    if major and len(major) > 2:
        if major in item_text:
            score += MATCH_SCORING["major_match_bonus"]
        # Also check common abbreviations
        elif major == "computer science" and any(kw in item_text for kw in ["cs", "programming", "software"]):
            score += MATCH_SCORING["major_match_bonus"]
        elif major == "engineering" and any(kw in item_text for kw in ["engineer", "stem"]):
            score += MATCH_SCORING["major_match_bonus"]

    # Grade/eligibility matching
    eligibility = item.get("eligibility")
    if grade and eligibility:
        elig_text = str(eligibility).lower()
        grade_map = {
            9: ["9th", "freshman", "9-12", "all grades", "high school"],
            10: ["10th", "sophomore", "10-12", "9-12", "all grades", "high school"],
            11: ["11th", "junior", "11-12", "9-12", "all grades", "high school"],
            12: ["12th", "senior", "11-12", "9-12", "all grades", "high school"],
        }
        for grade_term in grade_map.get(grade, []):
            if grade_term in elig_text:
                score += MATCH_SCORING["grade_match_bonus"]
                break

    # Prestige boost for high-prestige items
    prestige = item.get("prestige_score") or 0
    if prestige >= 8:
        score += MATCH_SCORING["prestige_bonus"]
    elif prestige >= 6:
        score += MATCH_SCORING["prestige_bonus"] * 0.5

    # Spike matching - student's unique strength area
    if spike and len(spike) > 2:
        if spike in item_text:
            score += 0.15  # Spike match bonus

    # For awards, check ideal_candidate_profile if available
    if source == "award":
        ideal_profile = (item.get("ideal_candidate_profile") or "").lower()
        if ideal_profile:
            if archetype:
                for kw in archetype_kws:
                    if kw in ideal_profile:
                        score += 0.1
                        break
            if spike and spike in ideal_profile:
                score += 0.1  # Spike mentioned in ideal candidate

    return min(score, 1.0)  # Cap at 1.0


def _get_match_reasons(
    profile: Dict[str, Any],
    item: Dict[str, Any],
    source: str = "opportunity"
) -> List[str]:
    """Generate human-readable match reasons."""
    reasons = []
    archetype = (profile.get("archetype") or "").replace("_", " ").title()

    # Deadline urgency
    deadline_field = "application_deadline" if source == "opportunity" else "deadline"
    deadline = item.get(deadline_field)
    if deadline:
        try:
            deadline_str = deadline.replace("Z", "") if isinstance(deadline, str) else str(deadline)
            deadline_dt = datetime.fromisoformat(deadline_str.split("T")[0])
            days_until = (deadline_dt - datetime.now()).days
            if days_until <= 7:
                reasons.append(f"⏰ Deadline in {days_until} days - act now!")
            elif days_until <= 14:
                reasons.append(f"📅 Deadline in {days_until} days")
        except Exception:
            pass

    # Archetype match
    if archetype:
        category = item.get("category", "")
        for cat_name, archetypes in CATEGORY_ARCHETYPE_AFFINITY.items():
            if cat_name.lower() in (category or "").lower():
                if profile.get("archetype", "").lower() in archetypes:
                    reasons.append(f"🎯 Matches your {archetype} profile")
                    break

    # Prestige
    prestige = item.get("prestige_score") or 0
    if prestige >= 8:
        reasons.append("⭐ Highly prestigious opportunity")
    elif prestige >= 6:
        reasons.append("✨ Well-recognized opportunity")

    # Organization
    org = item.get("organization")
    if org:
        reasons.append(f"🏛️ By {org}")

    # Jenny note
    jenny_note = item.get("jenny_note") or item.get("jenny_strategy")
    if jenny_note:
        # Add a shortened version of Jenny's tip
        tip = jenny_note[:80] + "..." if len(jenny_note) > 80 else jenny_note
        reasons.append(f"💡 Jenny's tip: {tip}")

    return reasons[:4]  # Max 4 reasons


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
        "notifications_created": 0,
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

                # Create nudges and notifications for matches
                for match in matches:
                    # Check if similar nudge exists in last 24 hours
                    existing = supabase_client.table("nudge_queue").select("id").eq(
                        "profile_id", profile_id
                    ).eq("nudge_type", "opportunity_match").eq(
                        "metadata->>source_id", str(match["source_id"])
                    ).gte(
                        "created_at", (datetime.now() - timedelta(hours=24)).isoformat()
                    ).execute()

                    if existing.data:
                        continue  # Skip duplicate

                    # Create nudge
                    nudge = {
                        "profile_id": profile_id,
                        "nudge_type": "opportunity_match",
                        "priority": "high" if match["match_score"] > 0.7 else (
                            "medium" if match["match_score"] > 0.5 else "low"
                        ),
                        "message_draft": _generate_opportunity_nudge(match),
                        "metadata": {
                            "source": match["source"],
                            "source_id": str(match["source_id"]),
                            "opportunity_name": match["opportunity_name"],
                            "organization": match.get("organization"),
                            "category": match.get("category"),
                            "deadline": match.get("deadline"),
                            "match_score": match["match_score"],
                            "match_reasons": match["match_reasons"],
                        },
                        "status": "pending",
                        "created_at": datetime.now().isoformat(),
                    }

                    supabase_client.table("nudge_queue").insert(nudge).execute()
                    results["nudges_created"] += 1

                    # Also create proactive notification
                    notification = {
                        "profile_id": profile_id,
                        "notification_type": "opportunity_match",
                        "title": f"New Match: {match['opportunity_name']}",
                        "message": match["match_reasons"][0] if match["match_reasons"] else "Found a great opportunity for you!",
                        "priority": nudge["priority"],
                        "metadata": nudge["metadata"],
                        "status": "pending",
                        "created_at": datetime.now().isoformat(),
                    }

                    try:
                        supabase_client.table("proactive_notifications").insert(notification).execute()
                        results["notifications_created"] += 1
                    except Exception as e:
                        logger.warning("notification_create_failed", error=str(e))

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
    source = match.get("source", "opportunity")
    reasons = match.get("match_reasons", [])
    deadline = match.get("deadline", "")
    org = match.get("organization", "")

    # Build message
    item_type = "award" if source == "award" else "opportunity"
    msg = f"Hey! I found a great {item_type} for you: **{name}**"

    if org:
        msg += f" by {org}"
    msg += "!"

    # Add reason if available
    if reasons:
        # Skip emoji prefixes for the message
        reason = reasons[0]
        if reason.startswith(("⏰", "📅", "🎯", "⭐", "✨", "🏛️", "💡")):
            reason = reason[2:].strip()
        msg += f" {reason}."

    # Deadline urgency
    if deadline:
        try:
            deadline_str = deadline.replace("Z", "") if isinstance(deadline, str) else str(deadline)
            deadline_dt = datetime.fromisoformat(deadline_str.split("T")[0])
            days_until = (deadline_dt - datetime.now()).days
            if days_until <= 7:
                msg += f" The deadline is in just **{days_until} days** - we should start preparing!"
            elif days_until <= 14:
                msg += f" The deadline is {deadline_dt.strftime('%B %d')} - still time to prepare a strong application."
            else:
                msg += f" Deadline: {deadline_dt.strftime('%B %d')}."
        except Exception:
            pass

    msg += "\n\nWant me to help you prepare your application?"

    return msg
