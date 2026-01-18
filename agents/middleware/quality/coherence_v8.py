"""
E5: Coherence Checking Pattern - Implementation

Ensure multi-turn and multi-agent response coherence.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class CoherenceType(str, Enum):
    """Types of coherence to check."""
    LOGICAL = "logical"  # Internal logical consistency
    TEMPORAL = "temporal"  # Time-based consistency
    FACTUAL = "factual"  # Fact consistency across turns
    TONAL = "tonal"  # Consistent tone
    TOPICAL = "topical"  # Staying on topic


class CoherenceIssue(BaseModel):
    """A detected coherence issue."""
    issue_type: CoherenceType
    severity: str = "medium"  # low, medium, high
    description: str
    location: Optional[str] = None  # Where in the response
    suggestion: Optional[str] = None


class CoherenceResult(BaseModel):
    """Result of coherence check."""
    is_coherent: bool = True
    coherence_score: float = Field(default=0.8, ge=0.0, le=1.0)
    issues: List[CoherenceIssue] = Field(default_factory=list)
    type_scores: Dict[str, float] = Field(default_factory=dict)
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CoherenceChecker:
    """
    Checks coherence of responses across turns and agents.

    Pattern E5: Coherence Checking

    GUARDRAILS:
    - NEW class - does not modify existing coherence checks
    - Works with conversation history
    """

    def __init__(
        self,
        llm_client=None,
        min_coherence_score: float = 0.7,
    ):
        """
        Initialize coherence checker.

        Args:
            llm_client: LLM client for checking
            min_coherence_score: Minimum score to pass
        """
        self.llm = llm_client
        self.min_score = min_coherence_score

    async def check_coherence(
        self,
        current_response: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> CoherenceResult:
        """
        Check coherence of response with history.

        Args:
            current_response: Response to check
            conversation_history: Previous messages
            context: Additional context

        Returns:
            CoherenceResult with issues
        """
        issues = []
        type_scores = {}

        # Check each type of coherence
        for coherence_type in CoherenceType:
            score, type_issues = await self._check_type(
                coherence_type=coherence_type,
                response=current_response,
                history=conversation_history,
                context=context,
            )
            type_scores[coherence_type.value] = score
            issues.extend(type_issues)

        # Calculate overall score
        overall_score = sum(type_scores.values()) / len(type_scores)
        is_coherent = overall_score >= self.min_score and not any(
            i.severity == "high" for i in issues
        )

        return CoherenceResult(
            is_coherent=is_coherent,
            coherence_score=overall_score,
            issues=issues,
            type_scores=type_scores,
        )

    async def _check_type(
        self,
        coherence_type: CoherenceType,
        response: str,
        history: Optional[List[Dict[str, str]]],
        context: Optional[Dict[str, Any]],
    ) -> tuple:
        """Check specific type of coherence."""
        if self.llm:
            return await self._llm_check_type(
                coherence_type, response, history, context
            )
        return self._heuristic_check_type(
            coherence_type, response, history
        )

    async def _llm_check_type(
        self,
        coherence_type: CoherenceType,
        response: str,
        history: Optional[List[Dict[str, str]]],
        context: Optional[Dict[str, Any]],
    ) -> tuple:
        """Check coherence using LLM."""
        type_descriptions = {
            CoherenceType.LOGICAL: "Check for logical consistency and contradictions",
            CoherenceType.TEMPORAL: "Check for time-related consistency (dates, sequences)",
            CoherenceType.FACTUAL: "Check for factual consistency with previous statements",
            CoherenceType.TONAL: "Check for consistent tone throughout",
            CoherenceType.TOPICAL: "Check if response stays on topic",
        }

        history_text = ""
        if history:
            history_text = "\n".join([
                f"{m.get('role', 'user')}: {m.get('content', '')[:200]}..."
                for m in history[-5:]  # Last 5 messages
            ])

        prompt = f"""Check this response for {coherence_type.value} coherence.

Task: {type_descriptions[coherence_type]}

CONVERSATION HISTORY:
{history_text or "No history"}

CURRENT RESPONSE:
{response}

OUTPUT as JSON:
{{
    "score": 0.0-1.0,
    "issues": [
        {{"description": "...", "severity": "low/medium/high", "suggestion": "..."}}
    ]
}}

