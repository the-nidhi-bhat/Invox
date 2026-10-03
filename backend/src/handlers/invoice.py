"""
Invoice Generation and Retrieval endpoint handlers.

POST /invoice/generate - Generate and persist invoice from M6 GST calculation
GET /invoice/{invoice_id} - Retrieve invoice by ID
"""

import json
import hashlib
from src.models.invoice import (
    InvoiceRequest,
    InvoiceResponse,
)
from src.validators.invoice import validate_invoice_request as validate_invoice_request_validator
from src.validators.extract import validate_request_size, validate_json_body
from src.utils.responses import (
    error_bad_request,
    error_payload_too_large,
    error_internal_server_error,
    error_method_not_allowed,
    error_not_found,
    build_response,
)
from src.services.invoice_service import (
    create_invoice_from_gst_calculation,
    validate_invoice_request as validate_invoice_request_service,
    DEFAULT_SELLER,
)
from src.services.persistence_service import (
    persist_invoice,
    retrieve_invoice,
)


def _generate_idempotency_key(data: dict) -> str:
    """Generate deterministic idempotency key from request data."""
    key_data = {
        'customer_name': data.get('customer_name'),
        'customer_location': data.get('customer_location'),
        'items': data.get('items'),
        'stated_gst_rate': data.get('stated_gst_rate'),
        'gst_calculation': data.get('gst_calculation'),
    }
    json_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()[:32]


def handle_invoice_generate(event: dict, context: object) -> dict:
    """
    Handle POST /invoice/generate requests.

    Generates invoice from M6 deterministic GST calculation result.
    Does NOT recalculate GST - uses authoritative M6 calculation.
    Persists invoice to DynamoDB.
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
    validation_result = validate_invoice_request_validator(data)
    if not validation_result.valid:
        return error_bad_request(
            validation_result.error_code,
            validation_result.error_message,
            validation_result.details
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

    # Persist invoice to DynamoDB
    try:
        # Generate idempotency key from request data
        idempotency_key = _generate_idempotency_key(data)

        # Persist invoice (handles idempotency internally)
        # create_invoice_from_gst_calculation returns a dict, persist_invoice returns InvoiceResponse
        persisted_response = persist_invoice(invoice_response, idempotency_key)

        # Use persisted response (includes timestamps)
        invoice_response = persisted_response
    except RuntimeError as e:
        # Log persistence error but don't fail the request - return invoice anyway
        # This ensures backward compatibility if DynamoDB is unavailable
        print(f"Invoice persistence warning: {e}")
        # Continue with in-memory invoice_response
    except Exception as e:
        # Unexpected error - log but don't expose details
        print(f"Invoice persistence error: {type(e).__name__}: {e}")
        # Continue with in-memory invoice_response

    # Handle both dict (from create_invoice_from_gst_calculation) and InvoiceResponse object
    if hasattr(invoice_response, 'to_dict'):
        response_body = invoice_response.to_dict()
    else:
        response_body = invoice_response

    return build_response(200, response_body)


def handle_invoice_get(event: dict, context: object) -> dict:
    """
    Handle GET /invoice/{invoice_id} requests.

    Retrieves an invoice by its ID from DynamoDB.
    """
    # Only allow GET
    http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', ''))
    if http_method != 'GET':
        return error_method_not_allowed()

    # Extract invoice_id from path parameters
    path_params = event.get('pathParameters') or {}
    invoice_id = path_params.get('invoice_id') or path_params.get('id')

    if not invoice_id:
        return error_bad_request('MISSING_INVOICE_ID', 'Invoice ID is required')

    # Retrieve invoice from DynamoDB
    try:
        invoice_response = retrieve_invoice(invoice_id)
    except Exception as e:
        print(f"Invoice retrieval error: {type(e).__name__}: {e}")
        return error_internal_server_error()

    if not invoice_response:
        return error_not_found('INVOICE_NOT_FOUND', f'Invoice not found: {invoice_id}')

    return build_response(200, invoice_response.to_dict())