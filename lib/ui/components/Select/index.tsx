/**
 * IvyQuest v3.0 — Select Component
 * 
 * Dropdown selection with single and multi-select support.
 * 
 * @version 1.0.0
 * @module components/Select
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../utils/cn';

// ============================================================================
// TYPES
// ============================================================================

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
  icon?: React.ReactNode;
}

export interface SelectProps {
  /** Select options */
  options: SelectOption[];
  
  /** Current value(s) */
  value?: string | string[];
  
  /** Change handler */
  onChange?: (value: string | string[]) => void;
  
  /** Label text */
  label?: string;
  
  /** Placeholder text */
  placeholder?: string;
  
  /** Allow multiple selection */
  isMulti?: boolean;
  
  /** Searchable options */
  isSearchable?: boolean;
  
  /** Disabled state */
  isDisabled?: boolean;
  
  /** Error message */
  error?: string;
  
  /** Hint text */
  hint?: string;
  
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  
  /** Full width */
  fullWidth?: boolean;
  
  /** Additional class */
  className?: string;
}

// ============================================================================
// SIZE CONFIG
// ============================================================================

const sizeConfig = {
  sm: {
    height: 'h-8',
    text: 'text-sm',
    padding: 'px-2',
    icon: 'w-4 h-4',
  },
  md: {
    height: 'h-10',
    text: 'text-base',
    padding: 'px-3',
    icon: 'w-5 h-5',
  },
  lg: {
    height: 'h-12',
    text: 'text-lg',
    padding: 'px-4',
    icon: 'w-6 h-6',
  },
};

// ============================================================================
// COMPONENT
// ============================================================================

export const Select: React.FC<SelectProps> = ({
  options,
  value,
  onChange,
  label,
  placeholder = 'Select...',
  isMulti = false,
  isSearchable = false,
  isDisabled = false,
  error,
  hint,
  size = 'md',
  fullWidth = false,
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  
  const config = sizeConfig[size];
  
  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearch('');
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  // Filter options by search
  const filteredOptions = options.filter(opt =>
    opt.label.toLowerCase().includes(search.toLowerCase())
  );
  
  // Get selected labels
  const getSelectedLabels = (): string => {
    if (!value) return '';
    
    if (isMulti && Array.isArray(value)) {
      if (value.length === 0) return '';
      if (value.length === 1) {
        return options.find(o => o.value === value[0])?.label || '';
      }
      return `${value.length} selected`;
    }
    
    return options.find(o => o.value === value)?.label || '';
  };
  
  // Handle option select
  const handleSelect = (optionValue: string) => {
    if (isMulti) {
      const currentValues = Array.isArray(value) ? value : [];
      const newValues = currentValues.includes(optionValue)
        ? currentValues.filter(v => v !== optionValue)
        : [...currentValues, optionValue];
      onChange?.(newValues);
    } else {
      onChange?.(optionValue);
      setIsOpen(false);
      setSearch('');
    }
  };
  
  // Check if option is selected
  const isSelected = (optionValue: string): boolean => {
    if (isMulti && Array.isArray(value)) {
      return value.includes(optionValue);
    }
    return value === optionValue;
  };
  
  return (
    <div
      ref={containerRef}
      className={cn('relative', fullWidth ? 'w-full' : 'w-64', className)}
    >
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-white/80 mb-1.5">
          {label}
        </label>
      )}
      
      {/* Trigger */}
      <button
        type="button"
        onClick={() => !isDisabled && setIsOpen(!isOpen)}
        className={cn(
          'relative w-full flex items-center justify-between',
          config.height,
          config.padding,
          config.text,
          'bg-white/5 border rounded-lg text-left',
          'transition-all duration-200',
          isOpen && !error && 'border-cyan-500 ring-2 ring-cyan-500/20',
          error ? 'border-red-500' : 'border-white/10',
          isDisabled && 'opacity-50 cursor-not-allowed',
          !isDisabled && 'hover:border-white/20'
        )}
        disabled={isDisabled}
      >
        {isSearchable && isOpen ? (
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-transparent outline-none text-white placeholder-white/40"
            placeholder={placeholder}
            autoFocus
          />
        ) : (
          <span className={cn(
            'flex-1 truncate',
            getSelectedLabels() ? 'text-white' : 'text-white/40'
          )}>
            {getSelectedLabels() || placeholder}
          </span>
        )}
        
        {/* Chevron */}
        <svg
          className={cn(
            'w-5 h-5 text-white/40 transition-transform',
            isOpen && 'rotate-180'
          )}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
            className={cn(
              'absolute z-50 w-full mt-1',
              'bg-slate-800 border border-white/10 rounded-lg shadow-xl',
              'max-h-60 overflow-auto'
            )}
          >
            {filteredOptions.length === 0 ? (
              <div className="px-3 py-2 text-sm text-white/40">
                No options found
              </div>
            ) : (
              filteredOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => !option.disabled && handleSelect(option.value)}
                  className={cn(
                    'w-full flex items-center gap-2 px-3 py-2 text-left',
                    config.text,
                    'transition-colors',
                    option.disabled && 'opacity-50 cursor-not-allowed',
                    isSelected(option.value)
                      ? 'bg-cyan-500/20 text-cyan-400'
                      : 'text-white hover:bg-white/5'
                  )}
                  disabled={option.disabled}
                >
                  {/* Multi-select checkbox */}
                  {isMulti && (
                    <div className={cn(
                      'w-4 h-4 rounded border flex items-center justify-center',
                      isSelected(option.value)
                        ? 'bg-cyan-500 border-cyan-500'
                        : 'border-white/30'
                    )}>
                      {isSelected(option.value) && (
                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  )}
                  
                  {/* Icon */}
                  {option.icon && (
                    <span className="flex-shrink-0">{option.icon}</span>
                  )}
                  
                  {/* Label */}
                  <span className="flex-1">{option.label}</span>
                  
                  {/* Single select check */}
                  {!isMulti && isSelected(option.value) && (
                    <svg className="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Error */}
      {error && (
        <p className="mt-1 text-sm text-red-400">{error}</p>
      )}
      
      {/* Hint */}
      {hint && !error && (
        <p className="mt-1 text-sm text-white/40">{hint}</p>
      )}
    </div>
  );
};

export default Select;
