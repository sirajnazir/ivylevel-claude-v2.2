# Bug Report: Auth Callback Page Stuck at "Verifying"

**Date**: January 5, 2026
**Severity**: High
**Component**: `/app/auth/callback/page.tsx`
**Status**: Open

---

## Summary

The password recovery flow gets stuck at "Verifying your session..." and never progresses to the password reset form. The page shows a spinner indefinitely despite the session being successfully established.

---

## Steps to Reproduce

1. Go to `/auth/login`
2. Click "Forgot password?"
3. Enter email and submit
4. Check email and click the password reset link
5. **Expected**: Password reset form appears
6. **Actual**: Page shows "Verifying your session..." forever

---

## Console Logs (Actual Behavior)

```
[Supabase] Creating browser client singleton
[Auth] Initializing...
[Auth] Cleaning up subscription
[Auth] Initializing...
[Auth] onAuthStateChange: SIGNED_OUT
[Auth] Updating state, session: false
[Auth] State updated: not authenticated
[Auth] onAuthStateChange: INITIAL_SESSION
[Fast Refresh] rebuilding
[Fast Refresh] done in 468ms
[Callback] Hash present: true
[Callback] Parsed: Object { hasAccessToken: true, type: 'recovery' }
[Callback] Scheduling session check...
[Callback] Timer scheduled: 12
[Callback] Setting session...
[Callback] startCallback function completed
[Callback] Checking session, attempt: 1    <-- Timer fires successfully
[Auth] onAuthStateChange: SIGNED_IN        <-- Session established!
[Auth] Updating state, session: true
[Fast Refresh] rebuilding                  <-- HMR kills everything
```

---

## Root Cause Analysis

### Primary Issue: Hot Module Replacement (HMR) Interference

The log sequence reveals the exact failure point:

1. `checkSession()` fires (attempt 1)
2. `supabase.auth.getSession()` is called (returns a Promise)
3. **Before the Promise resolves**, AuthProvider receives `SIGNED_IN` event
4. AuthProvider calls `setState()` to update session state
5. This state change triggers **Next.js Fast Refresh (HMR)**
6. HMR rebuilds the module, **destroying the pending Promise callback**
7. The `.then()` handler never executes
8. Page remains stuck at "processing" status

### Evidence

The logs show:
- `[Callback] Checking session, attempt: 1` appears (setTimeout worked)
- `[Callback] getSession result: ...` **never appears** (Promise callback killed)
- `[Fast Refresh] rebuilding` appears immediately after `SIGNED_IN`

### Why This Happens

1. **Shared Supabase Client**: The callback page and AuthProvider share the same Supabase client singleton
2. **Global Event Listeners**: `onAuthStateChange` fires globally when session changes
3. **React State Updates**: AuthProvider updates state on `SIGNED_IN`
4. **HMR Trigger**: Any state update in a parent provider can trigger Fast Refresh in dev mode
5. **Promise Cancellation**: Pending async operations are abandoned when modules reload

---

## Technical Deep Dive

### The Timing Problem

```
Timeline (milliseconds):
0ms    - checkSession() called
0ms    - getSession() Promise created
5ms    - setSession() completes internally
5ms    - Supabase fires SIGNED_IN event
6ms    - AuthProvider.onAuthStateChange receives event
7ms    - AuthProvider calls setState({ session: true })
8ms    - React triggers re-render
9ms    - Next.js HMR detects change, triggers rebuild
10ms   - Module reloads, Promise callback is orphaned
???    - getSession().then() NEVER EXECUTES
```

### Why the Callback Page Can't Use useAuth()

The original approach used `useAuth()` which depends on React Context:

```typescript
// BAD: Race condition
const { isAuthenticated } = useAuth();

useEffect(() => {
  if (isAuthenticated) {
    // This check happens BEFORE SIGNED_IN event arrives
    // isAuthenticated is still false at this point
  }
}, [isAuthenticated]);
```

The Context-based approach fails because:
1. `useEffect` runs synchronously after mount
2. `isAuthenticated` is `false` initially
3. `SIGNED_IN` event arrives asynchronously (too late)
4. By the time Context updates, the effect has already checked and moved on

### Why Direct Supabase Also Fails

The "fix" to use direct Supabase calls also fails due to HMR:

```typescript
// ALSO BAD: HMR kills pending promises
supabase.auth.getSession().then(({ data: { session } }) => {
  // This callback gets destroyed by HMR before it can execute
  if (session) {
    setStatus('password_reset'); // Never reached
  }
});
```

---

## Affected Files

| File | Role | Issue |
|------|------|-------|
| `app/auth/callback/page.tsx` | Client callback handler | Promise killed by HMR |
| `lib/auth/AuthProvider.tsx` | Global auth state | Triggers HMR on state change |
| `lib/auth/supabase-browser.ts` | Singleton client | Shared across components |

---

