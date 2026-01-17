"""
A6: ReAct Loop Pattern - Implementation

Full THINK -> ACT -> OBSERVE cycle with tool use and loop control.
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class ReActPhase(str, Enum):
    """Current phase in ReAct cycle."""
    THINK = "think"
    ACT = "act"
    OBSERVE = "observe"
    COMPLETE = "complete"


class ReActStep(BaseModel):
    """A single step in the ReAct loop."""
    step_number: int
    phase: ReActPhase

    # THINK phase
    thought: Optional[str] = None
    reasoning: Optional[str] = None

    # ACT phase
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None

    # OBSERVE phase
    observation: Optional[str] = None
    observation_summary: Optional[str] = None

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: int = 0


class ReActResult(BaseModel):
    """Result of a ReAct loop execution."""
    success: bool
    final_answer: Optional[str] = None

    # Process
    steps: List[ReActStep] = Field(default_factory=list)
    total_iterations: int = 0

    # Termination
    termination_reason: str = ""  # "goal_achieved", "max_iterations", "error"

    # Metadata
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_duration_ms: int = 0


class ReActLoop:
    """
    ReAct (Reasoning + Acting) loop implementation.

    Pattern A6: ReAct Loop

    Cycle:
    1. THINK: Reason about current state and what to do
    2. ACT: Execute an action (tool call)
    3. OBSERVE: Process the result
    4. Loop until goal achieved or max iterations

    Integration with Critical 15:
    - Uses A4 Chain-of-Thought for THINK phase
    - Uses B1 Working Memory to track state
    - Uses Tool Framework for ACT phase
    - Feeds J2 Metrics with execution data
    """

    def __init__(
        self,
        llm_client=None,
        tools: Optional[Dict[str, Callable]] = None,
        max_iterations: int = 5,
    ):
        """
        Initialize ReAct loop.

        Args:
            llm_client: LLM for reasoning
            tools: Available tools {name: async_callable}
            max_iterations: Maximum loop iterations
        """
        self.llm = llm_client
        self.tools = tools or {}
        self.max_iterations = max_iterations

    async def run(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        initial_observations: Optional[List[str]] = None,
    ) -> ReActResult:
        """
        Execute ReAct loop.

        Args:
            task: The task to accomplish
            context: Additional context
            initial_observations: Starting observations

        Returns:
            ReActResult with final answer and trace
        """
        start_time = datetime.utcnow()
        context = context or {}
        observations = initial_observations or []
        steps = []

        for i in range(self.max_iterations):
            step_start = datetime.utcnow()

            # THINK: Reason about what to do
            thought, action, action_input, is_final = await self._think(
                task=task,
                context=context,
                observations=observations,
                step_number=i + 1,
            )

            step = ReActStep(
                step_number=i + 1,
                phase=ReActPhase.THINK,
                thought=thought,
            )

            # Check if task is complete
            if is_final:
                step.phase = ReActPhase.COMPLETE
                steps.append(step)

                return ReActResult(
                    success=True,
                    final_answer=thought,
                    steps=steps,
                    total_iterations=i + 1,
                    termination_reason="goal_achieved",
                    started_at=start_time,
                    completed_at=datetime.utcnow(),
                    total_duration_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                )

            # ACT: Execute the action
            step.phase = ReActPhase.ACT
            step.action = action
            step.action_input = action_input

            observation = await self._act(action, action_input)

            # OBSERVE: Process the result
            step.phase = ReActPhase.OBSERVE
            step.observation = observation
            step.observation_summary = self._summarize_observation(observation)

            observations.append(f"Action: {action}\nResult: {observation}")

            step.duration_ms = int((datetime.utcnow() - step_start).total_seconds() * 1000)
            steps.append(step)

        # Max iterations reached
        final_answer = await self._generate_final_answer(
            task, context, observations
        )

        return ReActResult(
            success=False,
            final_answer=final_answer,
            steps=steps,
            total_iterations=self.max_iterations,
            termination_reason="max_iterations",
            started_at=start_time,
            completed_at=datetime.utcnow(),
            total_duration_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
        )

    async def _think(
        self,
        task: str,
        context: Dict[str, Any],
        observations: List[str],
        step_number: int,
    ) -> tuple:
        """
        THINK phase: Reason about what to do next.

        Returns:
            (thought, action, action_input, is_final)
        """
        tools_desc = "\n".join([
            f"- {name}: {getattr(func, '__doc__', 'No description') or 'No description'}"
            for name, func in self.tools.items()
        ])

        observations_text = "\n---\n".join(observations[-5:]) if observations else "None yet"

        prompt = f"""
You are a college admissions coaching AI using the ReAct framework.

TASK: {task}

CONTEXT:
{json.dumps(context, indent=2, default=str)}

AVAILABLE TOOLS:
{tools_desc}

PREVIOUS OBSERVATIONS:
{observations_text}

STEP {step_number}:

Think step by step:
1. What have I learned from observations so far?
2. What do I still need to know or do?
3. Is the task complete? Can I provide a final answer?
4. If not complete, which tool should I use and why?

Respond in this JSON format:
{{
    "thought": "Your reasoning here",
    "is_final": true/false,
    "action": "tool_name or null if final",
    "action_input": {{}},
    "final_answer": "Your answer if is_final=true"
}}
"""

        if self.llm:
            try:
                response = await self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"},
                )

                result = json.loads(response.choices[0].message.content)

                if result.get("is_final"):
                    return (
                        result.get("final_answer", result.get("thought")),
                        None,
                        None,
                        True,
                    )

                return (
                    result.get("thought", ""),
                    result.get("action"),
                    result.get("action_input", {}),
                    False,
                )
            except Exception as e:
                logger.error(f"Think phase failed: {e}")

        # Fallback
        return ("Unable to reason about task", None, None, True)

    async def _act(
        self,
        action: str,
        action_input: Dict[str, Any],
    ) -> str:
        """
        ACT phase: Execute the chosen action.

        Args:
            action: Tool name
            action_input: Tool parameters

        Returns:
            Observation string
        """
        if not action:
            return "No action specified"

        tool = self.tools.get(action)
        if not tool:
            return f"Error: Unknown tool '{action}'"

        try:
            result = await tool(**action_input)
            return str(result)
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return f"Error executing {action}: {str(e)}"

    def _summarize_observation(self, observation: str) -> str:
        """Create a brief summary of the observation."""
        if len(observation) <= 200:
            return observation
        return observation[:200] + "..."

    async def _generate_final_answer(
        self,
        task: str,
        context: Dict[str, Any],
        observations: List[str],
    ) -> str:
        """Generate best possible answer from available information."""
        observations_text = "\n---\n".join(observations[-10:])

        prompt = f"""
Based on all observations, provide the best possible answer to this task.

TASK: {task}

OBSERVATIONS:
{observations_text}

Provide a concise, helpful answer based on what you learned:
"""

        if self.llm:
            try:
                response = await self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=500,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Final answer generation failed: {e}")

        return "I was unable to complete this task with the available information."

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: Optional[str] = None,
    ):
        """Register a tool for the ReAct loop."""
        if description:
            func.__doc__ = description
        self.tools[name] = func
