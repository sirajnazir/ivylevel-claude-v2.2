// Multi-Agent Dashboard Tab
// File: components/dashboard/MultiAgentTab.tsx

'use client';

import React, { useState } from 'react';
import { Brain, Map, Zap, Award, Compass, RefreshCw, AlertCircle, CheckCircle, Loader2, ChevronRight, Activity, Clock, Flame } from 'lucide-react';
import { NarrativeDNACard } from '@/components/agents/NarrativeDNACard';
import {
  useAssessmentEnhancement,
  useGamePlan,
  useAwardMatches,
  useOpportunityMatches,
  useOpportunityAlerts,
  useExecutionDebtScore,
  useAgentHealth,
  useDashboardData,
} from '@/hooks/useAgentData';
import { useStudentStore } from '@/lib/store/useStudentStore';

// v2.0 Components
import { TimeAuditCardV2 } from '@/components/agents/TimeAuditCardV2';
import { AwardsPortfolioCardV2 } from '@/components/agents/AwardsPortfolioCardV2';
import { CrisisAlchemyModal } from '@/components/agents/CrisisAlchemyModal';
import { useAgentV2Health } from '@/lib/hooks/useAgentV2';

interface MultiAgentTabProps {
  profileId: string | null;
}

interface AgentCardProps {
  name: string;
  icon: React.ElementType;
  color: string;
  status: 'idle' | 'loading' | 'success' | 'error';
  error?: string;
  children: React.ReactNode;
  onRefresh?: () => void;
}

function AgentCard({ name, icon: Icon, color, status, error, children, onRefresh }: AgentCardProps) {
  const colorClasses: Record<string, { bg: string; icon: string; border: string }> = {
    purple: { bg: 'bg-purple-50 dark:bg-purple-900/20', icon: 'bg-purple-100 dark:bg-purple-800 text-purple-600 dark:text-purple-300', border: 'border-purple-200 dark:border-purple-800' },
    blue: { bg: 'bg-blue-50 dark:bg-blue-900/20', icon: 'bg-blue-100 dark:bg-blue-800 text-blue-600 dark:text-blue-300', border: 'border-blue-200 dark:border-blue-800' },
    green: { bg: 'bg-green-50 dark:bg-green-900/20', icon: 'bg-green-100 dark:bg-green-800 text-green-600 dark:text-green-300', border: 'border-green-200 dark:border-green-800' },
    amber: { bg: 'bg-amber-50 dark:bg-amber-900/20', icon: 'bg-amber-100 dark:bg-amber-800 text-amber-600 dark:text-amber-300', border: 'border-amber-200 dark:border-amber-800' },
    teal: { bg: 'bg-teal-50 dark:bg-teal-900/20', icon: 'bg-teal-100 dark:bg-teal-800 text-teal-600 dark:text-teal-300', border: 'border-teal-200 dark:border-teal-800' },
  };
  const colors = colorClasses[color] || colorClasses.purple;

  return (
    <div className={`rounded-xl border ${colors.border} ${colors.bg} overflow-hidden`}>
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${colors.icon}`}><Icon className="w-5 h-5" /></div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">{name}</h3>
              <div className="flex items-center gap-2 mt-0.5">
                {status === 'loading' && <span className="flex items-center gap-1 text-xs text-blue-600"><Loader2 className="w-3 h-3 animate-spin" />Processing...</span>}
                {status === 'success' && <span className="flex items-center gap-1 text-xs text-green-600"><CheckCircle className="w-3 h-3" />Ready</span>}
                {status === 'error' && <span className="flex items-center gap-1 text-xs text-red-600"><AlertCircle className="w-3 h-3" />Error</span>}
              </div>
            </div>
          </div>
          {onRefresh && (
            <button onClick={onRefresh} disabled={status === 'loading'} className="p-2 hover:bg-white dark:hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50">
              <RefreshCw className={`w-4 h-4 text-gray-500 ${status === 'loading' ? 'animate-spin' : ''}`} />
            </button>
          )}
        </div>
      </div>
      <div className="p-4">
        {status === 'error' && error ? (
          <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        ) : children}
      </div>
    </div>
  );
}

function AssessmentSection({ profileId }: { profileId: string }) {
  const { data, isLoading, isError, error, refetch } = useAssessmentEnhancement(profileId);

  return (
    <AgentCard name="Assessment Agent" icon={Brain} color="purple" status={isLoading ? 'loading' : isError ? 'error' : data ? 'success' : 'idle'} error={error?.message} onRefresh={() => refetch()}>
      {data ? (
        <div className="space-y-4">
          <NarrativeDNACard narrativeDNA={data.narrative_dna} compact />
          {data.archetype && (
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Archetype</span>
                <span className="px-2 py-1 bg-purple-100 dark:bg-purple-800 text-purple-700 dark:text-purple-300 rounded text-xs font-medium">{data.archetype.label}</span>
              </div>
              <div className="mt-2 flex items-center gap-2">
                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                  <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${data.archetype.confidence * 100}%` }} />
                </div>
                <span className="text-xs text-gray-500">{Math.round(data.archetype.confidence * 100)}%</span>
              </div>
            </div>
          )}
          {data.cri && (
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Context Relativity Index</span>
                <span className="text-lg font-bold text-purple-600 dark:text-purple-400">{data.cri.toFixed(2)}</span>
              </div>
            </div>
          )}
        </div>
      ) : <p className="text-sm text-gray-500">Loading assessment data...</p>}
    </AgentCard>
  );
}

