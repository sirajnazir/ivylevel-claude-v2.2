/**
 * IvyQuest v3.0 — Twin Aura Effect
 * 
 * Animated glow effect for twin avatars.
 * 
 * @version 1.0.0
 * @module components/TwinAvatar/TwinAura
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { AURA_CONFIG, ANIMATION_TIMINGS } from '../../constants/twin.constants';
import { withAlpha } from '../../utils/twinUtils';
import type { TwinAuraProps } from '../../types/twin.types';

// ============================================================================
// COMPONENT
// ============================================================================

const TwinAura: React.FC<TwinAuraProps> = ({
  primaryColor,
  secondaryColor,
  intensity,
  blur = AURA_CONFIG.baseBlur,
  breathing = true,
  speedMultiplier = 1,
  size,
}) => {
  const effectiveBlur = AURA_CONFIG.baseBlur + (AURA_CONFIG.maxBlur - AURA_CONFIG.baseBlur) * intensity;
  const shadowSize = AURA_CONFIG.baseShadowSize + (AURA_CONFIG.maxShadowSize - AURA_CONFIG.baseShadowSize) * intensity;
  
  // Breathing animation
  const breatheVariants = {
    animate: {
      scale: [1, 1 + AURA_CONFIG.breathingAmplitude * intensity, 1],
      opacity: [intensity * 0.5, intensity * 0.7, intensity * 0.5],
      transition: {
        duration: (ANIMATION_TIMINGS.auraFloat / 1000) / speedMultiplier,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    },
    static: {
      scale: 1,
      opacity: intensity * 0.6,
    },
  };
  
  // Create multiple glow layers for depth
  const layers = Array.from({ length: AURA_CONFIG.glowLayers }, (_, i) => {
    const layerIndex = i + 1;
    const layerScale = 1 + (layerIndex * 0.15);
    const layerOpacity = intensity * (1 - (layerIndex * 0.25));
    const layerBlur = effectiveBlur * layerScale;
    
    return (
      <motion.div
        key={`aura-layer-${i}`}
        className="absolute inset-0 rounded-full"
        style={{
          background: `radial-gradient(circle, ${withAlpha(primaryColor, layerOpacity)} 0%, ${secondaryColor ? withAlpha(secondaryColor, layerOpacity * 0.5) : 'transparent'} 50%, transparent 70%)`,
          filter: `blur(${layerBlur}px)`,
          transform: `scale(${layerScale})`,
        }}
        variants={breatheVariants}
        animate={breathing ? 'animate' : 'static'}
        transition={{ delay: i * 0.2 }}
      />
    );
  });
  
  return (
    <div
      className="absolute"
      style={{
        width: size.width * 1.5,
        height: size.height * 1.5,
        left: '50%',
        top: '50%',
        transform: 'translate(-50%, -50%)',
        pointerEvents: 'none',
      }}
    >
      {layers}
      
      {/* Central glow pulse */}
      <motion.div
        className="absolute rounded-full"
        style={{
          width: '40%',
          height: '40%',
          left: '30%',
          top: '30%',
          background: `radial-gradient(circle, ${withAlpha(primaryColor, intensity * 0.8)} 0%, transparent 70%)`,
          filter: `blur(${effectiveBlur / 2}px)`,
        }}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [intensity * 0.6, intensity * 0.9, intensity * 0.6],
        }}
        transition={{
          duration: (ANIMATION_TIMINGS.pulseInterval / 1000) / speedMultiplier,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
    </div>
  );
};

export default TwinAura;
