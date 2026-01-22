# IvyQuest PRD v15.0 - Complete Multi-Agent Platform
## Full-Stack Integration with Enhanced UI/UX & Production-Ready Backend

**Version:** 15.0.0
**Date:** January 12, 2026
**Status:** Production Ready
**Previous Version:** v13.3 (Frontend Integration)
**This Version:** v15.0 (Complete Platform with Production Fixes)

---

## Executive Summary

v15.0 represents the complete, production-ready IvyQuest multi-agent platform. This release consolidates all v13.x improvements and adds critical production fixes, enhanced UI/UX, and robust error handling.

### Version Lineage

| Version | Focus | Key Additions |
|---------|-------|---------------|
| v13.0 | Foundation | ReAct base, HITL, Events, 3-tier memory |
| v13.1 | Quality Gates | Thresholds (70/70/0.6), Golden benchmark, Handoffs |
| v13.2 | Memory System | Profile snapshots, Interaction memory, Complete API |
| v13.3 | Frontend Integration | 6-agent dashboard, Crisis Alchemy UI, Notifications |
| **v15.0** | **Production Ready** | **LLM reliability, Enhanced modals, Error handling, UI polish** |

### Key v15.0 Enhancements

1. **LLM Provider Reliability**
   - Google Gemini as primary provider (more stable)
   - OpenAI as fallback
   - Proper environment variable loading

2. **Enhanced Agent Detail Modals**
   - All 6 agent cards are clickable
   - Rich detail views for each agent type
   - Awards portfolio with tier breakdown

3. **Production-Ready Error Handling**
   - Extended API timeouts for LLM operations
   - Graceful abort error handling
   - React Query optimization

4. **Narrative Quality Improvements**
   - Fixed placeholder name hallucination
   - Anonymous student references
   - Improved prompt engineering

---

## PART 1: ARCHITECTURE OVERVIEW

### 1.1 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       IvyQuest v15.0 Platform                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FRONTEND (Next.js 14 + React Query + Zustand)                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Multi-Agent Dashboard                        │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │Assessment│ │ GamePlan │ │Execution │ │  Awards  │           │   │
│  │  │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │           │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │   │
│  │       │            │            │            │                  │   │
│  │  ┌────┴────────────┴────────────┴────────────┴────┐            │   │
│  │  │           AgentDetailModal (v15.0)             │            │   │
│  │  │  ┌─────────────────────────────────────────┐   │            │   │
│  │  │  │ Rich views for each agent type:         │   │            │   │
│  │  │  │ - Assessment: Narrative DNA, Themes     │   │            │   │
│  │  │  │ - GamePlan: Phases, Seeds, Actions      │   │            │   │
│  │  │  │ - Execution: EDS Score, Blockers        │   │            │   │
│  │  │  │ - Awards: Portfolio tiers, Strategy     │   │            │   │
│  │  │  │ - Opportunity: Deadlines, Matches       │   │            │   │
│  │  │  │ - Crisis: VARC Framework                │   │            │   │
│  │  │  └─────────────────────────────────────────┘   │            │   │
│  │  └────────────────────────────────────────────────┘            │   │
│  │                                                                 │   │
│  │  ┌──────────┐ ┌──────────┐                                     │   │
│  │  │Opportun- │ │  Crisis  │   NotificationBell                  │   │
│  │  │  ity     │ │ Response │   CrisisAlchemyModal                │   │
│  │  └──────────┘ └──────────┘                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              │ HTTP/REST                                │
│                              ▼                                          │
│  BACKEND (FastAPI + Python Agents)                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Agent Service (Port 8001)                    │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │               LLM Provider (v15.0 Enhancement)            │   │   │
│  │  │  ┌────────────────┐    ┌────────────────┐                │   │   │
│  │  │  │ Google Gemini  │───▶│    OpenAI      │                │   │   │
│  │  │  │   (Primary)    │    │   (Fallback)   │                │   │   │
│  │  │  └────────────────┘    └────────────────┘                │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │              ReAct Framework (v13.2 Base)                 │   │   │
│  │  │  THINK → ACTION → OBSERVE → LEARN → CORRECT               │   │   │
│  │  │  Quality Gates: 70/70/0.6 | Max Cycles: 3                │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │              Memory System (3-Tier)                       │   │   │
│  │  │  Working (In-memory) → Short-term (Redis) → Long (Supa)  │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

