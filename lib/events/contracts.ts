/**
 * IvyQuest v10.0 Event Bus Contracts
 * ==================================
 * Canonical event types for agent-to-agent and agent-to-UI communication.
 * Implemented via Supabase Realtime or internal pub/sub.
 */

// =====================================================
// Event Type Definitions
// =====================================================

export type IvyEventType =
  | 'ASSESSMENT_COMPLETED'
  | 'PROJECT_STALLED'
  | 'CRISIS_DETECTED'
  | 'CRISIS_RESOLVED'
  | 'HUMAN_OVERRIDE'
  | 'SUCCESS_ACHIEVED'
  | 'GAMEPLAN_GENERATED'
  | 'AWARD_MATCHED'
  | 'OPPORTUNITY_ALERT'
  | 'STATE_VERSIONED';

// =====================================================
// Event Payloads
// =====================================================

export interface AssessmentCompletedPayload {
  profileId: string;
  narrativeDna: string;
  narrativeThemes: string[];
  narrativeConfidence: number;
  cri: number;
  archetypeId: string | null;
  archetypeLabel: string;
  archetypeConfidence: number;
  archetypeRationale: string;
  hiddenTarget: string | null;
}

export interface ProjectStalledPayload {
  profileId: string;
  projectId: string;
  projectName: string;
  daysInactive: number;
  executionDebt: number;
  completionRate: number;
}

export interface CrisisDetectedPayload {
  profileId: string;
  crisisId: string;
  type: 'blocker' | 'rejection' | 'conflict' | 'deadline' | 'motivation' | 'academic' | 'external' | 'opportunity';
  title: string;
  description: string;
  severity: 1 | 2 | 3 | 4 | 5;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  requiresApproval: boolean;
  approvalDeadline: string;
}

export interface CrisisResolvedPayload {
  profileId: string;
  crisisId: string;
  resolutionHours: number;
  outcome: string;
  reframedOpportunity: string;
  convertedToActivity: boolean;
  activityId?: string;
}

export interface HumanOverridePayload {
  profileId: string;
  agent: 'Assessment' | 'Execution' | 'GamePlan' | 'Awards' | 'Opportunity';
  eventType: string;
  override: Record<string, unknown>;
  rationale: string;
  approvedBy: string;
  timestamp: string;
}

export interface SuccessAchievedPayload {
  profileId: string;
  type: 'project_complete' | 'award_won' | 'opportunity_accepted' | 'goal_met';
  impactScore: number;
  description: string;
  vectorData: {
    constraints: string[];
    archetype: string;
    spike: string;
    cri: number;
    outcome: string;
  };
  // CRITICAL: Only SUCCESS_ACHIEVED events are ingested for RLHF
  shouldIngestVector: true;
}

export interface GamePlanGeneratedPayload {
  profileId: string;
  activities: {
    name: string;
    type: string;
    touchpoints: string[];
    touchpointCount: number;
    roiScore: number;
    isStretch: boolean;
  }[];
  identitySeeds: {
    seed: string;
    plantDate: string;
    bloomDate: string;
    targetOpportunity: string;
    status: 'pending' | 'planted' | 'blooming' | 'harvested';
  }[];
  overwhelmFactor: number;
}

export interface AwardMatchedPayload {
  profileId: string;
  awardId: string;
  awardName: string;
  category: string;
  level: string;
  winProbability: number;
  roiScore: number;
  recommendation: 'likely' | 'stretch' | 'skip';
  effortHours: number;
}

export interface OpportunityAlertPayload {
  profileId: string;
  opportunityId: string;
  opportunityName: string;
  type: string;
  deadline: string;
  daysUntilDeadline: number;
  alertType: 'advance_planning' | 'application_open' | 'deadline_approaching' | 'last_chance';
  acceptProbability: number;
  backupOptions: string[];
}

export interface StateVersionedPayload {
  profileId: string;
  agent: string;
  version: number;
  eventType: string;
  createdBy: 'agent' | 'human' | 'system';
  timestamp: string;
}

