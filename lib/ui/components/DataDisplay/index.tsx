/**
 * IvyQuest v3.0 — Data Display Components
 * 
 * StatCard, Avatar, and Tag for displaying data.
 * 
 * @version 1.0.0
 * @module components/DataDisplay
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

// ============================================================================
// STAT CARD
// ============================================================================

export interface StatCardProps {
  /** Stat label */
  label: string;
  
  /** Stat value */
  value: string | number;
  
  /** Change from previous */
  change?: number;
  
  /** Trend direction */
  trend?: 'up' | 'down' | 'stable';
  
  /** Icon element */
  icon?: React.ReactNode;
  
  /** Color theme */
  color?: 'cyan' | 'green' | 'purple' | 'amber' | 'red';
  
  /** Show animation */
  animate?: boolean;
  
  /** Additional class */
  className?: string;
}

const statColorConfig = {
  cyan: { bg: 'bg-cyan-500/10', icon: 'text-cyan-400', border: 'border-cyan-500/20' },
  green: { bg: 'bg-green-500/10', icon: 'text-green-400', border: 'border-green-500/20' },
  purple: { bg: 'bg-purple-500/10', icon: 'text-purple-400', border: 'border-purple-500/20' },
  amber: { bg: 'bg-amber-500/10', icon: 'text-amber-400', border: 'border-amber-500/20' },
  red: { bg: 'bg-red-500/10', icon: 'text-red-400', border: 'border-red-500/20' },
};

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  change,
  trend = 'stable',
  icon,
  color = 'cyan',
  animate = true,
  className,
}) => {
  const colors = statColorConfig[color];
  
  const getTrendIcon = () => {
    if (trend === 'up') {
      return (
        <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      );
    }
    if (trend === 'down') {
      return (
        <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      );
    }
    return null;
  };
  
  const content = (
    <div
      className={cn(
        'p-4 rounded-xl border',
        colors.bg,
        colors.border,
        className
      )}
    >
      <div className="flex items-start justify-between">
        {/* Icon */}
        {icon && (
          <div className={cn('p-2 rounded-lg', colors.bg, colors.icon)}>
            {icon}
          </div>
        )}
        
        {/* Trend */}
        {change !== undefined && (
          <div className="flex items-center gap-1">
            {getTrendIcon()}
            <span className={cn(
              'text-sm font-medium',
              trend === 'up' && 'text-green-400',
              trend === 'down' && 'text-red-400',
              trend === 'stable' && 'text-white/50'
            )}>
              {change > 0 ? '+' : ''}{change}
            </span>
          </div>
        )}
      </div>
      
      {/* Value */}
      <div className="mt-3">
        <p className="text-3xl font-bold text-white">{value}</p>
        <p className="text-sm text-white/50 mt-1">{label}</p>
      </div>
    </div>
  );
  
  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {content}
      </motion.div>
    );
  }
  
  return content;
};

// ============================================================================
// AVATAR
// ============================================================================

export interface AvatarProps {
  /** Image source */
  src?: string;
  
  /** Alt text */
  alt?: string;
  
  /** Fallback initials */
  name?: string;
  
  /** Size variant */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  
  /** Border color */
  borderColor?: string;
  
  /** Show online indicator */
  showStatus?: boolean;
  
  /** Online status */
  status?: 'online' | 'offline' | 'away' | 'busy';
  
  /** Additional class */
  className?: string;
}

const avatarSizeConfig = {
  xs: { container: 'w-6 h-6', text: 'text-xs', status: 'w-2 h-2' },
  sm: { container: 'w-8 h-8', text: 'text-sm', status: 'w-2.5 h-2.5' },
  md: { container: 'w-10 h-10', text: 'text-base', status: 'w-3 h-3' },
  lg: { container: 'w-12 h-12', text: 'text-lg', status: 'w-3.5 h-3.5' },
  xl: { container: 'w-16 h-16', text: 'text-xl', status: 'w-4 h-4' },
};

