# INVOX — Kiro Build Journal

This journal records genuine development activity performed through Kiro.
Do not add fabricated entries. If evidence was not captured, write "Evidence not captured."

---

## Milestone 1 — React + Vite + Tailwind scaffold + initial INVOX UI

**Date:** 2026-10-02  
**Status:** ✅ Complete  
**Git commit:** `818a505`  
**Branch:** main  

### Objective
Initialize the INVOX project with React + Vite + Tailwind CSS and build the initial UI shell.

### What Kiro was asked to do
- Audit the existing project (single `index.html` with "hello world")
- Initialize Git repo with `main` branch
- Create `.gitignore` (node_modules, dist, .env, .aws)
- Scaffold React + Vite manually (interactive CLI blocked in PowerShell)
- Configure Tailwind CSS v3 + PostCSS
- Build initial UI: Header, ChatInput, InvoicePreview, EmptyState
- Verify production build
- Create GitHub repo and push

### Files changed
```
.gitignore
index.html                          (replaced hello-world shell)
package.json                        (name: invox, React 18 + Vite 5)
package-lock.json
postcss.config.js
tailwind.config.js
vite.config.js
src/main.jsx
src/index.css
src/App.jsx
src/components/Header.jsx
src/components/ChatInput.jsx        (with mock invoice for UI verification)
src/components/InvoicePreview.jsx   (GST line-item calc, totals)
src/components/EmptyState.jsx
```

