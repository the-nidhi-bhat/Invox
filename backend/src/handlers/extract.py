"""
Order extraction endpoint handler.

POST /extract

M4: Integrates with Amazon Bedrock for AI-powered extraction.
"""

import json
from src.models.request import ExtractRequest
from src.models.response import ExtractResponse, ExtractionItem
from src.models.extraction import BedrockExtraction
from src.validators.extract import validate_extract_request, validate_request_size, validate_json_body
from src.utils.responses import (
    extract_success,
    error_bad_request,
    error_payload_too_large,
    error_internal_server_error,
    error_method_not_allowed,
)
from src.services.bedrock_client import create_bedrock_client, BedrockConfig
from src.services.extraction_prompt import build_extraction_prompt
from src.services.response_parser import parse_bedrock_response, validate_extraction


# Bedrock client - created once and reused across invocations (Lambda reuse)
_bedrock_client = None


def _get_bedrock_client() -> object:
    """Get or create Bedrock client singleton."""
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = create_bedrock_client()
    return _bedrock_client


def _bedrock_extraction_to_response(extraction: BedrockExtraction) -> ExtractResponse:
    """Convert BedrockExtraction to API ExtractResponse."""
    return ExtractResponse(
        source='bedrock',
        customer=extraction.customer or '',
        location=extraction.location or '',
        items=[
            ExtractionItem(
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in extraction.items
        ],
        stated_gst_rate=extraction.stated_gst_rate if extraction.stated_gst_rate is not None else 0.0,
    )


def handle_extract(event: dict, context: object) -> dict:
    """
    Handle POST /extract requests.
    
    Validates input, invokes Bedrock for extraction, parses and validates response,
    returns normalized extraction.
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

    # Validate extract request
    extract_validation = validate_extract_request(data)
    if not extract_validation.valid:
        return error_bad_request(
            extract_validation.error_code,
            extract_validation.error_message,
            extract_validation.details
        )

    # Extract the message
    message = data['message'].strip()

    # Build prompt and invoke Bedrock
    prompt = build_extraction_prompt(message)
    client = _get_bedrock_client()
    bedrock_result = client.invoke_model(prompt)

    # Handle Bedrock errors
    if not bedrock_result.success:
        # Return safe error without exposing internal details
        return error_internal_server_error()

    # Parse Bedrock response
    parse_result = parse_bedrock_response(bedrock_result.content or '')
    if not parse_result.success:
        return error_internal_server_error()

    extraction = parse_result.extraction

    # Validate parsed extraction
    validation_errors = validate_extraction(extraction)
    if validation_errors:
        # Log validation errors but return safe error to client
        return error_internal_server_error()

    # Convert to API response format
    api_response = _bedrock_extraction_to_response(extraction)
    return extract_success(api_response)