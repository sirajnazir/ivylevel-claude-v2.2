-- =============================================================================
-- Create Profiles for Existing Auth Users
--
-- The new schema's handle_new_user trigger only creates profiles for NEW users.
-- This script creates profiles for existing auth.users who don't have one.
-- =============================================================================

-- Insert profiles for existing users who don't have one
INSERT INTO public.profiles (id, email, role, first_name, last_name)
SELECT
  u.id,
  u.email,
  COALESCE(u.raw_user_meta_data->>'role', 'student')::TEXT,
  u.raw_user_meta_data->>'first_name',
  u.raw_user_meta_data->>'last_name'
FROM auth.users u
WHERE NOT EXISTS (
  SELECT 1 FROM public.profiles p WHERE p.id = u.id
);

-- Show created profiles
SELECT id, email, role, created_at
FROM public.profiles
ORDER BY created_at DESC;
