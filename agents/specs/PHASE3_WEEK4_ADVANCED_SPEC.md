# Phase 3 Week 4: Advanced Reasoning & Safety Patterns Implementation Spec

## Overview

Week 4 focuses on advanced reasoning patterns and safety mechanisms.

| Pattern | ID | Priority | Dependencies |
|---------|-----|----------|--------------|
| Tree of Thought | A5 | High | OpenAI |
| Meta-Cognition | A12 | Medium | J1 (Reasoning Traces) |
| Content Moderation | F5 | High | OpenAI Moderation API / Guardrails |
| PII Detection | F6 | High | Regex + Guardrails AI |

### 3P Systems Used

| System | Purpose | Already in Use? |
|--------|---------|-----------------|
| **OpenAI** | ToT reasoning, Moderation API | ✅ Yes |
| **Guardrails AI** | Content/PII validation | ✅ Yes |
| **Langfuse** | Meta-cognition traces | ✅ Yes |

---

## A5: Tree of Thought

### Purpose
Explores multiple reasoning paths in parallel, evaluates them, and selects the best path. Superior to Chain-of-Thought for complex problems.

### 3P System Choice: **OpenAI + LangGraph** (Optional)

**Why:**
- ✅ Already using OpenAI - native LLM support
- ✅ Already using LangGraph - can model as graph if needed
- ✅ No new dependencies

**Design Choice:** Pure OpenAI implementation (simpler) vs LangGraph (more structured).
**Recommendation:** Start with pure OpenAI, add LangGraph if branching becomes complex.

### File: `middleware/reasoning/tot_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ThoughtNode(BaseModel):
    """A node in the thought tree."""
    id: str
    content: str
    parent_id: Optional[str] = None
    depth: int = 0
    evaluation_score: float = 0.0
    is_terminal: bool = False
    is_selected: bool = False
    children: List[str] = []  # Child node IDs
    metadata: Dict[str, Any] = {}


class ThoughtTree(BaseModel):
    """A complete thought tree."""
    id: str
    goal: str
    root_id: str
    nodes: Dict[str, ThoughtNode]
    max_depth: int
    best_path: List[str] = []  # Path of selected node IDs
    final_answer: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class TreeOfThoughtConfig(BaseModel):
    """Configuration for ToT execution."""
    max_depth: int = 3
    branching_factor: int = 3  # How many children per node
    evaluation_threshold: float = 0.5  # Min score to continue
    beam_width: int = 2  # Top K paths to keep at each level
    temperature: float = 0.7  # LLM temperature for diversity


class TreeOfThought:
    """
    Tree of Thought reasoning for complex problems.

    Explores multiple reasoning paths in parallel:
    1. Generate initial thoughts (branches)
    2. Evaluate each thought
    3. Expand promising thoughts
    4. Prune low-quality thoughts
    5. Converge to final answer

    Best for:
    - Complex planning problems
    - Multi-step reasoning
    - Problems with multiple valid approaches
    """

    def __init__(
        self,
        llm_client=None,
        config: Optional[TreeOfThoughtConfig] = None,
    ):
        """
        Initialize Tree of Thought.

        Args:
            llm_client: OpenAI client (already in use)
            config: ToT configuration
        """
        self.llm = llm_client
        self.config = config or TreeOfThoughtConfig()

    async def solve(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        evaluator: Optional[Callable] = None,
    ) -> ThoughtTree:
        """
        Solve a problem using Tree of Thought.

        Args:
            goal: The problem to solve
            context: Additional context
            evaluator: Optional custom evaluator function

        Returns:
            Complete thought tree with best path
        """
        pass

    async def generate_thoughts(
        self,
        parent_thought: str,
        goal: str,
        context: Dict[str, Any],
        count: int,
    ) -> List[str]:
        """Generate child thoughts from a parent thought."""
        pass

    async def evaluate_thought(
        self,
        thought: str,
        goal: str,
        context: Dict[str, Any],
    ) -> float:
        """
        Evaluate a thought's promise (0-1).

        Uses LLM to assess:
        - Relevance to goal
        - Logical coherence
        - Completeness
        - Progress toward solution
        """
        pass

    async def expand_tree(
        self,
        tree: ThoughtTree,
        depth: int,
    ) -> ThoughtTree:
        """Expand tree to specified depth."""
        pass

    async def prune_tree(
        self,
        tree: ThoughtTree,
    ) -> ThoughtTree:
        """Prune low-quality branches."""
        pass

    async def select_best_path(
        self,
        tree: ThoughtTree,
    ) -> List[str]:
        """Select the best path through the tree."""
        pass

    async def synthesize_answer(
        self,
        tree: ThoughtTree,
        path: List[str],
    ) -> str:
        """Synthesize final answer from best path."""
        pass

    def _build_generation_prompt(
        self,
        parent_thought: str,
        goal: str,
        context: Dict[str, Any],
    ) -> str:
        """Build prompt for thought generation."""
        pass

    def _build_evaluation_prompt(
        self,
        thought: str,
        goal: str,
    ) -> str:
        """Build prompt for thought evaluation."""
        pass
