/**
 * IvyQuest v3.0 — Materialize Sequence
 * 
 * Twin avatar spawn animation.
 * 
 * @version 1.0.0
 * @module components/animations/MaterializeSequence
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ANIMATION_TIMINGS, SCORE_TIERS } from '../../constants/twin.constants';
import { getTierColors, withAlpha, getAnimationPhase } from '../../utils/twinUtils';
import type { MaterializeSequenceProps } from '../../types/twin.types';

// ============================================================================
// PHASES
// ============================================================================

const MATERIALIZE_PHASES = [
  { name: 'converge', duration: ANIMATION_TIMINGS.materialize.particleConverge },
  { name: 'silhouette', duration: ANIMATION_TIMINGS.materialize.silhouetteForm },
  { name: 'features', duration: ANIMATION_TIMINGS.materialize.featuresResolve },
  { name: 'aura', duration: ANIMATION_TIMINGS.materialize.auraActivate },
];

// ============================================================================
// COMPONENT
// ============================================================================

const MaterializeSequence: React.FC<MaterializeSequenceProps> = ({
  duration = ANIMATION_TIMINGS.materialize.total,
  targetScore = 75,
  tier = 'competitive',
  style,
  onComplete,
  onProgress,
  autoPlay = true,
}) => {
  const [elapsed, setElapsed] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [isComplete, setIsComplete] = useState(false);
  
  const tierColors = getTierColors(tier);
  
  // Animation loop
  useEffect(() => {
    if (!isPlaying || isComplete) return;
    
    const startTime = performance.now();
    let animationFrame: number;
    
    const animate = (time: number) => {
      const currentElapsed = time - startTime;
      setElapsed(currentElapsed);
      
      const progress = Math.min(currentElapsed / duration, 1);
      onProgress?.(progress);
      
      if (currentElapsed < duration) {
        animationFrame = requestAnimationFrame(animate);
      } else {
        setIsComplete(true);
        onComplete?.();
      }
    };
    
    animationFrame = requestAnimationFrame(animate);
    
    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [isPlaying, isComplete, duration, onProgress, onComplete]);
  
  // Get current phase
  const { phase, progress: phaseProgress } = getAnimationPhase(elapsed, MATERIALIZE_PHASES);
  
  // Particle count based on phase
  const particleCount = phase === 'converge' ? 50 : phase === 'silhouette' ? 30 : 10;
  
  return (
    <div className="relative w-64 h-80 mx-auto">
      {/* Converging particles */}
      <AnimatePresence>
        {phase === 'converge' && (
          <>
            {Array.from({ length: particleCount }).map((_, i) => {
              const angle = (i / particleCount) * Math.PI * 2;
              const distance = 150 * (1 - phaseProgress);
              const startX = Math.cos(angle) * 200;
              const startY = Math.sin(angle) * 200;
              
              return (
                <motion.div
                  key={`particle-${i}`}
                  className="absolute w-2 h-2 rounded-full"
                  style={{
                    backgroundColor: tierColors.glow,
                    boxShadow: `0 0 10px ${tierColors.glow}`,
                    left: '50%',
                    top: '40%',
                  }}
                  initial={{
                    x: startX,
                    y: startY,
                    opacity: 0,
                    scale: 0.5,
                  }}
                  animate={{
                    x: Math.cos(angle) * distance,
                    y: Math.sin(angle) * distance,
                    opacity: 1,
                    scale: 1,
                  }}
                  exit={{
                    opacity: 0,
                    scale: 0,
                  }}
                  transition={{
                    duration: MATERIALIZE_PHASES[0].duration / 1000,
                    ease: 'easeInOut',
                  }}
                />
              );
            })}
          </>
        )}
      </AnimatePresence>
      
      {/* Silhouette forming */}
      <AnimatePresence>
        {(phase === 'silhouette' || phase === 'features' || phase === 'aura') && (
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            {/* Glowing silhouette */}
            <motion.div
              className="relative"
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ 
                opacity: phase === 'silhouette' ? phaseProgress : 1,
                scale: phase === 'silhouette' ? 0.5 + phaseProgress * 0.5 : 1,
              }}
              transition={{ duration: 0.3 }}
            >
              {/* Head */}
              <motion.div
                className="absolute w-20 h-20 rounded-full"
                style={{
                  background: `radial-gradient(circle, ${tierColors.primary} 0%, ${tierColors.secondary} 100%)`,
                  filter: `blur(${phase === 'silhouette' ? 10 : 0}px)`,
                  top: '-40px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  boxShadow: `0 0 30px ${withAlpha(tierColors.glow, 0.5)}`,
                }}
                animate={{
                  filter: phase === 'features' || phase === 'aura' ? 'blur(0px)' : 'blur(10px)',
                }}
              />
              
              {/* Body */}
              <motion.div
                className="w-24 h-36 rounded-full"
                style={{
                  background: `radial-gradient(circle at 50% 30%, ${tierColors.primary} 0%, ${tierColors.secondary} 100%)`,
                  filter: `blur(${phase === 'silhouette' ? 10 : 0}px)`,
                  boxShadow: `0 0 40px ${withAlpha(tierColors.glow, 0.5)}`,
                }}
                animate={{
                  filter: phase === 'features' || phase === 'aura' ? 'blur(0px)' : 'blur(10px)',
                }}
              />
              
              {/* Core glow */}
              <motion.div
                className="absolute w-12 h-16 rounded-full"
                style={{
                  background: `radial-gradient(circle, ${tierColors.glow} 0%, transparent 70%)`,
                  top: '30%',
                  left: '50%',
                  transform: 'translateX(-50%)',
                }}
                initial={{ opacity: 0 }}
                animate={{ opacity: phase === 'features' || phase === 'aura' ? 0.8 : 0 }}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Aura activation */}
      <AnimatePresence>
        {phase === 'aura' && (
          <>
            {/* Outer aura burst */}
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                background: `radial-gradient(circle, ${withAlpha(tierColors.glow, 0.4)} 0%, transparent 70%)`,
              }}
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 2, opacity: [0, 0.8, 0] }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
            
            {/* Inner aura stabilize */}
            <motion.div
              className="absolute inset-[20%] rounded-full"
              style={{
                background: `radial-gradient(circle, ${withAlpha(tierColors.primary, 0.3)} 0%, transparent 70%)`,
                filter: 'blur(15px)',
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1, scale: [1, 1.1, 1] }}
              transition={{ duration: 1, repeat: Infinity, ease: 'easeInOut' }}
            />
          </>
        )}
      </AnimatePresence>
      
      {/* Score reveal on complete */}
      <AnimatePresence>
        {isComplete && (
          <motion.div
            className="absolute bottom-0 left-1/2 -translate-x-1/2"
            initial={{ opacity: 0, y: 20, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          >
            <div
              className="px-6 py-2 rounded-full text-xl font-bold shadow-lg"
              style={{
                background: tierColors.primary,
                color: '#FFFFFF',
                boxShadow: `0 0 30px ${withAlpha(tierColors.glow, 0.6)}`,
              }}
            >
              {Math.round(targetScore)}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Phase indicator (dev) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-xs text-white/30">
          Phase: {phase} ({Math.round(phaseProgress * 100)}%)
        </div>
      )}
    </div>
  );
};

export default MaterializeSequence;
