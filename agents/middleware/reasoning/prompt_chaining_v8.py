"""
A9: Prompt Chaining Pattern - Implementation

Break complex tasks into sequential LLM calls.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging
import json
import re

logger = logging.getLogger(__name__)


class ChainStepStatus(str, Enum):
    """Status of a chain step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ChainStep(BaseModel):
    """Definition of a step in a prompt chain."""
    name: str
    prompt_template: str
    depends_on: List[str] = Field(default_factory=list)
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2000
    required_output_keys: List[str] = Field(default_factory=list)
    status: ChainStepStatus = ChainStepStatus.PENDING
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0


class ChainResult(BaseModel):
    """Result of executing a prompt chain."""
    chain_name: str
    success: bool = False
    step_outputs: Dict[str, Any] = Field(default_factory=dict)
    final_output: Optional[Any] = None
    steps_completed: int = 0
    steps_failed: int = 0
    steps_skipped: int = 0
    total_duration_ms: int = 0
    error_message: Optional[str] = None


class PromptChainExecutor:
    """
    Executes prompt chains with dependency resolution.

    Pattern A9: Prompt Chaining

    GUARDRAILS:
    - NEW class - does not modify existing chains
    - Uses existing LLM interface
    """

    def __init__(
        self,
        llm_client=None,
        output_parser: Optional[Callable[[str, List[str]], Dict[str, Any]]] = None,
    ):
        """
        Initialize chain executor.

        Args:
            llm_client: LLM client for execution
            output_parser: Custom output parser function
        """
        self.llm = llm_client
        self.parser = output_parser or self._default_parser

    async def execute(
        self,
        chain_name: str,
        steps: List[ChainStep],
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> ChainResult:
        """
        Execute a prompt chain.

        Args:
            chain_name: Name of the chain
            steps: List of chain steps
            initial_context: Starting context

        Returns:
            ChainResult with outputs
        """
        start_time = datetime.now(timezone.utc)
        context = dict(initial_context or {})
        result = ChainResult(chain_name=chain_name)

        # Resolve execution order
        try:
            execution_order = self._resolve_dependencies(steps)
        except ValueError as e:
            result.error_message = str(e)
            return result

        for step_name in execution_order:
            step = next(s for s in steps if s.name == step_name)

            # Check dependencies met
            deps_met = all(
                dep in result.step_outputs
                for dep in step.depends_on
            )

            if not deps_met:
                step.status = ChainStepStatus.SKIPPED
                result.steps_skipped += 1
                logger.warning(f"Skipping step {step_name}: dependencies not met")
                continue

            try:
                step.status = ChainStepStatus.RUNNING
                step.started_at = datetime.now(timezone.utc)

                step_output = await self._execute_step(
                    step, context, result.step_outputs
                )

                step.status = ChainStepStatus.COMPLETED
                step.output = step_output
                step.completed_at = datetime.now(timezone.utc)
                step.duration_ms = int(
                    (step.completed_at - step.started_at).total_seconds() * 1000
                )

                result.step_outputs[step_name] = step_output
                result.steps_completed += 1

                # Update context with step output
                if isinstance(step_output, dict):
                    context.update(step_output)
                else:
                    context[step_name] = step_output

            except Exception as e:
                step.status = ChainStepStatus.FAILED
                step.error = str(e)
                step.completed_at = datetime.now(timezone.utc)
                result.steps_failed += 1
                logger.error(f"Step {step_name} failed: {e}")

                # Don't break for validation steps
                if step.name not in ["validate", "check", "verify"]:
                    result.error_message = f"Step {step_name} failed: {e}"
                    break

        # Determine success
        if result.steps_failed == 0 and result.steps_completed > 0:
            result.success = True
            if result.step_outputs:
                last_step = execution_order[-1]
                result.final_output = result.step_outputs.get(last_step)

        result.total_duration_ms = int(
            (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        )

        return result

    def _resolve_dependencies(self, steps: List[ChainStep]) -> List[str]:
        """
        Topological sort of steps by dependencies.

        Args:
            steps: List of chain steps

        Returns:
            Ordered list of step names

        Raises:
            ValueError: If circular dependency detected
        """
        graph = {s.name: set(s.depends_on) for s in steps}
        in_degree = {name: len(deps) for name, deps in graph.items()}
        queue = [name for name, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for name, deps in graph.items():
                if node in deps:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)

        if len(result) != len(steps):
            raise ValueError("Circular dependency detected in chain")

        return result

    async def _execute_step(
        self,
        step: ChainStep,
        context: Dict[str, Any],
        previous_outputs: Dict[str, Any],
    ) -> Any:
        """Execute a single chain step."""
        # Interpolate template with context
        prompt = step.prompt_template

        # Replace context variables
        for key, value in context.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        # Replace step output variables
        for step_name, output in previous_outputs.items():
            if isinstance(output, dict):
                for k, v in output.items():
                    prompt = prompt.replace(f"{{{step_name}.{k}}}", str(v))
            else:
                prompt = prompt.replace(f"{{{step_name}}}", str(output))

        if not self.llm:
            # Fallback without LLM
            return {"raw": f"Mock output for: {step.name}"}

        try:
            response = await self.llm.chat.completions.create(
                model=step.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=step.temperature,
                max_tokens=step.max_tokens,
            )

            content = response.choices[0].message.content
            return self.parser(content, step.required_output_keys)
        except Exception as e:
            logger.error(f"LLM call failed for step {step.name}: {e}")
            raise

    def _default_parser(
        self,
        content: str,
        required_keys: List[str],
    ) -> Dict[str, Any]:
        """
        Default output parser.

        Args:
            content: LLM output content
            required_keys: Keys to extract

        Returns:
            Parsed output dict
        """
        # Try JSON parsing
        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
                return json.loads(json_str)
            elif content.strip().startswith("{"):
                return json.loads(content)
        except (json.JSONDecodeError, IndexError):
            pass

        # Key-value extraction fallback
        result = {"raw": content}

        for key in required_keys:
            pattern = rf"{key}:\s*(.+?)(?=\n[A-Z_]+:|$)"
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                result[key] = match.group(1).strip()

        return result


# Predefined chain templates for IvyLevel
class IvyLevelChains:
    """Predefined prompt chains for IvyLevel coaching."""

    @staticmethod
    def essay_review_chain() -> List[ChainStep]:
        """Chain for comprehensive essay review."""
        return [
            ChainStep(
                name="analyze_prompt",
                prompt_template="""Analyze this college essay prompt:
{essay_prompt}

Identify:
- Key themes the prompt is asking about
- Expected tone and approach
- Common pitfalls to avoid

OUTPUT as JSON with keys: themes, expected_tone, pitfalls""",
                required_output_keys=["themes", "expected_tone", "pitfalls"],
            ),
            ChainStep(
                name="evaluate_content",
                prompt_template="""Given the essay prompt themes: {analyze_prompt.themes}

Evaluate this essay:
{essay_content}

Score (1-10) and comment on:
- Theme alignment
- Personal voice
- Specific details
- Structure and flow

OUTPUT as JSON with keys: scores, overall_score, comments""",
                depends_on=["analyze_prompt"],
                required_output_keys=["scores", "overall_score", "comments"],
            ),
            ChainStep(
                name="generate_feedback",
                prompt_template="""Based on the evaluation:
Scores: {evaluate_content.scores}
Comments: {evaluate_content.comments}

Generate actionable feedback for the student:
- 3 specific strengths to keep
- 3 specific areas to improve
- 1 example revision for the weakest section

OUTPUT as JSON with keys: strengths, improvements, example_revision""",
                depends_on=["evaluate_content"],
                required_output_keys=["strengths", "improvements", "example_revision"],
            ),
        ]

    @staticmethod
    def activity_planning_chain() -> List[ChainStep]:
        """Chain for activity planning."""
        return [
            ChainStep(
                name="assess_profile",
                prompt_template="""Assess this student profile for activity planning:
Spike: {spike}
Current Activities: {current_activities}
Grade: {grade}

Identify:
- Strength areas
- Gap areas
- Time availability estimate

OUTPUT as JSON with keys: strengths, gaps, time_estimate""",
                required_output_keys=["strengths", "gaps", "time_estimate"],
            ),
            ChainStep(
                name="generate_recommendations",
                prompt_template="""Based on profile assessment:
Strengths: {assess_profile.strengths}
Gaps: {assess_profile.gaps}
Available time: {assess_profile.time_estimate}

Generate 5 activity recommendations that:
- Build on strengths
- Address gaps
- Fit time constraints
- Support the spike: {spike}

OUTPUT as JSON array with keys per activity: name, type, commitment, impact_score""",
                depends_on=["assess_profile"],
                required_output_keys=["recommendations"],
            ),
        ]
