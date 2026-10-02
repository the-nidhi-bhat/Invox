"""
Order extraction endpoint handler.

POST /extract

M3: Returns a deterministic placeholder response.
Future milestones will replace this with Bedrock integration.
"""

import json
from src.models.request import ExtractRequest
from src.models.response import ExtractResponse, ExtractionItem
from src.validators.extract import validate_extract_request, validate_request_size, validate_json_body
from src.utils.responses import (
    extract_success,
    error_bad_request,
    error_payload_too_large,
    error_internal_server_error,
    error_method_not_allowed,
)


# Deterministic placeholder extraction for M3
# Clearly indicates extraction is not yet connected to Bedrock
PLACEHOLDER_EXTRACTION = ExtractResponse(
    source='placeholder',
    customer='[Extraction not yet implemented — M3 placeholder]',
    location='[Extraction not yet implemented — M3 placeholder]',
    items=[
        ExtractionItem(name='[Extraction not yet implemented]', quantity=1, unit_price=0.0),
    ],
    stated_gst_rate=0.0,
)


def handle_extract(event: dict, context: object) -> dict:
    """
    Handle POST /extract requests.
    
    Validates input and returns deterministic placeholder extraction.
    Does NOT call Bedrock in M3.
    """
    # Only allow POST
    http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', ''))
    if http_method != 'POST':
        return error_method_not_allowed()

    # Get request body
    body = event.get('body', '')
    if body is None:
        body = ''

    # Validate request size
    size_validation = validate_request_size(body)
    if not size_validation.valid:
        return error_payload_too_large(size_validation.details)

    # Validate JSON
    json_validation = validate_json_body(body)
    if not json_validation.valid:
        return error_bad_request(
            json_validation.error_code,
            json_validation.error_message,
            json_validation.details
        )

    # Parse JSON
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_bad_request('MALFORMED_JSON', 'Request body must be valid JSON')

    # Validate extract request
    extract_validation = validate_extract_request(data)
    if not extract_validation.valid:
        return error_bad_request(
            extract_validation.error_code,
            extract_validation.error_message,
            extract_validation.details
        )

    # Return deterministic placeholder (M3 — no Bedrock yet)
    return extract_success(PLACEHOLDER_EXTRACTION)