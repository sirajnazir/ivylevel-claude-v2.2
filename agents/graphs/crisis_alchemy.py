"""
IvyQuest v10.0 Crisis Alchemy Protocol - LangGraph Implementation
================================================================
ACP-003: 4-step sequence to transform crises into opportunities.

CRITICAL: Uses LangGraph (NOT AutoGen) per v9.1 correction.

4-Step Protocol:
1. Validate (2 seconds) - Acknowledge emotion immediately, don't minimize
2. Act (10 seconds) - Give one concrete micro-action to restore agency
3. Reframe (30 seconds) - Find the opportunity angle in the setback
4. Create (2 minutes) - Design new activity or pivot from the crisis

Huda Benchmark: <72 hours recovery (Huda actual: <2 hours)
"""

from typing import TypedDict, Optional, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
import json
import structlog

from config import settings

logger = structlog.get_logger()


class CrisisState(TypedDict):
    """State passed through the Crisis Alchemy graph."""
    crisis_id: str
    profile_id: str
    type: str
    description: str
    urgency: int

    # Results from each step
    step1_validation: Optional[dict]
    step2_micro_action: Optional[dict]
    step3_reframe: Optional[dict]
    step4_creation: Optional[dict]

    # Control flow
    completed_steps: list
    error: Optional[str]


class CrisisAlchemyGraph:
    """
    4-Step Crisis Alchemy Protocol implemented with LangGraph.

    Each step builds on the previous:
    1. Validate → Acknowledge the emotion
    2. Act → Restore sense of agency
    3. Reframe → Find the opportunity
    4. Create → Design the comeback
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.agent_primary_model,
            temperature=0.7,
            api_key=settings.openai_api_key,
        )
        self.graph = self._build_graph()
        self.logger = logger.bind(component="CrisisAlchemyGraph")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        graph = StateGraph(CrisisState)

        # Add nodes for each step
        graph.add_node("validate", self._validate_step)
        graph.add_node("act", self._act_step)
        graph.add_node("reframe", self._reframe_step)
        graph.add_node("create", self._create_step)

        # Define edges (linear flow)
        graph.add_edge("validate", "act")
        graph.add_edge("act", "reframe")
        graph.add_edge("reframe", "create")
        graph.add_edge("create", END)

        # Set entry point
        graph.set_entry_point("validate")

        return graph.compile()

    async def _validate_step(self, state: CrisisState) -> CrisisState:
        """
        Step 1: Validate (2 seconds)
        Acknowledge the emotion immediately. Don't minimize.
        """
        self.logger.info("crisis_alchemy_step1", crisis_id=state["crisis_id"])

        prompt = f"""You are an empathetic counselor helping a high school student through a difficult moment.

CRISIS:
Type: {state['type']}
Description: {state['description']}
Urgency: {state['urgency']}/5

TASK: Generate a brief, empathetic validation message (2-3 sentences max).

RULES:
- Acknowledge their emotion FIRST
- Do NOT minimize their feelings
- Do NOT jump to solutions yet
- Use warm, supportive language
- Be genuine, not patronizing

