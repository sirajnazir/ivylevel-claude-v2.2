/**
 * IvyQuest v3.0 — Launch Sequence Animation
 * 
 * Frame transition animation with light streak effect.
 * 
 * @version 1.0.0
 * @module components/animations/LaunchSequence
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ANIMATION_TIMINGS } from '../../constants/twin.constants';
import type { LaunchSequenceProps } from '../../types/twin.types';

// ============================================================================
// COMPONENT
// ============================================================================

const LaunchSequence: React.FC<LaunchSequenceProps> = ({
  fromFrame,
  toFrame,
  duration = ANIMATION_TIMINGS.launch.total,
  onComplete,
  skip = false,
}) => {
  const [phase, setPhase] = useState<'dim' | 'elevate' | 'streak' | 'transition' | 'complete'>('dim');
  
  // Skip animation if requested
  useEffect(() => {
    if (skip) {
      onComplete?.();
      return;
    }
    
    const timings = ANIMATION_TIMINGS.launch;
    
    // Phase progression
    const timeouts: NodeJS.Timeout[] = [];
    
    timeouts.push(setTimeout(() => setPhase('elevate'), timings.backgroundDim));
    timeouts.push(setTimeout(() => setPhase('streak'), timings.backgroundDim + timings.twinElevate));
    timeouts.push(setTimeout(() => setPhase('transition'), timings.backgroundDim + timings.twinElevate + timings.lightStreak));
    timeouts.push(setTimeout(() => {
      setPhase('complete');
      onComplete?.();
    }, duration));
    
    return () => {
      timeouts.forEach(clearTimeout);
    };
  }, [skip, duration, onComplete]);
  
  if (skip) return null;
  
  return (
    <AnimatePresence>
      {phase !== 'complete' && (
        <motion.div
          className="fixed inset-0 z-50 pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {/* Background dim */}
          <motion.div
            className="absolute inset-0 bg-black"
            initial={{ opacity: 0 }}
            animate={{
              opacity: phase === 'dim' ? 0.7 :
                       phase === 'elevate' ? 0.8 :
                       phase === 'streak' ? 0.9 :
                       1,
            }}
            transition={{ duration: 0.15 }}
          />
          
          {/* Twin silhouette */}
          <motion.div
            className="absolute left-1/2 -translate-x-1/2"
            initial={{ top: '60%' }}
            animate={{
              top: phase === 'dim' ? '60%' :
                   phase === 'elevate' ? '40%' :
                   '-20%',
              scale: phase === 'streak' || phase === 'transition' ? 0.5 : 1,
              opacity: phase === 'transition' ? 0 : 1,
            }}
            transition={{
              duration: 0.15,
              ease: phase === 'streak' ? 'easeIn' : 'easeOut',
            }}
          >
            {/* Glowing orb representation of twin */}
            <div className="w-16 h-24 relative">
              <div
                className="absolute inset-0 rounded-full"
                style={{
                  background: 'radial-gradient(circle, #00D4FF 0%, #3B82F6 50%, transparent 70%)',
                  filter: 'blur(8px)',
                }}
              />
              <div
                className="absolute top-0 left-1/2 -translate-x-1/2 w-10 h-10 rounded-full"
                style={{
                  background: 'radial-gradient(circle, #FFFFFF 0%, #00D4FF 70%)',
                  filter: 'blur(4px)',
                }}
              />
            </div>
          </motion.div>
          
          {/* Light streak effect */}
          <AnimatePresence>
            {(phase === 'streak' || phase === 'transition') && (
              <>
                {/* Central streak */}
                <motion.div
                  className="absolute left-1/2 -translate-x-1/2 w-2"
                  style={{
                    background: 'linear-gradient(to top, transparent 0%, #00D4FF 30%, #FFFFFF 50%, #00D4FF 70%, transparent 100%)',
                    top: '-10%',
                    height: '120%',
                  }}
                  initial={{ opacity: 0, scaleY: 0 }}
                  animate={{ opacity: 1, scaleY: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
                />
                
                {/* Side streaks */}
                {[-30, -15, 15, 30].map((offset, i) => (
                  <motion.div
                    key={`streak-${i}`}
                    className="absolute w-1"
                    style={{
                      left: `calc(50% + ${offset}px)`,
                      background: 'linear-gradient(to top, transparent 0%, rgba(0, 212, 255, 0.5) 50%, transparent 100%)',
                      top: '-10%',
                      height: '120%',
                    }}
                    initial={{ opacity: 0, scaleY: 0 }}
                    animate={{ opacity: 0.6, scaleY: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15, delay: i * 0.02 }}
                  />
                ))}
                
                {/* Flash at peak */}
                <motion.div
                  className="absolute inset-0 bg-white"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: phase === 'transition' ? [0, 0.8, 0] : 0 }}
                  transition={{ duration: 0.15 }}
                />
              </>
            )}
          </AnimatePresence>
          
          {/* Frame indicator */}
          <motion.div
            className="absolute bottom-8 left-1/2 -translate-x-1/2 text-white/60 text-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: phase === 'dim' || phase === 'elevate' ? 1 : 0 }}
          >
            Frame {fromFrame} → Frame {toFrame}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default LaunchSequence;
