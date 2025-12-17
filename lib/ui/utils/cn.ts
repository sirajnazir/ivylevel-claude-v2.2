/**
 * IvyQuest v3.0 — Class Name Utility
 * 
 * Utility for conditionally joining class names.
 * 
 * @version 1.0.0
 * @module lib/utils/cn
 */

type ClassValue = string | number | boolean | undefined | null | ClassValue[];
type ClassObject = Record<string, boolean | undefined | null>;

/**
 * Conditionally join class names together
 * 
 * @example
 * cn('base', condition && 'conditional', { 'object-style': true })
 */
export function cn(...inputs: (ClassValue | ClassObject)[]): string {
  const classes: string[] = [];
  
  for (const input of inputs) {
    if (!input) continue;
    
    if (typeof input === 'string' || typeof input === 'number') {
      classes.push(String(input));
    } else if (Array.isArray(input)) {
      const inner = cn(...input);
      if (inner) classes.push(inner);
    } else if (typeof input === 'object') {
      for (const [key, value] of Object.entries(input)) {
        if (value) classes.push(key);
      }
    }
  }
  
  return classes.join(' ');
}

/**
 * Create a variant-based class generator
 * 
 * @example
 * const buttonStyles = cva('base-class', {
 *   variants: {
 *     variant: {
 *       primary: 'bg-blue-500',
 *       secondary: 'bg-gray-500',
 *     },
 *     size: {
 *       sm: 'text-sm',
 *       lg: 'text-lg',
 *     },
 *   },
 *   defaultVariants: {
 *     variant: 'primary',
 *     size: 'sm',
 *   },
 * });
 */
export function cva<T extends Record<string, Record<string, string>>>(
  base: string,
  config: {
    variants: T;
    defaultVariants?: { [K in keyof T]?: keyof T[K] };
    compoundVariants?: Array<{
      [K in keyof T]?: keyof T[K];
    } & { className: string }>;
  }
) {
  return (props?: { [K in keyof T]?: keyof T[K] } & { className?: string }) => {
    const { variants, defaultVariants = {}, compoundVariants = [] } = config;
    const { className: additionalClassName, ...variantProps } = props || {};
    
    const classes: string[] = [base];
    
    // Apply variant classes
    for (const [variantKey, variantOptions] of Object.entries(variants)) {
      const selectedVariant = (variantProps as Record<string, string>)?.[variantKey] 
        ?? defaultVariants[variantKey as keyof typeof defaultVariants];
      
      if (selectedVariant && variantOptions[selectedVariant as string]) {
        classes.push(variantOptions[selectedVariant as string]);
      }
    }
    
    // Apply compound variants
    for (const compound of compoundVariants) {
      const { className: compoundClass, ...conditions } = compound;
      
      const matches = Object.entries(conditions).every(([key, value]) => {
        const selectedValue = (variantProps as Record<string, string>)?.[key] 
          ?? defaultVariants[key as keyof typeof defaultVariants];
        return selectedValue === value;
      });
      
      if (matches && compoundClass) {
        classes.push(compoundClass);
      }
    }
    
    // Add additional className
    if (additionalClassName) {
      classes.push(additionalClassName);
    }
    
    return classes.filter(Boolean).join(' ');
  };
}

export default cn;
