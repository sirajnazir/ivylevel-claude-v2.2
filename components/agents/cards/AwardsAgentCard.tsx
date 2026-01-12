/**
 * AwardsAgentCard Component
 * v13.3 - Displays award matches from Awards Agent (Likely/Target/Stretch)
 */
'use client';

import { Award, Trophy, Target, Star } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { useAwardMatches, useAwardPortfolio } from '@/hooks/useAgentData';
import { AgentCardBase } from './AgentCardBase';

interface AwardsAgentCardProps {
  profileId: string;
  onChat?: () => void;
  onViewDetails?: (data: Record<string, unknown>) => void;
}

export function AwardsAgentCard({ profileId, onChat, onViewDetails }: AwardsAgentCardProps) {
  const { data: matchData, isLoading: matchLoading, isError: matchError, refetch } = useAwardMatches(profileId);
  const { data: portfolioData, isLoading: portfolioLoading } = useAwardPortfolio(profileId);

  const isLoading = matchLoading || portfolioLoading;
  const isError = matchError;

  // Get portfolio data
  const portfolio = portfolioData?.portfolio || matchData?.portfolio;

  const handleClick = () => {
    if (onViewDetails && (matchData || portfolioData)) {
      onViewDetails({ matches: matchData?.matches || [], portfolio, ...matchData } as unknown as Record<string, unknown>);
    }
  };
  const likelyCount = portfolio?.likely?.length || 0;
  const targetCount = portfolio?.target?.length || 0;
  const stretchCount = portfolio?.stretch?.length || 0;
  const expectedWins = portfolio?.expected_wins || 0;

  return (
    <AgentCardBase
      title="Awards Agent"
      icon={<Award size={20} style={{ color: BRAND_COLORS.primary }} />}
      isLoading={isLoading}
      isError={isError}
      onRefresh={() => refetch()}
      onChat={onChat}
      onClick={handleClick}
    >
      <div className="space-y-4">
        {/* Award Tiers */}
        <div className="grid grid-cols-3 gap-2">
          {/* Likely */}
          <div
            className="p-3 rounded-lg text-center"
            style={{ backgroundColor: BRAND_COLORS.bgSuccess }}
          >
            <Trophy size={16} style={{ color: BRAND_COLORS.success }} className="mx-auto mb-1" />
            <div
              className="text-xl font-bold"
              style={{ color: BRAND_COLORS.success }}
            >
              {likelyCount}
            </div>
            <div className="text-xs" style={{ color: BRAND_COLORS.success }}>
              Likely
            </div>
          </div>

          {/* Target */}
          <div
            className="p-3 rounded-lg text-center"
            style={{ backgroundColor: BRAND_COLORS.bgWarning }}
          >
            <Target size={16} style={{ color: BRAND_COLORS.warning }} className="mx-auto mb-1" />
            <div
              className="text-xl font-bold"
              style={{ color: BRAND_COLORS.warning }}
            >
              {targetCount}
            </div>
            <div className="text-xs" style={{ color: BRAND_COLORS.warning }}>
              Target
            </div>
          </div>

          {/* Stretch */}
          <div
            className="p-3 rounded-lg text-center"
            style={{ backgroundColor: BRAND_COLORS.primaryBg }}
          >
            <Star size={16} style={{ color: BRAND_COLORS.primary }} className="mx-auto mb-1" />
            <div
              className="text-xl font-bold"
              style={{ color: BRAND_COLORS.primary }}
            >
              {stretchCount}
            </div>
            <div className="text-xs" style={{ color: BRAND_COLORS.primary }}>
              Stretch
            </div>
          </div>
        </div>

        {/* Expected Wins */}
        <div
          className="p-3 rounded-lg"
          style={{
            backgroundColor: BRAND_COLORS.bgSecondary,
            border: `1px solid ${BRAND_COLORS.borderLight}`,
          }}
        >
          <div className="flex items-center justify-between">
            <span style={{ color: BRAND_COLORS.textMuted }} className="text-sm">
              Expected Wins
            </span>
            <span
              className="text-lg font-bold"
              style={{ color: BRAND_COLORS.success }}
            >
              {expectedWins.toFixed(1)}
            </span>
          </div>
          <p className="text-xs mt-1" style={{ color: BRAND_COLORS.textMuted }}>
            Based on probability analysis
          </p>
        </div>

        {/* Strategy Notes */}
        {portfolio?.strategy_notes && portfolio.strategy_notes.length > 0 && (
          <div>
            <p className="text-xs mb-1" style={{ color: BRAND_COLORS.textMuted }}>
              Strategy Tip
            </p>
            <p className="text-sm" style={{ color: BRAND_COLORS.textSecondary }}>
              {portfolio.strategy_notes[0]}
            </p>
          </div>
        )}

        {/* Total Recommended */}
        <div className="text-xs text-center" style={{ color: BRAND_COLORS.textMuted }}>
          {portfolio?.total_recommended || likelyCount + targetCount + stretchCount} awards recommended •
          {portfolio?.total_effort_hours || 0} total hours
        </div>
      </div>
    </AgentCardBase>
  );
}

export default AwardsAgentCard;
