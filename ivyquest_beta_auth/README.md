# IvyQuest Beta Auth System

## 🎯 Philosophy

**For beta with 10-20 users, eliminate all complexity:**
- ❌ No self-service signup (admin creates accounts)
- ❌ No password reset callbacks (admin resets passwords)
- ❌ No email verification flows (accounts are pre-verified)
- ✅ Simple email/password login only

This eliminates ALL the callback/HMR/race condition issues entirely.

## 📁 Package Contents

```
ivyquest_beta_auth/
├── lib/auth/
│   └── AuthProvider.tsx      # Simplified auth context
├── components/auth/
│   └── ProtectedRoute.tsx    # Route protection
├── app/
│   ├── page.tsx              # Entry redirect
│   └── auth/login/page.tsx   # Login page
├── ADMIN_GUIDE.md            # User management guide
└── README.md                 # This file
```

## 🚀 Integration Steps

### Step 1: Copy Files

```bash
# Copy auth provider
cp ivyquest_beta_auth/lib/auth/AuthProvider.tsx lib/auth/

# Copy protected route
mkdir -p components/auth
cp ivyquest_beta_auth/components/auth/ProtectedRoute.tsx components/auth/

# Copy pages
cp ivyquest_beta_auth/app/page.tsx app/
mkdir -p app/auth/login
cp ivyquest_beta_auth/app/auth/login/page.tsx app/auth/login/
```

### Step 2: Update Root Layout

```tsx
// app/layout.tsx
import { AuthProvider } from '@/lib/auth/AuthProvider';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

### Step 3: Protect Dashboard

```tsx
// app/dashboard/layout.tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <ProtectedRoute>{children}</ProtectedRoute>;
}
```

### Step 4: Protect Quest Flow

```tsx
// app/quest/layout.tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function QuestLayout({ children }: { children: React.ReactNode }) {
  return <ProtectedRoute>{children}</ProtectedRoute>;
}
```

### Step 5: Setup Database

Run the SQL from `ADMIN_GUIDE.md` in Supabase Dashboard → SQL Editor.

### Step 6: Create Beta Users

Follow `ADMIN_GUIDE.md` to create user accounts.

## 🔐 User Flow (Simplified)

```
┌─────────────┐
│   User      │
│  Visits /   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ Logged in?  │────▶│  Dashboard  │
│    YES      │     └─────────────┘
└──────┬──────┘
       │ NO
       ▼
┌─────────────┐     ┌─────────────┐
│   Login     │────▶│  Dashboard  │
│    Page     │     └─────────────┘
└─────────────┘

No callbacks. No email flows. No complexity.
```

## 🔧 Environment Variables

```env
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## 📝 What's Different from Full Auth

| Feature | Full Auth | Beta Auth |
|---------|-----------|-----------|
| Login | ✅ | ✅ |
| Signup | ✅ Self-service | ❌ Admin only |
| Password Reset | ✅ Email callback | ❌ Admin only |
| Email Verification | ✅ Callback flow | ❌ Pre-verified |
| OAuth | ✅ Google, etc | ❌ Not needed |
| MFA | ✅ Optional | ❌ Not needed |

## 🧪 Testing

### Test Login Flow

1. Create a test user in Supabase Dashboard
2. Go to `http://localhost:3000`
3. Should redirect to `/auth/login`
4. Enter credentials
5. Should redirect to `/dashboard`

### Test Protected Routes

1. Sign out (or use incognito)
2. Go to `http://localhost:3000/dashboard`
3. Should redirect to `/auth/login`

### Test Logout

1. While logged in, trigger sign out
2. Should redirect to `/auth/login`
3. Going to `/dashboard` should redirect to login

## 🚀 Scaling to Production

When ready for self-service auth:

1. **Keep this beta auth** for existing users
2. **Add new routes** for signup/reset
3. **Fix callback page** using server-side token exchange
4. **Test extensively** before enabling

Or use a different auth provider (Clerk, Auth0) that handles callbacks properly.

## ❓ FAQ

**Q: What if a user forgets their password?**
A: Admin resets it in Supabase Dashboard and emails them the new password.

**Q: Can users change their own password?**
A: Yes, you can add a settings page that calls `supabase.auth.updateUser({ password })`. No callback needed for this.

**Q: What about multiple roles?**
A: The `profile.role` field handles this. Use `requiredRole` prop on `ProtectedRoute`.

**Q: Is this secure?**
A: Yes. Supabase handles password hashing, JWT tokens, and session management. The simplification is only in the onboarding flow.

## 📞 Support

If users have issues:
1. Check they're using the correct email
2. Reset their password in Supabase Dashboard
3. Verify their profile exists in the `profiles` table
4. Check `is_active` is `true`

---

**This approach gets you to beta launch without the callback complexity. Add self-service later when you have time to properly architect the callback flows.**
