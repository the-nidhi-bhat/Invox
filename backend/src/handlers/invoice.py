"""
Invoice Generation endpoint handler.

POST /invoice/generate

Generates invoice from M6 deterministic GST calculation result.
Does NOT recalculate GST - uses authoritative M6 calculation.
"""

import json
from src.models.invoice import (
    InvoiceRequest,
    InvoiceResponse,
)
from src.validators.invoice import validate_invoice_request
from src.validators.extract import validate_request_size, validate_json_body
from src.utils.responses import (
    error_bad_request,
    error_payload_too_large,
    error_internal_server_error,
    error_method_not_allowed,
    build_response,
)
from src.services.invoice_service import (
    create_invoice_from_gst_calculation,
    validate_invoice_request,
    DEFAULT_SELLER,
)


def handle_invoice_generate(event: dict, context: object) -> dict:
    """
    Handle POST /invoice/generate requests.
    
    Generates invoice from M6 deterministic GST calculation result.
    Does NOT recalculate GST - uses authoritative M6 calculation.
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

    # Validate invoice generation request
    validation_errors = validate_invoice_request(data)
    if validation_errors:
        # Return the first validation error as the main error message
        return error_bad_request(
            'INVALID_INPUT',
            validation_errors[0],
            {'errors': validation_errors}
        )

    # Create invoice from M6 GST calculation
    try:
        # Use default seller for MVP
        seller = DEFAULT_SELLER
        
        # Create invoice from M6 GST calculation
        invoice_response = create_invoice_from_gst_calculation(data, seller)
    except ValueError as e:
        return error_bad_request('INVALID_INPUT', str(e))
    except Exception as e:
        # Log error but don't expose details
        print(f"Invoice generation error: {type(e).__name__}: {e}")
        return error_internal_server_error()

    return build_response(200, invoice_response)