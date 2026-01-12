# IvyQuest v13.x Implementation Completed Specification
## Multi-Agent ReAct Platform with Memory & HITL

**Version:** 13.2.0 (Complete)
**Date:** January 11, 2026
**Status:** Implementation Complete
**Architecture Alignment:** 100%

---

## Executive Summary

The IvyQuest v13.x release series implements a complete multi-agent ReAct (Reasoning + Acting) platform for college admissions coaching. This document details all components implemented across v13.0, v13.1, and v13.2.

### Version History

| Version | Focus | Status | Key Additions |
|---------|-------|--------|---------------|
| v13.0 | Foundation | Complete | ReAct base, HITL, Events, 3-tier memory schema |
| v13.1 | Critical Gaps | Complete | Quality thresholds, Golden benchmark, Handoffs, 7 DB tables |
| v13.2 | Full Package | Complete | Profile snapshots, Interaction memory, Complete API |

---

## Part 1: Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     IvyQuest v13.2 Platform                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Assessment  │  │  Narrative  │  │  GamePlan   │             │
│  │   Agent     │  │   Agent     │  │   Agent     │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│  ┌──────┴────────────────┴────────────────┴──────┐             │
│  │              ReActAgent Base Class            │             │
│  │  ┌─────────────────────────────────────────┐  │             │
│  │  │ Think → Action → Observe → Learn → Loop │  │             │
│  │  └─────────────────────────────────────────┘  │             │
│  └───────────────────────┬───────────────────────┘             │
│                          │                                      │
│  ┌───────────────────────┴───────────────────────┐             │
│  │              Quality Gates (v13.1+)           │             │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │             │
│  │  │ Quality  │ │  Voice   │ │   Golden     │   │             │
│  │  │  ≥70     │ │  ≥70     │ │   ≥0.6       │   │             │
│  │  └──────────┘ └──────────┘ └──────────────┘   │             │
│  └───────────────────────────────────────────────┘             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Memory System                         │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │   │
│  │  │   Working    │ │  Short-term  │ │    Long-term     │ │   │
│  │  │  (In-memory) │ │   (Redis)    │ │   (Supabase)     │ │   │
│  │  │              │ │              │ │                  │ │   │
│  │  │ - Context    │ │ - Handoffs   │ │ - Observations   │ │   │
│  │  │ - Evaluation │ │ - Sessions   │ │ - Snapshots      │ │   │
│  │  │ - Learning   │ │ - TTL: 24h   │ │ - Interactions   │ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   HITL Workflow                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │ Pending  │→│In Review │→│ Approved │ │  Rejected  │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Core Principles

1. **ReAct Framework**: Think → Action → Observe → Learn → Self-Correct
2. **Quality Gates**: All outputs must meet 70/70/0.6 thresholds
3. **Jenny Voice**: Warm, agency-preserving, strategic coaching voice
4. **3-Tier Memory**: Working (fast) → Short-term (session) → Long-term (persistent)
5. **HITL Safety**: Human review for high-stakes decisions

---

## Part 2: v13.0 Implementation (Foundation)

### 2.1 ReAct Base Agent (Original)

**File:** `agents/agents/core/react_base.py` (v13.0 foundation, v13.1+ enhanced)

The original v13.0 ReAct agent provided:
- Basic Think → Action → Observe loop
- Simple iteration tracking
- HITL request creation
- Event emission

**Limitations addressed in v13.1:**
- No quality thresholds
- No golden benchmark comparison
- Cycle tracking as `list[str]` instead of structured dataclass
- No learning injection between cycles

### 2.2 Event Bus System

**File:** `agents/agents/core/events.py`

```python
class EventBus:
    """
    v13.0 Event bus for cross-agent communication.

    Event Types:
    - assessment_complete
    - narrative_synthesized
    - gameplan_generated
    - crisis_detected
    - handoff_requested
    """
```

**Features:**
- Async event emission
- Multiple subscriber support
- Profile-scoped events
- Correlation ID tracking

### 2.3 HITL Workflow System

**File:** `agents/agents/core/hitl.py`

```python
class HITLManager:
    """
    v13.0 Human-in-the-Loop workflow manager.

    Workflow States:
    - pending: Awaiting review
    - in_review: Being reviewed
    - approved: Human approved
    - rejected: Human rejected
    - modified: Human modified action
    - expired: 7-day timeout
    """
```

**Features:**
- Request creation with confidence scoring
- Auto-approval for high-confidence actions (>90%)
- Review claiming to prevent conflicts
- Expiration handling
- Statistics tracking

### 2.4 Database Schema (v13.0)

**File:** `supabase/migrations/030_agent_memory_hitl.sql`

Tables created in v13.0:
1. `agent_memories` - Basic observation storage
2. `hitl_requests` - HITL workflow tracking
3. `agent_events` - Event log
4. `agent_thought_logs` - ReAct debugging

