---
inclusion: always
---

# INVOX — Master Development Workflow

Every meaningful feature follows this lifecycle. Do not skip phases.

## PHASE A — UNDERSTAND
Before coding:
1. Read relevant steering/spec files (do not re-read files already in context)
2. Inspect existing implementation of affected files only
3. Identify dependencies and risks
4. Confirm the feature belongs to the locked MVP
5. Determine what files will change

## PHASE B — PLAN
Create a concise implementation plan covering:
- Objective and requirements
- Architecture impact
- UI/UX impact
- Security impact
- Testing strategy
- AWS impact if applicable
- Files likely to change
- Verification criteria

For substantial features, create a Kiro spec first. Do not code until the spec is approved.

## PHASE C — IMPLEMENT
Implement the smallest correct solution:
- Preserve working code
- Avoid unnecessary rewrites and dependencies
- Follow existing architecture
- Maintain accessibility and responsive behavior
- Handle loading/error/empty states
- Validate inputs
- Never expose secrets
- Never trust client-side financial calculations

## PHASE D — VERIFY
After implementation:
1. Run relevant tests (`pytest` for backend, build for frontend)
2. Run `npm run build` — must be clean
3. Check lint/type errors where configured
4. Manually inspect affected behavior
5. Check edge cases and security implications
6. Do not claim "working" without verification

## PHASE E — REVIEW
Before committing, explicitly run and inspect:
```
git status
git diff
```
Check for: accidental files, secrets, scope creep, unrelated changes, code quality, UX, accessibility, security.

## PHASE F — COMMIT
Conventional commit format:
```
feat: add order extraction flow
feat: add deterministic GST validation
feat: add invoice generation
feat: add UPI payment request
fix: correct intra-state GST calculation
test: add GST engine coverage
security: restrict Lambda permissions
```
- One logical commit per milestone
- No giant catch-all commits
- No empty commits
- No squashing without Nidhi's explicit approval

## PHASE G — PUSH
After verification and Nidhi's approval:
- Push to correct GitHub branch
- Report commit hash and what was pushed
- Do NOT push unverified code
- Do NOT push automatically without Nidhi's approval

## After every milestone

**IMPLEMENT → VERIFY → DIFF REVIEW → COMMIT → PUSH → STOP**

Remind Nidhi to capture Kiro evidence screenshots before moving to the next milestone.

## Credit efficiency rules

- Do NOT re-read entire repository when relevant files are known
- Do NOT repeat context already in steering/specs
- Inspect only files relevant to the current task
- Prefer targeted changes over broad scans
- Do not run unnecessary builds or duplicate verification
- Reuse existing context and milestone results
- Keep prompts focused on one objective at a time
- Avoid speculative refactoring
- Ask for clarification rather than spending credits on assumptions