## Potential Solutions

### Solution 1: Isolate Callback from AuthProvider (Recommended)

Prevent the callback page from being affected by AuthProvider state changes:

```typescript
// In AuthProvider.tsx - skip state updates during callback
useEffect(() => {
  if (window.location.pathname === '/auth/callback') {
    console.log('[Auth] Skipping state updates on callback page');
    return;
  }
  // ... normal auth state handling
}, []);
```

**Pros**: Minimal change, addresses root cause
**Cons**: Special-case logic, could miss edge cases

### Solution 2: Server-Side Session Exchange

Move token exchange to server-side API route:

```typescript
// app/api/auth/exchange/route.ts
export async function POST(request: NextRequest) {
  const { accessToken, refreshToken } = await request.json();

  // Set session server-side
  const supabase = createServerClient(...);
  await supabase.auth.setSession({ access_token, refresh_token });

  // Return success, client just redirects
  return NextResponse.json({ success: true });
}
```

**Pros**: No client-side race conditions, works with HMR
**Cons**: Requires architectural change, cookie handling complexity

### Solution 3: Use localStorage Flag

Set a flag before session change, check it after HMR:

```typescript
// Before setSession
localStorage.setItem('auth_callback_pending', JSON.stringify({
  type: 'recovery',
  timestamp: Date.now()
}));

// On mount, check for pending callback
useEffect(() => {
  const pending = localStorage.getItem('auth_callback_pending');
  if (pending) {
    const { type, timestamp } = JSON.parse(pending);
    if (Date.now() - timestamp < 5000) {
      // Resume callback flow
      localStorage.removeItem('auth_callback_pending');
      handlePendingCallback(type);
    }
  }
}, []);
```

**Pros**: Survives HMR, simple implementation
**Cons**: Relies on localStorage, timing-based

### Solution 4: Disable HMR for Auth Pages

Configure Next.js to exclude auth pages from Fast Refresh:

```javascript
// next.config.js
module.exports = {
  experimental: {
    // No direct option exists, but could use middleware
  }
}
```

**Pros**: Addresses root cause directly
**Cons**: Not easily configurable in Next.js

### Solution 5: Production Build Testing

The issue may only occur in development mode. Test with:

```bash
npm run build && npm run start
```

**Pros**: Zero code changes if it works in production
**Cons**: Doesn't fix dev experience, harder to debug

---

## Recommended Fix Implementation

### Option A: Quick Fix (Solution 3 - localStorage)

```typescript
// app/auth/callback/page.tsx

const CALLBACK_STORAGE_KEY = 'ivyquest_auth_callback';

export default function AuthCallbackPage() {
  const router = useRouter();
  const [status, setStatus] = useState<CallbackStatus>('initializing');

  useEffect(() => {
    // Check for resumed callback first
    const stored = localStorage.getItem(CALLBACK_STORAGE_KEY);
    if (stored) {
      const { type, email, timestamp } = JSON.parse(stored);
      if (Date.now() - timestamp < 10000) {
        localStorage.removeItem(CALLBACK_STORAGE_KEY);
        setUserEmail(email);
        if (type === 'recovery') {
          setStatus('password_reset');
          return;
        }
        setStatus('success');
        setTimeout(() => router.push('/dashboard'), 1500);
        return;
      }
    }

    // Normal callback flow
    processCallback();
  }, []);

  function processCallback() {
    // ... existing hash parsing ...

    // Store callback info BEFORE setSession
    localStorage.setItem(CALLBACK_STORAGE_KEY, JSON.stringify({
      type,
      email: null, // Will be set after session
      timestamp: Date.now()
    }));

    // ... rest of implementation
  }
}
```

### Option B: Architectural Fix (Solution 2 - Server-Side)

This requires more significant changes but is more robust:

1. Create `/api/auth/exchange` endpoint
2. Callback page POSTs tokens to server
3. Server sets session via cookies
4. Client receives success response
5. Client checks session and renders appropriate UI

---

## Environment

- Next.js: 14.2.14
- React: 18.x (Strict Mode enabled)
- @supabase/ssr: ^0.5.2
- @supabase/supabase-js: ^2.49.1
- Node.js: v20.x
- Development mode with Fast Refresh enabled

---

## Testing Checklist

- [ ] Test in production build (`npm run build && npm run start`)
- [ ] Test with React Strict Mode disabled
- [ ] Test with different browsers
- [ ] Test magic link flow (not just password recovery)
- [ ] Test email confirmation flow
- [ ] Verify fix doesn't break normal login/logout

---

## Related Issues

- React 18 Strict Mode double-mount behavior
- Next.js App Router client/server component boundaries
- Supabase SSR cookie handling
- Hot Module Replacement and async operations

---

## Appendix: Full Component Code

See `/app/auth/callback/page.tsx` for current implementation.

---

*Report generated during debugging session. Last updated: January 5, 2026*