```
Frontend Stack:
├── Framework: Next.js 14.2+ (App Router)
├── State Management: Zustand + React Query v5
├── Styling: Tailwind CSS + BRAND_COLORS constants
├── HTTP Client: Custom agentClient.ts with timeout handling
├── Types: TypeScript with lib/types/agents.ts
└── UI Components: Lucide React icons

Backend Stack:
├── Framework: FastAPI (Python 3.10+)
├── LLM Providers:
│   ├── Primary: Google Gemini (gemini-2.0-flash-exp)
│   └── Fallback: OpenAI (gpt-4-turbo)
├── Memory:
│   ├── Working: In-memory buffers
│   ├── Short-term: Redis (24h TTL)
│   └── Long-term: Supabase (PostgreSQL + pgvector)
├── Agent Framework: LangChain + Custom ReAct
└── Environment: python-dotenv with cascading .env files

Database:
├── Supabase PostgreSQL
├── pgvector for semantic search
├── 7 agent-specific tables
└── 8 semantic search functions
```

---

## PART 2: v15.0 ENHANCEMENTS

### 2.1 LLM Provider Reliability (Critical Fix)

**Problem Solved:** OpenAI API instability causing agent failures

**Solution:** Dual-provider architecture with Google Gemini as primary

**File:** `agents/agents/narrative_synthesis.py`

```python
# v15.0: LLM Provider Selection
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_API_KEY = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    USE_GEMINI = bool(GOOGLE_API_KEY)
except ImportError:
    USE_GEMINI = False
    GOOGLE_API_KEY = None

from langchain_openai import ChatOpenAI

class NarrativeSynthesisAgent:
    def __init__(self):
        # Prefer Google Gemini for reliability
        if USE_GEMINI:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=GOOGLE_API_KEY,
                temperature=0.7
            )
            print(f"[NarrativeSynthesis] Using Google Gemini")
        else:
            self.llm = ChatOpenAI(model=settings.agent_primary_model, temperature=0.7)
            print(f"[NarrativeSynthesis] Using OpenAI")
```

**File:** `agents/main.py` (Environment Loading - Critical)

```python
# v15.0: Load environment variables FIRST (before any other imports)
import os
from dotenv import load_dotenv

# Load from parent .env.local first, then local .env to override
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'), override=False)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

# Now import everything else
from fastapi import FastAPI
# ... rest of imports
```

**Required Environment Variables:**

```env
# agents/.env
OPENAI_API_KEY=sk-proj-xxx
GOOGLE_GENERATIVE_AI_API_KEY=AIzaSyXxx
```

### 2.2 Extended API Timeouts (Production Fix)

**Problem Solved:** Game Plan agent timing out during LLM generation

**File:** `lib/api/agentClient.ts`

```typescript
// v15.0: Dual timeout configuration
const API_TIMEOUT = 60000;        // Standard operations (60s)
const API_TIMEOUT_LONG = 120000;  // LLM-heavy operations (120s)

interface ApiCallOptions extends RequestInit {
  timeout?: number;
}

async function apiCall<T>(endpoint: string, options: ApiCallOptions = {}): Promise<ApiResponse<T>> {
  const { timeout = API_TIMEOUT, ...fetchOptions } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${AGENT_API_URL}${endpoint}`, {
      ...fetchOptions,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...fetchOptions.headers,
      },
    });
    // ... handle response
  } finally {
    clearTimeout(timeoutId);
  }
}

