/**
 * IvyQuest v3.0 — Base Twin Avatar
 * 
 * Core avatar component with aura and animations.
 * 
 * @version 1.0.0
 * @module components/TwinAvatar/BaseTwin
 */

'use client';

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  TWIN_SIZES,
  ANIMATION_TIMINGS,
  type TwinSize,
} from '../../constants/twin.constants';
import {
  getTierColors,
  withAlpha,
} from '../../utils/twinUtils';
import type { BaseTwinProps } from '../../types/twin.types';

// ============================================================================
// AVATAR SVG
// ============================================================================

const AvatarSilhouette: React.FC<{
  size: { width: number; height: number };
  color: string;
  glowColor: string;
}> = ({ size, color, glowColor }) => (
  <svg
    width={size.width}
    height={size.height}
    viewBox="0 0 64 96"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      {/* Glow filter */}
      <filter id="twinGlow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="3" result="coloredBlur" />
        <feMerge>
          <feMergeNode in="coloredBlur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
      
      {/* Body gradient */}
      <linearGradient id="bodyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor={color} stopOpacity="1" />
        <stop offset="100%" stopColor={glowColor} stopOpacity="0.8" />
      </linearGradient>
      
      {/* Core glow */}
      <radialGradient id="coreGlow" cx="50%" cy="30%" r="50%">
        <stop offset="0%" stopColor={glowColor} stopOpacity="0.8" />
        <stop offset="100%" stopColor={color} stopOpacity="0.2" />
      </radialGradient>
    </defs>
    
    {/* Body */}
    <ellipse
      cx="32"
      cy="70"
      rx="18"
      ry="24"
      fill="url(#bodyGradient)"
      filter="url(#twinGlow)"
    />
    
    {/* Head */}
    <circle
      cx="32"
      cy="24"
      r="16"
      fill="url(#bodyGradient)"
      filter="url(#twinGlow)"
    />
    
    {/* Core glow */}
    <ellipse
      cx="32"
      cy="55"
      rx="10"
      ry="12"
      fill="url(#coreGlow)"
    />
    
    {/* Face features (minimal) */}
    <ellipse cx="26" cy="22" rx="2" ry="3" fill={withAlpha(glowColor, 0.6)} />
    <ellipse cx="38" cy="22" rx="2" ry="3" fill={withAlpha(glowColor, 0.6)} />
  </svg>
);

// ============================================================================
// COMPONENT
// ============================================================================

const BaseTwin: React.FC<BaseTwinProps> = ({
  score,
  tier,
  style,
  size = 'md',
  isActive = true,
  showParticles = true,
  showAura = true,
  className = '',
  onClick,
  animationState = 'idle',
}) => {
  // Get tier colors
  const tierColors = useMemo(() => getTierColors(tier), [tier]);
  
  // Get size config
  const sizeConfig = TWIN_SIZES[size];
  
  // Animation variants
  const containerVariants = {
    idle: {
      y: [0, -4, 0],
      transition: {
        duration: ANIMATION_TIMINGS.idleBob / 1000,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    },
    active: {
      y: [0, -8, 0],
      scale: [1, 1.02, 1],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    },
    celebrating: {
      y: [0, -16, 0],
      scale: [1, 1.1, 1],
      rotate: [0, 5, -5, 0],
      transition: {
        duration: 0.8,
        repeat: 3,
        ease: 'easeOut',
      },
    },
    transitioning: {
      y: -50,
      opacity: 0,
      scale: 0.8,
      transition: {
        duration: 0.3,
        ease: 'easeIn',
      },
    },
  };
  
  // Aura animation
  const auraVariants = {
    animate: {
      scale: [1, 1.1, 1],
      opacity: [0.4, 0.6, 0.4],
      transition: {
        duration: ANIMATION_TIMINGS.auraFloat / 1000,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    },
  };
  
  return (
    <motion.div
      className={`relative inline-flex items-center justify-center ${className}`}
      style={{
        width: sizeConfig.width,
        height: sizeConfig.height,
      }}
      variants={containerVariants}
      animate={animationState}
      onClick={onClick}
      whileHover={onClick ? { scale: 1.05 } : undefined}
      whileTap={onClick ? { scale: 0.98 } : undefined}
    >
      {/* Aura layers */}
      {showAura && (
        <>
          {/* Outer aura */}
          <motion.div
            className="absolute inset-0 rounded-full"
            style={{
              background: `radial-gradient(circle, ${withAlpha(tierColors.glow, 0.3)} 0%, transparent 70%)`,
              filter: 'blur(20px)',
            }}
            variants={auraVariants}
            animate="animate"
          />
          
          {/* Inner aura */}
          <motion.div
            className="absolute inset-[20%] rounded-full"
            style={{
              background: `radial-gradient(circle, ${withAlpha(tierColors.primary, 0.4)} 0%, transparent 70%)`,
              filter: 'blur(10px)',
            }}
            variants={auraVariants}
            animate="animate"
            transition={{ delay: 0.5 }}
          />
        </>
      )}
      
      {/* Avatar silhouette */}
      <div className="relative z-10">
        <AvatarSilhouette
          size={sizeConfig}
          color={tierColors.primary}
          glowColor={tierColors.glow}
        />
      </div>
      
      {/* Score badge */}
      {score > 0 && (
        <motion.div
          className="absolute -bottom-2 left-1/2 -translate-x-1/2 z-20"
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, type: 'spring', stiffness: 300 }}
        >
          <div
            className="px-3 py-1 rounded-full text-sm font-bold shadow-lg"
            style={{
              background: tierColors.primary,
              color: '#FFFFFF',
              boxShadow: `0 0 20px ${withAlpha(tierColors.glow, 0.5)}`,
            }}
          >
            {Math.round(score)}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default BaseTwin;
