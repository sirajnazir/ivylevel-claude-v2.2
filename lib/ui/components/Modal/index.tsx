/**
 * IvyQuest v3.0 — Modal Component
 * 
 * Dialog overlay with multiple sizes.
 * 
 * @version 1.0.0
 * @module components/Modal
 */

'use client';

import React, { useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../utils/cn';
import type {
  ModalProps,
  ModalBodyProps,
  ModalFooterProps,
  ModalSize,
} from '../../types/ui.types';

// ============================================================================
// SIZE STYLES
// ============================================================================

const sizeStyles: Record<ModalSize, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  full: 'max-w-[90vw] max-h-[90vh]',
};

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

const ModalBody: React.FC<ModalBodyProps> = ({ children, className }) => (
  <div className={cn('py-4 text-slate-300', className)}>
    {children}
  </div>
);

const ModalFooter: React.FC<ModalFooterProps> = ({ children, className }) => (
  <div className={cn(
    'flex items-center justify-end gap-3 pt-4',
    'border-t border-slate-700/50',
    className
  )}>
    {children}
  </div>
);

// ============================================================================
// MAIN COMPONENT
// ============================================================================

const Modal: React.FC<ModalProps> & {
  Body: typeof ModalBody;
  Footer: typeof ModalFooter;
} = ({
  isOpen,
  onClose,
  title,
  size = 'md',
  closeOnOverlay = true,
  showCloseButton = true,
  children,
  className,
  id,
  'data-testid': dataTestId,
}) => {
  // Handle escape key
  const handleEscape = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  }, [onClose]);
  
  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleEscape]);
  
  return (
    <AnimatePresence>
      {isOpen && (
        <div
          id={id}
          data-testid={dataTestId}
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeOnOverlay ? onClose : undefined}
          />
          
          {/* Modal content */}
          <motion.div
            className={cn(
              'relative w-full',
              'bg-slate-800 rounded-xl',
              'shadow-2xl shadow-black/30',
              'border border-slate-700/50',
              'overflow-hidden',
              sizeStyles[size],
              className
            )}
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
          >
            {/* Header */}
            {(title || showCloseButton) && (
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/50">
                {title && (
                  <h2 className="text-lg font-semibold text-white">
                    {title}
                  </h2>
                )}
                
                {showCloseButton && (
                  <button
                    type="button"
                    onClick={onClose}
                    className={cn(
                      'p-1 rounded-lg',
                      'text-slate-400 hover:text-white',
                      'hover:bg-slate-700',
                      'transition-colors duration-200',
                      !title && 'ml-auto'
                    )}
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
            )}
            
            {/* Content */}
            <div className="px-6 pb-6">
              {children}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

// Attach subcomponents
Modal.Body = ModalBody;
Modal.Footer = ModalFooter;

export { Modal };
export default Modal;
