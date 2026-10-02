"""
Input validation for Invoice generation endpoint.

Provides validation functions that can be tested independently
of the Lambda runtime.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ValidationResult:
    """Result of a validation check."""
    valid: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    details: Optional[dict] = None


# Maximum request body size (10 KB)
MAX_REQUEST_SIZE = 10 * 1024


def validate_json_body(body: str) -> ValidationResult:
    """
    Validate that the request body is valid JSON.
    Returns ValidationResult with valid=False if invalid.
    """
    import json
    try:
        json.loads(body)
        return ValidationResult(valid=True)
    except json.JSONDecodeError as e:
        return ValidationResult(
            valid=False,
            error_code='MALFORMED_JSON',
            error_message='Request body must be valid JSON',
            details={'parse_error': str(e)}
        )


def validate_request_size(body: str) -> ValidationResult:
    """
    Validate that the request body size is within limits.
    """
    size = len(body.encode('utf-8'))
    if size > MAX_REQUEST_SIZE:
        return ValidationResult(
            valid=False,
            error_code='REQUEST_TOO_LARGE',
            error_message=f'Request body exceeds maximum size of {MAX_REQUEST_SIZE} bytes',
            details={'max_size_bytes': MAX_REQUEST_SIZE, 'received_size_bytes': size}
        )
    return ValidationResult(valid=True)


# Maximum number of items
MAX_ITEMS = 20


def validate_invoice_request(data: dict) -> ValidationResult:
    """
    Validate the invoice generation request payload.
    """
    # Check gst_calculation field exists
    if 'gst_calculation' not in data:
        return ValidationResult(
            valid=False,
            error_code='MISSING_GST_CALCULATION',
            error_message='Request must contain a "gst_calculation" field',
        )

    gst_calc = data['gst_calculation']

    # Check items field exists
    if 'items' not in gst_calc:
        return ValidationResult(
            valid=False,
            error_code='MISSING_ITEMS',
            error_message='GST calculation must contain an "items" field',
        )

    items = gst_calc['items']

    # Check items is a list
    if not isinstance(items, list):
        return ValidationResult(
            valid=False,
            error_code='INVALID_ITEMS_TYPE',
            error_message='Items must be a list',
            details={'received_type': type(items).__name__}
        )

    # Check at least one item
    if len(items) == 0:
        return ValidationResult(
            valid=False,
            error_code='EMPTY_ITEMS',
            error_message='At least one item is required',
        )

    # Check max items
    if len(items) > 20:
        return ValidationResult(
            valid=False,
            error_code='TOO_MANY_ITEMS',
            error_message=f'Maximum 20 items allowed',
            details={'max_items': 20, 'received': len(items)}
        )

    # Validate each item
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            return ValidationResult(
                valid=False,
                error_code='INVALID_ITEM_TYPE',
                error_message=f'Item {idx} must be an object',
                details={'item_index': idx, 'received_type': type(item).__name__}
            )

        # Check name
        if 'name' not in item:
            return ValidationResult(
                valid=False,
                error_code='MISSING_ITEM_NAME',
                error_message=f'Item {idx} must have a name',
                details={'item_index': idx}
            )

        name = item['name']
        if not isinstance(name, str):
            return ValidationResult(
                valid=False,
                error_code='INVALID_ITEM_NAME_TYPE',
                error_message=f'Item {idx} name must be a string',
                details={'item_index': idx, 'received_type': type(name).__name__}
            )

        if not name.strip():
            return ValidationResult(
                valid=False,
                error_code='EMPTY_ITEM_NAME',
                error_message=f'Item {idx} name cannot be empty',
                details={'item_index': idx}
            )

        # Check quantity
        if 'quantity' not in item:
            return ValidationResult(
                valid=False,
                error_code='MISSING_QUANTITY',
                error_message=f'Item {idx} must have a quantity',
                details={'item_index': idx}
            )

        quantity = item['quantity']
        if not isinstance(quantity, (int, float)):
            return ValidationResult(
                valid=False,
                error_code='INVALID_QUANTITY_TYPE',
                error_message=f'Item {idx} quantity must be a number',
                details={'item_index': idx, 'received_type': type(quantity).__name__}
            )

        if not float(quantity).is_integer():
            return ValidationResult(
                valid=False,
                error_code='INVALID_QUANTITY',
                error_message=f'Item {idx} quantity must be a whole number',
                details={'item_index': idx}
            )

        qty = int(quantity)
        if qty <= 0:
            return ValidationResult(
                valid=False,
                error_code='INVALID_QUANTITY',
                error_message=f'Item {idx} quantity must be positive',
                details={'item_index': idx}
            )

        # Check unit_price
        if 'unit_price' not in item:
            return ValidationResult(
                valid=False,
                error_code='MISSING_UNIT_PRICE',
                error_message=f'Item {idx} must have a unit_price',
                details={'item_index': idx}
            )

        unit_price = item['unit_price']
        if not isinstance(unit_price, (int, float)):
            return ValidationResult(
                valid=False,
                error_code='INVALID_UNIT_PRICE_TYPE',
                error_message=f'Item {idx} unit_price must be a number',
                details={'item_index': idx, 'received_type': type(unit_price).__name__}
            )

        if unit_price < 0:
            return ValidationResult(
                valid=False,
                error_code='INVALID_UNIT_PRICE',
                error_message=f'Item {idx} unit_price cannot be negative',
                details={'item_index': idx}
            )

        # Validate stated_gst_rate if present
        if 'stated_gst_rate' in item and item['stated_gst_rate'] is not None:
            gst_rate = item['stated_gst_rate']
            if not isinstance(gst_rate, (int, float)):
                return ValidationResult(
                    valid=False,
                    error_code='INVALID_STATED_GST_TYPE',
                    error_message=f'Item {idx} stated_gst_rate must be a number',
                    details={'item_index': idx, 'received_type': type(gst_rate).__name__}
                )
            if gst_rate < 0 or gst_rate > 100:
                return ValidationResult(
                    valid=False,
                    error_code='INVALID_STATED_GST_RATE',
                    error_message=f'Item {idx} stated_gst_rate must be between 0 and 100',
                    details={'item_index': idx}
                )

    # Validate customer_state if present
    if 'customer_state' in gst_calc and gst_calc['customer_state'] is not None:
        customer_state = gst_calc['customer_state']
        if not isinstance(customer_state, str):
            return ValidationResult(
                valid=False,
                error_code='INVALID_CUSTOMER_STATE_TYPE',
                error_message='customer_state must be a string',
                details={'received_type': type(customer_state).__name__}
            )

    return ValidationResult(valid=True)