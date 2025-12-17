/**
 * IvyQuest v3.0 — ScoreDisplay Component
 * 
 * Animated score display with tier indicators.
 * 
 * @version 1.0.0
 * @module components/ScoreDisplay
 */

'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

// ============================================================================
// TYPES
// ============================================================================

export type ScoreTier = 'exceptional' | 'competitive' | 'average' | 'developing';

export interface ScoreDisplayProps {
  /** Score value (0-100) */
  score: number;
  
  /** Maximum score */
  maxScore?: number;
  
  /** Label text */
  label?: string;
  
  /** Score tier */
  tier?: ScoreTier;
  
  /** Show animation on mount/change */
  showAnimation?: boolean;
  
  /** Animation duration (ms) */
  animationDuration?: number;
  
  /** Size variant */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  
  /** Show tier badge */
  showTier?: boolean;
  
  /** Show progress ring */
  showRing?: boolean;
  
  /** Custom color override */
  color?: string;
  
  /** Additional class */
  className?: string;
}

// ============================================================================
// TIER CONFIG
// ============================================================================

const tierConfig: Record<ScoreTier, { label: string; color: string; bgColor: string }> = {
  exceptional: {
    label: 'Exceptional',
    color: '#FFD700',
    bgColor: 'rgba(255, 215, 0, 0.1)',
  },
  competitive: {
    label: 'Competitive',
    color: '#00D4FF',
    bgColor: 'rgba(0, 212, 255, 0.1)',
  },
  average: {
    label: 'Average',
    color: '#3B82F6',
    bgColor: 'rgba(59, 130, 246, 0.1)',
  },
  developing: {
    label: 'Developing',
    color: '#6B7280',
    bgColor: 'rgba(107, 114, 128, 0.1)',
  },
};

// ============================================================================
// SIZE CONFIG
// ============================================================================

const sizeConfig = {
  sm: {
    container: 'w-16 h-16',
    score: 'text-xl',
    label: 'text-xs',
    ring: 48,
    stroke: 3,
  },
  md: {
    container: 'w-24 h-24',
    score: 'text-3xl',
    label: 'text-sm',
    ring: 72,
    stroke: 4,
  },
  lg: {
    container: 'w-32 h-32',
    score: 'text-4xl',
    label: 'text-base',
    ring: 96,
    stroke: 5,
  },
  xl: {
    container: 'w-40 h-40',
    score: 'text-5xl',
    label: 'text-lg',
    ring: 120,
    stroke: 6,
  },
};

// ============================================================================
// HELPER: Get tier from score
// ============================================================================

const getTierFromScore = (score: number): ScoreTier => {
  if (score >= 85) return 'exceptional';
  if (score >= 70) return 'competitive';
  if (score >= 50) return 'average';
  return 'developing';
};

// ============================================================================
// COMPONENT
// ============================================================================

export const ScoreDisplay: React.FC<ScoreDisplayProps> = ({
  score,
  maxScore = 100,
  label,
  tier,
  showAnimation = true,
  animationDuration = 1500,
  size = 'md',
  showTier = true,
  showRing = true,
  color,
  className,
}) => {
  const [displayScore, setDisplayScore] = useState(showAnimation ? 0 : score);
  const config = sizeConfig[size];
  const actualTier = tier || getTierFromScore(score);
  const tierInfo = tierConfig[actualTier];
  const scoreColor = color || tierInfo.color;
  
  // Animate score on mount/change
  useEffect(() => {
    if (!showAnimation) {
      setDisplayScore(score);
      return;
    }
    
    const startTime = Date.now();
    const startScore = displayScore;
    const diff = score - startScore;
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / animationDuration, 1);
      
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayScore(Math.round(startScore + diff * eased));
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [score, showAnimation, animationDuration]);
  
  // Calculate ring progress
  const percentage = (displayScore / maxScore) * 100;
  const circumference = 2 * Math.PI * (config.ring / 2 - config.stroke);
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  
  return (
    <div className={cn('flex flex-col items-center gap-2', className)}>
      {/* Score circle */}
      <div className={cn('relative', config.container)}>
        {/* Background ring */}
        {showRing && (
          <svg
            className="absolute inset-0 -rotate-90"
            width={config.ring}
            height={config.ring}
            viewBox={`0 0 ${config.ring} ${config.ring}`}
          >
            {/* Track */}
            <circle
              cx={config.ring / 2}
              cy={config.ring / 2}
              r={config.ring / 2 - config.stroke}
              fill="none"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth={config.stroke}
            />
            
            {/* Progress */}
            <motion.circle
              cx={config.ring / 2}
              cy={config.ring / 2}
              r={config.ring / 2 - config.stroke}
              fill="none"
              stroke={scoreColor}
              strokeWidth={config.stroke}
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: animationDuration / 1000, ease: 'easeOut' }}
            />
          </svg>
        )}
        
        {/* Score number */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className={cn('font-bold tabular-nums', config.score)}
            style={{ color: scoreColor }}
            initial={showAnimation ? { scale: 0.5, opacity: 0 } : undefined}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          >
            {displayScore}
          </motion.span>
          
          {maxScore !== 100 && (
            <span className="text-white/40 text-xs">/ {maxScore}</span>
          )}
        </div>
        
        {/* Glow effect */}
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{
            background: `radial-gradient(circle, ${scoreColor}20 0%, transparent 70%)`,
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        />
      </div>
      
      {/* Label */}
      {label && (
        <span className={cn('text-white/70', config.label)}>{label}</span>
      )}
      
      {/* Tier badge */}
      {showTier && (
        <motion.div
          className="px-3 py-1 rounded-full text-xs font-semibold"
          style={{
            backgroundColor: tierInfo.bgColor,
            color: tierInfo.color,
          }}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          {tierInfo.label}
        </motion.div>
      )}
    </div>
  );
};

export default ScoreDisplay;
