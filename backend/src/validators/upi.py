"""
Input validation for UPI payment request endpoint.

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


def validate_upi_request(data: dict) -> List[str]:
    """
    Validate the UPI payment request payload.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # Check invoice_number
    if 'invoice_number' not in data:
        errors.append("Invoice number is required")
        return errors
    
    invoice_number = data.get('invoice_number')
    if not invoice_number or not str(invoice_number).strip():
        errors.append("Invoice number cannot be empty")
    
    # Check invoice_amount
    if 'invoice_amount' not in data:
        errors.append("Invoice amount is required")
        return errors
    
    amount = data.get('invoice_amount')
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            errors.append("Invoice amount must be positive")
    except (ValueError, TypeError):
        errors.append("Invoice amount must be a valid number")
    
    # Validate currency if present
    if 'currency' in data and data['currency']:
        currency = data['currency']
        if currency != 'INR':
            errors.append("Only INR currency is supported in MVP")
    
    # Validate customer_vpa format if present
    if 'customer_vpa' in data and data['customer_vpa']:
        vpa = data['customer_vpa']
        if not isinstance(vpa, str) or '@' not in vpa:
            errors.append("Customer VPA must be a valid UPI ID format (e.g., user@upi)")
    
    # Validate merchant_vpa format if present
    if 'merchant_vpa' in data and data['merchant_vpa']:
        vpa = data['merchant_vpa']
        if not isinstance(vpa, str) or '@' not in vpa:
            errors.append("Merchant VPA must be a valid UPI ID format (e.g., merchant@upi)")
    
    return errors