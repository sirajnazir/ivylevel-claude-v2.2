-- =============================================================================
-- Fix RLS Infinite Recursion on Profiles Table
--
-- The issue: "Coaches can view student profiles" policy queries profiles table
-- which triggers the same policy check, causing infinite recursion.
--
-- Solution: Create a security definer function to check user role without
-- triggering RLS, then use that function in policies.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Create helper function to get current user's role (bypasses RLS)
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.get_current_user_role()
RETURNS TEXT
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = public
AS $$
  SELECT role FROM public.profiles WHERE id = auth.uid();
$$;

-- Grant execute to authenticated users
GRANT EXECUTE ON FUNCTION public.get_current_user_role() TO authenticated;

-- -----------------------------------------------------------------------------
-- 2. Drop the problematic policies
-- -----------------------------------------------------------------------------

DROP POLICY IF EXISTS "Coaches can view student profiles" ON profiles;
DROP POLICY IF EXISTS "Coaches can view student assessments" ON assessments;
DROP POLICY IF EXISTS "Coaches can view student game plans" ON game_plans;
DROP POLICY IF EXISTS "Coaches can view student weekly vitals" ON weekly_vitals;
DROP POLICY IF EXISTS "Coaches can view student items" ON student_items;
DROP POLICY IF EXISTS "Coaches can view student timeline" ON timeline_events;

-- -----------------------------------------------------------------------------
-- 3. Recreate policies using the helper function
-- -----------------------------------------------------------------------------

-- Profiles: Coaches/Admins can view all profiles
CREATE POLICY "Coaches can view student profiles" ON profiles
  FOR SELECT USING (
    public.get_current_user_role() IN ('coach', 'admin')
  );

-- Assessments: Coaches/Admins can view all
CREATE POLICY "Coaches can view student assessments" ON assessments
  FOR SELECT USING (
    public.get_current_user_role() IN ('coach', 'admin')
  );

-- Game Plans: Coaches/Admins can view all
CREATE POLICY "Coaches can view student game plans" ON game_plans
  FOR SELECT USING (
    public.get_current_user_role() IN ('coach', 'admin')
  );

-- Weekly Vitals: Coaches/Admins can view all
CREATE POLICY "Coaches can view student weekly vitals" ON weekly_vitals
  FOR SELECT USING (
    public.get_current_user_role() IN ('coach', 'admin')
  );

-- Student Items: Coaches/Admins can view all
CREATE POLICY "Coaches can view student items" ON student_items
  FOR SELECT USING (
    public.get_current_user_role() IN ('coach', 'admin')
  );

-- Timeline Events: Coaches/Admins can view all
CREATE POLICY "Coaches can view student timeline" ON timeline_events
  FOR SELECT USING (
    public.get_current_user_role() IN ('coach', 'admin')
  );

-- -----------------------------------------------------------------------------
-- DONE!
-- -----------------------------------------------------------------------------

SELECT 'RLS recursion fix applied successfully' AS status;