// =====================================================
// Union Event Type
// =====================================================

export type IvyEvent =
  | { type: 'ASSESSMENT_COMPLETED'; payload: AssessmentCompletedPayload; timestamp: string }
  | { type: 'PROJECT_STALLED'; payload: ProjectStalledPayload; timestamp: string }
  | { type: 'CRISIS_DETECTED'; payload: CrisisDetectedPayload; timestamp: string }
  | { type: 'CRISIS_RESOLVED'; payload: CrisisResolvedPayload; timestamp: string }
  | { type: 'HUMAN_OVERRIDE'; payload: HumanOverridePayload; timestamp: string }
  | { type: 'SUCCESS_ACHIEVED'; payload: SuccessAchievedPayload; timestamp: string }
  | { type: 'GAMEPLAN_GENERATED'; payload: GamePlanGeneratedPayload; timestamp: string }
  | { type: 'AWARD_MATCHED'; payload: AwardMatchedPayload; timestamp: string }
  | { type: 'OPPORTUNITY_ALERT'; payload: OpportunityAlertPayload; timestamp: string }
  | { type: 'STATE_VERSIONED'; payload: StateVersionedPayload; timestamp: string };

// =====================================================
// Event Validation
// =====================================================

export function validateEvent(event: IvyEvent): boolean {
  if (!event.type || !event.payload || !event.timestamp) {
    return false;
  }

  // All events must have profileId (except some system events)
  if (!('profileId' in event.payload)) {
    return false;
  }

  return true;
}

// =====================================================
// Success Vector Ingestion Rule
// =====================================================

/**
 * CRITICAL: Only ingest on SUCCESS_ACHIEVED events, NOT crises.
 * Crises go to training logs, not Pinecone/pgvector similarity space.
 * This prevents poisoning the success vector space with failure patterns.
 */
export function shouldIngestVector(event: IvyEvent): boolean {
  return event.type === 'SUCCESS_ACHIEVED';
}

// =====================================================
// Event Factory Functions
// =====================================================

export function createEvent<T extends IvyEventType>(
  type: T,
  payload: Extract<IvyEvent, { type: T }>['payload']
): Extract<IvyEvent, { type: T }> {
  return {
    type,
    payload,
    timestamp: new Date().toISOString(),
  } as Extract<IvyEvent, { type: T }>;
}

export function createAssessmentCompletedEvent(
  payload: AssessmentCompletedPayload
): IvyEvent {
  return createEvent('ASSESSMENT_COMPLETED', payload);
}

export function createCrisisDetectedEvent(
  payload: CrisisDetectedPayload
): IvyEvent {
  return createEvent('CRISIS_DETECTED', payload);
}

export function createSuccessAchievedEvent(
  payload: SuccessAchievedPayload
): IvyEvent {
  return createEvent('SUCCESS_ACHIEVED', payload);
}

// =====================================================
// Event Handlers Type
// =====================================================

export type EventHandler<T extends IvyEventType> = (
  event: Extract<IvyEvent, { type: T }>
) => Promise<void> | void;

export interface EventHandlers {
  ASSESSMENT_COMPLETED?: EventHandler<'ASSESSMENT_COMPLETED'>;
  PROJECT_STALLED?: EventHandler<'PROJECT_STALLED'>;
  CRISIS_DETECTED?: EventHandler<'CRISIS_DETECTED'>;
  CRISIS_RESOLVED?: EventHandler<'CRISIS_RESOLVED'>;
  HUMAN_OVERRIDE?: EventHandler<'HUMAN_OVERRIDE'>;
  SUCCESS_ACHIEVED?: EventHandler<'SUCCESS_ACHIEVED'>;
  GAMEPLAN_GENERATED?: EventHandler<'GAMEPLAN_GENERATED'>;
  AWARD_MATCHED?: EventHandler<'AWARD_MATCHED'>;
  OPPORTUNITY_ALERT?: EventHandler<'OPPORTUNITY_ALERT'>;
  STATE_VERSIONED?: EventHandler<'STATE_VERSIONED'>;
}
