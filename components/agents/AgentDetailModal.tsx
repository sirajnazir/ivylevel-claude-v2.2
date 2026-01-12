/**
 * AgentDetailModal Component
 * v13.3 - Expanded detail view for agent cards
 *
 * Features:
 * - Full-screen modal with detailed agent data
 * - Different views for each agent type
 * - Scrollable content with sections
 */
'use client';

import { ReactNode, useEffect } from 'react';
import { X, Brain, Target, Award, Lightbulb, AlertTriangle, Zap, Calendar, Clock, CheckCircle2, TrendingUp } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';

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
  // Close on escape key
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

  if (!isOpen) return null;

  const renderContent = () => {
    if (!data) {
      return (
        <div className="text-center py-8" style={{ color: BRAND_COLORS.textMuted }}>
          No data available
        </div>
      );
    }

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
        return <pre className="text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div
        className="relative w-full max-w-4xl max-h-[90vh] bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-6 py-4 border-b"
          style={{ borderColor: BRAND_COLORS.borderLight }}
        >
          <h2
            className="text-xl font-bold"
            style={{ color: BRAND_COLORS.textHeading }}
          >
            {title}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X size={20} style={{ color: BRAND_COLORS.textMuted }} />
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

// ============================================================
// ASSESSMENT DETAIL VIEW
// ============================================================
function AssessmentDetail({ data }: { data: Record<string, unknown> }) {
  const dna = data.dna as string || data.narrative_dna as string || '';
  const themes = (data.themes as string[]) || [];
  const confidence = (data.confidence as number) || 0;
  const identityMarkers = (data.identity_markers as string[]) || [];
  const brandStatement = data.brand_statement as string || data.rationale as string || '';

  return (
    <div className="space-y-6">
      {/* Narrative DNA */}
      <Section title="Narrative DNA" icon={<Brain size={20} />}>
        <p className="text-base leading-relaxed" style={{ color: BRAND_COLORS.textPrimary }}>
          {dna || 'No narrative generated yet'}
        </p>
      </Section>

      {/* Brand Statement */}
      {brandStatement && (
        <Section title="Brand Statement" icon={<Zap size={20} />}>
          <p className="text-base italic" style={{ color: BRAND_COLORS.secondary }}>
            "{brandStatement}"
          </p>
        </Section>
      )}

      {/* Themes */}
      {themes.length > 0 && (
        <Section title="Key Themes" icon={<Target size={20} />}>
          <div className="flex flex-wrap gap-2">
            {themes.map((theme, i) => (
              <span
                key={i}
                className="px-3 py-1.5 rounded-full text-sm"
                style={{
                  backgroundColor: BRAND_COLORS.primaryBg,
                  color: BRAND_COLORS.primary,
                }}
              >
                {theme}
              </span>
            ))}
          </div>
        </Section>
      )}

      {/* Identity Markers */}
      {identityMarkers.length > 0 && (
        <Section title="Identity Markers" icon={<CheckCircle2 size={20} />}>
          <ul className="space-y-2">
            {identityMarkers.map((marker, i) => (
              <li key={i} className="flex items-start gap-2">
                <CheckCircle2 size={16} style={{ color: BRAND_COLORS.success }} className="mt-0.5" />
                <span style={{ color: BRAND_COLORS.textPrimary }}>{marker}</span>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Confidence Score */}
      <Section title="Confidence Score" icon={<TrendingUp size={20} />}>
        <div className="flex items-center gap-4">
          <div className="flex-1 h-4 rounded-full bg-gray-200">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${confidence * 100}%`,
                backgroundColor:
                  confidence >= 0.8
                    ? BRAND_COLORS.success
                    : confidence >= 0.6
                    ? BRAND_COLORS.warning
                    : BRAND_COLORS.error,
              }}
            />
          </div>
          <span className="text-lg font-bold" style={{ color: BRAND_COLORS.textHeading }}>
            {Math.round(confidence * 100)}%
          </span>
        </div>
      </Section>
    </div>
  );
}

// ============================================================
// GAME PLAN DETAIL VIEW
// ============================================================
function GamePlanDetail({ data }: { data: Record<string, unknown> }) {
  const gamePlan = (data.game_plan as Record<string, unknown>) || data;
  const activities = (gamePlan.activities as unknown[]) || [];
  const seeds = (gamePlan.identity_seeds as Record<string, unknown>[]) || [];
  const phases = (gamePlan.phases as Record<string, unknown>[]) || [];
  const narrativeDna = gamePlan.narrative_dna as string || '';
  const summary = (gamePlan.summary as Record<string, unknown>) || {};

  return (
    <div className="space-y-6">
      {/* Summary */}
      <Section title="Plan Summary" icon={<Target size={20} />}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Activities" value={activities.length} />
          <StatCard label="Identity Seeds" value={seeds.length} />
          <StatCard label="Phases" value={phases.length} />
          <StatCard label="Touchpoints" value={(summary.total_touchpoints as number) || 0} />
        </div>
      </Section>

      {/* Narrative DNA */}
      {narrativeDna && (
        <Section title="Guiding Narrative" icon={<Brain size={20} />}>
          <p className="text-sm leading-relaxed" style={{ color: BRAND_COLORS.textPrimary }}>
            {narrativeDna}
          </p>
        </Section>
      )}

      {/* Phases */}
      {phases.length > 0 && (
        <Section title="Strategic Phases" icon={<Calendar size={20} />}>
          <div className="space-y-4">
            {phases.map((phase, i) => (
              <div
                key={i}
                className="p-4 rounded-lg"
                style={{ backgroundColor: BRAND_COLORS.bgSecondary }}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold" style={{ color: BRAND_COLORS.textHeading }}>
                    {(phase.name as string) || `Phase ${i + 1}`}
                  </h4>
                  <span className="text-sm" style={{ color: BRAND_COLORS.textMuted }}>
                    {phase.duration as string}
                  </span>
                </div>
                <p className="text-sm" style={{ color: BRAND_COLORS.textPrimary }}>
                  {phase.focus as string}
                </p>
                <div className="mt-2 text-xs" style={{ color: BRAND_COLORS.textMuted }}>
                  {(phase.activity_count as number) || 0} activities
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Identity Seeds */}
      {seeds.length > 0 && (
        <Section title="Identity Seeds" icon={<Lightbulb size={20} />}>
          <div className="space-y-4">
            {seeds.map((seed, i) => (
              <div
                key={i}
                className="p-4 rounded-lg border"
                style={{ borderColor: BRAND_COLORS.borderLight }}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold" style={{ color: BRAND_COLORS.textHeading }}>
                    {(seed.target as string) || `Seed ${i + 1}`}
                  </h4>
                  <span
                    className="px-2 py-0.5 rounded-full text-xs"
                    style={{
                      backgroundColor: BRAND_COLORS.primaryBg,
                      color: BRAND_COLORS.primary,
                    }}
                  >
                    {seed.target_type as string}
                  </span>
                </div>
                {seed.narrative_connection && (
                  <p className="text-sm mb-3" style={{ color: BRAND_COLORS.textMuted }}>
                    {(seed.narrative_connection as string).slice(0, 200)}...
                  </p>
                )}
                {/* Actions */}
                {(seed.actions as Record<string, unknown>[])?.slice(0, 3).map((action, j) => (
                  <div key={j} className="flex items-start gap-2 mt-2 text-sm">
                    <CheckCircle2 size={14} style={{ color: BRAND_COLORS.success }} className="mt-0.5" />
                    <span style={{ color: BRAND_COLORS.textPrimary }}>{action.action as string}</span>
                  </div>
                ))}
                {((seed.actions as unknown[])?.length || 0) > 3 && (
                  <p className="text-xs mt-2" style={{ color: BRAND_COLORS.textMuted }}>
                    +{((seed.actions as unknown[]).length - 3)} more actions
                  </p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}

// ============================================================
// EXECUTION DETAIL VIEW
// ============================================================
function ExecutionDetail({ data }: { data: Record<string, unknown> }) {
  const eds = (data.eds as number) || 0;
  const blockers = (data.blockers as Record<string, unknown>[]) || [];
  const debtLevel = data.debt_level as string || 'Unknown';

  return (
    <div className="space-y-6">
      {/* EDS Score */}
      <Section title="Execution Debt Score" icon={<Zap size={20} />}>
        <div className="flex items-center gap-6">
          <div
            className="w-32 h-32 rounded-full flex items-center justify-center"
            style={{
              backgroundColor: eds < 25 ? BRAND_COLORS.bgSuccess : eds < 50 ? BRAND_COLORS.warningBg : BRAND_COLORS.errorBg,
            }}
          >
            <span className="text-4xl font-bold" style={{ color: BRAND_COLORS.textHeading }}>
              {eds}
            </span>
          </div>
          <div>
            <p className="text-lg font-semibold" style={{ color: BRAND_COLORS.textHeading }}>
              {eds < 25 ? 'Excellent' : eds < 50 ? 'Good' : eds < 75 ? 'Needs Attention' : 'Critical'}
            </p>
            <p style={{ color: BRAND_COLORS.textMuted }}>
              {eds < 25
                ? 'You are on track with your execution'
                : eds < 50
                ? 'Some tasks need attention'
                : 'Multiple blockers affecting progress'}
            </p>
          </div>
        </div>
      </Section>

      {/* Blockers */}
      {blockers.length > 0 && (
        <Section title="Active Blockers" icon={<AlertTriangle size={20} />}>
          <div className="space-y-3">
            {blockers.map((blocker, i) => (
              <div
                key={i}
                className="p-4 rounded-lg"
                style={{ backgroundColor: BRAND_COLORS.errorBg }}
              >
                <h4 className="font-semibold" style={{ color: BRAND_COLORS.error }}>
                  {blocker.title as string}
                </h4>
                <p className="text-sm mt-1" style={{ color: BRAND_COLORS.textPrimary }}>
                  {blocker.description as string}
                </p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {blockers.length === 0 && (
        <div className="text-center py-8">
          <CheckCircle2 size={48} style={{ color: BRAND_COLORS.success }} className="mx-auto mb-3" />
          <p className="text-lg font-semibold" style={{ color: BRAND_COLORS.textHeading }}>
            No Active Blockers
          </p>
          <p style={{ color: BRAND_COLORS.textMuted }}>
            Your execution is proceeding smoothly
          </p>
        </div>
      )}
    </div>
  );
}

// ============================================================
// AWARDS DETAIL VIEW
// ============================================================
function AwardsDetail({ data }: { data: Record<string, unknown> }) {
  const matches = (data.matches as Record<string, unknown>[]) || [];
  const portfolio = (data.portfolio as Record<string, unknown>) || {};

  // Get awards from portfolio tiers
  const likelyAwards = (portfolio.likely as Record<string, unknown>[]) || [];
  const targetAwards = (portfolio.target as Record<string, unknown>[]) || [];
  const stretchAwards = (portfolio.stretch as Record<string, unknown>[]) || [];
  const expectedWins = (portfolio.expected_wins as number) || 0;
  const strategyNotes = (portfolio.strategy_notes as string[]) || [];

  // Render an award item
  const renderAwardItem = (award: Record<string, unknown>, tierColor: string, tierBg: string) => {
    const fitReasons = (award.fit_reasons as string[]) || [];
    return (
      <div
        key={award.name as string || award.award_id as string}
        className="p-3 rounded-lg border"
        style={{ borderColor: BRAND_COLORS.borderLight, backgroundColor: tierBg }}
      >
        <div className="flex items-center justify-between mb-1">
          <h4 className="font-medium text-sm" style={{ color: BRAND_COLORS.textHeading }}>
            {award.name as string}
          </h4>
          {award.win_probability !== undefined && (
            <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: tierColor, color: '#fff' }}>
              {Math.round((award.win_probability as number) * 100)}% prob
            </span>
          )}
        </div>
        {/* Category and Level */}
        {(award.category || award.level) && (
          <div className="flex items-center gap-2 mb-1">
            {award.category && (
              <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: BRAND_COLORS.bgSecondary, color: BRAND_COLORS.textMuted }}>
                {award.category as string}
              </span>
            )}
            {award.level && (
              <span className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>
                {award.level as string}
              </span>
            )}
          </div>
        )}
        {/* Fit Reasons */}
        {fitReasons.length > 0 && (
          <p className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>
            {fitReasons.slice(0, 2).join(' • ')}
          </p>
        )}
        {/* Metadata row */}
        <div className="flex items-center gap-3 mt-2 text-xs" style={{ color: BRAND_COLORS.textMuted }}>
          {award.deadline && (
            <span className="flex items-center gap-1">
              <Clock size={10} />
              {award.deadline as string}
            </span>
          )}
          {award.effort_hours && (
            <span>{award.effort_hours}h effort</span>
          )}
          {award.roi !== undefined && (
            <span>ROI: {(award.roi as number).toFixed(1)}</span>
          )}
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
            <p className="text-3xl font-bold" style={{ color: BRAND_COLORS.success }}>{likelyAwards.length}</p>
            <p className="text-sm" style={{ color: BRAND_COLORS.textMuted }}>Likely</p>
          </div>
          <div className="text-center p-4 rounded-lg" style={{ backgroundColor: BRAND_COLORS.bgWarning }}>
            <p className="text-3xl font-bold" style={{ color: BRAND_COLORS.warning }}>{targetAwards.length}</p>
            <p className="text-sm" style={{ color: BRAND_COLORS.textMuted }}>Target</p>
          </div>
          <div className="text-center p-4 rounded-lg" style={{ backgroundColor: BRAND_COLORS.primaryBg }}>
            <p className="text-3xl font-bold" style={{ color: BRAND_COLORS.primary }}>{stretchAwards.length}</p>
            <p className="text-sm" style={{ color: BRAND_COLORS.textMuted }}>Stretch</p>
          </div>
        </div>
        {expectedWins > 0 && (
          <div className="text-center p-3 rounded-lg" style={{ backgroundColor: BRAND_COLORS.bgSecondary }}>
            <span style={{ color: BRAND_COLORS.textMuted }}>Expected Wins: </span>
            <span className="font-bold" style={{ color: BRAND_COLORS.success }}>{expectedWins.toFixed(1)}</span>
          </div>
        )}
      </Section>

      {/* Likely Awards */}
      {likelyAwards.length > 0 && (
        <Section title="Likely Awards (High Win Probability)" icon={<CheckCircle2 size={20} style={{ color: BRAND_COLORS.success }} />}>
          <div className="space-y-2">
            {likelyAwards.map((award) => renderAwardItem(award, BRAND_COLORS.success, `${BRAND_COLORS.bgSuccess}40`))}
          </div>
        </Section>
      )}

      {/* Target Awards */}
      {targetAwards.length > 0 && (
        <Section title="Target Awards (Competitive)" icon={<Target size={20} style={{ color: BRAND_COLORS.warning }} />}>
          <div className="space-y-2">
            {targetAwards.map((award) => renderAwardItem(award, BRAND_COLORS.warning, `${BRAND_COLORS.bgWarning}40`))}
          </div>
        </Section>
      )}

      {/* Stretch Awards */}
      {stretchAwards.length > 0 && (
        <Section title="Stretch Awards (High Prestige)" icon={<TrendingUp size={20} style={{ color: BRAND_COLORS.primary }} />}>
          <div className="space-y-2">
            {stretchAwards.map((award) => renderAwardItem(award, BRAND_COLORS.primary, `${BRAND_COLORS.primaryBg}40`))}
          </div>
        </Section>
      )}

      {/* Strategy Notes */}
      {strategyNotes.length > 0 && (
        <Section title="Strategy Notes" icon={<Brain size={20} />}>
          <ul className="space-y-2">
            {strategyNotes.map((note, i) => (
              <li key={i} className="flex items-start gap-2 text-sm" style={{ color: BRAND_COLORS.textSecondary }}>
                <span style={{ color: BRAND_COLORS.primary }}>•</span>
                {note}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Fallback: Show matches if portfolio tiers are empty */}
      {matches.length > 0 && likelyAwards.length === 0 && targetAwards.length === 0 && stretchAwards.length === 0 && (
        <Section title="Recommended Awards" icon={<Target size={20} />}>
          <div className="space-y-3">
            {matches.map((match, i) => (
              <div
                key={i}
                className="p-4 rounded-lg border"
                style={{ borderColor: BRAND_COLORS.borderLight }}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold" style={{ color: BRAND_COLORS.textHeading }}>
                    {match.name as string || match.award_name as string}
                  </h4>
                  <span
                    className="px-2 py-0.5 rounded-full text-xs"
                    style={{
                      backgroundColor:
                        (match.fit_score as number) >= 0.8
                          ? BRAND_COLORS.bgSuccess
                          : (match.fit_score as number) >= 0.6
                          ? BRAND_COLORS.bgWarning
                          : BRAND_COLORS.bgError,
                      color: BRAND_COLORS.textPrimary,
                    }}
                  >
                    {Math.round((match.fit_score as number || 0) * 100)}% fit
                  </span>
                </div>
                <p className="text-sm" style={{ color: BRAND_COLORS.textMuted }}>
                  {match.description as string || match.rationale as string}
                </p>
                {match.deadline && (
                  <div className="flex items-center gap-1 mt-2 text-xs" style={{ color: BRAND_COLORS.textMuted }}>
                    <Clock size={12} />
                    Deadline: {match.deadline as string}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}

// ============================================================
// OPPORTUNITY DETAIL VIEW
// ============================================================
function OpportunityDetail({ data }: { data: Record<string, unknown> }) {
  const matches = (data.matches as Record<string, unknown>[]) || [];
  const alerts = (data.alerts as Record<string, unknown>[]) || [];
  const urgentCount = (data.urgent_count as number) || 0;

  return (
    <div className="space-y-6">
      {/* Alerts */}
      {urgentCount > 0 && (
        <Section title="Urgent Deadlines" icon={<AlertTriangle size={20} />}>
          <div className="space-y-3">
            {alerts.filter(a => a.urgent).map((alert, i) => (
              <div
                key={i}
                className="p-4 rounded-lg"
                style={{ backgroundColor: BRAND_COLORS.errorBg }}
              >
                <h4 className="font-semibold" style={{ color: BRAND_COLORS.error }}>
                  {alert.title as string}
                </h4>
                <p className="text-sm mt-1" style={{ color: BRAND_COLORS.textPrimary }}>
                  {alert.message as string}
                </p>
                {alert.deadline && (
                  <div className="flex items-center gap-1 mt-2 text-xs" style={{ color: BRAND_COLORS.error }}>
                    <Clock size={12} />
                    Due: {alert.deadline as string}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Opportunity Matches */}
      {matches.length > 0 && (
        <Section title="Matched Opportunities" icon={<Lightbulb size={20} />}>
          <div className="space-y-3">
            {matches.map((match, i) => (
              <div
                key={i}
                className="p-4 rounded-lg border"
                style={{ borderColor: BRAND_COLORS.borderLight }}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold" style={{ color: BRAND_COLORS.textHeading }}>
                    {match.name as string || match.opportunity_name as string}
                  </h4>
                  <span
                    className="px-2 py-0.5 rounded-full text-xs"
                    style={{
                      backgroundColor: BRAND_COLORS.primaryBg,
                      color: BRAND_COLORS.primary,
                    }}
                  >
                    {match.type as string || 'Opportunity'}
                  </span>
                </div>
                <p className="text-sm" style={{ color: BRAND_COLORS.textMuted }}>
                  {match.description as string || match.rationale as string}
                </p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {matches.length === 0 && alerts.length === 0 && (
        <div className="text-center py-8">
          <Lightbulb size={48} style={{ color: BRAND_COLORS.textMuted }} className="mx-auto mb-3" />
          <p className="text-lg font-semibold" style={{ color: BRAND_COLORS.textHeading }}>
            No Opportunities Yet
          </p>
          <p style={{ color: BRAND_COLORS.textMuted }}>
            Keep exploring - new opportunities will be matched based on your profile
          </p>
        </div>
      )}
    </div>
  );
}

// ============================================================
// CRISIS DETAIL VIEW
// ============================================================
function CrisisDetail({ data }: { data: Record<string, unknown> }) {
  const activeCrises = (data.active_crises as Record<string, unknown>[]) || [];
  const resolvedCrises = (data.resolved_crises as Record<string, unknown>[]) || [];

  return (
    <div className="space-y-6">
      {/* Active Crises */}
      {activeCrises.length > 0 && (
        <Section title="Active Crises" icon={<AlertTriangle size={20} />}>
          <div className="space-y-3">
            {activeCrises.map((crisis, i) => (
              <div
                key={i}
                className="p-4 rounded-lg"
                style={{ backgroundColor: BRAND_COLORS.errorBg }}
              >
                <h4 className="font-semibold" style={{ color: BRAND_COLORS.error }}>
                  {crisis.type as string}
                </h4>
                <p className="text-sm mt-1" style={{ color: BRAND_COLORS.textPrimary }}>
                  {crisis.description as string}
                </p>
                {crisis.varc_response && (
                  <div className="mt-3 p-3 rounded bg-white">
                    <p className="text-sm font-medium" style={{ color: BRAND_COLORS.textHeading }}>
                      VARC Response
                    </p>
                    <p className="text-sm" style={{ color: BRAND_COLORS.textMuted }}>
                      {crisis.varc_response as string}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {activeCrises.length === 0 && (
        <div className="text-center py-8">
          <CheckCircle2 size={48} style={{ color: BRAND_COLORS.success }} className="mx-auto mb-3" />
          <p className="text-lg font-semibold" style={{ color: BRAND_COLORS.textHeading }}>
            No Active Crises
          </p>
          <p style={{ color: BRAND_COLORS.textMuted }}>
            Everything is on track. Report a crisis if you need support.
          </p>
        </div>
      )}

      {/* VARC Framework Info */}
      <Section title="VARC Framework" icon={<Brain size={20} />}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-3 rounded-lg text-center" style={{ backgroundColor: BRAND_COLORS.bgSecondary }}>
            <p className="font-bold" style={{ color: BRAND_COLORS.primary }}>V</p>
            <p className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>Validate</p>
          </div>
          <div className="p-3 rounded-lg text-center" style={{ backgroundColor: BRAND_COLORS.bgSecondary }}>
            <p className="font-bold" style={{ color: BRAND_COLORS.primary }}>A</p>
            <p className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>Act</p>
          </div>
          <div className="p-3 rounded-lg text-center" style={{ backgroundColor: BRAND_COLORS.bgSecondary }}>
            <p className="font-bold" style={{ color: BRAND_COLORS.primary }}>R</p>
            <p className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>Reframe</p>
          </div>
          <div className="p-3 rounded-lg text-center" style={{ backgroundColor: BRAND_COLORS.bgSecondary }}>
            <p className="font-bold" style={{ color: BRAND_COLORS.primary }}>C</p>
            <p className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>Create</p>
          </div>
        </div>
      </Section>
    </div>
  );
}

// ============================================================
// HELPER COMPONENTS
// ============================================================
function Section({ title, icon, children }: { title: string; icon: ReactNode; children: ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <span style={{ color: BRAND_COLORS.primary }}>{icon}</span>
        <h3 className="text-lg font-semibold" style={{ color: BRAND_COLORS.textHeading }}>
          {title}
        </h3>
      </div>
      {children}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="p-4 rounded-lg text-center" style={{ backgroundColor: BRAND_COLORS.bgSecondary }}>
      <p className="text-2xl font-bold" style={{ color: BRAND_COLORS.textHeading }}>{value}</p>
      <p className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>{label}</p>
    </div>
  );
}

export default AgentDetailModal;
