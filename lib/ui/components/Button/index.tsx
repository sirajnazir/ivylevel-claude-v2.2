/**
 * IvyQuest v3.0 — Button Component
 * 
 * Primary action button with multiple variants.
 * 
 * @version 1.0.0
 * @module components/Button
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';
import { colors, componentSizes, borderRadius, transitions } from '../../constants/theme.constants';
import type { ButtonProps, ButtonVariant, Size } from '../../types/ui.types';

// ============================================================================
// STYLES
// ============================================================================

const baseStyles = `
  inline-flex items-center justify-center gap-2
  font-medium rounded-lg
  transition-all duration-200
  focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900
  disabled:opacity-50 disabled:cursor-not-allowed
`;

const variantStyles: Record<ButtonVariant, string> = {
  primary: `
    bg-gradient-to-r from-cyan-500 to-blue-500
    hover:from-cyan-400 hover:to-blue-400
    text-white
    shadow-lg shadow-cyan-500/25
    focus:ring-cyan-500
  `,
  secondary: `
    bg-slate-700 hover:bg-slate-600
    text-white
    border border-slate-600
    focus:ring-slate-500
  `,
  ghost: `
    bg-transparent hover:bg-slate-800
    text-slate-300 hover:text-white
    focus:ring-slate-500
  `,
  danger: `
    bg-red-600 hover:bg-red-500
    text-white
    shadow-lg shadow-red-500/25
    focus:ring-red-500
  `,
  success: `
    bg-emerald-600 hover:bg-emerald-500
    text-white
    shadow-lg shadow-emerald-500/25
    focus:ring-emerald-500
  `,
};

const sizeStyles: Record<Size, string> = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-6 text-base',
};

// ============================================================================
// LOADING SPINNER
// ============================================================================

const LoadingSpinner: React.FC<{ size: Size }> = ({ size }) => {
  const spinnerSize = size === 'sm' ? 14 : size === 'lg' ? 20 : 16;
  
  return (
    <svg
      className="animate-spin"
      width={spinnerSize}
      height={spinnerSize}
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
};

// ============================================================================
// COMPONENT
// ============================================================================

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  type = 'button',
  onClick,
  children,
  className,
  id,
  'data-testid': dataTestId,
}) => {
  const isDisabled = disabled || loading;
  
  return (
    <motion.button
      type={type}
      id={id}
      data-testid={dataTestId}
      disabled={isDisabled}
      onClick={onClick}
      className={cn(
        baseStyles,
        variantStyles[variant],
        sizeStyles[size],
        fullWidth && 'w-full',
        className
      )}
      whileHover={!isDisabled ? { scale: 1.02 } : undefined}
      whileTap={!isDisabled ? { scale: 0.98 } : undefined}
    >
      {loading ? (
        <LoadingSpinner size={size} />
      ) : (
        leftIcon
      )}
      
      <span>{children}</span>
      
      {!loading && rightIcon}
    </motion.button>
  );
};

export { Button };
export default Button;
