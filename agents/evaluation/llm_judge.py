"""
IvyQuest v10.0 - LLM-as-Judge
============================

LLM-based evaluation for subjective quality assessment.
Uses GPT-4 or Claude to score agent outputs against rubrics.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import structlog
from openai import AsyncOpenAI

logger = structlog.get_logger()


@dataclass
class JudgeScore:
    """A single dimension score from the judge."""
    dimension: str
    score: int  # 1-5
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'dimension': self.dimension,
            'score': self.score,
            'rationale': self.rationale,
        }


@dataclass
class JudgeResult:
    """Complete result from LLM judge evaluation."""
    scores: List[JudgeScore]
    overall_score: float  # 1.0-5.0
    top_weakness: str
    improvement_suggestion: str
    raw_response: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'scores': [s.to_dict() for s in self.scores],
            'overall_score': self.overall_score,
            'top_weakness': self.top_weakness,
            'improvement_suggestion': self.improvement_suggestion,
        }

    @property
    def normalized_score(self) -> float:
        """Get score normalized to 0-1 range."""
        return (self.overall_score - 1) / 4  # Convert 1-5 to 0-1


class LLMJudge:
    """LLM-as-judge for subjective quality evaluation."""

    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize the LLM judge.

        Args:
            model: Model to use for evaluation
        """
        self.model = model
        self.client = AsyncOpenAI()
        self.logger = logger.bind(component='llm_judge')

    async def evaluate_narrative(
        self,
        student_profile: Dict[str, Any],
        agent_output: Dict[str, Any],
        golden_output: Dict[str, Any],
        jenny_annotations: Dict[str, Any]
    ) -> JudgeResult:
        """
        Evaluate narrative synthesis quality.

        Args:
            student_profile: The student's input profile
            agent_output: Output from NarrativeSynthesisAgent
            golden_output: Expected output from Jenny Duan
            jenny_annotations: Jenny's quality notes

        Returns:
            JudgeResult with scores and feedback
        """
        prompt = self._build_narrative_prompt(
            student_profile,
            agent_output,
            golden_output,
            jenny_annotations
        )

        return await self._call_llm(prompt, 'narrative')

    async def evaluate_awards(
        self,
        student_profile: Dict[str, Any],
        agent_output: Dict[str, Any],
        golden_output: Dict[str, Any]
    ) -> JudgeResult:
        """
        Evaluate awards recommendations quality.

        Args:
            student_profile: The student's input profile
            agent_output: Output from AwardsAgent
            golden_output: Expected recommendations

        Returns:
            JudgeResult with scores and feedback
        """
        prompt = self._build_awards_prompt(
            student_profile,
            agent_output,
            golden_output
        )

        return await self._call_llm(prompt, 'awards')

    async def evaluate_crisis(
        self,
        crisis_context: Dict[str, Any],
        agent_response: Dict[str, Any],
        golden_response: Dict[str, Any]
    ) -> JudgeResult:
        """
        Evaluate Crisis Alchemy response quality.

        Args:
            crisis_context: The crisis situation context
            agent_response: Output from Crisis Alchemy
            golden_response: Expected response from Jenny

        Returns:
            JudgeResult with scores and feedback
        """
        prompt = self._build_crisis_prompt(
            crisis_context,
            agent_response,
            golden_response
        )

        return await self._call_llm(prompt, 'crisis')

    async def _call_llm(self, prompt: str, eval_type: str) -> JudgeResult:
        """
        Call the LLM and parse the response.

        Args:
            prompt: The evaluation prompt
            eval_type: Type of evaluation for logging

        Returns:
            JudgeResult
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator for college admissions coaching quality."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            self.logger.debug("llm_response", eval_type=eval_type, response_length=len(content or ''))

            return self._parse_response(content or '')

        except Exception as e:
            self.logger.error("llm_call_error", eval_type=eval_type, error=str(e))
            return JudgeResult(
                scores=[],
                overall_score=1.0,
                top_weakness=f"LLM call failed: {str(e)}",
                improvement_suggestion="",
                raw_response=""
            )

    def _build_narrative_prompt(
        self,
        profile: Dict[str, Any],
        agent: Dict[str, Any],
        golden: Dict[str, Any],
        annotations: Dict[str, Any]
    ) -> str:
        """Build prompt for narrative evaluation."""
        return f"""You are an expert evaluator for college admissions narrative synthesis.

Your task is to compare an AI agent's output against a golden reference from expert coach Jenny Duan.