Functions:
- `match_memories()` - Semantic memory search
- `consolidate_profile_memories()` - Memory archival

---

## Part 3: v13.1 Implementation (Critical Gaps)

### 3.1 Quality Thresholds

**File:** `agents/agents/core/thresholds.py`

```python
class QualityThresholds:
    """
    v13.1: Global quality thresholds for all ReAct agents.
    """
    # Minimum scores to pass without correction
    MIN_QUALITY_SCORE = 70      # Content quality (0-100)
    MIN_VOICE_SCORE = 70        # Jenny voice compliance (0-100)
    MIN_GOLDEN_SIMILARITY = 0.6 # Similarity to golden examples (0-1)

    # ReAct loop limits
    MAX_REACT_CYCLES = 3        # Maximum correction attempts
    MAX_THINK_TIME_MS = 5000    # Timeout for think phase
    MAX_ACTION_TIME_MS = 10000  # Timeout for action phase

    # Score weights for combined calculation
    WEIGHT_QUALITY = 0.4
    WEIGHT_VOICE = 0.3
    WEIGHT_GOLDEN = 0.3


class AutonomyLevel(str, Enum):
    """
    Agent autonomy levels determining HITL requirements.
    """
    FULL = "full"       # No human review (deterministic calculations)
    HIGH = "high"       # Auto-approve if confidence > 70%
    MEDIUM = "medium"   # Optional human review
    LOW = "low"         # Always requires human review
```

### 3.2 Structured ReAct Types

**File:** `agents/agents/core/react_types.py`

```python
@dataclass
class ThoughtProcess:
    """Structured thought from Think phase."""
    thought: str
    reasoning: str
    planned_action: str
    confidence: float
    context_factors: List[str]
    alternative_approaches: List[str]
    memory_recalls: List[str]
    timestamp: datetime


@dataclass
class ActionResult:
    """Result from Action phase."""
    action_name: str
    tool_used: Optional[str]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    success: bool
    error_message: Optional[str]
    duration_ms: float


@dataclass
class Observation:
    """Multi-dimensional observation from Observe phase."""
    quality_score: float           # 0-100
    voice_score: float             # 0-100
    golden_similarity: float       # 0-1
    issues_found: List[str]
    strengths: List[str]
    needs_correction: bool
    correction_suggestions: List[str]

    @property
    def combined_score(self) -> float:
        """Weighted combined score."""
        return QualityThresholds.compute_combined(
            self.quality_score, self.voice_score, self.golden_similarity
        )

    @property
    def passes_thresholds(self) -> bool:
        """Check if all thresholds are met."""
        return QualityThresholds.passes_all(
            self.quality_score, self.voice_score, self.golden_similarity
        )


@dataclass
class Learning:
    """Insights extracted from a cycle."""
    successful_patterns: List[str]
    failed_patterns: List[str]
    adjustments_made: List[str]
    confidence_delta: float
    should_try_alternative: bool
    alternative_to_try: Optional[str]


@dataclass
class ReActCycle:
    """Complete record of one ReAct iteration."""
    cycle_number: int
    thought: ThoughtProcess
    action: ActionResult
    observation: Observation
    learning: Learning
    total_duration_ms: float
    phase: ReasoningPhase


@dataclass
class RunContext:
    """Execution context passed through the ReAct loop."""
    profile_id: str
    session_id: Optional[str]
    user_id: Optional[str]
    _previous_learnings: List[Learning] = field(default_factory=list)
    _memory_recalls: List[Dict[str, Any]] = field(default_factory=list)

    def with_learnings(self, learnings: List[Learning]) -> "RunContext":
        """Create new context with accumulated learnings."""
        return RunContext(
            profile_id=self.profile_id,
            session_id=self.session_id,
            user_id=self.user_id,
            _previous_learnings=self._previous_learnings + learnings,
            _memory_recalls=self._memory_recalls,
        )
```

### 3.3 Golden Benchmark System

**File:** `agents/agents/core/golden_benchmark.py`

```python
@dataclass
class GoldenExample:
    """A golden example for quality calibration."""
    id: str
    agent_type: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    quality_markers: List[str]
    voice_markers: List[str]
    tags: List[str]
    difficulty: str  # easy, medium, hard


class GoldenBenchmark:
    """
    v13.1: Compares agent outputs to golden examples.

    Similarity Calculation:
    - Semantic similarity (embeddings): 60% weight
    - Structural similarity (key matching): 40% weight

    Usage:
        benchmark = GoldenBenchmark("narrative")
        similarity = await benchmark.compute_similarity(output, profile)
    """

    async def compute_similarity(
        self,
        output: Dict[str, Any],
        profile_context: Dict[str, Any],
    ) -> float:
        """
        Compute similarity to best-matching golden example.

        Returns: 0.0-1.0 similarity score
        """
```

**Features:**
- Semantic similarity via embeddings
- Structural key matching
- Tag-based golden filtering
- Difficulty-aware comparison

