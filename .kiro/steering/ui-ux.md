---
inclusion: always
---

# INVOX — UI/UX Rules

INVOX is a real product prototype, not an AI-generated demo page.

## Core workflow — this must always be obvious to the user
```
ORDER MESSAGE
  → AI EXTRACTION
  → REVIEW / EDIT
  → GST VALIDATION
  → INVOICE
  → PAYMENT
```

## The user must always understand
- What INVOX is doing (loading/processing states)
- What AI extracted vs what rules validated
- What they can edit
- What the final invoice contains

## AI transparency — non-negotiable
Never make AI appear authoritative. Use language like:
- "AI extracted"
- "Suggested by AI"
- "Review before issuing"
- "GST validated by rules"
- "Final calculation"

The UI must visibly distinguish: **AI suggestion** vs **validated result**.
A GST mismatch must be understandable without reading technical documentation.

## Design principles
- Clean professional interface
- Strong visual hierarchy
- Business-oriented usability
- Responsive design (mobile-first)
- Clear typography and consistent spacing
- Meaningful empty/loading/error states
- Accessible controls and keyboard usability
- Visible focus states
- Restrained animation
- Consistent components

## What to avoid
- Excessive gradients, glassmorphism
- Meaningless decorative cards
- Unnecessary dashboards
- UI added just to look bigger
- Color as the only differentiator
- Animations that obscure workflow

## Accessibility — always
- Semantic HTML
- Labels for all inputs
- Keyboard accessible
- Visible focus
- Sufficient contrast
- Meaningful error messages
- ARIA only when actually needed
- Do not sacrifice accessibility for visual effects

## Every UI element must support the product workflow
If it doesn't serve the ORDER → INVOICE → PAYMENT flow, question whether it belongs.
