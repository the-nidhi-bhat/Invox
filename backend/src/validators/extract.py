"""
Input validation for INVOX API endpoints.

Provides validation functions that can be tested independently
of the Lambda runtime.
"""

from dataclasses import dataclass
from typing import Optional

# Maximum request body size (10 KB)
MAX_REQUEST_SIZE = 10 * 1024

# Maximum message length
MAX_MESSAGE_LENGTH = 5000


@dataclass
class ValidationResult:
    """Result of a validation check."""
    valid: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    details: Optional[dict] = None


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


def validate_extract_request(data: dict) -> ValidationResult:
    """
    Validate the extract request payload.
    Checks: message exists, is string, not empty, reasonable length.
    """
    # Check message field exists
    if 'message' not in data:
        return ValidationResult(
            valid=False,
            error_code='MISSING_MESSAGE',
            error_message='Request must contain a "message" field',
        )

    message = data['message']

    # Check message is a string
    if not isinstance(message, str):
        return ValidationResult(
            valid=False,
            error_code='INVALID_MESSAGE_TYPE',
            error_message='Message must be a string',
            details={'received_type': type(message).__name__}
        )

    # Check message is not empty after trimming
    if not message.strip():
        return ValidationResult(
            valid=False,
            error_code='EMPTY_MESSAGE',
            error_message='Message must not be empty',
        )

    # Check message length
    if len(message) > MAX_MESSAGE_LENGTH:
        return ValidationResult(
            valid=False,
            error_code='MESSAGE_TOO_LONG',
            error_message=f'Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters',
            details={'max_length': MAX_MESSAGE_LENGTH, 'received_length': len(message)}
        )

    return ValidationResult(valid=True)


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