```

### Test File: `tests/phase3/test_tree_of_thought.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.reasoning.tot_v9 import (
    TreeOfThought,
    TreeOfThoughtConfig,
    ThoughtTree,
    ThoughtNode,
)


class TestTreeOfThought:
    """Tests for A5: Tree of Thought."""

    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.chat = MagicMock()
        llm.chat.completions = MagicMock()
        llm.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(
                message=MagicMock(content="Generated thought")
            )]
        ))
        return llm

    @pytest.fixture
    def tot(self, mock_llm):
        return TreeOfThought(
            llm_client=mock_llm,
            config=TreeOfThoughtConfig(
                max_depth=2,
                branching_factor=2,
            ),
        )

    @pytest.mark.asyncio
    async def test_solve_returns_tree(self, tot):
        """Test solving a problem."""
        tree = await tot.solve(
            goal="Plan a summer research project",
            context={"student_interests": ["biology", "AI"]},
        )

        assert isinstance(tree, ThoughtTree)
        assert tree.goal == "Plan a summer research project"

    @pytest.mark.asyncio
    async def test_generate_thoughts_returns_list(self, tot):
        """Test thought generation."""
        thoughts = await tot.generate_thoughts(
            parent_thought="Start planning",
            goal="Plan a project",
            context={},
            count=3,
        )

        assert isinstance(thoughts, list)

    @pytest.mark.asyncio
    async def test_evaluate_thought_returns_score(self, tot):
        """Test thought evaluation."""
        score = await tot.evaluate_thought(
            thought="Research local labs for opportunities",
            goal="Find summer research",
            context={},
        )

        assert isinstance(score, float)
        assert 0 <= score <= 1

    @pytest.mark.asyncio
    async def test_tree_respects_max_depth(self, tot):
        """Test tree depth is bounded."""
        tree = await tot.solve(goal="Test goal")

        max_actual_depth = max(
            node.depth for node in tree.nodes.values()
        ) if tree.nodes else 0

        assert max_actual_depth <= tot.config.max_depth

    @pytest.mark.asyncio
    async def test_best_path_is_selected(self, tot):
        """Test best path selection."""
        tree = await tot.solve(goal="Test goal")

        assert len(tree.best_path) > 0

    @pytest.mark.asyncio
    async def test_custom_evaluator(self, tot):
        """Test custom evaluator function."""
        async def custom_eval(thought, goal, context):
            return 0.9 if "good" in thought.lower() else 0.1

        tree = await tot.solve(
            goal="Test goal",
            evaluator=custom_eval,
        )

        assert tree is not None
```

---

## A12: Meta-Cognition

### Purpose
Agent reflects on its own reasoning process, identifies biases, and adjusts approach accordingly.

### 3P System Choice: **OpenAI + Langfuse**

**Why:**
- ✅ OpenAI for meta-cognitive reasoning
- ✅ Langfuse for trace visualization (already integrated)
- ✅ Builds on J1 (Reasoning Traces) already implemented

### File: `middleware/reasoning/metacognition_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BiasType(str, Enum):
    """Types of cognitive biases."""
    CONFIRMATION = "confirmation"  # Seeking confirming evidence
    ANCHORING = "anchoring"  # Over-relying on first info
    AVAILABILITY = "availability"  # Over-weighting recent info
    RECENCY = "recency"  # Favoring recent interactions
    OVERCONFIDENCE = "overconfidence"  # Unjustified certainty


