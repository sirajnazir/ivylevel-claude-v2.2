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

import { useCallback, useMemo, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { useSessionStore } from '@/lib/store/useSessionStore';
import { useResultsStore } from '@/lib/store/useResultsStore';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { getProfileTier } from '@/lib/utils/skipLogic';
import CircularProgress from '@/components/rings/CircularProgress';
import { PillarCards } from '@/components/rings/PillarCards';
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
// HELPER FUNCTIONS - FRESH CALCULATION WITH LOGGING
// ============================================================================

/**
 * Helper: Check if value exists and is positive
 */
const hasValue = (val: any) => val !== null && val !== undefined && val !== 0 && val !== '';

/**
 * APTITUDE SCORE (0-100)
 * Calculates fresh every time with comprehensive logging
 * Schema: AptitudeAttributes from student.ts
 */
function calculateAptitudeScore(profile: any): number {
  console.log('=== CALCULATING APTITUDE SCORE ===');
  const apt = profile.aptitude;

  if (!apt) {
    console.log('No aptitude data - returning 0');
    return 0;
  }

  let total = 0;
  let count = 0;

  // GPA component
  const gpa = apt.gpa_weighted ?? apt.gpa_unweighted;
  if (hasValue(gpa) && gpa > 0) {
    const gpaMax = apt.gpa_weighted ? 5.0 : 4.0;
    const gpaScore = (gpa / gpaMax) * 100;
    total += gpaScore;
    count++;
    console.log(`GPA: ${gpa}/${gpaMax} = ${gpaScore.toFixed(1)}%`);
  } else {
    console.log('No GPA data');
  }

  // SAT component (field: sat_total)
  if (hasValue(apt.sat_total) && apt.sat_total > 0) {
    const satScore = (apt.sat_total / 1600) * 100;
    total += satScore;
    count++;
    console.log(`SAT: ${apt.sat_total}/1600 = ${satScore.toFixed(1)}%`);
  } else {
    console.log('No SAT data');
  }

  // ACT component (field: act_total, NOT act_composite)
  if (hasValue(apt.act_total) && apt.act_total > 0) {
    const actScore = (apt.act_total / 36) * 100;
    total += actScore;
    count++;
    console.log(`ACT: ${apt.act_total}/36 = ${actScore.toFixed(1)}%`);
  } else {
    console.log('No ACT data');
  }

  // AP component (field: ap_count, NOT ap_courses)
  if (hasValue(apt.ap_count) && apt.ap_count > 0) {
    const apScore = Math.min((apt.ap_count / 12) * 100, 100);
    total += apScore;
    count++;
    console.log(`APs: ${apt.ap_count}/12 = ${apScore.toFixed(1)}%`);
  } else {
    console.log('No AP data');
  }

  const result = count > 0 ? Math.round(total / count) : 0;
  console.log(`Aptitude FINAL: ${result}% (from ${count} components)`);
  return result;
}

/**
 * PASSION SCORE (0-100)
 * EC commitment: 40pts, Leadership: 30pts, Awards: 30pts
 * Schema: PassionAttributes from student.ts
 */
function calculatePassionScore(profile: any): number {
  console.log('=== CALCULATING PASSION SCORE ===');
  const pass = profile.passion;

  if (!pass) {
    console.log('No passion data - returning 0');
    return 0;
  }

  let score = 0;

  // EC Commitment (40 points max) - based on ec_commitment_years
  const ecYears = pass.ec_commitment_years;
  if (hasValue(ecYears) && ecYears > 0) {
    const ecScore = Math.min((ecYears / 4) * 40, 40);
    score += ecScore;
    console.log(`EC Years: ${ecYears}/4 years = ${ecScore.toFixed(1)} pts`);
  } else {
    console.log('No EC commitment data');
  }

  // Leadership (30 points)
  const leadership = pass.leadership_level;
  if (leadership && leadership !== 'PARTICIPANT') {
    score += 30;
    console.log(`Leadership: ${leadership} = 30 pts`);
  } else {
    console.log(`No meaningful leadership (${leadership})`);
  }

  // Awards (30 points) - field: ec_awards (array of strings)
  const awards = pass.ec_awards;
  if (Array.isArray(awards) && awards.length > 0) {
    score += 30;
    console.log(`EC Awards: ${awards.length} items = 30 pts`);
  } else {
    console.log('No EC awards data');
  }

  console.log(`Passion FINAL: ${Math.round(score)}%`);
  return Math.round(score);
}

/**
 * SERVICE SCORE (0-100)
 * Based on community service hours
 * Schema: CommunityAttributes from student.ts
 */
function calculateServiceScore(profile: any): number {
  console.log('=== CALCULATING SERVICE SCORE ===');
  const community = profile.community;

  if (!community || !hasValue(community.service_hours) || community.service_hours === 0) {
    console.log('No service data - returning 0');
    return 0;
  }

  const score = Math.min((community.service_hours / 300) * 100, 100);
  console.log(`Service: ${community.service_hours} hours = ${Math.round(score)}%`);
  return Math.round(score);
}

/**
 * IDENTITY SCORE (0-100)
 * 25pts each for: favorite subject, strengths, career direction, first gen
 * Schema: OperatingData + DemographicContext from student.ts
 */
function calculateIdentityScore(profile: any): number {
  console.log('=== CALCULATING IDENTITY SCORE ===');
  let score = 0;

  // Favorite subject (25 pts)
  if (hasValue(profile.operating?.favoriteSubject)) {
    score += 25;
    console.log(`Has favorite subject: +25 pts`);
  } else {
    console.log('No favorite subject');
  }

  // Strengths (25 pts)
  const strengths = profile.operating?.strengths;
  if (Array.isArray(strengths) && strengths.length > 0) {
    score += 25;
    console.log(`Has ${strengths.length} strengths: +25 pts`);
  } else {
    console.log('No strengths data');
  }

  // Career direction (25 pts)
  const career = profile.operating?.careerDirection;
  if (career && career !== 'no-idea' && career !== '') {
    score += 25;
    console.log(`Career direction "${career}": +25 pts`);
  } else {
    console.log(`No career direction (${career})`);
  }

  // First gen (25 pts) - field: demographics.first_gen
  if (profile.demographics?.first_gen === true) {
    score += 25;
    console.log('First generation: +25 pts');
  } else {
    console.log('Not first generation');
  }

  console.log(`Identity FINAL: ${score}%`);
  return score;
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
  const setResults = useResultsStore((s) => s.setResults);
  const existingResults = useResultsStore((s) => s.results);
  const [isScoring, setIsScoring] = useState(false);

  // Debug logging
  useEffect(() => {
    console.log('Frame6ProfileReveal: Profile data:', {
      identity: profile.identity,
      aptitude: profile.aptitude,
      passion: profile.passion,
      community: profile.community,
      operating: profile.operating,
      completeness: profile.completeness,
    });
  }, [profile]);

  // Run scoring API to populate results for the results page
  useEffect(() => {
    // Skip if already have results or currently scoring
    if (existingResults || isScoring) return;

    const runScoring = async () => {
      setIsScoring(true);
      try {
        const response = await fetch('/api/score', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ profile }),
        });

        const data = await response.json();
        console.log('Frame6ProfileReveal: Scoring API response:', {
          success: data.success,
          hasResults: !!data.results
        });

        if (response.ok && data.results) {
          setResults(data.results);
        }
      } catch (error) {
        console.error('Frame6ProfileReveal: Scoring error:', error);
        // Non-blocking - continue even if scoring fails
      } finally {
        setIsScoring(false);
      }
    };

    runScoring();
  }, [profile, existingResults, isScoring, setResults]);

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

  // CRITICAL: Calculate completeness FRESH based on actual data, not stored flags
  const { completeness, hasAcademics, hasActivities } = useMemo(() => {
    let score = 0;
    let academics = false;
    let activities = false;

    // Check for REAL academic data (not null, not 0)
    const gpa = profile.aptitude?.gpa_weighted ?? profile.aptitude?.gpa_unweighted;
    if (gpa != null && gpa > 0) {
      score += 15;
      academics = true;
    }
    const testScore = profile.aptitude?.sat_total ?? profile.aptitude?.act_total;
    if (testScore != null && testScore > 0) {
      score += 15;
      academics = true;
    }

    // Check for REAL activity data
    const ecYears = profile.passion?.ec_commitment_years;
    if (ecYears != null && ecYears > 0) {
      score += 20;
      activities = true;
    }
    const serviceHours = profile.community?.service_hours;
    if (serviceHours != null && serviceHours > 0) {
      score += 15;
      activities = true;
    }
    const leadership = profile.passion?.leadership_level;
    // TypeScript knows leadership_level is a specific union type, so just check for truthy and not PARTICIPANT
    if (leadership && leadership !== 'PARTICIPANT') {
      score += 15;
      activities = true;
    }

    // Check for identity/operating data
    if (profile.operating?.favoriteSubject && profile.operating.favoriteSubject !== '') {
      score += 10;
    }
    if (Array.isArray(profile.operating?.strengths) && profile.operating.strengths.length > 0) {
      score += 10;
    }

    return { completeness: score, hasAcademics: academics, hasActivities: activities };
  }, [profile]);

  const tier = getProfileTier(profile);
  const archetype = profile.classification?.archetype || 'Explorer';

  // Extract strengths - based on ACTUAL data, not stored flags
  const strengths = useMemo(() => {
    const result: string[] = [];

    // Check for REAL academics (not stored hasAcademics flag)
    const hasRealAcademics =
      (profile.aptitude?.gpa_weighted != null && profile.aptitude.gpa_weighted > 0) ||
      (profile.aptitude?.gpa_unweighted != null && profile.aptitude.gpa_unweighted > 0) ||
      (profile.aptitude?.sat_total != null && profile.aptitude.sat_total > 0);
    if (hasRealAcademics) {
      result.push('Strong academic foundation');
    }

    if (Array.isArray(profile.operating?.strengths) && profile.operating.strengths.length > 0) {
      result.push('Clear personal strengths identified');
    }

    // Check REAL available hours (must be explicitly set and >= 8)
    const availableHours = profile.operating?.availableHoursPerWeek;
    if (availableHours != null && availableHours >= 8) {
      result.push(`Good time availability (${availableHours} hrs/week)`);
    }

    // Check for REAL activities (not stored hasActivities flag)
    const hasRealActivities =
      (profile.passion?.ec_commitment_years != null && profile.passion.ec_commitment_years > 0);
    if (hasRealActivities) {
      result.push('Started building extracurricular profile');
    }

    // Check for REAL leadership
    const leadership = profile.passion?.leadership_level;
    if (leadership && leadership !== 'PARTICIPANT') {
      result.push('Leadership experience');
    }

    // Check for REAL service hours
    const serviceHours = profile.community?.service_hours;
    if (serviceHours != null && serviceHours >= 50) {
      result.push('Community service commitment');
    }

    return result.length > 0 ? result : ['Starting fresh - building from a clean slate!'];
  }, [profile]);

  // Extract gaps - based on ACTUAL data
  const gaps = useMemo(() => {
    const result: string[] = [];

    // Check for MISSING academics
    const hasAnyAcademics =
      (profile.aptitude?.gpa_weighted != null && profile.aptitude.gpa_weighted > 0) ||
      (profile.aptitude?.sat_total != null && profile.aptitude.sat_total > 0);
    if (!hasAnyAcademics) {
      result.push('Track academic data (GPA, test scores)');
    }

    const ecYears = profile.passion?.ec_commitment_years;
    if (ecYears == null || ecYears < 2) {
      result.push('Need more sustained activity involvement');
    }

    const leadershipGap = profile.passion?.leadership_level;
    if (!leadershipGap || leadershipGap === 'PARTICIPANT') {
      result.push('Need leadership roles');
    }

    const apCount = profile.aptitude?.ap_count;
    if (apCount == null || apCount < 3) {
      result.push('Consider adding course rigor (APs/honors)');
    }

    const serviceHours = profile.community?.service_hours;
    if (serviceHours == null || serviceHours < 50) {
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

      {/* Ivy+ Ready Score - 5-Ring Circular Visualization */}
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
            textAlign: 'center',
          }}
        >
          Your Ivy+ Ready Score
        </h2>

        {/* CircularProgress - 5 concentric rings visualization */}
        <div style={{ maxWidth: 400, margin: '0 auto' }}>
          <CircularProgress
            aptitude={categoryScores.find((c) => c.name === 'Aptitude')?.score || 0}
            passion={categoryScores.find((c) => c.name === 'Passion')?.score || 0}
            community={categoryScores.find((c) => c.name === 'Service')?.score || 0}
            narrative={categoryScores.find((c) => c.name === 'Identity')?.score || 0}
            totalScore={Math.round(
              categoryScores.reduce((sum, c) => sum + c.score, 0) / categoryScores.length
            )}
            size={360}
          />
        </div>
      </motion.div>

      {/* Four Pillars - 2x2 Grid with Wave Animations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
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
            textAlign: 'center',
          }}
        >
          Four Pillars of Excellence
        </h2>

        {/* PillarCards - 2x2 grid with SVG wave animations */}
        <div style={{ maxWidth: 500, margin: '0 auto' }}>
          <PillarCards
            aptitude={categoryScores.find((c) => c.name === 'Aptitude')?.score || 0}
            passion={categoryScores.find((c) => c.name === 'Passion')?.score || 0}
            community={categoryScores.find((c) => c.name === 'Service')?.score || 0}
            narrative={categoryScores.find((c) => c.name === 'Identity')?.score || 0}
          />
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
