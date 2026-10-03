"""
UPI Payment Request endpoint handler.

POST /upi/generate

Generates UPI payment request with deep link and QR code.
Does NOT process real payments - honest/simulated status only.
"""

import json
from src.models.upi import (
    UPIRequest,
    UPIResponse,
)
from src.validators.upi import validate_upi_request
from src.validators.extract import validate_request_size, validate_json_body
from src.utils.responses import (
    error_bad_request,
    error_payload_too_large,
    error_internal_server_error,
    error_method_not_allowed,
    build_response,
)
from src.services.upi_service import (
    create_upi_payment_request,
    validate_upi_request,
    DEFAULT_MERCHANT_VPA,
    DEFAULT_MERCHANT_NAME,
)


def handle_upi_generate(event: dict, context: object) -> dict:
    """
    Handle POST /upi/generate requests.
    
    Generates UPI payment request with deep link and QR code.
    Does NOT process real payments - honest/simulated status only.
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

    # Validate UPI generation request
    validation_errors = validate_upi_request(data)
    if validation_errors:
        return error_bad_request(
            'INVALID_INPUT',
            validation_errors[0],
            {'errors': validation_errors}
        )

    # Create UPI payment request
    try:
        # Use default merchant for MVP
        merchant_vpa = DEFAULT_MERCHANT_VPA
        merchant_name = DEFAULT_MERCHANT_NAME
        
        # Create UPI payment request
        upi_response = create_upi_payment_request(data, merchant_vpa, merchant_name)
    except ValueError as e:
        return error_bad_request('INVALID_INPUT', str(e))
    except Exception as e:
        # Log error but don't expose details
        print(f"UPI generation error: {type(e).__name__}: {e}")
        return error_internal_server_error()

    return build_response(200, upi_response)