class MetaCognitiveInsight(BaseModel):
    """An insight from meta-cognitive reflection."""
    insight_type: str
    description: str
    severity: float  # 0-1
    recommendation: str
    affected_steps: List[str] = []


class MetaCognitiveReport(BaseModel):
    """Complete meta-cognitive analysis."""
    trace_id: str
    biases_detected: List[BiasType]
    insights: List[MetaCognitiveInsight]
    overall_quality: float
    recommended_adjustments: List[str]
    confidence_calibration: float  # How well-calibrated is confidence
    created_at: datetime


class MetaCognition:
    """
    Meta-cognitive reflection on reasoning processes.

    Analyzes reasoning traces (J1) to:
    - Detect cognitive biases
    - Identify reasoning gaps
    - Calibrate confidence levels
    - Suggest adjustments

    Enables agents to "think about their thinking."
    """

    def __init__(
        self,
        llm_client=None,
        langfuse_client=None,
        trace_collector=None,  # J1 ReasoningTraceCollector
    ):
        """
        Initialize meta-cognition.

        Args:
            llm_client: OpenAI for meta-cognitive reasoning
            langfuse_client: Langfuse for trace access
            trace_collector: J1 trace collector
        """
        self.llm = llm_client
        self.langfuse = langfuse_client
        self.traces = trace_collector

    async def analyze_trace(
        self,
        trace_id: str,
    ) -> MetaCognitiveReport:
        """
        Analyze a reasoning trace for biases and issues.

        Args:
            trace_id: ID of the reasoning trace to analyze

        Returns:
            Complete meta-cognitive report
        """
        pass

    async def analyze_session(
        self,
        session_id: str,
    ) -> List[MetaCognitiveReport]:
        """Analyze all traces in a session."""
        pass

    async def detect_biases(
        self,
        reasoning_steps: List[Dict[str, Any]],
    ) -> List[BiasType]:
        """
        Detect cognitive biases in reasoning.

        Checks for:
        - Confirmation bias
        - Anchoring bias
        - Availability heuristic
        - Recency bias
        - Overconfidence
        """
        pass

    async def calibrate_confidence(
        self,
        trace_id: str,
        actual_outcome: Optional[str] = None,
    ) -> float:
        """
        Calibrate confidence based on outcomes.

        Returns calibration score (1.0 = perfectly calibrated)
        """
        pass

    async def suggest_adjustments(
        self,
        report: MetaCognitiveReport,
    ) -> List[str]:
        """
        Suggest adjustments based on meta-cognitive analysis.

        Returns actionable adjustments for future reasoning.
        """
        pass

    async def apply_corrections(
        self,
        original_output: str,
        insights: List[MetaCognitiveInsight],
    ) -> str:
        """
        Apply meta-cognitive corrections to output.

        Uses insights to improve/correct the original output.
        """
        pass

    def _build_bias_detection_prompt(
        self,
        reasoning_steps: List[Dict[str, Any]],
    ) -> str:
        """Build prompt for bias detection."""
        pass
```

### Test File: `tests/phase3/test_metacognition.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.reasoning.metacognition_v9 import (
    MetaCognition,
    MetaCognitiveReport,
    MetaCognitiveInsight,
    BiasType,
)


