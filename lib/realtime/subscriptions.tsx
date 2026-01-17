/**
 * Supabase Realtime Subscriptions for Execution Agent
 * v5.3 - Wires existing event bus to database changes
 *
 * Features:
 * - Subscribe to notifications table for nudges
 * - Subscribe to projects table for stall detection
 * - Subscribe to conversations table for chat messages
 * - Subscribe to crises table for crisis alerts
 * - Auto-reconnect with exponential backoff
 */

'use client';

import { useEffect, useCallback, useRef } from 'react';
import { RealtimeChannel, RealtimePostgresChangesPayload } from '@supabase/supabase-js';
import { getSupabaseClient } from '@/lib/supabase/client';

// Generic payload type for postgres changes
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type PostgresPayload = RealtimePostgresChangesPayload<{ [key: string]: any }>;
import { eventBus, publishEvent } from '@/lib/events/bus';
import {
  ExecutionNudgePayload,
  ExecutionChatMessagePayload,
  createEvent,
} from '@/lib/events/contracts';

// =====================================================
// Types
// =====================================================

export interface RealtimeSubscription {
  table: string;
  event: 'INSERT' | 'UPDATE' | 'DELETE' | '*';
  filter?: string;
}

export interface RealtimeStatus {
  isConnected: boolean;
  error: string | null;
  reconnectAttempts: number;
}

// =====================================================
// Hook: useRealtimeNotifications
// Subscribe to notifications table for nudges
// =====================================================

export function useRealtimeNotifications(
  profileId: string | null,
  onNotification?: (notification: Record<string, unknown>) => void
) {
  const channelRef = useRef<RealtimeChannel | null>(null);

  useEffect(() => {
    if (!profileId) return;

    const supabase = getSupabaseClient();

    // Subscribe to new notifications for this profile
    channelRef.current = supabase
      .channel(`notifications:${profileId}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'notifications',
          filter: `profile_id=eq.${profileId}`,
        },
        (payload: PostgresPayload) => {
          const notification = payload.new as Record<string, unknown>;

          // Call custom handler if provided
          onNotification?.(notification);

          // Publish to event bus as EXECUTION_NUDGE
          if (notification.type?.toString().includes('nudge') ||
              notification.type?.toString().includes('stall') ||
              notification.type?.toString().includes('deadline')) {
            const nudgePayload: ExecutionNudgePayload = {
              profileId: notification.profile_id as string,
              nudgeType: mapNotificationTypeToNudgeType(notification.type as string),
              title: notification.title as string,
              message: typeof notification.message === 'string'
                ? notification.message
                : JSON.stringify(notification.message),
              priority: (notification.priority as 'low' | 'medium' | 'high') || 'medium',
              contextType: notification.context_type as 'project' | 'step' | 'crisis' | 'weekly_plan' | undefined,
              contextId: notification.context_id as string | undefined,
            };

            publishEvent(createEvent('EXECUTION_NUDGE', nudgePayload));
          }

          console.log('[Realtime] Notification received:', notification.title);
        }
      )
      .subscribe((status: string) => {
        if (status === 'SUBSCRIBED') {
          console.log('[Realtime] Subscribed to notifications for profile:', profileId);
        } else if (status === 'CHANNEL_ERROR') {
          console.error('[Realtime] Notification channel error');
        }
      });

    return () => {
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
        channelRef.current = null;
      }
    };
  }, [profileId, onNotification]);
}

// =====================================================
// Hook: useRealtimeConversations
// Subscribe to conversations table for chat messages
// =====================================================

export function useRealtimeConversations(
  profileId: string | null,
  threadId?: string | null,
  onMessage?: (message: Record<string, unknown>) => void
) {
  const channelRef = useRef<RealtimeChannel | null>(null);

  useEffect(() => {
    if (!profileId) return;

    const supabase = getSupabaseClient();

    // Build filter - optionally include thread
    const filter = threadId
      ? `profile_id=eq.${profileId},thread_id=eq.${threadId}`
      : `profile_id=eq.${profileId}`;

    channelRef.current = supabase
      .channel(`conversations:${profileId}:${threadId || 'all'}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'conversations',
          filter,
        },
        (payload: PostgresPayload) => {
          const message = payload.new as Record<string, unknown>;

          // Only process assistant messages (user messages are handled locally)
          if (message.role === 'assistant') {
            onMessage?.(message);

            // Publish to event bus
            const chatPayload: ExecutionChatMessagePayload = {
              profileId: message.profile_id as string,
              conversationId: message.id as string,
              threadId: message.thread_id as string | undefined,
              role: message.role as 'user' | 'assistant',
              content: message.content as string,
              contextType: message.context_type as string | undefined,
              contextId: message.context_id as string | undefined,
              isProactive: message.is_proactive as boolean,
            };

            publishEvent(createEvent('EXECUTION_CHAT_MESSAGE', chatPayload));
          }

          console.log('[Realtime] Conversation message received:', message.role);
        }
      )
      .subscribe((status: string) => {
        if (status === 'SUBSCRIBED') {
          console.log('[Realtime] Subscribed to conversations');
        }
      });

    return () => {
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
        channelRef.current = null;
      }
    };
  }, [profileId, threadId, onMessage]);
}

