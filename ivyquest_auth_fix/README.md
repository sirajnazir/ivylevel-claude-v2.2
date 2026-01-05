# IvyQuest Auth Callback Fix

## 🐛 Bug Summary

The password recovery callback page (`/auth/callback`) gets stuck at "Verifying" because:
1. `useAuth()` depends on React Context which has timing issues
2. `SIGNED_IN` event fires AFTER the useEffect has already checked `isAuthenticated`
3. Module-level singletons don't survive across Next.js SSR/client hydration

## 🔬 Root Cause Analysis

```
BROKEN FLOW:
─────────────────────────────────────────────────────────────────
t=0ms   │ Page mounts
t=1ms   │ useEffect runs, calls useAuth()
t=2ms   │ useAuth() returns { isAuthenticated: false } ← STALE!
t=5ms   │ Page shows "Verifying..." and waits for state change
t=10ms  │ Supabase parses URL hash
t=50ms  │ Supabase calls setSession()
t=55ms  │ onAuthStateChange fires SIGNED_IN
t=60ms  │ AuthProvider calls setState()
t=65ms  │ Context consumers SHOULD re-render... but don't reliably
─────────────────────────────────────────────────────────────────
        │ Page stuck on "Verifying..." forever
```

### Why Context Updates Don't Propagate

1. **Multiple Supabase client instances**: Despite singleton pattern, Next.js can create multiple instances during SSR hydration
2. **React 18 Strict Mode**: Double-mounts components, creating race conditions
3. **Stale closures**: useEffect callbacks capture old values
4. **Async timing**: setSession() is async, component renders before it completes

## ✅ The Fix: Bypass React Context

**The callback page should NEVER depend on React Context. It should directly use Supabase.**

```
FIXED FLOW:
─────────────────────────────────────────────────────────────────
t=0ms   │ Page mounts
t=1ms   │ useEffect runs (NO useAuth call!)
t=2ms   │ Create FRESH Supabase client
t=3ms   │ Parse URL hash manually
t=4ms   │ Call supabase.auth.setSession() with tokens
t=10ms  │ setSession() returns { session, user }
t=11ms  │ Check callback type (recovery, signup, etc.)
t=12ms  │ Show appropriate UI (password reset form, success, etc.)
─────────────────────────────────────────────────────────────────
        │ No dependency on React Context = No race condition
```

## 📁 Files in This Fix

| File | Purpose |
|------|---------|
| `app/auth/callback/page.tsx` | **Client-side callback handler** - Does NOT use useAuth() |
| `app/auth/reset-password/page.tsx` | Password reset request page |
| `app/api/auth/callback/route.ts` | Server-side callback for OAuth (optional) |
| `lib/auth/supabase-browser.ts` | Fixed Supabase client with window-based singleton |
| `lib/auth/AuthProvider.tsx` | Fixed AuthProvider with proper state propagation |

## 🚀 Integration Steps

### Step 1: Replace Callback Page

Replace your existing `/app/auth/callback/page.tsx` with the new version:

```bash
cp ivyquest_auth_fix/app/auth/callback/page.tsx app/auth/callback/page.tsx
```

**Key changes:**
- Does NOT import `useAuth`
- Creates fresh Supabase client directly
- Manually parses URL hash
- Handles all callback types (recovery, signup, magiclink)
- Includes inline password reset form

### Step 2: Replace Supabase Browser Client

```bash
cp ivyquest_auth_fix/lib/auth/supabase-browser.ts lib/auth/supabase-browser.ts
```

**Key changes:**
- Uses `window` object for true singleton (survives HMR, SSR)
- Exports `getSupabaseBrowserClient()` function, not instance
- Provides `createFreshSupabaseClient()` for isolated operations

### Step 3: Update AuthProvider

```bash
cp ivyquest_auth_fix/lib/auth/AuthProvider.tsx lib/auth/AuthProvider.tsx
```

**Key changes:**
- Uses window-based singleton
- Separates `isInitialized` from `isLoading`
- Handles React 18 Strict Mode double-mounting
- Properly cleans up subscriptions

### Step 4: Add Reset Password Page (if missing)

```bash
cp ivyquest_auth_fix/app/auth/reset-password/page.tsx app/auth/reset-password/page.tsx
```

### Step 5: Update Supabase Redirect URL

In your Supabase Dashboard → Authentication → URL Configuration:

```
Site URL: http://localhost:3006 (or your domain)
Redirect URLs: 
  - http://localhost:3006/auth/callback
  - https://yourdomain.com/auth/callback
```

## 🧪 Testing the Fix

### Test 1: Password Recovery Flow

1. Go to `/auth/reset-password`
2. Enter email, click "Send Reset Link"
3. Check email, click recovery link
4. Should see password reset form (NOT stuck on "Verifying")
5. Enter new password
6. Should redirect to dashboard

### Test 2: Check Console Logs

You should see:
```
[Callback] Hash present: true
[Callback] Parsed: { hasAccessToken: true, type: 'recovery' }
[Callback] Setting session with tokens...
[Callback] Session established for: user@example.com
[Callback] Password recovery flow
```

NOT:
```
[Auth] State change: SIGNED_OUT
[Auth] State change: INITIAL_SESSION
[Auth Callback] Auth state: { isAuthenticated: false, ... }  ← BAD
```

### Test 3: Signup Flow

1. Go to `/auth/signup`
2. Create account
3. Check email, click confirmation link
4. Should see "Email Verified!" (NOT stuck on "Verifying")
5. Should redirect to dashboard

## 🔧 Troubleshooting

### Still stuck on "Verifying..."

Check browser console for:
- `[Callback] Hash present: false` → URL hash was stripped
- `[Callback] setSession error: ...` → Token issue
- Network tab shows failed requests

### "Invalid token" error

- Token might be expired (24 hour limit)
- Request a new password reset email

### Session not persisting

Check that cookies are being set:
- Open DevTools → Application → Cookies
- Should see `sb-*-auth-token` cookies

## 📊 Architecture Comparison

### Before (Broken)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Callback   │────▶│  useAuth()  │────▶│AuthProvider │
│    Page     │     │   (hook)    │     │  (context)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  Supabase   │
                                        │   Client    │
                                        └─────────────┘
                                        
Problem: Multiple layers of indirection + async timing = race condition
```

### After (Fixed)

```
┌─────────────┐     ┌─────────────┐
│  Callback   │────▶│  Supabase   │
│    Page     │     │   Client    │
└─────────────┘     │  (direct)   │
                    └─────────────┘
                    
Solution: Direct Supabase access = no race condition
```

## 🔒 Security Notes

1. **Token Exposure**: Tokens in URL hash are never sent to server (hash is client-only)
2. **Fresh Client**: Callback uses fresh client to avoid stale session state
3. **HTTPS Required**: In production, always use HTTPS to protect tokens in transit

## ✅ Verification Checklist

- [ ] Callback page does NOT import `useAuth`
- [ ] Callback page creates fresh Supabase client
- [ ] Callback page manually parses URL hash
- [ ] Supabase redirect URL is configured correctly
- [ ] Password reset flow completes without getting stuck
- [ ] Signup email verification flow completes
- [ ] Console shows proper log sequence

---

**This fix addresses the fundamental architecture issue: auth callbacks should never depend on React Context state.**
