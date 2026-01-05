/**
 * Supabase Database Types
 *
 * IvyQuest Beta Database Schema Types
 * Generated from: supabase/migrations/010_beta_complete_schema.sql
 */

export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[];

// =============================================================================
// Database Schema Definition
// =============================================================================

export interface Database {
  public: {
    Tables: {
      // -------------------------------------------------------------------------
      // Profiles (Extended User Metadata)
      // -------------------------------------------------------------------------
      profiles: {
        Row: {
          id: string;
          email: string;
          role: UserRole;
          first_name: string | null;
          last_name: string | null;
          grade: number | null;
          graduation_year: number | null;
          high_school: string | null;
          target_major: string | null;
          organization: string | null;
          onboarding_completed: boolean;
          onboarding_step: number;
          preferences: ProfilePreferences;
          is_active: boolean;
          is_verified: boolean;
          created_at: string;
          updated_at: string;
          last_login_at: string | null;
        };
        Insert: {
          id: string;
          email: string;
          role?: UserRole;
          first_name?: string | null;
          last_name?: string | null;
          grade?: number | null;
          graduation_year?: number | null;
          high_school?: string | null;
          target_major?: string | null;
          organization?: string | null;
          onboarding_completed?: boolean;
          onboarding_step?: number;
          preferences?: ProfilePreferences;
          is_active?: boolean;
          is_verified?: boolean;
          created_at?: string;
          updated_at?: string;
          last_login_at?: string | null;
        };
        Update: {
          id?: string;
          email?: string;
          role?: UserRole;
          first_name?: string | null;
          last_name?: string | null;
          grade?: number | null;
          graduation_year?: number | null;
          high_school?: string | null;
          target_major?: string | null;
          organization?: string | null;
          onboarding_completed?: boolean;
          onboarding_step?: number;
          preferences?: ProfilePreferences;
          is_active?: boolean;
          is_verified?: boolean;
          created_at?: string;
          updated_at?: string;
          last_login_at?: string | null;
        };
      };

      // -------------------------------------------------------------------------
      // Assessments (IvyReady Assessment Results)
      // -------------------------------------------------------------------------
      assessments: {
        Row: {
          id: string;
          user_id: string;
          session_id: string;
          assessment_version: string;
          assessment_type: AssessmentType;
          profile_data: Json;
          scores: Json;
          archetype: string | null;
          archetype_confidence: number | null;
          completeness_score: number;
          questions_answered: number;
          total_questions: number;
          started_at: string;
          completed_at: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          session_id: string;
          assessment_version?: string;
          assessment_type?: AssessmentType;
          profile_data: Json;
          scores: Json;
          archetype?: string | null;
          archetype_confidence?: number | null;
          completeness_score?: number;
          questions_answered?: number;
          total_questions?: number;
          started_at?: string;
          completed_at?: string | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          session_id?: string;
          assessment_version?: string;
          assessment_type?: AssessmentType;
          profile_data?: Json;
          scores?: Json;
          archetype?: string | null;
          archetype_confidence?: number | null;
          completeness_score?: number;
          questions_answered?: number;
          total_questions?: number;
          started_at?: string;
          completed_at?: string | null;
          created_at?: string;
        };
      };

      // -------------------------------------------------------------------------
      // Game Plans (Strategic Multi-Year Plans)
      // -------------------------------------------------------------------------
      game_plans: {
        Row: {
          id: string;
          user_id: string;
          assessment_id: string | null;
          plan_version: number;
          plan_status: GamePlanStatus;
          plan_data: Json;
          target_archetype: string | null;
          target_tier: string | null;
          target_schools: Json | null;
          current_phase: string | null;
          current_week: number;
          completion_percentage: number;
          created_at: string;
          updated_at: string;
          activated_at: string | null;
          completed_at: string | null;
        };
        Insert: {
          id?: string;
          user_id: string;
          assessment_id?: string | null;
          plan_version?: number;
          plan_status?: GamePlanStatus;
          plan_data: Json;
          target_archetype?: string | null;
          target_tier?: string | null;
          target_schools?: Json | null;
          current_phase?: string | null;
          current_week?: number;
          completion_percentage?: number;
          created_at?: string;
          updated_at?: string;
          activated_at?: string | null;
          completed_at?: string | null;
        };
        Update: {
          id?: string;
          user_id?: string;
          assessment_id?: string | null;
          plan_version?: number;
          plan_status?: GamePlanStatus;
          plan_data?: Json;
          target_archetype?: string | null;
          target_tier?: string | null;
          target_schools?: Json | null;
          current_phase?: string | null;
          current_week?: number;
          completion_percentage?: number;
          created_at?: string;
          updated_at?: string;
          activated_at?: string | null;
          completed_at?: string | null;
        };
      };

      // -------------------------------------------------------------------------
      // Weekly Vitals (Weekly Progress & Action Plans)
      // -------------------------------------------------------------------------
      weekly_vitals: {
        Row: {
          id: string;
          user_id: string;
          game_plan_id: string | null;
          week_number: number;
          week_start_date: string;
          week_end_date: string;
          academic_year: string | null;
          progress_status: ProgressStatus;
          completion_percentage: number;
          academic_vitals: Json | null;
          ec_vitals: Json | null;
          growth_vitals: Json | null;
          action_plan: Json | null;
          session_date: string | null;
          session_notes: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          game_plan_id?: string | null;
          week_number: number;
          week_start_date: string;
          week_end_date: string;
          academic_year?: string | null;
          progress_status?: ProgressStatus;
          completion_percentage?: number;
          academic_vitals?: Json | null;
          ec_vitals?: Json | null;
          growth_vitals?: Json | null;
          action_plan?: Json | null;
          session_date?: string | null;
          session_notes?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          game_plan_id?: string | null;
          week_number?: number;
          week_start_date?: string;
          week_end_date?: string;
          academic_year?: string | null;
          progress_status?: ProgressStatus;
          completion_percentage?: number;
          academic_vitals?: Json | null;
          ec_vitals?: Json | null;
          growth_vitals?: Json | null;
          action_plan?: Json | null;
          session_date?: string | null;
          session_notes?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };

      // -------------------------------------------------------------------------
      // Student Items (Universal Ledger)
      // -------------------------------------------------------------------------
      student_items: {
        Row: {
          id: string;
          user_id: string;
          item_type: ItemType;
          item_subtype: string | null;
          title: string;
          description: string | null;
          tier1_state: ItemState;
          tier2_substate: string | null;
          status_detail: string | null;
          metric_type: string | null;
          metric_value: string | null;
          metric_unit: string | null;
          start_date: string | null;
          end_date: string | null;
          deadline_date: string | null;
          submit_date: string | null;
          outcome_date: string | null;
          organization: string | null;
          location: string | null;
          grade_levels: string[] | null;
          extended_data: Json;
          source: string;
          confidence: ConfidenceLevel;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          item_type: ItemType;
          item_subtype?: string | null;
          title: string;
          description?: string | null;
          tier1_state?: ItemState;
          tier2_substate?: string | null;
          status_detail?: string | null;
          metric_type?: string | null;
          metric_value?: string | null;
          metric_unit?: string | null;
          start_date?: string | null;
          end_date?: string | null;
          deadline_date?: string | null;
          submit_date?: string | null;
          outcome_date?: string | null;
          organization?: string | null;
          location?: string | null;
          grade_levels?: string[] | null;
          extended_data?: Json;
          source?: string;
          confidence?: ConfidenceLevel;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          item_type?: ItemType;
          item_subtype?: string | null;
          title?: string;
          description?: string | null;
          tier1_state?: ItemState;
          tier2_substate?: string | null;
          status_detail?: string | null;
          metric_type?: string | null;
          metric_value?: string | null;
          metric_unit?: string | null;
          start_date?: string | null;
          end_date?: string | null;
          deadline_date?: string | null;
          submit_date?: string | null;
          outcome_date?: string | null;
          organization?: string | null;
          location?: string | null;
          grade_levels?: string[] | null;
          extended_data?: Json;
          source?: string;
          confidence?: ConfidenceLevel;
          created_at?: string;
          updated_at?: string;
        };
      };

      // -------------------------------------------------------------------------
      // Timeline Events (Growth Journey)
      // -------------------------------------------------------------------------
      timeline_events: {
        Row: {
          id: string;
          user_id: string;
          event_type: EventType;
          event_subtype: string | null;
          title: string;
          description: string | null;
          event_date: string;
          impact: ImpactLevel | null;
          impact_score: number | null;
          icon: string | null;
          color: string | null;
          related_item_id: string | null;
          metadata: Json;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          event_type: EventType;
          event_subtype?: string | null;
          title: string;
          description?: string | null;
          event_date: string;
          impact?: ImpactLevel | null;
          impact_score?: number | null;
          icon?: string | null;
          color?: string | null;
          related_item_id?: string | null;
          metadata?: Json;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          event_type?: EventType;
          event_subtype?: string | null;
          title?: string;
          description?: string | null;
          event_date?: string;
          impact?: ImpactLevel | null;
          impact_score?: number | null;
          icon?: string | null;
          color?: string | null;
          related_item_id?: string | null;
          metadata?: Json;
          created_at?: string;
        };
      };

      // -------------------------------------------------------------------------
      // Coach Relationships
      // -------------------------------------------------------------------------
      coach_relationships: {
        Row: {
          id: string;
          coach_id: string;
          student_id: string;
          status: RelationshipStatus;
          can_view_assessments: boolean;
          can_view_game_plan: boolean;
          can_edit_game_plan: boolean;
          can_view_progress: boolean;
          can_send_messages: boolean;
          started_at: string;
          ended_at: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          coach_id: string;
          student_id: string;
          status?: RelationshipStatus;
          can_view_assessments?: boolean;
          can_view_game_plan?: boolean;
          can_edit_game_plan?: boolean;
          can_view_progress?: boolean;
          can_send_messages?: boolean;
          started_at?: string;
          ended_at?: string | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          coach_id?: string;
          student_id?: string;
          status?: RelationshipStatus;
          can_view_assessments?: boolean;
          can_view_game_plan?: boolean;
          can_edit_game_plan?: boolean;
          can_view_progress?: boolean;
          can_send_messages?: boolean;
          started_at?: string;
          ended_at?: string | null;
          created_at?: string;
        };
      };
    };

    Views: {
      v_current_assessment: {
        Row: {
          id: string;
          user_id: string;
          session_id: string;
          profile_data: Json;
          scores: Json;
          archetype: string | null;
          completeness_score: number;
          completed_at: string | null;
          created_at: string;
        };
      };
      v_active_game_plan: {
        Row: {
          id: string;
          user_id: string;
          assessment_id: string | null;
          plan_version: number;
          plan_data: Json;
          target_archetype: string | null;
          current_phase: string | null;
          current_week: number;
          completion_percentage: number;
          created_at: string;
          updated_at: string;
        };
      };
      v_current_week_vitals: {
        Row: {
          id: string;
          user_id: string;
          week_number: number;
          week_start_date: string;
          progress_status: ProgressStatus;
          completion_percentage: number;
          academic_vitals: Json | null;
          ec_vitals: Json | null;
          growth_vitals: Json | null;
          action_plan: Json | null;
          updated_at: string;
        };
      };
      v_user_dashboard: {
        Row: {
          user_id: string;
          email: string;
          first_name: string | null;
          last_name: string | null;
          role: UserRole;
          grade: number | null;
          graduation_year: number | null;
          onboarding_completed: boolean;
          latest_assessment_id: string | null;
          archetype: string | null;
          ivy_ready_score: string | null;
          assessment_completed_at: string | null;
          active_game_plan_id: string | null;
          current_phase: string | null;
          current_week: number | null;
          plan_completion: number | null;
          current_week_number: number | null;
          progress_status: ProgressStatus | null;
          week_completion: number | null;
          award_count: number;
          ec_count: number;
          application_count: number;
          timeline_event_count: number;
        };
      };
      v_awards: {
        Row: Database['public']['Tables']['student_items']['Row'];
      };
      v_extracurriculars: {
        Row: Database['public']['Tables']['student_items']['Row'];
      };
      v_programs: {
        Row: Database['public']['Tables']['student_items']['Row'];
      };
      v_applications: {
        Row: Database['public']['Tables']['student_items']['Row'];
      };
      v_goals: {
        Row: Database['public']['Tables']['student_items']['Row'];
      };
    };

    Functions: {
      [_ in never]: never;
    };

    Enums: {
      user_role: UserRole;
      assessment_type: AssessmentType;
      game_plan_status: GamePlanStatus;
      progress_status: ProgressStatus;
      item_type: ItemType;
      item_state: ItemState;
      event_type: EventType;
      impact_level: ImpactLevel;
      confidence_level: ConfidenceLevel;
      relationship_status: RelationshipStatus;
    };
  };
}

// =============================================================================
// Enum Types
// =============================================================================

export type UserRole = 'student' | 'coach' | 'admin' | 'parent';
export type AssessmentType = 'full' | 'quick' | 'refresh';
export type GamePlanStatus = 'draft' | 'active' | 'archived' | 'completed';
export type ProgressStatus = 'not_started' | 'behind' | 'on_track' | 'ahead';
export type ItemType = 'award' | 'extracurricular' | 'program' | 'application' | 'goal' | 'test' | 'essay' | 'recommendation' | 'project';
export type ItemState = 'planned' | 'in_progress' | 'submitted' | 'outcome' | 'archived';
export type EventType = 'milestone' | 'growth_event' | 'phase_transition' | 'academic' | 'application' | 'award' | 'program' | 'project';
export type ImpactLevel = 'minor' | 'moderate' | 'major';
export type ConfidenceLevel = 'high' | 'medium' | 'low';
export type RelationshipStatus = 'pending' | 'active' | 'paused' | 'ended';

// =============================================================================
// Helper Types
// =============================================================================

export interface ProfilePreferences {
  notifications?: boolean;
  theme?: 'light' | 'dark';
  timezone?: string;
}

export interface AssessmentScores {
  aptitude?: number;
  passion?: number;
  community?: number;
  identity?: number;
  overall?: number;
  ivy_ready_score?: number;
  [key: string]: number | undefined;
}

// =============================================================================
// Table Row/Insert/Update Type Aliases
// =============================================================================

// Profiles
export type Profile = Database['public']['Tables']['profiles']['Row'];
export type ProfileInsert = Database['public']['Tables']['profiles']['Insert'];
export type ProfileUpdate = Database['public']['Tables']['profiles']['Update'];

// Assessments
export type Assessment = Database['public']['Tables']['assessments']['Row'];
export type AssessmentInsert = Database['public']['Tables']['assessments']['Insert'];
export type AssessmentUpdate = Database['public']['Tables']['assessments']['Update'];

// Game Plans
export type GamePlan = Database['public']['Tables']['game_plans']['Row'];
export type GamePlanInsert = Database['public']['Tables']['game_plans']['Insert'];
export type GamePlanUpdate = Database['public']['Tables']['game_plans']['Update'];

// Weekly Vitals
export type WeeklyVitals = Database['public']['Tables']['weekly_vitals']['Row'];
export type WeeklyVitalsInsert = Database['public']['Tables']['weekly_vitals']['Insert'];
export type WeeklyVitalsUpdate = Database['public']['Tables']['weekly_vitals']['Update'];

// Student Items
export type StudentItem = Database['public']['Tables']['student_items']['Row'];
export type StudentItemInsert = Database['public']['Tables']['student_items']['Insert'];
export type StudentItemUpdate = Database['public']['Tables']['student_items']['Update'];

// Timeline Events
export type TimelineEvent = Database['public']['Tables']['timeline_events']['Row'];
export type TimelineEventInsert = Database['public']['Tables']['timeline_events']['Insert'];
export type TimelineEventUpdate = Database['public']['Tables']['timeline_events']['Update'];

// Coach Relationships
export type CoachRelationship = Database['public']['Tables']['coach_relationships']['Row'];
export type CoachRelationshipInsert = Database['public']['Tables']['coach_relationships']['Insert'];
export type CoachRelationshipUpdate = Database['public']['Tables']['coach_relationships']['Update'];

// View Types
export type CurrentAssessment = Database['public']['Views']['v_current_assessment']['Row'];
export type ActiveGamePlan = Database['public']['Views']['v_active_game_plan']['Row'];
export type CurrentWeekVitals = Database['public']['Views']['v_current_week_vitals']['Row'];
export type UserDashboard = Database['public']['Views']['v_user_dashboard']['Row'];