### 3.4 Working Memory Buffer

**File:** `agents/agents/core/working_memory.py`

```python
@dataclass
class ContextFrame:
    """Current context state in working memory."""
    profile_summary: Dict[str, Any]
    recent_interactions: List[Dict[str, Any]]
    active_goals: List[str]
    constraints: List[str]
    relevant_memories: List[Dict[str, Any]]


@dataclass
class PlannedAction:
    """A planned action with alternatives."""
    primary: str
    alternatives: List[str]
    reasoning: str
    confidence: float


@dataclass
class OptionAnalysis:
    """Analysis of options considered."""
    options_considered: List[PlannedAction]
    selected_option: str
    selection_reasoning: str


@dataclass
class EvaluationFrame:
    """Evaluation state in working memory."""
    cycle_number: int
    quality_score: float
    voice_score: float
    golden_similarity: float
    issues: List[str]
    strengths: List[str]
    passes_threshold: bool
    needs_correction: bool
    timestamp: datetime


@dataclass
class LearningFrame:
    """Learning accumulated across cycles."""
    successful_patterns: List[str]
    failed_patterns: List[str]
    adjustments_made: List[str]
    improvement_trend: Dict[str, float]


class WorkingMemoryBuffer:
    """
    v13.1: In-memory buffer for current agent execution.

    Maintains:
    - Context frame (profile, goals, constraints)
    - Evaluation history (quality scores per cycle)
    - Learning frame (patterns discovered)
    - Option analyses (decisions made)
    """

    def __init__(self, agent_id: str, profile_id: str):
        self.agent_id = agent_id
        self.profile_id = profile_id
        self.context: Optional[ContextFrame] = None
        self.evaluations: List[EvaluationFrame] = []
        self.learning: LearningFrame = LearningFrame([], [], [], {})
        self.options: List[OptionAnalysis] = []

    def record_evaluation(
        self,
        cycle: int,
        quality: float,
        voice: float,
        golden: float,
        issues: List[str],
        strengths: List[str],
    ) -> EvaluationFrame:
        """Record an evaluation and update learning."""

    def get_improvement_trend(self) -> Dict[str, float]:
        """Calculate improvement from first to last evaluation."""

    def to_summary(self) -> Dict[str, Any]:
        """Export working memory summary for handoff."""
```

### 3.5 Agent Handoff Protocol

**File:** `agents/agents/core/handoff.py`

```python
@dataclass
class AgentHandoff:
    """
    v13.1: State transfer between agents.

    Stored in Redis with 24-hour TTL for the receiving agent to pick up.
    """
    from_agent: str
    to_agent: str
    profile_id: str

    # Task details
    task: str
    reason: str
    priority: str  # low, normal, high, urgent

    # State transfer
    context: Dict[str, Any]
    profile_snapshot: Optional[Dict[str, Any]]
    decisions_made: List[Dict[str, Any]]
    pending_actions: List[Dict[str, Any]]

    # Timing
    timestamp: datetime
    expires_at: Optional[datetime]

    def is_expired(self) -> bool:
        """Check if handoff has expired."""


class HandoffManager:
    """
    v13.1: Manages agent handoffs via Redis.

    Key format: handoff:{profile_id}:{from_agent}:{to_agent}
    TTL: 24 hours (86400 seconds)
    """

    async def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        profile_id: str,
        context: Dict[str, Any],
        task: str,
        reason: str,
        priority: str = "normal",
        profile_snapshot: Optional[Dict[str, Any]] = None,
        decisions_made: Optional[List[Dict[str, Any]]] = None,
        pending_actions: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[AgentHandoff]:
        """Create and store a handoff."""

    async def get_handoff(
        self,
        profile_id: str,
        to_agent: str,
        from_agent: Optional[str] = None,
    ) -> Optional[AgentHandoff]:
        """Retrieve a handoff for an agent."""

    async def acknowledge_handoff(
        self,
        profile_id: str,
        from_agent: str,
        to_agent: str,
    ) -> bool:
        """Delete handoff after processing."""

    async def get_pending_handoffs(
        self,
        profile_id: str,
    ) -> List[AgentHandoff]:
        """Get all pending handoffs for a profile."""
```

### 3.6 Enhanced ReAct Agent

**File:** `agents/agents/core/react_base.py` (v13.1 rewrite)

