# Phase 3 Week 3: Learning Patterns Implementation Spec

## Overview

Week 3 focuses on implementing learning and adaptation capabilities for personalized agent behavior.

| Pattern | ID | Priority | Dependencies |
|---------|-----|----------|--------------|
| Learning From Feedback | I1 | High | Supabase |
| Adaptive Behavior | I2 | Medium | I1 |
| Personalization Engine | I3 | Medium | B2 (Episodic Memory), B4 |
| Pattern Recognition | I5 | Low | LLM, B4 |

### 3P Systems Used

| System | Purpose | Already in Use? |
|--------|---------|-----------------|
| **Supabase** | Feedback storage, patterns | ✅ Yes |
| **OpenAI** | Pattern recognition, adaptation | ✅ Yes |
| **Redis** | Real-time adaptation cache | ✅ Yes |

---

## I1: Learning From Feedback

### Purpose
Captures and learns from explicit user feedback (thumbs up/down, ratings, corrections) and implicit signals (engagement, time spent, follow-up questions).

### 3P System Choice: **Supabase**

**Why:**
- ✅ Already using Supabase - consistent data layer
- ✅ JSONB for flexible feedback metadata
- ✅ Can join with profiles and sessions

### File: `middleware/learning/feedback_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    """Types of feedback."""
    EXPLICIT_POSITIVE = "explicit_positive"  # Thumbs up, 5 stars
    EXPLICIT_NEGATIVE = "explicit_negative"  # Thumbs down, 1 star
    EXPLICIT_CORRECTION = "explicit_correction"  # User corrects output
    IMPLICIT_ENGAGEMENT = "implicit_engagement"  # Long session, multiple messages
    IMPLICIT_ABANDONMENT = "implicit_abandonment"  # User leaves quickly
    IMPLICIT_FOLLOWUP = "implicit_followup"  # User asks clarifying question


