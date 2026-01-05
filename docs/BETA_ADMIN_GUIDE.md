# Beta User Management Guide

## Overview

For the beta release (10-20 users), all account management is done by the admin through the Supabase Dashboard. This eliminates all callback/recovery flow complexity.

## Setup Steps

### 1. Database Setup

Run this SQL in Supabase Dashboard → SQL Editor:

```sql
-- Profiles table (if not exists)
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'coach', 'admin')),
  first_name TEXT,
  last_name TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Users can read their own profile
CREATE POLICY "Users can view own profile" ON public.profiles
  FOR SELECT USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, role, first_name, last_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'role', 'student'),
    NEW.raw_user_meta_data->>'first_name',
    NEW.raw_user_meta_data->>'last_name'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();
```

### 2. Disable Self-Service Auth (Important!)

In Supabase Dashboard → Authentication → Providers:

1. **Email Provider Settings**:
   - Enable Email Confirmations: **OFF** (admin creates verified accounts)
   - Secure Email Change: **OFF**
   - Double Confirm Email Changes: **OFF**

2. **OPTIONAL - Disable signup API**:
   - In Auth Settings → Advanced, you can restrict signup
   - For beta, you can leave it on (no signup UI anyway)

### 3. Create Beta User Accounts

**Method A: Supabase Dashboard (Recommended)**

1. Go to Supabase Dashboard → Authentication → Users
2. Click "Add User" → "Create new user"
3. Enter:
   - Email: `user@example.com`
   - Password: Generate a strong password (e.g., `TempPass123!`)
   - Check "Auto Confirm User" ✓
4. Click "Create User"
5. Note the user ID (UUID)
6. Go to Table Editor → profiles
7. Find the auto-created profile row
8. Update `role` to: `student`, `coach`, or `admin`
9. Update `first_name` and `last_name`

**Method B: SQL (Bulk Creation)**

```sql
-- Create user via Supabase Auth API (can't do via SQL directly)
-- But you can update profiles after creation:

UPDATE public.profiles 
SET 
  role = 'student',
  first_name = 'John',
  last_name = 'Doe'
WHERE email = 'john@example.com';
```

**Method C: Admin API Script**

Create a Node.js script for bulk user creation:

```javascript
// scripts/create-beta-users.js
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY  // Use SERVICE ROLE key!
);

const betaUsers = [
  { email: 'student1@example.com', password: 'TempPass123!', role: 'student', first_name: 'Student', last_name: 'One' },
  { email: 'student2@example.com', password: 'TempPass456!', role: 'student', first_name: 'Student', last_name: 'Two' },
  { email: 'coach1@example.com', password: 'CoachPass789!', role: 'coach', first_name: 'Coach', last_name: 'One' },
  { email: 'admin@example.com', password: 'AdminPass000!', role: 'admin', first_name: 'Admin', last_name: 'User' },
];

async function createUsers() {
  for (const user of betaUsers) {
    console.log(`Creating user: ${user.email}`);
    
    // Create auth user
    const { data, error } = await supabase.auth.admin.createUser({
      email: user.email,
      password: user.password,
      email_confirm: true,  // Auto-confirm
      user_metadata: {
        role: user.role,
        first_name: user.first_name,
        last_name: user.last_name,
      }
    });
    
    if (error) {
      console.error(`Error creating ${user.email}:`, error.message);
      continue;
    }
    
    console.log(`Created: ${user.email} (${data.user.id})`);
    
    // Update profile role (trigger should have created profile)
    const { error: profileError } = await supabase
      .from('profiles')
      .update({ role: user.role })
      .eq('id', data.user.id);
    
    if (profileError) {
      console.error(`Error updating profile:`, profileError.message);
    }
  }
  
  console.log('Done!');
}

createUsers();
```

Run with:
```bash
SUPABASE_URL=https://xxx.supabase.co \
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key \
node scripts/create-beta-users.js
```

## User Onboarding Email Template

Send this to each beta user:

```
Subject: Your IvyQuest Beta Access

Hi [First Name],

Welcome to the IvyQuest beta! Here are your login credentials:

🔗 Login URL: https://your-domain.com/auth/login

📧 Email: [their email]
🔑 Password: [their temporary password]

Please sign in and start exploring. Your account has [student/coach/admin] access.

If you have any issues, contact us at support@ivyquest.com.

Best,
The IvyQuest Team
```

## Password Resets (Admin Process)

When a user forgets their password:

1. **Option A: Dashboard**
   - Go to Supabase Dashboard → Authentication → Users
   - Find the user
   - Click the three dots menu → "Send password recovery"
   - User receives email with reset link

2. **Option B: Set New Password Directly**
   ```javascript
   // Using admin API
   const { error } = await supabase.auth.admin.updateUserById(
     'user-uuid-here',
     { password: 'NewTempPass123!' }
   );
   ```
   - Then email the user their new password

3. **Option C: Dashboard Direct Reset**
   - Go to Users → Click user → "Reset password"
   - Enter new password
   - Email user the new password

## Monitoring & Troubleshooting

### Check User Sessions

```sql
-- See all user sessions
SELECT 
  u.email,
  s.created_at as session_created,
  s.updated_at as last_active
FROM auth.sessions s
JOIN auth.users u ON s.user_id = u.id
ORDER BY s.updated_at DESC;
```

### Check Login Failures

In Supabase Dashboard → Logs → Auth, filter for:
- Type: `auth`
- Status: `error`

### Common Issues

| Issue | Solution |
|-------|----------|
| "Invalid login credentials" | Check email is correct, reset password |
| "Email not confirmed" | In Dashboard, edit user → Enable "Email Confirmed" |
| User can't access dashboard | Check `role` in profiles table |
| Profile not created | Manually insert row in profiles table |

## Security Notes

1. **Use strong passwords** - At least 12 chars with mixed case, numbers, symbols
2. **Change default passwords** - Require users to change on first login (future feature)
3. **Service Role Key** - NEVER expose in client code, only use server-side
4. **Audit access** - Periodically review user list and deactivate unused accounts

## Scaling Beyond Beta

When ready for self-service:

1. Enable email confirmations in Supabase
2. Add `/auth/signup` page
3. Add `/auth/reset-password` page  
4. Add `/auth/callback` page for email flows
5. Test callback flows thoroughly before launch

---

## Quick Reference

| Task | Where |
|------|-------|
| Create user | Dashboard → Auth → Users → Add User |
| Change role | Table Editor → profiles → Edit row |
| Reset password | Dashboard → Auth → Users → Send recovery |
| Disable user | Table Editor → profiles → Set is_active = false |
| View logs | Dashboard → Logs → Auth |

---

*Last updated: January 2026*