class TestMetaCognition:
    """Tests for A12: Meta-Cognition."""

    @pytest.fixture
    def mock_trace_collector(self):
        collector = MagicMock()
        collector.get_trace = AsyncMock(return_value=MagicMock(
            events=[
                {"type": "thought", "content": "First thought"},
                {"type": "action", "content": "Took action"},
            ]
        ))
        return collector

    @pytest.fixture
    def metacog(self, mock_trace_collector):
        return MetaCognition(
            llm_client=MagicMock(),
            trace_collector=mock_trace_collector,
        )

    @pytest.mark.asyncio
    async def test_analyze_trace_returns_report(self, metacog):
        """Test trace analysis."""
        report = await metacog.analyze_trace("test-trace-id")

        assert isinstance(report, MetaCognitiveReport)
        assert report.trace_id == "test-trace-id"

    @pytest.mark.asyncio
    async def test_detect_biases_returns_list(self, metacog):
        """Test bias detection."""
        biases = await metacog.detect_biases([
            {"type": "thought", "content": "As I already established..."},
            {"type": "thought", "content": "This confirms my initial view..."},
        ])

        assert isinstance(biases, list)

    @pytest.mark.asyncio
    async def test_calibrate_confidence(self, metacog):
        """Test confidence calibration."""
        calibration = await metacog.calibrate_confidence(
            trace_id="test-trace",
            actual_outcome="success",
        )

        assert isinstance(calibration, float)
        assert 0 <= calibration <= 1

    @pytest.mark.asyncio
    async def test_suggest_adjustments(self, metacog):
        """Test adjustment suggestions."""
        report = MetaCognitiveReport(
            trace_id="test",
            biases_detected=[BiasType.CONFIRMATION],
            insights=[],
            overall_quality=0.6,
            recommended_adjustments=[],
            confidence_calibration=0.8,
            created_at=datetime.utcnow(),
        )

        adjustments = await metacog.suggest_adjustments(report)

        assert isinstance(adjustments, list)

    @pytest.mark.asyncio
    async def test_apply_corrections(self, metacog):
        """Test applying corrections."""
        corrected = await metacog.apply_corrections(
            original_output="Original response",
            insights=[
                MetaCognitiveInsight(
                    insight_type="bias",
                    description="Confirmation bias detected",
                    severity=0.7,
                    recommendation="Consider alternative viewpoints",
                )
            ],
        )

        assert isinstance(corrected, str)
```

---

## F5: Content Moderation

### Purpose
Moderates content for appropriateness, especially important for minor students. Blocks harmful, inappropriate, or off-topic content.

### 3P System Choice: **OpenAI Moderation API + Guardrails AI**

**Why:**
- ✅ OpenAI Moderation API - fast, free, accurate for harmful content
- ✅ Guardrails AI already in use - custom validators
- ✅ Defense in depth - multiple layers

**Strategy:**
1. OpenAI Moderation API for harmful content (hate, violence, self-harm)
2. Guardrails AI for custom rules (off-topic, age-inappropriate)

### File: `middleware/safety/moderation_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ModerationCategory(str, Enum):
    """Content moderation categories."""
    HATE = "hate"
    HARASSMENT = "harassment"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    SEXUAL = "sexual"
    DANGEROUS = "dangerous"
    AGE_INAPPROPRIATE = "age_inappropriate"
    OFF_TOPIC = "off_topic"
    SPAM = "spam"


class ModerationResult(BaseModel):
    """Result of content moderation."""
    flagged: bool
    categories: List[ModerationCategory]
    scores: Dict[str, float]  # Category -> score
    blocked: bool  # Should this content be blocked?
    reason: Optional[str] = None
    suggested_action: str = "allow"  # 'allow', 'flag', 'block', 'review'