// =====================================================
// Hook: useRealtimeProjects
// Subscribe to projects table for stall detection
// =====================================================

export function useRealtimeProjects(
  profileId: string | null,
  onProjectUpdate?: (project: Record<string, unknown>, eventType: string) => void
) {
  const channelRef = useRef<RealtimeChannel | null>(null);

  useEffect(() => {
    if (!profileId) return;

    const supabase = getSupabaseClient();

    channelRef.current = supabase
      .channel(`projects:${profileId}`)
      .on(
        'postgres_changes',
        {
          event: '*', // All events (INSERT, UPDATE, DELETE)
          schema: 'public',
          table: 'projects',
          filter: `profile_id=eq.${profileId}`,
        },
        (payload: PostgresPayload) => {
          const project = (payload.new || payload.old) as Record<string, unknown>;
          const eventType = payload.eventType;

          onProjectUpdate?.(project, eventType);

          // Check for stall condition
          if (eventType === 'UPDATE' && payload.new) {
            const newProject = payload.new as Record<string, unknown>;
            const daysInactive = newProject.days_since_activity as number;

            if (daysInactive >= 5 && newProject.status !== 'completed') {
              publishEvent(createEvent('PROJECT_STALLED', {
                profileId: newProject.profile_id as string,
                projectId: newProject.id as string,
                projectName: newProject.name as string,
                daysInactive,
                executionDebt: 0, // Will be calculated by backend
                completionRate: newProject.completion_rate as number || 0,
              }));
            }
          }

          console.log('[Realtime] Project update:', eventType, project.name);
        }
      )
      .subscribe();

    return () => {
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
        channelRef.current = null;
      }
    };
  }, [profileId, onProjectUpdate]);
}

// =====================================================
// Hook: useRealtimeCrises
// Subscribe to crises table for crisis alerts
// =====================================================

