/**
 * IvyQuest v3.0 — Score Delta Components
 * 
 * @version 1.0.0
 * @module components/ScoreDelta
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import ScoreDeltaPopup from './ScoreDeltaPopup';
import { getCategoryColors } from '../../utils/feedbackUtils';
import type { ScoreDeltaTrailProps } from '../../types/feedback.types';

// ============================================================================
// SCORE DELTA TRAIL
// ============================================================================

const ScoreDeltaTrail: React.FC<ScoreDeltaTrailProps> = ({
  from,
  to,
  color,
  onComplete,
}) => {
  return (
    <svg
      className="fixed inset-0 pointer-events-none z-40"
      style={{ width: '100%', height: '100%' }}
    >
      <defs>
        <linearGradient id="trailGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={color} stopOpacity="0" />
          <stop offset="50%" stopColor={color} stopOpacity="0.8" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      
      <motion.circle
        r="4"
        fill={color}
        filter="url(#glow)"
        initial={{ cx: from.x, cy: from.y, opacity: 1 }}
        animate={{ cx: to.x, cy: to.y, opacity: 0 }}
        transition={{ duration: 0.5, ease: 'easeInOut' }}
        onAnimationComplete={onComplete}
      />
      
      <motion.line
        x1={from.x}
        y1={from.y}
        x2={to.x}
        y2={to.y}
        stroke="url(#trailGradient)"
        strokeWidth="2"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: [0, 0.8, 0] }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      />
    </svg>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

export { ScoreDeltaPopup, ScoreDeltaTrail };
export default ScoreDeltaPopup;
