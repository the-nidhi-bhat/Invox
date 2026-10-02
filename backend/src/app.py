"""
INVOX Lambda Handler — Main entry point.

Routes API Gateway requests to appropriate handlers.
Supports:
- GET /health
- POST /extract
- POST /gst/calculate
- OPTIONS (CORS preflight)
"""

import json
from src.handlers.health import handle_health
from src.handlers.extract import handle_extract
from src.handlers.gst import handle_gst_calculate
from src.utils.responses import (
    error_not_found,
    error_method_not_allowed,
    build_response,
)


def route_request(event: dict, context: object) -> dict:
    """
    Route the incoming API Gateway request to the appropriate handler.
    
    Args:
        event: API Gateway Lambda proxy event
        context: Lambda context object
        
    Returns:
        Lambda proxy response
    """
    # Extract path and method from event
    # Support both REST API (httpMethod) and HTTP API (requestContext.http.method) formats
    http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method', '')
    path = event.get('path') or event.get('rawPath') or event.get('requestContext', {}).get('http', {}).get('path', '')
    
    # Normalize path (API Gateway may include stage prefix)
    if path.startswith('/prod') or path.startswith('/dev') or path.startswith('/test'):
        # Remove stage prefix if present
        parts = path.split('/', 2)
        if len(parts) > 2:
            path = '/' + parts[2]
        else:
            path = '/'

    # Handle CORS preflight
    if http_method == 'OPTIONS':
        return build_response(200, {}, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        })

    # Route to handlers
    if path == '/health':
        if http_method == 'GET':
            return handle_health(event, context)
        return error_method_not_allowed()
    
    if path == '/extract':
        if http_method == 'POST':
            return handle_extract(event, context)
        return error_method_not_allowed()
    
    if path == '/gst/calculate':
        if http_method == 'POST':
            return handle_gst_calculate(event, context)
        return error_method_not_allowed()

    # Not found
    return error_not_found('NOT_FOUND', f'Endpoint not found: {http_method} {path}')


def lambda_handler(event: dict, context: object) -> dict:
    """
    AWS Lambda entry point.
    
    Wraps route_request with top-level error handling to ensure
    all responses are properly formatted JSON with CORS headers.
    """
    try:
        return route_request(event, context)
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Unhandled error in lambda_handler: {type(e).__name__}: {e}")
        # Return generic error without exposing internal details
        from src.utils.responses import error_internal_server_error
        return error_internal_server_error()