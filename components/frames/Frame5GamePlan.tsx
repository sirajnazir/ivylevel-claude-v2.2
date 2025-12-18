'use client';

/**
 * Frame 5: Game Plan Display
 *
 * Displays the personalized game plan generated from the student's profile.
 * Shows phases, actions, quick wins, and summary.
 *
 * STYLING: Uses BRAND_COLORS constants for consistent Ivylevel branding.
 * @version 1.0.0
 */

import { useState, useEffect, useMemo, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { useSessionStore } from '@/lib/store/useSessionStore';
import { generateGamePlan, getStrengthBasedRecommendations } from '@/lib/gamePlan/gamePlanEngine';
import type { GamePlan, GamePlanAction, GamePlanPhase, ActionPriority } from '@/lib/gamePlan/gamePlanEngine';
import { BRAND_COLORS } from '@/lib/constants/brand';
import {
  ChevronRight,
  ChevronLeft,
  ChevronDown,
  ChevronUp,
  Target,
  Zap,
  Clock,
  AlertTriangle,
  CheckCircle,
  Star,
  BookOpen,
  Award,
  Users,
  Lightbulb,
  Calendar,
  TrendingUp,
  ArrowRight,
  Trophy,
  Sparkles,
  Download,
  Loader2,
} from 'lucide-react';

// Dynamically import PDF components to avoid SSR issues
const PDFDownloadLink = dynamic(
  () => import('@react-pdf/renderer').then((mod) => mod.PDFDownloadLink),
  { ssr: false, loading: () => <span>Loading PDF...</span> }
);
const GamePlanPDF = dynamic(
  () => import('@/lib/pdf/GamePlanPDF').then((mod) => mod.GamePlanPDF),
  { ssr: false }
);
const CoachBooking = dynamic(() => import('@/components/booking/CoachBooking'), { ssr: false });

// ============================================================================
// CONSTANTS
// ============================================================================

const PRIORITY_STYLES: Record<ActionPriority, { bg: string; border: string; badge: string }> = {
  critical: {
    bg: 'rgba(220, 38, 38, 0.08)',
    border: '#dc2626',
    badge: '#dc2626',
  },
  high: {
    bg: 'rgba(255, 74, 35, 0.08)',
    border: BRAND_COLORS.primary,
    badge: BRAND_COLORS.primary,
  },
  medium: {
    bg: 'rgba(217, 119, 6, 0.08)',
    border: '#d97706',
    badge: '#d97706',
  },
  low: {
    bg: 'rgba(107, 114, 128, 0.08)',
    border: '#6b7280',
    badge: '#6b7280',
  },
};

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  academics: <BookOpen size={18} />,
  activities: <Sparkles size={18} />,
  leadership: <Trophy size={18} />,
  service: <Users size={18} />,
  testing: <Target size={18} />,
  awards: <Award size={18} />,
  narrative: <Lightbulb size={18} />,
  research: <TrendingUp size={18} />,
  summer: <Calendar size={18} />,
};

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

interface ActionCardProps {
  action: GamePlanAction;
  expanded: boolean;
  onToggle: () => void;
}

