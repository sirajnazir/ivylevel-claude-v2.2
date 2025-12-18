'use client';

/**
 * Frame 6: Profile Reveal
 *
 * Displays profile overview with:
 * - Overall completeness score
 * - Category breakdown (Aptitude, Passion, Service, Identity)
 * - Strengths and gaps analysis
 * - Quick wins for next 30 days
 *
 * STYLING: Uses BRAND_COLORS constants for consistent Ivylevel branding.
 * @version 1.0.0
 */

import { useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { useSessionStore } from '@/lib/store/useSessionStore';
import { BRAND_COLORS } from '@/lib/constants/brand';
import {
  TrendingUp,
  Target,
  ChevronRight,
  CheckCircle,
  BookOpen,
  Sparkles,
  Users,
  Star,
} from 'lucide-react';

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function calculateAptitudeScore(profile: any): number {
  let score = 0;
  let count = 0;

  if (profile.aptitude?.gpa_weighted) {
    const gpa = profile.aptitude.gpa_weighted;
    score += (gpa / 4.5) * 100;
    count++;
  }

  if (profile.aptitude?.sat_total) {
    const sat = profile.aptitude.sat_total;
    score += (sat / 1600) * 100;
    count++;
  }

  if (profile.aptitude?.ap_count !== undefined) {
    const aps = profile.aptitude.ap_count;
    score += Math.min((aps / 12) * 100, 100);
    count++;
  }

  return count > 0 ? Math.round(score / count) : 0;
}

function calculatePassionScore(profile: any): number {
  const ecYears = profile.passion?.ec_commitment_years || 0;
  const hasLeadership =
    profile.passion?.leadership_level && profile.passion.leadership_level !== 'PARTICIPANT';
  const hasAwards =
    (profile.passion?.ec_awards && profile.passion.ec_awards.length > 0) ||
    (profile.aptitude?.academic_awards && profile.aptitude.academic_awards.length > 0);

  let score = 0;
  score += Math.min((ecYears / 4) * 40, 40);
  score += hasLeadership ? 30 : 0;
  score += hasAwards ? 30 : 0;

  return Math.round(score);
}

function calculateServiceScore(profile: any): number {
  const hours = profile.community?.service_hours || 0;
  return Math.round(Math.min((hours / 300) * 100, 100));
}

function calculateIdentityScore(profile: any): number {
  let score = 0;

  if (profile.operating?.favoriteSubject) score += 25;
  if (profile.operating?.strengths && profile.operating.strengths.length > 0) score += 25;
  if (profile.operating?.careerDirection && profile.operating.careerDirection !== 'no-idea')
    score += 25;
  if (profile.demographics?.first_gen) score += 25;

  return score;
}

function getCategoryColor(color: string): string {
  const colors: Record<string, string> = {
    blue: '#3b82f6',
    purple: '#a855f7',
    green: '#22c55e',
    amber: '#f59e0b',
  };
  return colors[color] || '#6b7280';
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

interface Frame6ProfileRevealProps {
  onComplete?: () => void;
}

export function Frame6ProfileReveal({ onComplete }: Frame6ProfileRevealProps) {
  const { profile } = useStudentStore();
  const { nextFrame, completeFrame } = useSessionStore();

  // Calculate category scores
  const categoryScores = useMemo(
    () => [
      {
        name: 'Aptitude',
        score: calculateAptitudeScore(profile),
        color: 'blue',
        icon: <BookOpen size={20} />,
      },
      {
        name: 'Passion',
        score: calculatePassionScore(profile),
        color: 'purple',
        icon: <Sparkles size={20} />,
      },
      {
        name: 'Service',
        score: calculateServiceScore(profile),
        color: 'green',
        icon: <Users size={20} />,
      },
      {
        name: 'Identity',
        score: calculateIdentityScore(profile),
        color: 'amber',
        icon: <Star size={20} />,
      },
    ],
    [profile]
  );

  const completeness = profile.completeness?.score || 0;
  const tier = profile.classification?.tier || 'fresh-start';
  const archetype = profile.classification?.archetype || 'Explorer';

  // Extract strengths
  const strengths = useMemo(() => {
    const result: string[] = [];
    if (profile.completeness?.hasAcademics) {
      result.push('Strong academic foundation');
    }
    if (profile.operating?.strengths && profile.operating.strengths.length > 0) {
      result.push('Clear personal strengths identified');
    }
    if ((profile.operating?.availableHoursPerWeek || 0) >= 8) {
      result.push(`Good time availability (${profile.operating?.availableHoursPerWeek} hrs/week)`);
    }
    if (profile.completeness?.hasActivities) {
      result.push('Started building extracurricular profile');
    }
    if (profile.passion?.leadership_level && profile.passion.leadership_level !== 'PARTICIPANT') {
      result.push('Leadership experience');
    }
    if ((profile.community?.service_hours || 0) >= 50) {
      result.push('Community service commitment');
    }
    return result.length > 0 ? result : ['Starting fresh - building from a clean slate!'];
  }, [profile]);

  // Extract gaps
  const gaps = useMemo(() => {
    const result: string[] = [];
    if (!profile.completeness?.hasAcademics) {
      result.push('Track academic data (GPA, test scores)');
    }
    if ((profile.passion?.ec_commitment_years || 0) < 2) {
      result.push('Need more sustained activity involvement');
    }
    if (!profile.passion?.leadership_level || profile.passion.leadership_level === 'PARTICIPANT') {
      result.push('Need leadership roles');
    }
    if ((profile.aptitude?.ap_count || 0) < 3) {
      result.push('Consider adding course rigor (APs/honors)');
    }
    if ((profile.community?.service_hours || 0) < 50) {
      result.push('Increase community service hours');
    }
    return result.slice(0, 4);
  }, [profile]);

  // Quick wins
  const quickWins = useMemo(() => {
    const wins: string[] = [];

    if (completeness < 30) {
      wins.push('Track your current GPA');
      wins.push('Take a diagnostic SAT/ACT test');
    }

    if ((profile.passion?.ec_commitment_years || 0) < 2) {
      wins.push('Join 2 school clubs this month');
    }

    if (!profile.passion?.leadership_level || profile.passion.leadership_level === 'PARTICIPANT') {
      wins.push('Pursue a leadership role in existing activity');
    }

    if ((profile.community?.service_hours || 0) < 30) {
      wins.push('Find a weekly volunteer opportunity');
    }

    return wins.slice(0, 3);
  }, [profile, completeness]);

  const handleNext = useCallback(() => {
    completeFrame();
    if (onComplete) {
      onComplete();
    } else {
      nextFrame();
    }
  }, [completeFrame, nextFrame, onComplete]);

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
        <h1
          style={{
            fontSize: 32,
            fontWeight: 700,
            color: BRAND_COLORS.textHeading,
            marginBottom: 8,
          }}
        >
          Your Profile Overview
        </h1>
        <p
          style={{
            fontSize: 18,
            color: BRAND_COLORS.textPrimary,
          }}
        >
          Here's where you stand and what to focus on
        </p>
      </motion.div>

      {/* Completeness Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        style={{
          background: 'linear-gradient(135deg, #eff6ff, #e0e7ff)',
          border: '2px solid #93c5fd',
          borderRadius: 16,
          padding: 24,
          marginBottom: 24,
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 16,
          }}
        >
          <div>
            <h2
              style={{
                fontSize: 24,
                fontWeight: 700,
                color: BRAND_COLORS.textHeading,
                marginBottom: 4,
              }}
            >
              Overall Completeness
            </h2>
            <p style={{ fontSize: 14, color: BRAND_COLORS.textPrimary }}>
              {tier === 'fresh-start' && 'Foundation Building Phase'}
              {tier === 'emerging' && 'Direction Setting Phase'}
              {tier === 'optimization' && 'Profile Optimization Phase'}
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div
              style={{
                fontSize: 48,
                fontWeight: 700,
                color: '#3b82f6',
              }}
            >
              {completeness}%
            </div>
            <p style={{ fontSize: 12, color: BRAND_COLORS.textMuted }}>Profile Complete</p>
          </div>
        </div>

        {/* Progress bar */}
        <div
          style={{
            width: '100%',
            backgroundColor: '#e5e7eb',
            borderRadius: 8,
            height: 16,
            overflow: 'hidden',
          }}
        >
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${completeness}%` }}
            transition={{ duration: 1, delay: 0.5 }}
            style={{
              height: '100%',
              background: 'linear-gradient(90deg, #3b82f6, #6366f1)',
              borderRadius: 8,
            }}
          />
        </div>

        <p style={{ fontSize: 13, color: BRAND_COLORS.textMuted, marginTop: 8 }}>
          Archetype: <strong style={{ color: BRAND_COLORS.textPrimary }}>{archetype}</strong>
        </p>
      </motion.div>

      {/* Category Scores */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        style={{
          backgroundColor: 'white',
          border: `2px solid ${BRAND_COLORS.borderLight}`,
          borderRadius: 16,
          padding: 24,
          marginBottom: 24,
        }}
      >
        <h2
          style={{
            fontSize: 20,
            fontWeight: 700,
            color: BRAND_COLORS.textHeading,
            marginBottom: 20,
          }}
        >
          Category Breakdown
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {categoryScores.map((category, index) => (
            <motion.div
              key={category.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 + index * 0.1 }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: 8,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ color: getCategoryColor(category.color) }}>{category.icon}</span>
                  <span style={{ fontWeight: 600, color: BRAND_COLORS.textHeading }}>
                    {category.name}
                  </span>
                </div>
                <span style={{ fontSize: 18, fontWeight: 700, color: BRAND_COLORS.textPrimary }}>
                  {category.score}%
                </span>
              </div>
              <div
                style={{
                  width: '100%',
                  backgroundColor: '#e5e7eb',
                  borderRadius: 6,
                  height: 12,
                  overflow: 'hidden',
                }}
              >
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${category.score}%` }}
                  transition={{ duration: 0.8, delay: 0.8 + index * 0.1 }}
                  style={{
                    height: '100%',
                    backgroundColor: getCategoryColor(category.color),
                    borderRadius: 6,
                  }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Strengths & Gaps */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 24,
          marginBottom: 24,
        }}
      >
        {/* Strengths */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 1.0 }}
          style={{
            backgroundColor: 'rgba(22, 163, 74, 0.08)',
            border: '2px solid #22c55e',
            borderRadius: 16,
            padding: 20,
          }}
        >
          <h3
            style={{
              fontSize: 18,
              fontWeight: 700,
              color: '#166534',
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <TrendingUp size={20} />
            Your Strengths
          </h3>
          <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
            {strengths.map((strength, i) => (
              <li
                key={i}
                style={{
                  color: '#166534',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 8,
                  marginBottom: 8,
                  fontSize: 14,
                }}
              >
                <CheckCircle size={16} style={{ flexShrink: 0, marginTop: 2 }} />
                {strength}
              </li>
            ))}
          </ul>
        </motion.div>

        {/* Priority Gaps */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 1.2 }}
          style={{
            backgroundColor: 'rgba(234, 88, 12, 0.08)',
            border: '2px solid #f97316',
            borderRadius: 16,
            padding: 20,
          }}
        >
          <h3
            style={{
              fontSize: 18,
              fontWeight: 700,
              color: '#9a3412',
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <Target size={20} />
            Priority Gaps
          </h3>
          <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
            {gaps.map((gap, i) => (
              <li
                key={i}
                style={{
                  color: '#9a3412',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 8,
                  marginBottom: 8,
                  fontSize: 14,
                }}
              >
                <ChevronRight size={16} style={{ flexShrink: 0, marginTop: 2 }} />
                {gap}
              </li>
            ))}
          </ul>
        </motion.div>
      </div>

      {/* Quick Wins */}
      {quickWins.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.4 }}
          style={{
            backgroundColor: 'rgba(220, 38, 38, 0.08)',
            border: '2px solid #ef4444',
            borderRadius: 16,
            padding: 24,
            marginBottom: 32,
          }}
        >
          <h3
            style={{
              fontSize: 20,
              fontWeight: 700,
              color: '#991b1b',
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            Quick Wins (Next 30 Days)
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {quickWins.map((win, index) => (
              <div
                key={index}
                style={{
                  backgroundColor: 'white',
                  border: '1px solid #fecaca',
                  borderRadius: 10,
                  padding: 16,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                }}
              >
                <div
                  style={{
                    backgroundColor: '#fef2f2',
                    color: '#dc2626',
                    borderRadius: 20,
                    width: 32,
                    height: 32,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    flexShrink: 0,
                  }}
                >
                  {index + 1}
                </div>
                <span style={{ color: BRAND_COLORS.textHeading, fontWeight: 500 }}>{win}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* CTA */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.6 }}
        style={{ textAlign: 'center' }}
      >
        <button
          onClick={handleNext}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 12,
            background: `linear-gradient(135deg, ${BRAND_COLORS.primary}, #ff6b4a)`,
            color: 'white',
            padding: '16px 32px',
            borderRadius: 12,
            border: 'none',
            fontSize: 18,
            fontWeight: 700,
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(254, 74, 34, 0.3)',
          }}
        >
          View Your Detailed Game Plan
          <ChevronRight size={24} />
        </button>
        <p
          style={{
            fontSize: 14,
            color: BRAND_COLORS.textMuted,
            marginTop: 12,
          }}
        >
          We've created a personalized action plan based on your profile
        </p>
      </motion.div>
    </div>
  );
}

export default Frame6ProfileReveal;