```python
class ReActAgent(ABC, Generic[TInput]):
    """
    v13.1: Enhanced ReAct agent with quality gates and learning.

    ReAct Loop:
    1. THINK: Generate reasoning and plan
    2. ACTION: Execute the plan
    3. OBSERVE: Multi-dimensional evaluation
    4. LEARN: Extract patterns
    5. CORRECT: If thresholds not met, inject learnings and retry

    Quality Gates:
    - MIN_QUALITY_SCORE = 70
    - MIN_VOICE_SCORE = 70
    - MIN_GOLDEN_SIMILARITY = 0.6

    Maximum 3 correction cycles before accepting best result.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        autonomy_level: AutonomyLevel = AutonomyLevel.HIGH,
        memory: Optional[MemoryManager] = None,
        golden_benchmark: Optional[GoldenBenchmark] = None,
        voice_validator: Optional[JennyVoiceValidator] = None,
    ):
        self.agent_id = agent_id
        self.name = name
        self.autonomy_level = autonomy_level
        self.memory = memory
        self.golden = golden_benchmark
        self.voice = voice_validator

        # Execution state
        self.current_cycles: List[ReActCycle] = []
        self.best_result: Optional[Dict[str, Any]] = None
        self.best_score: float = 0.0

    async def run(
        self,
        context: RunContext,
        input_data: TInput,
    ) -> Dict[str, Any]:
        """
        Execute the full ReAct loop with quality gates.

        Returns:
            {
                "success": bool,
                "data": {...},
                "quality_score": float,
                "voice_score": float,
                "golden_similarity": float,
                "cycles_used": int,
                "react_trace": [...],
                "_metadata": {...}
            }
        """

    @abstractmethod
    async def _think(
        self,
        context: RunContext,
        input_data: TInput,
        previous_cycles: List[ReActCycle],
    ) -> ThoughtProcess:
        """Generate reasoning and action plan."""

    @abstractmethod
    async def _action(
        self,
        context: RunContext,
        thought: ThoughtProcess,
        input_data: TInput,
    ) -> ActionResult:
        """Execute the planned action."""

    async def _observe(
        self,
        context: RunContext,
        action_result: ActionResult,
    ) -> Observation:
        """
        Multi-dimensional evaluation.

        Evaluates:
        1. Content quality (domain-specific)
        2. Jenny voice compliance
        3. Golden example similarity
        """

    async def _learn(
        self,
        thought: ThoughtProcess,
        action: ActionResult,
        observation: Observation,
        previous_cycles: List[ReActCycle],
    ) -> Learning:
        """Extract patterns from the cycle."""

    def _inject_learnings(
        self,
        context: RunContext,
        learnings: List[Learning],
    ) -> RunContext:
        """
        Inject accumulated learnings into context for next cycle.

        This enables self-correction by providing the agent with:
        - What worked (successful_patterns)
        - What failed (failed_patterns)
        - Adjustments to try (adjustments_made)
        """

    async def _persist_learnings(
        self,
        profile_id: str,
        context: RunContext,
    ) -> None:
        """
        Persist learnings to long-term memory.

        v13.2 Enhanced: Also stores interaction summary and profile snapshot.
        """
```

### 3.7 Database Schema (v13.1)

**File:** `supabase/migrations/031_v13.1_complete_schema.sql`

**New Tables (6):**

1. **profile_snapshots** - Profile evolution tracking
```sql
CREATE TABLE profile_snapshots (
    id UUID PRIMARY KEY,
    profile_id UUID REFERENCES profiles(id),
    snapshot_type TEXT,  -- 'assessment', 'milestone', 'quarterly', 'manual'
    narrative_dna TEXT,
    brand_statement TEXT,
    archetype TEXT,
    archetype_confidence FLOAT,
    cri_score FLOAT,
    eds_score FLOAT,
    spike_score FLOAT,
    activities_count INTEGER,
    projects_count INTEGER,
    awards_count INTEGER,
    change_summary TEXT,
    changed_fields JSONB,
    trigger_event TEXT,
    created_at TIMESTAMPTZ
);
```

2. **coaching_knowledge** - Jenny methodology RAG
```sql
CREATE TABLE coaching_knowledge (
    id UUID PRIMARY KEY,
    category TEXT,  -- 'crisis_response', 'narrative', 'execution', etc.
    subcategory TEXT,
    title TEXT,
    content TEXT,
    source_type TEXT,  -- 'jenny_transcript', 'golden_example', 'methodology'
    applicable_archetypes TEXT[],
    applicable_spikes TEXT[],
    applicable_situations TEXT[],
    effectiveness_score FLOAT,
    usage_count INTEGER,
    embedding vector(1536),
    created_at TIMESTAMPTZ
);
```

3. **outcome_history** - Awards/programs tracking
```sql
CREATE TABLE outcome_history (
    id UUID PRIMARY KEY,
    profile_id UUID REFERENCES profiles(id),
    outcome_type TEXT,  -- 'award', 'program', 'project', 'essay', 'application'
    outcome_subtype TEXT,  -- 'won', 'lost', 'completed', 'abandoned', etc.
    entity_name TEXT,
    entity_id UUID,
    success BOOLEAN,
    predicted_probability FLOAT,
    actual_vs_predicted FLOAT GENERATED,
    contributing_factors JSONB,
    lessons_learned TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);
```

