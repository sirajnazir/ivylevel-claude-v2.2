/**
 * IvyQuest v3.0 — Input Component
 * 
 * Form input with label, hints, and validation.
 * 
 * @version 1.0.0
 * @module components/Input
 */

'use client';

import React, { forwardRef, useId } from 'react';
import { cn } from '../../utils/cn';
import type { InputProps, Size } from '../../types/ui.types';

// ============================================================================
// STYLES
// ============================================================================

const baseInputStyles = `
  w-full
  bg-slate-800/50
  border border-slate-600
  rounded-lg
  text-white
  placeholder-slate-500
  transition-all duration-200
  focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20
  disabled:opacity-50 disabled:cursor-not-allowed
`;

const sizeStyles: Record<Size, string> = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-10 px-3 text-sm',
  lg: 'h-12 px-4 text-base',
};

const errorStyles = 'border-red-500 focus:border-red-500 focus:ring-red-500/20';

// ============================================================================
// COMPONENT
// ============================================================================

const Input = forwardRef<HTMLInputElement, InputProps>(({
  type = 'text',
  label,
  placeholder,
  value,
  onChange,
  onBlur,
  onFocus,
  onKeyDown,
  error,
  hint,
  disabled = false,
  required = false,
  readOnly = false,
  size = 'md',
  leftIcon,
  rightIcon,
  min,
  max,
  step,
  autoFocus = false,
  autoComplete,
  className,
  id: providedId,
  'data-testid': dataTestId,
}, ref) => {
  const generatedId = useId();
  const id = providedId || generatedId;
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };
  
  return (
    <div className={cn('w-full', className)}>
      {/* Label */}
      {label && (
        <label
          htmlFor={id}
          className="block mb-1.5 text-sm font-medium text-slate-300"
        >
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}
      
      {/* Input wrapper */}
      <div className="relative">
        {/* Left icon */}
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            {leftIcon}
          </div>
        )}
        
        {/* Input */}
        <input
          ref={ref}
          id={id}
          type={type}
          data-testid={dataTestId}
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
          onBlur={onBlur}
          onFocus={onFocus}
          onKeyDown={onKeyDown}
          disabled={disabled}
          required={required}
          readOnly={readOnly}
          min={min}
          max={max}
          step={step}
          autoFocus={autoFocus}
          autoComplete={autoComplete}
          className={cn(
            baseInputStyles,
            sizeStyles[size],
            error && errorStyles,
            !!leftIcon && 'pl-10',
            !!rightIcon && 'pr-10'
          )}
        />
        
        {/* Right icon */}
        {rightIcon && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
            {rightIcon}
          </div>
        )}
      </div>
      
      {/* Error message */}
      {error && (
        <p className="mt-1.5 text-sm text-red-400 flex items-center gap-1">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
      
      {/* Hint text */}
      {hint && !error && (
        <p className="mt-1.5 text-sm text-slate-500">
          {hint}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export { Input };
export default Input;
