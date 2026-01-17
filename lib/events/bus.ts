/**
 * IvyQuest v10.0 Event Bus
 * ========================
 * Lightweight event bus for agent-to-agent and agent-to-UI communication.
 * Uses Supabase Realtime for cross-client sync when enabled.
 */

import { createClient, RealtimeChannel } from '@supabase/supabase-js';
import {
  IvyEvent,
  IvyEventType,
  EventHandlers,
  validateEvent,
  shouldIngestVector,
} from './contracts';

// =====================================================
// Event Bus Class
// =====================================================

class EventBus {
  private handlers: Map<IvyEventType, Set<(event: IvyEvent) => void>> = new Map();
  private supabase: ReturnType<typeof createClient> | null = null;
  private channel: RealtimeChannel | null = null;
  private isConnected = false;

  constructor() {
    // Initialize handlers map
    const eventTypes: IvyEventType[] = [
      'ASSESSMENT_COMPLETED',
      'PROJECT_STALLED',
      'CRISIS_DETECTED',
      'CRISIS_RESOLVED',
      'HUMAN_OVERRIDE',
      'SUCCESS_ACHIEVED',
      'GAMEPLAN_GENERATED',
      'AWARD_MATCHED',
      'OPPORTUNITY_ALERT',
      'STATE_VERSIONED',
      // v5.3 Execution Agent events
      'EXECUTION_NUDGE',
      'EXECUTION_CHAT_MESSAGE',
      'WEEKLY_PLAN_UPDATED',
      'EDS_THRESHOLD_EXCEEDED',
    ];

    eventTypes.forEach((type) => {
      this.handlers.set(type, new Set());
    });
  }

  /**
   * Initialize Supabase Realtime connection for cross-client sync.
   */
  async connect(supabaseUrl?: string, supabaseKey?: string): Promise<void> {
    if (this.isConnected) return;

    const url = supabaseUrl || process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = supabaseKey || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!url || !key) {
      console.warn('[EventBus] Supabase credentials not available, running in local mode');
      return;
    }

    try {
      this.supabase = createClient(url, key);

      // Subscribe to events channel
      this.channel = this.supabase
        .channel('ivy-events')
        .on('broadcast', { event: 'ivy-event' }, (payload) => {
          const event = payload.payload as IvyEvent;
          if (validateEvent(event)) {
            this.dispatch(event, false); // Don't re-broadcast
          }
        })
        .subscribe((status) => {
          if (status === 'SUBSCRIBED') {
            this.isConnected = true;
            console.log('[EventBus] Connected to Supabase Realtime');
          }
        });
    } catch (error) {
      console.error('[EventBus] Connection error:', error);
    }
  }

  /**
   * Disconnect from Supabase Realtime.
   */
  async disconnect(): Promise<void> {
    if (this.channel) {
      await this.channel.unsubscribe();
      this.channel = null;
    }
    this.isConnected = false;
  }

  /**
   * Subscribe to an event type.
   */
  on<T extends IvyEventType>(
    eventType: T,
    handler: (event: Extract<IvyEvent, { type: T }>) => void
  ): () => void {
    const handlers = this.handlers.get(eventType);
    if (handlers) {
      handlers.add(handler as (event: IvyEvent) => void);
    }

    // Return unsubscribe function
    return () => {
      handlers?.delete(handler as (event: IvyEvent) => void);
    };
  }

  /**
   * Subscribe to multiple event types at once.
   */
  onMany(eventHandlers: Partial<EventHandlers>): () => void {
    const unsubscribes: (() => void)[] = [];

    Object.entries(eventHandlers).forEach(([eventType, handler]) => {
      if (handler) {
        const unsub = this.on(eventType as IvyEventType, handler as (event: IvyEvent) => void);
        unsubscribes.push(unsub);
      }
    });

    return () => {
      unsubscribes.forEach((unsub) => unsub());
    };
  }

  /**
   * Publish an event.
   */
  async publish(event: IvyEvent): Promise<boolean> {
    if (!validateEvent(event)) {
      console.error('[EventBus] Invalid event:', event);
      return false;
    }

    // Add timestamp if not present
    if (!event.timestamp) {
      (event as IvyEvent).timestamp = new Date().toISOString();
    }

    // Log event
    console.log('[EventBus] Publishing:', event.type, event.payload);

    // Dispatch locally
    this.dispatch(event, true);

    // Broadcast via Supabase if connected
    if (this.isConnected && this.channel) {
      try {
        await this.channel.send({
          type: 'broadcast',
          event: 'ivy-event',
          payload: event,
        });
      } catch (error) {
        console.error('[EventBus] Broadcast error:', error);
      }
    }

    // Handle success vector ingestion
    if (shouldIngestVector(event)) {
      await this.ingestSuccessVector(event);
    }

    return true;
  }

  /**
   * Dispatch event to local handlers.
   */
  private dispatch(event: IvyEvent, log = true): void {
    const handlers = this.handlers.get(event.type);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(event);
        } catch (error) {
          console.error(`[EventBus] Handler error for ${event.type}:`, error);
        }
      });
    }

    if (log) {
      console.log(`[EventBus] Dispatched ${event.type} to ${handlers?.size || 0} handlers`);
    }
  }

  /**
   * Ingest success vector for RLHF.
   * CRITICAL: Only called for SUCCESS_ACHIEVED events.
   */
  private async ingestSuccessVector(event: IvyEvent): Promise<void> {
    if (event.type !== 'SUCCESS_ACHIEVED') return;

    console.log('[EventBus] Ingesting success vector for RLHF:', event.payload);

    // TODO: Implement vector embedding and storage
    // 1. Generate embedding via OpenAI
    // 2. Store in success_vectors table with pgvector
    // 3. Associate with profile for similarity search
  }

  /**
   * Get connection status.
   */
  get connected(): boolean {
    return this.isConnected;
  }
}

// =====================================================
// Singleton Instance
// =====================================================

export const eventBus = new EventBus();

// =====================================================
// React Hook for Event Subscription
// =====================================================

import { useEffect, useCallback } from 'react';

export function useEventBus<T extends IvyEventType>(
  eventType: T,
  handler: (event: Extract<IvyEvent, { type: T }>) => void,
  deps: React.DependencyList = []
): void {
  const stableHandler = useCallback(handler, deps);

  useEffect(() => {
    const unsubscribe = eventBus.on(eventType, stableHandler);
    return unsubscribe;
  }, [eventType, stableHandler]);
}

export function useEventBusMany(
  handlers: Partial<EventHandlers>,
  deps: React.DependencyList = []
): void {
  useEffect(() => {
    const unsubscribe = eventBus.onMany(handlers);
    return unsubscribe;
  }, deps);
}

// =====================================================
// Utility Functions
// =====================================================

export async function publishEvent(event: IvyEvent): Promise<boolean> {
  return eventBus.publish(event);
}

export function subscribeToEvent<T extends IvyEventType>(
  eventType: T,
  handler: (event: Extract<IvyEvent, { type: T }>) => void
): () => void {
  return eventBus.on(eventType, handler);
}