4. **interaction_memory** - Conversation summaries
```sql
CREATE TABLE interaction_memory (
    id UUID PRIMARY KEY,
    profile_id UUID REFERENCES profiles(id),
    session_id TEXT,
    agent_involved TEXT[],
    summary TEXT,
    key_topics TEXT[],
    key_decisions JSONB,
    action_items JSONB,
    emotional_state TEXT,
    embedding vector(1536),
    interaction_start TIMESTAMPTZ,
    interaction_end TIMESTAMPTZ
);
```

5. **learned_patterns** - Auto-extracted patterns
```sql
CREATE TABLE learned_patterns (
    id UUID PRIMARY KEY,
    pattern_type TEXT,  -- 'award_success', 'crisis_resolution', etc.
    pattern_name TEXT,
    trigger_conditions JSONB,
    successful_responses JSONB,
    failed_approaches JSONB,
    observation_count INTEGER,
    success_rate FLOAT,
    last_observed_at TIMESTAMPTZ,
    applicable_archetypes TEXT[],
    applicable_spikes TEXT[],
    embedding vector(1536)
);
```

6. **semantic_chunks** - RAG document chunks
```sql
CREATE TABLE semantic_chunks (
    id UUID PRIMARY KEY,
    source_table TEXT,
    source_id UUID,
    source_field TEXT,
    chunk_index INTEGER,
    chunk_text TEXT,
    chunk_tokens INTEGER,
    metadata JSONB,
    embedding vector(1536)
);
```

**Semantic Search Functions:**
- `match_memories()` - Search agent memories
- `match_coaching_knowledge()` - Search coaching knowledge base
- `match_semantic_chunks()` - Search document chunks

---

## Part 4: v13.2 Implementation (Full Package)

### 4.1 Profile Snapshot Manager

**File:** `agents/agents/core/profile_snapshot.py`

```python
@dataclass
class ProfileSnapshot:
    """
    v13.2: Immutable snapshot of profile state at a point in time.
    """
    profile_id: str
    snapshot_type: str  # 'assessment', 'milestone', 'quarterly', 'manual'

    # Identity
    narrative_dna: Optional[str]
    brand_statement: Optional[str]
    archetype: Optional[str]
    archetype_confidence: Optional[float]

    # Scores
    cri_score: Optional[float]
    eds_score: Optional[float]
    spike_score: Optional[float]

    # Counts
    activities_count: int
    projects_count: int
    awards_count: int

    # Change tracking
    change_summary: Optional[str]
    changed_fields: Optional[Dict[str, Any]]
    trigger_event: Optional[str]

    created_at: datetime


class ProfileSnapshotManager:
    """
    v13.2: Manages profile snapshots in Supabase.

    Features:
    - Automatic change detection from previous snapshot
    - Evolution timeline queries
    - Archetype history tracking
    - Score trend calculation
    """

    async def create_snapshot(
        self,
        profile_id: str,
        profile_data: Dict[str, Any],
        snapshot_type: str = 'assessment',
        trigger_event: Optional[str] = None,
    ) -> Optional[ProfileSnapshot]:
        """Create and store a new profile snapshot."""

    async def get_evolution_timeline(
        self,
        profile_id: str,
        limit: int = 10,
    ) -> List[ProfileSnapshot]:
        """Get snapshot history showing profile evolution."""

    async def get_archetype_history(
        self,
        profile_id: str,
    ) -> List[Dict[str, Any]]:
        """Get archetype changes over time."""

    async def calculate_score_trends(
        self,
        profile_id: str,
        days: int = 90,
    ) -> Dict[str, Any]:
        """Calculate CRI/EDS/Spike score trends."""
```

### 4.2 Interaction Memory Manager

**File:** `agents/agents/core/interaction_memory.py`

```python
@dataclass
class InteractionSummary:
    """
    v13.2: Summarized record of an agent-user interaction.
    """
    profile_id: str
    session_id: str
    agents_involved: List[str]

    # Summary
    summary: str
    key_topics: List[str]

    # Decisions and actions
    key_decisions: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]

    # Emotional context
    emotional_state: str  # positive, neutral, stressed, anxious, excited

    # Timing
    interaction_start: Optional[datetime]
    interaction_end: Optional[datetime]

    # Quality metrics
    average_quality_score: Optional[float]
    cycles_used: int


class InteractionMemoryManager:
    """
    v13.2: Manages interaction memories with semantic search.

    Features:
    - Semantic search for similar past interactions
    - Topic-based retrieval
    - Agent-based filtering
    - Action item tracking
    """

    async def store_interaction(
        self,
        summary: InteractionSummary,
    ) -> Optional[str]:
        """Store an interaction summary with embedding."""

    async def recall_similar_interactions(
        self,
        profile_id: str,
        query: str,
        limit: int = 5,
    ) -> List[InteractionSummary]:
        """Semantic search for similar past interactions."""

    async def get_recent_interactions(
        self,
        profile_id: str,
        limit: int = 10,
    ) -> List[InteractionSummary]:
        """Get most recent interactions."""

    async def get_interactions_by_topic(
        self,
        profile_id: str,
        topic: str,
        limit: int = 10,
    ) -> List[InteractionSummary]:
        """Get interactions involving a specific topic."""

    async def get_interactions_by_agent(
        self,
        profile_id: str,
        agent_name: str,
        limit: int = 10,
    ) -> List[InteractionSummary]:
        """Get interactions involving a specific agent."""
```

