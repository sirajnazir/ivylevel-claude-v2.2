"""
IvyQuest v10.0 - Workflow Runner with APScheduler
=================================================

Manages scheduled execution of all proactive workflows.

Usage:
    from workflows import WorkflowRunner

    runner = WorkflowRunner(db_client)
    runner.start()  # Starts scheduler
    runner.stop()   # Stops scheduler
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Type
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, JobExecutionEvent
import structlog

from .base import BaseWorkflow, WorkflowResult

logger = structlog.get_logger()


class WorkflowRunner:
    """
    Manages scheduled execution of proactive workflows.

    Uses APScheduler for cron-based scheduling.
    """

    # Workflow schedules (cron expressions)
    WORKFLOW_SCHEDULES = {
        'silence_detector': '0 */4 * * *',      # Every 4 hours
        'deadline_alerts': '0 9 * * *',          # Daily at 9 AM
        'weekly_scout': '0 9 * * 1',             # Monday at 9 AM
        'daily_checkin': '0 15 * * *',           # Daily at 3 PM (adjustable per user)
    }

    def __init__(self, db_client, timezone: str = 'America/New_York'):
        """
        Initialize the workflow runner.

        Args:
            db_client: Supabase client instance
            timezone: Timezone for schedule execution
        """
        self.db = db_client
        self.timezone = timezone
        self.scheduler = AsyncIOScheduler(timezone=timezone)
        self.workflows: Dict[str, BaseWorkflow] = {}
        self.logger = logger.bind(component='workflow_runner')

        # Register event listeners
        self.scheduler.add_listener(
            self._on_job_executed,
            EVENT_JOB_EXECUTED
        )
        self.scheduler.add_listener(
            self._on_job_error,
            EVENT_JOB_ERROR
        )

    def register_workflow(self, workflow_class: Type[BaseWorkflow]) -> None:
        """
        Register a workflow for scheduled execution.

        Args:
            workflow_class: The workflow class to register
        """
        workflow = workflow_class(self.db)
        self.workflows[workflow.name] = workflow

        # Get schedule from workflow or use default
        schedule = getattr(workflow, 'schedule', None)
        if not schedule:
            schedule = self.WORKFLOW_SCHEDULES.get(workflow.name)

        if schedule:
            trigger = CronTrigger.from_crontab(schedule, timezone=self.timezone)
            self.scheduler.add_job(
                self._run_workflow,
                trigger=trigger,
                id=workflow.name,
                args=[workflow.name],
                replace_existing=True,
                name=f"workflow_{workflow.name}"
            )
            self.logger.info(
                "workflow_registered",
                workflow=workflow.name,
                schedule=schedule
            )
        else:
            self.logger.warning(
                "workflow_no_schedule",
                workflow=workflow.name
            )

    def register_all_workflows(self) -> None:
        """Register all standard workflows."""
        # Import here to avoid circular imports
        from .silence_detector import SilenceDetectorWorkflow
        from .deadline_alerts import DeadlineAlertWorkflow
        from .weekly_scout import WeeklyScoutWorkflow
        from .daily_checkin import DailyCheckinWorkflow

        self.register_workflow(SilenceDetectorWorkflow)
        self.register_workflow(DeadlineAlertWorkflow)
        self.register_workflow(WeeklyScoutWorkflow)
        self.register_workflow(DailyCheckinWorkflow)

    async def _run_workflow(self, workflow_name: str) -> Optional[WorkflowResult]:
        """
        Execute a workflow by name.

        Args:
            workflow_name: Name of the workflow to run

        Returns:
            WorkflowResult or None if workflow not found
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            self.logger.error("workflow_not_found", workflow=workflow_name)
            return None

        self.logger.info("workflow_executing", workflow=workflow_name)

        try:
            result = await workflow.run()

            # Log result to database
            await self._log_workflow_run(workflow_name, result)

            return result

        except Exception as e:
            self.logger.error(
                "workflow_execution_error",
                workflow=workflow_name,
                error=str(e)
            )
            # Create error result
            error_result = WorkflowResult(
                success=False,
                profiles_processed=0,
                notifications_sent=0,
                errors=[f"Execution error: {str(e)}"],
                metadata={'workflow': workflow_name, 'run_at': datetime.utcnow().isoformat()}
            )
            await self._log_workflow_run(workflow_name, error_result)
            return error_result

    async def _log_workflow_run(
        self,
        workflow_name: str,
        result: WorkflowResult
    ) -> None:
        """
        Log workflow run to database.

        Args:
            workflow_name: Name of the workflow
            result: The execution result
        """
        try:
            self.db.table('workflow_runs').insert({
                'workflow_name': workflow_name,
                'success': result.success,
                'profiles_processed': result.profiles_processed,
                'notifications_sent': result.notifications_sent,
                'errors': result.errors,
                'duration_ms': result.metadata.get('duration_ms'),
                'run_at': result.metadata.get('run_at', datetime.utcnow().isoformat()),
            }).execute()
        except Exception as e:
            self.logger.error(
                "log_workflow_run_error",
                workflow=workflow_name,
                error=str(e)
            )

    def _on_job_executed(self, event: JobExecutionEvent) -> None:
        """Handle successful job execution."""
        self.logger.debug(
            "job_executed",
            job_id=event.job_id,
            scheduled_run_time=str(event.scheduled_run_time)
        )

    def _on_job_error(self, event: JobExecutionEvent) -> None:
        """Handle job execution error."""
        self.logger.error(
            "job_error",
            job_id=event.job_id,
            exception=str(event.exception),
            traceback=str(event.traceback)
        )

    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("scheduler_started")

    def stop(self, wait: bool = True) -> None:
        """
        Stop the scheduler.

        Args:
            wait: Whether to wait for running jobs to complete
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            self.logger.info("scheduler_stopped")

    async def run_now(self, workflow_name: str) -> Optional[WorkflowResult]:
        """
        Run a workflow immediately (bypass schedule).

        Args:
            workflow_name: Name of the workflow to run

        Returns:
            WorkflowResult or None if workflow not found
        """
        return await self._run_workflow(workflow_name)

    async def run_all_now(self) -> Dict[str, WorkflowResult]:
        """
        Run all workflows immediately.

        Returns:
            Dict of workflow names to results
        """
        results = {}
        for name in self.workflows:
            result = await self._run_workflow(name)
            if result:
                results[name] = result
        return results

    def get_status(self) -> Dict[str, Any]:
        """
        Get scheduler and workflow status.

        Returns:
            Status dictionary with scheduler state and job info
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': str(job.next_run_time) if job.next_run_time else None,
                'trigger': str(job.trigger),
            })

        return {
            'running': self.scheduler.running,
            'timezone': str(self.timezone),
            'workflows_registered': list(self.workflows.keys()),
            'jobs': jobs,
        }

    def pause_workflow(self, workflow_name: str) -> bool:
        """
        Pause a workflow's scheduled execution.

        Args:
            workflow_name: Name of the workflow to pause

        Returns:
            True if successfully paused
        """
        try:
            self.scheduler.pause_job(workflow_name)
            self.logger.info("workflow_paused", workflow=workflow_name)
            return True
        except Exception as e:
            self.logger.error(
                "pause_workflow_error",
                workflow=workflow_name,
                error=str(e)
            )
            return False

    def resume_workflow(self, workflow_name: str) -> bool:
        """
        Resume a paused workflow.

        Args:
            workflow_name: Name of the workflow to resume

        Returns:
            True if successfully resumed
        """
        try:
            self.scheduler.resume_job(workflow_name)
            self.logger.info("workflow_resumed", workflow=workflow_name)
            return True
        except Exception as e:
            self.logger.error(
                "resume_workflow_error",
                workflow=workflow_name,
                error=str(e)
            )
            return False