function ActionCard({ action, expanded, onToggle }: ActionCardProps) {
  const styles = PRIORITY_STYLES[action.priority];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        backgroundColor: styles.bg,
        border: `1px solid ${styles.border}`,
        borderRadius: 12,
        overflow: 'hidden',
        marginBottom: 12,
      }}
    >
      {/* Header - always visible */}
      <button
        onClick={onToggle}
        style={{
          width: '100%',
          padding: 16,
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          textAlign: 'left',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, flex: 1 }}>
          {/* Icon */}
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 10,
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 20,
              flexShrink: 0,
            }}
          >
            {action.icon}
          </div>

          {/* Content */}
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <h4
                style={{
                  fontSize: 16,
                  fontWeight: 600,
                  color: BRAND_COLORS.textHeading,
                  margin: 0,
                }}
              >
                {action.title}
              </h4>
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  color: 'white',
                  backgroundColor: styles.badge,
                  padding: '2px 6px',
                  borderRadius: 4,
                }}
              >
                {action.priority}
              </span>
            </div>
            <p
              style={{
                fontSize: 14,
                color: BRAND_COLORS.textPrimary,
                margin: 0,
                lineHeight: 1.4,
              }}
            >
              {action.description}
            </p>

            {/* Meta info */}
            <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
              <span
                style={{
                  fontSize: 12,
                  color: BRAND_COLORS.textMuted,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                }}
              >
                <Clock size={12} />
                {action.timeCommitment}
              </span>
              {action.deadline && (
                <span
                  style={{
                    fontSize: 12,
                    color: BRAND_COLORS.textMuted,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                  }}
                >
                  <Calendar size={12} />
                  {action.deadline}
                </span>
              )}
              <span
                style={{
                  fontSize: 12,
                  color: BRAND_COLORS.success,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                }}
              >
                <TrendingUp size={12} />+{action.impact.points} pts
              </span>
            </div>
          </div>
        </div>

        {/* Expand indicator */}
        <div style={{ color: BRAND_COLORS.textMuted, marginLeft: 8 }}>
          {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>
      </button>

      {/* Expanded content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            style={{
              overflow: 'hidden',
              borderTop: `1px solid ${styles.border}`,
            }}
          >
            <div style={{ padding: 16, backgroundColor: 'rgba(255, 255, 255, 0.5)' }}>
              {/* Tips */}
              <div style={{ marginBottom: 16 }}>
                <h5
                  style={{
                    fontSize: 13,
                    fontWeight: 600,
                    color: BRAND_COLORS.textHeading,
                    marginBottom: 8,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                  }}
                >
                  <Lightbulb size={14} />
                  Tips for Success
                </h5>
                <ul
                  style={{
                    margin: 0,
                    padding: 0,
                    listStyle: 'none',
                  }}
                >
                  {action.tips.map((tip, i) => (
                    <li
                      key={i}
                      style={{
                        fontSize: 13,
                        color: BRAND_COLORS.textPrimary,
                        marginBottom: 6,
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: 8,
                      }}
                    >
                      <CheckCircle
                        size={14}
                        style={{ color: BRAND_COLORS.success, flexShrink: 0, marginTop: 2 }}
                      />
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Resources */}
              {action.resources && action.resources.length > 0 && (
                <div>
                  <h5
                    style={{
                      fontSize: 13,
                      fontWeight: 600,
                      color: BRAND_COLORS.textHeading,
                      marginBottom: 8,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                    }}
                  >
                    <BookOpen size={14} />
                    Resources
                  </h5>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {action.resources.map((resource, i) => (
                      <span
                        key={i}
                        style={{
                          fontSize: 12,
                          color: resource.url ? BRAND_COLORS.primary : BRAND_COLORS.textPrimary,
                          backgroundColor: 'white',
                          padding: '4px 10px',
                          borderRadius: 6,
                          border: `1px solid ${BRAND_COLORS.borderLight}`,
                        }}
                      >
                        {resource.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

interface PhaseCardProps {
  phase: GamePlanPhase;
  isActive: boolean;
  onSelect: () => void;
}

function PhaseCard({ phase, isActive, onSelect }: PhaseCardProps) {
  return (
    <button
      onClick={onSelect}
      style={{
        padding: '12px 16px',
        borderRadius: 10,
        border: `2px solid ${isActive ? BRAND_COLORS.primary : BRAND_COLORS.borderLight}`,
        backgroundColor: isActive ? BRAND_COLORS.primaryBg : 'white',
        cursor: 'pointer',
        textAlign: 'left',
        transition: 'all 0.2s',
        minWidth: 180,
      }}
    >
      <h4
        style={{
          fontSize: 14,
          fontWeight: 600,
          color: isActive ? BRAND_COLORS.primary : BRAND_COLORS.textHeading,
          margin: 0,
          marginBottom: 4,
        }}
      >
        {phase.title}
      </h4>
      <p
        style={{
          fontSize: 12,
          color: BRAND_COLORS.textMuted,
          margin: 0,
        }}
      >
        {phase.timeframe} • {phase.actions.length} actions
      </p>
    </button>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

interface Frame5GamePlanProps {
  onComplete?: () => void;
}

export function Frame5GamePlan({ onComplete }: Frame5GamePlanProps) {
  const { profile } = useStudentStore();
  const { nextFrame, completeFrame } = useSessionStore();
  const [activePhaseIndex, setActivePhaseIndex] = useState(0);
  const [expandedActions, setExpandedActions] = useState<Set<string>>(new Set());
  const [showSummary, setShowSummary] = useState(true);

  // Generate game plan
  const gamePlan = useMemo(() => generateGamePlan(profile), [profile]);

  // Get strength-based recommendations
  const strengthRecs = useMemo(
    () => getStrengthBasedRecommendations(profile.operating?.strengths),
    [profile.operating?.strengths]
  );

  const toggleAction = useCallback((actionId: string) => {
    setExpandedActions((prev) => {
      const next = new Set(prev);
      if (next.has(actionId)) {
        next.delete(actionId);
      } else {
        next.add(actionId);
      }
      return next;
    });
  }, []);

  const handleComplete = useCallback(() => {
    completeFrame();
    if (onComplete) {
      onComplete();
    } else {
      nextFrame();
    }
  }, [completeFrame, nextFrame, onComplete]);

  const activePhase = gamePlan.phases[activePhaseIndex];

  return (
    <div
      style={{
        maxWidth: 900,
        margin: '0 auto',
        padding: '24px 16px',
      }}
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ textAlign: 'center', marginBottom: 32 }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '8px 16px',
            backgroundColor: BRAND_COLORS.primaryBg,
            borderRadius: 20,
            marginBottom: 16,
          }}
        >
          <Target size={18} style={{ color: BRAND_COLORS.primary }} />
          <span style={{ fontSize: 14, fontWeight: 600, color: BRAND_COLORS.primary }}>
            Your Personalized Game Plan
          </span>
        </div>

        <h1
          style={{
            fontSize: 28,
            fontWeight: 700,
            color: BRAND_COLORS.textHeading,
            marginBottom: 8,
          }}
        >
          {gamePlan.tierInfo.title}
        </h1>
        <p
          style={{
            fontSize: 16,
            color: BRAND_COLORS.textPrimary,
            maxWidth: 600,
            margin: '0 auto',
          }}
        >
          {gamePlan.tierInfo.description}
        </p>
      </motion.div>

      {/* Warnings */}
      {gamePlan.warnings.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            backgroundColor: 'rgba(220, 38, 38, 0.08)',
            border: '1px solid #dc2626',
            borderRadius: 12,
            padding: 16,
            marginBottom: 24,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <AlertTriangle size={18} style={{ color: '#dc2626' }} />
            <h3 style={{ fontSize: 15, fontWeight: 600, color: '#dc2626', margin: 0 }}>
              Important Considerations
            </h3>
          </div>
          <ul style={{ margin: 0, padding: '0 0 0 24px' }}>
            {gamePlan.warnings.map((warning, i) => (
              <li
                key={i}
                style={{ fontSize: 14, color: BRAND_COLORS.textPrimary, marginBottom: 4 }}
              >
                {warning}
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* Summary Section */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          backgroundColor: 'white',
          border: `1px solid ${BRAND_COLORS.borderLight}`,
          borderRadius: 16,
          marginBottom: 24,
          overflow: 'hidden',
        }}
      >
        <button
          onClick={() => setShowSummary(!showSummary)}
          style={{
            width: '100%',
            padding: 16,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Sparkles size={20} style={{ color: BRAND_COLORS.primary }} />
            <span style={{ fontSize: 16, fontWeight: 600, color: BRAND_COLORS.textHeading }}>
              Your Profile Summary
            </span>
          </div>
          {showSummary ? (
            <ChevronUp size={20} style={{ color: BRAND_COLORS.textMuted }} />
          ) : (
            <ChevronDown size={20} style={{ color: BRAND_COLORS.textMuted }} />
          )}
        </button>

        <AnimatePresence>
          {showSummary && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              style={{ overflow: 'hidden', borderTop: `1px solid ${BRAND_COLORS.borderLight}` }}
            >
              <div style={{ padding: 20 }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                  {/* Strengths */}
                  <div>
                    <h4
                      style={{
                        fontSize: 14,
                        fontWeight: 600,
                        color: BRAND_COLORS.success,
                        marginBottom: 10,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                      }}
                    >
                      <CheckCircle size={16} />
                      Your Strengths
                    </h4>
                    {gamePlan.summary.strengthAreas.length > 0 ? (
                      <ul style={{ margin: 0, padding: '0 0 0 20px' }}>
                        {gamePlan.summary.strengthAreas.map((area, i) => (
                          <li
                            key={i}
                            style={{ fontSize: 13, color: BRAND_COLORS.textPrimary, marginBottom: 4 }}
                          >
                            {area}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p style={{ fontSize: 13, color: BRAND_COLORS.textMuted, margin: 0 }}>
                        Building from scratch - that's your advantage!
                      </p>
                    )}
                  </div>

                  {/* Areas to Develop */}
                  <div>
                    <h4
                      style={{
                        fontSize: 14,
                        fontWeight: 600,
                        color: BRAND_COLORS.primary,
                        marginBottom: 10,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                      }}
                    >
                      <TrendingUp size={16} />
                      Areas to Develop
                    </h4>
                    {gamePlan.summary.improvementAreas.length > 0 ? (
                      <ul style={{ margin: 0, padding: '0 0 0 20px' }}>
                        {gamePlan.summary.improvementAreas.map((area, i) => (
                          <li
                            key={i}
                            style={{ fontSize: 13, color: BRAND_COLORS.textPrimary, marginBottom: 4 }}
                          >
                            {area}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p style={{ fontSize: 13, color: BRAND_COLORS.textMuted, margin: 0 }}>
                        Great coverage across all areas!
                      </p>
                    )}
                  </div>
                </div>

                {/* Focus Recommendation */}
                <div
                  style={{
                    marginTop: 20,
                    padding: 16,
                    backgroundColor: BRAND_COLORS.primaryBg,
                    borderRadius: 10,
                  }}
                >
                  <h4
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: BRAND_COLORS.textHeading,
                      marginBottom: 8,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                    }}
                  >
                    <Zap size={16} style={{ color: BRAND_COLORS.primary }} />
                    Your Focus Area
                  </h4>
                  <p style={{ fontSize: 14, color: BRAND_COLORS.textPrimary, margin: 0, lineHeight: 1.5 }}>
                    {gamePlan.summary.focusRecommendation}
                  </p>
                </div>

                {/* Time Commitment */}
                <div
                  style={{
                    display: 'flex',
                    gap: 20,
                    marginTop: 20,
                    paddingTop: 16,
                    borderTop: `1px solid ${BRAND_COLORS.borderLight}`,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Clock size={18} style={{ color: BRAND_COLORS.textMuted }} />
                    <span style={{ fontSize: 13, color: BRAND_COLORS.textMuted }}>
                      Weekly commitment:{' '}
                      <strong style={{ color: BRAND_COLORS.textPrimary }}>
                        ~{gamePlan.weeklyCommitment} hrs/week
                      </strong>
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Target size={18} style={{ color: BRAND_COLORS.textMuted }} />
                    <span style={{ fontSize: 13, color: BRAND_COLORS.textMuted }}>
                      Actions:{' '}
                      <strong style={{ color: BRAND_COLORS.textPrimary }}>
                        {gamePlan.phases.reduce((t, p) => t + p.actions.length, 0)} total
                      </strong>
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Strength-Based Recommendations */}
      {strengthRecs.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          style={{
            backgroundColor: 'rgba(22, 163, 74, 0.08)',
            border: `1px solid ${BRAND_COLORS.success}`,
            borderRadius: 12,
            padding: 16,
            marginBottom: 24,
          }}
        >
          <h3
            style={{
              fontSize: 15,
              fontWeight: 600,
              color: BRAND_COLORS.success,
              marginBottom: 12,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <Star size={18} />
            Activities Based on Your Strengths
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {strengthRecs.slice(0, 3).map((rec, i) => (
              <div
                key={i}
                style={{
                  backgroundColor: 'white',
                  padding: 12,
                  borderRadius: 8,
                }}
              >
                <p
                  style={{
                    fontSize: 14,
                    fontWeight: 600,
                    color: BRAND_COLORS.textHeading,
                    margin: 0,
                    marginBottom: 4,
                  }}
                >
                  {rec.activity}
                </p>
                <p style={{ fontSize: 13, color: BRAND_COLORS.textMuted, margin: 0 }}>
                  {rec.rationale}
                </p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Phase Selector */}
      {gamePlan.phases.length > 0 && (
        <>
          <div
            style={{
              display: 'flex',
              gap: 12,
              overflowX: 'auto',
              paddingBottom: 8,
              marginBottom: 20,
            }}
          >
            {gamePlan.phases.map((phase, i) => (
              <PhaseCard
                key={phase.id}
                phase={phase}
                isActive={i === activePhaseIndex}
                onSelect={() => setActivePhaseIndex(i)}
              />
            ))}
          </div>

          {/* Active Phase Content */}
          {activePhase && (
            <motion.div
              key={activePhase.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <div style={{ marginBottom: 16 }}>
                <h3
                  style={{
                    fontSize: 18,
                    fontWeight: 600,
                    color: BRAND_COLORS.textHeading,
                    marginBottom: 4,
                  }}
                >
                  {activePhase.title}
                </h3>
                <p style={{ fontSize: 14, color: BRAND_COLORS.textMuted, margin: 0 }}>
                  {activePhase.description}
                </p>
              </div>

              {/* Actions */}
              <div>
                {activePhase.actions.map((action) => (
                  <ActionCard
                    key={action.id}
                    action={action}
                    expanded={expandedActions.has(action.id)}
                    onToggle={() => toggleAction(action.id)}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </>
      )}

      {/* Quick Wins Section */}
      {gamePlan.quickWins.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          style={{
            backgroundColor: 'white',
            border: `1px solid ${BRAND_COLORS.borderLight}`,
            borderRadius: 16,
            padding: 20,
            marginTop: 24,
          }}
        >
          <h3
            style={{
              fontSize: 16,
              fontWeight: 600,
              color: BRAND_COLORS.textHeading,
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <Zap size={18} style={{ color: BRAND_COLORS.primary }} />
            Quick Wins - Start Today
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
            {gamePlan.quickWins.slice(0, 4).map((action) => (
              <div
                key={action.id}
                style={{
                  backgroundColor: BRAND_COLORS.primaryBg,
                  padding: '10px 14px',
                  borderRadius: 8,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <span>{action.icon}</span>
                <span style={{ fontSize: 13, color: BRAND_COLORS.textPrimary }}>{action.title}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        style={{
          marginTop: 32,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 16,
        }}
      >
        {/* PDF Download Button */}
        {typeof window !== 'undefined' && (
          <PDFDownloadLink
            document={
              <GamePlanPDF
                gamePlan={gamePlan}
                studentName={profile.identity?.name || 'Student'}
                studentGrade={typeof profile.identity?.grade === 'number' ? profile.identity.grade : 9}
              />
            }
            fileName={`${(profile.identity?.name || 'Student').replace(/\s+/g, '_')}_GamePlan.pdf`}
          >
            {({ loading, error }) => (
              <button
                disabled={loading}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '12px 24px',
                  backgroundColor: 'white',
                  border: `2px solid ${BRAND_COLORS.primary}`,
                  borderRadius: 10,
                  color: BRAND_COLORS.primary,
                  fontSize: 15,
                  fontWeight: 600,
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                }}
              >
                {loading ? (
                  <>
                    <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
                    Preparing PDF...
                  </>
                ) : (
                  <>
                    <Download size={18} />
                    Download Game Plan (PDF)
                  </>
                )}
              </button>
            )}
          </PDFDownloadLink>
        )}

        {/* Complete Button */}
        <button
          onClick={handleComplete}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '14px 32px',
            background: `linear-gradient(135deg, ${BRAND_COLORS.primary}, #ff6b4a)`,
            border: 'none',
            borderRadius: 10,
            color: 'white',
            fontSize: 16,
            fontWeight: 600,
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(254, 74, 34, 0.3)',
          }}
        >
          Continue to Results
          <ArrowRight size={18} />
        </button>
      </motion.div>

      {/* Coach Booking Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        style={{ marginTop: 32 }}
      >
        <CoachBooking compact />
      </motion.div>

      {/* Encouragement Footer */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        style={{
          textAlign: 'center',
          fontSize: 14,
          color: BRAND_COLORS.textMuted,
          marginTop: 24,
          fontStyle: 'italic',
        }}
      >
        {gamePlan.tierInfo.encouragement}
      </motion.p>
    </div>
  );
}

export default Frame5GamePlan;
