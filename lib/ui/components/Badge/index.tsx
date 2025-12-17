/**
 * IvyQuest v3.0 — Badge Component
 * 
 * Status indicators and labels.
 * 
 * @version 1.0.0
 * @module components/Badge
 */

'use client';

import React from 'react';
import { cn } from '../../utils/cn';
import type { BadgeProps, BadgeVariant, Size } from '../../types/ui.types';

// ============================================================================
// STYLES
// ============================================================================

const baseStyles = `
  inline-flex items-center gap-1.5
  font-medium rounded-full
  whitespace-nowrap
`;

const variantStyles: Record<BadgeVariant, string> = {
  success: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
  warning: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
  error: 'bg-red-500/20 text-red-400 border border-red-500/30',
  info: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
  neutral: 'bg-slate-500/20 text-slate-400 border border-slate-500/30',
};

const sizeStyles: Record<Size, string> = {
  sm: 'h-5 px-2 text-xs',
  md: 'h-6 px-2.5 text-xs',
  lg: 'h-7 px-3 text-sm',
};

const dotColors: Record<BadgeVariant, string> = {
  success: 'bg-emerald-400',
  warning: 'bg-amber-400',
  error: 'bg-red-400',
  info: 'bg-blue-400',
  neutral: 'bg-slate-400',
};

// ============================================================================
// COMPONENT
// ============================================================================

const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  size = 'md',
  dot = false,
  icon,
  children,
  className,
  id,
  'data-testid': dataTestId,
}) => {
  const dotSize = size === 'sm' ? 'w-1.5 h-1.5' : 'w-2 h-2';
  
  return (
    <span
      id={id}
      data-testid={dataTestId}
      className={cn(
        baseStyles,
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {dot && (
        <span className={cn(dotSize, 'rounded-full', dotColors[variant])} />
      )}
      {icon && !dot && (
        <span className="flex-shrink-0">{icon}</span>
      )}
      {children}
    </span>
  );
};

export { Badge };
export default Badge;