class FeedbackSignal(str, Enum):
    """Aggregated feedback signal."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class FeedbackEntry(BaseModel):
    """A feedback entry."""
    id: str
    profile_id: str
    session_id: str
    agent_name: str
    action_type: str  # What action was taken
    feedback_type: FeedbackType
    feedback_value: Optional[float] = None  # 0-1 for ratings
    feedback_text: Optional[str] = None  # For corrections
    context: Dict[str, Any] = {}  # What led to this feedback
    created_at: datetime


class FeedbackAggregation(BaseModel):
    """Aggregated feedback for an agent/action."""
    agent_name: str
    action_type: str
    total_feedback: int
    positive_count: int
    negative_count: int
    average_rating: float
    signal: FeedbackSignal
    last_updated: datetime


class FeedbackLearner:
    """
    Captures and learns from user feedback.

    Tracks:
    - Explicit feedback (ratings, corrections)
    - Implicit feedback (engagement patterns)
    - Aggregated signals per agent/action
    """

    def __init__(
        self,
        supabase_client=None,
        redis_client=None,
    ):
        """
        Initialize feedback learner.

        Args:
            supabase_client: Supabase for persistence
            redis_client: Redis for real-time aggregations
        """
        self.db = supabase_client
        self.redis = redis_client

    async def record_explicit_feedback(
        self,
        profile_id: str,
        session_id: str,
        agent_name: str,
        action_type: str,
        feedback_type: FeedbackType,
        feedback_value: Optional[float] = None,
        feedback_text: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> FeedbackEntry:
        """
        Record explicit user feedback.

        Args:
            profile_id: Profile giving feedback
            session_id: Session where feedback occurred
            agent_name: Agent that produced the output
            action_type: Type of action (e.g., "essay_feedback", "activity_suggestion")
            feedback_type: Type of feedback
            feedback_value: Rating value (0-1)
            feedback_text: Text for corrections
            context: Context about what led to feedback

        Returns:
            The recorded feedback entry
        """
        pass

    async def record_implicit_feedback(
        self,
        profile_id: str,
        session_id: str,
        agent_name: str,
        action_type: str,
        feedback_type: FeedbackType,
        metrics: Dict[str, Any],  # session_duration, message_count, etc.
    ) -> FeedbackEntry:
        """Record implicit feedback based on user behavior."""
        pass

    async def get_feedback_for_profile(
        self,
        profile_id: str,
        agent_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[FeedbackEntry]:
        """Get recent feedback for a profile."""
        pass

    async def get_aggregation(
        self,
        agent_name: str,
        action_type: str,
        profile_id: Optional[str] = None,
    ) -> FeedbackAggregation:
        """
        Get aggregated feedback for an agent/action.

        If profile_id is provided, returns profile-specific aggregation.
        Otherwise, returns global aggregation.
        """
        pass

    async def get_learning_insights(
        self,
        agent_name: str,
        min_feedback_count: int = 10,
    ) -> Dict[str, Any]:
        """
        Get learning insights for an agent.

        Returns:
            - Most successful actions
            - Areas needing improvement
            - Common correction patterns
        """
        pass

    async def update_aggregations(self) -> int:
        """Update cached aggregations. Returns count updated."""
        pass
```

### Database Schema

```sql
CREATE TABLE agent_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES profiles(id) NOT NULL,
    session_id UUID,
    agent_name TEXT NOT NULL,
    action_type TEXT NOT NULL,
    feedback_type TEXT NOT NULL CHECK (feedback_type IN (
        'explicit_positive', 'explicit_negative', 'explicit_correction',
        'implicit_engagement', 'implicit_abandonment', 'implicit_followup'
    )),
    feedback_value FLOAT CHECK (feedback_value >= 0 AND feedback_value <= 1),
    feedback_text TEXT,
    context JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_feedback_profile ON agent_feedback(profile_id);
CREATE INDEX idx_agent_feedback_agent ON agent_feedback(agent_name, action_type);
CREATE INDEX idx_agent_feedback_type ON agent_feedback(feedback_type);
CREATE INDEX idx_agent_feedback_created ON agent_feedback(created_at DESC);

-- Aggregation cache table
CREATE TABLE feedback_aggregations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL,
    action_type TEXT NOT NULL,
    profile_id UUID REFERENCES profiles(id),  -- NULL for global
    total_feedback INTEGER DEFAULT 0,
    positive_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,
    average_rating FLOAT DEFAULT 0.5,
    signal TEXT DEFAULT 'neutral',
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(agent_name, action_type, profile_id)
);
```

### Test File: `tests/phase3/test_feedback_learning.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.learning.feedback_v9 import (
    FeedbackLearner,
    FeedbackEntry,
    FeedbackType,
    FeedbackSignal,
    FeedbackAggregation,
)


class TestFeedbackLearner:
    """Tests for I1: Learning From Feedback."""

    @pytest.fixture
    def mock_supabase(self):
        db = MagicMock()
        db.table = MagicMock(return_value=MagicMock(
            insert=MagicMock(return_value=MagicMock(
                execute=MagicMock(return_value=MagicMock(data=[{"id": "test-id"}]))
            )),
            select=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    order=MagicMock(return_value=MagicMock(
                        limit=MagicMock(return_value=MagicMock(
                            execute=MagicMock(return_value=MagicMock(data=[]))
                        ))
                    ))
                ))
            ))
        ))
        return db

    @pytest.fixture
    def learner(self, mock_supabase):
        return FeedbackLearner(supabase_client=mock_supabase)

    @pytest.mark.asyncio
    async def test_record_explicit_positive_feedback(self, learner):
        """Test recording positive feedback."""
        entry = await learner.record_explicit_feedback(
            profile_id="test-profile",
            session_id="test-session",
            agent_name="ExecutionChatAgent",
            action_type="essay_feedback",
            feedback_type=FeedbackType.EXPLICIT_POSITIVE,
            feedback_value=1.0,
        )

        assert entry is not None
        assert entry.feedback_type == FeedbackType.EXPLICIT_POSITIVE

    @pytest.mark.asyncio
    async def test_record_correction_feedback(self, learner):
        """Test recording correction feedback."""
        entry = await learner.record_explicit_feedback(
            profile_id="test-profile",
            session_id="test-session",
            agent_name="NarrativeSynthesis",
            action_type="brand_statement",
            feedback_type=FeedbackType.EXPLICIT_CORRECTION,
            feedback_text="Actually, I'm focused on biology, not chemistry",
        )

        assert entry is not None
        assert entry.feedback_text is not None

    @pytest.mark.asyncio
    async def test_record_implicit_engagement(self, learner):
        """Test recording implicit engagement feedback."""
        entry = await learner.record_implicit_feedback(
            profile_id="test-profile",
            session_id="test-session",
            agent_name="ExecutionChatAgent",
            action_type="conversation",
            feedback_type=FeedbackType.IMPLICIT_ENGAGEMENT,
            metrics={"session_duration_ms": 300000, "message_count": 15},
        )

        assert entry is not None

    @pytest.mark.asyncio
    async def test_get_aggregation_returns_signal(self, learner):
        """Test getting aggregated feedback."""
        agg = await learner.get_aggregation(
            agent_name="ExecutionChatAgent",
            action_type="essay_feedback",
        )

        assert isinstance(agg, FeedbackAggregation)
        assert agg.signal in FeedbackSignal.__members__.values()

    @pytest.mark.asyncio
    async def test_get_learning_insights(self, learner):
        """Test getting learning insights."""
        insights = await learner.get_learning_insights(
            agent_name="ExecutionChatAgent",
        )

        assert isinstance(insights, dict)
```

---

## I2: Adaptive Behavior

### Purpose
Adapts agent behavior in real-time based on learned feedback patterns.

### 3P System Choice: **Redis + OpenAI**

**Why:**
- ✅ Redis for fast behavioral state access
- ✅ OpenAI for generating adapted prompts
- ✅ Already using both

### File: `middleware/learning/adaptive_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from enum import Enum
import logging

from .feedback_v9 import FeedbackLearner, FeedbackSignal

logger = logging.getLogger(__name__)


class AdaptationType(str, Enum):
    """Types of adaptations."""
    TONE = "tone"  # Adjust communication tone
    DETAIL_LEVEL = "detail_level"  # More/less detailed responses
    PACING = "pacing"  # Faster/slower progression
    EXAMPLE_STYLE = "example_style"  # Types of examples used
    ENCOURAGEMENT = "encouragement"  # Level of positive reinforcement


class AdaptationConfig(BaseModel):
    """Configuration for a behavior adaptation."""
    adaptation_type: AdaptationType
    current_value: str
    possible_values: List[str]
    confidence: float = 0.5


class BehaviorProfile(BaseModel):
    """Behavioral profile for a student."""
    profile_id: str
    adaptations: Dict[str, AdaptationConfig]
    last_updated: datetime
    feedback_basis: int  # Number of feedback entries used


class AdaptiveBehavior:
    """
    Adapts agent behavior based on feedback.

    Learns preferences like:
    - Communication tone (formal vs casual)
    - Detail level (concise vs comprehensive)
    - Pacing (quick vs thorough)
    - Example styles (academic vs real-world)
    """

    def __init__(
        self,
        feedback_learner: FeedbackLearner,
        redis_client=None,
        llm_client=None,
    ):
        """
        Initialize adaptive behavior.

        Args:
            feedback_learner: Feedback learner for historical data
            redis_client: Redis for caching behavior profiles
            llm_client: LLM for generating adaptations
        """
        self.feedback = feedback_learner
        self.redis = redis_client
        self.llm = llm_client

    async def get_behavior_profile(
        self,
        profile_id: str,
    ) -> BehaviorProfile:
        """
        Get current behavior profile for a student.

        First checks Redis cache, then computes from feedback if needed.
        """
        pass

    async def adapt_prompt(
        self,
        base_prompt: str,
        profile_id: str,
        agent_name: str,
    ) -> str:
        """
        Adapt a prompt based on learned preferences.

        Modifies tone, detail level, etc. based on behavior profile.

        Args:
            base_prompt: The original prompt
            profile_id: Student profile
            agent_name: Agent making the request

        Returns:
            Adapted prompt
        """
        pass

    async def adapt_response(
        self,
        response: str,
        profile_id: str,
        agent_name: str,
    ) -> str:
        """Adapt a response before sending to user."""
        pass

    async def update_adaptations(
        self,
        profile_id: str,
        force: bool = False,
    ) -> BehaviorProfile:
        """
        Update adaptations based on recent feedback.

        Args:
            profile_id: Profile to update
            force: Force update even if recently updated

        Returns:
            Updated behavior profile
        """
        pass

    async def reset_adaptations(
        self,
        profile_id: str,
    ) -> None:
        """Reset all adaptations to defaults."""
        pass

    def _compute_adaptations(
        self,
        feedback_entries: List[Any],
    ) -> Dict[str, AdaptationConfig]:
        """Compute adaptations from feedback entries."""
        pass
```

### Test File: `tests/phase3/test_adaptive_behavior.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.learning.adaptive_v9 import (
    AdaptiveBehavior,
    AdaptationType,
    AdaptationConfig,
    BehaviorProfile,
)
from middleware.learning.feedback_v9 import FeedbackLearner


class TestAdaptiveBehavior:
    """Tests for I2: Adaptive Behavior."""

    @pytest.fixture
    def mock_feedback_learner(self):
        learner = MagicMock(spec=FeedbackLearner)
        learner.get_feedback_for_profile = AsyncMock(return_value=[])
        return learner

    @pytest.fixture
    def adaptive(self, mock_feedback_learner):
        return AdaptiveBehavior(
            feedback_learner=mock_feedback_learner,
            redis_client=MagicMock(),
            llm_client=MagicMock(),
        )

    @pytest.mark.asyncio
    async def test_get_behavior_profile_returns_defaults(self, adaptive):
        """Test default behavior profile for new user."""
        profile = await adaptive.get_behavior_profile("new-profile")

        assert isinstance(profile, BehaviorProfile)
        assert len(profile.adaptations) > 0

    @pytest.mark.asyncio
    async def test_adapt_prompt_modifies_text(self, adaptive):
        """Test prompt adaptation."""
        adapted = await adaptive.adapt_prompt(
            base_prompt="Please help the student with their essay.",
            profile_id="test-profile",
            agent_name="ExecutionChatAgent",
        )

        assert isinstance(adapted, str)

    @pytest.mark.asyncio
    async def test_update_adaptations_uses_feedback(self, adaptive, mock_feedback_learner):
        """Test adaptations are updated from feedback."""
        mock_feedback_learner.get_feedback_for_profile.return_value = [
            MagicMock(feedback_type="explicit_positive"),
            MagicMock(feedback_type="explicit_positive"),
        ]

        profile = await adaptive.update_adaptations("test-profile")

        mock_feedback_learner.get_feedback_for_profile.assert_called()
        assert profile.feedback_basis >= 0

    @pytest.mark.asyncio
    async def test_reset_adaptations_clears_profile(self, adaptive):
        """Test resetting adaptations."""
        await adaptive.reset_adaptations("test-profile")
        # Should not raise
```

---

## I3: Personalization Engine

### Purpose
Deep personalization based on student's full history - memories, patterns, preferences, and goals.

### 3P System Choice: **Supabase + Redis + OpenAI**

**Why:**
- ✅ Supabase for long-term personalization data
- ✅ Redis for session-level personalization
- ✅ OpenAI for generating personalized content

### File: `middleware/learning/personalization_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class PersonalizationDimension(BaseModel):
    """A dimension of personalization."""
    name: str
    value: Any
    confidence: float
    source: str  # 'explicit', 'inferred', 'default'
    last_updated: datetime


class PersonalizationProfile(BaseModel):
    """Complete personalization profile for a student."""
    profile_id: str
    dimensions: Dict[str, PersonalizationDimension]
    themes: List[str]  # Key themes for this student
    communication_style: str
    interest_areas: List[str]
    strength_areas: List[str]
    growth_areas: List[str]
    created_at: datetime
    updated_at: datetime


class PersonalizationEngine:
    """
    Deep personalization based on full student history.

    Aggregates:
    - Long-term memories (B4)
    - Episodic memories (B2)
    - Feedback patterns (I1)
    - Assessment data
    - Conversation history

    Produces personalized prompts, responses, and recommendations.
    """

    def __init__(
        self,
        supabase_client=None,
        redis_client=None,
        llm_client=None,
        longterm_memory=None,  # B4
        episodic_memory=None,  # B2
    ):
        """
        Initialize personalization engine.

        Args:
            supabase_client: Supabase for persistence
            redis_client: Redis for caching
            llm_client: LLM for generating personalized content
            longterm_memory: Long-term memory manager (B4)
            episodic_memory: Episodic memory manager (B2)
        """
        self.db = supabase_client
        self.redis = redis_client
        self.llm = llm_client
        self.longterm = longterm_memory
        self.episodic = episodic_memory

    async def get_personalization_profile(
        self,
        profile_id: str,
        refresh: bool = False,
    ) -> PersonalizationProfile:
        """
        Get complete personalization profile.

        Args:
            profile_id: Student profile
            refresh: Force refresh from all sources

        Returns:
            Complete personalization profile
        """
        pass

    async def personalize_prompt(
        self,
        base_prompt: str,
        profile_id: str,
        context_type: str,
    ) -> str:
        """
        Personalize a prompt for a specific student.

        Injects student-specific context, themes, and style.
        """
        pass

    async def personalize_response(
        self,
        response: str,
        profile_id: str,
        context_type: str,
    ) -> str:
        """Personalize a response with student-specific references."""
        pass

    async def get_personalized_examples(
        self,
        profile_id: str,
        topic: str,
        count: int = 3,
    ) -> List[str]:
        """Get examples personalized to student's interests."""
        pass

    async def get_personalized_recommendations(
        self,
        profile_id: str,
        recommendation_type: str,
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get recommendations based on personalization profile."""
        pass

    async def update_profile(
        self,
        profile_id: str,
    ) -> PersonalizationProfile:
        """Update personalization profile from all sources."""
        pass

    async def _aggregate_from_memories(
        self,
        profile_id: str,
    ) -> Dict[str, Any]:
        """Aggregate insights from memory systems."""
        pass

    async def _aggregate_from_assessment(
        self,
        profile_id: str,
    ) -> Dict[str, Any]:
        """Aggregate insights from assessment data."""
        pass
```

### Test File: `tests/phase3/test_personalization.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.learning.personalization_v9 import (
    PersonalizationEngine,
    PersonalizationProfile,
    PersonalizationDimension,
)


class TestPersonalizationEngine:
    """Tests for I3: Personalization Engine."""

    @pytest.fixture
    def mock_dependencies(self):
        return {
            "supabase_client": MagicMock(),
            "redis_client": MagicMock(),
            "llm_client": MagicMock(),
            "longterm_memory": MagicMock(),
            "episodic_memory": MagicMock(),
        }

    @pytest.fixture
    def engine(self, mock_dependencies):
        return PersonalizationEngine(**mock_dependencies)

    @pytest.mark.asyncio
    async def test_get_personalization_profile(self, engine):
        """Test getting personalization profile."""
        profile = await engine.get_personalization_profile("test-profile")

        assert isinstance(profile, PersonalizationProfile)
        assert len(profile.dimensions) >= 0

    @pytest.mark.asyncio
    async def test_personalize_prompt_adds_context(self, engine):
        """Test prompt personalization."""
        personalized = await engine.personalize_prompt(
            base_prompt="Help with essay",
            profile_id="test-profile",
            context_type="essay_help",
        )

        assert isinstance(personalized, str)

    @pytest.mark.asyncio
    async def test_get_personalized_examples(self, engine):
        """Test getting personalized examples."""
        examples = await engine.get_personalized_examples(
            profile_id="test-profile",
            topic="leadership",
            count=3,
        )

        assert isinstance(examples, list)
        assert len(examples) <= 3

    @pytest.mark.asyncio
    async def test_get_personalized_recommendations(self, engine):
        """Test getting personalized recommendations."""
        recs = await engine.get_personalized_recommendations(
            profile_id="test-profile",
            recommendation_type="activities",
            count=5,
        )

        assert isinstance(recs, list)
```

---

## I5: Pattern Recognition

### Purpose
Identifies patterns across student interactions and uses them to improve agent behavior.

### 3P System Choice: **OpenAI + Supabase**

**Why:**
- ✅ OpenAI for pattern analysis via LLM
- ✅ Supabase for storing recognized patterns
- ✅ No new dependencies

### File: `middleware/learning/patterns_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PatternType(str, Enum):
    """Types of patterns."""
    BEHAVIORAL = "behavioral"  # User behavior patterns
    TEMPORAL = "temporal"  # Time-based patterns
    TOPIC = "topic"  # Topic interest patterns
    LEARNING = "learning"  # Learning style patterns
    ENGAGEMENT = "engagement"  # Engagement patterns


class RecognizedPattern(BaseModel):
    """A recognized pattern."""
    id: str
    pattern_type: PatternType
    description: str
    evidence: List[str]  # Evidence supporting this pattern
    confidence: float
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    profile_ids: List[str] = []  # Profiles exhibiting this pattern


class PatternInsight(BaseModel):
    """An insight derived from patterns."""
    pattern: RecognizedPattern
    recommendation: str
    impact_score: float


class PatternRecognizer:
    """
    Recognizes patterns across student interactions.

    Identifies:
    - Behavioral patterns (common requests, preferences)
    - Temporal patterns (active times, deadlines)
    - Topic patterns (interest evolution)
    - Learning patterns (what works, what doesn't)
    """

    def __init__(
        self,
        supabase_client=None,
        llm_client=None,
        longterm_memory=None,  # B4
    ):
        """
        Initialize pattern recognizer.

        Args:
            supabase_client: Supabase for pattern storage
            llm_client: LLM for pattern analysis
            longterm_memory: Long-term memory for historical data
        """
        self.db = supabase_client
        self.llm = llm_client
        self.longterm = longterm_memory

    async def analyze_profile(
        self,
        profile_id: str,
        lookback_days: int = 30,
    ) -> List[RecognizedPattern]:
        """
        Analyze patterns for a specific profile.

        Args:
            profile_id: Profile to analyze
            lookback_days: How far back to look

        Returns:
            List of recognized patterns
        """
        pass

    async def analyze_cross_profile(
        self,
        min_profiles: int = 10,
    ) -> List[RecognizedPattern]:
        """
        Analyze patterns across all profiles.

        Finds common patterns that appear across many students.
        Useful for improving general agent behavior.
        """
        pass

    async def get_patterns(
        self,
        profile_id: Optional[str] = None,
        pattern_type: Optional[PatternType] = None,
        min_confidence: float = 0.5,
    ) -> List[RecognizedPattern]:
        """Get stored patterns with filters."""
        pass

    async def get_insights(
        self,
        profile_id: str,
        limit: int = 5,
    ) -> List[PatternInsight]:
        """
        Get actionable insights from patterns.

        Returns recommendations based on recognized patterns.
        """
        pass

    async def record_pattern(
        self,
        pattern: RecognizedPattern,
    ) -> RecognizedPattern:
        """Record a newly recognized pattern."""
        pass

    async def update_pattern(
        self,
        pattern_id: str,
        new_evidence: List[str],
    ) -> RecognizedPattern:
        """Update an existing pattern with new evidence."""
        pass

    async def schedule_analysis(
        self,
        profile_id: str,
        run_at: datetime,
    ) -> str:
        """Schedule a pattern analysis for later."""
        pass
```

### Database Schema

```sql
CREATE TABLE recognized_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_type TEXT NOT NULL CHECK (pattern_type IN (
        'behavioral', 'temporal', 'topic', 'learning', 'engagement'
    )),
    description TEXT NOT NULL,
    evidence JSONB DEFAULT '[]',
    confidence FLOAT DEFAULT 0.5,
    occurrences INTEGER DEFAULT 1,
    profile_ids UUID[] DEFAULT '{}',
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_patterns_type ON recognized_patterns(pattern_type);
CREATE INDEX idx_patterns_confidence ON recognized_patterns(confidence DESC);
CREATE INDEX idx_patterns_profiles ON recognized_patterns USING GIN(profile_ids);
```

### Test File: `tests/phase3/test_pattern_recognition.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.learning.patterns_v9 import (
    PatternRecognizer,
    RecognizedPattern,
    PatternType,
    PatternInsight,
)


class TestPatternRecognizer:
    """Tests for I5: Pattern Recognition."""

    @pytest.fixture
    def mock_dependencies(self):
        return {
            "supabase_client": MagicMock(),
            "llm_client": MagicMock(),
            "longterm_memory": MagicMock(),
        }

    @pytest.fixture
    def recognizer(self, mock_dependencies):
        return PatternRecognizer(**mock_dependencies)

    @pytest.mark.asyncio
    async def test_analyze_profile_returns_patterns(self, recognizer):
        """Test profile analysis."""
        patterns = await recognizer.analyze_profile(
            profile_id="test-profile",
            lookback_days=30,
        )

        assert isinstance(patterns, list)

    @pytest.mark.asyncio
    async def test_analyze_cross_profile(self, recognizer):
        """Test cross-profile analysis."""
        patterns = await recognizer.analyze_cross_profile(
            min_profiles=5,
        )

        assert isinstance(patterns, list)

    @pytest.mark.asyncio
    async def test_get_patterns_filters_by_type(self, recognizer):
        """Test pattern retrieval with type filter."""
        patterns = await recognizer.get_patterns(
            pattern_type=PatternType.BEHAVIORAL,
        )

        assert isinstance(patterns, list)

    @pytest.mark.asyncio
    async def test_get_insights_returns_recommendations(self, recognizer):
        """Test getting pattern insights."""
        insights = await recognizer.get_insights(
            profile_id="test-profile",
            limit=5,
        )

        assert isinstance(insights, list)

    @pytest.mark.asyncio
    async def test_record_pattern_persists(self, recognizer):
        """Test recording a new pattern."""
        pattern = RecognizedPattern(
            id="test-pattern",
            pattern_type=PatternType.TOPIC,
            description="Student shows interest in STEM",
            evidence=["Mentioned robotics", "Asked about CS programs"],
            confidence=0.8,
            occurrences=5,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
        )

        result = await recognizer.record_pattern(pattern)

        assert result is not None
```

---

## Implementation Checklist

### I1: Learning From Feedback
- [ ] Create `middleware/learning/feedback_v9.py`
- [ ] Implement `FeedbackLearner` class
- [ ] Add database migrations
- [ ] Create tests in `tests/phase3/test_feedback_learning.py`
- [ ] Run tests and verify passing

### I2: Adaptive Behavior
- [ ] Create `middleware/learning/adaptive_v9.py`
- [ ] Implement `AdaptiveBehavior` class
- [ ] Create tests in `tests/phase3/test_adaptive_behavior.py`
- [ ] Run tests and verify passing

### I3: Personalization Engine
- [ ] Create `middleware/learning/personalization_v9.py`
- [ ] Implement `PersonalizationEngine` class
- [ ] Create tests in `tests/phase3/test_personalization.py`
- [ ] Run tests and verify passing

### I5: Pattern Recognition
- [ ] Create `middleware/learning/patterns_v9.py`
- [ ] Implement `PatternRecognizer` class
- [ ] Add database migration
- [ ] Create tests in `tests/phase3/test_pattern_recognition.py`
- [ ] Run tests and verify passing

### Integration
- [ ] Add all learning patterns to `stack_v9.py`
- [ ] Wire up feedback collection in agents
- [ ] Create integration tests

---

*Phase 3 Week 3 Specification*
*Generated: 2026-01-17*
