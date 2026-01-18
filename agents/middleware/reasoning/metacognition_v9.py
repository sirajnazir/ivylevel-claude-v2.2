"""
Metacognition - Self-reflection and reasoning about reasoning.

Pattern: A12
3P: OpenAI (LLM for self-reflection)
Lines: ~120 (thin wrapper)

Features:
- Analyze own reasoning process
- Identify knowledge gaps
- Estimate confidence
- Suggest improvements
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class MetacognitiveInsight(BaseModel):
    """An insight from metacognitive analysis."""
    insight_type: str  # confidence, gap, assumption, limitation
    description: str
    confidence: float = 0.5
    suggestion: Optional[str] = None


class MetacognitiveAnalysis(BaseModel):
    """Result of metacognitive analysis."""
    overall_confidence: float = 0.5
    insights: List[MetacognitiveInsight] = Field(default_factory=list)
    knowledge_gaps: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)


METACOGNITION_PROMPT = """Analyze your reasoning process for the response you just gave.

Your response was:
{response}

The user's question/request was:
{request}

Reflect on your reasoning and provide a JSON analysis with:
1. overall_confidence: 0-1 score of how confident you are in your response
2. knowledge_gaps: List of topics you may need more information about
3. assumptions: List of assumptions you made
4. limitations: Any limitations in your response
5. suggested_actions: Actions that could improve the response

Respond with valid JSON only."""


class Metacognitor:
    """
    Self-reflection and reasoning analysis.

    Pattern A12: Metacognition
    3P: OpenAI (LLM for self-reflection)

    Thin wrapper - uses LLM for self-reflection on reasoning.
    """

    MODEL = "gpt-4o-mini"

    def __init__(self, openai_client=None):
        self.openai = openai_client
        self._initialized = openai_client is not None

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def analyze(
        self,
        request: str,
        response: str,
    ) -> MetacognitiveAnalysis:
        """Analyze a response for metacognitive insights."""
        if not self.is_available:
            logger.warning("Metacognitor not available - no OpenAI client")
            return MetacognitiveAnalysis()

        try:
            result = self.openai.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a metacognitive analyzer. Reflect on AI reasoning and provide structured insights."
                    },
                    {
                        "role": "user",
                        "content": METACOGNITION_PROMPT.format(
                            response=response[:2000],  # Truncate for efficiency
                            request=request[:500],
                        )
                    }
                ],
                response_format={"type": "json_object"},
            )

            data = json.loads(result.choices[0].message.content)

            insights = []

            # Convert gaps to insights
            for gap in data.get("knowledge_gaps", []):
                insights.append(MetacognitiveInsight(
                    insight_type="gap",
                    description=gap,
                    confidence=0.5,
                ))

            # Convert assumptions to insights
            for assumption in data.get("assumptions", []):
                insights.append(MetacognitiveInsight(
                    insight_type="assumption",
                    description=assumption,
                    confidence=0.6,
                ))

            # Convert limitations to insights
            for limitation in data.get("limitations", []):
                insights.append(MetacognitiveInsight(
                    insight_type="limitation",
                    description=limitation,
                    confidence=0.7,
                ))

            return MetacognitiveAnalysis(
                overall_confidence=data.get("overall_confidence", 0.5),
                insights=insights,
                knowledge_gaps=data.get("knowledge_gaps", []),
                assumptions=data.get("assumptions", []),
                limitations=data.get("limitations", []),
                suggested_actions=data.get("suggested_actions", []),
            )
        except Exception as e:
            logger.error(f"Metacognitive analysis failed: {e}")
            return MetacognitiveAnalysis()

    async def estimate_confidence(
        self,
        response: str,
        domain: Optional[str] = None,
    ) -> float:
        """Estimate confidence in a response."""
        if not self.is_available:
            return 0.5

        try:
            result = self.openai.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You estimate confidence in AI responses. Return only a number 0-1."
                    },
                    {
                        "role": "user",
                        "content": f"Rate confidence (0-1) for this response{f' in the {domain} domain' if domain else ''}:\n\n{response[:1000]}"
                    }
                ],
            )

            content = result.choices[0].message.content.strip()
            return min(1.0, max(0.0, float(content)))
        except Exception:
            return 0.5

    def check_for_uncertainty_markers(
        self,
        text: str,
    ) -> List[str]:
        """Check text for markers of uncertainty."""
        markers = []

        uncertainty_phrases = [
            "I'm not sure",
            "I think",
            "might be",
            "could be",
            "possibly",
            "probably",
            "perhaps",
            "it's possible",
            "I believe",
            "may",
        ]

        text_lower = text.lower()
        for phrase in uncertainty_phrases:
            if phrase.lower() in text_lower:
                markers.append(phrase)

        return markers

    def should_ask_for_clarification(
        self,
        analysis: MetacognitiveAnalysis,
        threshold: float = 0.5,
    ) -> bool:
        """Determine if clarification should be requested."""
        if analysis.overall_confidence < threshold:
            return True

        if len(analysis.knowledge_gaps) > 2:
            return True

        if len(analysis.assumptions) > 3:
            return True

        return False

    def get_improvement_suggestions(
        self,
        analysis: MetacognitiveAnalysis,
    ) -> List[str]:
        """Get suggestions for improving a response."""
        suggestions = list(analysis.suggested_actions)

        # Add suggestions based on insights
        if analysis.knowledge_gaps:
            suggestions.append(f"Research these topics: {', '.join(analysis.knowledge_gaps[:3])}")

        if analysis.assumptions:
            suggestions.append("Validate assumptions with the user")

        if analysis.overall_confidence < 0.5:
            suggestions.append("Consider asking for more context")

        return suggestions