### Verification performed
- `npm install` — 129 packages, no errors
- `npm run build` — 35 modules transformed, clean output
  - dist/index.html: 0.73 kB
  - dist/assets/*.css: 11.58 kB
  - dist/assets/*.js: 151.34 kB

### Build result
✅ Clean — no errors, no warnings blocking build

### Push result
✅ Pushed to https://github.com/the-nidhi-bhat/Invox main

### Notes
- Folder rename (`aws` → `invox`) deferred — folder locked as active Kiro workspace. Rename via Explorer when project is closed.
- Mock invoice in ChatInput.jsx is intentional — Bedrock wired in Milestone 3
- Two audit vulnerabilities in npm reported (not blocking, will address in Milestone 9)

### Screenshot evidence
- [ ] Kiro session showing scaffold implementation — Evidence not captured (capture before M2)
- [ ] Build output — Evidence not captured
- [ ] GitHub repo with M1 commit — capture from browser

---

## Configuration Layer — Kiro steering, hooks, evidence system, AGENTS.md

**Date:** 2026-10-02  
**Status:** ✅ Complete  
**Git commit:** `5ecde8c`  
**Branch:** main  

### Objective
Transform the Kiro workspace into the INVOX Master Engineering + Hackathon Command Center — configuration only, no application code changes.

### What Kiro was asked to do
- Inspect existing `.kiro` config (none existed)
- Create 7 steering files covering: project identity, architecture, workflow, security, UI/UX, GST/financial, hackathon rules
- Create 2 hooks: secret detection on save, milestone completion reminder
- Create `AGENTS.md` at project root
- Create `docs/kiro-evidence/` with build journal, milestone-commit map, contribution summary

### Files changed
```
.kiro/hooks/milestone-complete-reminder.json
.kiro/hooks/secret-detection.json
.kiro/steering/architecture.md
.kiro/steering/gst-financial.md
.kiro/steering/hackathon.md
.kiro/steering/project.md
.kiro/steering/security.md
.kiro/steering/ui-ux.md
.kiro/steering/workflow.md
AGENTS.md
docs/kiro-evidence/build-journal.md
docs/kiro-evidence/kiro-contribution-summary.md
docs/kiro-evidence/milestone-commits.md
```

### Verification performed
- `git diff --stat` confirmed: 13 new files, 759 insertions, 0 deletions
- Zero changes to application code (src/, index.html, package.json, configs)
- No existing M1 code modified

### Push result
✅ Pushed to https://github.com/the-nidhi-bhat/Invox main (`818a505..5ecde8c`)

---

## README Correction — architecture and project status

**Date:** 2026-10-02
**Status:** ✅ Complete
**Git commit:** `6da0c43`
**Branch:** main

### Objective
Correct five inaccuracies in the README identified during review.

### Changes made (README.md only)
1. Mermaid diagrams — removed stadium shapes `([...])`, diamond `{...}` in workflow, special chars (`·`, `/`), unquoted edge labels; unquoted subgraph IDs; renamed `E1–E5` node IDs to `A1–A5`
2. Backend structure — replaced three-Lambda layout with correct single-Lambda structure (`handler.py`, `bedrock.py`, `gst.py`, etc.) plus explicit architecture note
3. Antideploy claim — removed premature "Production frontend is deployed via Antideploy"; replaced with accurate statement about initial connectivity test
4. Project Status — removed "Backend milestones are in progress"; replaced with accurate status table showing M1/config/README complete, M2+ not started
5. Milestone history — added `cfd6e73` README commit row

### Verification performed
- `git diff --check` — clean
- `git status` — only README.md modified
- Mermaid block count: 4, all balanced
- Secret scan — clean
- No application code touched

---

## Milestone 2 — WhatsApp-style order experience + branding cleanup

**Date:** 2026-10-02
**Status:** ✅ Complete
**Git commit:** `037764a`
**Branch:** main

### Objective
Build the complete frontend order-input → extraction → review/edit experience with a deterministic mock extractor. Remove event branding from the application UI. Deploy to Antideploy.

### What Kiro implemented
- `src/services/mockExtractor.js` — isolated async mock; `extractOrder(msg)` returns canonical INVOX demo data after 900ms; "fail" trigger for error-path testing; clean boundary for M3 Bedrock swap
- `src/components/OrderComposer.jsx` — WhatsApp-style textarea, "Use example order" shortcut, "Extract Order" CTA, loading state, input validation
- `src/components/LoadingState.jsx` — extraction loading panel with spinner + message echo
- `src/components/ExtractionReview.jsx` — editable 6-field review form (Customer, Location, Product, Qty, Unit price, Stated GST), per-field validation, GST disclaimer banner
- `src/App.jsx` — full 5-state state machine (idle → loading → review → confirmed → error), WorkflowSteps progress indicator
- `src/components/EmptyState.jsx` — copy fix ("Generate Invoice" → "Extract Order")
- `src/components/Header.jsx` — removed "CloudBuild AI Virtual Build-a-Thon" event branding from UI

### Files changed
```
src/services/mockExtractor.js          (new)
src/components/OrderComposer.jsx       (new)
src/components/LoadingState.jsx        (new)
src/components/ExtractionReview.jsx    (new)
src/App.jsx                            (updated)
src/components/EmptyState.jsx          (updated)
src/components/Header.jsx              (updated — branding removed)
docs/kiro-evidence/build-journal.md   (updated)
docs/kiro-evidence/milestone-commits.md (updated)
```

### Verification performed
- `npm run build` — ✅ 37 modules, 0 errors
- `git diff --check` — ✅ clean
- Dev server started, all 8 modules HTTP 200
- All 20 manual verification checks passed
- Secret scan — ✅ clean
- "CloudBuild AI Virtual Build-a-Thon" confirmed absent from all runtime source

### Antideploy deployment
- Application: invox (`2711060a-ce92-4b37-b32f-15aa05b55bb7`)
- URL: https://invox.antideploy.app
- Deployment result: *(to be filled after deploy)*

### Screenshot evidence
- Evidence not captured — capture Kiro session + deployed UI before M3

---

## Milestone 3 — (pending)

*To be filled after implementation.*

---

## Milestone 4 — (pending)

*To be filled after implementation.*

---

## Milestone 5 — (pending)

*To be filled after implementation.*

---

## Milestone 6 — (pending)

*To be filled after implementation.*

---

## Milestone 7 — (pending)

*To be filled after implementation.*

---

## Milestone 8 — (pending)

*To be filled after implementation.*

---

## Milestone 9 — (pending)

*To be filled after implementation.*

---

## Milestone 10 — (pending)

*To be filled after implementation.*
