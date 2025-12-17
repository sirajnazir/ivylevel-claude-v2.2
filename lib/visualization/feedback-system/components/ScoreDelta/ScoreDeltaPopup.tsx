/**
 * IvyQuest v3.0 — Score Delta Popup
 * 
 * Animated popup showing score change.
 * 
 * @version 1.0.0
 * @module components/ScoreDelta/ScoreDeltaPopup
 */

'use client';

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  getDeltaColors,
  getDeltaSize,
  getCategoryColors,
  formatDelta,
  getAnimationDuration,
  getDeltaMagnitude,
} from '../../utils/feedbackUtils';
import { SCORE_DELTA_CONFIG } from '../../constants/feedback.constants';
import type { ScoreDeltaPopupProps } from '../../types/feedback.types';

// ============================================================================
// COMPONENT
// ============================================================================

const ScoreDeltaPopup: React.FC<ScoreDeltaPopupProps> = ({
  delta,
  category,
  position,
  onComplete,
  duration: customDuration,
  showTrail = false,
}) => {
  const deltaColors = getDeltaColors(delta);
  const categoryColors = getCategoryColors(category);
  const sizeConfig = getDeltaSize(delta);
  const magnitude = getDeltaMagnitude(delta);
  const duration = customDuration ?? getAnimationDuration(delta);
  
  // Trigger onComplete after animation
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete?.();
    }, duration);
    
    return () => clearTimeout(timer);
  }, [duration, onComplete]);
  
  const isPositive = delta > 0;
  const yMovement = isPositive ? -60 : 60;
  
  return (
    <motion.div
      className="fixed pointer-events-none z-50"
      style={{
        left: position.x,
        top: position.y,
        transform: 'translate(-50%, -50%)',
      }}
      initial={{ opacity: 0, y: 0, scale: 0.5 }}
      animate={{
        opacity: [0, 1, 1, 0],
        y: [0, yMovement * 0.3, yMovement * 0.7, yMovement],
        scale: [0.5, sizeConfig.scale * 1.2, sizeConfig.scale, sizeConfig.scale * 0.8],
      }}
      transition={{
        duration: duration / 1000,
        times: [0, 0.2, 0.7, 1],
        ease: 'easeOut',
      }}
    >
      {/* Main delta text */}
      <div
        className="font-bold tabular-nums whitespace-nowrap"
        style={{
          fontSize: sizeConfig.fontSize,
          color: deltaColors.primary,
          textShadow: `
            0 0 10px ${deltaColors.glow},
            0 0 20px ${deltaColors.glow},
            0 2px 4px rgba(0,0,0,0.3)
          `,
        }}
      >
        {formatDelta(delta)}
      </div>
      
      {/* Category indicator */}
      <motion.div
        className="text-xs text-center mt-1 uppercase tracking-wider opacity-70"
        style={{ color: categoryColors.primary }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.7 }}
        transition={{ delay: 0.1 }}
      >
        {category}
      </motion.div>
      
      {/* Sparkle particles for major changes */}
      {magnitude === 'major' || magnitude === 'exceptional' ? (
        <AnimatePresence>
          {Array.from({ length: magnitude === 'exceptional' ? 8 : 4 }).map((_, i) => {
            const angle = (i / (magnitude === 'exceptional' ? 8 : 4)) * Math.PI * 2;
            const distance = 30 + Math.random() * 20;
            
            return (
              <motion.div
                key={`sparkle-${i}`}
                className="absolute w-1.5 h-1.5 rounded-full"
                style={{
                  backgroundColor: deltaColors.glow,
                  left: '50%',
                  top: '50%',
                }}
                initial={{
                  x: 0,
                  y: 0,
                  opacity: 1,
                  scale: 1,
                }}
                animate={{
                  x: Math.cos(angle) * distance,
                  y: Math.sin(angle) * distance,
                  opacity: 0,
                  scale: 0,
                }}
                transition={{
                  duration: 0.6,
                  delay: 0.1 + i * 0.03,
                  ease: 'easeOut',
                }}
              />
            );
          })}
        </AnimatePresence>
      ) : null}
    </motion.div>
  );
};

export default ScoreDeltaPopup;
