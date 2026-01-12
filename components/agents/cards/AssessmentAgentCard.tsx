/**
 * AssessmentAgentCard Component
 * v13.3 - Displays Narrative DNA and Archetype from Assessment Agent
 */
'use client';

import { Brain } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { useNarrativeDNA } from '@/hooks/useAgentData';
import { AgentCardBase } from './AgentCardBase';

interface AssessmentAgentCardProps {
  profileId: string;
  onChat?: () => void;
  onViewDetails?: (data: Record<string, unknown>) => void;
}

export function AssessmentAgentCard({ profileId, onChat, onViewDetails }: AssessmentAgentCardProps) {
  const { data, isLoading, isError, refetch } = useNarrativeDNA(profileId);

  const handleClick = () => {
    if (onViewDetails && data) {
      onViewDetails(data as unknown as Record<string, unknown>);
    }
  };

  return (
    <AgentCardBase
      title="Assessment Agent"
      icon={<Brain size={20} style={{ color: BRAND_COLORS.primary }} />}
      isLoading={isLoading}
      isError={isError}
      onRefresh={() => refetch()}
      onChat={onChat}
      onClick={handleClick}
    >
      {data && (
        <div className="space-y-3">
          {/* Narrative DNA */}
          <div>
            <p
              style={{ color: BRAND_COLORS.textMuted }}
              className="text-xs uppercase tracking-wide mb-1"
            >
              Narrative DNA
            </p>
            <p
              style={{ color: BRAND_COLORS.textPrimary }}
              className="text-sm italic line-clamp-2"
            >
              "{data.dna || 'Generating your unique narrative...'}"
            </p>
          </div>

          {/* Themes */}
          {data.themes && data.themes.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {data.themes.slice(0, 3).map((theme, i) => (
                <span
                  key={i}
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{
                    backgroundColor: BRAND_COLORS.primaryBg,
                    color: BRAND_COLORS.primary,
                  }}
                >
                  {theme}
                </span>
              ))}
            </div>
          )}

          {/* Confidence */}
          <div className="flex items-center justify-between">
            <span style={{ color: BRAND_COLORS.textMuted }} className="text-sm">
              Confidence
            </span>
            <div className="flex items-center gap-2">
              <div className="w-20 h-2 rounded-full bg-gray-200">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${(data.confidence || 0) * 100}%`,
                    backgroundColor:
                      data.confidence >= 0.8
                        ? BRAND_COLORS.success
                        : data.confidence >= 0.6
                        ? BRAND_COLORS.warning
                        : BRAND_COLORS.error,
                  }}
                />
              </div>
              <span style={{ color: BRAND_COLORS.textPrimary }} className="text-sm font-medium">
                {Math.round((data.confidence || 0) * 100)}%
              </span>
            </div>
          </div>
        </div>
      )}
    </AgentCardBase>
  );
}

export default AssessmentAgentCard;
