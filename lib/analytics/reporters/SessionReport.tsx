/**
 * IvyQuest v3.0 — Analytics Reporter Components
 * 
 * Visual reports and charts for session analytics.
 * 
 * @version 1.0.0
 * @module reporters
 */

'use client';

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  CHART_COLORS,
  REPORT_CONFIG,
} from '../constants/analytics.constants';
import {
  formatDuration,
  formatDurationShort,
  getFrameChartData,
} from '../utils/analyticsUtils';
import { useAnalytics, useSessionMetrics } from '../context/AnalyticsContext';
import type {
  SessionReportProps,
  ProgressChartProps,
  TimeBreakdownProps,
  InsightsPanelProps,
  FrameMetrics,
} from '../types/analytics.types';

// ============================================================================
// SESSION REPORT
// ============================================================================

export const SessionReport: React.FC<SessionReportProps> = ({
  showTimeline = true,
  showScoreEvolution = true,
  showInsights = true,
  showFrameBreakdown = true,
  onExport,
}) => {
  const { getScoreHistory, getInsights, exportReport } = useAnalytics();
  const { metrics, frameMetrics } = useSessionMetrics();
  const scoreEvolution = getScoreHistory();
  const insights = getInsights();
  
  const handleExport = async (format: 'json' | 'csv' | 'pdf') => {
    const data = await exportReport(format);
    onExport?.(format);
    
    // Trigger download
    const blob = new Blob([data as string], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ivyquest-report.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Session Report</h2>
          <p className="text-white/60">
            Duration: {formatDuration(metrics.totalDuration)} • 
            {metrics.completionPercentage}% Complete
          </p>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => handleExport('json')}
            className="px-3 py-1.5 bg-white/10 rounded text-sm text-white hover:bg-white/20"
          >
            Export JSON
          </button>
          <button
            onClick={() => handleExport('csv')}
            className="px-3 py-1.5 bg-white/10 rounded text-sm text-white hover:bg-white/20"
          >
            Export CSV
          </button>
        </div>
      </div>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SummaryCard
          label="Active Time"
          value={formatDuration(metrics.activeDuration)}
          color={CHART_COLORS.primary}
        />
        <SummaryCard
          label="Frames Completed"
          value={`${metrics.framesCompleted}/6`}
          color={CHART_COLORS.success}
        />
        <SummaryCard
          label="Interactions"
          value={metrics.interactionCount.toString()}
          color={CHART_COLORS.secondary}
        />
        <SummaryCard
          label="Final Score"
          value={scoreEvolution.finalScore.toString()}
          color={CHART_COLORS.scores.ivyReady}
        />
      </div>
      
      {/* Frame Breakdown */}
      {showFrameBreakdown && (
        <div className="bg-white/5 rounded-xl p-4">
          <h3 className="text-lg font-semibold text-white mb-4">Frame Progress</h3>
          <ProgressChart data={frameMetrics} type="bar" showLabels />
        </div>
      )}
      
      {/* Time Breakdown */}
      {showTimeline && (
        <div className="bg-white/5 rounded-xl p-4">
          <h3 className="text-lg font-semibold text-white mb-4">Time Distribution</h3>
          <TimeBreakdown frameMetrics={frameMetrics} showExpected />
        </div>
      )}
      
      {/* Score Evolution */}
      {showScoreEvolution && scoreEvolution.entries.length > 0 && (
        <div className="bg-white/5 rounded-xl p-4">
          <h3 className="text-lg font-semibold text-white mb-4">Score Evolution</h3>
          <ScoreEvolutionChart data={scoreEvolution.entries} />
        </div>
      )}
      
      {/* Insights */}
      {showInsights && (
        <InsightsPanel insights={insights} />
      )}
    </div>
  );
};

// ============================================================================
// SUMMARY CARD
// ============================================================================

interface SummaryCardProps {
  label: string;
  value: string;
  color: string;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ label, value, color }) => (
  <motion.div
    className="bg-white/5 rounded-lg p-4 border-l-4"
    style={{ borderColor: color }}
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
  >
    <p className="text-white/60 text-sm">{label}</p>
    <p className="text-2xl font-bold text-white">{value}</p>
  </motion.div>
);

// ============================================================================
// PROGRESS CHART
// ============================================================================

export const ProgressChart: React.FC<ProgressChartProps> = ({
  data,
  type = 'bar',
  showLabels = true,
  interactive = true,
  height = REPORT_CONFIG.chartHeight,
  onFrameClick,
}) => {
  const chartData = useMemo(() => getFrameChartData(data), [data]);
  const maxDuration = Math.max(...chartData.map(d => d.duration), 1);
  
  if (type === 'bar') {
    return (
      <div className="space-y-3" style={{ minHeight: height }}>
        {chartData.map((frame, index) => (
          <motion.div
            key={frame.name}
            className={`flex items-center gap-3 ${interactive ? 'cursor-pointer hover:opacity-80' : ''}`}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => interactive && onFrameClick?.(index)}
          >
            {showLabels && (
              <span className="w-24 text-sm text-white/70">{frame.name}</span>
            )}
            <div className="flex-1 h-6 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{ backgroundColor: frame.color }}
                initial={{ width: 0 }}
                animate={{ width: `${(frame.duration / maxDuration) * 100}%` }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              />
            </div>
            <span className="w-12 text-sm text-white/60 text-right">
              {frame.duration}m
            </span>
          </motion.div>
        ))}
      </div>
    );
  }
  
  // Pie chart placeholder
  return (
    <div className="flex items-center justify-center" style={{ height }}>
      <p className="text-white/50">Pie chart coming soon</p>
    </div>
  );
};