=== STUDENT PROFILE ===
{json.dumps(profile, indent=2, default=str)}

=== GOLDEN REFERENCE (Jenny Duan) ===
Brand Statement: {golden.get('brand_statement', 'N/A')}
Themes: {golden.get('themes', [])}
First Principle: {golden.get('first_principle', 'N/A')}
Jenny's Quality Notes: {annotations.get('notes', 'N/A')}
Jenny's Scores: Brand={annotations.get('brand_statement_quality', 'N/A')}, Themes={annotations.get('theme_coherence', 'N/A')}, Activities={annotations.get('activity_alignment', 'N/A')}

=== AGENT OUTPUT ===
Brand Statement: {agent.get('brand_statement', 'N/A')}
Themes: {agent.get('themes', [])}
First Principle: {agent.get('first_principle', 'N/A')}
Narrative DNA: {(agent.get('narrative_dna', '') or '')[:500]}...

=== EVALUATION CRITERIA ===

Score each dimension from 1-5:

**1. AUTHENTICITY (Weight: 25%)**
- 5: Deeply personal, specific details, could only be about this student
- 4: Personal with some unique elements
- 3: Somewhat personal but has generic elements
- 2: Mostly generic with few personal touches
- 1: Could apply to many students, lacks specificity

**2. IDENTITY_INTEGRATION (Weight: 25%)**
- 5: Seamlessly integrates all identity elements into cohesive story
- 4: Integrates most elements well
- 3: Mentions elements but doesn't fully connect them
- 2: Misses some key elements
- 1: Misses or misrepresents major identity elements

**3. NARRATIVE_POWER (Weight: 20%)**
- 5: Would immediately stand out to admissions officers
- 4: Strong and memorable
- 3: Acceptable but not particularly memorable
- 2: Weak or confusing
- 1: Likely to hurt the application

**4. JENNY_ALIGNMENT (Weight: 15%)**
- 5: Indistinguishable from Jenny's work
- 4: Very similar approach and quality
- 3: Similar approach but different voice/depth
- 2: Somewhat different methodology
- 1: Completely different approach

**5. ACTIONABILITY (Weight: 15%)**
- 5: Ready to use, provides clear direction
- 4: Minor refinements needed
- 3: Needs some work but usable foundation
- 2: Significant refinement required
- 1: Too vague or wrong direction

=== OUTPUT FORMAT ===

Respond with valid JSON:
{{
  "scores": [
    {{"dimension": "authenticity", "score": <1-5>, "rationale": "<brief explanation>"}},
    {{"dimension": "identity_integration", "score": <1-5>, "rationale": "<brief>"}},
    {{"dimension": "narrative_power", "score": <1-5>, "rationale": "<brief>"}},
    {{"dimension": "jenny_alignment", "score": <1-5>, "rationale": "<brief>"}},
    {{"dimension": "actionability", "score": <1-5>, "rationale": "<brief>"}}
  ],
  "overall_score": <weighted average as float 1.0-5.0>,
  "top_weakness": "<single most important area to improve>",
  "improvement_suggestion": "<specific actionable suggestion>"
}}"""

    def _build_awards_prompt(
        self,
        profile: Dict[str, Any],
        agent: Dict[str, Any],
        golden: Dict[str, Any]
    ) -> str:
        """Build prompt for awards evaluation."""
        return f"""You are evaluating award recommendations for a college applicant.

=== STUDENT PROFILE ===
{json.dumps(profile, indent=2, default=str)}

=== GOLDEN REFERENCE (Expert recommendations) ===
{json.dumps(golden, indent=2, default=str)}

=== AGENT RECOMMENDATIONS ===
{json.dumps(agent, indent=2, default=str)}

=== EVALUATION CRITERIA ===

Score each dimension from 1-5:

**1. RELEVANCE**
- Do awards align with student's spike and narrative?
- Are they appropriate for the student's grade level and abilities?

**2. STRATEGIC_FIT**
- Would winning these strengthen the application?
- Do they complement existing achievements?

**3. ACHIEVABILITY**
- Is the likely/target/stretch balance realistic?
- Are success predictions reasonable?

**4. COMPREHENSIVENESS**
- Are important awards missing?
- Is there good coverage across categories?

**5. RATIONALE_QUALITY**
- Are the "why" explanations compelling?
- Do they connect awards to the student's story?

=== OUTPUT FORMAT ===

