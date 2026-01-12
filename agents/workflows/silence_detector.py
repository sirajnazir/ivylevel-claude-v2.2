"""
IvyQuest v10.0 - Silence Detector Workflow
==========================================

Detects students who haven't engaged in 72+ hours and sends
personalized re-engagement notifications.

Schedule: Every 4 hours (0 */4 * * *)

Logic:
1. Find profiles with last_activity_at > 72 hours ago
2. Check if silence notification was already sent recently
3. Generate personalized nudge based on their current state
4. Create notification with actionable next step
5. Escalate to coach if 7+ days of silence
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import structlog

from .base import BaseWorkflow

logger = structlog.get_logger()


class SilenceDetectorWorkflow(BaseWorkflow):
    """
    Detects and re-engages inactive students.

    Sends personalized nudges after 72 hours of inactivity.
    Escalates to coach after 7 days.
    """

    name = "silence_detector"
    schedule = "0 */4 * * *"  # Every 4 hours
    description = "Detect 72h+ inactivity and send re-engagement notifications"

    # Configuration
    SILENCE_THRESHOLD_HOURS = 72        # 3 days
    ESCALATION_THRESHOLD_HOURS = 168    # 7 days
    MIN_HOURS_BETWEEN_NUDGES = 48       # Don't spam - wait 48h between nudges
    MAX_NUDGES_PER_PROFILE = 3          # Max nudges before escalating

    # Personalized message templates
    NUDGE_TEMPLATES = {
        'has_deadline': {
            'title': "Don't miss your deadline, {first_name}!",
            'message': "You have {count} upcoming deadline(s). Let's make sure you're on track!",
            'action_label': "View Deadlines",
            'action_url': "/dashboard?tab=opportunities",
        },
        'has_incomplete_profile': {
            'title': "Let's complete your profile, {first_name}",
            'message': "A complete profile helps us give you better recommendations. Just a few more steps!",
            'action_label': "Complete Profile",
            'action_url': "/profile",
        },
        'has_recommendations': {
            'title': "New opportunities for you, {first_name}!",
            'message': "We've found {count} opportunities that match your interests. Check them out!",
            'action_label': "View Opportunities",
            'action_url': "/dashboard?tab=opportunities",
        },
        'general': {
            'title': "We miss you, {first_name}!",
            'message': "Your college journey awaits. Let's pick up where we left off.",
            'action_label': "Continue",
            'action_url': "/dashboard",
        },
    }

    async def get_eligible_profiles(self) -> List[str]:
        """
        Find profiles with 72+ hours of inactivity.

        Returns:
            List of profile UUIDs that need re-engagement
        """
        threshold = datetime.utcnow() - timedelta(hours=self.SILENCE_THRESHOLD_HOURS)

        try:
            result = self.db.table('profiles').select('id').eq(
                'role', 'student'
            ).lt(
                'last_activity_at', threshold.isoformat()
            ).execute()

            profiles = [p['id'] for p in result.data] if result.data else []
            self.logger.info("eligible_profiles", count=len(profiles))
            return profiles

        except Exception as e:
            self.logger.error("get_eligible_profiles_error", error=str(e))
            return []

    async def process_profile(self, profile_id: str) -> bool:
        """
        Process a single inactive profile.

        Args:
            profile_id: The profile UUID

        Returns:
            True if notification was sent
        """
        # Check notification preferences
        if not await self.check_notification_preferences(profile_id, 'silence_nudges'):
            self.logger.debug("silence_nudges_disabled", profile_id=profile_id)
            return False

        # Get workflow state to check nudge history
        state = await self.get_workflow_state(profile_id)
        if state:
            nudge_count = state.get('state', {}).get('nudge_count', 0)
            last_nudge = state.get('state', {}).get('last_nudge_at')

            # Check if we've hit max nudges
            if nudge_count >= self.MAX_NUDGES_PER_PROFILE:
                # Check for escalation
                return await self._maybe_escalate(profile_id, state)

            # Check if enough time has passed since last nudge
            if last_nudge:
                last_nudge_dt = datetime.fromisoformat(last_nudge)
                hours_since_nudge = (datetime.utcnow() - last_nudge_dt).total_seconds() / 3600
                if hours_since_nudge < self.MIN_HOURS_BETWEEN_NUDGES:
                    self.logger.debug(
                        "too_soon_for_nudge",
                        profile_id=profile_id,
                        hours_since_nudge=hours_since_nudge
                    )
                    return False
        else:
            nudge_count = 0

        # Get profile context for personalization
        context = await self._get_profile_context(profile_id)

        # Select appropriate template
        template = self._select_template(context)

        # Format message with context
        title = template['title'].format(**context)
        message = template['message'].format(**context)

        # Create notification
        notification_id = await self.create_notification(
            profile_id=profile_id,
            title=title,
            message=message,
            notification_type='silence_alert',
            action_url=template.get('action_url'),
            action_label=template.get('action_label'),
            metadata={
                'nudge_count': nudge_count + 1,
                'template': template.get('type', 'general'),
                'context': context,
            }
        )

        if notification_id:
            # Update workflow state
            await self.update_workflow_state(
                profile_id=profile_id,
                state={
                    'nudge_count': nudge_count + 1,
                    'last_nudge_at': datetime.utcnow().isoformat(),
                    'last_notification_id': notification_id,
                }
            )
            return True

        return False

    async def _get_profile_context(self, profile_id: str) -> Dict[str, Any]:
        """
        Get context for personalizing the nudge message.

        Args:
            profile_id: The profile UUID

        Returns:
            Context dictionary for template formatting
        """
        context = {
            'first_name': 'there',  # Default fallback
            'count': 0,
            'has_deadline': False,
            'has_incomplete_profile': False,
            'has_recommendations': False,
        }

        try:
            # Get profile info
            profile_result = self.db.table('profiles').select(
                'first_name, narrative_brand_statement, grade'
            ).eq('id', profile_id).maybe_single().execute()

            if profile_result.data:
                context['first_name'] = profile_result.data.get('first_name', 'there')
                context['has_incomplete_profile'] = not profile_result.data.get('narrative_brand_statement')

            # Check for upcoming deadlines
            upcoming = datetime.utcnow() + timedelta(days=30)
            deadlines_result = self.db.table('student_opportunities').select(
                'id'
            ).eq('profile_id', profile_id).eq('status', 'tracking').execute()

            # Count opportunities with deadlines
            if deadlines_result.data:
                context['count'] = len(deadlines_result.data)
                context['has_deadline'] = context['count'] > 0

            # Check for new recommendations (simplified - would integrate with opportunity agent)
            context['has_recommendations'] = True  # Assume we have recommendations

        except Exception as e:
            self.logger.error("get_profile_context_error", profile_id=profile_id, error=str(e))

        return context

    def _select_template(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select the most appropriate nudge template.

        Args:
            context: Profile context

        Returns:
            Template dictionary
        """
        # Priority order for template selection
        if context.get('has_deadline'):
            template = self.NUDGE_TEMPLATES['has_deadline'].copy()
            template['type'] = 'has_deadline'
        elif context.get('has_incomplete_profile'):
            template = self.NUDGE_TEMPLATES['has_incomplete_profile'].copy()
            template['type'] = 'has_incomplete_profile'
        elif context.get('has_recommendations'):
            template = self.NUDGE_TEMPLATES['has_recommendations'].copy()
            template['type'] = 'has_recommendations'
        else:
            template = self.NUDGE_TEMPLATES['general'].copy()
            template['type'] = 'general'

        return template

    async def _maybe_escalate(self, profile_id: str, state: Dict) -> bool:
        """
        Check if profile should be escalated to coach.

        Args:
            profile_id: The profile UUID
            state: Current workflow state

        Returns:
            True if escalation was created
        """
        # Check if already escalated
        if state.get('state', {}).get('escalated'):
            return False

        # Get last activity
        try:
            profile_result = self.db.table('profiles').select(
                'last_activity_at, first_name, last_name'
            ).eq('id', profile_id).maybe_single().execute()

            if not profile_result.data:
                return False

            last_activity = datetime.fromisoformat(
                profile_result.data.get('last_activity_at', datetime.utcnow().isoformat())
            )
            hours_inactive = (datetime.utcnow() - last_activity).total_seconds() / 3600

            if hours_inactive >= self.ESCALATION_THRESHOLD_HOURS:
                # Create coach task
                first_name = profile_result.data.get('first_name', 'Student')
                last_name = profile_result.data.get('last_name', '')

                self.db.table('coach_tasks').insert({
                    'profile_id': profile_id,
                    'task_type': 'silence_intervention',
                    'priority': 'medium',
                    'title': f"Extended silence: {first_name} {last_name}",
                    'description': f"Student has been inactive for {int(hours_inactive)} hours "
                                 f"({int(hours_inactive / 24)} days). Multiple automated nudges "
                                 f"have not resulted in re-engagement. Personal outreach recommended.",
                    'status': 'pending',
                }).execute()

                # Update workflow state
                await self.update_workflow_state(
                    profile_id=profile_id,
                    state={
                        **state.get('state', {}),
                        'escalated': True,
                        'escalated_at': datetime.utcnow().isoformat(),
                    },
                    run_count_increment=0  # Don't increment run count for escalation
                )

                self.logger.info(
                    "profile_escalated",
                    profile_id=profile_id,
                    hours_inactive=hours_inactive
                )
                return True

        except Exception as e:
            self.logger.error("escalation_error", profile_id=profile_id, error=str(e))

        return False
