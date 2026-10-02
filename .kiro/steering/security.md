---
inclusion: always
---

# INVOX — Security Rules

## Input validation
Treat ALL external input as untrusted:
- Order text (user input)
- AI output from Bedrock (schema-validate every response)
- Quantities, prices, GST rates
- Customer information and state
- Invoice identifiers
- API payloads

## Secrets — NEVER commit or expose
- AWS credentials / access keys / secret keys
- Bedrock credentials
- DynamoDB credentials
- Antideploy tokens (`~/.antideploy/config.json`)
- API keys
- Environment secrets / `.env` files
- Private certificates

Do not put secrets into frontend code. Do not send secrets to GitHub.

If a secret is accidentally detected in a diff or file, STOP immediately and tell Nidhi.

## AWS / IAM
- Use least-privilege IAM — Lambda only receives permissions it actually requires
- Browser must NOT directly call Bedrock, DynamoDB, or privileged AWS APIs
- API security must include: input validation, request-size limits, safe error handling, CORS, throttling/rate limiting

## Logging
- Never log sensitive information unnecessarily
- Do not expose internal stack traces to users
- Developer details stay in logs, not public UI

## Financial safety
- AI extraction is untrusted input
- Client calculations are not authoritative
- Backend recalculates all totals
- GST calculation must be deterministic and isolated
- Reject invalid numeric values (negative qty/price, malformed tax rates)
- Never silently accept AI-provided tax calculations as truth
- Use decimal-safe money calculations; round consistently per invoice policy

## Deployment pre-check
Before every deploy, verify: no secrets in code, CORS correct, API endpoints verified, production behavior tested.

## Stop conditions
STOP and ask Nidhi when any security-sensitive decision is needed.
