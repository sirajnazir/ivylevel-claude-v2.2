"""
IvyQuest v10.0 - Proactive Workflows
=====================================

Autonomous workflows that run on schedule to proactively engage students:

| Workflow         | Schedule       | Purpose                                    |
|------------------|----------------|--------------------------------------------|
| SilenceDetector  | Every 4 hours  | Detect 72h+ inactivity, send re-engagement |
| DeadlineAlerts   | Daily 9am      | Multi-tier deadline reminders (30/7/3/1d)  |
| WeeklyScout      | Monday 9am     | New opportunity/award recommendations      |
| DailyCheckin     | Daily (pref)   | Progress encouragement, EDS monitoring     |
"""

from .base import BaseWorkflow, WorkflowResult
from .runner import WorkflowRunner
from .silence_detector import SilenceDetectorWorkflow
from .deadline_alerts import DeadlineAlertWorkflow
from .weekly_scout import WeeklyScoutWorkflow
from .daily_checkin import DailyCheckinWorkflow

__all__ = [
    'BaseWorkflow',
    'WorkflowResult',
    'WorkflowRunner',
    'SilenceDetectorWorkflow',
    'DeadlineAlertWorkflow',
    'WeeklyScoutWorkflow',
    'DailyCheckinWorkflow',
]
