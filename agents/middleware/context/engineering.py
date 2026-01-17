"""
C5: Context Engineering - Implementation

Engineers rich context for agent interactions.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EngineeredContext(BaseModel):
    """
    The complete, engineered context for an agent interaction.

    This is what agents receive - carefully curated and prioritized.
    """
    # Core identity
    profile_id: str
    student_name: str = ""

    # Student context (filtered by relevance)
    student: Optional[Dict[str, Any]] = None

    # Temporal context (deadlines, phase)
    temporal: Optional[Dict[str, Any]] = None

    # Task context (if applicable)
    task: Optional[Dict[str, Any]] = None

    # Working memory (session state)
    working_memory: Optional[Dict[str, Any]] = None

    # Retrieved context (from memory/knowledge)
    retrieved_episodes: List[Dict[str, Any]] = Field(default_factory=list)
    retrieved_knowledge: List[Dict[str, Any]] = Field(default_factory=list)

    # Engineering metadata
    context_token_estimate: int = 0
    context_quality_score: float = 0.0
    engineering_notes: List[str] = Field(default_factory=list)

    def to_prompt_context(self, max_tokens: int = 4000) -> str:
        """
        Convert to string for LLM prompt inclusion.

        Prioritizes information based on token budget.
        """
        sections = []
        token_count = 0

        # Priority 1: Core student identity (always include)
        identity_section = self._format_identity()
        sections.append(identity_section)
        token_count += self._estimate_tokens(identity_section)

        # Priority 2: Current task (if exists)
        if self.task and self.task.get("objective"):
            task_section = self._format_task()
            if token_count + self._estimate_tokens(task_section) < max_tokens:
                sections.append(task_section)
                token_count += self._estimate_tokens(task_section)

        # Priority 3: Urgent deadlines
        if self.temporal and self.temporal.get("has_urgent_items"):
            deadline_section = self._format_urgent_deadlines()
            if token_count + self._estimate_tokens(deadline_section) < max_tokens:
                sections.append(deadline_section)
                token_count += self._estimate_tokens(deadline_section)

        # Priority 4: Working memory (recent conversation)
        if self.working_memory:
            wm_section = self._format_working_memory()
            if token_count + self._estimate_tokens(wm_section) < max_tokens:
                sections.append(wm_section)
                token_count += self._estimate_tokens(wm_section)

        # Priority 5: Retrieved episodes (if space)
        if self.retrieved_episodes and token_count < max_tokens - 500:
            episode_section = self._format_episodes(max_tokens - token_count - 100)
            sections.append(episode_section)

        return "\n\n".join(sections)

    def _format_identity(self) -> str:
        """Format core student identity."""
        lines = [
            "## Student Context",
            f"Name: {self.student_name}",
        ]

        if self.student:
            if self.student.get("grade"):
                lines.append(f"Grade: {self.student.get('grade')}")
            if self.student.get("archetype"):
                lines.append(f"Archetype: {self.student.get('archetype')}")
            if self.student.get("spike"):
                lines.append(f"Spike: {self.student.get('spike')}")
            if self.student.get("pillars"):
                lines.append(f"Pillars: {', '.join(self.student.get('pillars', []))}")
            if self.student.get("communication_style"):
                lines.append(f"Communication Style: {self.student.get('communication_style')}")

        return "\n".join(lines)

    def _format_task(self) -> str:
        """Format current task context."""
        lines = [
            "## Current Task",
            f"Objective: {self.task.get('objective', 'Unknown')}",
            f"Type: {self.task.get('task_type', 'general')}",
        ]
        if self.task.get("steps_total"):
            lines.append(f"Progress: {self.task.get('steps_completed', 0)}/{self.task.get('steps_total')}")
        if self.task.get("blocker"):
            lines.append(f"Blocker: {self.task.get('blocker')}")
        return "\n".join(lines)

    def _format_urgent_deadlines(self) -> str:
        """Format urgent deadlines."""
        lines = ["## Urgent Deadlines"]
        deadlines = self.temporal.get("imminent_deadlines", [])
        for deadline in deadlines[:5]:
            if isinstance(deadline, dict):
                lines.append(
                    f"- {deadline.get('name', 'Unknown')}: {deadline.get('days_until', '?')} days "
                    f"({deadline.get('priority', 'normal')})"
                )
        return "\n".join(lines)

    def _format_working_memory(self) -> str:
        """Format working memory state."""
        lines = ["## Session State"]

        sentiment = self.working_memory.get("detected_sentiment", "neutral")
        if sentiment != "neutral":
            lines.append(f"Student sentiment: {sentiment}")

        signals = self.working_memory.get("recent_signals", [])
        if signals:
            signal_types = [s.get("signal_type", "unknown") if isinstance(s, dict) else str(s) for s in signals[-3:]]
            lines.append(f"Recent signals: {', '.join(signal_types)}")

        facts = self.working_memory.get("session_facts", [])
        if facts:
            lines.append("Recent facts learned:")
            for fact in facts[-5:]:
                lines.append(f"  - {fact}")

        return "\n".join(lines)

    def _format_episodes(self, max_tokens: int) -> str:
        """Format retrieved episodes within token budget."""
        lines = ["## Relevant Past Experiences"]
        token_count = self._estimate_tokens(lines[0])

        for episode in self.retrieved_episodes:
            episode_line = (
                f"- {episode.get('situation', 'Unknown')}: "
                f"{episode.get('outcome', 'Unknown outcome')}"
            )
            line_tokens = self._estimate_tokens(episode_line)

            if token_count + line_tokens < max_tokens:
                lines.append(episode_line)
                token_count += line_tokens
            else:
                break

        return "\n".join(lines)

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token)."""
        return len(text) // 4


