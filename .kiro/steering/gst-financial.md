---
inclusion: always
---

# INVOX — GST and Financial Safety Rules

## Fundamental rule
**AI extraction is untrusted input. Client calculations are not authoritative. Backend recalculates everything.**

## GST calculation requirements
- Must be deterministic (same input → same output, always)
- Must be isolated and independently testable
- Intra-state: CGST + SGST (equal split)
- Inter-state: IGST
- State information from order must be validated to determine treatment
- Validate: quantities, prices, GST rates, state info
- Reject: negative quantities/prices, malformed tax rates, invalid numerics
- Use decimal-safe money calculations — avoid floating-point rounding errors
- Round consistently per the defined invoice calculation policy
- Never silently accept AI-provided tax rates as correct

## GST mismatch handling
- If AI suggests a GST rate that differs from the validated rate for the item category, FLAG IT visibly
- Show the mismatch clearly to the user
- Apply the correct validated rate after user review
- Never silently override — the user must see and approve the correction

## Stop condition
If requirements for a specific GST rule are uncertain, STOP and ask Nidhi rather than inventing a tax rule.

## Testing priority
1. GST engine (highest priority)
2. Invoice totals
3. AI output validation
4. Rounding edge cases
5. Intra-state vs inter-state cases
6. GST mismatch detection
7. Zero/invalid value edge cases
