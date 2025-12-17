/**
 * IvyQuest v3.0 — Card Component
 * 
 * Content container with multiple variants.
 * 
 * @version 1.0.0
 * @module components/Card
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';
import type {
  CardProps,
  CardHeaderProps,
  CardBodyProps,
  CardFooterProps,
  CardVariant,
  CardPadding,
} from '../../types/ui.types';

// ============================================================================
// STYLES
// ============================================================================

const baseStyles = 'rounded-xl overflow-hidden';

const variantStyles: Record<CardVariant, string> = {
  default: `
    bg-slate-800/50
    border border-slate-700/50
  `,
  elevated: `
    bg-slate-800
    shadow-xl shadow-black/20
    border border-slate-700/30
  `,
  outlined: `
    bg-transparent
    border-2 border-slate-600
  `,
  glass: `
    bg-white/5
    backdrop-blur-xl
    border border-white/10
    shadow-lg shadow-black/10
  `,
};

const paddingStyles: Record<CardPadding, string> = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-6',
};

const interactiveStyles = `
  cursor-pointer
  transition-all duration-200
  hover:border-cyan-500/50
  hover:shadow-lg hover:shadow-cyan-500/10
`;

const selectedStyles = `
  border-cyan-500
  ring-2 ring-cyan-500/30
`;

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

const CardHeader: React.FC<CardHeaderProps> = ({
  children,
  action,
  className,
}) => (
  <div className={cn(
    'flex items-center justify-between',
    'pb-3 mb-3 border-b border-slate-700/50',
    className
  )}>
    <div className="font-semibold text-white">{children}</div>
    {action && <div>{action}</div>}
  </div>
);

const CardBody: React.FC<CardBodyProps> = ({
  children,
  className,
}) => (
  <div className={cn('text-slate-300', className)}>
    {children}
  </div>
);

const CardFooter: React.FC<CardFooterProps> = ({
  children,
  align = 'right',
  className,
}) => {
  const alignStyles = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
    between: 'justify-between',
  };
  
  return (
    <div className={cn(
      'flex items-center gap-3',
      'pt-4 mt-4 border-t border-slate-700/50',
      alignStyles[align],
      className
    )}>
      {children}
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

const Card: React.FC<CardProps> & {
  Header: typeof CardHeader;
  Body: typeof CardBody;
  Footer: typeof CardFooter;
} = ({
  variant = 'default',
  padding = 'md',
  interactive = false,
  selected = false,
  onClick,
  children,
  className,
  id,
  'data-testid': dataTestId,
}) => {
  const Component = interactive ? motion.div : 'div';
  const motionProps = interactive ? {
    whileHover: { y: -2 },
    whileTap: { scale: 0.99 },
  } : {};
  
  return (
    <Component
      id={id}
      data-testid={dataTestId}
      onClick={onClick}
      className={cn(
        baseStyles,
        variantStyles[variant],
        paddingStyles[padding],
        interactive && interactiveStyles,
        selected && selectedStyles,
        className
      )}
      {...motionProps}
    >
      {children}
    </Component>
  );
};

// Attach subcomponents
Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;

export { Card };
export default Card;
