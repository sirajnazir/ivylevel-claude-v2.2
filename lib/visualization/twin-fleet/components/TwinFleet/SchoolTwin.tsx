/**
 * IvyQuest v3.0 — School Twin Avatar
 * 
 * School-specific twin with branded colors and fit indicator.
 * 
 * @version 1.0.0
 * @module components/TwinFleet/SchoolTwin
 */

'use client';

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  TWIN_SIZES,
  SCHOOL_COLORS,
  type TwinSize,
} from '../../constants/twin.constants';
import {
  getTierFromScore,
  withAlpha,
  getProbabilityColor,
  formatProbability,
} from '../../utils/twinUtils';
import type { SchoolTwinProps } from '../../types/twin.types';

// ============================================================================
// SCHOOL AVATAR SVG
// ============================================================================

const SchoolAvatarSilhouette: React.FC<{
  size: { width: number; height: number };
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
}> = ({ size, primaryColor, secondaryColor, accentColor }) => (
  <svg
    width={size.width}
    height={size.height}
    viewBox="0 0 64 96"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      {/* School gradient */}
      <linearGradient id="schoolBodyGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor={primaryColor} stopOpacity="1" />
        <stop offset="50%" stopColor={secondaryColor} stopOpacity="0.9" />
        <stop offset="100%" stopColor={primaryColor} stopOpacity="1" />
      </linearGradient>
      
      {/* Glow filter */}
      <filter id="schoolGlow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="2" result="coloredBlur" />
        <feMerge>
          <feMergeNode in="coloredBlur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
      
      {/* Core highlight */}
      <radialGradient id="schoolCore" cx="50%" cy="40%" r="50%">
        <stop offset="0%" stopColor={accentColor} stopOpacity="0.6" />
        <stop offset="100%" stopColor={primaryColor} stopOpacity="0.2" />
      </radialGradient>
    </defs>
    
    {/* Body */}
    <ellipse
      cx="32"
      cy="68"
      rx="16"
      ry="22"
      fill="url(#schoolBodyGradient)"
      filter="url(#schoolGlow)"
    />
    
    {/* Head */}
    <circle
      cx="32"
      cy="24"
      r="14"
      fill="url(#schoolBodyGradient)"
      filter="url(#schoolGlow)"
    />
    
    {/* Core highlight */}
    <ellipse
      cx="32"
      cy="55"
      rx="8"
      ry="10"
      fill="url(#schoolCore)"
    />
    
    {/* School emblem hint (small circle) */}
    <circle
      cx="32"
      cy="58"
      r="4"
      fill={accentColor}
      opacity="0.8"
    />
  </svg>
);

// ============================================================================
// FIT RING
// ============================================================================

const FitRing: React.FC<{
  probability: number;
  size: { width: number; height: number };
  color: string;
}> = ({ probability, size, color }) => {
  const ringSize = Math.max(size.width, size.height) * 1.3;
  const strokeWidth = 4;
  const radius = (ringSize - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = probability / 100;
  const offset = circumference * (1 - progress);
  
  return (
    <svg
      width={ringSize}
      height={ringSize}
      className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
      style={{ transform: 'translate(-50%, -50%) rotate(-90deg)' }}
    >
      {/* Background ring */}
      <circle
        cx={ringSize / 2}
        cy={ringSize / 2}
        r={radius}
        fill="none"
        stroke={withAlpha(color, 0.2)}
        strokeWidth={strokeWidth}
      />
      
      {/* Progress ring */}
      <motion.circle
        cx={ringSize / 2}
        cy={ringSize / 2}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={circumference}
        initial={{ strokeDashoffset: circumference }}
        animate={{ strokeDashoffset: offset }}
        transition={{ duration: 1, ease: 'easeOut' }}
        style={{
          filter: `drop-shadow(0 0 4px ${color})`,
        }}
      />
    </svg>
  );
};

// ============================================================================
// COMPONENT
// ============================================================================

const SchoolTwin: React.FC<SchoolTwinProps> = ({
  schoolId,
  probability,
  categoryScores,
  styleMatch = 0,
  isSelected = false,
  showFitRing = true,
  size = 'md',
  isActive = true,
  showParticles = false,
  showAura = true,
  label,
  className = '',
  onClick,
  animationState = 'idle',
}) => {
  // Get school colors
  const schoolColors = SCHOOL_COLORS[schoolId];
  const sizeConfig = TWIN_SIZES[size];
  
  // Calculate derived tier from overall score
  const overallScore = (
    categoryScores.aptitude * 0.35 +
    categoryScores.passion * 0.30 +
    categoryScores.community * 0.20 +
    categoryScores.operating * 0.15
  );
  
  // Probability color
  const probColor = useMemo(() => getProbabilityColor(probability), [probability]);
  
  // Animation variants
  const containerVariants = {
    idle: {
      y: [0, -3, 0],
      transition: {
        duration: 2.5,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    },
    active: {
      y: [0, -6, 0],
      scale: [1, 1.03, 1],
      transition: {
        duration: 1.8,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    },
    selected: {
      scale: 1.1,
      y: -10,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 20,
      },
    },
  };
  
  return (
    <motion.div
      className={`relative inline-flex flex-col items-center ${className}`}
      variants={containerVariants}
      animate={isSelected ? 'selected' : (animationState === 'active' ? 'active' : 'idle')}
      onClick={onClick}
      whileHover={onClick ? { scale: 1.05, y: -5 } : undefined}
      whileTap={onClick ? { scale: 0.98 } : undefined}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {/* Fit ring */}
      {showFitRing && (
        <FitRing
          probability={probability}
          size={sizeConfig}
          color={probColor}
        />
      )}
      
      {/* School aura */}
      {showAura && (
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{
            background: `radial-gradient(circle, ${withAlpha(schoolColors.primary, 0.3)} 0%, transparent 70%)`,
            filter: 'blur(15px)',
            transform: 'scale(1.2)',
          }}
          animate={{
            scale: [1.2, 1.3, 1.2],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      )}
      
      {/* Avatar */}
      <div
        className="relative z-10"
        style={{
          width: sizeConfig.width,
          height: sizeConfig.height,
        }}
      >
        <SchoolAvatarSilhouette
          size={sizeConfig}
          primaryColor={schoolColors.primary}
          secondaryColor={schoolColors.secondary}
          accentColor={schoolColors.accent}
        />
      </div>
      
      {/* Style match indicator */}
      {styleMatch > 0.7 && (
        <motion.div
          className="absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center z-20"
          style={{
            background: schoolColors.accent,
            boxShadow: `0 0 10px ${schoolColors.accent}`,
          }}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 400, damping: 15 }}
        >
          <span className="text-xs">⚡</span>
        </motion.div>
      )}
      
      {/* School label and probability */}
      <motion.div
        className="mt-2 text-center z-20"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="text-xs font-semibold text-white/80">
          {label || schoolColors.name}
        </div>
        <div
          className="text-sm font-bold"
          style={{ color: probColor }}
        >
          {formatProbability(probability)}
        </div>
      </motion.div>
      
      {/* Selection indicator */}
      {isSelected && (
        <motion.div
          className="absolute -bottom-4 left-1/2 -translate-x-1/2"
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ type: 'spring', stiffness: 400 }}
        >
          <div
            className="w-0 h-0"
            style={{
              borderLeft: '8px solid transparent',
              borderRight: '8px solid transparent',
              borderBottom: `8px solid ${schoolColors.primary}`,
            }}
          />
        </motion.div>
      )}
    </motion.div>
  );
};

export default SchoolTwin;
