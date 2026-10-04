/goal
================================================================================
AUTONOMOUS GOAL ENGINE v2.1 — FEUDAL HRL INSTRUCTION SET
================================================================================

[CONTEXT & OBJECTIVE]
Target Workspace: /workspace/saas-core
Primary Objective: Migrate user organization membership from single-tenant schema to multi-tenant role-based access control (RBAC) with zero downtime migration script and integration tests.

--------------------------------------------------------------------------------
[1. CONSTRAINTS & WORKER BOUNDARIES]
- Autonomy Level: FULL-AUTONOMY
- Execution Scope: Restrict mutations to `prisma/`, `src/services/auth/`, and `tests/e2e/`.
- Standards: Prisma schema validation, backward-compatible migration strategy, strict zero data loss checks.

--------------------------------------------------------------------------------
[2. META-CONTROLLER & OPTION DISPATCH]
- Build DAG:
  1. g₁: Prisma schema update adding `OrganizationMembership` join model.
  2. g₂: Data backfill script copying legacy relations to join table.
  3. g₃: Refactor auth service queries to read from new relation.
  4. g₄: E2E test suite verifying backward-compatibility and RBAC permissions.
- Retry budget: 3 attempts per subgoal.

--------------------------------------------------------------------------------
[3. DETERMINISTIC VERIFICATION ORACLES β(s)]
[ ] Oracle 1 (Schema & Client): `npx prisma validate && npx prisma generate` (exit code 0).
[ ] Oracle 2 (Build & Typecheck): `npm run build` (exit code 0).
[ ] Oracle 3 (E2E Tests): `npm run test:e2e` (exit code 0, 0 failures).
[ ] Oracle 4 (Clean Stage): `git diff --check` (exit code 0).

--------------------------------------------------------------------------------
[4. DUAL-SIGNAL COMPLETION TRIGGER]
Upon β(s) = 1:
1. Convergence artifact written.
2. Signal: `osascript -e 'display notification "RBAC Migration Complete & Verified!" with title "Antigravity Engine"' && printf '\a'`
================================================================================