If no issues, return empty issues array."""

        try:
            result = await self.llm.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            import json
            content = result.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            data = json.loads(content)

            issues = [
                CoherenceIssue(
                    issue_type=coherence_type,
                    severity=i.get("severity", "medium"),
                    description=i.get("description", ""),
                    suggestion=i.get("suggestion"),
                )
                for i in data.get("issues", [])
            ]

            return (data.get("score", 0.8), issues)
        except Exception as e:
            logger.error(f"LLM coherence check failed: {e}")
            return self._heuristic_check_type(coherence_type, response, history)

    def _heuristic_check_type(
        self,
        coherence_type: CoherenceType,
        response: str,
        history: Optional[List[Dict[str, str]]],
    ) -> tuple:
        """Heuristic coherence check."""
        issues = []
        score = 0.8

        if coherence_type == CoherenceType.LOGICAL:
            # Check for contradictions
            contradiction_patterns = [
                (r"but\s+however", "Uses redundant contrasting conjunctions"),
                (r"always\s+never", "Contradictory absolute terms"),
                (r"definitely\s+maybe", "Contradictory certainty terms"),
            ]
            for pattern, desc in contradiction_patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    score -= 0.15
                    issues.append(CoherenceIssue(
                        issue_type=coherence_type,
                        severity="medium",
                        description=desc,
                    ))

        elif coherence_type == CoherenceType.TEMPORAL:
            # Check for time consistency
            if "yesterday" in response and "tomorrow" in response:
                # Check if they're used in contradictory ways
                if "yesterday we will" in response.lower():
                    score -= 0.2
                    issues.append(CoherenceIssue(
                        issue_type=coherence_type,
                        severity="high",
                        description="Past time reference with future action",
                    ))

        elif coherence_type == CoherenceType.TOPICAL:
            # Check topic drift from history
            if history and len(history) > 0:
                last_topics = self._extract_topics(
                    [m.get("content", "") for m in history[-3:]]
                )
                current_topics = self._extract_topics([response])

                if last_topics and current_topics:
                    overlap = len(last_topics & current_topics) / max(
                        len(last_topics), 1
                    )
                    if overlap < 0.2:
                        score -= 0.2
                        issues.append(CoherenceIssue(
                            issue_type=coherence_type,
                            severity="medium",
                            description="Response may have drifted from topic",
                        ))

        return (max(score, 0.0), issues)

    def _extract_topics(self, texts: List[str]) -> set:
        """Extract topic keywords from texts."""
        topics = set()
        # Simple keyword extraction
        topic_indicators = [
            "essay", "college", "application", "activity",
            "deadline", "school", "recommendation", "gpa",
            "test", "sat", "act", "major", "career",
        ]
        for text in texts:
            text_lower = text.lower()
            for indicator in topic_indicators:
                if indicator in text_lower:
                    topics.add(indicator)
        return topics

    async def check_multi_agent_coherence(
        self,
        responses: List[Dict[str, Any]],
    ) -> CoherenceResult:
        """
        Check coherence across multiple agent responses.

        Args:
            responses: List of {agent, response, timestamp} dicts

        Returns:
            CoherenceResult
        """
        issues = []
        type_scores = {t.value: 0.8 for t in CoherenceType}

        # Check for contradictions between agents
        if len(responses) >= 2:
            for i in range(len(responses) - 1):
                for j in range(i + 1, len(responses)):
                    r1 = responses[i]
                    r2 = responses[j]

                    # Simple factual consistency check
                    if self._detect_contradiction(
                        r1.get("response", ""),
                        r2.get("response", ""),
                    ):
                        type_scores["factual"] -= 0.2
                        issues.append(CoherenceIssue(
                            issue_type=CoherenceType.FACTUAL,
                            severity="high",
                            description=f"Potential contradiction between {r1.get('agent')} and {r2.get('agent')}",
                        ))

        overall_score = sum(type_scores.values()) / len(type_scores)

        return CoherenceResult(
            is_coherent=overall_score >= self.min_score,
            coherence_score=overall_score,
            issues=issues,
            type_scores=type_scores,
        )

    def _detect_contradiction(self, text1: str, text2: str) -> bool:
        """Detect potential contradiction between texts."""
        # Simple heuristic: look for opposite statements
        negation_pairs = [
            ("should", "should not"),
            ("can", "cannot"),
            ("will", "will not"),
            ("is required", "is not required"),
            ("is important", "is not important"),
        ]

        text1_lower = text1.lower()
        text2_lower = text2.lower()

        for pos, neg in negation_pairs:
            if pos in text1_lower and neg in text2_lower:
                return True
            if neg in text1_lower and pos in text2_lower:
                return True

        return False