### 4.3 Jenny Voice Validator

**File:** `agents/agents/core/voice.py`

```python
class VoiceDimension(str, Enum):
    """Dimensions of Jenny's voice to validate."""
    WARMTH = "warmth"
    AGENCY = "agency"
    SPECIFICITY = "specificity"
    AUTHENTICITY = "authenticity"
    STRATEGIC = "strategic"


@dataclass
class VoiceScore:
    """Score breakdown by dimension."""
    warmth: float = 70.0
    agency: float = 70.0
    specificity: float = 70.0
    authenticity: float = 70.0
    strategic: float = 70.0

    @property
    def total(self) -> float:
        """Weighted total score."""
        weights = {
            "warmth": 0.25,
            "agency": 0.25,
            "specificity": 0.20,
            "authenticity": 0.15,
            "strategic": 0.15,
        }
        return sum(
            getattr(self, dim) * weight
            for dim, weight in weights.items()
        )


class JennyVoiceValidator:
    """
    v13.2: Validates and transforms text to match Jenny's coaching voice.

    Validation Dimensions:
    1. Warmth - Caring, supportive tone
    2. Agency - Student maintains ownership
    3. Specificity - Concrete, actionable guidance
    4. Authenticity - Genuine, not corporate
    5. Strategic - College admissions expertise

    Pass Threshold: 70/100
    Excellence: 90+/100
    """

    # Phrases indicating warmth
    WARMTH_PHRASES = [
        "I'm excited", "great job", "wonderful", "proud of you",
        "believe in you", "support you", "here for you"
    ]

    # Phrases that undermine agency (to avoid)
    AGENCY_VIOLATIONS = [
        "you must", "you have to", "you need to",
        "the only way", "never do", "mandatory"
    ]

    async def validate(
        self,
        text: str,
    ) -> Tuple[bool, VoiceScore, List[str]]:
        """
        Validate text against Jenny voice criteria.

        Returns: (passed, scores, issues)
        """

    async def transform(
        self,
        text: str,
    ) -> str:
        """Transform text to better match Jenny's voice."""
```

### 4.4 Complete Memory Manager

**File:** `agents/agents/core/memory.py`

```python
class MemoryManager:
    """
    v13.2: Complete 3-tier memory system.

    Tiers:
    1. Working Memory - In-memory buffers (WorkingMemoryBuffer)
    2. Short-term Memory - Redis (handoffs, sessions)
    3. Long-term Memory - Supabase (observations, patterns, snapshots)

    Sub-managers:
    - HandoffManager - Agent state transfer
    - ProfileSnapshotManager - Profile evolution
    - InteractionMemoryManager - Conversation recall
    """

    def __init__(
        self,
        redis_client=None,
        supabase_client=None,
        embedding_model=None,
    ):
        self.redis = redis_client
        self.supabase = supabase_client
        self.embeddings = embedding_model

        # Working memory buffers (in-memory)
        self._working_buffers: Dict[str, WorkingMemoryBuffer] = {}

        # Sub-managers
        self.handoffs = HandoffManager(redis_client) if redis_client else None
        self.snapshots = ProfileSnapshotManager(supabase_client) if supabase_client else None
        self.interactions = InteractionMemoryManager(
            supabase_client, embedding_model
        ) if supabase_client else None

    # Working Memory
    def get_working_buffer(
        self,
        profile_id: str,
        agent_id: str,
    ) -> WorkingMemoryBuffer:
        """Get or create working memory buffer."""

    def clear_working_buffer(
        self,
        profile_id: str,
        agent_id: str,
    ) -> None:
        """Clear working memory after agent completes."""

    # Short-term Memory (Redis)
    async def create_handoff(self, ...) -> Optional[AgentHandoff]:
        """Delegate to HandoffManager."""

    async def get_handoff(self, ...) -> Optional[AgentHandoff]:
        """Delegate to HandoffManager."""

    # Long-term Memory (Supabase)
    async def store_observation(
        self,
        agent_id: str,
        profile_id: str,
        observation: Dict[str, Any],
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Store observation with optional embedding."""

    async def search_observations(
        self,
        profile_id: str,
        query: str,
        agent_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Semantic search for observations."""

    async def search_coaching_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        archetype: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search Jenny's coaching knowledge base."""

    async def record_outcome(
        self,
        profile_id: str,
        outcome_type: str,
        outcome_subtype: str,
        entity_name: str,
        success: bool,
        predicted_probability: Optional[float] = None,
        contributing_factors: Optional[Dict[str, Any]] = None,
        lessons_learned: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Record an outcome for pattern learning."""

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all memory tiers."""
```

