/**
 * AgentCardBase Component
 * v13.3 - Base template for all agent cards
 *
 * Features:
 * - Consistent card styling with BRAND_COLORS
 * - Loading/error/content states
 * - Refresh and Chat action buttons
 * - Customizable header icon
 */
'use client';

import { ReactNode } from 'react';
import { RefreshCw, MessageSquare, AlertCircle } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';

interface AgentCardBaseProps {
  title: string;
  icon: ReactNode;
  isLoading: boolean;
  isError: boolean;
  errorMessage?: string;
  onRefresh: () => void;
  onChat?: () => void;
  children: ReactNode;
  actions?: ReactNode;
  headerBadge?: ReactNode;
}

export function AgentCardBase({
  title,
  icon,
  isLoading,
  isError,
  errorMessage,
  onRefresh,
  onChat,
  children,
  actions,
  headerBadge,
}: AgentCardBaseProps) {
  return (
    <div
      className="rounded-xl p-5 shadow-sm h-full flex flex-col"
      style={{
        backgroundColor: '#ffffff',
        border: `1px solid ${BRAND_COLORS.borderLight}`,
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className="p-2 rounded-lg"
            style={{ backgroundColor: BRAND_COLORS.primaryBg }}
          >
            {icon}
          </div>
          <div>
            <h3
              className="font-semibold"
              style={{ color: BRAND_COLORS.textHeading }}
            >
              {title}
            </h3>
            {headerBadge}
          </div>
        </div>

        {isLoading && (
          <RefreshCw
            size={16}
            className="animate-spin"
            style={{ color: BRAND_COLORS.textMuted }}
          />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-h-[120px]">
        {isError ? (
          <div className="flex flex-col items-center justify-center h-full py-4">
            <AlertCircle size={24} style={{ color: BRAND_COLORS.error }} className="mb-2" />
            <p style={{ color: BRAND_COLORS.error }} className="text-sm text-center">
              {errorMessage || 'Failed to load data'}
            </p>
            <button
              onClick={onRefresh}
              className="mt-3 text-sm underline"
              style={{ color: BRAND_COLORS.primary }}
            >
              Retry
            </button>
          </div>
        ) : isLoading ? (
          <div className="flex flex-col items-center justify-center h-full py-4">
            <RefreshCw
              size={24}
              className="animate-spin mb-2"
              style={{ color: BRAND_COLORS.textMuted }}
            />
            <p style={{ color: BRAND_COLORS.textMuted }} className="text-sm">
              Loading...
            </p>
          </div>
        ) : (
          children
        )}
      </div>

      {/* Actions */}
      <div
        className="flex items-center gap-2 mt-4 pt-4 border-t"
        style={{ borderColor: BRAND_COLORS.borderLight }}
      >
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-colors hover:opacity-80 disabled:opacity-50"
          style={{
            backgroundColor: BRAND_COLORS.bgSecondary,
            color: BRAND_COLORS.textPrimary,
          }}
        >
          <RefreshCw size={14} />
          Refresh
        </button>

        {onChat && (
          <button
            onClick={onChat}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-colors hover:opacity-80"
            style={{
              backgroundColor: BRAND_COLORS.primaryBg,
              color: BRAND_COLORS.primary,
            }}
          >
            <MessageSquare size={14} />
            Chat
          </button>
        )}

        {actions}
      </div>
    </div>
  );
}

export default AgentCardBase;
