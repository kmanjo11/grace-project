# Grace Frontend Auth & Navigation Map

Use this as a wiring chart and checklist when working on auth, token storage, and navigation.

## Overview
- Single source of truth for JWT: localStorage['grace_auth_token'] via helpers in `src/ui/utils/authUtils.ts`.
- Verified auth state lives in `src/ui/components/AuthContext.tsx` (isAuthenticated, user, loading).
- Navigation policy enforced by `AuthGuard` inside `src/ui/pages/_app.tsx`.
- Pages (Login/Register) delegate storage and navigation to the above; no direct token storage.
- App state persistence excludes JWTs; only UI/session data is saved.

## Core modules and their links

- __Token utils__ — `src/ui/utils/authUtils.ts`
  - Exposes: `getAuthToken()`, `storeAuthToken()`, `clearAuthTokens()`, `addAuthHeaders()`
  - Storage: `localStorage['grace_auth_token']` (+ optional `grace_token_expiry`)
  - Used by: `apiClient.ts`, `AuthContext.tsx`, `devAuth.ts`

- __API client__ — `src/ui/api/apiClient.ts`
  - Uses: `addAuthHeaders(getAuthToken())` for Authorization
  - Persists token on successful responses via `storeAuthToken()`
  - Exposes: `api.get/post(...)`, `API_ENDPOINTS`
  - Should not do any direct localStorage/sessionStorage writes

- __Auth context (truth for auth)__ — `src/ui/components/AuthContext.tsx`
  - Uses: `getAuthToken()` to verify with backend
  - Owns: `isAuthenticated`, `user`, `loading`, `login()`, `logout()`, `verifyToken()`
  - Includes: short no-token grace to prevent flicker

- __Auth guard (navigation policy)__ — `src/ui/pages/_app.tsx` (component: `AuthGuard`)
  - Reads: `useAuth()` only (verified auth state)
  - Redirects rules:
    - If NOT authenticated on a protected page → `router.replace('/login')`
    - If authenticated on a public page → `router.replace('/chat')`
    - Never redirect if already on the target path
    - Throttles redirects (2s) to avoid loops
  - Do not read token here; rely on `AuthContext`

- __Login page__ — `src/ui/pages/login.tsx`
  - Calls: `api.post(API_ENDPOINTS.AUTH.LOGIN, ...)` → `await login(data)`
  - Sets: `sessionStorage['GRACE_POST_LOGIN_REDIRECT'] = '1'` (one-time hint)
  - No direct token writes

- __Register page__ — `src/ui/pages/register.tsx`
  - Same pattern: `api.post(...)` → `await login(data)`
  - Sets: `GRACE_POST_LOGIN_REDIRECT` (one-time), no direct navigation; guard handles redirect

- __Admin/dev bypass__ — `src/ui/utils/devAuth.ts`
  - Uses: `storeAuthToken(ADMIN_TOKEN)` only
  - No legacy or sessionStorage token writes

- __App state & persistence (non-auth)__
  - `src/ui/context/AppStateContext.tsx`: syncs user info only; token is NOT stored (kept empty)
  - `src/ui/utils/StatePersistence.ts`: snapshots UI/session data; token should not be depended on

## Protected vs public pages
- Public: `['/', '/login', '/register', '/forgot', '/reset']`
- Protected: everything else (e.g., `/chat`, `/wallet`, `/trading`, `/social`, `/settings`)
- Lists are defined and used in `src/ui/pages/_app.tsx`

## Keys and flags (must match)
- Token key: `grace_auth_token` (authUtils only)
- Optional expiry key: `grace_token_expiry` (authUtils only)
- One-time post-login redirect flag: `sessionStorage['GRACE_POST_LOGIN_REDIRECT']`

## Change-impact map (When you change X, check Y)
- Change `authUtils.ts` → verify `apiClient.ts` still uses `addAuthHeaders()` and `storeAuthToken()`; verify `AuthContext.tsx` reads via `getAuthToken()`.
- Change `AuthContext.tsx` (verify/login/logout) → verify `_app.tsx` `AuthGuard` conditions (no token reads, only verified state); verify Login/Register flows await `login(data)`.
- Change `AuthGuard` in `_app.tsx` → ensure Login/Register are not also navigating (use one-time flag only); ensure no redirect when already on `/chat`.
- Change State Persistence (`AppStateContext.tsx` / `StatePersistence.ts`) → ensure token is not saved/restored; only UI/session metadata.
- Add a protected page → ensure it is not added to public pages; add to `pagesWithLayout` if needed.

## Flow diagrams

- __App mount (no token)__
```
_next/_app.tsx (AuthGuard mounts)
  ↓
AuthContext.verifyToken() → no token → isAuthenticated=false, loading=false
  ↓
AuthGuard sees: unauth + protected page → router.replace('/login')
```

- __Login__
```
login.tsx → api.post(LOGIN) → data.token
  ↓
await AuthContext.login(data) → storeAuthToken() → set isAuthenticated=true, user
  ↓
sessionStorage['GRACE_POST_LOGIN_REDIRECT']='1'
  ↓
AuthGuard (public page + authenticated) → router.replace('/chat')
```

- __App mount (with valid token)__
```
AuthContext.verifyToken() → 200 OK → isAuthenticated=true, user
  ↓
AuthGuard: if on public page → replace('/chat'); if already on /chat → no-op
```

## Troubleshooting quick checklist
- Flicker/loops: ensure `_app.tsx` `AuthGuard` never reads token; only verified state. Check throttling and path no-op.
- Stuck on login with known valid token: check `AuthContext.verifyToken()` endpoint and base URL; ensure backend reachable.
- Random unauth flips: confirm only `authUtils.ts` touches `grace_auth_token`; remove legacy/sessionStorage writes.
- Persisted state causing churn: ensure `AppStateContext.tsx` never stores/restores token; snapshots should not be used for auth.
