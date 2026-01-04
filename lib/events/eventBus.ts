/**
 * IvyQuest Event Bus
 * Real-time communication between agents and UI components.
 * @version 10.0
 */

/**
 * Event types emitted by agents
 */
export type AgentEventType =
  | 'agent.loading'
  | 'agent.success'
  | 'agent.error'
  | 'cri.computed'
  | 'narrative.computed'
  | 'crisis.detected'
  | 'crisis.resolved'
  | 'action.started'
  | 'action.completed'
  | 'action.blocked'
  | 'insight.generated'
  | 'suggestion.ready'
  | 'award.matched'
  | 'opportunity.alert';

export interface AgentEvent<T = any> {
  type: AgentEventType;
  data: T;
  timestamp: number;
  source: string;
}

type EventCallback<T = any> = (event: AgentEvent<T>) => void;

interface EventBusState {
  listeners: Map<string, Set<EventCallback>>;
  lastEvents: Map<string, any>;
}

const state: EventBusState = {
  listeners: new Map(),
  lastEvents: new Map(),
};

/**
 * Subscribe to an event type
 */
export function subscribe<T = any>(
  eventType: AgentEventType,
  callback: EventCallback<T>
): () => void {
  if (!state.listeners.has(eventType)) {
    state.listeners.set(eventType, new Set());
  }
  
  state.listeners.get(eventType)!.add(callback as EventCallback);
  
  // Return unsubscribe function
  return () => {
    state.listeners.get(eventType)?.delete(callback as EventCallback);
  };
}

/**
 * Emit an event
 */
export function emit<T = any>(eventType: AgentEventType, data: T, source = 'unknown'): void {
  const event: AgentEvent<T> = {
    type: eventType,
    data,
    timestamp: Date.now(),
    source,
  };
  
  // Store last event of this type
  state.lastEvents.set(eventType, event);
  
  // Notify listeners
  const listeners = state.listeners.get(eventType);
  if (listeners) {
    listeners.forEach(callback => {
      try {
        callback(event);
      } catch (err) {
        console.error(`Event handler error for ${eventType}:`, err);
      }
    });
  }
  
  // Also emit to wildcard listeners
  const wildcardListeners = state.listeners.get('*' as AgentEventType);
  if (wildcardListeners) {
    wildcardListeners.forEach(callback => {
      try {
        callback(event);
      } catch (err) {
        console.error('Wildcard event handler error:', err);
      }
    });
  }
}

/**
 * Get last event of a type
 */
export function getLastEvent<T = any>(eventType: AgentEventType): AgentEvent<T> | null {
  return state.lastEvents.get(eventType) || null;
}

/**
 * Clear all listeners (for testing)
 */
export function clearAllListeners(): void {
  state.listeners.clear();
  state.lastEvents.clear();
}

/**
 * React hook for subscribing to events
 */
import { useEffect, useState, useCallback } from 'react';

export function useEventBus<T = any>(eventType: AgentEventType): AgentEvent<T> | null {
  const [event, setEvent] = useState<AgentEvent<T> | null>(
    () => getLastEvent<T>(eventType)
  );
  
  useEffect(() => {
    const unsubscribe = subscribe<T>(eventType, (e) => setEvent(e));
    return unsubscribe;
  }, [eventType]);
  
  return event;
}

/**
 * Hook for multiple event types
 */
export function useMultipleEvents(eventTypes: AgentEventType[]): Map<AgentEventType, AgentEvent | null> {
  const [events, setEvents] = useState<Map<AgentEventType, AgentEvent | null>>(
    () => new Map(eventTypes.map(t => [t, getLastEvent(t)]))
  );
  
  useEffect(() => {
    const unsubscribes = eventTypes.map(type =>
      subscribe(type, (e) => {
        setEvents(prev => new Map(prev).set(type, e));
      })
    );
    
    return () => unsubscribes.forEach(unsub => unsub());
  }, [eventTypes.join(',')]);
  
  return events;
}

// Export singleton-style object
export const eventBus = {
  subscribe,
  emit,
  getLastEvent,
  clearAllListeners,
};

export default eventBus;
