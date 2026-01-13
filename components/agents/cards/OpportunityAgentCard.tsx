/**
 * OpportunityAgentCard Component
 * v13.4 - Added strategic fit from Programs Agent
 */
'use client';

import { Lightbulb, AlertTriangle, Calendar, TrendingUp, Star } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { useOpportunityMatches, useOpportunityAlerts } from '@/hooks/useAgentData';
import { useResultsStore } from '@/lib/store/useResultsStore';
import { AgentCardBase } from './AgentCardBase';

interface OpportunityAgentCardProps {
  profileId: string;
  onChat?: () => void;
  onViewDetails?: (data: Record<string, unknown>) => void;
}

export function OpportunityAgentCard({ profileId, onChat, onViewDetails }: OpportunityAgentCardProps) {
  const { data: matchData, isLoading: matchLoading, isError: matchError, refetch: refetchMatch } = useOpportunityMatches(profileId);
  const { data: alertsData, isLoading: alertsLoading, refetch: refetchAlerts } = useOpportunityAlerts(profileId);
  const programs_portfolio = useResultsStore((state) => state.programs_portfolio);

  const isLoading = matchLoading || alertsLoading;
  const isError = matchError;
  const hasStrategicPrograms = programs_portfolio && (programs_portfolio.primary?.length > 0 || programs_portfolio.alternatives?.length > 0);

  const handleRefresh = () => {
    refetchMatch();
    refetchAlerts();
  };

  const handleClick = () => {
    if (onViewDetails && (matchData || alertsData)) {
      onViewDetails({ matches: matchData?.matches || [], alerts: alertsData?.alerts || [], urgent_count: alertsData?.urgent_count || 0 } as Record<string, unknown>);
    }
  };

  // Get data
  const matchCount = matchData?.matches?.length || 0;
  const urgentCount = alertsData?.urgent_count || 0;
  const alertCount = alertsData?.count || alertsData?.alerts?.length || 0;

  // Get upcoming deadlines
  const upcomingAlerts = alertsData?.alerts?.slice(0, 2) || [];

  return (
    <AgentCardBase
      title="Opportunity Agent"
      icon={<Lightbulb size={20} style={{ color: BRAND_COLORS.primary }} />}
      isLoading={isLoading}
      isError={isError}
      onRefresh={handleRefresh}
      onChat={onChat}
      onClick={handleClick}
      headerBadge={
        urgentCount > 0 && (
          <span
            className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full mt-1"
            style={{
              backgroundColor: BRAND_COLORS.bgError,
              color: BRAND_COLORS.error,
            }}
          >
            <AlertTriangle size={12} />
            {urgentCount} urgent
          </span>
        )
      }
    >
      <div className="space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-2 gap-3">
          {/* Matches */}
          <div
            className="p-3 rounded-lg text-center"
            style={{ backgroundColor: BRAND_COLORS.primaryBg }}
          >
            <TrendingUp size={16} style={{ color: BRAND_COLORS.primary }} className="mx-auto mb-1" />
            <div
              className="text-2xl font-bold"
              style={{ color: BRAND_COLORS.primary }}
            >
              {matchCount}
            </div>
            <div className="text-xs" style={{ color: BRAND_COLORS.primary }}>
              Matches
            </div>
          </div>

          {/* Alerts */}
          <div
            className="p-3 rounded-lg text-center"
            style={{
              backgroundColor: alertCount > 0 ? BRAND_COLORS.bgWarning : BRAND_COLORS.bgSecondary,
            }}
          >
            <Calendar
              size={16}
              style={{ color: alertCount > 0 ? BRAND_COLORS.warning : BRAND_COLORS.textMuted }}
              className="mx-auto mb-1"
            />
            <div
              className="text-2xl font-bold"
              style={{ color: alertCount > 0 ? BRAND_COLORS.warning : BRAND_COLORS.textMuted }}
            >
              {alertCount}
            </div>
            <div
              className="text-xs"
              style={{ color: alertCount > 0 ? BRAND_COLORS.warning : BRAND_COLORS.textMuted }}
            >
              Deadlines
            </div>
          </div>
        </div>

        {/* Upcoming Alerts */}
        {upcomingAlerts.length > 0 ? (
          <div className="space-y-2">
            <p className="text-xs font-medium" style={{ color: BRAND_COLORS.textMuted }}>
              Upcoming Deadlines
            </p>
            {upcomingAlerts.map((alert, i) => (
              <div
                key={i}
                className="p-2 rounded-lg flex items-start gap-2"
                style={{
                  backgroundColor:
                    alert.urgency === 'URGENT' ? BRAND_COLORS.bgError : BRAND_COLORS.bgWarning,
                }}
              >
                <AlertTriangle
                  size={14}
                  style={{
                    color:
                      alert.urgency === 'URGENT' ? BRAND_COLORS.error : BRAND_COLORS.warning,
                  }}
                  className="flex-shrink-0 mt-0.5"
                />
                <div className="flex-1 min-w-0">
                  <p
                    className="text-sm font-medium line-clamp-1"
                    style={{ color: BRAND_COLORS.textHeading }}
                  >
                    {alert.opportunity_name}
                  </p>
                  <p className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>
                    {alert.months_remaining <= 1
                      ? `Due: ${alert.deadline}`
                      : `${alert.months_remaining} months`}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div
            className="p-3 rounded-lg text-center"
            style={{ backgroundColor: BRAND_COLORS.bgSecondary }}
          >
            <p className="text-sm" style={{ color: BRAND_COLORS.textMuted }}>
              No urgent deadlines
            </p>
            <p className="text-xs mt-1" style={{ color: BRAND_COLORS.textMuted }}>
              Keep exploring opportunities!
            </p>
          </div>
        )}

        {/* Strategic Programs (v1.1.0) */}
        {hasStrategicPrograms && programs_portfolio?.primary && programs_portfolio.primary.length > 0 && (
          <div className="space-y-2 pt-2 border-t" style={{ borderColor: BRAND_COLORS.borderLight }}>
            <p className="text-xs font-medium" style={{ color: BRAND_COLORS.textMuted }}>
              Top Programs
            </p>
            {programs_portfolio.primary.slice(0, 2).map((program, i) => (
              <div
                key={i}
                className="p-2 rounded-lg flex items-start justify-between"
                style={{ backgroundColor: BRAND_COLORS.bgSuccess }}
              >
                <div className="flex-1 min-w-0">
                  <p
                    className="text-sm font-medium line-clamp-1"
                    style={{ color: BRAND_COLORS.textHeading }}
                  >
                    {program.name}
                  </p>
                  <p className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>
                    {program.organization}
                  </p>
                </div>
                <div className="text-right flex-shrink-0 ml-2">
                  <span
                    className="text-xs font-medium"
                    style={{ color: BRAND_COLORS.success }}
                  >
                    {Math.round(program.fit_score * 100)}%
                  </span>
                  <p className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>
                    fit
                  </p>
                </div>
              </div>
            ))}
            {/* Hidden Value Teaser */}
            {programs_portfolio.primary[0]?.hidden_value?.[0] && (
              <div className="flex items-start gap-1 text-xs" style={{ color: BRAND_COLORS.info }}>
                <Star size={12} className="flex-shrink-0 mt-0.5" />
                <span className="line-clamp-1">{programs_portfolio.primary[0].hidden_value[0]}</span>
              </div>
            )}
          </div>
        )}

        {/* Top Match Preview (Legacy) */}
        {!hasStrategicPrograms && matchData?.matches?.[0] && (
          <div className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>
            Top match: <span style={{ color: BRAND_COLORS.textPrimary }}>{matchData.matches[0].name}</span>
            {' '}({Math.round(matchData.matches[0].fit_score * 100)}% fit)
          </div>
        )}
      </div>
    </AgentCardBase>
  );
}

export default OpportunityAgentCard;