class ContentModerator:
    """
    Content moderation for student safety.

    Uses:
    - OpenAI Moderation API for harmful content
    - Guardrails AI for custom rules
    - Custom validators for education context

    All content to/from students passes through moderation.
    """

    # Categories that should always block
    BLOCK_CATEGORIES = {
        ModerationCategory.VIOLENCE,
        ModerationCategory.SELF_HARM,
        ModerationCategory.SEXUAL,
        ModerationCategory.DANGEROUS,
    }

    # Categories that should flag for review
    FLAG_CATEGORIES = {
        ModerationCategory.HATE,
        ModerationCategory.HARASSMENT,
        ModerationCategory.AGE_INAPPROPRIATE,
    }

    def __init__(
        self,
        openai_client=None,
        guardrails_client=None,
    ):
        """
        Initialize content moderator.

        Args:
            openai_client: OpenAI client for Moderation API
            guardrails_client: Guardrails AI client
        """
        self.openai = openai_client
        self.guardrails = guardrails_client

    async def moderate(
        self,
        content: str,
        content_type: str = "message",
        context: Optional[Dict[str, Any]] = None,
    ) -> ModerationResult:
        """
        Moderate content for appropriateness.

        Args:
            content: Content to moderate
            content_type: Type of content (message, essay, response)
            context: Additional context (student grade, topic)

        Returns:
            ModerationResult with decision
        """
        pass

    async def moderate_input(
        self,
        user_input: str,
        profile_id: str,
    ) -> ModerationResult:
        """Moderate user input before processing."""
        pass

    async def moderate_output(
        self,
        agent_output: str,
        profile_id: str,
    ) -> ModerationResult:
        """Moderate agent output before sending to user."""
        pass

    async def _check_openai_moderation(
        self,
        content: str,
    ) -> Dict[str, Any]:
        """Call OpenAI Moderation API."""
        pass

    async def _check_guardrails(
        self,
        content: str,
        validators: List[str],
    ) -> Dict[str, Any]:
        """Run Guardrails AI validators."""
        pass

    def _is_off_topic(
        self,
        content: str,
        context: Dict[str, Any],
    ) -> bool:
        """Check if content is off-topic for education context."""
        pass

    def _is_age_appropriate(
        self,
        content: str,
        student_grade: int,
    ) -> bool:
        """Check if content is age-appropriate."""
        pass

    def _determine_action(
        self,
        categories: List[ModerationCategory],
        scores: Dict[str, float],
    ) -> str:
        """Determine action based on categories and scores."""
        pass
```

### Test File: `tests/phase3/test_content_moderation.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.safety.moderation_v9 import (
    ContentModerator,
    ModerationResult,
    ModerationCategory,
)


class TestContentModerator:
    """Tests for F5: Content Moderation."""

    @pytest.fixture
    def mock_openai(self):
        client = MagicMock()
        client.moderations = MagicMock()
        client.moderations.create = AsyncMock(return_value=MagicMock(
            results=[MagicMock(
                flagged=False,
                categories=MagicMock(
                    hate=False,
                    violence=False,
                    self_harm=False,
                    sexual=False,
                ),
                category_scores=MagicMock(
                    hate=0.01,
                    violence=0.02,
                    self_harm=0.01,
                    sexual=0.01,
                ),
            )]
        ))
        return client

    @pytest.fixture
    def moderator(self, mock_openai):
        return ContentModerator(openai_client=mock_openai)

    @pytest.mark.asyncio
    async def test_moderate_clean_content_allows(self, moderator):
        """Test clean content is allowed."""
        result = await moderator.moderate(
            content="Help me with my college essay about leadership",
        )

        assert isinstance(result, ModerationResult)
        assert result.flagged is False
        assert result.blocked is False

    @pytest.mark.asyncio
    async def test_moderate_harmful_content_blocks(self, moderator, mock_openai):
        """Test harmful content is blocked."""
        mock_openai.moderations.create.return_value = MagicMock(
            results=[MagicMock(
                flagged=True,
                categories=MagicMock(violence=True),
                category_scores=MagicMock(violence=0.95),
            )]
        )

        result = await moderator.moderate(
            content="Harmful content here",
        )

        assert result.flagged is True
        assert result.blocked is True
        assert ModerationCategory.VIOLENCE in result.categories

    @pytest.mark.asyncio
    async def test_moderate_input_checks_user_content(self, moderator):
        """Test input moderation."""
        result = await moderator.moderate_input(
            user_input="Hello, I need help",
            profile_id="test-profile",
        )

        assert isinstance(result, ModerationResult)

    @pytest.mark.asyncio
    async def test_moderate_output_checks_agent_content(self, moderator):
        """Test output moderation."""
        result = await moderator.moderate_output(
            agent_output="Here's your essay feedback",
            profile_id="test-profile",
        )

        assert isinstance(result, ModerationResult)

    @pytest.mark.asyncio
    async def test_off_topic_is_flagged(self, moderator):
        """Test off-topic content is flagged."""
        result = await moderator.moderate(
            content="What's the best cryptocurrency to invest in?",
            context={"topic": "college_admissions"},
        )

        # Off-topic should be flagged but not blocked
        assert result.suggested_action in ["flag", "block"]
