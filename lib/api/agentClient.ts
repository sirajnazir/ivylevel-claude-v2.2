// IvyQuest Agent API Client
// File: lib/api/agentClient.ts

const AGENT_API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 60000;
const API_TIMEOUT_LONG = 120000; // For slow LLM endpoints like game plan generation

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

interface ApiCallOptions extends RequestInit {
  timeout?: number;
}

async function apiCall<T>(endpoint: string, options: ApiCallOptions = {}): Promise<ApiResponse<T>> {
  const { timeout = API_TIMEOUT, ...fetchOptions } = options;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${AGENT_API_URL}${endpoint}`, {
      headers: { 'Content-Type': 'application/json', ...fetchOptions.headers },
      signal: controller.signal,
      ...fetchOptions,
    });
    clearTimeout(timeoutId);

    const data = await response.json();
    if (!response.ok || data.success === false) {
      return { success: false, error: data.detail || data.error || `HTTP ${response.status}` };
    }
    return { success: true, data };
  } catch (error) {
    clearTimeout(timeoutId);
    // Check if this is an abort error
    if (error instanceof Error && (error.name === 'AbortError' || error.message.includes('abort'))) {
      // Return a special response for aborts that the caller can detect
      return { success: false, error: 'REQUEST_ABORTED' };
    }
    return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
  }
}

// Assessment Agent
export async function enhanceAssessment(profileId: string, data?: Record<string, unknown>) {
  return apiCall('/agents/assessment/enhance', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId, data }),
  });
}

export async function synthesizeNarrativeDNA(profileId: string) {
  // Backend endpoint is /agents/narrative/synthesize, not /agents/assessment/narrative
  return apiCall('/agents/narrative/synthesize', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId }),
  });
}

export async function detectArchetype(profileId: string) {
  return apiCall('/agents/assessment/archetype', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId }),
  });
}

// Game Plan Agent
export async function generateGamePlan(profileId: string, assessmentData?: Record<string, unknown>) {
  // Use longer timeout for game plan generation (LLM-intensive operation)
  return apiCall('/agents/gameplan/generate', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId, data: assessmentData }),
    timeout: API_TIMEOUT_LONG,
  });
}

export async function getFilteredActivities(profileId: string) {
  return apiCall(`/agents/gameplan/activities/${profileId}`);
}

export async function getIdentitySeeds(profileId: string) {
  return apiCall(`/agents/gameplan/seeds/${profileId}`);
}

// Execution Agent
export async function scaffoldProject(input: { profile_id: string; name: string; type: string; description?: string; deadline?: string }) {
  return apiCall('/agents/execution/scaffold', { method: 'POST', body: JSON.stringify(input) });
}

export async function handleCrisis(input: { profile_id: string; crisis_type: string; description: string; urgency?: number }) {
  return apiCall('/agents/execution/crisis', { method: 'POST', body: JSON.stringify(input) });
}

export async function getBlockers(profileId: string) {
  return apiCall(`/agents/execution/blockers/${profileId}`);
}

export async function getExecutionDebtScore(profileId: string) {
  return apiCall(`/agents/execution/eds/${profileId}`);
}

export async function approveHandoff(crisisId: string, approved: boolean, rationale?: string) {
  return apiCall('/agents/handoff/approve', {
    method: 'POST',
    body: JSON.stringify({ crisis_id: crisisId, approved, rationale }),
  });
}

// Awards Agent
export async function matchAwards(profileId: string) {
  return apiCall(`/agents/awards/match/${profileId}`);
}

export async function getAwardPortfolio(profileId: string) {
  return apiCall(`/agents/awards/portfolio/${profileId}`);
}

export async function getAwardTimeline(profileId: string) {
  return apiCall(`/agents/awards/timeline/${profileId}`);
}

// Opportunities Agent
export async function matchOpportunities(profileId: string) {
  return apiCall(`/agents/opportunities/match/${profileId}`);
}

export async function getOpportunityAlerts(profileId: string) {
  return apiCall(`/agents/opportunities/alerts/${profileId}`);
}

export async function getBackupCascades(profileId: string) {
  return apiCall(`/agents/opportunities/cascades/${profileId}`);
}

export async function getOpportunityTimeline(profileId: string) {
  return apiCall(`/agents/opportunities/timeline/${profileId}`);
}

// Tools
export async function applyMicroEdits(text: string, essayType: string = 'common_app') {
  return apiCall('/tools/micro-edits', {
    method: 'POST',
    body: JSON.stringify({ text, essay_type: essayType }),
  });
}

export async function analyzeEssay(text: string, essayType: string = 'common_app') {
  return apiCall('/tools/analyze-essay', {
    method: 'POST',
    body: JSON.stringify({ text, essay_type: essayType }),
  });
}

// V2.0 Jenny Intelligence APIs
export async function validateJennyVoice(text: string) {
  return apiCall('/validation/jenny-voice', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function analyzeTimeAudit(input: {
  school_hours: number;
  sleep_hours: number;
  fixed_commitments: number;
  social_media_hours: number;
}) {
  return apiCall('/agents/time-audit', {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export async function getNCWITStrategy(profileId: string) {
  return apiCall('/agents/ncwit-strategy', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId }),
  });
}

export async function transformCrisis(profileId: string, crisisDescription: string) {
  return apiCall('/agents/crisis-alchemy', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId, crisis_description: crisisDescription }),
  });
}

export async function generateWeeklyPlan(profileId: string) {
  return apiCall('/agents/weekly-plan', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId }),
  });
}

export async function getJennyTechniques() {
  return apiCall('/agents/jenny-techniques');
}

// Health Check
export async function checkAgentHealth() {
  return apiCall('/health');
}

export const agentApi = {
  enhanceAssessment,
  synthesizeNarrativeDNA,
  detectArchetype,
  generateGamePlan,
  getFilteredActivities,
  getIdentitySeeds,
  scaffoldProject,
  handleCrisis,
  getBlockers,
  getExecutionDebtScore,
  approveHandoff,
  matchAwards,
  getAwardPortfolio,
  getAwardTimeline,
  matchOpportunities,
  getOpportunityAlerts,
  getBackupCascades,
  getOpportunityTimeline,
  applyMicroEdits,
  analyzeEssay,
  checkAgentHealth,
  // V2.0 Jenny Intelligence
  validateJennyVoice,
  analyzeTimeAudit,
  getNCWITStrategy,
  transformCrisis,
  generateWeeklyPlan,
  getJennyTechniques,
};

export default agentApi;
