"""
GST Calculation endpoint handler.

POST /gst/calculate

Calculates deterministic GST for confirmed orders.
"""

import json
from decimal import Decimal
from src.models.gst import (
    GSTCalculationRequest,
    CalculatedItemResponse,
    GSTCalculationResponse,
    TaxType,
)
from src.validators.gst import validate_gst_request
from src.validators.extract import validate_request_size, validate_json_body
from src.utils.responses import (
    error_bad_request,
    error_payload_too_large,
    error_internal_server_error,
    error_method_not_allowed,
    build_response,
)
from src.services.gst_engine import (
    calculate_gst,
    create_default_config,
    GSTLineItem,
    GSTEngineConfig,
)


def _to_decimal(value: float) -> Decimal:
    """Convert float to Decimal safely."""
    return Decimal(str(value))


def _gst_line_item_from_request(req_item: dict) -> GSTLineItem:
    """Convert request item dict to GST engine line item."""
    return GSTLineItem(
        name=req_item['name'],
        quantity=req_item['quantity'],
        unit_price=_to_decimal(req_item['unit_price']),
        stated_gst_rate=_to_decimal(req_item['stated_gst_rate']) if req_item.get('stated_gst_rate') is not None else None,
    )


def _calculated_item_to_response(calculated) -> CalculatedItemResponse:
    """Convert engine calculated item to API response."""
    return CalculatedItemResponse(
        name=calculated.name,
        quantity=calculated.quantity,
        unit_price=float(calculated.unit_price),
        subtotal=float(calculated.subtotal),
        gst_rate=float(calculated.gst_rate),
        gst_amount=float(calculated.gst_amount),
        cgst_rate=float(calculated.cgst_rate),
        cgst_amount=float(calculated.cgst_amount),
        sgst_rate=float(calculated.sgst_rate),
        sgst_amount=float(calculated.sgst_amount),
        igst_rate=float(calculated.igst_rate),
        igst_amount=float(calculated.igst_amount),
        stated_gst_rate=float(calculated.stated_gst_rate) if calculated.stated_gst_rate is not None else None,
        gst_mismatch=calculated.gst_mismatch,
        tax_type=calculated.tax_type.value,
    )


def handle_gst_calculate(event: dict, context: object) -> dict:
    """
    Handle POST /gst/calculate requests.
    
    Calculates deterministic GST for confirmed orders.
    Does NOT use AI for financial calculations.
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

    # Validate GST calculation request
    gst_validation = validate_gst_request(data)
    if not gst_validation.valid:
        return error_bad_request(
            gst_validation.error_code,
            gst_validation.error_message,
            gst_validation.details
        )

    # Convert request to engine format
    try:
        items = [_gst_line_item_from_request(item) for item in data['items']]
        customer_state = data.get('customer_state')
        
        # Use default config (MVP rules)
        config = create_default_config()
        
        # Calculate GST
        result = calculate_gst(items, customer_state, config)
    except ValueError as e:
        return error_bad_request('INVALID_INPUT', str(e))
    except Exception as e:
        # Log error but don't expose details
        print(f"GST calculation error: {type(e).__name__}: {e}")
        return error_internal_server_error()

    # Convert to API response
    response = GSTCalculationResponse(
        items=[_calculated_item_to_response(item) for item in result.items],
        total_subtotal=float(result.total_subtotal),
        total_gst_amount=float(result.total_gst_amount),
        total_cgst=float(result.total_cgst),
        total_sgst=float(result.total_sgst),
        total_igst=float(result.total_igst),
        grand_total=float(result.grand_total),
        tax_type=result.tax_type.value,
        seller_state=result.seller_state,
        customer_state=result.customer_state,
        stated_gst_rate=float(result.stated_gst_rate) if result.stated_gst_rate is not None else None,
        determined_gst_rate=float(result.determined_gst_rate),
        gst_mismatch=result.gst_mismatch,
        mismatch_details=result.mismatch_details,
    )

    return build_response(200, response.to_dict())