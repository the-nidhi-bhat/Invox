# INVOX — OpenCode Contribution Summary

This document records only genuine OpenCode contributions to the INVOX project.
It is distinct from the historical Kiro contributions recorded in `docs/kiro-evidence/kiro-contribution-summary.md`.

---

## How OpenCode was used for planning

*To be filled as milestones progress.*

---

## How OpenCode specs were used

| Milestone | Spec used? | Notes |
|-----------|-----------|-------|
| 3 | TBD | Will use OpenCode planning for substantial milestones |
| 4–10 | TBD | |

*Update as specs are created.*

---

## How OpenCode helped implement features

| Milestone | What OpenCode implemented | Result |
|-----------|---------------------------|--------|
| — | Evidence/documentation structure setup | ✅ Created |

*Update after each milestone.*

---

## How OpenCode helped test/review/debug

*To be filled as testing milestones are reached.*

---

## How OpenCode maintained project consistency

OpenCode operates under the same project constraints defined in:
- `AGENTS.md` — project rules and agent instructions
- `.kiro/steering/architecture.md` — locked architecture
- `.kiro/steering/security.md` — security rules
- `.kiro/steering/gst-financial.md` — financial safety rules
- `.kiro/steering/ui-ux.md` — UI/UX standards
- `.kiro/steering/workflow.md` — Git workflow discipline
- `.kiro/steering/hackathon.md` — hackathon requirements

OpenCode follows the mandated workflow:
**IMPLEMENT → VERIFY → DIFF REVIEW → DOCUMENT → COMMIT → PUSH → ANTIDEPLOY → DEPLOYED VERIFICATION → STOP**

---

## How Git milestones correspond to development stages

See `docs/opencode-evidence/milestone-commits.md` for the OpenCode mapping.
See `docs/kiro-evidence/milestone-commits.md` for the historical Kiro mapping.

Each commit corresponds to a verified, independently deployable milestone.
This gives the hackathon reviewer a clear progression from M2 (Kiro) through M10 (OpenCode).

---

## Honest limitations

- OpenCode started after M2 was already complete and deployed
- All M1–M2 work was performed by Kiro before its usage limit was reached
- This summary only covers OpenCode's contribution from M3 onward
- No application code changes have been made by OpenCode yet