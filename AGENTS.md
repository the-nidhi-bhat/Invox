# INVOX — AGENTS.md

This file provides top-level context for any Kiro session or workflow agent working on INVOX.
Read this before acting. Do not re-read steering files already loaded into context.

## Project at a glance

- **INVOX** — AI-assisted invoicing platform (English/Hinglish order → structured invoice)
- **Developer:** Nidhi Bhat (the-nidhi-bhat)
- **Repo:** https://github.com/the-nidhi-bhat/Invox.git
- **Event:** CloudBuild AI Virtual Build-a-Thon
- **Core principle:** AI proposes. Rules decide. You stay in control.

## Current state

- **Completed milestone:** M1 (`818a505`) — React + Vite + Tailwind scaffold + UI shell
- **Next milestone:** M2 (WhatsApp-style order input) — NOT started until Nidhi says go
- **Local folder:** `c:\Users\theni\OneDrive\Desktop\projects main\aws` (rename to `invox` when not open in Kiro)

## Key file locations

| Path | Purpose |
|------|---------|
| `src/App.jsx` | Root layout — two-panel (ChatInput + InvoicePreview) |
| `src/components/Header.jsx` | Top nav |
| `src/components/ChatInput.jsx` | Order text input + mock invoice (Bedrock in M3) |
| `src/components/InvoicePreview.jsx` | Invoice display + GST calc |
| `src/components/EmptyState.jsx` | Pre-invoice placeholder |
| `src/index.css` | Tailwind base |
| `vite.config.js` | Vite config |
| `tailwind.config.js` | Tailwind config (dark theme, brand colors, Inter font) |
| `.kiro/steering/` | Persistent rules — always loaded |
| `docs/kiro-evidence/` | Build journal, milestone map, contribution summary |

## Architecture (locked — do not change without Nidhi's approval)

```
Browser (React + Vite + Tailwind)
  → API Gateway
  → Python Lambda
  → Bedrock + DynamoDB
```

Deployed via **Antideploy**. Built exclusively in **Kiro**.

## Roles (internal reasoning — not runtime services)

| Role | Responsibility |
|------|---------------|
| Architect | System design and tradeoffs |
| Builder | Implementation |
| Reviewer | Code and diff review |
| Tester | Behavior and edge cases |
| AWS Specialist | Lambda, Bedrock, DynamoDB, IAM, API Gateway |
| Security Reviewer | Secrets, permissions, input validation |
| UI/UX Reviewer | Usability, responsiveness, accessibility |
| Hackathon Reviewer | Demo quality, evidence, submission readiness |

## Mandatory workflow per milestone

UNDERSTAND → PLAN → IMPLEMENT → VERIFY → REVIEW → COMMIT → PUSH → STOP

See `.kiro/steering/workflow.md` for full details.

## Hard stop conditions

STOP and ask Nidhi when:
- Requirements are ambiguous
- Architecture change needed
- New AWS service required
- Security-sensitive decision needed
- GST rule is uncertain
- Destructive Git action proposed
- Credentials required
- Scope expansion suggested
- Implementation cannot be safely verified

## Never do

- Commit or push without Nidhi's approval
- Force push / reset --hard / destructive Git
- Put secrets in code or commits
- Let AI own financial calculations
- Use Node/Express instead of Python Lambda
- Add out-of-scope features (Razorpay, Twilio, OCR, RAG, auth, etc.)
- Fabricate evidence, test results, or tool usage
