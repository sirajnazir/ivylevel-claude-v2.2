"""
Pattern A4: Chain-of-Thought Reasoning
v5.4 True Autonomous Agents

3P: OpenAI/Anthropic LLM APIs
USP: Structured reasoning for college admissions decisions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ThoughtStep(BaseModel):
    """A single step in chain-of-thought reasoning."""
    step_number: int
    thought: str
    observation: Optional[str] = None
    conclusion: Optional[str] = None
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class ReasoningChain(BaseModel):
    """Complete chain-of-thought reasoning."""
    task: str
    steps: List[ThoughtStep] = Field(default_factory=list)
    final_conclusion: str = ""
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning_time_ms: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Reasoning templates for different tasks (USP)
REASONING_TEMPLATES = {
    "activity_assessment": """
Let's analyze this activity step by step:

Step 1: Understand the activity
- What is the activity? {activity_name}
- What category does it fall under? {category}
- What is the time commitment? {hours_per_week} hours/week

Step 2: Evaluate impact and leadership
- What impact has the student made?
- Is there evidence of leadership?
- Are there measurable outcomes?

Step 3: Consider uniqueness and fit
- How does this differentiate the student?
- Does it align with their spike?
- What story does it tell?

Step 4: Identify gaps and opportunities
- What's missing that could strengthen this?
- What would take this to the next level?

Final Assessment: [Synthesize above into recommendation]
""",

    "spike_identification": """
Let's identify the student's spike through structured analysis:

Step 1: Review all activities and achievements
{activities_list}

Step 2: Look for patterns and themes
- What areas show the deepest commitment?
- Where has the student achieved the most?
- What connects multiple activities?

Step 3: Identify the unique angle
- What makes this student different from others with similar interests?
- What specific domain within the broader field?
- What population or problem do they focus on?

Step 4: Test the spike hypothesis
- Does it explain most of their activities?
- Can it anchor a compelling narrative?
- Is it specific enough to be memorable?

Spike Identification: [Specific spike statement]
""",

    "school_fit": """
Let's evaluate school fit systematically:

Step 1: Understand student profile
- Spike: {spike}
- Archetype: {archetype}
- GPA: {gpa}
- Key achievements: {achievements}

Step 2: Analyze school requirements
- Academic threshold: {school_gpa}
- Program strengths: {school_programs}
- Culture fit factors: {school_culture}

Step 3: Assess match quality
- Academic fit (GPA, test scores)
- Program fit (major, research opportunities)
- Culture fit (values, community)
- Spike fit (opportunities to continue/grow)

Step 4: Consider strategic positioning
- Is this a reach, target, or safety?
- What unique value does student bring?
- What essays could highlight fit?

School Fit Assessment: [Rating and rationale]
""",

    "award_recommendation": """
Let's evaluate this award opportunity:

Step 1: Understand the award
- Name: {award_name}
- Category: {category}
- Selectivity: {selectivity}
- Deadline: {deadline}

Step 2: Assess student eligibility
- Does student meet basic requirements?
- Is student's profile competitive?
- Is timing appropriate?

Step 3: Evaluate strategic fit
- Does it align with spike?
- Would it strengthen weak areas?
- What's the opportunity cost?

Step 4: Determine priority
- Urgency (deadline proximity)
- Impact (how much would winning help?)
- Feasibility (likelihood of success)

