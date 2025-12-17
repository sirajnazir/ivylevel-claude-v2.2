'use client';

import React from 'react';
import { motion } from 'framer-motion';

/**
 * CircularProgress - 5-ring circular progress visualization
 *
 * Displays IvyReady score with concentric animated rings for each pillar.
 *
 * Ring order (inner to outer):
 * 1. Narrative (displayed as "Identity")
 * 2. Community (displayed as "Service")
 * 3. Passion
 * 4. Aptitude
 * 5. Total Score
 */

// Ring configuration - centralized constants
const RING_CONFIG = {
  // Colors from Claude brand spec
  colors: {
    aptitude: '#FF4A23',    // Ivylevel orange
    passion: '#FF6E6D',     // Coral
    community: '#55AAAA',   // Teal (Service)
    narrative: '#641432',   // Ivylevel maroon (Identity)
    total: '#020202',       // Near black
    background: '#E5E7EB',  // Gray background rings
  },
  // Ring radii (inner to outer)
  radii: {
    narrative: 60,   // Ring 1 - innermost
    community: 90,   // Ring 2
    passion: 120,    // Ring 3
    aptitude: 150,   // Ring 4
    total: 180,      // Ring 5 - outermost
  },
  // Stroke widths
  strokeWidth: {
    default: 20,
    total: 30,       // Thicker for total score ring
  },
  // Animation timing
  animation: {
    duration: 1.5,   // seconds per ring
    stagger: 0.2,    // seconds between rings
    easing: 'easeOut',
  },
} as const;

interface CircularProgressProps {
  /** Aptitude pillar score (0-100) */
  aptitude: number;
  /** Passion pillar score (0-100) */
  passion: number;
  /** Community/Service pillar score (0-100) */
  community: number;
  /** Narrative/Identity pillar score (0-100) */
  narrative: number;
  /** Overall IvyReady score (0-100) */
  totalScore: number;
  /** SVG size in pixels (default: 400) */
  size?: number;
}

interface RingData {
  name: string;
  displayLabel: string;
  radius: number;
  color: string;
  strokeWidth: number;
  score: number;
  index: number;
}

/**
 * Calculate SVG path for a circular arc
 */
function getCirclePath(radius: number, centerX: number, centerY: number): string {
  // Create a near-complete circle (359.9 degrees) to allow strokeDasharray animation
  const startX = centerX;
  const startY = centerY - radius;

  // Large arc flag = 1 for arcs > 180 degrees
  return `M ${startX} ${startY} A ${radius} ${radius} 0 1 1 ${startX - 0.001} ${startY}`;
}

/**
 * Calculate the circumference of a circle
 */
function getCircumference(radius: number): number {
  return 2 * Math.PI * radius;
}

/**
 * Clamp a value between min and max
 */
function clampScore(score: number): number {
  return Math.max(0, Math.min(100, score));
}

export const CircularProgress: React.FC<CircularProgressProps> = ({
  aptitude,
  passion,
  community,
  narrative,
  totalScore,
  size = 400,
}) => {
  const { colors, radii, strokeWidth, animation } = RING_CONFIG;

  // Calculate center point based on size
  const viewBoxSize = 400; // Fixed viewBox for consistent scaling
  const center = viewBoxSize / 2;

  // Define rings from inner to outer (matching render order)
  const rings: RingData[] = [
    {
      name: 'narrative',
      displayLabel: 'Identity',
      radius: radii.narrative,
      color: colors.narrative,
      strokeWidth: strokeWidth.default,
      score: clampScore(narrative),
      index: 0,
    },
    {
      name: 'community',
      displayLabel: 'Service',
      radius: radii.community,
      color: colors.community,
      strokeWidth: strokeWidth.default,
      score: clampScore(community),
      index: 1,
    },
    {
      name: 'passion',
      displayLabel: 'Passion',
      radius: radii.passion,
      color: colors.passion,
      strokeWidth: strokeWidth.default,
      score: clampScore(passion),
      index: 2,
    },
    {
      name: 'aptitude',
      displayLabel: 'Aptitude',
      radius: radii.aptitude,
      color: colors.aptitude,
      strokeWidth: strokeWidth.default,
      score: clampScore(aptitude),
      index: 3,
    },
    {
      name: 'total',
      displayLabel: 'Total',
      radius: radii.total,
      color: colors.total,
      strokeWidth: strokeWidth.total,
      score: clampScore(totalScore),
      index: 4,
    },
  ];

  // Calculate total animation time for center score delay
  const totalAnimationTime = animation.duration + (rings.length - 1) * animation.stagger;
  const centerScoreDelay = 1.0; // Delay after rings start

  return (
    <div
      style={{
        position: 'relative',
        width: size,
        height: size,
        margin: '0 auto',
      }}
    >
      {/* SVG Rings Container */}
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${viewBoxSize} ${viewBoxSize}`}
        style={{
          transform: 'rotate(-90deg)', // Start rings from top (12 o'clock)
        }}
      >
        {rings.map((ring) => {
          const circumference = getCircumference(ring.radius);
          const path = getCirclePath(ring.radius, center, center);
          const strokeDashoffset = circumference * (1 - ring.score / 100);
          const animationDelay = ring.index * animation.stagger;

          return (
            <g key={ring.name}>
              {/* Background ring (gray) */}
              <circle
                cx={center}
                cy={center}
                r={ring.radius}
                fill="none"
                stroke={colors.background}
                strokeWidth={ring.strokeWidth}
              />

              {/* Animated progress ring */}
              <motion.circle
                cx={center}
                cy={center}
                r={ring.radius}
                fill="none"
                stroke={ring.color}
                strokeWidth={ring.strokeWidth}
                strokeLinecap="round"
                strokeDasharray={circumference}
                initial={{ strokeDashoffset: circumference }}
                animate={{ strokeDashoffset }}
                transition={{
                  duration: animation.duration,
                  delay: animationDelay,
                  ease: animation.easing,
                }}
              />
            </g>
          );
        })}
      </svg>

      {/* Center Score Display */}
      <motion.div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{
          duration: 0.5,
          delay: centerScoreDelay,
          ease: 'easeOut',
        }}
      >
        {/* Score Number */}
        <motion.span
          style={{
            fontSize: size * 0.15, // Responsive font size (~60px at 400px)
            fontWeight: 700,
            color: colors.total,
            lineHeight: 1,
            fontFamily: 'Inter, system-ui, sans-serif',
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{
            duration: 0.3,
            delay: centerScoreDelay + 0.2,
          }}
        >
          {clampScore(totalScore)}
        </motion.span>

        {/* Label */}
        <motion.span
          style={{
            fontSize: size * 0.035, // Responsive font size (~14px at 400px)
            color: '#9ca3af', // text-gray-400
            marginTop: size * 0.01,
            fontFamily: 'Inter, system-ui, sans-serif',
            fontWeight: 500,
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{
            duration: 0.3,
            delay: centerScoreDelay + 0.3,
          }}
        >
          IvyReady Score
        </motion.span>
      </motion.div>
    </div>
  );
};

export default CircularProgress;
