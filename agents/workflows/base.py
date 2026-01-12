"""
IvyQuest v10.0 - BaseWorkflow Abstract Class
=============================================

All proactive workflows inherit from this base class.
Provides common utilities for:
- Workflow state management
- Notification creation
- Notification preference checking
- Standardized execution pattern
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import structlog

logger = structlog.get_logger()


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""
    success: bool
    profiles_processed: int
    notifications_sent: int
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'profiles_processed': self.profiles_processed,
            'notifications_sent': self.notifications_sent,
            'errors': self.errors,
            'metadata': self.metadata,
        }


class BaseWorkflow(ABC):
    """
    Base class for all proactive workflows.

    Subclasses must implement:
    - name: Workflow identifier (e.g., "silence_detector")
    - schedule: Cron expression (e.g., "0 */4 * * *")
    - description: Human-readable description
    - get_eligible_profiles(): Returns profile IDs to process
    - process_profile(profile_id): Processes a single profile
    """

    # Subclasses must define these
    name: str
    schedule: str
    description: str

    def __init__(self, db_client):
        """
        Initialize workflow with database client.

        Args:
            db_client: Supabase client instance
        """
        self.db = db_client
        self.logger = logger.bind(workflow=self.name)

    async def get_workflow_state(self, profile_id: str) -> Optional[Dict]:
        """
        Get workflow state from workflow_state table.

        Args:
            profile_id: The profile UUID

        Returns:
            Workflow state dict or None if not found
        """
        try:
            result = self.db.table('workflow_state').select('*').eq(
                'profile_id', profile_id
            ).eq('workflow_name', self.name).maybe_single().execute()
            return result.data if result.data else None
        except Exception as e:
            self.logger.error("get_workflow_state_error",
                            profile_id=profile_id, error=str(e))
            return None

    async def update_workflow_state(
        self,
        profile_id: str,
        state: Dict[str, Any],
        run_count_increment: int = 1
    ) -> bool:
        """
        Upsert workflow state.

        Args:
            profile_id: The profile UUID
            state: Workflow-specific state to store
            run_count_increment: How much to increment run_count

        Returns:
            True if successful
        """
        try:
            # Get current state to increment run_count
            current = await self.get_workflow_state(profile_id)
            current_run_count = current.get('run_count', 0) if current else 0

            self.db.table('workflow_state').upsert({
                'profile_id': profile_id,
                'workflow_name': self.name,
                'last_run': datetime.utcnow().isoformat(),
                'run_count': current_run_count + run_count_increment,
                'state': state,
                'enabled': True,
                'updated_at': datetime.utcnow().isoformat(),
            }, on_conflict='profile_id,workflow_name').execute()
            return True
        except Exception as e:
            self.logger.error("update_workflow_state_error",
                            profile_id=profile_id, error=str(e))
            return False

    async def create_notification(
        self,
        profile_id: str,
        title: str,
        message: str,
        notification_type: str,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Create notification in database.

        Args:
            profile_id: Target profile UUID
            title: Notification title
            message: Notification message body
            notification_type: Type from allowed enum values
            action_url: Optional deep link URL
            action_label: Optional button label
            metadata: Optional additional data

        Returns:
            Notification ID if successful, None otherwise
        """
        try:
            result = self.db.table('notifications').insert({
                'profile_id': profile_id,
                'title': title,
                'message': message,
                'type': notification_type,
                'source': 'workflow',
                'source_workflow': self.name,
                'action_url': action_url,
                'action_label': action_label,
                'metadata': metadata or {},
                'read': False,
            }).execute()

            if result.data and len(result.data) > 0:
                return result.data[0].get('id')
            return None
        except Exception as e:
            self.logger.error("create_notification_error",
                            profile_id=profile_id, error=str(e))
            return None

    async def check_notification_preferences(
        self,
        profile_id: str,
        preference_key: str
    ) -> bool:
        """
        Check if user wants this type of notification.

        Args:
            profile_id: The profile UUID
            preference_key: Key in notification_preferences JSON
                           (e.g., 'silence_nudges', 'deadline_alerts')

        Returns:
            True if enabled (defaults to True if not set)
        """
        try:
            result = self.db.table('profiles').select(
                'notification_preferences'
            ).eq('id', profile_id).maybe_single().execute()

            if not result.data:
                return True  # Default to enabled

            prefs = result.data.get('notification_preferences', {})
            if isinstance(prefs, dict):
                return prefs.get(preference_key, True)
            return True
        except Exception as e:
            self.logger.error("check_preferences_error",
                            profile_id=profile_id, error=str(e))
            return True  # Default to enabled on error

    async def update_last_activity(self, profile_id: str) -> bool:
        """
        Update the last_activity_at timestamp for a profile.
        Called when user interacts with the system.

        Args:
            profile_id: The profile UUID

        Returns:
            True if successful
        """
        try:
            self.db.table('profiles').update({
                'last_activity_at': datetime.utcnow().isoformat()
            }).eq('id', profile_id).execute()
            return True
        except Exception as e:
            self.logger.error("update_last_activity_error",
                            profile_id=profile_id, error=str(e))
            return False

    @abstractmethod
    async def get_eligible_profiles(self) -> List[str]:
        """
        Return list of profile IDs eligible for this workflow run.

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    async def process_profile(self, profile_id: str) -> bool:
        """
        Process a single profile.

        Must be implemented by subclasses.

        Args:
            profile_id: The profile UUID to process

        Returns:
            True if notification was sent, False otherwise
        """
        pass

    async def run(self) -> WorkflowResult:
        """
        Execute workflow for all eligible profiles.

        This is the main entry point for workflow execution.
        """
        start_time = datetime.utcnow()
        self.logger.info("workflow_starting")

        errors: List[str] = []
        notifications_sent = 0
        profiles_processed = 0

        try:
            # Get eligible profiles
            profiles = await self.get_eligible_profiles()
            self.logger.info("eligible_profiles_found", count=len(profiles))

            # Process each profile
            for profile_id in profiles:
                profiles_processed += 1
                try:
                    if await self.process_profile(profile_id):
                        notifications_sent += 1
                        self.logger.debug("profile_processed",
                                        profile_id=profile_id,
                                        notification_sent=True)
                except Exception as e:
                    error_msg = f"{profile_id}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error("profile_processing_error",
                                    profile_id=profile_id,
                                    error=str(e))

            # Calculate duration
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            result = WorkflowResult(
                success=len(errors) == 0,
                profiles_processed=profiles_processed,
                notifications_sent=notifications_sent,
                errors=errors,
                metadata={
                    'run_at': start_time.isoformat(),
                    'duration_ms': duration_ms,
                    'workflow': self.name,
                }
            )

            self.logger.info("workflow_completed",
                           success=result.success,
                           profiles_processed=result.profiles_processed,
                           notifications_sent=result.notifications_sent,
                           errors_count=len(errors),
                           duration_ms=duration_ms)

            return result

        except Exception as e:
            self.logger.error("workflow_failed", error=str(e))
            return WorkflowResult(
                success=False,
                profiles_processed=profiles_processed,
                notifications_sent=notifications_sent,
                errors=[f"Workflow error: {str(e)}"],
                metadata={
                    'run_at': start_time.isoformat(),
                    'workflow': self.name,
                }
            )
