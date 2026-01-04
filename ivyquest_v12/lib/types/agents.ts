/**
 * Agent Types - v11.0
 */

export type AgentType = 'assessment' | 'execution' | 'gameplan' | 'crisis' | 'cri' | 'narrative' | 'awards' | 'opportunity' | 'chat';

export interface AgentResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
  agentType: AgentType;
}

export interface GamePlanAction {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  phase: 'immediate' | 'short_term' | 'long_term';
  timeEstimate: string;
  edgePoints: number;
  impactScore: number;
  tips: string[];
}

export interface CrisisData {
  id: string;
  title: string;
  severity: 'high' | 'medium' | 'low';
  status: 'detected' | 'proposed' | 'approved' | 'resolved';
  protocol: {
    validate: string;
    act: string;
    reframe: string;
    create: string;
  };
  approvalDeadline?: string;
}

export interface AwardMatch {
  id: string;
  name: string;
  amount: number;
  deadline: string;
  deadlineDays: number;
  winProbability: number;
  roi: 'high' | 'medium' | 'low';
  effortHours: number;
  matchReasons: string[];
  requirements: string[];
}

export interface OpportunityMatch {
  id: string;
  name: string;
  type: 'summer_program' | 'internship' | 'research' | 'competition' | 'conference';
  fitScore: number;
  deadline?: string;
  isFree: boolean;
  description: string;
  matchReasons: string[];
}