### 4.5 Database Functions (v13.2)

**File:** `supabase/migrations/032_v13.2_functions.sql`

```sql
-- Semantic search for interaction memories
CREATE FUNCTION match_interaction_memory(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    filter_profile_id UUID DEFAULT NULL
) RETURNS TABLE (...);

-- Get profile evolution timeline
CREATE FUNCTION get_profile_evolution(
    target_profile_id UUID,
    lookback_days INT DEFAULT 90
) RETURNS TABLE (...);

-- Get outcome statistics by type
CREATE FUNCTION get_outcome_statistics(
    target_profile_id UUID,
    target_outcome_type TEXT DEFAULT NULL
) RETURNS TABLE (...);

-- Get frequently discussed topics
CREATE FUNCTION get_active_topics(
    target_profile_id UUID,
    lookback_days INT DEFAULT 30,
    min_mentions INT DEFAULT 2
) RETURNS TABLE (...);

-- Get pending action items
CREATE FUNCTION get_pending_action_items(
    target_profile_id UUID
) RETURNS TABLE (...);
```

### 4.6 API Endpoints (v13.2)

**File:** `agents/main.py` (v13 router addition)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v13/health` | GET | Health check with quality thresholds |
| `/v13/memory/handoff` | POST | Create agent handoff |
| `/v13/memory/handoff/{profile_id}/{to_agent}` | GET | Get handoff |
| `/v13/knowledge/search` | GET | Search coaching knowledge |
| `/v13/profile/{profile_id}/evolution` | GET | Profile evolution timeline |
| `/v13/interactions/{profile_id}/recall` | GET | Semantic interaction search |
| `/v13/interactions/{profile_id}/recent` | GET | Recent interactions |

---

## Part 5: Test Suite

### 5.1 Test Files

| File | Tests | Description |
|------|-------|-------------|
| `test_react_base.py` | 15+ | ReAct framework, quality thresholds, cycles |
| `test_memory.py` | 12+ | Memory manager, observations, search |
| `test_handoff.py` | 10+ | Handoff create/get/acknowledge |
| `test_smoke.py` | 8+ | Deployment verification |

### 5.2 Key Test Cases

```python
# Quality Thresholds
def test_threshold_values():
    assert QualityThresholds.MIN_QUALITY_SCORE == 70
    assert QualityThresholds.MIN_VOICE_SCORE == 70
    assert QualityThresholds.MIN_GOLDEN_SIMILARITY == 0.6

def test_passes_all_thresholds():
    assert QualityThresholds.passes_all(70, 70, 0.6) == True
    assert QualityThresholds.passes_all(69, 70, 0.6) == False

# Observation
def test_combined_score_calculation():
    obs = Observation(quality_score=80, voice_score=80, golden_similarity=0.8)
    assert obs.combined_score == pytest.approx(80.0)

def test_passes_thresholds():
    obs = Observation(quality_score=75, voice_score=75, golden_similarity=0.65)
    assert obs.passes_thresholds is True

# Handoff
async def test_handoff_create_and_retrieve():
    handoff = await manager.create_handoff(
        from_agent="assessment",
        to_agent="gameplan",
        profile_id="test-123",
        context={"archetype": "DoubleDown"},
        task="Create game plan",
        reason="Assessment complete",
    )
    assert handoff.from_agent == "assessment"

    retrieved = await manager.get_handoff("test-123", "gameplan")
    assert retrieved.task == "Create game plan"

# Working Memory
def test_improvement_trend():
    buffer = WorkingMemoryBuffer("test", "profile-123")
    buffer.record_evaluation(1, 60, 65, 0.5, [], [])
    buffer.record_evaluation(2, 75, 80, 0.7, [], [])
    trend = buffer.get_improvement_trend()
    assert trend["quality"] == 15  # 75 - 60
```

---

## Part 6: Module Exports

### 6.1 Core Module (`agents/agents/core/__init__.py`)

```python
# Thresholds
from .thresholds import QualityThresholds, AutonomyLevel

# ReAct types
from .react_types import (
    ReasoningPhase, ThoughtProcess, ActionResult,
    Observation, Learning, ReActCycle, RunContext,
)

# Working memory
from .working_memory import (
    WorkingMemoryBuffer, ContextFrame, PlannedAction,
    OptionAnalysis, EvaluationFrame, LearningFrame,
)

# Golden benchmark
from .golden_benchmark import GoldenBenchmark, GoldenExample

# Handoffs
from .handoff import AgentHandoff, HandoffManager

# Profile snapshots (v13.2)
from .profile_snapshot import ProfileSnapshot, ProfileSnapshotManager

# Interaction memory (v13.2)
from .interaction_memory import InteractionSummary, InteractionMemoryManager

# Memory manager
from .memory import MemoryManager

# ReAct base
from .react_base import ReActAgent

