/**
 * Database Types for Supabase
 *
 * Types for the database schema used by Supabase client
 */

import type { UserRole } from './auth';

// Profile row type (what we get from the database)
export interface ProfileRow {
  id: string;
  email: string;
  role: UserRole;
  first_name: string | null;
  last_name: string | null;
  avatar_url: string | null;
  phone: string | null;
  grade: number | null;
  high_school: string | null;
  target_graduation: number | null;
  organization: string | null;
  specialization: string | null;
  max_students: number | null;
  is_active: boolean;
  is_verified: boolean;
  notification_preferences: Record<string, boolean> | null;
  timezone: string | null;
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
}

// Profile insert type (what we send to insert)
export interface ProfileInsert {
  id: string;
  email: string;
  role: UserRole;
  first_name?: string | null;
  last_name?: string | null;
  avatar_url?: string | null;
  phone?: string | null;
  grade?: number | null;
  high_school?: string | null;
  target_graduation?: number | null;
  organization?: string | null;
  specialization?: string | null;
  max_students?: number | null;
  is_active?: boolean;
  is_verified?: boolean;
  notification_preferences?: Record<string, boolean> | null;
  timezone?: string | null;
}

// Profile update type (what we send to update)
export interface ProfileUpdate {
  email?: string;
  role?: UserRole;
  first_name?: string | null;
  last_name?: string | null;
  avatar_url?: string | null;
  phone?: string | null;
  grade?: number | null;
  high_school?: string | null;
  target_graduation?: number | null;
  organization?: string | null;
  specialization?: string | null;
  max_students?: number | null;
  is_active?: boolean;
  is_verified?: boolean;
  notification_preferences?: Record<string, boolean> | null;
  timezone?: string | null;
  updated_at?: string;
  last_login_at?: string | null;
}

// Assessment row type
export interface AssessmentRow {
  id: string;
  user_id: string;
  session_id: string | null;
  ivy_ready_score: Record<string, unknown> | null;
  school_probabilities: Record<string, unknown>[] | null;
  category_scores: Record<string, number> | null;
  helping_factors: string[] | null;
  holding_back_factors: string[] | null;
  archetype: string | null;
  archetype_label: string | null;
  narrative_tagline: string | null;
  profile_snapshot: Record<string, unknown> | null;
  version: string;
  created_at: string;
}

// Database schema type for Supabase
export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: ProfileRow;
        Insert: ProfileInsert;
        Update: ProfileUpdate;
      };
      user_sessions: {
        Row: {
          id: string;
          user_id: string;
          device_info: string | null;
          ip_address: string | null;
          user_agent: string | null;
          is_current: boolean;
          last_active_at: string;
          created_at: string;
        };
        Insert: {
          user_id: string;
          device_info?: string | null;
          ip_address?: string | null;
          user_agent?: string | null;
          is_current?: boolean;
          last_active_at?: string;
        };
        Update: {
          device_info?: string | null;
          ip_address?: string | null;
          user_agent?: string | null;
          is_current?: boolean;
          last_active_at?: string;
        };
      };
      coach_students: {
        Row: {
          id: string;
          coach_id: string;
          student_id: string;
          status: 'active' | 'paused' | 'completed' | 'archived';
          started_at: string;
          notes: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          coach_id: string;
          student_id: string;
          status?: 'active' | 'paused' | 'completed' | 'archived';
          started_at?: string;
          notes?: string | null;
        };
        Update: {
          status?: 'active' | 'paused' | 'completed' | 'archived';
          notes?: string | null;
          updated_at?: string;
        };
      };
      assessments: {
        Row: AssessmentRow;
        Insert: {
          user_id: string;
          session_id?: string | null;
          ivy_ready_score?: Record<string, unknown> | null;
          school_probabilities?: Record<string, unknown>[] | null;
          category_scores?: Record<string, number> | null;
          helping_factors?: string[] | null;
          holding_back_factors?: string[] | null;
          archetype?: string | null;
          archetype_label?: string | null;
          narrative_tagline?: string | null;
          profile_snapshot?: Record<string, unknown> | null;
          version?: string;
        };
        Update: {
          session_id?: string | null;
          ivy_ready_score?: Record<string, unknown> | null;
          school_probabilities?: Record<string, unknown>[] | null;
          category_scores?: Record<string, number> | null;
          helping_factors?: string[] | null;
          holding_back_factors?: string[] | null;
          archetype?: string | null;
          archetype_label?: string | null;
          narrative_tagline?: string | null;
          profile_snapshot?: Record<string, unknown> | null;
        };
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: {
      user_role: UserRole;
    };
  };
}