```

---

## F6: PII Detection

### Purpose
Detects and redacts Personally Identifiable Information before processing or storage.

### 3P System Choice: **Guardrails AI + Regex**

**Why:**
- ✅ Guardrails AI already in use - has PII validators
- ✅ Regex for deterministic patterns (SSN, phone, email)
- ✅ Fast, no LLM cost

**Strategy:**
1. Regex for structured PII (SSN, phone, email, credit card)
2. Guardrails AI for context-aware PII (names in specific contexts)

### File: `middleware/safety/pii_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class PIIType(str, Enum):
    """Types of PII."""
    SSN = "ssn"
    PHONE = "phone"
    EMAIL = "email"
    CREDIT_CARD = "credit_card"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    DRIVERS_LICENSE = "drivers_license"
    PASSPORT = "passport"
    NAME = "name"  # Context-aware
    SCHOOL_ID = "school_id"


class PIIMatch(BaseModel):
    """A detected PII match."""
    pii_type: PIIType
    original: str
    redacted: str
    start_index: int
    end_index: int
    confidence: float


class PIIDetectionResult(BaseModel):
    """Result of PII detection."""
    contains_pii: bool
    matches: List[PIIMatch]
    redacted_text: str
    pii_types_found: List[PIIType]


class PIIDetector:
    """
    Detects and redacts Personally Identifiable Information.

    Uses:
    - Regex patterns for structured PII (SSN, phone, email)
    - Guardrails AI for context-aware PII (names)

    All content is checked before storage.
    """

    # Regex patterns for common PII
    PATTERNS = {
        PIIType.SSN: r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b',
        PIIType.PHONE: r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        PIIType.CREDIT_CARD: r'\b(?:\d{4}[-.\s]?){3}\d{4}\b',
        PIIType.DATE_OF_BIRTH: r'\b(?:0?[1-9]|1[0-2])[-/](?:0?[1-9]|[12]\d|3[01])[-/](?:19|20)\d{2}\b',
    }

    # Redaction format by type
    REDACTION_FORMAT = {
        PIIType.SSN: "[SSN REDACTED]",
        PIIType.PHONE: "[PHONE REDACTED]",
        PIIType.EMAIL: "[EMAIL REDACTED]",
        PIIType.CREDIT_CARD: "[CARD REDACTED]",
        PIIType.DATE_OF_BIRTH: "[DOB REDACTED]",
        PIIType.ADDRESS: "[ADDRESS REDACTED]",
        PIIType.NAME: "[NAME REDACTED]",
    }

    def __init__(
        self,
        guardrails_client=None,
        allow_email: bool = True,  # Emails often needed in edu context
    ):
        """
        Initialize PII detector.

        Args:
            guardrails_client: Guardrails AI for advanced detection
            allow_email: Whether to allow emails (common in edu)
        """
        self.guardrails = guardrails_client
        self.allow_email = allow_email
        self._compiled_patterns = {
            pii_type: re.compile(pattern, re.IGNORECASE)
            for pii_type, pattern in self.PATTERNS.items()
        }

    def detect(
        self,
        text: str,
        redact: bool = True,
    ) -> PIIDetectionResult:
        """
        Detect PII in text.

        Args:
            text: Text to scan
            redact: Whether to redact found PII

        Returns:
            PIIDetectionResult with matches and redacted text
        """
        pass

    def detect_and_redact(
        self,
        text: str,
    ) -> Tuple[str, List[PIIMatch]]:
        """
        Detect and redact PII in one step.

        Returns:
            Tuple of (redacted_text, matches)
        """
        pass

    async def detect_with_context(
        self,
        text: str,
        context_type: str,
    ) -> PIIDetectionResult:
        """
        Context-aware PII detection using Guardrails.

        Better at detecting names and contextual PII.
        """
        pass

    def _detect_regex_patterns(
        self,
        text: str,
    ) -> List[PIIMatch]:
        """Detect PII using regex patterns."""
        pass

    def _redact_text(
        self,
        text: str,
        matches: List[PIIMatch],
    ) -> str:
        """Redact PII from text."""
        pass

    def is_safe_for_storage(
        self,
        text: str,
    ) -> bool:
        """Check if text is safe for storage (no PII)."""
        result = self.detect(text, redact=False)
        return not result.contains_pii
