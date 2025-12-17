/**
 * IvyQuest v3.0 — Validation Feedback Components
 * 
 * Field and card-level validation UI.
 * 
 * @version 1.0.0
 * @module components/ValidationFeedback
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { VALIDATION_STATES } from '../../constants/feedback.constants';
import { getValidationConfig, getValidationSummary } from '../../utils/feedbackUtils';
import type { FieldValidationProps, CardValidationProps } from '../../types/feedback.types';

// ============================================================================
// FIELD VALIDATION
// ============================================================================

const FieldValidation: React.FC<FieldValidationProps> = ({
  state,
  message,
  showIcon = true,
  animate = true,
  className = '',
}) => {
  const config = getValidationConfig(state);
  
  if (state === 'empty' && !message) {
    return null;
  }
  
  const content = (
    <div
      className={`flex items-center gap-2 text-sm ${className}`}
      style={{ color: config.textColor }}
    >
      {showIcon && config.icon && (
        <span className="flex-shrink-0">{config.icon}</span>
      )}
      {message && <span>{message}</span>}
    </div>
  );
  
  if (!animate) {
    return content;
  }
  
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={state}
        initial={{ opacity: 0, y: -5, height: 0 }}
        animate={{ opacity: 1, y: 0, height: 'auto' }}
        exit={{ opacity: 0, y: 5, height: 0 }}
        transition={{ duration: 0.2 }}
      >
        {content}
      </motion.div>
    </AnimatePresence>
  );
};

// ============================================================================
// CARD VALIDATION
// ============================================================================

const CardValidation: React.FC<CardValidationProps> = ({
  cardId,
  fields,
  isValid,
  showSummary = true,
  requiredFields = [],
}) => {
  const summary = getValidationSummary(fields);
  const invalidFields = Object.entries(fields).filter(([_, v]) => v.state === 'invalid');
  const emptyRequiredFields = requiredFields.filter(
    fieldId => fields[fieldId]?.state === 'empty'
  );
  
  return (
    <div className="space-y-2">
      {/* Invalid field messages */}
      <AnimatePresence>
        {invalidFields.map(([fieldId, field]) => (
          <motion.div
            key={fieldId}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 10 }}
            className="flex items-start gap-2 text-sm"
            style={{ color: VALIDATION_STATES.invalid.textColor }}
          >
            <span className="flex-shrink-0">{VALIDATION_STATES.invalid.icon}</span>
            <span>{field.message || `${fieldId} is invalid`}</span>
          </motion.div>
        ))}
      </AnimatePresence>
      
      {/* Empty required fields */}
      <AnimatePresence>
        {emptyRequiredFields.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-sm text-yellow-500"
          >
            {emptyRequiredFields.length === 1
              ? `Please fill in: ${emptyRequiredFields[0]}`
              : `Please fill in: ${emptyRequiredFields.join(', ')}`}
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Summary */}
      {showSummary && !isValid && (
        <div className="text-xs text-gray-500 mt-2">
          {summary.valid} of {summary.total} fields complete
        </div>
      )}
      
      {/* All valid indicator */}
      <AnimatePresence>
        {isValid && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="flex items-center gap-2 text-sm"
            style={{ color: VALIDATION_STATES.valid.textColor }}
          >
            <span>{VALIDATION_STATES.valid.icon}</span>
            <span>All fields complete!</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ============================================================================
// INPUT WRAPPER WITH VALIDATION
// ============================================================================

interface ValidatedInputWrapperProps {
  state: FieldValidationProps['state'];
  message?: string;
  children: React.ReactNode;
  className?: string;
}

const ValidatedInputWrapper: React.FC<ValidatedInputWrapperProps> = ({
  state,
  message,
  children,
  className = '',
}) => {
  const config = getValidationConfig(state);
  
  return (
    <div className={`relative ${className}`}>
      <div
        className="rounded-lg transition-all duration-200"
        style={{
          borderWidth: '2px',
          borderStyle: 'solid',
          borderColor: config.borderColor,
          backgroundColor: config.backgroundColor,
        }}
      >
        {children}
      </div>
      
      {message && (
        <div className="mt-1">
          <FieldValidation state={state} message={message} showIcon={true} />
        </div>
      )}
    </div>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

export { FieldValidation, CardValidation, ValidatedInputWrapper };
export default FieldValidation;
