/**
 * IvyQuest v3.0 — Progress Components
 * 
 * Progress bars, rings, and step indicators.
 * 
 * @version 1.0.0
 * @module components/Progress
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';
import { tierColors } from '../../constants/theme.constants';
import type {
  ProgressBarProps,
  ProgressRingProps,
  ProgressStepsProps,
  ProgressColor,
  Size,
  ExtendedSize,
} from '../../types/ui.types';

// ============================================================================
// COLOR MAPPING
// ============================================================================

const colorStyles: Record<ProgressColor, string> = {
  primary: 'bg-gradient-to-r from-cyan-500 to-blue-500',
  success: 'bg-gradient-to-r from-emerald-500 to-green-500',
  warning: 'bg-gradient-to-r from-amber-500 to-orange-500',
  error: 'bg-gradient-to-r from-red-500 to-rose-500',
  tier: '', // Handled dynamically
};

// ============================================================================
// PROGRESS BAR
// ============================================================================

const sizeHeights: Record<Size, string> = {
  sm: 'h-1.5',
  md: 'h-2',
  lg: 'h-3',
};

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  color = 'primary',
  size = 'md',
  showLabel = false,
  animated = true,
  label,
  tierColor,
  className,
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const barColor = color === 'tier' && tierColor
    ? tierColor
    : colorStyles[color];
  
  return (
    <div className={cn('w-full', className)}>
      {(label || showLabel) && (
        <div className="flex items-center justify-between mb-1.5 text-sm">
          {label && <span className="text-slate-400">{label}</span>}
          {showLabel && <span className="text-white font-medium">{Math.round(percentage)}%</span>}
        </div>
      )}
      
      <div className={cn(
        'w-full rounded-full overflow-hidden bg-slate-700/50',
        sizeHeights[size]
      )}>
        <motion.div
          className={cn(
            'h-full rounded-full',
            color !== 'tier' && barColor
          )}
          style={color === 'tier' && tierColor ? { backgroundColor: tierColor } : undefined}
          initial={animated ? { width: 0 } : { width: `${percentage}%` }}
          animate={{ width: `${percentage}%` }}
          transition={animated ? { duration: 0.8, ease: 'easeOut' } : { duration: 0 }}
        />
      </div>
    </div>
  );
};

// ============================================================================
// PROGRESS RING
// ============================================================================

const ringSizes: Record<ExtendedSize, { size: number; stroke: number }> = {
  xs: { size: 32, stroke: 3 },
  sm: { size: 48, stroke: 4 },
  md: { size: 64, stroke: 5 },
  lg: { size: 96, stroke: 6 },
  xl: { size: 128, stroke: 8 },
};

export const ProgressRing: React.FC<ProgressRingProps> = ({
  value,
  max = 100,
  size = 'md',
  strokeWidth,
  color = 'primary',
  showLabel = true,
  label,
  tierColor,
  className,
}) => {
  const sizeConfig = ringSizes[size];
  const actualSize = sizeConfig.size;
  const actualStroke = strokeWidth ?? sizeConfig.stroke;
  const radius = (actualSize - actualStroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const offset = circumference - (percentage / 100) * circumference;
  
  const strokeColor = color === 'tier' && tierColor
    ? tierColor
    : color === 'primary' ? '#00D4FF'
    : color === 'success' ? '#10B981'
    : color === 'warning' ? '#F59E0B'
    : '#EF4444';
  
  return (
    <div className={cn('relative inline-flex', className)}>
      <svg width={actualSize} height={actualSize}>
        {/* Background circle */}
        <circle
          cx={actualSize / 2}
          cy={actualSize / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={actualStroke}
          className="text-slate-700/50"
        />
        
        {/* Progress circle */}
        <motion.circle
          cx={actualSize / 2}
          cy={actualSize / 2}
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth={actualStroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          style={{
            transform: 'rotate(-90deg)',
            transformOrigin: '50% 50%',
          }}
        />
      </svg>
      
      {/* Center label */}
      {showLabel && (
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-white font-bold" style={{ fontSize: actualSize / 4 }}>
            {Math.round(value)}
          </span>
          {label && (
            <span className="text-slate-400 text-xs">{label}</span>
          )}
        </div>
      )}
    </div>
  );
};

// ============================================================================
// PROGRESS STEPS
// ============================================================================

export const ProgressSteps: React.FC<ProgressStepsProps> = ({
  current,
  total,
  labels,
  clickable = false,
  onStepClick,
  className,
}) => {
  return (
    <div className={cn('flex items-center w-full', className)}>
      {Array.from({ length: total }).map((_, index) => {
        const stepNumber = index + 1;
        const isComplete = stepNumber < current;
        const isCurrent = stepNumber === current;
        const isClickable = clickable && (isComplete || stepNumber <= current + 1);
        
        return (
          <React.Fragment key={index}>
            {/* Step dot */}
            <motion.button
              type="button"
              disabled={!isClickable}
              onClick={() => isClickable && onStepClick?.(stepNumber)}
              className={cn(
                'relative flex flex-col items-center',
                isClickable && 'cursor-pointer'
              )}
              whileHover={isClickable ? { scale: 1.1 } : undefined}
              whileTap={isClickable ? { scale: 0.95 } : undefined}
            >
              {/* Circle */}
              <div
                className={cn(
                  'w-8 h-8 rounded-full flex items-center justify-center',
                  'text-sm font-medium transition-all duration-200',
                  isComplete && 'bg-cyan-500 text-white',
                  isCurrent && 'bg-cyan-500/20 text-cyan-400 ring-2 ring-cyan-500',
                  !isComplete && !isCurrent && 'bg-slate-700 text-slate-500'
                )}
              >
                {isComplete ? (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  stepNumber
                )}
              </div>
              
              {/* Label */}
              {labels?.[index] && (
                <span
                  className={cn(
                    'absolute -bottom-6 text-xs whitespace-nowrap',
                    isCurrent ? 'text-cyan-400' : 'text-slate-500'
                  )}
                >
                  {labels[index]}
                </span>
              )}
            </motion.button>
            
            {/* Connector line */}
            {index < total - 1 && (
              <div className="flex-1 h-0.5 mx-2 bg-slate-700">
                <motion.div
                  className="h-full bg-cyan-500"
                  initial={{ width: 0 }}
                  animate={{ width: isComplete ? '100%' : '0%' }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};

// ============================================================================
// COMBINED EXPORT
// ============================================================================

const Progress = {
  Bar: ProgressBar,
  Ring: ProgressRing,
  Steps: ProgressSteps,
};

export { Progress };
export default Progress;