Recommendation: [Priority level and action items]
""",
}


class ChainOfThoughtReasoner:
    """
    Implements chain-of-thought reasoning for agent decisions.

    Pattern A4: Chain-of-Thought (3P: OpenAI/Anthropic)

    Why this matters:
    1. Makes reasoning transparent
    2. Improves decision quality
    3. Enables debugging and improvement
    4. Builds trust with users
    """

    def __init__(
        self,
        llm_client=None,
        templates: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize reasoner.

        Args:
            llm_client: LLM client for reasoning (OpenAI/Anthropic)
            templates: Custom reasoning templates
        """
        self.llm = llm_client
        self.templates = templates or REASONING_TEMPLATES

    async def reason(
        self,
        task_type: str,
        context: Dict[str, Any],
        max_steps: int = 5,
    ) -> ReasoningChain:
        """
        Perform chain-of-thought reasoning.

        Args:
            task_type: Type of reasoning task
            context: Context variables for template
            max_steps: Maximum reasoning steps

        Returns:
            ReasoningChain with steps and conclusion
        """
        start_time = datetime.utcnow()

        # Get template
        template = self.templates.get(task_type)
        if not template:
            logger.warning(f"No template for task type: {task_type}")
            template = self._default_template(task_type)

        # Fill template with context
        filled_template = self._fill_template(template, context)

        # If we have an LLM, use it for reasoning
        if self.llm:
            chain = await self._llm_reasoning(filled_template, task_type, max_steps)
        else:
            # Fallback to template-based reasoning
            chain = self._template_reasoning(filled_template, task_type)

        # Calculate timing
        end_time = datetime.utcnow()
        chain.reasoning_time_ms = int((end_time - start_time).total_seconds() * 1000)

        return chain

    async def _llm_reasoning(
        self,
        prompt: str,
        task_type: str,
        max_steps: int,
    ) -> ReasoningChain:
        """Use LLM for chain-of-thought reasoning."""
        try:
            # Build the CoT prompt
            system_prompt = """
You are a college admissions expert using chain-of-thought reasoning.
Think step by step, showing your reasoning at each stage.
Be specific and evidence-based in your analysis.
End with a clear conclusion and confidence level (0-100%).
"""

            response = await self.llm.chat.completions.create(
                model="gpt-4",  # Or claude-3-sonnet
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            content = response.choices[0].message.content
            return self._parse_llm_response(content, task_type)

        except Exception as e:
            logger.error(f"LLM reasoning failed: {e}")
            return self._template_reasoning(prompt, task_type)

    def _template_reasoning(
        self,
        filled_template: str,
        task_type: str,
    ) -> ReasoningChain:
        """Fallback template-based reasoning (no LLM)."""
        lines = filled_template.strip().split("\n")
        steps = []
        current_step = None

        for line in lines:
            line = line.strip()
            if line.startswith("Step"):
                if current_step:
                    steps.append(current_step)
                step_num = len(steps) + 1
                current_step = ThoughtStep(
                    step_number=step_num,
                    thought=line,
                )
            elif current_step and line.startswith("-"):
                current_step.observation = (
                    (current_step.observation or "") + line + "\n"
                )
            elif "Assessment:" in line or "Conclusion:" in line or "Recommendation:" in line:
                if current_step:
                    steps.append(current_step)
                    current_step = None

        if current_step:
            steps.append(current_step)

        # Calculate overall confidence
        if steps:
            overall_confidence = sum(s.confidence for s in steps) / len(steps)
        else:
            overall_confidence = 0.5

        return ReasoningChain(
            task=task_type,
            steps=steps,
            final_conclusion="Analysis complete based on template reasoning",
            overall_confidence=overall_confidence,
        )

    def _parse_llm_response(
        self,
        response: str,
        task_type: str,
    ) -> ReasoningChain:
        """Parse LLM response into ReasoningChain."""
        lines = response.strip().split("\n")
        steps = []
        current_step = None
        final_conclusion = ""

        for line in lines:
            line = line.strip()

            # Detect step headers
            if any(line.lower().startswith(f"step {i}") for i in range(1, 10)):
                if current_step:
                    steps.append(current_step)
                step_num = len(steps) + 1
                current_step = ThoughtStep(
                    step_number=step_num,
                    thought=line,
                )

            # Detect conclusions
            elif any(keyword in line.lower() for keyword in [
                "conclusion", "assessment", "recommendation", "final"
            ]):
                if current_step:
                    steps.append(current_step)
                    current_step = None
                final_conclusion = line

            # Add to current step
            elif current_step:
                current_step.thought += "\n" + line

        if current_step:
            steps.append(current_step)

        # Extract confidence if mentioned
        confidence = 0.7
        if "%" in response:
            import re
            matches = re.findall(r"(\d+)%", response)
            if matches:
                confidence = int(matches[-1]) / 100

        return ReasoningChain(
            task=task_type,
            steps=steps,
            final_conclusion=final_conclusion or "Analysis complete",
            overall_confidence=confidence,
        )

    def _fill_template(
        self,
        template: str,
        context: Dict[str, Any],
    ) -> str:
        """Fill template placeholders with context values."""
        filled = template
        for key, value in context.items():
            placeholder = "{" + key + "}"
            if placeholder in filled:
                filled = filled.replace(placeholder, str(value))
        return filled

    def _default_template(self, task_type: str) -> str:
        """Generate default template for unknown task types."""
        return f"""
Let's analyze this {task_type} step by step:

Step 1: Understand the inputs
- What information do we have?
- What are we trying to determine?

Step 2: Apply relevant criteria
- What factors should we consider?
- How do we weight different aspects?

Step 3: Synthesize findings
- What patterns emerge?
- What conclusion follows?

Final Assessment: [Your conclusion here]
"""


# Convenience function
async def think_step_by_step(
    task_type: str,
    context: Dict[str, Any],
    llm_client=None,
) -> ReasoningChain:
    """
    Quick helper for chain-of-thought reasoning.

    Usage:
        chain = await think_step_by_step(
            "activity_assessment",
            {"activity_name": "Debate Club", "category": "academic", "hours_per_week": 5}
        )
    """
    reasoner = ChainOfThoughtReasoner(llm_client)
    return await reasoner.reason(task_type, context)
