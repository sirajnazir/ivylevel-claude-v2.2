"""
A11: Planning Pattern - Implementation

Create and execute multi-step plans for complex tasks.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging
import json
import uuid

logger = logging.getLogger(__name__)


class PlanStepType(str, Enum):
    """Types of plan steps."""
    RESEARCH = "research"
    ANALYZE = "analyze"
    GENERATE = "generate"
    VALIDATE = "validate"
    TOOL_USE = "tool_use"
    DECISION = "decision"
    COMMUNICATE = "communicate"


class PlanStepStatus(str, Enum):
    """Status of a plan step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class PlanStep(BaseModel):
    """A step in the execution plan."""
    step_id: str
    step_type: PlanStepType
    description: str
    prerequisites: List[str] = Field(default_factory=list)
    tool_name: Optional[str] = None
    prompt: Optional[str] = None
    expected_output: Optional[str] = None
    status: PlanStepStatus = PlanStepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class Plan(BaseModel):
    """A complete execution plan."""
    plan_id: str
    goal: str
    context: Dict[str, Any] = Field(default_factory=dict)
    steps: List[PlanStep] = Field(default_factory=list)
    current_step: int = 0
    status: str = "created"  # created, executing, completed, failed
    success: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    total_duration_ms: int = 0


class PlanningEngine:
    """
    Creates and executes multi-step plans.

    Pattern A11: Planning

    GUARDRAILS:
    - NEW class - does not modify existing planning
    - Uses existing LLM and tools
    """

    def __init__(
        self,
        llm_client=None,
        tool_executor: Optional[Callable[[str, Dict], Awaitable[Any]]] = None,
        max_replans: int = 2,
    ):
        """
        Initialize planning engine.

        Args:
            llm_client: LLM client for planning
            tool_executor: Function to execute tools
            max_replans: Maximum replan attempts on failure
        """
        self.llm = llm_client
        self.tools = tool_executor
        self.max_replans = max_replans

    async def create_plan(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None,
    ) -> Plan:
        """
        Create an execution plan for a goal.

        Args:
            goal: The goal to achieve
            context: Context information
            available_tools: List of available tool names

        Returns:
            Plan with steps
        """
        plan_prompt = f"""Create a step-by-step plan to accomplish this goal.

GOAL: {goal}

{"CONTEXT: " + json.dumps(context) if context else ""}
{"AVAILABLE TOOLS: " + ", ".join(available_tools) if available_tools else ""}

Create 3-7 steps. For each step specify:
- step_id: Unique identifier (step_1, step_2, etc.)
- step_type: One of [research, analyze, generate, validate, tool_use, decision, communicate]
- description: What this step accomplishes
- prerequisites: List of step_ids that must complete first
- tool_name: If step_type is tool_use, which tool to use
- expected_output: What this step should produce

OUTPUT as JSON array of steps."""

        steps = []

        if self.llm:
            try:
                response = await self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a planning assistant."},
                        {"role": "user", "content": plan_prompt},
                    ],
                    temperature=0.5,
                )
                steps = self._parse_plan_steps(response.choices[0].message.content)
            except Exception as e:
                logger.error(f"Plan creation failed: {e}")

        # Fallback: create simple plan
        if not steps:
            steps = self._create_fallback_plan(goal)

        return Plan(
            plan_id=str(uuid.uuid4()),
            goal=goal,
            context=context or {},
            steps=steps,
        )

    def _parse_plan_steps(self, content: str) -> List[PlanStep]:
        """Parse LLM output into plan steps."""
        try:
            # Extract JSON from content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "[" in content:
                start = content.index("[")
                end = content.rindex("]") + 1
                json_str = content[start:end]
            else:
                json_str = content

            steps_data = json.loads(json_str)

            return [
                PlanStep(
                    step_id=s.get("step_id", f"step_{i}"),
                    step_type=PlanStepType(s.get("step_type", "analyze")),
                    description=s.get("description", ""),
                    prerequisites=s.get("prerequisites", []),
                    tool_name=s.get("tool_name"),
                    prompt=s.get("prompt"),
                    expected_output=s.get("expected_output"),
                )
                for i, s in enumerate(steps_data)
            ]
        except Exception as e:
            logger.error(f"Failed to parse plan: {e}")
            return []

    def _create_fallback_plan(self, goal: str) -> List[PlanStep]:
        """Create a simple fallback plan."""
        return [
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.ANALYZE,
                description=f"Analyze the goal: {goal}",
                expected_output="Understanding of what needs to be done",
            ),
            PlanStep(
                step_id="step_2",
                step_type=PlanStepType.GENERATE,
                description="Generate a response to achieve the goal",
                prerequisites=["step_1"],
                expected_output="Response or solution",
            ),
            PlanStep(
                step_id="step_3",
                step_type=PlanStepType.VALIDATE,
                description="Validate the generated response",
                prerequisites=["step_2"],
                expected_output="Validation result",
            ),
        ]

    async def execute_plan(self, plan: Plan) -> Plan:
        """
        Execute a plan step by step.

        Args:
            plan: Plan to execute

        Returns:
            Updated plan with results
        """
        start_time = datetime.now(timezone.utc)
        plan.status = "executing"
        replan_count = 0

        while plan.current_step < len(plan.steps):
            step = plan.steps[plan.current_step]

            # Check prerequisites
            prereqs_met = all(
                any(s.step_id == p and s.status == PlanStepStatus.COMPLETED
                    for s in plan.steps)
                for p in step.prerequisites
            )

            if not prereqs_met:
                step.status = PlanStepStatus.BLOCKED
                logger.error(f"Prerequisites not met for {step.step_id}")
                break

            try:
                step.status = PlanStepStatus.IN_PROGRESS
                step.started_at = datetime.now(timezone.utc)

                result = await self._execute_step(step, plan)

                step.status = PlanStepStatus.COMPLETED
                step.result = result
                step.completed_at = datetime.now(timezone.utc)

                # Update context with result
                if isinstance(result, dict):
                    plan.context.update(result)
                else:
                    plan.context[step.step_id] = result

                plan.current_step += 1

            except Exception as e:
                step.status = PlanStepStatus.FAILED
                step.error = str(e)
                step.completed_at = datetime.now(timezone.utc)
                logger.error(f"Step {step.step_id} failed: {e}")

                # Try replanning
                if replan_count < self.max_replans:
                    replan_count += 1
                    plan = await self._replan(plan, step, str(e))
                else:
                    plan.status = "failed"
                    break

        # Finalize plan
        if all(s.status == PlanStepStatus.COMPLETED for s in plan.steps):
            plan.status = "completed"
            plan.success = True
        elif plan.status != "failed":
            plan.status = "failed"

        plan.completed_at = datetime.now(timezone.utc)
        plan.total_duration_ms = int(
            (plan.completed_at - start_time).total_seconds() * 1000
        )

        return plan

    async def _execute_step(self, step: PlanStep, plan: Plan) -> Any:
        """Execute a single plan step."""
        # Tool use
        if step.step_type == PlanStepType.TOOL_USE:
            if not self.tools or not step.tool_name:
                raise ValueError(f"No tool available: {step.tool_name}")
            return await self.tools(step.tool_name, plan.context)

        # LLM-based steps
        if not self.llm:
            return {"status": "completed", "output": f"Mock: {step.description}"}

        prompt = f"""Execute this planning step.

STEP: {step.description}
EXPECTED OUTPUT: {step.expected_output}
CONTEXT: {json.dumps(plan.context)}

Previous step results:
{self._format_previous_results(plan)}

Provide the output for this step."""

        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        return {"output": response.choices[0].message.content}

    def _format_previous_results(self, plan: Plan) -> str:
        """Format completed step results for context."""
        results = []
        for step in plan.steps:
            if step.status == PlanStepStatus.COMPLETED and step.result:
                result_str = str(step.result)[:200]
                results.append(f"- {step.step_id}: {result_str}...")
        return "\n".join(results) if results else "None yet"

    async def _replan(
        self,
        plan: Plan,
        failed_step: PlanStep,
        error: str,
    ) -> Plan:
        """Create alternative plan after failure."""
        if not self.llm:
            return plan

        replan_prompt = f"""The current plan failed. Create an alternative approach.

ORIGINAL GOAL: {plan.goal}
FAILED STEP: {failed_step.description}
ERROR: {error}

What has been completed:
{self._format_previous_results(plan)}

Create alternative steps to complete the goal, working around the failure.
OUTPUT as JSON array of steps."""

        try:
            response = await self.llm.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": replan_prompt}],
                temperature=0.5,
            )

            new_steps = self._parse_plan_steps(response.choices[0].message.content)
            if new_steps:
                completed = [s for s in plan.steps if s.status == PlanStepStatus.COMPLETED]
                plan.steps = completed + new_steps
                plan.current_step = len(completed)
                logger.info(f"Replanned with {len(new_steps)} new steps")
        except Exception as e:
            logger.error(f"Replan failed: {e}")

        return plan

    def get_plan_summary(self, plan: Plan) -> Dict[str, Any]:
        """Get summary of plan execution."""
        return {
            "plan_id": plan.plan_id,
            "goal": plan.goal,
            "status": plan.status,
            "success": plan.success,
            "total_steps": len(plan.steps),
            "completed_steps": sum(
                1 for s in plan.steps if s.status == PlanStepStatus.COMPLETED
            ),
            "failed_steps": sum(
                1 for s in plan.steps if s.status == PlanStepStatus.FAILED
            ),
            "duration_ms": plan.total_duration_ms,
        }