const statusColorConfig = {
  online: 'bg-green-500',
  offline: 'bg-gray-500',
  away: 'bg-amber-500',
  busy: 'bg-red-500',
};

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt,
  name,
  size = 'md',
  borderColor,
  showStatus = false,
  status = 'offline',
  className,
}) => {
  const config = avatarSizeConfig[size];
  
  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };
  
  const getBackgroundColor = (name?: string): string => {
    if (!name) return 'bg-gray-600';
    const colors = ['bg-cyan-600', 'bg-purple-600', 'bg-amber-600', 'bg-green-600', 'bg-red-600'];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  };
  
  return (
    <div className={cn('relative inline-block', className)}>
      <div
        className={cn(
          'rounded-full overflow-hidden flex items-center justify-center',
          config.container,
          !src && getBackgroundColor(name),
          borderColor && 'ring-2',
        )}
        style={borderColor ? { '--tw-ring-color': borderColor } as React.CSSProperties : undefined}
      >
        {src ? (
          <img
            src={src}
            alt={alt || name || 'Avatar'}
            className="w-full h-full object-cover"
          />
        ) : name ? (
          <span className={cn('font-medium text-white', config.text)}>
            {getInitials(name)}
          </span>
        ) : (
          <svg className="w-1/2 h-1/2 text-white/60" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
          </svg>
        )}
      </div>
      
      {/* Status indicator */}
      {showStatus && (
        <span
          className={cn(
            'absolute bottom-0 right-0 rounded-full border-2 border-slate-900',
            config.status,
            statusColorConfig[status]
          )}
        />
      )}
    </div>
  );
};

// ============================================================================
// AVATAR GROUP
// ============================================================================

export interface AvatarGroupProps {
  /** Avatars data */
  avatars: Array<{
    src?: string;
    name?: string;
  }>;
  
  /** Maximum to show */
  max?: number;
  
  /** Size variant */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  
  /** Additional class */
  className?: string;
}

export const AvatarGroup: React.FC<AvatarGroupProps> = ({
  avatars,
  max = 4,
  size = 'md',
  className,
}) => {
  const visible = avatars.slice(0, max);
  const remaining = avatars.length - max;
  const config = avatarSizeConfig[size];
  
  return (
    <div className={cn('flex -space-x-2', className)}>
      {visible.map((avatar, index) => (
        <Avatar
          key={index}
          {...avatar}
          size={size}
          className="ring-2 ring-slate-900"
        />
      ))}
      
      {remaining > 0 && (
        <div
          className={cn(
            'rounded-full bg-gray-700 flex items-center justify-center ring-2 ring-slate-900',
            config.container
          )}
        >
          <span className={cn('text-white font-medium', config.text)}>
            +{remaining}
          </span>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// TAG
// ============================================================================

export interface TagProps {
  /** Tag content */
  children: React.ReactNode;
  
  /** Color variant */
  color?: 'gray' | 'cyan' | 'green' | 'amber' | 'red' | 'purple';
  
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  
  /** Variant style */
  variant?: 'solid' | 'subtle' | 'outline';
  
  /** Left icon */
  leftIcon?: React.ReactNode;
  
  /** Removable */
  removable?: boolean;
  
  /** Remove handler */
  onRemove?: () => void;
  
  /** Additional class */
  className?: string;
}

const tagColorConfig = {
  gray: { solid: 'bg-gray-600', subtle: 'bg-gray-500/20 text-gray-300', outline: 'border-gray-500 text-gray-300' },
  cyan: { solid: 'bg-cyan-600', subtle: 'bg-cyan-500/20 text-cyan-300', outline: 'border-cyan-500 text-cyan-300' },
  green: { solid: 'bg-green-600', subtle: 'bg-green-500/20 text-green-300', outline: 'border-green-500 text-green-300' },
  amber: { solid: 'bg-amber-600', subtle: 'bg-amber-500/20 text-amber-300', outline: 'border-amber-500 text-amber-300' },
  red: { solid: 'bg-red-600', subtle: 'bg-red-500/20 text-red-300', outline: 'border-red-500 text-red-300' },
  purple: { solid: 'bg-purple-600', subtle: 'bg-purple-500/20 text-purple-300', outline: 'border-purple-500 text-purple-300' },
};

const tagSizeConfig = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

export const Tag: React.FC<TagProps> = ({
  children,
  color = 'gray',
  size = 'md',
  variant = 'subtle',
  leftIcon,
  removable = false,
  onRemove,
  className,
}) => {
  const colors = tagColorConfig[color];
  
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full font-medium',
        tagSizeConfig[size],
        variant === 'solid' && cn(colors.solid, 'text-white'),
        variant === 'subtle' && colors.subtle,
        variant === 'outline' && cn('border', colors.outline, 'bg-transparent'),
        className
      )}
    >
      {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
      {children}
      
      {removable && (
        <button
          onClick={onRemove}
          className="ml-1 hover:opacity-70 transition-opacity"
          aria-label="Remove"
        >
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </span>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

export default { StatCard, Avatar, AvatarGroup, Tag };
