"""
IvyQuest v10.0 - Daily Check-in Workflow
========================================

Daily progress encouragement and EDS (Early Distress Signal) monitoring.

Schedule: Daily at 3 PM (user-configurable)

Logic:
1. Review student progress against their game plan
2. Celebrate small wins and milestones
3. Monitor for distress signals (dropping engagement, missed deadlines)
4. Send personalized encouragement or gentle nudge
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import structlog

from .base import BaseWorkflow

logger = structlog.get_logger()


class DailyCheckinWorkflow(BaseWorkflow):
    """
    Daily progress check-in and encouragement.

    Monitors engagement, celebrates wins, and provides motivation.
    Includes Early Distress Signal (EDS) detection.
    """

    name = "daily_checkin"
    schedule = "0 15 * * *"  # Daily at 3 PM
    description = "Daily progress encouragement and EDS monitoring"

    # EDS (Early Distress Signal) thresholds
    EDS_THRESHOLDS = {
        'days_inactive': 2,             # 2+ days without activity
        'missed_deadlines': 1,          # Any missed deadline
        'declining_engagement_days': 5, # Engagement declining over 5 days
        'abandoned_applications': 2,    # 2+ started but abandoned applications
    }

    # Encouragement templates
    ENCOURAGEMENT_TEMPLATES = {
        'progress_made': {
            'title': "Great progress, {first_name}!",
            'message': "You've been making steady progress on your journey. "
                      "Keep up the momentum!",
        },
        'streak': {
            'title': "{streak} day streak! Keep it up, {first_name}!",
            'message': "You've been active for {streak} days in a row. "
                      "That consistency will pay off!",
        },
        'milestone': {
            'title': "Milestone reached!",
            'message': "Congratulations, {first_name}! You've {milestone}. "
                      "That's a real achievement!",
        },
        'comeback': {
            'title': "Welcome back, {first_name}!",
            'message': "Good to see you again! Ready to pick up where you left off?",
        },
        'gentle_nudge': {
            'title': "Quick check-in, {first_name}",
            'message': "How are things going? We're here to help if you need anything.",
        },
    }

    async def get_eligible_profiles(self) -> List[str]:
        """
        Get active student profiles for daily check-in.

        Returns:
            List of profile UUIDs
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
        Process daily check-in for a profile.

        Args:
            profile_id: The profile UUID

        Returns:
            True if notification was sent
        """
        # Get profile data
        profile_data = await self._get_profile_data(profile_id)
        if not profile_data:
            return False

        # Check preferred contact time (skip if not their time)
        if not self._is_preferred_time(profile_data.get('preferred_contact_time')):
            return False

        # Get workflow state
        state = await self.get_workflow_state(profile_id)
        last_checkin = None
        if state:
            last_checkin_str = state.get('state', {}).get('last_checkin')
            if last_checkin_str:
                last_checkin = datetime.fromisoformat(last_checkin_str)

        # Don't check in more than once per day
        if last_checkin and (datetime.utcnow() - last_checkin).days < 1:
            return False

        # Calculate engagement metrics
        metrics = await self._calculate_engagement_metrics(profile_id, profile_data)

        # Check for distress signals
        eds_signals = self._detect_distress_signals(metrics)

        # Choose appropriate action
        if eds_signals:
            notification_sent = await self._handle_distress(
                profile_id, profile_data, eds_signals, metrics
            )
        else:
            notification_sent = await self._send_encouragement(
                profile_id, profile_data, metrics
            )

        # Update workflow state
        if notification_sent:
            await self.update_workflow_state(
                profile_id=profile_id,
                state={
                    'last_checkin': datetime.utcnow().isoformat(),
                    'last_metrics': metrics,
                    'eds_detected': len(eds_signals) > 0,
                }
            )

        return notification_sent

    async def _get_profile_data(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get profile data for check-in."""
        try:
            result = self.db.table('profiles').select(
                'first_name, last_activity_at, preferred_contact_time'
            ).eq('id', profile_id).maybe_single().execute()

            return result.data if result.data else None

        except Exception as e:
            self.logger.error("get_profile_data_error", profile_id=profile_id, error=str(e))
            return None

    def _is_preferred_time(self, preferred_time: Optional[str]) -> bool:
        """
        Check if current time matches user's preferred contact time.

        Args:
            preferred_time: Time string (HH:MM format)

        Returns:
            True if within preferred time window (1 hour buffer)
        """
        if not preferred_time:
            return True  # No preference, always OK

        try:
            # Parse preferred time
            pref_hour = int(preferred_time.split(':')[0])
            current_hour = datetime.utcnow().hour

            # Allow 1 hour buffer
            return abs(current_hour - pref_hour) <= 1

        except Exception:
            return True

    async def _calculate_engagement_metrics(
        self,
        profile_id: str,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate engagement metrics for the profile.

        Args:
            profile_id: The profile UUID
            profile_data: Basic profile data

        Returns:
            Metrics dictionary
        """
        metrics = {
            'days_since_activity': 0,
            'activity_streak': 0,
            'tracked_items': 0,
            'submitted_applications': 0,
            'missed_deadlines': 0,
            'recent_wins': [],
        }

        try:
            # Days since activity
            last_activity = profile_data.get('last_activity_at')
            if last_activity:
                last_dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                metrics['days_since_activity'] = (datetime.utcnow() - last_dt).days

            # Count tracked items
            opps_result = self.db.table('student_opportunities').select(
                'id, status'
            ).eq('profile_id', profile_id).execute()

            if opps_result.data:
                metrics['tracked_items'] += len([
                    o for o in opps_result.data if o['status'] == 'tracking'
                ])
                metrics['submitted_applications'] += len([
                    o for o in opps_result.data if o['status'] == 'submitted'
                ])

            awards_result = self.db.table('student_awards').select(
                'id, status'
            ).eq('profile_id', profile_id).execute()

            if awards_result.data:
                metrics['tracked_items'] += len([
                    a for a in awards_result.data if a['status'] == 'tracking'
                ])

                # Check for wins
                wins = [a for a in awards_result.data if a['status'] == 'won']
                metrics['recent_wins'] = wins[:3]

            # Count missed deadlines (opportunities past deadline still in 'tracking')
            # This is a simplified check
            missed_count = 0
            if opps_result.data:
                for opp in opps_result.data:
                    if opp['status'] == 'tracking':
                        # Would need to join with opportunities table
                        # Simplified: count as potential miss
                        pass
            metrics['missed_deadlines'] = missed_count

            # Calculate activity streak (simplified)
            metrics['activity_streak'] = max(0, 7 - metrics['days_since_activity'])

        except Exception as e:
            self.logger.error(
                "calculate_metrics_error",
                profile_id=profile_id,
                error=str(e)
            )

        return metrics

    def _detect_distress_signals(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Detect early distress signals.

        Args:
            metrics: Engagement metrics

        Returns:
            List of detected distress signal types
        """
        signals = []

        if metrics.get('days_since_activity', 0) >= self.EDS_THRESHOLDS['days_inactive']:
            signals.append('prolonged_inactivity')

        if metrics.get('missed_deadlines', 0) >= self.EDS_THRESHOLDS['missed_deadlines']:
            signals.append('missed_deadline')

        # Would add more sophisticated checks here
        # - Declining engagement trend
        # - Abandoned applications
        # - Unusual patterns

        return signals

    async def _handle_distress(
        self,
        profile_id: str,
        profile_data: Dict[str, Any],
        eds_signals: List[str],
        metrics: Dict[str, Any]
    ) -> bool:
        """
        Handle detected distress signals.

        Args:
            profile_id: The profile UUID
            profile_data: Profile data
            eds_signals: Detected distress signals
            metrics: Engagement metrics

        Returns:
            True if notification was sent
        """
        first_name = profile_data.get('first_name', 'there')

        # For mild distress, send gentle nudge
        if 'prolonged_inactivity' in eds_signals and len(eds_signals) == 1:
            template = self.ENCOURAGEMENT_TEMPLATES['comeback']
            notification_id = await self.create_notification(
                profile_id=profile_id,
                title=template['title'].format(first_name=first_name),
                message=template['message'].format(first_name=first_name),
                notification_type='info',
                action_url="/dashboard",
                action_label="Continue",
                metadata={'eds_signals': eds_signals, 'metrics': metrics}
            )
            return notification_id is not None

        # For more serious distress, create coach task
        if len(eds_signals) > 1 or 'missed_deadline' in eds_signals:
            try:
                self.db.table('coach_tasks').insert({
                    'profile_id': profile_id,
                    'task_type': 'followup',
                    'priority': 'medium',
                    'title': f"EDS: Check in with {first_name}",
                    'description': f"Early distress signals detected: {', '.join(eds_signals)}. "
                                 f"Days inactive: {metrics.get('days_since_activity', 0)}. "
                                 f"Recommend personal outreach.",
                    'status': 'pending',
                }).execute()

                self.logger.info(
                    "eds_escalated",
                    profile_id=profile_id,
                    signals=eds_signals
                )

            except Exception as e:
                self.logger.error(
                    "eds_escalation_error",
                    profile_id=profile_id,
                    error=str(e)
                )

            # Still send a gentle notification
            template = self.ENCOURAGEMENT_TEMPLATES['gentle_nudge']
            notification_id = await self.create_notification(
                profile_id=profile_id,
                title=template['title'].format(first_name=first_name),
                message=template['message'].format(first_name=first_name),
                notification_type='info',
                action_url="/dashboard",
                action_label="Check In",
                metadata={'eds_signals': eds_signals}
            )
            return notification_id is not None

        return False

    async def _send_encouragement(
        self,
        profile_id: str,
        profile_data: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> bool:
        """
        Send appropriate encouragement based on metrics.

        Args:
            profile_id: The profile UUID
            profile_data: Profile data
            metrics: Engagement metrics

        Returns:
            True if notification was sent
        """
        first_name = profile_data.get('first_name', 'there')

        # Check for recent wins
        if metrics.get('recent_wins'):
            template = self.ENCOURAGEMENT_TEMPLATES['milestone']
            notification_id = await self.create_notification(
                profile_id=profile_id,
                title=template['title'],
                message=template['message'].format(
                    first_name=first_name,
                    milestone="won an award"
                ),
                notification_type='celebration',
                action_url="/dashboard?tab=awards",
                action_label="View Awards",
            )
            return notification_id is not None

        # Check for streak
        streak = metrics.get('activity_streak', 0)
        if streak >= 3:
            template = self.ENCOURAGEMENT_TEMPLATES['streak']
            notification_id = await self.create_notification(
                profile_id=profile_id,
                title=template['title'].format(streak=streak, first_name=first_name),
                message=template['message'].format(streak=streak),
                notification_type='success',
                action_url="/dashboard",
                action_label="Keep Going",
            )
            return notification_id is not None

        # Default: progress message (but not too frequently)
        # Only send if there's something to report
        if metrics.get('tracked_items', 0) > 0 or metrics.get('submitted_applications', 0) > 0:
            template = self.ENCOURAGEMENT_TEMPLATES['progress_made']
            notification_id = await self.create_notification(
                profile_id=profile_id,
                title=template['title'].format(first_name=first_name),
                message=template['message'],
                notification_type='info',
                action_url="/dashboard",
                action_label="View Progress",
            )
            return notification_id is not None

        # Nothing significant to report, skip notification
        return False
