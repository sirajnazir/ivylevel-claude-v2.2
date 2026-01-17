"""
Context Patterns - v5.4 True Autonomous Agents

Patterns implemented:
- C2: User Context (3P: Supabase + Custom Selection)
- C4: Task Context (3P: LangGraph StateGraph)
- C6: Temporal Context (3P: Supabase)
"""

from .types import (
    # User Context types
    StudentContext,
    ContextSelection,
    CommunicationStyle,
    MotivationType,
    # Temporal Context types
    TemporalContext,
    Deadline,
    DeadlinePriority,
    DeadlineStatus,
    DeadlineCategory,
    AdmissionsPhase,
    # Task Context types
    TaskContext,
    TaskStatus,
    TaskType,
    # Working Memory types
    WorkingMemory,
    ConversationTurn,
    ConversationRole,
    DetectedSignal,
)

from .user_context import (
    UserContextLoader,
    load_student_context,
)

from .temporal_context import (
    TemporalContextLoader,
    load_temporal_context,
    get_phase_recommendations,
    ADMISSIONS_CALENDAR,
)

from .task_context import (
    TaskContextManager,
    TaskContextBuilder,
    create_assessment_task,
    create_gameplan_task,
)

from .context_selector import (
    ContextSelector,
    ContextRelevance,
    CONTEXT_RELEVANCE_MATRIX,
    get_agent_context_needs,
)

__all__ = [
    # Types
    "StudentContext",
    "ContextSelection",
    "CommunicationStyle",
    "MotivationType",
    "TemporalContext",
    "Deadline",
    "DeadlinePriority",
    "DeadlineStatus",
    "DeadlineCategory",
    "AdmissionsPhase",
    "TaskContext",
    "TaskStatus",
    "TaskType",
    "WorkingMemory",
    "ConversationTurn",
    "ConversationRole",
    "DetectedSignal",
    # Loaders
    "UserContextLoader",
    "load_student_context",
    "TemporalContextLoader",
    "load_temporal_context",
    "get_phase_recommendations",
    "ADMISSIONS_CALENDAR",
    # Task management
    "TaskContextManager",
    "TaskContextBuilder",
    "create_assessment_task",
    "create_gameplan_task",
    # Context selection (USP)
    "ContextSelector",
    "ContextRelevance",
    "CONTEXT_RELEVANCE_MATRIX",
    "get_agent_context_needs",
]
