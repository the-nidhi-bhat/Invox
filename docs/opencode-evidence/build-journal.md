# INVOX — OpenCode Build Journal

This journal records genuine development activity performed through OpenCode.
Do not add fabricated entries. If evidence was not captured, write "Evidence not captured."

---

## Setup — OpenCode evidence structure initialization

**Date:** 2026-10-02
**Status:** ✅ Complete
**Git commit:** (not yet committed)
**Branch:** main

### Objective
Create the OpenCode evidence/documentation structure as specified in the project instructions, distinct from the historical Kiro evidence.

### Files created
```
docs/opencode-evidence/build-journal.md          (this file)
docs/opencode-evidence/milestone-commits.md
docs/opencode-evidence/contribution-summary.md
```

### Verification performed
- Directory `docs/opencode-evidence/` created
- Three evidence files created with proper structure
- Existing `docs/kiro-evidence/` preserved intact
- No application code modified

### Notes
- This is a documentation/setup task only
- No build, test, or deployment performed
- Application code remains at M2 complete (commit `037764a`)
- Kiro evidence directory untouched — historical record preserved

---

## Milestone 3 — Python Lambda + API Gateway Foundation

**Date:** 2026-10-02
**Status:** ✅ Complete
**Git commit:** `588a018`
**Branch:** main

### Objective
Create a clean, testable AWS serverless backend foundation using Python Lambda, API Gateway, AWS SAM, and Pytest. Establish the API contract for future Bedrock integration without implementing Bedrock yet.

### Files created
```
backend/
├── src/
│   ├── app.py                           # Main Lambda handler (routing + error handling)
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── health.py                    # GET /health handler
│   │   └── extract.py                   # POST /extract handler (placeholder)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py                   # Request dataclasses
│   │   └── response.py                  # Response dataclasses
│   ├── validators/
│   │   ├── __init__.py
│   │   └── extract.py                   # Input validation (separate from runtime)
│   └── utils/
│       ├── __init__.py
│       └── responses.py                 # Standardized response builders
├── tests/
│   ├── __init__.py
│   ├── test_app.py                      # Main handler routing tests (9 tests)
│   ├── test_extract.py                  # Extract endpoint tests (15 tests)
│   ├── test_health.py                   # Health endpoint tests (2 tests)
│   ├── test_responses.py                # Response utility tests (12 tests)
│   └── test_validators.py               # Validator tests (17 tests)
├── template.yaml                        # SAM template (Lambda + API Gateway)
├── requirements.txt                     # Production deps (empty - stdlib only)
└── requirements-dev.txt                 # Dev deps (pytest, pytest-cov)
```

### Files modified (pre-existing)
- None — pure addition