Respond with valid JSON:
{{
  "scores": [
    {{"dimension": "relevance", "score": <1-5>, "rationale": "<brief>"}},
    {{"dimension": "strategic_fit", "score": <1-5>, "rationale": "<brief>"}},
    {{"dimension": "achievability", "score": <1-5>, "rationale": "<brief>"}},
    {{"dimension": "comprehensiveness", "score": <1-5>, "rationale": "<brief>"}},
    {{"dimension": "rationale_quality", "score": <1-5>, "rationale": "<brief>"}}
  ],
  "overall_score": <float 1.0-5.0>,
  "top_weakness": "<single issue>",
  "improvement_suggestion": "<specific fix>"
}}"""

    def _build_crisis_prompt(
        self,
        context: Dict[str, Any],
        agent: Dict[str, Any],
        golden: Dict[str, Any]
    ) -> str:
        """Build prompt for crisis response evaluation."""
        return f"""You are evaluating a Crisis Alchemy response for a struggling student.

The Crisis Alchemy Protocol has 4 steps:
1. VALIDATE (2s) - Acknowledge emotion genuinely
2. ACT (10s) - Micro-action to restore agency
3. REFRAME (30s) - Find opportunity angle
4. CREATE (2min) - Design pivot activity

=== CRISIS CONTEXT ===
Type: {context.get('type', 'unknown')}
Student message: {context.get('message', 'N/A')}
Urgency: {context.get('urgency', 'N/A')}

=== GOLDEN RESPONSE (Jenny's approach) ===
Validation: {golden.get('validation', 'N/A')}
Micro-action: {golden.get('micro_action', 'N/A')}
Reframe: {golden.get('reframe', 'N/A')}
Pivot activity: {golden.get('pivot_activity', 'N/A')}

=== AGENT RESPONSE ===
Validation: {agent.get('validation', 'N/A')}
Micro-action: {agent.get('micro_action', 'N/A')}
Reframe: {agent.get('reframe', 'N/A')}
Pivot activity: {agent.get('pivot_activity', 'N/A')}

=== EVALUATION CRITERIA ===

Score each step from 1-5:

**1. VALIDATION_QUALITY**
- Is it genuine acknowledgment without toxic positivity?
- Does it name the emotion accurately?

**2. MICRO_ACTION_QUALITY**
- Is it truly small (<5 min)?
- Does it restore agency?

**3. REFRAME_QUALITY**
- Is there a genuine opportunity angle?
- Does it avoid minimizing the setback?

**4. PIVOT_ACTIVITY_QUALITY**
- Is it concrete and achievable?
- Does it transform the setback into strength?

**5. OVERALL_TONE**
- Does it have Jenny-like warmth and directness?
- Is it appropriately urgent for the situation?

=== OUTPUT FORMAT ===

Respond with valid JSON:
{{
  "scores": [
    {{"dimension": "validation_quality", "score": <1-5>, "rationale": "<brief>"}},
    {{"dimension": "micro_action_quality", "score": <1-5>, "rationale": "<brief>"}},
    {{"dimension": "reframe_quality", "score": <1-5>, "rationale": "<brief>"}},
    {{"dimension": "pivot_activity_quality", "score": <1-5>, "rationale": "<brief>"}},
    {{"dimension": "overall_tone", "score": <1-5>, "rationale": "<brief>"}}
  ],
  "overall_score": <float 1.0-5.0>,
  "top_weakness": "<issue>",
  "improvement_suggestion": "<fix>"
}}"""

    def _parse_response(self, content: str) -> JudgeResult:
        """
        Parse LLM response into JudgeResult.

        Args:
            content: Raw response content

        Returns:
            JudgeResult
        """
        try:
            # Clean potential markdown code blocks
            content = content.strip()
            if content.startswith('```'):
                lines = content.split('\n')
                content = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])
                if content.startswith('json'):
                    content = content[4:].strip()

            data = json.loads(content)

            scores = [
                JudgeScore(
                    dimension=s.get('dimension', 'unknown'),
                    score=int(s.get('score', 3)),
                    rationale=s.get('rationale', '')
                )
                for s in data.get('scores', [])
            ]

            overall = data.get('overall_score', 3.0)
            if isinstance(overall, str):
                overall = float(overall)

            return JudgeResult(
                scores=scores,
                overall_score=overall,
                top_weakness=data.get('top_weakness', ''),
                improvement_suggestion=data.get('improvement_suggestion', ''),
                raw_response=content
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.error("parse_response_error", error=str(e))
            return JudgeResult(
                scores=[],
                overall_score=1.0,
                top_weakness=f"Parse error: {str(e)}",
                improvement_suggestion="",
                raw_response=content
            )