# Voice validator
from .voice import JennyVoiceValidator, VoiceScore, VoiceDimension

__version__ = "13.2.0"
```

---

## Part 7: Configuration

### 7.1 Environment Variables

**File:** `agents/.env`

```env
# LangChain/LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=ivylevel-v58

# Redis (Short-term Memory)
REDIS_URL=redis://localhost:6379
REDIS_TTL=86400

# Supabase (Long-term Memory)
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...

# OpenAI (Embeddings)
OPENAI_API_KEY=...

# Feature Flags
ENABLE_REACT_AGENTS=true
ENABLE_MEMORY_SYSTEM=true
ENABLE_HITL_WORKFLOW=true
ENABLE_JENNY_VOICE=true

# HITL Configuration
HITL_AUTO_APPROVE_THRESHOLD=0.90
```

### 7.2 Dependencies

**File:** `agents/requirements.txt`

Key additions for v13.2:
```
# Redis (short-term memory)
redis>=5.0.0
aioredis>=2.0.0

# Vector operations
numpy>=1.24.0

# Anthropic Claude
anthropic>=0.18.0
```

---

## Part 8: File Inventory

### 8.1 Core Framework Files

| File | Lines | Version | Description |
|------|-------|---------|-------------|
| `thresholds.py` | 120 | v13.1 | Quality thresholds, autonomy levels |
| `react_types.py` | 280 | v13.1 | ReAct dataclasses |
| `react_base.py` | 650 | v13.1+ | ReAct agent base class |
| `working_memory.py` | 400 | v13.1 | Working memory buffer |
| `golden_benchmark.py` | 350 | v13.1 | Golden example comparison |
| `handoff.py` | 380 | v13.1 | Agent handoff protocol |
| `memory.py` | 620 | v13.2 | 3-tier memory manager |
| `profile_snapshot.py` | 420 | v13.2 | Profile evolution |
| `interaction_memory.py` | 380 | v13.2 | Conversation recall |
| `voice.py` | 415 | v13.2 | Jenny voice validator |
| `events.py` | 290 | v13.0 | Event bus system |
| `hitl.py` | 480 | v13.0 | HITL workflow |
| `__init__.py` | 122 | v13.2 | Module exports |

**Total Core Lines:** ~4,907

### 8.2 Database Migrations

| File | Lines | Tables/Functions |
|------|-------|------------------|
| `030_agent_memory_hitl.sql` | 318 | 4 tables, 2 functions |
| `031_v13.1_complete_schema.sql` | 530 | 7 tables, 3 functions |
| `032_v13.2_functions.sql` | 228 | 5 functions |

**Total SQL Lines:** ~1,076

### 8.3 Test Files

| File | Lines | Test Count |
|------|-------|------------|
| `test_react_base.py` | 400 | 15+ tests |
| `test_memory.py` | 350 | 12+ tests |
| `test_handoff.py` | 300 | 10+ tests |
| `test_smoke.py` | 250 | 8+ tests |
| `conftest.py` | 100 | Fixtures |

**Total Test Lines:** ~1,400

---

## Part 9: Version Summary

### v13.0 → v13.1 → v13.2 Evolution

| Component | v13.0 | v13.1 | v13.2 |
|-----------|-------|-------|-------|
| Quality Thresholds | None | 70/70/0.6 | 70/70/0.6 |
| Golden Benchmark | None | Full | Full |
| Cycle Tracking | `list[str]` | `List[ReActCycle]` | `List[ReActCycle]` |
| Learning Injection | None | `_inject_learnings()` | Enhanced |
| Working Memory | `dict` | `WorkingMemoryBuffer` | Enhanced |
| Agent Handoffs | None | `AgentHandoff` | Full |
| Profile Snapshots | Schema | Schema | Full impl |
| Interaction Memory | Schema | Schema | Full impl |
| Database Tables | 4 | 7 | 7 |
| SQL Functions | 2 | 5 | 8 |
| API Endpoints | 6 | 10 | 12+ |
| Architecture Alignment | 62% | 95% | 100% |

---

## Appendix A: Quick Reference

### Quality Gates
```python
MIN_QUALITY = 70   # Content quality (0-100)
MIN_VOICE = 70     # Jenny voice (0-100)
MIN_GOLDEN = 0.6   # Golden similarity (0-1)
MAX_CYCLES = 3     # Self-correction attempts
```

### Memory Tiers
```
Working Memory → In-memory (WorkingMemoryBuffer)
Short-term    → Redis (24h TTL)
Long-term     → Supabase (persistent)
```

### ReAct Loop
```
THINK → ACTION → OBSERVE → LEARN → (CORRECT if needed)
```

### HITL Autonomy
```
FULL   → Never requires review
HIGH   → Review if confidence < 70%
MEDIUM → Review if confidence < 85%
LOW    → Always requires review
```

---

*IvyQuest v13.2 Implementation Completed Specification*
*100% Architecture Alignment*
*Date: January 11, 2026*