// v15.0: Extended timeout for game plan generation
export async function generateGamePlan(profileId: string, assessmentData?: Record<string, unknown>) {
  return apiCall('/agents/gameplan/generate', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId, data: assessmentData }),
    timeout: API_TIMEOUT_LONG,  // 120s for LLM generation
  });
}
```

### 2.3 React Query Optimization (Production Fix)

**Problem Solved:** "Signal is aborted without reason" errors on React Strict Mode re-renders

**File:** `hooks/useAgentData.ts`

```typescript
// v15.0: Optimized Game Plan hook
export function useGamePlan(profileId: string | null) {
  return useQuery({
    queryKey: ['gameplan', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      try {
        const result = await agentApi.generateGamePlan(profileId);
        if (!result.success) {
          console.error('[useGamePlan] API error:', result.error);
          throw new Error(result.error || 'Failed to generate game plan');
        }
        // ... transform data
        return gamePlanData;
      } catch (error) {
        // v15.0: Gracefully handle abort errors (React Strict Mode)
        if (error instanceof Error && error.message.includes('abort')) {
          console.log('[useGamePlan] Request aborted (likely React Strict Mode)');
          return null;
        }
        throw error;
      }
    },
    enabled: !!profileId,
    staleTime: 10 * 60 * 1000,      // Cache for 10 minutes
    gcTime: 30 * 60 * 1000,         // Keep in garbage collection for 30 min
    retry: false,                    // Don't retry on failure
    refetchOnWindowFocus: false,     // Don't refetch when window regains focus
    refetchOnMount: 'always',        // Always refetch on mount
  });
}
```

### 2.4 Clickable Agent Cards with Detail Modals

**Problem Solved:** Agent cards showed summary only; users needed detailed views

**File:** `components/agents/cards/AgentCardBase.tsx`

```typescript
interface AgentCardBaseProps {
  title: string;
  icon: ReactNode;
  isLoading: boolean;
  isError: boolean;
  onRefresh: () => void;
  onChat?: () => void;
  onClick?: () => void;  // v15.0: Clickable cards
  children: ReactNode;
  actions?: ReactNode;
  headerBadge?: ReactNode;
}

export function AgentCardBase({
  title,
  icon,
  isLoading,
  isError,
  onRefresh,
  onChat,
  onClick,  // v15.0
  children,
  actions,
  headerBadge,
}: AgentCardBaseProps) {
  const isClickable = !!onClick && !isLoading && !isError;

  return (
    <div
      className={`rounded-xl p-5 shadow-sm h-full flex flex-col transition-all ${
        isClickable ? 'cursor-pointer hover:shadow-md hover:scale-[1.01]' : ''
      }`}
      style={{
        backgroundColor: '#ffffff',
        border: `1px solid ${BRAND_COLORS.borderLight}`,
      }}
      onClick={isClickable ? onClick : undefined}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
    >
      {/* Header with "Click for details" hint */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {/* ... icon and title ... */}
        </div>
        {isClickable && (
          <span className="ml-auto text-xs" style={{ color: BRAND_COLORS.textMuted }}>
            Click for details
          </span>
        )}
      </div>
      {/* ... rest of card ... */}
    </div>
  );
}
```

### 2.5 Agent Detail Modal (New Component)

**File:** `components/agents/AgentDetailModal.tsx`

```typescript
export type AgentType = 'assessment' | 'gameplan' | 'execution' | 'awards' | 'opportunity' | 'crisis';

interface AgentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  agentType: AgentType;
  title: string;
  data: Record<string, unknown> | null;
}

