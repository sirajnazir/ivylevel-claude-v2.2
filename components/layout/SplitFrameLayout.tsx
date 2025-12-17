'use client';

import React from 'react';
import { BRAND_COLORS } from '@/lib/constants/brand';

/**
 * SplitFrameLayout - 2-column responsive layout for frames
 *
 * Layout Structure:
 * ┌──────────────────────────────────────────────────────┐
 * │  Left Panel (40%)       │  Right Panel (60%)        │
 * │  ─────────────────      │  ─────────────────        │
 * │  Input Cards            │  IV Animation             │
 * │  (children)             │  + Code Box               │
 * └──────────────────────────────────────────────────────┘
 *
 * Responsive Behavior:
 * - Desktop (≥1024px): 2 columns side-by-side
 * - Mobile/Tablet (<1024px): Stack vertically
 */

interface SplitFrameLayoutProps {
  /** Left panel content (input cards) */
  children: React.ReactNode;

  /** Right panel: IV animation component (centered in container) */
  ivAnimation?: React.ReactNode;

  /** Right panel: Full-width custom content (no centering wrapper) */
  rightPanel?: React.ReactNode;

  /** Right panel: Code box content (single message or array of messages) */
  codeBoxContent?: string | string[];

  /** Left panel width (default: "40%") - used for inline style on desktop */
  leftWidth?: string;

  /** Right panel width (default: "60%") - used for inline style on desktop */
  rightWidth?: string;

  /** Additional CSS classes for the container */
  className?: string;

  /** Hide the code box even if content is provided */
  hideCodeBox?: boolean;

  /** Hide the IV animation section even if provided */
  hideIVAnimation?: boolean;
}

/**
 * Code box styling constants
 * Using brand orange colors for the code box
 */
const CODE_BOX_STYLES = {
  container: {
    backgroundColor: BRAND_COLORS.primaryBg,
    border: `2px solid ${BRAND_COLORS.primary}20`,
    borderRadius: '12px',
    padding: '24px',
  },
  text: {
    color: BRAND_COLORS.secondary,
    fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
    fontSize: '14px',
    lineHeight: '1.6',
  },
} as const;

/**
 * IV Animation section styling constants
 */
const IV_ANIMATION_STYLES = {
  container: {
    backgroundColor: BRAND_COLORS.bgPrimary,
    border: `1px solid ${BRAND_COLORS.borderLight}`,
    borderRadius: '12px',
    padding: '32px',
    minHeight: '300px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
  },
} as const;

export function SplitFrameLayout({
  children,
  ivAnimation,
  rightPanel,
  codeBoxContent,
  leftWidth = '40%',
  rightWidth = '60%',
  className = '',
  hideCodeBox = false,
  hideIVAnimation = false,
}: SplitFrameLayoutProps) {
  // Determine if we should show right panel sections
  const showIVAnimation = ivAnimation && !hideIVAnimation;
  const showRightPanel = !!rightPanel;
  const showCodeBox = codeBoxContent && !hideCodeBox;
  const hasRightPanelContent = showIVAnimation || showRightPanel || showCodeBox;

  // Convert codeBoxContent to array for consistent rendering
  const codeMessages = codeBoxContent
    ? Array.isArray(codeBoxContent)
      ? codeBoxContent
      : [codeBoxContent]
    : [];

  return (
    <div className={`w-full ${className}`}>
      {/* Desktop: 2-column grid, Mobile: Stack vertically */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
        {/* LEFT PANEL: Input Cards (children) */}
        <div
          className="space-y-6"
          style={{
            // Apply custom width on desktop via CSS custom property
            // The grid will handle the actual layout
          }}
        >
          {children}
        </div>

        {/* RIGHT PANEL: IV Animation / Custom Panel / Code Box */}
        {hasRightPanelContent && (
          <div className="space-y-6">
            {/* IV Animation Section (centered) - renders first */}
            {showIVAnimation && (
              <div style={IV_ANIMATION_STYLES.container}>
                {ivAnimation}
              </div>
            )}

            {/* Custom Right Panel (full-width, no wrapper) */}
            {showRightPanel && rightPanel}

            {/* Code Box Section */}
            {showCodeBox && (
              <div style={CODE_BOX_STYLES.container}>
                <div className="space-y-3">
                  {codeMessages.map((message, index) => (
                    <p
                      key={index}
                      style={CODE_BOX_STYLES.text}
                    >
                      {message}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default SplitFrameLayout;
