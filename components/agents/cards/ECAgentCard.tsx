/**
 * ECAgentCard Component
 * v4.0 - Displays Extracurricular Activities from game plan orchestration
 *
 * Specializes in:
 * - Listing and categorizing activities
 * - Showing activity portfolio balance
 * - Displaying activity recommendations
 */
'use client';

import { Activity, Briefcase, Heart, Users, Lightbulb, ChevronRight } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { useGamePlan } from '@/hooks/useAgentData';
import { AgentCardBase } from './AgentCardBase';

interface ECAgentCardProps {
  profileId: string;
  onChat?: () => void;
  onViewDetails?: (data: Record<string, unknown>) => void;
}

// Activity type icons
const ACTIVITY_ICONS: Record<string, React.ReactNode> = {
  academic: <Briefcase size={14} />,
  service: <Heart size={14} />,
  leadership: <Users size={14} />,
  creative: <Lightbulb size={14} />,
  default: <Activity size={14} />,
};

export function ECAgentCard({ profileId, onChat, onViewDetails }: ECAgentCardProps) {
  const { data: gamePlan, isLoading, isError, refetch } = useGamePlan(profileId);

  // v5.0: Extract EC Generation Engine data (proper EC activities like signature projects, leadership, etc.)
  const ecGeneration = (gamePlan?.game_plan?.ec_generation as Record<string, unknown>) || {};
  const ecEngineActivities = (ecGeneration.recommended_activities as Array<{
    name?: string;
    title?: string;
    activity_type?: string;
    description?: string;
  }>) || [];

  // Fallback to game_plan activities if no EC Engine activities
  const gamePlanActivities = (gamePlan?.game_plan?.activities as Array<{
    name?: string;
    type?: string;
    category?: string;
    description?: string;
    touchpoints?: string[];
  }>) || [];

  // Use EC Engine activities if available, otherwise use game plan activities (filtered)
  // Filter out awards/programs from gamePlan activities (they come from other agents)
  const filteredGamePlanActivities = gamePlanActivities.filter(a => {
    const cat = (a.category || a.type || '').toLowerCase();
    return !['award', 'program', 'awards', 'programs'].includes(cat);
  });

  // Prefer EC Engine activities (signature projects, leadership, etc.)
  const activities = ecEngineActivities.length > 0
    ? ecEngineActivities.map(a => ({ name: a.title || a.name, type: a.activity_type, ...a }))
    : filteredGamePlanActivities;

  // Get identity seeds that relate to activities
  const seeds = (gamePlan?.game_plan?.identity_seeds as Array<{
    name?: string;
    type?: string;
    planted?: boolean;
  }>) || [];

  // v5.0: Get identity synthesis for spike, archetype, pillars
  const identitySynthesis = (gamePlan?.game_plan?.identity_synthesis as Record<string, unknown>) || {};

  // Categorize activities
  const categorizedActivities = activities.reduce((acc, act) => {
    const category = act.category || act.type || 'other';
    if (!acc[category]) acc[category] = [];
    acc[category].push(act);
    return acc;
  }, {} as Record<string, typeof activities>);

  const categories = Object.keys(categorizedActivities);
  const plantedSeeds = seeds.filter(s => s.planted).length;

  const handleClick = () => {
    if (onViewDetails) {
      // v5.0: Get EC-specific ReAct data from _react_by_agent or identity_synthesis._react
      const ecReact =
        (gamePlan as Record<string, unknown>)?._react_by_agent?.ec ||
        gamePlan?.game_plan?.identity_synthesis?._react ||
        gamePlan?.game_plan?._react;

      onViewDetails({
        activities,
        identity_seeds: seeds,
        categories: categorizedActivities,
        total_activities: activities.length,
        planted_seeds: plantedSeeds,
        // v5.0: Include EC Generation Engine data (4 pillars, recommended activities, etc.)
        ec_generation: ecGeneration,
        // v5.0: Include identity synthesis (spike, archetype, pillars)
        identity_synthesis: identitySynthesis,
        spike: identitySynthesis.spike,
        archetype: identitySynthesis.archetype,
        pillars: identitySynthesis.pillars,
        // v5.0: Include EC-specific ReAct metadata for cycle visualization
        _react: ecReact,
      } as Record<string, unknown>);
    }
  };

  const hasData = activities.length > 0;

  return (
    <AgentCardBase
      title="EC Agent"
      icon={<Activity size={20} style={{ color: BRAND_COLORS.primary }} />}
      isLoading={isLoading}
      isError={isError}
      onRefresh={() => refetch()}
      onChat={onChat}
      onClick={handleClick}
    >
      {hasData ? (
        <div className="space-y-3">
          {/* Activity Stats */}
          <div className="grid grid-cols-2 gap-2">
            <div
              className="p-3 rounded-lg text-center"
              style={{ backgroundColor: BRAND_COLORS.primaryBg }}
            >
              <div
                className="text-2xl font-bold"
                style={{ color: BRAND_COLORS.primary }}
              >
                {activities.length}
              </div>
              <div className="text-xs" style={{ color: BRAND_COLORS.primary }}>
                Activities
              </div>
            </div>
            <div
              className="p-3 rounded-lg text-center"
              style={{ backgroundColor: BRAND_COLORS.bgSuccess }}
            >
              <div
                className="text-2xl font-bold"
                style={{ color: BRAND_COLORS.success }}
              >
                {plantedSeeds}
              </div>
              <div className="text-xs" style={{ color: BRAND_COLORS.success }}>
                Seeds Planted
              </div>
            </div>
          </div>

          {/* Activity Categories */}
          {categories.length > 0 && (
            <div
              className="p-3 rounded-lg"
              style={{
                backgroundColor: BRAND_COLORS.bgSecondary,
                border: `1px solid ${BRAND_COLORS.borderLight}`,
              }}
            >
              <p
                className="text-xs font-medium mb-2"
                style={{ color: BRAND_COLORS.textMuted }}
              >
                Activity Categories
              </p>
              <div className="space-y-1.5">
                {categories.slice(0, 4).map((category) => (
                  <div
                    key={category}
                    className="flex items-center justify-between text-sm"
                  >
                    <div className="flex items-center gap-2">
                      <span style={{ color: BRAND_COLORS.primary }}>
                        {ACTIVITY_ICONS[category.toLowerCase()] || ACTIVITY_ICONS.default}
                      </span>
                      <span style={{ color: BRAND_COLORS.textPrimary }}>
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </span>
                    </div>
                    <span
                      className="px-2 py-0.5 rounded-full text-xs font-medium"
                      style={{
                        backgroundColor: BRAND_COLORS.primaryBg,
                        color: BRAND_COLORS.primary,
                      }}
                    >
                      {categorizedActivities[category].length}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Top Activities Preview */}
          {activities.length > 0 && (
            <div className="space-y-1.5">
              <p
                className="text-xs font-medium"
                style={{ color: BRAND_COLORS.textMuted }}
              >
                Recommended Activities
              </p>
              {activities.slice(0, 2).map((activity, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 text-sm"
                  style={{ color: BRAND_COLORS.textPrimary }}
                >
                  <ChevronRight
                    size={14}
                    style={{ color: BRAND_COLORS.primary }}
                    className="mt-0.5 flex-shrink-0"
                  />
                  <span className="line-clamp-1">{activity.name}</span>
                </div>
              ))}
            </div>
          )}

          {/* Summary */}
          <div
            className="text-xs text-center"
            style={{ color: BRAND_COLORS.textMuted }}
          >
            {categories.length} categories • Click for details
          </div>
        </div>
      ) : (
        <div className="text-center py-4">
          <p style={{ color: BRAND_COLORS.textMuted }} className="text-sm">
            Loading activity recommendations...
          </p>
        </div>
      )}
    </AgentCardBase>
  );
}

export default ECAgentCard;
