/**
 * IvyQuest v3.0 — Score Reveal Animation
 * 
 * Animated score counter with tier badge.
 * 
 * @version 1.0.0
 * @module components/animations/ScoreReveal
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ANIMATION_TIMINGS, SCORE_TIERS } from '../../constants/twin.constants';
import { getTierColors, withAlpha, createAnimationCounter, easings } from '../../utils/twinUtils';
import type { ScoreRevealProps } from '../../types/twin.types';

// ============================================================================
// COMPONENT
// ============================================================================

const ScoreReveal: React.FC<ScoreRevealProps> = ({
  fromScore = 0,
  toScore,
  tier,
  duration = ANIMATION_TIMINGS.scoreReveal.total,
  showTierBadge = true,
  onComplete,
  easing = 'easeOut',
}) => {
  const [currentScore, setCurrentScore] = useState(fromScore);
  const [phase, setPhase] = useState<'counting' | 'landed' | 'badge' | 'complete'>('counting');
  
  const tierColors = getTierColors(tier);
  const tierConfig = SCORE_TIERS[tier];
  
  // Start counter animation
  useEffect(() => {
    const countDuration = ANIMATION_TIMINGS.scoreReveal.countUp;
    
    createAnimationCounter(
      fromScore,
      toScore,
      countDuration,
      easing as keyof typeof easings,
      (value) => setCurrentScore(value),
      () => {
        setPhase('landed');
        
        // Show badge after delay
        setTimeout(() => {
          setPhase('badge');
          
          // Complete after badge animation
          setTimeout(() => {
            setPhase('complete');
            onComplete?.();
          }, ANIMATION_TIMINGS.scoreReveal.auraIntensify);
        }, ANIMATION_TIMINGS.scoreReveal.tierBadge);
      }
    );
  }, [fromScore, toScore, easing, onComplete]);
  
  // Score size based on phase
  const scoreScale = phase === 'landed' ? 1.2 : phase === 'badge' || phase === 'complete' ? 1 : 1;
  
  return (
    <div className="relative flex flex-col items-center gap-4">
      {/* Glow effect behind score */}
      <motion.div
        className="absolute inset-0 -z-10"
        style={{
          background: `radial-gradient(circle, ${withAlpha(tierColors.glow, 0.3)} 0%, transparent 70%)`,
          filter: 'blur(40px)',
        }}
        animate={{
          scale: phase === 'badge' || phase === 'complete' ? [1, 1.2, 1] : 1,
          opacity: phase === 'complete' ? 0.6 : 0.3,
        }}
        transition={{
          duration: 2,
          repeat: phase === 'complete' ? Infinity : 0,
          ease: 'easeInOut',
        }}
      />
      
      {/* Score display */}
      <motion.div
        className="relative"
        animate={{
          scale: scoreScale,
        }}
        transition={{
          type: 'spring',
          stiffness: 300,
          damping: 15,
        }}
      >
        <motion.span
          className="text-7xl font-bold tabular-nums"
          style={{
            color: tierColors.primary,
            textShadow: `0 0 40px ${withAlpha(tierColors.glow, 0.5)}`,
          }}
          animate={{
            textShadow: phase === 'badge' || phase === 'complete'
              ? `0 0 60px ${withAlpha(tierColors.glow, 0.8)}`
              : `0 0 40px ${withAlpha(tierColors.glow, 0.5)}`,
          }}
        >
          {currentScore}
        </motion.span>
        
        {/* Sparkle effects on land */}
        <AnimatePresence>
          {phase === 'landed' && (
            <>
              {Array.from({ length: 8 }).map((_, i) => {
                const angle = (i / 8) * Math.PI * 2;
                return (
                  <motion.div
                    key={`sparkle-${i}`}
                    className="absolute w-2 h-2 rounded-full"
                    style={{
                      backgroundColor: tierColors.glow,
                      boxShadow: `0 0 8px ${tierColors.glow}`,
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
                      x: Math.cos(angle) * 80,
                      y: Math.sin(angle) * 80,
                      opacity: 0,
                      scale: 0,
                    }}
                    exit={{ opacity: 0 }}
                    transition={{
                      duration: 0.5,
                      ease: 'easeOut',
                    }}
                  />
                );
              })}
            </>
          )}
        </AnimatePresence>
      </motion.div>
      
      {/* Label */}
      <motion.div
        className="text-white/60 text-sm uppercase tracking-widest"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        Ivy+ Ready Score
      </motion.div>
      
      {/* Tier badge */}
      <AnimatePresence>
        {showTierBadge && (phase === 'badge' || phase === 'complete') && (
          <motion.div
            className="relative"
            initial={{ opacity: 0, scale: 0, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0 }}
            transition={{
              type: 'spring',
              stiffness: 400,
              damping: 20,
            }}
          >
            <div
              className="px-6 py-2 rounded-full text-sm font-bold uppercase tracking-wider"
              style={{
                background: `linear-gradient(135deg, ${tierColors.primary} 0%, ${tierColors.secondary} 100%)`,
                color: '#FFFFFF',
                boxShadow: `0 0 30px ${withAlpha(tierColors.glow, 0.5)}`,
              }}
            >
              {tierConfig.label}
            </div>
            
            {/* Badge glow pulse */}
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                background: `linear-gradient(135deg, ${tierColors.primary} 0%, ${tierColors.secondary} 100%)`,
                filter: 'blur(10px)',
                zIndex: -1,
              }}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.3, 0.5, 0.3],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Score range context */}
      <AnimatePresence>
        {phase === 'complete' && (
          <motion.div
            className="text-xs text-white/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {tierConfig.minScore}-{tierConfig.maxScore} range
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ScoreReveal;
