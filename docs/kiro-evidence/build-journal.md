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

## Milestone 2 — (pending)

*To be filled after implementation.*

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
