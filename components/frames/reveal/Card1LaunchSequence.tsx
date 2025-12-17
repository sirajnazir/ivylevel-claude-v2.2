'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils/cn';
import { LAUNCH_TIMINGS, EASING, ENGINE_PARTICLES, SCREEN_SHAKE } from '@/lib/constants/frame4.constants';
import { useFrame4Store } from '@/lib/store/useFrame4Store';
import type { LaunchPhase } from '@/lib/types/frame4.types';
import { Rocket, Sparkles } from 'lucide-react';

interface Card1LaunchSequenceProps {
  onComplete: () => void;
}

export function Card1LaunchSequence({ onComplete }: Card1LaunchSequenceProps) {
  const [countdown, setCountdown] = useState(3);
  const { launchPhase, setLaunchPhase, setIsAnimating, hasSeenLaunch } = useFrame4Store();
  const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number; size: number }>>([]);
  const [shake, setShake] = useState({ x: 0, y: 0 });

  // Start launch sequence on mount
  useEffect(() => {
    if (hasSeenLaunch) {
      // Skip to completion if already seen
      onComplete();
      return;
    }

    setLaunchPhase('countdown');
    setIsAnimating(true);
  }, [hasSeenLaunch, setLaunchPhase, setIsAnimating, onComplete]);

  // Countdown logic
  useEffect(() => {
    if (launchPhase !== 'countdown') return;

    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          setLaunchPhase('launch');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [launchPhase, setLaunchPhase]);

  // Phase progression
  useEffect(() => {
    if (launchPhase === 'launch') {
      const timer = setTimeout(() => setLaunchPhase('flight'), LAUNCH_TIMINGS.launch);
      return () => clearTimeout(timer);
    }
    if (launchPhase === 'flight') {
      const timer = setTimeout(() => setLaunchPhase('landing'), LAUNCH_TIMINGS.flight);
      return () => clearTimeout(timer);
    }
    if (launchPhase === 'landing') {
      // Trigger screen shake
      triggerScreenShake();
      const timer = setTimeout(() => setLaunchPhase('reveal'), LAUNCH_TIMINGS.landing);
      return () => clearTimeout(timer);
    }
    if (launchPhase === 'reveal') {
      const timer = setTimeout(() => {
        setIsAnimating(false);
        onComplete();
      }, LAUNCH_TIMINGS.revealDelay);
      return () => clearTimeout(timer);
    }
  }, [launchPhase, setLaunchPhase, setIsAnimating, onComplete]);

  // Generate engine particles
  useEffect(() => {
    if (launchPhase !== 'countdown' && launchPhase !== 'launch') return;

    const interval = setInterval(() => {
      setParticles((prev) => {
        const newParticle = {
          id: Date.now() + Math.random(),
          x: 50 + (Math.random() - 0.5) * 20,
          y: 70,
          size: ENGINE_PARTICLES.size.min + Math.random() * (ENGINE_PARTICLES.size.max - ENGINE_PARTICLES.size.min),
        };
        // Keep only last 20 particles
        return [...prev.slice(-19), newParticle];
      });
    }, 100);

    return () => clearInterval(interval);
  }, [launchPhase]);

  // Screen shake effect
  const triggerScreenShake = useCallback(() => {
    let intensity = SCREEN_SHAKE.intensity;
    const interval = setInterval(() => {
      setShake({
        x: (Math.random() - 0.5) * intensity * 2,
        y: (Math.random() - 0.5) * intensity * 2,
      });
      intensity *= SCREEN_SHAKE.decay;
      if (intensity < 0.5) {
        clearInterval(interval);
        setShake({ x: 0, y: 0 });
      }
    }, 16);
  }, []);

  return (
    <motion.div
      className="relative w-full h-full min-h-[400px] flex flex-col items-center justify-center overflow-hidden bg-gradient-to-b from-background-primary to-background-secondary rounded-2xl"
      style={{
        transform: `translate(${shake.x}px, ${shake.y}px)`,
      }}
    >
      {/* Stars background */}
      <div className="absolute inset-0 overflow-hidden">
        {Array.from({ length: 50 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0.3, 1, 0.3],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 2 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* Countdown display */}
      <AnimatePresence mode="wait">
        {launchPhase === 'countdown' && (
          <motion.div
            key="countdown"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 1.5, opacity: 0 }}
            className="z-10 text-center"
          >
            <motion.div
              key={countdown}
              initial={{ scale: 2, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.5, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="text-8xl font-display font-bold text-primary-blue"
            >
              {countdown}
            </motion.div>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-4 text-lg text-text-secondary"
            >
              Preparing for launch...
            </motion.p>
          </motion.div>
        )}

        {(launchPhase === 'launch' || launchPhase === 'flight') && (
          <motion.div
            key="rocket"
            initial={{ y: 100, opacity: 0 }}
            animate={{
              y: launchPhase === 'flight' ? -300 : 0,
              opacity: 1,
            }}
            exit={{ y: -500, opacity: 0 }}
            transition={{
              duration: launchPhase === 'flight' ? LAUNCH_TIMINGS.flight / 1000 : LAUNCH_TIMINGS.launch / 1000,
              ease: EASING.scoreReveal as unknown as string,
            }}
            className="z-10 flex flex-col items-center"
          >
            {/* Twin fleet rockets */}
            <div className="flex gap-8">
              <motion.div
                animate={{ rotate: [-5, 5, -5] }}
                transition={{ duration: 0.2, repeat: Infinity }}
              >
                <Rocket className="w-16 h-16 text-primary-blue transform -rotate-45" />
              </motion.div>
              <motion.div
                animate={{ rotate: [5, -5, 5] }}
                transition={{ duration: 0.2, repeat: Infinity }}
              >
                <Rocket className="w-16 h-16 text-warning-amber transform -rotate-45" />
              </motion.div>
            </div>

            {/* Engine glow */}
            <motion.div
              className="mt-2 w-24 h-32 bg-gradient-to-b from-warning-amber via-error-red to-transparent rounded-full blur-lg"
              animate={{
                scaleY: [1, 1.3, 1],
                opacity: [0.8, 1, 0.8],
              }}
              transition={{ duration: 0.1, repeat: Infinity }}
            />
          </motion.div>
        )}

        {launchPhase === 'landing' && (
          <motion.div
            key="landing"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="z-10 flex flex-col items-center"
          >
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.3, repeat: 2 }}
            >
              <Sparkles className="w-24 h-24 text-warning-amber" />
            </motion.div>
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 text-xl font-semibold text-text-primary"
            >
              Impact!
            </motion.p>
          </motion.div>
        )}

        {launchPhase === 'reveal' && (
          <motion.div
            key="reveal"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: 'spring', damping: 10 }}
            className="z-10 text-center"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <Sparkles className="w-16 h-16 text-success-green mx-auto" />
            </motion.div>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="mt-4 text-2xl font-display font-bold text-text-primary"
            >
              Your Results Are Ready!
            </motion.p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Engine particles */}
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: particle.size,
            height: particle.size,
            backgroundColor: ENGINE_PARTICLES.color,
          }}
          initial={{ opacity: 1, y: 0 }}
          animate={{ opacity: 0, y: 100 }}
          transition={{ duration: ENGINE_PARTICLES.lifetime / 1000 }}
        />
      ))}

      {/* Progress indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2">
        {(['countdown', 'launch', 'flight', 'landing', 'reveal'] as LaunchPhase[]).map((phase, idx) => {
          const phases: LaunchPhase[] = ['countdown', 'launch', 'flight', 'landing', 'reveal'];
          const currentIdx = phases.indexOf(launchPhase);
          return (
            <motion.div
              key={phase}
              className={cn(
                'w-2 h-2 rounded-full',
                idx <= currentIdx ? 'bg-primary-blue' : 'bg-border-subtle'
              )}
              animate={idx === currentIdx ? { scale: [1, 1.3, 1] } : {}}
              transition={{ duration: 0.5, repeat: Infinity }}
            />
          );
        })}
      </div>
    </motion.div>
  );
}

export default Card1LaunchSequence;
