# INVOX — Kiro Contribution Summary

This document supports the AWS Builder Center blog post and hackathon submission.
It records only genuine Kiro contributions. Do not add fabricated entries.

---

## How Kiro was used for planning

- Kiro performed the initial project audit (single `index.html` → full gap analysis)
- Kiro proposed the React + Vite + Tailwind + Python Lambda + Bedrock + DynamoDB architecture
- Kiro created the master engineering command center (steering files, workflow, evidence system)
- Kiro will create Kiro-native specs for each substantial milestone before implementation

*Update this section as each milestone progresses.*

---

## How Kiro specs were used

| Milestone | Spec used? | Notes |
|-----------|-----------|-------|
| 1 | No — scope was clear and small | Direct implementation |
| 2–10 | TBD | Substantial milestones will use Kiro specs |

*Update as specs are created.*

---

## How Kiro helped implement features

| Milestone | What Kiro implemented | Result |
|-----------|----------------------|--------|
| 1 | Scaffold, Tailwind config, 5 React components, Git setup | ✅ Build clean, pushed |

*Update after each milestone.*

---

## How Kiro helped test/review/debug

*To be filled as testing milestones are reached.*

---

## How Kiro steering maintained project consistency

Kiro steering files (`.kiro/steering/`) are loaded into every Kiro session and enforce:
- Architecture lock (React + Vite + Python Lambda + Bedrock + DynamoDB)
- Security rules (no secrets in code, least-privilege IAM, validate AI output)
- GST financial safety (deterministic engine, AI never authoritative)
- UI/UX standards (AI transparency language, accessible components)
- Git workflow (IMPLEMENT → VERIFY → DIFF → COMMIT → PUSH → STOP)
- Hackathon rules (Kiro-only coding, Antideploy deployment)

This means every Kiro session, regardless of what is being built, operates within the same constraints without needing to re-explain them.

---

## How Kiro hooks contributed

| Hook | Purpose | Created? |
|------|---------|---------|
| Secret detection on save | Warn if .env or credential patterns detected | ✅ Yes |
| Build reminder after edit | Remind to run build after significant changes | ✅ Yes |

---

## How Git milestones correspond to development stages

See `milestone-commits.md` for the full mapping.

Each commit corresponds to a verified, independently deployable milestone.
This gives the hackathon reviewer a clear progression from empty project to working product.

---

## Honest limitations

- Vite interactive scaffold CLI was blocked in PowerShell → Kiro wrote project files directly (equivalent result, documented)
- Folder rename (`aws` → `invox`) deferred due to active workspace lock → rename via Explorer
- Mock invoice in M1 ChatInput is intentional placeholder for Bedrock (M3)
