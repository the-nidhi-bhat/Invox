---
inclusion: always
---

# INVOX — Locked Technical Architecture

Do NOT change this architecture without explicit approval from Nidhi.

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite + Tailwind CSS |
| Backend | Python AWS Lambda |
| API | Amazon API Gateway |
| AI | Amazon Bedrock |
| Database | Amazon DynamoDB |
| Infrastructure | AWS SAM |
| Testing | Pytest + frontend testing |
| Deployment | Antideploy |
| IDE | Kiro (exclusive) |
| AWS assistance | Amazon Q |
| Source control | Git + GitHub |

## Runtime flow

```
Browser
  → INVOX frontend (React/Vite, hosted via Antideploy)
  → API Gateway
  → Python Lambda
  → Bedrock (AI extraction)
  → DynamoDB (persistence)
```

## Hard rules

- Browser must NOT directly access Bedrock, DynamoDB, or privileged AWS APIs
- Python Lambda is responsible for: request validation, Bedrock interaction, AI-output validation, deterministic GST calculation, invoice calculation, persistence, UPI generation
- Do NOT replace Python Lambda with Node/Express
- Do NOT introduce unnecessary AWS services
- Use on-demand DynamoDB capacity unless there is a demonstrated reason otherwise
- Keep the AWS architecture intentionally small

## Explicitly out of scope

Real WhatsApp/Twilio, Razorpay, real payment verification, voice, OCR, RAG, multi-agent runtime, auth/multi-tenancy, CRM, inventory, Tally/Zoho/QuickBooks, GSTN filing, e-invoice IRN, analytics dashboard, unnecessary AWS services.

Do not add any of these unless Nidhi explicitly changes scope.
