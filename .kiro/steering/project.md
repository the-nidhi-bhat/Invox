---
inclusion: always
---

# INVOX — Project Identity

**Developer:** Nidhi Bhat  
**GitHub:** https://github.com/the-nidhi-bhat/Invox.git  
**GitHub username:** the-nidhi-bhat  
**Email:** the.nidhi.bhat@gmail.com  
**Branch:** main  
**Baseline commit:** 818a505 (Milestone 1 complete)  
**Event:** CloudBuild AI Virtual Build-a-Thon  

## What INVOX is

INVOX is an AI-assisted invoicing platform that converts messy English/Hinglish business order messages into structured, reviewable invoices.

**Core principle:** AI proposes. Rules decide. You stay in control.

### Example input
> "bhaiya 50 mouse 450 wala, Acme Pune ko, 5% gst laga dena"

### What INVOX does
1. Accept messy business order text
2. Use Amazon Bedrock to interpret it
3. Extract structured information (customer, items, qty, price, GST)
4. Present extraction to the seller for review/edit
5. Run deterministic GST validation — AI never owns financial calculations
6. Detect and visibly flag GST mismatches
7. Recalculate invoice server-side
8. Generate the invoice
9. Generate UPI payment request/QR
10. Show PENDING or clearly simulated PAID status
11. Persist verified invoices in DynamoDB

**AI must never be the final authority for financial calculations.**

## Current milestone status

| Milestone | Description | Status | Commit |
|-----------|-------------|--------|--------|
| 1 | React+Vite+Tailwind scaffold + initial UI | ✅ Done | 818a505 |
| 2 | WhatsApp-style order input | ⬜ Pending | — |
| 3 | Bedrock AI extraction | ⬜ Pending | — |
| 4 | Review/edit experience | ⬜ Pending | — |
| 5 | Deterministic GST engine | ⬜ Pending | — |
| 6 | Invoice generation | ⬜ Pending | — |
| 7 | UPI request / QR | ⬜ Pending | — |
| 8 | DynamoDB persistence | ⬜ Pending | — |
| 9 | Testing + security | ⬜ Pending | — |
| 10 | Antideploy deployment | ⬜ Pending | — |