export function useRealtimeCrises(
  profileId: string | null,
  onCrisis?: (crisis: Record<string, unknown>, eventType: string) => void
) {
  const channelRef = useRef<RealtimeChannel | null>(null);

  useEffect(() => {
    if (!profileId) return;

    const supabase = getSupabaseClient();

    channelRef.current = supabase
      .channel(`crises:${profileId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'crises',
          filter: `profile_id=eq.${profileId}`,
        },
        (payload: PostgresPayload) => {
          const crisis = (payload.new || payload.old) as Record<string, unknown>;
          const eventType = payload.eventType;

          onCrisis?.(crisis, eventType);

          // Publish appropriate event
          if (eventType === 'INSERT') {
            publishEvent(createEvent('CRISIS_DETECTED', {
              profileId: crisis.profile_id as string,
              crisisId: crisis.id as string,
              type: crisis.type as 'blocker' | 'rejection' | 'conflict' | 'deadline' | 'motivation' | 'academic' | 'external' | 'opportunity',
              title: crisis.title as string,
              description: crisis.description as string || '',
              severity: mapUrgencyToSeverity(crisis.urgency as string),
              urgency: crisis.urgency as 'low' | 'medium' | 'high' | 'critical',
              requiresApproval: crisis.requires_human_approval as boolean || false,
              approvalDeadline: crisis.approval_deadline as string || '',
            }));
          } else if (eventType === 'UPDATE' && crisis.status === 'resolved') {
            publishEvent(createEvent('CRISIS_RESOLVED', {
              profileId: crisis.profile_id as string,
              crisisId: crisis.id as string,
              resolutionHours: crisis.resolution_hours as number || 0,
              outcome: crisis.outcome as string || '',
              reframedOpportunity: crisis.reframed_opportunity as string || '',
              convertedToActivity: crisis.converted_to_activity as boolean || false,
              activityId: crisis.activity_id as string | undefined,
            }));
          }

          console.log('[Realtime] Crisis event:', eventType, crisis.title);
        }
      )
      .subscribe();

    return () => {
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
        channelRef.current = null;
      }
    };
  }, [profileId, onCrisis]);
}

// =====================================================
// Hook: useExecutionRealtime
// Combined hook for all Execution Agent subscriptions
// =====================================================

export interface ExecutionRealtimeCallbacks {
  onNotification?: (notification: Record<string, unknown>) => void;
  onMessage?: (message: Record<string, unknown>) => void;
  onProjectUpdate?: (project: Record<string, unknown>, eventType: string) => void;
  onCrisis?: (crisis: Record<string, unknown>, eventType: string) => void;
}

export function useExecutionRealtime(
  profileId: string | null,
  callbacks: ExecutionRealtimeCallbacks = {}
) {
  // Subscribe to all relevant tables
  useRealtimeNotifications(profileId, callbacks.onNotification);
  useRealtimeConversations(profileId, null, callbacks.onMessage);
  useRealtimeProjects(profileId, callbacks.onProjectUpdate);
  useRealtimeCrises(profileId, callbacks.onCrisis);

  // Also connect the event bus to Supabase broadcast channel
  useEffect(() => {
    if (!profileId) return;

    eventBus.connect();

    return () => {
      // Don't disconnect on unmount - keep event bus alive
    };
  }, [profileId]);
}

// =====================================================
// Helper Functions
// =====================================================

function mapNotificationTypeToNudgeType(
  type: string
): 'stall_detected' | 'deadline_approaching' | 'eds_high' | 'weekly_checkin' | 'celebration' {
  if (type.includes('stall') || type.includes('silence')) return 'stall_detected';
  if (type.includes('deadline')) return 'deadline_approaching';
  if (type.includes('eds') || type.includes('debt')) return 'eds_high';
  if (type.includes('weekly') || type.includes('checkin')) return 'weekly_checkin';
  if (type.includes('celebrat') || type.includes('success')) return 'celebration';
  return 'stall_detected'; // Default
}

function mapUrgencyToSeverity(urgency: string): 1 | 2 | 3 | 4 | 5 {
  switch (urgency) {
    case 'low': return 1;
    case 'medium': return 2;
    case 'high': return 4;
    case 'critical': return 5;
    default: return 3;
  }
}

// =====================================================
// Provider Component
// =====================================================

export interface EventBusProviderProps {
  profileId: string | null;
  children: React.ReactNode;
  onNudge?: (payload: ExecutionNudgePayload) => void;
}

/**
 * Provider component that initializes event bus and realtime subscriptions.
 * Wrap your app or page with this to enable realtime features.
 *
 * Usage:
 * ```tsx
 * <EventBusProvider profileId={profileId} onNudge={handleNudge}>
 *   <MyComponent />
 * </EventBusProvider>
 * ```
 */
export function EventBusProvider({
  profileId,
  children,
  onNudge,
}: EventBusProviderProps) {
  // Subscribe to EXECUTION_NUDGE events
  useEffect(() => {
    if (!onNudge) return;

    const unsubscribe = eventBus.on('EXECUTION_NUDGE', (event) => {
      onNudge(event.payload);
    });

    return unsubscribe;
  }, [onNudge]);

  // Set up realtime subscriptions
  useExecutionRealtime(profileId, {
    onNotification: (notification) => {
      console.log('[EventBusProvider] Notification:', notification.title);
    },
  });

  return <>{children}</>;
}
