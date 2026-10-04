/goal
================================================================================
AUTONOMOUS GOAL ENGINE v2.1 — FEUDAL HRL INSTRUCTION SET
================================================================================

[CONTEXT & OBJECTIVE]
Target Workspace: /workspace/api-gateway
Primary Objective: Implement sliding-window counter rate limiting middleware using Redis, with unit and integration test coverage.

--------------------------------------------------------------------------------
[1. CONSTRAINTS & WORKER BOUNDARIES]
- Autonomy Level: FULL-AUTONOMY
- Execution Scope: Modify `/src/middleware/rateLimiter.ts`, `/src/config/redis.ts`, and `/tests/rateLimiter.test.ts`.
- Code Base Standards: Strict TypeScript checks, async/await paradigms, zero extra unapproved npm packages (use existing `ioredis`).

--------------------------------------------------------------------------------
[2. META-CONTROLLER & OPTION DISPATCH (PLAN & EXECUTE)]
- Build DAG:
  1. g₁: Redis connection pool helper & sliding-window Lua script.
  2. g₂: Express middleware wrapping token evaluation logic.
  3. g₃: Integration test suite simulating burst and throttled clients.
- Offload subagent runs to isolate stdout logs.
- Retry budget: 3 attempts per module before rolling back and replanning.

--------------------------------------------------------------------------------
[3. DETERMINISTIC VERIFICATION ORACLES β(s)]
[ ] Oracle 1 (Build): `npx tsc --noEmit` exits with code 0.
[ ] Oracle 2 (Tests): `npm test tests/rateLimiter.test.ts` passes 100% of cases (exit code 0).
[ ] Oracle 3 (Lint): `npm run lint` yields 0 warnings/errors (exit code 0).
[ ] Oracle 4 (Git State): `git diff --check` exits with code 0.

--------------------------------------------------------------------------------
[4. DUAL-SIGNAL COMPLETION TRIGGER]
Upon β(s) = 1 verification:
1. Generate completion summary artifact.
2. Signal: `osascript -e 'display notification "Redis Rate Limiter Built & Verified!" with title "Antigravity Engine"' && printf '\a'`
================================================================================
