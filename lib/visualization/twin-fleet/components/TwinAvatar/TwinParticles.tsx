/**
 * IvyQuest v3.0 — Twin Particles
 * 
 * Animated particle system for twin avatars.
 * 
 * @version 1.0.0
 * @module components/TwinAvatar/TwinParticles
 */

'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PARTICLE_CONFIG } from '../../constants/twin.constants';
import { createParticle, updateParticle } from '../../utils/twinUtils';
import type { TwinParticlesProps, Particle } from '../../types/twin.types';

// ============================================================================
// COMPONENT
// ============================================================================

const TwinParticles: React.FC<TwinParticlesProps> = ({
  color,
  secondaryColor,
  density = 1,
  pattern = 'default',
  speedMultiplier = 1,
  bounds,
  isActive = true,
}) => {
  const [particles, setParticles] = useState<Particle[]>([]);
  const frameRef = useRef<number>(0);
  const lastTimeRef = useRef<number>(0);
  
  // Get particle config based on density
  const config = density >= 1.2 
    ? PARTICLE_CONFIG.dense 
    : density <= 0.6 
    ? PARTICLE_CONFIG.sparse 
    : PARTICLE_CONFIG.base;
  
  const particleCount = Math.round(config.count * density);
  
  // Initialize particles
  useEffect(() => {
    if (!isActive) {
      setParticles([]);
      return;
    }
    
    const initialParticles: Particle[] = [];
    for (let i = 0; i < particleCount; i++) {
      initialParticles.push(
        createParticle(bounds, {
          color: i % 2 === 0 ? color : (secondaryColor || color),
          sizeRange: config.size,
          speedRange: { min: config.speed.min * speedMultiplier, max: config.speed.max * speedMultiplier },
          lifespanRange: config.lifespan,
        })
      );
    }
    setParticles(initialParticles);
  }, [isActive, particleCount, bounds.width, bounds.height, color, secondaryColor]);
  
  // Animation loop
  useEffect(() => {
    if (!isActive) return;
    
    const animate = (time: number) => {
      if (lastTimeRef.current === 0) {
        lastTimeRef.current = time;
      }
      
      const deltaTime = (time - lastTimeRef.current) / 1000;
      lastTimeRef.current = time;
      
      setParticles(prevParticles => {
        return prevParticles.map(p => {
          const updated = updateParticle(p, deltaTime, bounds);
          
          // Respawn if dead
          if (updated.age >= updated.lifespan) {
            return createParticle(bounds, {
              color: Math.random() > 0.5 ? color : (secondaryColor || color),
              sizeRange: config.size,
              speedRange: { min: config.speed.min * speedMultiplier, max: config.speed.max * speedMultiplier },
              lifespanRange: config.lifespan,
            });
          }
          
          return updated;
        });
      });
      
      frameRef.current = requestAnimationFrame(animate);
    };
    
    frameRef.current = requestAnimationFrame(animate);
    
    return () => {
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
    };
  }, [isActive, bounds, color, secondaryColor, config, speedMultiplier]);
  
  // Get pattern-specific movement modifications
  const getPatternOffset = useCallback((particle: Particle, time: number) => {
    switch (pattern) {
      case 'structured':
        // Grid-like movement
        return {
          x: Math.round(particle.x / 20) * 20,
          y: Math.round(particle.y / 20) * 20,
        };
      case 'flowing':
        // Wave-like movement
        return {
          x: particle.x + Math.sin(time / 1000 + particle.y / 50) * 5,
          y: particle.y,
        };
      case 'expansive':
        // Outward burst
        const centerX = bounds.width / 2;
        const centerY = bounds.height / 2;
        const angle = Math.atan2(particle.y - centerY, particle.x - centerX);
        const dist = Math.sin(time / 500) * 10;
        return {
          x: particle.x + Math.cos(angle) * dist,
          y: particle.y + Math.sin(angle) * dist,
        };
      case 'orbital':
        // Circular orbit
        const orbitSpeed = 0.001 * speedMultiplier;
        const orbitRadius = 20;
        const orbitAngle = time * orbitSpeed;
        return {
          x: particle.x + Math.cos(orbitAngle + particles.indexOf(particle)) * orbitRadius,
          y: particle.y + Math.sin(orbitAngle + particles.indexOf(particle)) * orbitRadius,
        };
      default:
        return { x: particle.x, y: particle.y };
    }
  }, [pattern, bounds, speedMultiplier, particles]);
  
  return (
    <div
      className="absolute inset-0 pointer-events-none overflow-hidden"
      style={{ width: bounds.width, height: bounds.height }}
    >
      <AnimatePresence>
        {particles.map(particle => (
          <motion.div
            key={particle.id}
            className="absolute rounded-full"
            style={{
              width: particle.size,
              height: particle.size,
              backgroundColor: particle.color,
              boxShadow: `0 0 ${particle.size * 2}px ${particle.color}`,
            }}
            initial={{ opacity: 0, scale: 0 }}
            animate={{
              x: particle.x,
              y: particle.y,
              opacity: particle.opacity,
              scale: 1,
            }}
            exit={{ opacity: 0, scale: 0 }}
            transition={{
              type: 'spring',
              stiffness: 50,
              damping: 10,
            }}
          />
        ))}
      </AnimatePresence>
    </div>
  );
};

export default TwinParticles;
