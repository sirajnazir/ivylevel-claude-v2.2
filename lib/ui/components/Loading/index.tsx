/**
 * IvyQuest v3.0 — Loading Components
 * 
 * Spinner and Skeleton for loading states.
 * 
 * @version 1.0.0
 * @module components/Loading
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

// ============================================================================
// SPINNER TYPES
// ============================================================================

export interface SpinnerProps {
  /** Size variant */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  
  /** Color */
  color?: 'cyan' | 'white' | 'gray';
  
  /** Label for accessibility */
  label?: string;
  
  /** Additional class */
  className?: string;
}

// ============================================================================
// SPINNER SIZE CONFIG
// ============================================================================

const spinnerSizeConfig = {
  xs: 'w-3 h-3',
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12',
};

const spinnerColorConfig = {
  cyan: 'text-cyan-500',
  white: 'text-white',
  gray: 'text-gray-400',
};

// ============================================================================
// SPINNER COMPONENT
// ============================================================================

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'cyan',
  label = 'Loading...',
  className,
}) => {
  return (
    <div
      role="status"
      aria-label={label}
      className={cn('inline-flex', className)}
    >
      <motion.svg
        className={cn(spinnerSizeConfig[size], spinnerColorConfig[color])}
        viewBox="0 0 24 24"
        fill="none"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="3"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </motion.svg>
      <span className="sr-only">{label}</span>
    </div>
  );
};

// ============================================================================
// SKELETON TYPES
// ============================================================================

export interface SkeletonProps {
  /** Width */
  width?: string | number;
  
  /** Height */
  height?: string | number;
  
  /** Border radius */
  borderRadius?: 'none' | 'sm' | 'md' | 'lg' | 'full';
  
  /** Animation variant */
  animation?: 'pulse' | 'wave' | 'none';
  
  /** Additional class */
  className?: string;
}

// ============================================================================
// SKELETON COMPONENT
// ============================================================================

export const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height = 20,
  borderRadius = 'md',
  animation = 'pulse',
  className,
}) => {
  const radiusMap = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full',
  };
  
  const baseClass = cn(
    'bg-white/10',
    radiusMap[borderRadius],
    className
  );
  
  const style: React.CSSProperties = {
    width: width,
    height: height,
  };
  
  if (animation === 'pulse') {
    return (
      <motion.div
        className={baseClass}
        style={style}
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
      />
    );
  }
  
  if (animation === 'wave') {
    return (
      <div className={cn(baseClass, 'overflow-hidden')} style={style}>
        <motion.div
          className="h-full w-full bg-gradient-to-r from-transparent via-white/10 to-transparent"
          animate={{ x: ['-100%', '100%'] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>
    );
  }
  
  return <div className={baseClass} style={style} />;
};

// ============================================================================
// SKELETON TEXT
// ============================================================================

export interface SkeletonTextProps {
  /** Number of lines */
  lines?: number;
  
  /** Line spacing */
  spacing?: 'sm' | 'md' | 'lg';
  
  /** Additional class */
  className?: string;
}

export const SkeletonText: React.FC<SkeletonTextProps> = ({
  lines = 3,
  spacing = 'md',
  className,
}) => {
  const spacingMap = {
    sm: 'space-y-1',
    md: 'space-y-2',
    lg: 'space-y-3',
  };
  
  return (
    <div className={cn(spacingMap[spacing], className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          height={16}
          width={i === lines - 1 ? '60%' : '100%'}
        />
      ))}
    </div>
  );
};

// ============================================================================
// SKELETON CARD
// ============================================================================

export const SkeletonCard: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('bg-white/5 rounded-xl p-4 space-y-4', className)}>
      <div className="flex items-center gap-3">
        <Skeleton width={40} height={40} borderRadius="full" />
        <div className="flex-1 space-y-2">
          <Skeleton height={16} width="60%" />
          <Skeleton height={12} width="40%" />
        </div>
      </div>
      <SkeletonText lines={2} />
      <div className="flex gap-2">
        <Skeleton height={32} width={80} borderRadius="lg" />
        <Skeleton height={32} width={80} borderRadius="lg" />
      </div>
    </div>
  );
};

// ============================================================================
// LOADING OVERLAY
// ============================================================================

export interface LoadingOverlayProps {
  /** Is loading */
  isLoading: boolean;
  
  /** Loading text */
  text?: string;
  
  /** Blur background */
  blur?: boolean;
  
  /** Children to wrap */
  children: React.ReactNode;
  
  /** Additional class */
  className?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  text,
  blur = true,
  children,
  className,
}) => {
  return (
    <div className={cn('relative', className)}>
      {children}
      
      {isLoading && (
        <motion.div
          className={cn(
            'absolute inset-0 flex flex-col items-center justify-center',
            'bg-slate-900/80 z-10',
            blur && 'backdrop-blur-sm'
          )}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <Spinner size="lg" />
          {text && (
            <p className="mt-3 text-white/70 text-sm">{text}</p>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default Spinner;