```

### Test File: `tests/phase3/test_pii_detection.py`

```python
import pytest
from middleware.safety.pii_v9 import (
    PIIDetector,
    PIIDetectionResult,
    PIIMatch,
    PIIType,
)


class TestPIIDetector:
    """Tests for F6: PII Detection."""

    @pytest.fixture
    def detector(self):
        return PIIDetector()

    def test_detect_ssn(self, detector):
        """Test SSN detection."""
        result = detector.detect("My SSN is 123-45-6789")

        assert result.contains_pii is True
        assert PIIType.SSN in result.pii_types_found
        assert "[SSN REDACTED]" in result.redacted_text

    def test_detect_phone(self, detector):
        """Test phone number detection."""
        result = detector.detect("Call me at (555) 123-4567")

        assert result.contains_pii is True
        assert PIIType.PHONE in result.pii_types_found

    def test_detect_email(self, detector):
        """Test email detection."""
        detector_no_email = PIIDetector(allow_email=False)
        result = detector_no_email.detect("Contact john@example.com")

        assert result.contains_pii is True
        assert PIIType.EMAIL in result.pii_types_found

    def test_detect_credit_card(self, detector):
        """Test credit card detection."""
        result = detector.detect("Card: 1234-5678-9012-3456")

        assert result.contains_pii is True
        assert PIIType.CREDIT_CARD in result.pii_types_found

    def test_clean_text_no_pii(self, detector):
        """Test clean text has no PII."""
        result = detector.detect("I want to study computer science at MIT")

        assert result.contains_pii is False
        assert len(result.matches) == 0

    def test_redact_multiple_pii(self, detector):
        """Test multiple PII redaction."""
        text = "SSN: 123-45-6789, Phone: 555-123-4567"
        result = detector.detect(text)

        assert result.contains_pii is True
        assert "[SSN REDACTED]" in result.redacted_text
        assert "[PHONE REDACTED]" in result.redacted_text

    def test_detect_and_redact_returns_tuple(self, detector):
        """Test convenience method."""
        redacted, matches = detector.detect_and_redact("SSN: 123-45-6789")

        assert isinstance(redacted, str)
        assert isinstance(matches, list)

    def test_is_safe_for_storage(self, detector):
        """Test storage safety check."""
        assert detector.is_safe_for_storage("Clean text") is True
        assert detector.is_safe_for_storage("SSN: 123-45-6789") is False
```

---

## Implementation Checklist

### A5: Tree of Thought
- [ ] Create `middleware/reasoning/tot_v9.py`
- [ ] Implement `TreeOfThought` class
- [ ] Create tests in `tests/phase3/test_tree_of_thought.py`
- [ ] Run tests and verify passing

### A12: Meta-Cognition
- [ ] Create `middleware/reasoning/metacognition_v9.py`
- [ ] Implement `MetaCognition` class
- [ ] Create tests in `tests/phase3/test_metacognition.py`
- [ ] Run tests and verify passing

### F5: Content Moderation
- [ ] Create `middleware/safety/__init__.py`
- [ ] Create `middleware/safety/moderation_v9.py`
- [ ] Implement `ContentModerator` class
- [ ] Create tests in `tests/phase3/test_content_moderation.py`
- [ ] Run tests and verify passing

### F6: PII Detection
- [ ] Create `middleware/safety/pii_v9.py`
- [ ] Implement `PIIDetector` class
- [ ] Create tests in `tests/phase3/test_pii_detection.py`
- [ ] Run tests and verify passing

### Integration
- [ ] Add all patterns to `stack_v9.py`
- [ ] Wire moderation into agent input/output
- [ ] Create integration tests

---

*Phase 3 Week 4 Specification*
*Generated: 2026-01-17*
