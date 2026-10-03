"""
UPI Payment Request endpoint handler.

POST /upi/generate

Generates UPI payment request with deep link and QR code.
Does NOT process real payments - honest/simulated status only.
Persists UPI info to the associated invoice.
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
    error_not_found,
    build_response,
)
from src.services.upi_service import (
    create_upi_payment_request,
    validate_upi_request,
    DEFAULT_MERCHANT_VPA,
    DEFAULT_MERCHANT_NAME,
)
from src.services.persistence_service import (
    add_upi_payment_info,
    retrieve_invoice,
)


def handle_upi_generate(event: dict, context: object) -> dict:
    """
    Handle POST /upi/generate requests.
    
    Generates UPI payment request with deep link and QR code.
    Does NOT process real payments - honest/simulated status only.
    Persists UPI info to the associated invoice.
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

    # Persist UPI info to the associated invoice
    invoice_number = data.get('invoice_number')
    if invoice_number:
        try:
            # First retrieve the invoice to get its ID
            invoice = retrieve_invoice(invoice_number)
            if invoice:
                # Add UPI info to the invoice
                add_upi_payment_info(invoice.invoice_number, upi_response)
            else:
                print(f"Warning: Invoice not found for UPI persistence: {invoice_number}")
        except Exception as e:
            # Log but don't fail the request - UPI response is still valid
            print(f"UPI persistence warning: {type(e).__name__}: {e}")

    return build_response(200, upi_response)