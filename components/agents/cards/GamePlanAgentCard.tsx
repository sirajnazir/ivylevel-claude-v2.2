/**
 * GamePlanAgentCard Component
 * v13.3 - Displays activities, seeds, and phases from GamePlan Agent
 */
'use client';

import { Target, Calendar, Sprout } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { useGamePlan, useFilteredActivities, useIdentitySeeds } from '@/hooks/useAgentData';
import { AgentCardBase } from './AgentCardBase';

interface GamePlanAgentCardProps {
  profileId: string;
  onChat?: () => void;
  onViewDetails?: (data: Record<string, unknown>) => void;
}

export function GamePlanAgentCard({ profileId, onChat, onViewDetails }: GamePlanAgentCardProps) {
  const { data: gamePlan, isLoading: planLoading, isError: planError, refetch: refetchPlan } = useGamePlan(profileId);
  const { data: activities, isLoading: activitiesLoading } = useFilteredActivities(profileId);
  const { data: seeds, isLoading: seedsLoading } = useIdentitySeeds(profileId);

  const isLoading = planLoading || activitiesLoading || seedsLoading;
  const isError = planError;

  const handleRefresh = () => {
    refetchPlan();
  };

  const handleClick = () => {
    if (onViewDetails && gamePlan) {
      onViewDetails(gamePlan as unknown as Record<string, unknown>);
    }
  };

  // Extract counts from data
  const activityCount = gamePlan?.game_plan?.activities?.length || activities?.activities?.length || 0;
  const seedCount = gamePlan?.game_plan?.identity_seeds?.length || seeds?.seeds?.length || 0;
  const phaseCount = gamePlan?.game_plan?.phases?.length || 3;

  return (
    <AgentCardBase
      title="Game Plan Agent"
      icon={<Target size={20} style={{ color: BRAND_COLORS.primary }} />}
      isLoading={isLoading}
      isError={isError}
      onRefresh={handleRefresh}
      onChat={onChat}
      onClick={handleClick}
    >
      <div className="space-y-4">
        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-3">
          {/* Activities */}
          <div
            className="p-3 rounded-lg text-center"
            style={{ backgroundColor: BRAND_COLORS.bgSecondary }}
          >
            <div
              className="text-2xl font-bold"
              style={{ color: BRAND_COLORS.textHeading }}
            >
              {activityCount}
            </div>
            <div className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>
              Activities
            </div>
          </div>

          {/* Seeds */}
          <div
            className="p-3 rounded-lg text-center"
            style={{ backgroundColor: BRAND_COLORS.bgSecondary }}
          >
            <div className="flex items-center justify-center mb-1">
              <Sprout size={16} style={{ color: BRAND_COLORS.success }} />
            </div>
            <div
              className="text-2xl font-bold"
              style={{ color: BRAND_COLORS.textHeading }}
            >
              {seedCount}
            </div>
            <div className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>
              Seeds
            </div>
          </div>

          {/* Phases */}
          <div
            className="p-3 rounded-lg text-center"
            style={{ backgroundColor: BRAND_COLORS.bgSecondary }}
          >
            <div className="flex items-center justify-center mb-1">
              <Calendar size={16} style={{ color: BRAND_COLORS.info }} />
            </div>
            <div
              className="text-2xl font-bold"
              style={{ color: BRAND_COLORS.textHeading }}
            >
              {phaseCount}
            </div>
            <div className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>
              Phases
            </div>
          </div>
        </div>

        {/* Current Phase */}
        {gamePlan?.game_plan?.phases?.[0] && (
          <div
            className="p-3 rounded-lg"
            style={{
              backgroundColor: BRAND_COLORS.primaryBg,
              border: `1px solid ${BRAND_COLORS.primary}20`,
            }}
          >
            <p className="text-xs font-medium" style={{ color: BRAND_COLORS.primary }}>
              Current Phase
            </p>
            <p
              className="text-sm font-semibold mt-1"
              style={{ color: BRAND_COLORS.textHeading }}
            >
              {gamePlan.game_plan.phases[0].name}
            </p>
            <p className="text-xs mt-0.5" style={{ color: BRAND_COLORS.textMuted }}>
              {gamePlan.game_plan.phases[0].duration}
            </p>
          </div>
        )}

        {/* Summary */}
        {gamePlan?.game_plan?.summary && (
          <div className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>
            {gamePlan.game_plan.summary.total_touchpoints} touchpoints •
            Avg ROI: {gamePlan.game_plan.summary.average_roi?.toFixed(1) || 'N/A'}
          </div>
        )}
      </div>
    </AgentCardBase>
  );
}

export default GamePlanAgentCard;
