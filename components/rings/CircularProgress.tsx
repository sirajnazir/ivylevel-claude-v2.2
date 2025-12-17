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

// Ring configuration - matches Gemini Phoenix exactly
// Phoenix uses SVG sizes: 895, 1090, 1287, 1482, 1750 scaled by 0.22
// This gives effective diameters: ~197, 240, 283, 326, 385 px
// We use radii that produce similar visual proportions in a 400px viewBox
const RING_CONFIG = {
  // Colors from Gemini Phoenix (outer to inner order)
  colors: {
    total: 'url(#ivyGradient)',  // Gradient for Ivy+ Score ring (outer)
    aptitude: '#FFBB6D',         // Golden
    passion: '#FF6E6D',          // Coral
    community: '#55AAAA',        // Teal (Service)
    narrative: '#979797',        // Gray (Identity)
    background: '#FFFFFF',       // White background rings
  },
  // Ring radii (inner to outer) - scaled to match Gemini Phoenix proportions
  // Innermost ring leaves ~70px radius clear for center circle
  radii: {
    narrative: 78,   // Ring 1 - innermost (Identity) ~156px diameter
    community: 98,   // Ring 2 (Service) ~196px diameter
    passion: 118,    // Ring 3 ~236px diameter
    aptitude: 138,   // Ring 4 ~276px diameter
    total: 162,      // Ring 5 - outermost (Ivy+ Score) ~324px diameter
  },
  // Stroke widths - Phoenix uses 55 scaled by 0.22 = ~12px for inner, 80*0.22=~18 for outer
  strokeWidth: {
    default: 12,
    total: 18,       // Thicker for Ivy+ Score ring
  },
  // Animation timing
  animation: {
    duration: 1.5,   // seconds per ring
    stagger: 0.15,   // seconds between rings
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
        width: '100%',
        maxWidth: size,
        aspectRatio: '1',
        margin: '0 auto',
      }}
    >
      {/* SVG Container - matches Phoenix structure */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <svg
          width="100%"
          height="100%"
          viewBox={`0 0 ${viewBoxSize} ${viewBoxSize}`}
          style={{
            transform: 'rotate(-90deg)', // Start rings from top (12 o'clock)
          }}
        >
        {/* Gradient definition for Ivy+ Score ring - matches Gemini Phoenix */}
        <defs>
          <linearGradient id="ivyGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#641432" />
            <stop offset="30%" stopColor="#8A1D45" />
            <stop offset="50%" stopColor="#FE4A22" />
            <stop offset="70%" stopColor="#FF7224" />
            <stop offset="100%" stopColor="#FFBB6D" />
          </linearGradient>
        </defs>

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
      </div>

      {/* Center Profile Circle - matches Gemini Phoenix exactly */}
      <motion.div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: 80,  // Fixed 80px like Phoenix
          height: 80, // Fixed 80px like Phoenix
          borderRadius: '50%',
          overflow: 'hidden',
          background: 'linear-gradient(135deg, #FF4A23 0%, #FF7043 100%)',
          border: '3px solid white',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10,
        }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{
          duration: 0.5,
          delay: centerScoreDelay,
          ease: 'easeOut',
        }}
      >
        <motion.span
          style={{
            color: 'white',
            fontFamily: 'Inter, system-ui, sans-serif',
            fontSize: 24,  // Fixed 24px like Phoenix
            fontWeight: 700,
            textAlign: 'center',
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{
            duration: 0.3,
            delay: centerScoreDelay + 0.2,
          }}
        >
          {clampScore(totalScore)}%
        </motion.span>
      </motion.div>

      {/* Bottom Score Label - positioned just below the outer ring */}
      <motion.div
        style={{
          position: 'absolute',
          bottom: '5%',  // Closer to rings (outer ring ends at ~7% from bottom)
          left: '50%',
          transform: 'translateX(-50%)',
          background: 'linear-gradient(135deg, #FF5733 0%, #FF7043 100%)',
          color: 'white',
          padding: '12px 24px',
          borderRadius: 12,
          textAlign: 'center',
          zIndex: 10,
          boxShadow: '0 4px 20px rgba(255, 87, 51, 0.2)',
        }}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: 0.5,
          delay: centerScoreDelay + 0.3,
          ease: 'easeOut',
        }}
      >
        <div style={{ fontSize: 32, fontWeight: 700, lineHeight: 1 }}>
          {clampScore(totalScore)}%
        </div>
        <div style={{ fontSize: 11, opacity: 0.9, textTransform: 'uppercase', letterSpacing: 1 }}>
          Ivy+ Ready Score
        </div>
      </motion.div>
    </div>
  );
};

export default CircularProgress;
