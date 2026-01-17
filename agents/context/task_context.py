"""
Pattern C4: Task Context Manager
v5.4 True Autonomous Agents

3P: LangGraph StateGraph for state management
USP: Multi-agent task coordination
"""

from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import logging
import uuid

from .types import (
    TaskContext,
    TaskStatus,
    TaskType,
)

logger = logging.getLogger(__name__)


class TaskContextManager:
    """
    Manages task context for multi-agent coordination.

    Pattern C4: Task Context (3P: LangGraph StateGraph)

    This is critical because:
    - Agents need to know what task they're working on
    - Progress needs to be tracked across agent handoffs
    - Blockers need to be detected and handled
    """

    def __init__(self, supabase_client=None):
        """
        Initialize task context manager.

        Args:
            supabase_client: Optional Supabase client for persistence
        """
        self.supabase = supabase_client
        self._active_tasks: Dict[str, TaskContext] = {}
        self._task_listeners: List[Callable[[TaskContext], None]] = []

    def create_task(
        self,
        task_type: TaskType,
        objective: str,
        profile_id: Optional[str] = None,
        steps_total: int = 0,
        sub_tasks: Optional[List[Dict[str, Any]]] = None,
    ) -> TaskContext:
        """
        Create a new task context.

        Args:
            task_type: Type of task (assessment, gameplan, etc.)
            objective: What this task aims to accomplish
            profile_id: Student profile this task is for
            steps_total: Expected number of steps
            sub_tasks: Optional list of sub-task definitions

        Returns:
            New TaskContext instance
        """
        task_id = str(uuid.uuid4())

        task = TaskContext(
            task_id=task_id,
            task_type=task_type,
            objective=objective,
            status=TaskStatus.PENDING,
            started_at=None,
            steps_total=steps_total,
            sub_tasks=sub_tasks or [],
        )

        self._active_tasks[task_id] = task
        logger.info(f"Created task {task_id}: {task_type.value} - {objective}")

        return task

    def start_task(self, task_id: str, agent_name: Optional[str] = None) -> TaskContext:
        """
        Mark task as started.

        Args:
            task_id: Task to start
            agent_name: Agent starting the task

        Returns:
            Updated TaskContext
        """
        task = self._active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        task.current_agent = agent_name

        self._notify_listeners(task)
        logger.info(f"Started task {task_id} with agent {agent_name}")

        return task

    def update_progress(
        self,
        task_id: str,
        steps_completed: int,
        current_agent: Optional[str] = None,
    ) -> TaskContext:
        """
        Update task progress.

        Args:
            task_id: Task to update
            steps_completed: Number of steps completed
            current_agent: Agent currently working

        Returns:
            Updated TaskContext
        """
        task = self._active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.steps_completed = steps_completed
        if task.steps_total > 0:
            task.progress_percentage = (steps_completed / task.steps_total) * 100

        if current_agent:
            # Track agent transitions
            if task.current_agent and task.current_agent != current_agent:
                task.agents_completed.append(task.current_agent)
            task.current_agent = current_agent

        self._notify_listeners(task)
        logger.debug(f"Task {task_id} progress: {steps_completed}/{task.steps_total}")

        return task

    def set_blocker(
        self,
        task_id: str,
        blocker: str,
    ) -> TaskContext:
        """
        Mark task as blocked.

        Args:
            task_id: Task that is blocked
            blocker: Description of what's blocking

        Returns:
            Updated TaskContext
        """
        task = self._active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.BLOCKED
        task.blocker = blocker
        task.blocker_since = datetime.utcnow()

        self._notify_listeners(task)
        logger.warning(f"Task {task_id} blocked: {blocker}")

        return task

    def clear_blocker(self, task_id: str) -> TaskContext:
        """Clear blocker and resume task."""
        task = self._active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.IN_PROGRESS
        task.blocker = None
        task.blocker_since = None

        self._notify_listeners(task)
        logger.info(f"Task {task_id} unblocked")

        return task

    def complete_task(
        self,
        task_id: str,
        success: bool = True,
    ) -> TaskContext:
        """
        Mark task as completed or failed.

        Args:
            task_id: Task to complete
            success: Whether task succeeded

        Returns:
            Updated TaskContext
        """
        task = self._active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        task.progress_percentage = 100.0 if success else task.progress_percentage

        # Track final agent
        if task.current_agent:
            task.agents_completed.append(task.current_agent)
            task.current_agent = None

        self._notify_listeners(task)
        logger.info(f"Task {task_id} {'completed' if success else 'failed'}")

        return task

    def get_task(self, task_id: str) -> Optional[TaskContext]:
        """Get task by ID."""
        return self._active_tasks.get(task_id)

    def get_active_tasks(self) -> List[TaskContext]:
        """Get all active (in-progress) tasks."""
        return [
            task for task in self._active_tasks.values()
            if task.status == TaskStatus.IN_PROGRESS
        ]

    def get_blocked_tasks(self) -> List[TaskContext]:
        """Get all blocked tasks."""
        return [
            task for task in self._active_tasks.values()
            if task.status == TaskStatus.BLOCKED
        ]

    def add_listener(self, callback: Callable[[TaskContext], None]) -> None:
        """Add a task status listener."""
        self._task_listeners.append(callback)

    def remove_listener(self, callback: Callable[[TaskContext], None]) -> None:
        """Remove a task status listener."""
        self._task_listeners.remove(callback)

    def _notify_listeners(self, task: TaskContext) -> None:
        """Notify all listeners of task update."""
        for listener in self._task_listeners:
            try:
                listener(task)
            except Exception as e:
                logger.error(f"Error in task listener: {e}")

    async def persist_task(self, task: TaskContext) -> None:
        """
        Persist task to database.

        Args:
            task: Task to persist
        """
        if not self.supabase:
            return

        try:
            await self.supabase.table("task_contexts").upsert({
                "id": task.task_id,
                "task_type": task.task_type.value,
                "objective": task.objective,
                "status": task.status.value,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "steps_completed": task.steps_completed,
                "steps_total": task.steps_total,
                "progress_percentage": task.progress_percentage,
                "current_agent": task.current_agent,
                "agents_completed": task.agents_completed,
                "blocker": task.blocker,
                "updated_at": datetime.utcnow().isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Error persisting task {task.task_id}: {e}")


class TaskContextBuilder:
    """
    Builder pattern for creating task contexts.

    USP: Fluent API for task definition.
    """

    def __init__(self, manager: TaskContextManager):
        self.manager = manager
        self._type: TaskType = TaskType.GENERAL
        self._objective: str = ""
        self._profile_id: Optional[str] = None
        self._steps: int = 0
        self._sub_tasks: List[Dict[str, Any]] = []

    def for_assessment(self) -> "TaskContextBuilder":
        """Task is an assessment."""
        self._type = TaskType.ASSESSMENT
        return self

    def for_gameplan(self) -> "TaskContextBuilder":
        """Task is a gameplan generation."""
        self._type = TaskType.GAMEPLAN
        return self

    def for_execution(self) -> "TaskContextBuilder":
        """Task is an execution workflow."""
        self._type = TaskType.EXECUTION
        return self

    def for_crisis(self) -> "TaskContextBuilder":
        """Task is crisis intervention."""
        self._type = TaskType.CRISIS
        return self

    def with_objective(self, objective: str) -> "TaskContextBuilder":
        """Set task objective."""
        self._objective = objective
        return self

    def for_profile(self, profile_id: str) -> "TaskContextBuilder":
        """Set profile this task is for."""
        self._profile_id = profile_id
        return self

    def with_steps(self, count: int) -> "TaskContextBuilder":
        """Set expected step count."""
        self._steps = count
        return self

    def with_sub_task(
        self,
        name: str,
        agent: str,
        order: int = 0,
    ) -> "TaskContextBuilder":
        """Add a sub-task."""
        self._sub_tasks.append({
            "name": name,
            "agent": agent,
            "order": order,
            "status": "pending",
        })
        return self

    def build(self) -> TaskContext:
        """Create the task context."""
        return self.manager.create_task(
            task_type=self._type,
            objective=self._objective,
            profile_id=self._profile_id,
            steps_total=self._steps,
            sub_tasks=sorted(self._sub_tasks, key=lambda x: x.get("order", 0)),
        )


# Convenience functions
def create_assessment_task(
    manager: TaskContextManager,
    profile_id: str,
) -> TaskContext:
    """Create a standard assessment task."""
    return (
        TaskContextBuilder(manager)
        .for_assessment()
        .with_objective("Analyze student profile and generate identity synthesis")
        .for_profile(profile_id)
        .with_steps(4)
        .with_sub_task("Load Profile", "context_loader", 1)
        .with_sub_task("Analyze Activities", "ec_agent", 2)
        .with_sub_task("Generate Identity", "ec_agent", 3)
        .with_sub_task("Quality Check", "validator", 4)
        .build()
    )


def create_gameplan_task(
    manager: TaskContextManager,
    profile_id: str,
) -> TaskContext:
    """Create a standard gameplan task."""
    return (
        TaskContextBuilder(manager)
        .for_gameplan()
        .with_objective("Generate personalized college prep gameplan")
        .for_profile(profile_id)
        .with_steps(6)
        .with_sub_task("Load Context", "context_loader", 1)
        .with_sub_task("Assess Identity", "ec_agent", 2)
        .with_sub_task("Find Awards", "awards_agent", 3)
        .with_sub_task("Find Programs", "programs_agent", 4)
        .with_sub_task("Prioritize", "prioritizer", 5)
        .with_sub_task("Build Gameplan", "gameplan_agent", 6)
        .build()
    )
