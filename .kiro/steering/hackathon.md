---
inclusion: always
---

# INVOX — Hackathon Rules

**Event:** CloudBuild AI Virtual Build-a-Thon

## Required tools (event mandate)
- **Kiro** — primary and exclusive coding IDE
- **Antideploy** — required deployment platform

### Tool rules
- Do NOT use OpenCode for implementation
- Do NOT silently generate implementation through another coding agent/tool
- Amazon Q may assist with AWS-specific questions/debugging/security
- Do NOT switch deployment platforms without Nidhi's explicit approval
- Do NOT fabricate Kiro, Amazon Q, or Antideploy usage evidence

## Required deliverables
1. Working prototype deployed via Antideploy
2. AWS Builder Center blog post
3. LinkedIn post
4. Official submission form

## Blog post must accurately cover
- INVOX problem and solution
- USP
- Architecture
- How Kiro was used (specs, vibe, agentic coding)
- How Antideploy was used
- Development journey
- Lessons learned

## Evidence integrity
- Never invent results, usage, benchmarks, security claims, or tool contributions
- Record only genuine development activity
- If evidence is unavailable, write: "Evidence not captured"
- Do NOT fabricate screenshots or tool activity

## Demo scenario (must work end-to-end)
Input: `"bhaiya 50 mouse 450 wala, Acme Pune ko, 5% gst laga dena"`

Must demonstrate:
1. AI extraction
2. Extracted fields displayed
3. Human review/edit
4. GST mismatch detected and shown
5. Deterministic correction applied
6. Final tax breakdown
7. Invoice generated
8. UPI payment request shown
9. Payment status displayed

The audience must understand the product without reading source code.

## Screenshot checklist (capture at each milestone — do NOT fabricate)
- [ ] Kiro steering configuration visible
- [ ] Kiro spec for a substantial feature
- [ ] Kiro implementation session in progress
- [ ] Kiro verification/test result
- [ ] Kiro code review/diff inspection
- [ ] Completed milestone with working UI
- [ ] Git commit hash corresponding to milestone
- [ ] Antideploy deployment in progress
- [ ] Deployed application at public URL
- [ ] Demo scenario running end-to-end

Remind Nidhi to capture screenshots at the END of each milestone, before moving to the next.