### API endpoints implemented
1. **GET /health** — Returns `{"status": "ok", "service": "invox-api"}`
2. **POST /extract** — Validates input, returns deterministic placeholder response with `source: "placeholder"`, clearly indicating extraction not yet connected to Bedrock
3. **OPTIONS /** — CORS preflight handling

### Validation implemented
- JSON body parsing with MALFORMED_JSON error
- Required `message` field (MISSING_MESSAGE)
- Message must be string (INVALID_MESSAGE_TYPE)
- Message non-empty (EMPTY_MESSAGE)
- Message length ≤ 5000 chars (MESSAGE_TOO_LONG)
- Request body size ≤ 10KB (PAYLOAD_TOO_LARGE)
- Unsupported HTTP methods return 405 METHOD_NOT_ALLOWED
- Unknown routes return 404 NOT_FOUND

### Error handling
- Consistent JSON error format: `{error, code, details?}`
- No stack traces or internal details exposed
- Appropriate HTTP status codes (400, 404, 405, 413, 500)

### CORS
- Configured in SAM template: AllowOrigin='*', AllowHeaders='Content-Type', AllowMethods='GET,POST,OPTIONS'
- Lambda responses include CORS headers
- No localhost assumptions

### SAM infrastructure
- Single Python 3.11 Lambda (`invox-api`)
- API Gateway with prod stage
- Least-privilege IAM: only `AWSLambdaBasicExecutionRole`
- No Bedrock or DynamoDB permissions (added in future milestones)
- Tracing enabled (X-Ray)

### Tests
- **56 tests total** — all passing
- Coverage: health endpoint, extract endpoint (valid + all error cases), validators, response utilities, main handler routing
- Deterministic placeholder response verified identical across inputs
- No implementation details tested, only behavior

### Verification performed
- `pytest tests/ -v` — 56 passed, 0 failed
- SAM template YAML structure validated
- `npm run build` (frontend) — clean, M2 unaffected
- `git diff --check` — clean
- No secrets in source
- No localhost references
- Deployed frontend verified at https://invox.antideploy.app — returns HTTP 200, loads INVOX UI

### Build result
✅ Clean — all tests pass, frontend builds, SAM template valid

### Antideploy deployment
- Frontend deployment: https://invox.antideploy.app (unchanged from M2)
- Backend (Lambda + API Gateway): Not yet deployed via SAM — separate AWS deployment step
- Deployed frontend verified: HTTP 200, correct INVOX title and assets loading

### Notes
- Implemented by OpenCode (Kiro unavailable due to usage limit)
- M2 frontend remains at commit `037764a`, deployed at https://invox.antideploy.app
- No application code modified — backend is additive only
- Deterministic placeholder enables M4 to swap in Bedrock without API contract changes
- Backend SAM deployment required for /health and /extract endpoints to be publicly reachable

---

## Milestone 4 — Amazon Bedrock Extraction Integration

**Date:** 2026-10-02
**Status:** ✅ Complete
**Git commits:** `700a427` (boto3 + IAM), `59ec4b4` (Bedrock client), `7ad4a54` (extraction schema), `aab3d31` (prompt), `a869048` (parser), `6ecb4cb` (integration)
**Branch:** main

### Objective
Replace the deterministic `/extract` placeholder from M3 with a real Amazon Bedrock-powered extraction pipeline. The core flow: user's messy order message → API Gateway → Python Lambda → Amazon Bedrock → structured extraction → validation → JSON response.

### Files created
```
backend/src/services/
├── bedrock_client.py          # Bedrock runtime client (configurable model, testable)
├── extraction_prompt.py       # Hinglish/English extraction system prompt
├── response_parser.py         # Bedrock response parsing + validation
backend/src/models/
├── extraction.py              # Structured extraction contract (BedrockExtraction)
backend/tests/
├── test_extract.py            # Updated with 20 Bedrock-mocked tests
├── test_app.py                # Updated with Bedrock mocking for integration tests
```

### Files modified
```
backend/requirements.txt       # Added boto3>=1.34.0
backend/template.yaml          # Added bedrock:InvokeModel permissions (Claude 3 Haiku/Sonnet)
backend/src/handlers/extract.py    # Replaced placeholder with Bedrock integration
backend/src/services/response_parser.py  # Stricter validation for negative quantities
backend/src/models/__init__.py       # Export extraction models
```

### API contract maintained
- **GET /health** — Unchanged
- **POST /extract** — Same request/response format, now with `source: "bedrock"` and real extraction
- Request validation unchanged (message field, size limits, etc.)
- Error format unchanged (consistent JSON with code, no stack traces)

### Bedrock integration
- **Model**: Anthropic Claude 3 Haiku (primary), Sonnet (fallback) — configurable via `BEDROCK_MODEL_ID` env var
- **Prompt**: Focused system prompt for Hinglish/English business orders with explicit rules:
  - Extract only stated/inferable info, no hallucination
  - Return `null` for missing fields
  - Preserve user's stated GST rate as `stated_gst_rate` (NOT validated rate)
  - Explicit instruction: "stated GST rate ≠ validated GST rate"
- **Response parsing**: Robust JSON extraction from model output (handles markdown, extra text)
- **Validation**: Structured validation of all fields (customer, location, items[], stated_gst_rate)
  - Rejects negative quantities/prices, invalid GST rates (>100 or <0)
  - Missing required fields → 500 (safe error, no internal details)

### Failure handling
- Bedrock throttling → 500 with `INTERNAL_ERROR` (no internal details)
- Bedrock access denied → 500
- Invalid model output (malformed JSON, missing fields) → 500
- Model validation failures (negative qty, invalid GST) → 500
- All errors return consistent format without stack traces or credentials

### IAM permissions (least privilege)
- `bedrock:InvokeModel` for specific model ARNs:
  - `arn:aws:bedrock:${AWS::Region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0`
  - `arn:aws:bedrock:${AWS::Region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0`
- No DynamoDB, S3, or other permissions added

### Tests
- **61 tests total** (5 new service tests + 20 Bedrock integration tests + 36 existing)
- New test coverage:
  - Valid Bedrock extraction with mocked client
  - Bedrock throttling → 500
  - Bedrock access denied → 500
  - Invalid model JSON → 500
  - Missing required fields in model output → 500
  - Negative quantity in model output → 500
  - Invalid GST rate in model output → 500
  - CORS headers on successful extraction
  - Request validation still works (400/405/413)
  - HTTP API event format support
- All 61 tests passing

### Verification performed
- `pytest tests/ -v` — 61 passed, 0 failed
- SAM template YAML structure validated
- `npm run build` (frontend) — clean, M2 unaffected
- `git diff --check` — clean
- No secrets in source
- No localhost references
- Frontend verified at https://invox.antideploy.app — HTTP 200

### Build result
✅ Clean — all tests pass, frontend builds, SAM template valid

### Notes
- Implemented by OpenCode (Kiro unavailable due to usage limit)
- M2 frontend remains at commit `037764a`, deployed at https://invox.antideploy.app
- Granular Git history: 6 meaningful commits showing step-by-step implementation
- Backend SAM deployment required for /health and /extract endpoints to be publicly reachable
- Frontend mockExtractor.js unchanged — ready for API integration in future milestone

---

## Milestone 5 — Human Review / Edit Layer

**Date:** 2026-10-02
**Status:** ✅ Complete
**Git commit:** `4884396`
**Branch:** main

### Objective
Build a reliable human-review step between extraction and invoice calculation. The product principle: AI proposes. Human reviews/edits. Rules decide.

### Files modified
```
src/components/ExtractionReview.jsx    # Complete rewrite for multiple items, optional fields, human-edited tracking
```

### Features implemented
1. **Multiple items support** — Dynamic item list with add/remove (max 5 items)
2. **Optional customer/location** — Fields no longer required; empty allowed
3. **Human-edited tracking** — Visual "Edited" badges on fields modified by user
4. **Source-aware badge** — Shows "Demo data" (mock), "AI extracted" (bedrock), or "Not implemented" (placeholder)
5. **Improved validation** — Touched-state validation (errors only show after blur)
6. **Stated GST rate optional** — If not provided, passes null to backend
7. **Items validation** — Each item requires name, positive integer quantity, non-negative price

### Validation rules
- Customer: optional (empty allowed)
- Location: optional (empty allowed)
- Items: at least one required; each item needs name, positive integer quantity, non-negative price
- Stated GST rate: optional; if provided, must be 0-100
- Error messages only show after field is blurred (touched)

### UI improvements
- "Edited" badge on human-modified fields
- Source badge works for mock, bedrock, placeholder
- Add/remove items (max 5)
- Remove button per item (disabled when only 1 item)
- Cleaner label wording: "Customer (optional)", "Location (optional)", "Stated GST rate (%) — optional"

### Confirmation boundary
- Before confirm: AI-proposed data can be edited
- After confirm: reviewed structured order passed forward to next stage (M6)
- Confirmed order contains: customer, location, items[], statedGstRate (null if not provided)

### Edge cases handled
1. Empty customer/location — allowed
2. Invalid quantity (non-numeric, zero, negative) — rejected with clear message
3. Invalid unit price (non-numeric, negative) — rejected
4. GST rate below 0 or above 100 — rejected
5. Multiple items (up to 5) — supported with add/remove
6. User edits and confirms — values persist in confirmed order
7. User edits and cancels — onReset clears form
8. Extraction failure — handled by App.jsx error state
9. Empty item names — rejected
10. Empty items list — rejected

### Verification performed
- `npm run build` — clean, M2 unaffected
- `pytest tests/ -v` (backend) — 61 passed, 0 failed
- `git diff --check` — clean
- No secrets in source
- No localhost references
- No stack traces in error responses

### Build result
✅ Clean — all tests pass, frontend builds

### Antideploy deployment
- Frontend deployment to https://invox.antideploy.app: **Pending manual trigger**
- Antideploy auto-deploy on push did not trigger (asset hash unchanged: `index-CJgPDAWn.js`)
- Antideploy token in `~/.antideploy/config.json` is single-use and spent — requires re-authentication via Antideploy dashboard
- Manual deployment via Antideploy dashboard required to update live frontend with M5 changes
- Antideploy account: the.nidhi.bhat@gmail.com

### Notes
- Implemented by OpenCode (Kiro unavailable due to usage limit)
- M2/M4 frontend/backend contracts maintained
- M5 is purely the human review/edit layer — no GST calculation, no invoice generation, no payments
- Granular Git history: 1 meaningful commit for M5 implementation

---

## Milestone 6 — Deterministic GST Engine

**Date:** 2026-10-02
**Status:** ✅ Complete
**Git commits:** `53de17e` (backend engine), `8299b38` (frontend display)
**Branch:** main

### Objective
Build the deterministic GST calculation layer. The core principle: AI proposes. Rules decide. You stay in control.

### Files created (backend)
```
backend/src/services/
├── gst_engine.py                # Deterministic GST engine with product mapping, intra/inter-state logic
backend/src/models/
├── gst.py                       # GST calculation request/response models
backend/src/handlers/
├── gst.py                       # POST /gst/calculate endpoint handler
backend/src/validators/
├── gst.py                       # GST calculation request validation
backend/tests/
├── test_gst_engine.py           # 25 unit tests for GST engine
├── test_gst_handler.py          # 17 integration tests for /gst/calculate endpoint
├── test_gst_validators.py       # 23 validator tests
```

### Files modified
```
backend/src/app.py                    # Added /gst/calculate route
backend/src/handlers/__init__.py      # Export gst handler
backend/src/models/__init__.py        # Export GST models
backend/src/validators/__init__.py    # Export GST validators
src/App.jsx                           # Frontend GST calculation display
```

### GST Engine Features
1. **Product GST mapping** — MVP ruleset with 18 products across electronics (18%), stationery (12%), food (5%/0%)
2. **Intra-state calculation** — CGST + SGST (equal split of determined rate)
3. **Inter-state calculation** — IGST (full determined rate)
4. **Deterministic Decimal arithmetic** — No floating-point errors, ROUND_HALF_UP rounding
4. **Mismatch detection** — Compares stated GST rate vs determined rate
5. **Fallback behavior** — Unknown products default to 18%
5. **Seller state configuration** — Default: MAHARASHTRA

### API Contract
- **POST /gst/calculate** — Calculates deterministic GST for confirmed orders
- Request: `{customer_state, items[{name, quantity, unit_price, stated_gst_rate}]}`
- Response: Items with subtotals, GST breakdown (CGST/SGST or IGST), totals, mismatch flag

### Mismatch Detection
- When `stated_gst_rate` != `determined_gst_rate` → `gst_mismatch: true`
- Returns explicit mismatch details per item
- UI clearly flags: "Message stated X% GST, but rules determine Y%. Calculation uses determined rate."

### Frontend Integration
- New `calculating` state with loading spinner
- Confirmed view shows:
  - Mismatch warning banner (amber) when rates differ
  - Tax type badge (Intra-state/Inter-state)
  - Per-item breakdown: subtotal, GST rate, CGST/SGST/IGST amounts
  - Totals: subtotal, total GST, CGST/SGST or IGST, grand total
  - "AI proposed. Rules decided." confirmation message
- Error state handles both extraction and GST calculation failures

### Tests
- **Backend: 126 tests total** (25 GST engine + 17 handler + 23 validators + 61 existing)
- All 126 tests passing
- Frontend build clean

### Verification performed
- `pytest tests/ -v` — 126 passed, 0 failed
- `npm run build` — clean
- `git diff --check` — clean
- No secrets in source
- No localhost references

### Build result
✅ Clean — all tests pass, frontend builds

### Notes
- Implemented by OpenCode (Kiro unavailable due to usage limit)
- M5 frontend/backend contracts maintained
- M6 is purely the deterministic GST layer — no invoice generation, no UPI, no DynamoDB
- Live AWS verification NOT performed (no AWS credentials configured)
- Antideploy frontend deployment pending manual trigger
- Granular Git history: 2 meaningful commits for M6 (backend + frontend)

---

## Milestone 7 — (pending)

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