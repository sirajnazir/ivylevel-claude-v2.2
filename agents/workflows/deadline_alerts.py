"""
IvyQuest v10.0 - Deadline Alerts Workflow
=========================================

Multi-tier deadline reminder system for tracked opportunities and awards.

Schedule: Daily at 9 AM (0 9 * * *)

Alert Tiers:
- 30 days: Low priority - "Time to start preparing"
- 7 days: Medium priority - "One week left"
- 3 days: High priority - "Critical deadline approaching"
- 1 day: Urgent - "Deadline tomorrow!"

Logic:
1. Find all tracked opportunities/awards with upcoming deadlines
2. Categorize by days remaining
3. Send appropriate tier notification
4. Track which alerts have been sent to avoid duplicates
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import structlog

from .base import BaseWorkflow

logger = structlog.get_logger()


class DeadlineAlertWorkflow(BaseWorkflow):
    """
    Sends multi-tier deadline reminders for tracked items.

    Alerts at 30, 7, 3, and 1 day marks.
    """

    name = "deadline_alerts"
    schedule = "0 9 * * *"  # Daily at 9 AM
    description = "Multi-tier deadline reminders (30/7/3/1 days)"

    # Alert tier configuration
    ALERT_TIERS = [
        {
            'days': 30,
            'type': 'deadline_low',
            'priority': 'low',
            'title_template': "30 days until {item_name} deadline",
            'message_template': "Start preparing your application for {item_name}. "
                               "Deadline: {deadline_date}.",
        },
        {
            'days': 7,
            'type': 'deadline_medium',
            'priority': 'medium',
            'title_template': "One week left: {item_name}",
            'message_template': "The deadline for {item_name} is in one week ({deadline_date}). "
                               "Time to finalize your application!",
        },
        {
            'days': 3,
            'type': 'deadline_high',
            'priority': 'high',
            'title_template': "3 days: {item_name} deadline approaching!",
            'message_template': "Critical: Only 3 days left to submit {item_name}. "
                               "Deadline: {deadline_date}. Don't miss this opportunity!",
        },
        {
            'days': 1,
            'type': 'urgent',
            'priority': 'urgent',
            'title_template': "TOMORROW: {item_name} deadline!",
            'message_template': "Final reminder: {item_name} is due TOMORROW ({deadline_date}). "
                               "Submit now!",
        },
    ]

    async def get_eligible_profiles(self) -> List[str]:
        """
        Find profiles with tracked items that have upcoming deadlines.

        Returns:
            List of profile UUIDs with upcoming deadlines
        """
        try:
            # Get all active students
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
        Process deadline alerts for a single profile.

        Args:
            profile_id: The profile UUID

        Returns:
            True if any notifications were sent
        """
        # Check notification preferences
        if not await self.check_notification_preferences(profile_id, 'deadline_alerts'):
            self.logger.debug("deadline_alerts_disabled", profile_id=profile_id)
            return False

        # Get workflow state for tracking sent alerts
        state = await self.get_workflow_state(profile_id)
        sent_alerts = state.get('state', {}).get('sent_alerts', {}) if state else {}

        notifications_sent = 0

        # Check opportunities
        opp_notifications = await self._check_opportunity_deadlines(
            profile_id, sent_alerts
        )
        notifications_sent += opp_notifications

        # Check awards
        award_notifications = await self._check_award_deadlines(
            profile_id, sent_alerts
        )
        notifications_sent += award_notifications

        # Update state if any notifications sent
        if notifications_sent > 0:
            await self.update_workflow_state(
                profile_id=profile_id,
                state={
                    'sent_alerts': sent_alerts,
                    'last_check': datetime.utcnow().isoformat(),
                }
            )

        return notifications_sent > 0

    async def _check_opportunity_deadlines(
        self,
        profile_id: str,
        sent_alerts: Dict[str, List[int]]
    ) -> int:
        """
        Check tracked opportunities for upcoming deadlines.

        Args:
            profile_id: The profile UUID
            sent_alerts: Dict tracking which alerts have been sent

        Returns:
            Number of notifications sent
        """
        notifications_sent = 0

        try:
            # Get tracked opportunities with deadlines
            result = self.db.table('student_opportunities').select(
                'id, opportunity_id, opportunities(name, application_deadline)'
            ).eq('profile_id', profile_id).eq('status', 'tracking').execute()

            if not result.data:
                return 0

            for tracked in result.data:
                opp = tracked.get('opportunities', {})
                deadline_str = opp.get('application_deadline')
                if not deadline_str:
                    continue

                opp_name = opp.get('name', 'Opportunity')
                opp_key = f"opp_{tracked['opportunity_id']}"

                sent = await self._process_deadline_item(
                    profile_id=profile_id,
                    item_key=opp_key,
                    item_name=opp_name,
                    deadline_str=deadline_str,
                    item_type='opportunity',
                    item_id=tracked['opportunity_id'],
                    sent_alerts=sent_alerts,
                )
                if sent:
                    notifications_sent += 1

        except Exception as e:
            self.logger.error(
                "check_opportunity_deadlines_error",
                profile_id=profile_id,
                error=str(e)
            )

        return notifications_sent

    async def _check_award_deadlines(
        self,
        profile_id: str,
        sent_alerts: Dict[str, List[int]]
    ) -> int:
        """
        Check tracked awards for upcoming deadlines.

        Args:
            profile_id: The profile UUID
            sent_alerts: Dict tracking which alerts have been sent

        Returns:
            Number of notifications sent
        """
        notifications_sent = 0

        try:
            # Get tracked awards with deadlines
            result = self.db.table('student_awards').select(
                'id, award_id, awards(name, deadline)'
            ).eq('profile_id', profile_id).eq('status', 'tracking').execute()

            if not result.data:
                return 0

            for tracked in result.data:
                award = tracked.get('awards', {})
                deadline_str = award.get('deadline')
                if not deadline_str:
                    continue

                award_name = award.get('name', 'Award')
                award_key = f"award_{tracked['award_id']}"

                sent = await self._process_deadline_item(
                    profile_id=profile_id,
                    item_key=award_key,
                    item_name=award_name,
                    deadline_str=deadline_str,
                    item_type='award',
                    item_id=tracked['award_id'],
                    sent_alerts=sent_alerts,
                )
                if sent:
                    notifications_sent += 1

        except Exception as e:
            self.logger.error(
                "check_award_deadlines_error",
                profile_id=profile_id,
                error=str(e)
            )

        return notifications_sent

    async def _process_deadline_item(
        self,
        profile_id: str,
        item_key: str,
        item_name: str,
        deadline_str: str,
        item_type: str,
        item_id: str,
        sent_alerts: Dict[str, List[int]]
    ) -> bool:
        """
        Process a single deadline item and send notification if needed.

        Args:
            profile_id: The profile UUID
            item_key: Unique key for tracking
            item_name: Display name of the item
            deadline_str: ISO format deadline date
            item_type: 'opportunity' or 'award'
            item_id: The item UUID
            sent_alerts: Tracking dict for sent alerts

        Returns:
            True if notification was sent
        """
        try:
            # Parse deadline
            deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            if hasattr(deadline, 'date'):
                deadline = datetime.combine(deadline.date(), datetime.min.time())

            # Calculate days until deadline
            days_until = (deadline - datetime.utcnow()).days

            # Check each tier
            for tier in self.ALERT_TIERS:
                tier_days = tier['days']

                # Check if we're at this tier
                if days_until != tier_days:
                    continue

                # Check if already sent for this tier
                if item_key not in sent_alerts:
                    sent_alerts[item_key] = []

                if tier_days in sent_alerts[item_key]:
                    continue

                # Send notification
                deadline_formatted = deadline.strftime('%B %d, %Y')
                title = tier['title_template'].format(
                    item_name=item_name,
                    deadline_date=deadline_formatted
                )
                message = tier['message_template'].format(
                    item_name=item_name,
                    deadline_date=deadline_formatted
                )

                # Determine action URL
                if item_type == 'opportunity':
                    action_url = f"/dashboard?tab=opportunities&id={item_id}"
                else:
                    action_url = f"/dashboard?tab=awards&id={item_id}"

                notification_id = await self.create_notification(
                    profile_id=profile_id,
                    title=title,
                    message=message,
                    notification_type=tier['type'],
                    action_url=action_url,
                    action_label="View Details",
                    metadata={
                        'item_type': item_type,
                        'item_id': item_id,
                        'item_name': item_name,
                        'days_until': days_until,
                        'tier': tier_days,
                        'priority': tier['priority'],
                    }
                )

                if notification_id:
                    sent_alerts[item_key].append(tier_days)
                    self.logger.info(
                        "deadline_alert_sent",
                        profile_id=profile_id,
                        item_type=item_type,
                        item_name=item_name,
                        days_until=days_until,
                        tier=tier_days
                    )
                    return True

        except Exception as e:
            self.logger.error(
                "process_deadline_error",
                profile_id=profile_id,
                item_name=item_name,
                error=str(e)
            )

        return False

    async def get_upcoming_deadlines(
        self,
        profile_id: str,
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get all upcoming deadlines for a profile.

        Utility method for dashboard display.

        Args:
            profile_id: The profile UUID
            days_ahead: How many days ahead to look

        Returns:
            List of deadline items with details
        """
        deadlines = []
        cutoff = datetime.utcnow() + timedelta(days=days_ahead)

        try:
            # Get opportunities
            opp_result = self.db.table('student_opportunities').select(
                'opportunity_id, opportunities(name, application_deadline, type)'
            ).eq('profile_id', profile_id).eq('status', 'tracking').execute()

            if opp_result.data:
                for item in opp_result.data:
                    opp = item.get('opportunities', {})
                    deadline_str = opp.get('application_deadline')
                    if deadline_str:
                        deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                        if datetime.utcnow() <= deadline <= cutoff:
                            days_until = (deadline - datetime.utcnow()).days
                            deadlines.append({
                                'type': 'opportunity',
                                'id': item['opportunity_id'],
                                'name': opp.get('name'),
                                'subtype': opp.get('type'),
                                'deadline': deadline_str,
                                'days_until': days_until,
                                'priority': self._get_priority(days_until),
                            })

            # Get awards
            award_result = self.db.table('student_awards').select(
                'award_id, awards(name, deadline, category)'
            ).eq('profile_id', profile_id).eq('status', 'tracking').execute()

            if award_result.data:
                for item in award_result.data:
                    award = item.get('awards', {})
                    deadline_str = award.get('deadline')
                    if deadline_str:
                        deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                        if datetime.utcnow() <= deadline <= cutoff:
                            days_until = (deadline - datetime.utcnow()).days
                            deadlines.append({
                                'type': 'award',
                                'id': item['award_id'],
                                'name': award.get('name'),
                                'subtype': award.get('category'),
                                'deadline': deadline_str,
                                'days_until': days_until,
                                'priority': self._get_priority(days_until),
                            })

            # Sort by deadline
            deadlines.sort(key=lambda x: x['days_until'])

        except Exception as e:
            self.logger.error(
                "get_upcoming_deadlines_error",
                profile_id=profile_id,
                error=str(e)
            )

        return deadlines

    def _get_priority(self, days_until: int) -> str:
        """Get priority level based on days until deadline."""
        if days_until <= 1:
            return 'urgent'
        elif days_until <= 3:
            return 'high'
        elif days_until <= 7:
            return 'medium'
        else:
            return 'low'
