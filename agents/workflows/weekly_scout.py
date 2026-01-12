"""
IvyQuest v10.0 - Weekly Scout Workflow
=====================================

Weekly opportunity and award recommendations based on student profiles.

Schedule: Monday at 9 AM (0 9 * * 1)

Logic:
1. Analyze student profile and current tracked items
2. Find new matching opportunities and awards
3. Score and rank by fit
4. Send personalized weekly digest
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import structlog

from .base import BaseWorkflow

logger = structlog.get_logger()


class WeeklyScoutWorkflow(BaseWorkflow):
    """
    Sends weekly opportunity and award recommendations.

    Runs every Monday to provide fresh recommendations
    based on student profile and interests.
    """

    name = "weekly_scout"
    schedule = "0 9 * * 1"  # Monday at 9 AM
    description = "Weekly opportunity and award recommendations"

    # Configuration
    MAX_OPPORTUNITIES = 3       # Max opportunities to recommend
    MAX_AWARDS = 2              # Max awards to recommend
    MIN_FIT_SCORE = 0.6         # Minimum fit score to recommend
    LOOKBACK_DAYS = 7           # Don't recommend items sent in last 7 days

    async def get_eligible_profiles(self) -> List[str]:
        """
        Find active student profiles.

        Returns:
            List of profile UUIDs eligible for weekly scout
        """
        try:
            result = self.db.table('profiles').select('id').eq(
                'role', 'student'
            ).execute()

            profiles = [p['id'] for p in result.data] if result.data else []
            self.logger.info("eligible_profiles", count=len(profiles))
            return profiles

        except Exception as e:
            self.logger.error("get_eligible_profiles_error", error=str(e))
            return []

    async def process_profile(self, profile_id: str) -> bool:
        """
        Generate and send weekly recommendations for a profile.

        Args:
            profile_id: The profile UUID

        Returns:
            True if recommendations were sent
        """
        # Check notification preferences
        if not await self.check_notification_preferences(profile_id, 'weekly_digest'):
            self.logger.debug("weekly_digest_disabled", profile_id=profile_id)
            return False

        # Get profile data for matching
        profile_data = await self._get_profile_data(profile_id)
        if not profile_data:
            return False

        # Get workflow state to avoid duplicate recommendations
        state = await self.get_workflow_state(profile_id)
        recently_recommended = state.get('state', {}).get('recently_recommended', []) if state else []

        # Find matching opportunities
        opportunities = await self._find_matching_opportunities(
            profile_id, profile_data, recently_recommended
        )

        # Find matching awards
        awards = await self._find_matching_awards(
            profile_id, profile_data, recently_recommended
        )

        # If nothing to recommend, skip
        if not opportunities and not awards:
            self.logger.debug("no_recommendations", profile_id=profile_id)
            return False

        # Create digest notification
        first_name = profile_data.get('first_name', 'there')
        notification_sent = await self._send_weekly_digest(
            profile_id=profile_id,
            first_name=first_name,
            opportunities=opportunities,
            awards=awards,
        )

        if notification_sent:
            # Update workflow state
            new_recommended = [
                *[f"opp_{o['id']}" for o in opportunities],
                *[f"award_{a['id']}" for a in awards],
            ]

            # Keep only last 2 weeks of recommendations
            all_recommended = recently_recommended + new_recommended
            cutoff_count = 20  # Keep last 20 items
            all_recommended = all_recommended[-cutoff_count:]

            await self.update_workflow_state(
                profile_id=profile_id,
                state={
                    'recently_recommended': all_recommended,
                    'last_digest': datetime.utcnow().isoformat(),
                    'opportunities_count': len(opportunities),
                    'awards_count': len(awards),
                }
            )

        return notification_sent

    async def _get_profile_data(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get profile data for matching.

        Args:
            profile_id: The profile UUID

        Returns:
            Profile data dictionary
        """
        try:
            result = self.db.table('profiles').select(
                'first_name, grade, narrative_themes, narrative_brand_statement'
            ).eq('id', profile_id).maybe_single().execute()

            if result.data:
                # Also get psychometric data
                psych_result = self.db.table('student_psychometrics').select(
                    'spike_category, interests'
                ).eq('profile_id', profile_id).maybe_single().execute()

                data = result.data
                if psych_result and psych_result.data:
                    data['spike_category'] = psych_result.data.get('spike_category')
                    data['interests'] = psych_result.data.get('interests', [])

                return data

            return None

        except Exception as e:
            self.logger.error("get_profile_data_error", profile_id=profile_id, error=str(e))
            return None

    async def _find_matching_opportunities(
        self,
        profile_id: str,
        profile_data: Dict[str, Any],
        recently_recommended: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Find opportunities matching the student's profile.

        Args:
            profile_id: The profile UUID
            profile_data: Student profile data
            recently_recommended: List of recently recommended item keys

        Returns:
            List of matching opportunities with scores
        """
        matching = []

        try:
            # Get already tracked opportunities
            tracked_result = self.db.table('student_opportunities').select(
                'opportunity_id'
            ).eq('profile_id', profile_id).execute()

            tracked_ids = {t['opportunity_id'] for t in tracked_result.data} if tracked_result.data else set()

            # Get active opportunities with upcoming deadlines
            deadline_threshold = datetime.utcnow() + timedelta(days=60)
            opp_result = self.db.table('opportunities').select(
                'id, name, type, category, prestige_score, application_deadline, description'
            ).eq('is_active', True).gte(
                'application_deadline', datetime.utcnow().isoformat()
            ).lte(
                'application_deadline', deadline_threshold.isoformat()
            ).execute()

            if not opp_result.data:
                return []

            # Score and filter opportunities
            spike = profile_data.get('spike_category', '').lower()
            interests = [i.lower() for i in profile_data.get('interests', [])]
            grade = profile_data.get('grade', 11)

            for opp in opp_result.data:
                opp_id = opp['id']

                # Skip if already tracked
                if opp_id in tracked_ids:
                    continue

                # Skip if recently recommended
                if f"opp_{opp_id}" in recently_recommended:
                    continue

                # Calculate fit score
                fit_score = self._calculate_opportunity_fit(opp, spike, interests, grade)

                if fit_score >= self.MIN_FIT_SCORE:
                    matching.append({
                        'id': opp_id,
                        'name': opp['name'],
                        'type': opp['type'],
                        'category': opp.get('category'),
                        'prestige_score': opp.get('prestige_score', 5),
                        'deadline': opp.get('application_deadline'),
                        'fit_score': fit_score,
                        'description': opp.get('description', '')[:200],
                    })

            # Sort by fit score and take top N
            matching.sort(key=lambda x: x['fit_score'], reverse=True)
            matching = matching[:self.MAX_OPPORTUNITIES]

        except Exception as e:
            self.logger.error(
                "find_matching_opportunities_error",
                profile_id=profile_id,
                error=str(e)
            )

        return matching

    async def _find_matching_awards(
        self,
        profile_id: str,
        profile_data: Dict[str, Any],
        recently_recommended: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Find awards matching the student's profile.

        Args:
            profile_id: The profile UUID
            profile_data: Student profile data
            recently_recommended: List of recently recommended item keys

        Returns:
            List of matching awards with scores
        """
        matching = []

        try:
            # Get already tracked awards
            tracked_result = self.db.table('student_awards').select(
                'award_id'
            ).eq('profile_id', profile_id).execute()

            tracked_ids = {t['award_id'] for t in tracked_result.data} if tracked_result.data else set()

            # Get active awards with upcoming deadlines
            deadline_threshold = datetime.utcnow() + timedelta(days=90)
            award_result = self.db.table('awards').select(
                'id, name, category, level, prestige_score, deadline, description'
            ).eq('is_active', True).gte(
                'deadline', datetime.utcnow().isoformat()
            ).lte(
                'deadline', deadline_threshold.isoformat()
            ).execute()

            if not award_result.data:
                return []

            # Score and filter awards
            spike = profile_data.get('spike_category', '').lower()
            interests = [i.lower() for i in profile_data.get('interests', [])]

            for award in award_result.data:
                award_id = award['id']

                # Skip if already tracked
                if award_id in tracked_ids:
                    continue

                # Skip if recently recommended
                if f"award_{award_id}" in recently_recommended:
                    continue

                # Calculate fit score
                fit_score = self._calculate_award_fit(award, spike, interests)

                if fit_score >= self.MIN_FIT_SCORE:
                    matching.append({
                        'id': award_id,
                        'name': award['name'],
                        'category': award.get('category'),
                        'level': award.get('level'),
                        'prestige_score': award.get('prestige_score', 5),
                        'deadline': award.get('deadline'),
                        'fit_score': fit_score,
                        'description': award.get('description', '')[:200],
                    })

            # Sort by fit score and take top N
            matching.sort(key=lambda x: x['fit_score'], reverse=True)
            matching = matching[:self.MAX_AWARDS]

        except Exception as e:
            self.logger.error(
                "find_matching_awards_error",
                profile_id=profile_id,
                error=str(e)
            )

        return matching

    def _calculate_opportunity_fit(
        self,
        opp: Dict[str, Any],
        spike: str,
        interests: List[str],
        grade: int
    ) -> float:
        """Calculate fit score for an opportunity."""
        score = 0.5  # Base score

        opp_category = (opp.get('category') or '').lower()
        opp_type = (opp.get('type') or '').lower()

        # Category match with spike
        if spike and opp_category == spike:
            score += 0.3

        # Interest overlap
        opp_text = f"{opp.get('name', '')} {opp.get('description', '')}".lower()
        for interest in interests:
            if interest in opp_text:
                score += 0.1
                break

        # Prestige bonus
        prestige = opp.get('prestige_score', 5)
        if prestige >= 8:
            score += 0.1

        return min(score, 1.0)

    def _calculate_award_fit(
        self,
        award: Dict[str, Any],
        spike: str,
        interests: List[str]
    ) -> float:
        """Calculate fit score for an award."""
        score = 0.5  # Base score

        award_category = (award.get('category') or '').lower()

        # Category match with spike
        if spike and award_category == spike:
            score += 0.3

        # Interest overlap
        award_text = f"{award.get('name', '')} {award.get('description', '')}".lower()
        for interest in interests:
            if interest in award_text:
                score += 0.1
                break

        # Level/prestige bonus
        level = (award.get('level') or '').lower()
        if level in ['national', 'international']:
            score += 0.1

        return min(score, 1.0)

    async def _send_weekly_digest(
        self,
        profile_id: str,
        first_name: str,
        opportunities: List[Dict],
        awards: List[Dict]
    ) -> bool:
        """
        Send the weekly digest notification.

        Args:
            profile_id: The profile UUID
            first_name: Student's first name
            opportunities: List of recommended opportunities
            awards: List of recommended awards

        Returns:
            True if notification was sent
        """
        # Build message
        total_count = len(opportunities) + len(awards)
        title = f"Your weekly picks are here, {first_name}!"

        message_parts = [f"We found {total_count} new items for you this week:"]

        if opportunities:
            message_parts.append(f"\n{len(opportunities)} Opportunities:")
            for opp in opportunities[:2]:
                message_parts.append(f"  • {opp['name']}")

        if awards:
            message_parts.append(f"\n{len(awards)} Awards:")
            for award in awards[:2]:
                message_parts.append(f"  • {award['name']}")

        message = "\n".join(message_parts)

        notification_id = await self.create_notification(
            profile_id=profile_id,
            title=title,
            message=message,
            notification_type='opportunity',
            action_url="/dashboard?tab=opportunities&view=recommended",
            action_label="View All",
            metadata={
                'digest_type': 'weekly',
                'opportunities': [o['id'] for o in opportunities],
                'awards': [a['id'] for a in awards],
                'total_count': total_count,
            }
        )

        return notification_id is not None
