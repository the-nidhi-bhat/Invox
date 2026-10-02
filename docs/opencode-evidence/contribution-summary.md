# INVOX — OpenCode Contribution Summary

This document records only genuine OpenCode contributions to the INVOX project.
It is distinct from the historical Kiro contributions recorded in `docs/kiro-evidence/kiro-contribution-summary.md`.

---

## How OpenCode was used for planning

- M3: OpenCode analyzed existing M2 frontend contract (mockExtractor.js, OrderComposer.jsx, App.jsx) to design compatible backend API
- M3: OpenCode created implementation plan covering backend structure, API design, validation, SAM template, and testing strategy
- M4: OpenCode designed Bedrock integration architecture: client isolation, prompt engineering, response parsing, schema validation, failure handling, IAM least-privilege
- M5: OpenCode designed human review layer: multi-item support, optional fields, human-edited tracking, validation UX
- M6: OpenCode designed deterministic GST engine: product mapping, intra/inter-state logic, Decimal arithmetic, mismatch detection
- M7: OpenCode designed invoice generation layer: invoice numbering, M6 authoritative data usage, mismatch preservation, PENDING status

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
| 3 | Python Lambda + API Gateway foundation (health, extract, validation, SAM, 56 tests) | ✅ Tests pass, SAM valid, frontend build clean |
| 4 | Bedrock integration: client, prompt, parser, schema, /extract integration, 61 tests | ✅ Tests pass, SAM valid, frontend build clean |
| 5 | Human review layer: multi-item, optional fields, edited badges, validation UX | ✅ Tests pass, frontend build clean |
| 6 | Deterministic GST engine: product mapping, intra/inter-state, Decimal arithmetic, mismatch detection, frontend display | ✅ 126 tests pass, frontend build clean |
| 7 | Invoice generation: invoice numbering, M6 authoritative data, mismatch preservation, PENDING status, frontend UI | ✅ 155 tests pass, frontend build clean |

*Update after each milestone.*

---

## How OpenCode helped test/review/debug

- M4: Created comprehensive test suite with mocked Bedrock client (20 new integration tests)
- M4: Tests cover valid extraction, throttling, access denied, invalid JSON, missing fields, negative qty, invalid GST
- M4: All 61 tests passing with mocked Bedrock (no live AWS calls needed)
- M4: Verified no stack traces or internal details in error responses
- M5: Verified all edge cases in review layer (empty fields, invalid qty/price/GST, multi-item, cancel flow)
- M5: All 61 backend tests + frontend build passing
- M6: Created 65 new tests for GST engine (25 unit + 17 handler + 23 validators)
- M6: All 126 backend tests passing
- M6: Verified intra-state (CGST+SGST), inter-state (IGST), mismatch detection, Decimal precision
- M7: Created 49 new tests for invoice layer (8 models + 12 service + 29 handler)
- M7: All 155 backend tests passing
- M7: Verified invoice numbering, M6 authoritative data usage, mismatch preservation, PENDING status

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
- M4 Bedrock integration tested with mocked client only — live AWS Bedrock not yet invoked
- Backend SAM deployment not yet performed — endpoints not publicly reachable
- M5 human review layer tested locally only — no live AWS verification
- Antideploy frontend deployment not yet performed for M5 changes
- M6 GST engine tested locally only — no live AWS verification
- Antideploy frontend deployment not yet performed for M6 changes
- M7 invoice generation tested locally only — no live AWS verification
- Antideploy frontend deployment not yet performed for M7 changes