// ============================================================================
// TIME BREAKDOWN
// ============================================================================

export const TimeBreakdown: React.FC<TimeBreakdownProps> = ({
  frameMetrics,
  showExpected = false,
  showComparison = false,
}) => {
  const totalTime = frameMetrics.reduce((sum, f) => sum + f.duration, 0);
  
  return (
    <div className="space-y-2">
      {frameMetrics.map((frame, index) => {
        const percentage = totalTime > 0 ? (frame.duration / totalTime) * 100 : 0;
        const color = CHART_COLORS.frames[index as keyof typeof CHART_COLORS.frames] || '#6B7280';
        
        return (
          <div key={frame.frameId} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="flex-1 text-sm text-white">{frame.frameName}</span>
            <span className="text-sm text-white/60">
              {formatDurationShort(frame.duration)}
            </span>
            <span className="text-sm text-white/40 w-12 text-right">
              {Math.round(percentage)}%
            </span>
          </div>
        );
      })}
      
      {/* Total */}
      <div className="flex items-center gap-2 pt-2 border-t border-white/10 mt-2">
        <span className="flex-1 text-sm text-white font-medium">Total</span>
        <span className="text-sm text-white">{formatDuration(totalTime)}</span>
      </div>
    </div>
  );
};

// ============================================================================
// SCORE EVOLUTION CHART
// ============================================================================

interface ScoreEvolutionChartProps {
  data: Array<{
    timestamp: number;
    scores: { ivyReady: number };
  }>;
}

const ScoreEvolutionChart: React.FC<ScoreEvolutionChartProps> = ({ data }) => {
  const maxScore = Math.max(...data.map(d => d.scores.ivyReady), 100);
  const minScore = Math.min(...data.map(d => d.scores.ivyReady), 0);
  const range = maxScore - minScore || 1;
  
  const points = data.map((entry, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = 100 - ((entry.scores.ivyReady - minScore) / range) * 100;
    return `${x},${y}`;
  }).join(' ');
  
  return (
    <div className="relative h-48">
      <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        {/* Grid lines */}
        <line x1="0" y1="25" x2="100" y2="25" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
        <line x1="0" y1="50" x2="100" y2="50" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
        <line x1="0" y1="75" x2="100" y2="75" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
        
        {/* Score line */}
        <motion.polyline
          fill="none"
          stroke={CHART_COLORS.scores.ivyReady}
          strokeWidth="2"
          points={points}
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1 }}
        />
        
        {/* Data points */}
        {data.map((entry, index) => {
          const x = (index / (data.length - 1)) * 100;
          const y = 100 - ((entry.scores.ivyReady - minScore) / range) * 100;
          
          return (
            <motion.circle
              key={index}
              cx={x}
              cy={y}
              r="1.5"
              fill={CHART_COLORS.scores.ivyReady}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 + 0.5 }}
            />
          );
        })}
      </svg>
      
      {/* Y-axis labels */}
      <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-white/50">
        <span>{maxScore}</span>
        <span>{Math.round((maxScore + minScore) / 2)}</span>
        <span>{minScore}</span>
      </div>
    </div>
  );
};

// ============================================================================
// INSIGHTS PANEL
// ============================================================================

export const InsightsPanel: React.FC<InsightsPanelProps> = ({
  insights,
  showStrengths = true,
  showImprovements = true,
  showSuggestions = true,
  maxItems = 5,
}) => {
  const typeConfig = {
    strength: { icon: '💪', color: '#10B981', label: 'Strengths' },
    improvement: { icon: '📈', color: '#F59E0B', label: 'Areas to Improve' },
    suggestion: { icon: '💡', color: '#3B82F6', label: 'Suggestions' },
    achievement: { icon: '🏆', color: '#FFD700', label: 'Achievements' },
  };
  
  return (
    <div className="bg-white/5 rounded-xl p-4">
      <h3 className="text-lg font-semibold text-white mb-4">Insights</h3>
      
      <div className="space-y-4">
        {showStrengths && insights.strengths.length > 0 && (
          <InsightSection
            items={insights.strengths.slice(0, maxItems)}
            {...typeConfig.strength}
          />
        )}
        
        {showImprovements && insights.improvements.length > 0 && (
          <InsightSection
            items={insights.improvements.slice(0, maxItems)}
            {...typeConfig.improvement}
          />
        )}
        
        {showSuggestions && insights.suggestions.length > 0 && (
          <InsightSection
            items={insights.suggestions.slice(0, maxItems)}
            {...typeConfig.suggestion}
          />
        )}
        
        {insights.achievements.length > 0 && (
          <InsightSection
            items={insights.achievements.slice(0, maxItems)}
            {...typeConfig.achievement}
          />
        )}
      </div>
    </div>
  );
};

interface InsightSectionProps {
  icon: string;
  color: string;
  label: string;
  items: string[];
}

const InsightSection: React.FC<InsightSectionProps> = ({
  icon,
  color,
  label,
  items,
}) => (
  <div>
    <h4 className="flex items-center gap-2 text-sm font-medium text-white/70 mb-2">
      <span>{icon}</span>
      <span>{label}</span>
    </h4>
    <ul className="space-y-1">
      {items.map((item, index) => (
        <motion.li
          key={index}
          className="flex items-start gap-2 text-sm"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0"
            style={{ backgroundColor: color }}
          />
          <span className="text-white">{item}</span>
        </motion.li>
      ))}
    </ul>
  </div>
);

// ============================================================================
// EXPORTS
// ============================================================================

export default SessionReport;