Return JSON:
{{"message": "Your validation message", "emotion_acknowledged": "the emotion you identified"}}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an empathetic counselor. Respond only with valid JSON."),
                HumanMessage(content=prompt)
            ])

            result = self._parse_json_response(response.content, {
                "message": "I hear you. This is really difficult, and it's okay to feel this way.",
                "emotion_acknowledged": "frustration"
            })

            state["step1_validation"] = result
            state["completed_steps"] = state.get("completed_steps", []) + ["validate"]

        except Exception as e:
            self.logger.error("validate_step_error", error=str(e))
            state["step1_validation"] = {
                "message": "I hear you. This is a difficult situation, and your feelings are completely valid.",
                "emotion_acknowledged": "distress"
            }
            state["completed_steps"] = state.get("completed_steps", []) + ["validate"]

        return state

    async def _act_step(self, state: CrisisState) -> CrisisState:
        """
        Step 2: Act (10 seconds)
        Give ONE concrete micro-action to restore agency.
        """
        self.logger.info("crisis_alchemy_step2", crisis_id=state["crisis_id"])

        validation = state.get("step1_validation", {})

        prompt = f"""A student is going through a crisis. They've been validated with:
"{validation.get('message', '')}"

CRISIS:
Type: {state['type']}
Description: {state['description']}

TASK: Suggest ONE specific, immediately actionable micro-task (under 5 minutes) that will restore the student's sense of agency.

RULES:
- Must be completable in under 5 minutes
- Must be specific and concrete (not "think about it")
- Should give them a small win
- Should feel achievable even when overwhelmed

Examples:
- "Text one friend about this right now"
- "Write 3 bullet points of what happened"
- "Take a 2-minute walk around the block"
- "Write down one thing you can control"

Return JSON:
{{"action": "The specific micro-action", "duration_minutes": 5, "why_it_helps": "Brief explanation"}}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a practical counselor. Respond only with valid JSON."),
                HumanMessage(content=prompt)
            ])

            result = self._parse_json_response(response.content, {
                "action": "Write down exactly what happened in 3 bullet points",
                "duration_minutes": 5,
                "why_it_helps": "Writing it down helps process the experience and regain clarity"
            })

            state["step2_micro_action"] = result
            state["completed_steps"] = state.get("completed_steps", []) + ["act"]

        except Exception as e:
            self.logger.error("act_step_error", error=str(e))
            state["step2_micro_action"] = {
                "action": "Take 5 minutes to write down exactly what happened",
                "duration_minutes": 5,
                "why_it_helps": "Processing through writing restores clarity"
            }
            state["completed_steps"] = state.get("completed_steps", []) + ["act"]

        return state

    async def _reframe_step(self, state: CrisisState) -> CrisisState:
        """
        Step 3: Reframe (30 seconds)
        Find the opportunity angle in the setback.
        """
        self.logger.info("crisis_alchemy_step3", crisis_id=state["crisis_id"])

        prompt = f"""A student has experienced a setback and completed a micro-action to regain agency.

CRISIS:
Type: {state['type']}
Description: {state['description']}

TASK: Find the hidden opportunity in this setback. How can this crisis become a STRENGTH in their college application narrative?