class ContextEngineer:
    """
    Engineers rich context for agent interactions.

    Pattern C5: Context Engineering (USP)

    This is critical because:
    - Quality of output directly depends on quality of context
    - Too much context = slow, expensive, unfocused
    - Too little context = generic, unhelpful advice
    - Smart selection = personalized AND efficient
    """

    def __init__(
        self,
        supabase_client=None,
        redis_client=None,
        max_context_tokens: int = 4000,
    ):
        """
        Initialize context engineer.

        Args:
            supabase_client: For loading persistent context
            redis_client: For working memory
            max_context_tokens: Token budget for context
        """
        self.supabase = supabase_client
        self.redis = redis_client
        self.max_tokens = max_context_tokens

    async def engineer_context(
        self,
        profile_id: str,
        session_id: str,
        task_type: str = "general",
        current_message: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> EngineeredContext:
        """
        Build complete engineered context.

        Args:
            profile_id: Student profile
            session_id: Current session
            task_type: Type of task for context selection
            current_message: Student's current message
            agent_name: Which agent needs context

        Returns:
            EngineeredContext ready for agent use
        """
        import asyncio

        engineering_notes = []

        # Parallel fetch all context components
        student_task = self._load_student_context(profile_id)
        temporal_task = self._load_temporal_context(profile_id)
        working_memory_task = self._load_working_memory(session_id)

        student, temporal, working_memory = await asyncio.gather(
            student_task,
            temporal_task,
            working_memory_task,
        )

        # Get task context if in task
        task = None
        if working_memory and isinstance(working_memory, dict):
            scratchpad = working_memory.get("scratchpad", {})
            task = scratchpad.get("current_task_context")

        # Retrieve relevant episodes if we have a message
        retrieved_episodes = []
        if current_message:
            retrieved_episodes = await self._retrieve_relevant_episodes(
                profile_id,
                current_message,
            )
            if retrieved_episodes:
                engineering_notes.append(
                    f"Retrieved {len(retrieved_episodes)} relevant past episodes"
                )

        # Apply context selection based on task type
        selection = self._get_selection_for_task(task_type)

        # Apply selection to student context
        filtered_student = self._apply_selection(student, selection) if student else None
        engineering_notes.append(
            f"Context selection for {task_type}: "
            f"activities={selection.get('include_activities', True)}, "
            f"academics={selection.get('include_academics', True)}"
        )

        # Get student name
        student_name = ""
        if filtered_student and isinstance(filtered_student, dict):
            student_name = filtered_student.get("name", "")

        # Calculate context quality
        quality_score = self._calculate_quality_score(
            filtered_student,
            temporal,
            working_memory,
            retrieved_episodes,
        )

        # Estimate tokens
        token_estimate = self._estimate_total_tokens(
            filtered_student,
            temporal,
            task,
            working_memory,
            retrieved_episodes,
        )
        engineering_notes.append(f"Estimated context tokens: {token_estimate}")

        return EngineeredContext(
            profile_id=profile_id,
            student_name=student_name,
            student=filtered_student,
            temporal=temporal,
            task=task,
            working_memory=working_memory,
            retrieved_episodes=retrieved_episodes,
            context_token_estimate=token_estimate,
            context_quality_score=quality_score,
            engineering_notes=engineering_notes,
        )

    async def _load_student_context(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Load student context from database."""
        if not self.supabase:
            return None
        try:
            # Use existing UserContextLoader if available
            from context import UserContextLoader
            loader = UserContextLoader(self.supabase)
            ctx = await loader.load_context(profile_id)
            return ctx.model_dump() if ctx else None
        except Exception as e:
            logger.warning(f"Failed to load student context: {e}")
            return None

    async def _load_temporal_context(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Load temporal context from database."""
        if not self.supabase:
            return None
        try:
            # Use existing TemporalContextLoader if available
            from context import TemporalContextLoader
            loader = TemporalContextLoader(self.supabase)
            ctx = await loader.load_context(profile_id)
            return ctx.model_dump() if ctx else None
        except Exception as e:
            logger.warning(f"Failed to load temporal context: {e}")
            return None

    async def _load_working_memory(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load working memory from Redis."""
        if not self.redis:
            return None
        try:
            # Use existing WorkingMemoryManager if available
            from memory import WorkingMemoryManager
            manager = WorkingMemoryManager(self.redis)
            wm = await manager.get_or_create(session_id, "")
            return wm.model_dump() if wm else None
        except Exception as e:
            logger.warning(f"Failed to load working memory: {e}")
            return None

    async def _retrieve_relevant_episodes(
        self,
        profile_id: str,
        query: str,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant past episodes using B7 Memory Retrieval."""
        try:
            from memory import MemoryRetriever
            retriever = MemoryRetriever(self.supabase)
            result = await retriever.retrieve(
                profile_id=profile_id,
                query=query,
                memory_types=["episodic"],
                k=k,
            )
            return [item.content for item in result.items] if result and result.items else []
        except Exception as e:
            logger.warning(f"Episode retrieval failed: {e}")
            return []

    def _get_selection_for_task(self, task_type: str) -> Dict[str, bool]:
        """Get context selection based on task type."""
        # Task-specific context selection
        selections = {
            "ec_assessment": {
                "include_activities": True,
                "include_academics": False,
                "include_goals": True,
                "include_constraints": True,
            },
            "gameplan": {
                "include_activities": True,
                "include_academics": True,
                "include_goals": True,
                "include_constraints": True,
            },
            "essay_help": {
                "include_activities": True,
                "include_academics": False,
                "include_goals": True,
                "include_constraints": False,
            },
            "general": {
                "include_activities": True,
                "include_academics": True,
                "include_goals": True,
                "include_constraints": True,
            },
        }
        return selections.get(task_type, selections["general"])

    def _apply_selection(
        self,
        student: Optional[Dict[str, Any]],
        selection: Dict[str, bool],
    ) -> Optional[Dict[str, Any]]:
        """Apply context selection to filter student context."""
        if not student:
            return None

        filtered = student.copy()

        if not selection.get("include_activities", True):
            filtered["activities"] = []
            filtered["activity_count"] = 0

        if not selection.get("include_academics", True):
            filtered["gpa"] = None
            filtered["target_schools"] = []
            filtered["intended_major"] = None

        if not selection.get("include_constraints", True):
            filtered["constraints"] = {}

        return filtered

    def _calculate_quality_score(
        self,
        student: Optional[Dict[str, Any]],
        temporal: Optional[Dict[str, Any]],
        working_memory: Optional[Dict[str, Any]],
        episodes: List[Dict],
    ) -> float:
        """
        Calculate context quality score (0-1).

        Higher score = more complete, relevant context.
        """
        score = 0.0

        # Student identity completeness (0.3)
        if student:
            identity_score = 0.0
            if student.get("name"):
                identity_score += 0.05
            if student.get("archetype"):
                identity_score += 0.1
            if student.get("spike"):
                identity_score += 0.1
            if student.get("pillars"):
                identity_score += 0.05
            score += min(identity_score, 0.3)

        # Temporal awareness (0.2)
        if temporal:
            temporal_score = 0.1  # Base score
            if temporal.get("deadlines"):
                temporal_score += 0.05
            if temporal.get("has_urgent_items"):
                temporal_score += 0.05  # More valuable if urgent
            score += min(temporal_score, 0.2)

        # Session context (0.2)
        if working_memory:
            session_score = 0.1  # Base score
            if working_memory.get("conversation_buffer"):
                session_score += 0.05
            if working_memory.get("session_facts"):
                session_score += 0.05
            score += min(session_score, 0.2)

        # Retrieved context (0.3)
        if episodes:
            score += min(len(episodes) * 0.06, 0.3)

        return min(score, 1.0)

    def _estimate_total_tokens(
        self,
        student: Optional[Dict[str, Any]],
        temporal: Optional[Dict[str, Any]],
        task: Optional[Dict[str, Any]],
        working_memory: Optional[Dict[str, Any]],
        episodes: List[Dict],
    ) -> int:
        """Estimate total tokens for context."""
        # Rough estimates
        tokens = 200  # Base overhead

        if student:
            tokens += 100  # Student identity
            tokens += len(student.get("activities", [])) * 50

        if temporal:
            tokens += len(temporal.get("deadlines", [])) * 30

        if task:
            tokens += 100

        if working_memory:
            tokens += len(working_memory.get("conversation_buffer", [])) * 50

        tokens += len(episodes) * 100

        return tokens