export function AgentDetailModal({
  isOpen,
  onClose,
  agentType,
  title,
  data,
}: AgentDetailModalProps) {
  // Escape key to close
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  const renderContent = () => {
    switch (agentType) {
      case 'assessment':
        return <AssessmentDetail data={data} />;
      case 'gameplan':
        return <GamePlanDetail data={data} />;
      case 'execution':
        return <ExecutionDetail data={data} />;
      case 'awards':
        return <AwardsDetail data={data} />;
      case 'opportunity':
        return <OpportunityDetail data={data} />;
      case 'crisis':
        return <CrisisDetail data={data} />;
      default:
        return <pre>{JSON.stringify(data, null, 2)}</pre>;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-xl font-bold">{title}</h2>
          <button onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}
```

### 2.6 Enhanced Awards Detail View

**v15.0 Enhancement:** Full portfolio breakdown with tier-specific views

```typescript
function AwardsDetail({ data }: { data: Record<string, unknown> }) {
  const portfolio = (data.portfolio as Record<string, unknown>) || {};

  // Get awards from portfolio tiers
  const likelyAwards = (portfolio.likely as Record<string, unknown>[]) || [];
  const targetAwards = (portfolio.target as Record<string, unknown>[]) || [];
  const stretchAwards = (portfolio.stretch as Record<string, unknown>[]) || [];
  const expectedWins = (portfolio.expected_wins as number) || 0;
  const strategyNotes = (portfolio.strategy_notes as string[]) || [];

  const renderAwardItem = (award: Record<string, unknown>, tierColor: string, tierBg: string) => {
    const fitReasons = (award.fit_reasons as string[]) || [];
    return (
      <div key={award.name as string} className="p-3 rounded-lg border">
        <div className="flex items-center justify-between mb-1">
          <h4 className="font-medium text-sm">{award.name as string}</h4>
          {award.win_probability !== undefined && (
            <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: tierColor, color: '#fff' }}>
              {Math.round((award.win_probability as number) * 100)}% prob
            </span>
          )}
        </div>
        {/* Category and Level */}
        {(award.category || award.level) && (
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs px-2 py-0.5 rounded">{award.category as string}</span>
            <span className="text-xs">{award.level as string}</span>
          </div>
        )}
        {/* Fit Reasons */}
        {fitReasons.length > 0 && (
          <p className="text-xs">{fitReasons.slice(0, 2).join(' • ')}</p>
        )}
        {/* Metadata */}
        <div className="flex items-center gap-3 mt-2 text-xs">
          {award.deadline && <span>📅 {award.deadline as string}</span>}
          {award.effort_hours && <span>{award.effort_hours}h effort</span>}
          {award.roi !== undefined && <span>ROI: {(award.roi as number).toFixed(1)}</span>}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Portfolio Summary */}
      <Section title="Awards Portfolio" icon={<Award size={20} />}>
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center p-4 rounded-lg" style={{ backgroundColor: BRAND_COLORS.bgSuccess }}>
            <p className="text-3xl font-bold">{likelyAwards.length}</p>
            <p className="text-sm">Likely</p>
          </div>
          <div className="text-center p-4 rounded-lg" style={{ backgroundColor: BRAND_COLORS.bgWarning }}>
            <p className="text-3xl font-bold">{targetAwards.length}</p>
            <p className="text-sm">Target</p>
          </div>
          <div className="text-center p-4 rounded-lg" style={{ backgroundColor: BRAND_COLORS.primaryBg }}>
            <p className="text-3xl font-bold">{stretchAwards.length}</p>
            <p className="text-sm">Stretch</p>
          </div>
        </div>
        {expectedWins > 0 && (
          <div className="text-center p-3 rounded-lg">
            <span>Expected Wins: </span>
            <span className="font-bold">{expectedWins.toFixed(1)}</span>
          </div>
        )}
      </Section>

      {/* Likely Awards */}
      {likelyAwards.length > 0 && (
        <Section title="Likely Awards (High Win Probability)" icon={<CheckCircle2 />}>
          <div className="space-y-2">
            {likelyAwards.map((award) => renderAwardItem(award, BRAND_COLORS.success, BRAND_COLORS.bgSuccess))}
          </div>
        </Section>
      )}

      {/* Target Awards */}
      {targetAwards.length > 0 && (
        <Section title="Target Awards (Competitive)" icon={<Target />}>
          <div className="space-y-2">
            {targetAwards.map((award) => renderAwardItem(award, BRAND_COLORS.warning, BRAND_COLORS.bgWarning))}
          </div>
        </Section>
      )}

      {/* Stretch Awards */}
      {stretchAwards.length > 0 && (
        <Section title="Stretch Awards (High Prestige)" icon={<TrendingUp />}>
          <div className="space-y-2">
            {stretchAwards.map((award) => renderAwardItem(award, BRAND_COLORS.primary, BRAND_COLORS.primaryBg))}
          </div>
        </Section>
      )}

      {/* Strategy Notes */}
      {strategyNotes.length > 0 && (
        <Section title="Strategy Notes" icon={<Brain />}>
          <ul className="space-y-2">
            {strategyNotes.map((note, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span style={{ color: BRAND_COLORS.primary }}>•</span>
                {note}
              </li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  );
}
```

### 2.7 Narrative Synthesis Quality Fix

**Problem Solved:** LLM was hallucinating placeholder names like "Jenny"

**File:** `agents/agents/narrative_synthesis.py`

```python
def _build_synthesis_prompt(self, identity, aptitude, passion, service, scores, archetype):
    return f"""You are an elite college admissions strategist...

CRITICAL: Do NOT use any names like "Jenny", "John", or any made-up names in the narrative.
Refer to the student as "this student", "they", or write in a way that describes their journey
without using a specific name. The narrative should be written about the student in third person
without naming them.

## THE IVYLEVEL NARRATIVE FORMULA
Create a narrative using this proven formula:
IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE

...

2. **Narrative DNA** (2-3 paragraphs): A compelling narrative that:
   - Shows transformation and growth
   - Connects identity to achievements
   - Demonstrates authentic voice
   - IMPORTANT: Do NOT use any names. Write about "this student", "they", or describe their
     journey in third person without a name.

...
"""
```

---

## PART 3: COMPLETE FILE MANIFEST

### 3.1 Core Agent Components

| File | Description | v15.0 Changes |
|------|-------------|---------------|
| `components/agents/AgentDashboardV13.tsx` | Main 6-agent dashboard | Added modal state management |
| `components/agents/AgentDetailModal.tsx` | **NEW** Detail modal for all agents | Full implementation |
| `components/agents/cards/AgentCardBase.tsx` | Base card template | Added `onClick` prop |
| `components/agents/cards/AssessmentAgentCard.tsx` | Narrative DNA card | Added `onViewDetails` |
| `components/agents/cards/GamePlanAgentCard.tsx` | Game plan card | Added `onViewDetails` |
| `components/agents/cards/ExecutionAgentCard.tsx` | EDS score card | Added `onViewDetails` |
| `components/agents/cards/AwardsAgentCard.tsx` | Portfolio card | Added `onViewDetails` |
| `components/agents/cards/OpportunityAgentCard.tsx` | Matches & alerts card | Added `onViewDetails` |
| `components/agents/cards/CrisisAgentCard.tsx` | Crisis response card | Added `onViewDetails` |
| `components/agents/CrisisAlchemyModal.tsx` | Crisis report workflow | Existing |
| `components/agents/NotificationsPreview.tsx` | Dashboard notifications | Existing |

### 3.2 API & Hooks

| File | Description | v15.0 Changes |
|------|-------------|---------------|
| `lib/api/agentClient.ts` | Agent API client | Extended timeouts (120s for LLM) |
| `lib/api/agentV13Client.ts` | v13 specific endpoints | Existing |
| `hooks/useAgentData.ts` | React Query hooks | Abort error handling, retry:false |

### 3.3 Backend Files

| File | Description | v15.0 Changes |
|------|-------------|---------------|
| `agents/main.py` | FastAPI entry point | **Environment loading before imports** |
| `agents/agents/narrative_synthesis.py` | Narrative agent | Gemini primary, prompt fix |
| `agents/agents/core/react_base.py` | ReAct framework | Existing (v13.2) |
| `agents/agents/core/memory.py` | Memory manager | Existing (v13.2) |
| `agents/.env` | Agent environment | **New API keys** |

### 3.4 Type Definitions

| File | Description | v15.0 Changes |
|------|-------------|---------------|
| `lib/types/agents.ts` | Agent type definitions | AwardMatch, AwardPortfolio types |
| `lib/constants/brand.ts` | Brand colors | Existing |

---

## PART 4: CONFIGURATION

### 4.1 Environment Variables

**Frontend (`.env.local`)**
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
NEXT_PUBLIC_AGENT_API_URL=http://localhost:8001
```

**Backend (`agents/.env`)**
```env
# LLM Providers (v15.0: Dual provider support)
OPENAI_API_KEY=sk-proj-xxx
GOOGLE_GENERATIVE_AI_API_KEY=AIzaSyXxx

# LangChain/LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_xxx
LANGCHAIN_PROJECT=ivylevel-v15

# Redis (Short-term Memory)
REDIS_URL=redis://localhost:6379
REDIS_TTL=86400

# Supabase (Long-term Memory)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx

# Feature Flags
ENABLE_REACT_AGENTS=true
ENABLE_MEMORY_SYSTEM=true
ENABLE_HITL_WORKFLOW=true
```

### 4.2 Quality Thresholds

```python
# agents/agents/core/thresholds.py
class QualityThresholds:
    MIN_QUALITY_SCORE = 70      # Content quality (0-100)
    MIN_VOICE_SCORE = 70        # Voice compliance (0-100)
    MIN_GOLDEN_SIMILARITY = 0.6 # Golden example match (0-1)
    MAX_REACT_CYCLES = 3        # Self-correction attempts
```

### 4.3 API Timeouts

```typescript
// lib/api/agentClient.ts
const API_TIMEOUT = 60000;        // Standard: 60 seconds
const API_TIMEOUT_LONG = 120000;  // LLM operations: 120 seconds

// Operations using extended timeout:
// - generateGamePlan()
// - synthesizeNarrative()
// - handleCrisis()
```

---

## PART 5: TESTING CHECKLIST

### 5.1 v15.0 Specific Tests

| TC# | Test Case | Steps | Expected Result |
|-----|-----------|-------|-----------------|
| TC-V15-001 | LLM provider selection | Start backend, check logs | "Using Google Gemini" message |
| TC-V15-002 | Extended timeout | Request game plan generation | No timeout for ~60s operations |
| TC-V15-003 | Abort error handling | Rapidly navigate in/out of tab | No console errors, graceful handling |
| TC-V15-004 | Agent card click | Click any agent card | Detail modal opens |
| TC-V15-005 | Awards detail view | Click Awards card | Shows Likely/Target/Stretch breakdown |
| TC-V15-006 | Narrative no names | Generate narrative | No "Jenny" or other placeholder names |
| TC-V15-007 | Modal keyboard close | Press Escape in modal | Modal closes |

### 5.2 Regression Tests

| TC# | Test Case | Expected Result |
|-----|-----------|-----------------|
| TC-REG-001 | Dashboard loads | All 6 agent cards visible |
| TC-REG-002 | Refresh All | All cards reload |
| TC-REG-003 | Health indicator | Shows green "Backend healthy" |
| TC-REG-004 | Notification bell | Badge shows unread count |
| TC-REG-005 | Crisis report | VARC response displayed |

---

## PART 6: DEPLOYMENT

### 6.1 Prerequisites

```bash
# Backend
cd agents
pip install -r requirements.txt
# Ensure .env has both OPENAI_API_KEY and GOOGLE_GENERATIVE_AI_API_KEY

# Frontend
npm install
# Ensure .env.local has NEXT_PUBLIC_AGENT_API_URL
```

### 6.2 Start Services

```bash
# Terminal 1: Backend
cd agents
python main.py
# Should see: "Uvicorn running on http://0.0.0.0:8001"
# Should see: "[NarrativeSynthesis] Using Google Gemini"

# Terminal 2: Frontend
npm run dev
# Should see: "Ready on http://localhost:3000"
```

### 6.3 Health Check

```bash
# Check backend health
curl http://localhost:8001/v13/health

# Expected response:
{
  "status": "healthy",
  "version": "15.0.0",
  "react_enabled": true,
  "memory_enabled": true,
  "hitl_enabled": true,
  "thresholds": {
    "min_quality": 70,
    "min_voice": 70,
    "min_golden": 0.6,
    "max_cycles": 3
  }
}
```

---

## PART 7: MIGRATION FROM v13.3

### 7.1 Breaking Changes

None. v15.0 is fully backward compatible with v13.3.

### 7.2 Required Updates

1. **Update `agents/.env`** - Add Google API key
2. **Update `agents/main.py`** - Add dotenv loading at top
3. **No frontend changes required** - New components are additive

### 7.3 Recommended Updates

1. Update version badge in dashboard header
2. Update health endpoint version response
3. Update documentation references

---

## APPENDIX A: Version Comparison Matrix

| Feature | v13.0 | v13.1 | v13.2 | v13.3 | v15.0 |
|---------|-------|-------|-------|-------|-------|
| ReAct Framework | ✅ | ✅ | ✅ | ✅ | ✅ |
| Quality Gates (70/70/0.6) | ❌ | ✅ | ✅ | ✅ | ✅ |
| Memory System | Schema | Schema | Full | Full | Full |
| HITL Workflow | ✅ | ✅ | ✅ | ✅ | ✅ |
| 6-Agent Dashboard | ❌ | ❌ | ❌ | ✅ | ✅ |
| Agent Detail Modals | ❌ | ❌ | ❌ | ❌ | **✅** |
| Clickable Cards | ❌ | ❌ | ❌ | ❌ | **✅** |
| Awards Tier View | ❌ | ❌ | ❌ | ❌ | **✅** |
| Dual LLM Provider | ❌ | ❌ | ❌ | ❌ | **✅** |
| Extended Timeouts | ❌ | ❌ | ❌ | ❌ | **✅** |
| Abort Error Handling | ❌ | ❌ | ❌ | ❌ | **✅** |
| Prompt Quality Fix | ❌ | ❌ | ❌ | ❌ | **✅** |
| Notifications | ❌ | ❌ | ❌ | ✅ | ✅ |
| Crisis Alchemy UI | ❌ | ❌ | ❌ | ✅ | ✅ |

---

## APPENDIX B: API Endpoints Reference

### B.1 Agent Endpoints

| Endpoint | Method | Timeout | Description |
|----------|--------|---------|-------------|
| `/v13/health` | GET | 60s | Health check with version |
| `/agents/narrative/{profile_id}` | GET | 60s | Get narrative DNA |
| `/agents/narrative/synthesize` | POST | 120s | Generate narrative |
| `/agents/gameplan/generate` | POST | 120s | Generate game plan |
| `/agents/execution/eds/{profile_id}` | GET | 60s | Get EDS score |
| `/agents/execution/crisis` | POST | 120s | Handle crisis |
| `/agents/awards/match/{profile_id}` | GET | 60s | Get award matches |
| `/agents/awards/portfolio/{profile_id}` | GET | 60s | Get portfolio |
| `/agents/opportunities/match/{profile_id}` | GET | 60s | Get opportunities |
| `/agents/opportunities/alerts/{profile_id}` | GET | 60s | Get alerts |
| `/notifications/{profile_id}` | GET | 60s | Get notifications |
| `/notifications/{profile_id}/count` | GET | 60s | Get unread count |

### B.2 Memory Endpoints (v13.2+)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v13/memory/handoff` | POST | Create handoff |
| `/v13/memory/handoff/{profile_id}/{to_agent}` | GET | Get handoff |
| `/v13/knowledge/search` | GET | Search knowledge base |
| `/v13/profile/{profile_id}/evolution` | GET | Profile timeline |
| `/v13/interactions/{profile_id}/recall` | GET | Semantic search |
| `/v13/interactions/{profile_id}/recent` | GET | Recent interactions |

---

## APPENDIX C: Brand Colors Quick Reference

```typescript
export const BRAND_COLORS = {
  // Primary
  primary: '#FF4A23',              // Ivylevel orange
  primaryBg: 'rgba(255, 74, 35, 0.1)',

  // Secondary
  secondary: '#641432',            // Ivylevel maroon

  // Text
  textHeading: '#641432',          // Maroon
  textPrimary: '#374151',          // Gray-700
  textSecondary: '#4b5563',        // Gray-600
  textMuted: '#9ca3af',            // Gray-400

  // Backgrounds
  bgPrimary: 'rgba(255, 255, 255, 0.95)',
  bgSecondary: '#f9fafb',          // Gray-50
  bgPage: '#f3f4f6',               // Gray-100
  bgSuccess: 'rgba(22, 163, 74, 0.1)',
  bgWarning: 'rgba(234, 183, 5, 0.1)',
  bgError: 'rgba(220, 38, 38, 0.1)',

  // Status
  success: '#16a34a',              // Green-600
  warning: '#d97706',              // Amber-600
  error: '#dc2626',                // Red-600

  // Borders
  borderLight: '#e5e7eb',          // Gray-200
  borderDefault: '#d1d5db',        // Gray-300
};
```

---

*PRD v15.0 - Complete Multi-Agent Platform*
*Production Ready Release*
*Date: January 12, 2026*