REAL EXAMPLES (Jenny's coaching):
- "MSA exclusion" → Became founder of Muslim Girls Club (shows initiative, resilience)
- "Science fair rejection" → Pivoted to original research (shows adaptability)
- "Leadership dispute" → Started new organization (shows entrepreneurship)
- "Family duties preventing ECs" → Documented leadership at home (shows maturity)

RULES:
- Find a genuine opportunity, not toxic positivity
- Connect to college application narrative
- Be specific about how this helps their story
- Reference the SFFA rubric: barriers overcome score 4/5 in holistic admissions

Return JSON:
{{
    "opportunity_angle": "The opportunity found in this setback",
    "narrative_connection": "How this strengthens their college application story",
    "sffa_relevance": "How this maps to SFFA holistic criteria"
}}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a strategic college counselor. Respond only with valid JSON."),
                HumanMessage(content=prompt)
            ])

            result = self._parse_json_response(response.content, {
                "opportunity_angle": "This setback can become proof of resilience and adaptability",
                "narrative_connection": "Demonstrates ability to overcome obstacles - a key differentiator",
                "sffa_relevance": "Maps to 'overcoming barriers' which scores 4/5 in holistic review"
            })

            state["step3_reframe"] = result
            state["completed_steps"] = state.get("completed_steps", []) + ["reframe"]

        except Exception as e:
            self.logger.error("reframe_step_error", error=str(e))
            state["step3_reframe"] = {
                "opportunity_angle": "This experience reveals a gap that can become your unique contribution",
                "narrative_connection": "Shows resilience and ability to transform challenges into growth",
                "sffa_relevance": "Overcoming barriers is weighted 4/5 in holistic admissions"
            }
            state["completed_steps"] = state.get("completed_steps", []) + ["reframe"]

        return state

    async def _create_step(self, state: CrisisState) -> CrisisState:
        """
        Step 4: Create (2 minutes)
        Design a new activity or pivot from the crisis.
        """
        self.logger.info("crisis_alchemy_step4", crisis_id=state["crisis_id"])

        reframe = state.get("step3_reframe", {})

        prompt = f"""A student has reframed their crisis as an opportunity:
"{reframe.get('opportunity_angle', '')}"

CRISIS:
Type: {state['type']}
Description: {state['description']}

TASK: Design a concrete new activity or project that:
1. Transforms this crisis into a positive narrative
2. Has at least 4 application touchpoints (essay, interview, recommendation, activity list)
3. Can be started THIS WEEK
4. Connects to their existing interests/identity

TOUCHPOINTS TO CONSIDER:
1. Activity list entry
2. Essay topic
3. Interview talking point
4. Recommendation letter mention
5. Portfolio piece
6. Research opportunity
7. Leadership position

Return JSON:
{{
    "activity_name": "Name of the new activity/project",
    "description": "What this activity involves",
    "first_step": "The very first action to take (this week)",
    "touchpoints": ["list", "of", "touchpoints", "it serves"],
    "timeline_weeks": 8,
    "impact_potential": "What impact this could create"
}}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a strategic college counselor. Respond only with valid JSON."),
                HumanMessage(content=prompt)
            ])

            result = self._parse_json_response(response.content, {
                "activity_name": "Crisis Pivot Project",
                "description": "Document and share learnings from this experience",
                "first_step": "Draft a 1-paragraph reflection on what you learned",
                "touchpoints": ["essay", "interview", "activity"],
                "timeline_weeks": 8,
                "impact_potential": "Personal growth story that demonstrates resilience"
            })

            state["step4_creation"] = result
            state["completed_steps"] = state.get("completed_steps", []) + ["create"]

        except Exception as e:
            self.logger.error("create_step_error", error=str(e))
            state["step4_creation"] = {
                "activity_name": "Reflection and Growth Project",
                "description": "Transform this experience into a documented journey of growth",
                "first_step": "Schedule 30 minutes tomorrow to outline your next steps",
                "touchpoints": ["essay", "interview"],
                "timeline_weeks": 4,
                "impact_potential": "Authentic story of resilience for applications"
            }
            state["completed_steps"] = state.get("completed_steps", []) + ["create"]

        return state

    def _parse_json_response(self, content: str, fallback: dict) -> dict:
        """Parse JSON from LLM response with fallback."""
        try:
            # Try to extract JSON from response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            return json.loads(content.strip())
        except json.JSONDecodeError:
            self.logger.warning("json_parse_failed", content=content[:100])
            return fallback

    async def run(self, initial_state: dict) -> dict:
        """
        Execute the full 4-step Crisis Alchemy protocol.

        Args:
            initial_state: Dict with crisis_id, profile_id, type, description, urgency

        Returns:
            Complete state with all 4 step results
        """
        self.logger.info("crisis_alchemy_started", crisis_id=initial_state.get("crisis_id"))

        # Initialize state
        state: CrisisState = {
            "crisis_id": initial_state.get("crisis_id", "unknown"),
            "profile_id": initial_state.get("profile_id", "unknown"),
            "type": initial_state.get("type", "unknown"),
            "description": initial_state.get("description", ""),
            "urgency": initial_state.get("urgency", 3),
            "step1_validation": None,
            "step2_micro_action": None,
            "step3_reframe": None,
            "step4_creation": None,
            "completed_steps": [],
            "error": None,
        }

        try:
            # Run the graph
            result = await self.graph.ainvoke(state)

            self.logger.info(
                "crisis_alchemy_completed",
                crisis_id=initial_state.get("crisis_id"),
                steps_completed=result.get("completed_steps", [])
            )

            return result

        except Exception as e:
            self.logger.error("crisis_alchemy_error", error=str(e))
            state["error"] = str(e)
            return state
