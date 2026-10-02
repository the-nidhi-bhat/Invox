"""
Standardized HTTP response utilities for INVOX Lambda.

Ensures consistent response format, headers, and error handling.
"""

import json
from typing import Any, Dict, Optional
from src.models.response import HealthResponse, ExtractResponse, ErrorResponse


def build_response(
    status_code: int,
    body: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Build a standard Lambda proxy integration response.
    
    Args:
        status_code: HTTP status code
        body: Response body as dictionary (will be JSON-serialized)
        headers: Additional headers to include
        
    Returns:
        Lambda proxy response format
    """
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body),
    }


def health_ok() -> Dict[str, Any]:
    """Build successful health check response."""
    response = HealthResponse(status='ok', service='invox-api')
    return build_response(200, response.to_dict())


def extract_success(response: ExtractResponse) -> Dict[str, Any]:
    """Build successful extraction response."""
    return build_response(200, response.to_dict())


def error_response(
    status_code: int,
    error_code: str,
    error_message: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Build standardized error response."""
    response = ErrorResponse(
        error=error_message,
        code=error_code,
        details=details
    )
    return build_response(status_code, response.to_dict())


# Specific error responses for common cases
def error_bad_request(error_code: str, error_message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
    return error_response(400, error_code, error_message, details)


def error_not_found(error_code: str, error_message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
    return error_response(404, error_code, error_message, details)


def error_method_not_allowed() -> Dict[str, Any]:
    return error_response(405, 'METHOD_NOT_ALLOWED', 'HTTP method not allowed for this endpoint')


def error_internal_server_error() -> Dict[str, Any]:
    return error_response(500, 'INTERNAL_ERROR', 'An internal server error occurred')


def error_payload_too_large(details: Optional[Dict] = None) -> Dict[str, Any]:
    return error_response(413, 'PAYLOAD_TOO_LARGE', 'Request payload too large', details)