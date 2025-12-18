/**
 * Supabase Database Types
 *
 * These types define the database schema for IvyQuest assessments.
 * Profiles are stored with optional email linking for retrieval.
 */

export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[];

export interface Database {
  public: {
    Tables: {
      assessments: {
        Row: {
          id: string;
          session_id: string;
          email: string | null;
          profile_data: Json;
          game_plan_data: Json | null;
          scores: AssessmentScores | null;
          completeness: number;
          tier: string | null;
          archetype: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          session_id: string;
          email?: string | null;
          profile_data: Json;
          game_plan_data?: Json | null;
          scores?: AssessmentScores | null;
          completeness?: number;
          tier?: string | null;
          archetype?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          session_id?: string;
          email?: string | null;
          profile_data?: Json;
          game_plan_data?: Json | null;
          scores?: AssessmentScores | null;
          completeness?: number;
          tier?: string | null;
          archetype?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      coach_sessions: {
        Row: {
          id: string;
          assessment_id: string;
          email: string;
          scheduled_at: string | null;
          calendly_event_id: string | null;
          coach_notes: string | null;
          status: 'pending' | 'scheduled' | 'completed' | 'cancelled';
          created_at: string;
        };
        Insert: {
          id?: string;
          assessment_id: string;
          email: string;
          scheduled_at?: string | null;
          calendly_event_id?: string | null;
          coach_notes?: string | null;
          status?: 'pending' | 'scheduled' | 'completed' | 'cancelled';
          created_at?: string;
        };
        Update: {
          id?: string;
          assessment_id?: string;
          email?: string;
          scheduled_at?: string | null;
          calendly_event_id?: string | null;
          coach_notes?: string | null;
          status?: 'pending' | 'scheduled' | 'completed' | 'cancelled';
          created_at?: string;
        };
      };
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      [_ in never]: never;
    };
    Enums: {
      coach_session_status: 'pending' | 'scheduled' | 'completed' | 'cancelled';
    };
  };
}

export interface AssessmentScores {
  aptitude: number;
  passion: number;
  community: number;
  identity: number;
  overall: number;
}

export type Assessment = Database['public']['Tables']['assessments']['Row'];
export type AssessmentInsert = Database['public']['Tables']['assessments']['Insert'];
export type AssessmentUpdate = Database['public']['Tables']['assessments']['Update'];
export type CoachSession = Database['public']['Tables']['coach_sessions']['Row'];
export type CoachSessionInsert = Database['public']['Tables']['coach_sessions']['Insert'];