function GamePlanSection({ profileId }: { profileId: string }) {
  const { data, isLoading, isError, error, refetch } = useGamePlan(profileId);

  return (
    <AgentCard name="Game Plan Agent" icon={Map} color="blue" status={isLoading ? 'loading' : isError ? 'error' : data ? 'success' : 'idle'} error={error?.message} onRefresh={() => refetch()}>
      {data?.game_plan ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700 text-center">
              <p className="text-2xl font-bold text-blue-600">{data.game_plan.activities?.length || 0}</p>
              <p className="text-xs text-gray-500">Activities</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700 text-center">
              <p className="text-2xl font-bold text-blue-600">{data.game_plan.identity_seeds?.length || 0}</p>
              <p className="text-xs text-gray-500">Seeds Planted</p>
            </div>
          </div>
          {data.game_plan.phases && data.game_plan.phases.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Phases</p>
              {data.game_plan.phases.slice(0, 3).map((phase, i) => (
                <div key={i} className="flex items-center gap-2 text-sm text-gray-600">
                  <ChevronRight className="w-4 h-4 text-blue-500" />
                  <span className="font-medium">{phase.name}:</span>
                  <span>{phase.activity_count} activities</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : <p className="text-sm text-gray-500">Loading game plan...</p>}
    </AgentCard>
  );
}

function ExecutionSection({ profileId }: { profileId: string }) {
  const { data: eds, isLoading, isError, error, refetch } = useExecutionDebtScore(profileId);
  const statusColors = {
    healthy: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    at_risk: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
    critical: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
  };

  return (
    <AgentCard name="Execution Agent" icon={Zap} color="green" status={isLoading ? 'loading' : isError ? 'error' : eds ? 'success' : 'idle'} error={error?.message} onRefresh={() => refetch()}>
      {eds ? (
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Execution Debt Score</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[eds.status]}`}>{eds.status.replace('_', ' ')}</span>
            </div>
            <div className="flex items-end gap-4">
              <div className="text-4xl font-bold text-gray-900 dark:text-white">{Math.round(eds.execution_debt_score)}</div>
              <div className="flex-1">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className={`h-2 rounded-full transition-all ${eds.status === 'healthy' ? 'bg-green-500' : eds.status === 'at_risk' ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${Math.min(100, (eds.execution_debt_score / 100) * 100)}%` }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : <p className="text-sm text-gray-500">Loading execution data...</p>}
    </AgentCard>
  );
}

function AwardsSection({ profileId }: { profileId: string }) {
  const { data, isLoading, isError, error, refetch } = useAwardMatches(profileId);

  return (
    <AgentCard name="Awards Agent" icon={Award} color="amber" status={isLoading ? 'loading' : isError ? 'error' : data ? 'success' : 'idle'} error={error?.message} onRefresh={() => refetch()}>
      {data?.portfolio ? (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-green-50 dark:bg-green-900/30 rounded-lg p-2 text-center">
              <p className="text-lg font-bold text-green-600">{data.portfolio.likely?.length || 0}</p>
              <p className="text-xs text-gray-500">Likely</p>
            </div>
            <div className="bg-yellow-50 dark:bg-yellow-900/30 rounded-lg p-2 text-center">
              <p className="text-lg font-bold text-yellow-600">{data.portfolio.target?.length || 0}</p>
              <p className="text-xs text-gray-500">Target</p>
            </div>
            <div className="bg-orange-50 dark:bg-orange-900/30 rounded-lg p-2 text-center">
              <p className="text-lg font-bold text-orange-600">{data.portfolio.stretch?.length || 0}</p>
              <p className="text-xs text-gray-500">Stretch</p>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Expected Wins</span>
              <span className="text-lg font-bold text-amber-600">{data.portfolio.expected_wins?.toFixed(1) || 0}</span>
            </div>
          </div>
        </div>
      ) : <p className="text-sm text-gray-500">Loading award matches...</p>}
    </AgentCard>
  );
}

function OpportunitiesSection({ profileId }: { profileId: string }) {
  const { data, isLoading, isError, error, refetch } = useOpportunityMatches(profileId);
  const alerts = useOpportunityAlerts(profileId);

  return (
    <AgentCard name="Opportunities Agent" icon={Compass} color="teal" status={isLoading ? 'loading' : isError ? 'error' : data ? 'success' : 'idle'} error={error?.message} onRefresh={() => refetch()}>
      {data ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700 text-center">
              <p className="text-2xl font-bold text-teal-600">{data.matches?.length || 0}</p>
              <p className="text-xs text-gray-500">Matches</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700 text-center">
              <p className="text-2xl font-bold text-teal-600">{alerts.data?.urgent_count || 0}</p>
              <p className="text-xs text-gray-500">Urgent Alerts</p>
            </div>
          </div>
          {alerts.data?.alerts && alerts.data.alerts.length > 0 && (
            <div className="space-y-2">
              {alerts.data.alerts.slice(0, 2).map((alert, i) => (
                <div key={i} className={`rounded-lg p-2 text-sm ${alert.urgency === 'URGENT' ? 'bg-red-50 dark:bg-red-900/30 text-red-700' : 'bg-blue-50 dark:bg-blue-900/30 text-blue-700'}`}>
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    <span className="font-medium">{alert.opportunity_name}</span>
                    <span className="ml-auto text-xs">{alert.months_remaining}mo left</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : <p className="text-sm text-gray-500">Loading opportunities...</p>}
    </AgentCard>
  );
}

export function MultiAgentTab({ profileId }: MultiAgentTabProps) {
  const health = useAgentHealth();
  const v2Health = useAgentV2Health();
  const { refetchAll, isLoading } = useDashboardData(profileId);
  const [showCrisisModal, setShowCrisisModal] = useState(false);

  // Get real profile data from store
  const profile = useStudentStore((s) => s.profile);

  // Build studentProfile for V2 components from real profile data
  const studentProfile = {
    spike: profile.passion?.spike_category || 'general',
    identity: [
      profile.passion?.brag_text,
      profile.intended_major,
      profile.identity?.name,
    ].filter(Boolean) as string[],
    activities: [
      profile.passion?.project_description && {
        name: 'Main Project',
        description: profile.passion.project_description,
      },
      ...(profile.aptitude?.academic_awards || []).map((award) => ({
        name: award,
        description: 'Academic award',
      })),
      ...(profile.passion?.ec_awards || []).map((award) => ({
        name: award,
        description: 'Extracurricular award',
      })),
    ].filter(Boolean) as Array<{ name: string; description?: string }>,
    has_working_project: Boolean(
      profile.passion?.project_description &&
      profile.passion.project_description.length > 20
    ),
  };

  if (!profileId) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Brain className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">No Profile Selected</h3>
        <p className="text-gray-500 dark:text-gray-400">Complete your assessment to see multi-agent insights.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* v2.0 Backend Status */}
      <div className="mb-4 flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className={`w-2 h-2 rounded-full ${
          v2Health.data?.status === 'healthy' ? 'bg-green-500' :
          v2Health.isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'
        }`} />
        <span className="text-sm text-gray-600 dark:text-gray-400">
          v2.0 Backend: {v2Health.data?.status || (v2Health.isLoading ? 'connecting...' : 'offline')}
        </span>
        {v2Health.data?.version && (
          <span className="text-xs text-gray-400 ml-2">({v2Health.data.version})</span>
        )}
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Multi-Agent Dashboard</h2>
          <p className="text-gray-500 dark:text-gray-400">Your 5-agent coaching team working in parallel</p>
        </div>
        <div className="flex items-center gap-3">
          {health.data && (
            <span className="flex items-center gap-2 px-3 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-lg text-sm">
              <Activity className="w-4 h-4" />
              Backend {health.data.status}
            </span>
          )}
          <button
            onClick={() => setShowCrisisModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg font-medium hover:bg-orange-600 transition-colors"
          >
            <Flame className="w-4 h-4" />
            Crisis Help
          </button>
          <button onClick={refetchAll} disabled={isLoading} className="flex items-center gap-2 px-4 py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg font-medium hover:bg-gray-800 transition-colors disabled:opacity-50">
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh All
          </button>
        </div>
      </div>

      {/* v2.0 Feature Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TimeAuditCardV2 />
        <AwardsPortfolioCardV2 studentProfile={studentProfile} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AssessmentSection profileId={profileId} />
        <GamePlanSection profileId={profileId} />
        <ExecutionSection profileId={profileId} />
        <AwardsSection profileId={profileId} />
        <OpportunitiesSection profileId={profileId} />
      </div>

      {/* Crisis Alchemy Modal */}
      <CrisisAlchemyModal
        isOpen={showCrisisModal}
        onClose={() => setShowCrisisModal(false)}
        studentProfile={studentProfile}
      />
    </div>
  );
}

export default MultiAgentTab;
