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
**Git commit:** (to be filled after commit)
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

### Build result
✅ Clean — all tests pass, frontend builds, SAM template valid

### Notes
- Implemented by OpenCode (Kiro unavailable due to usage limit)
- M2 frontend remains at commit `037764a`, deployed at https://invox.antideploy.app
- No application code modified — backend is additive only
- Deterministic placeholder enables M4 to swap in Bedrock without API contract changes

---

## Milestone 4 — (pending)

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