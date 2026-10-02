"""
Tests for response utilities.
"""

import json
from src.utils.responses import (
    build_response,
    health_ok,
    extract_success,
    error_bad_request,
    error_not_found,
    error_method_not_allowed,
    error_internal_server_error,
    error_payload_too_large,
)
from src.models.response import ExtractResponse, ExtractionItem


class TestBuildResponse:
    """Tests for build_response utility."""

    def test_basic_response_structure(self):
        """Response has correct structure."""
        response = build_response(200, {'key': 'value'})
        
        assert response['statusCode'] == 200
        assert 'headers' in response
        assert 'body' in response
        assert json.loads(response['body']) == {'key': 'value'}

    def test_default_cors_headers(self):
        """Default CORS headers are included."""
        response = build_response(200, {})
        
        headers = response['headers']
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Access-Control-Allow-Headers'] == 'Content-Type'
        assert headers['Access-Control-Allow-Methods'] == 'GET,POST,OPTIONS'
        assert headers['Content-Type'] == 'application/json'

    def test_custom_headers_merged(self):
        """Custom headers are merged with defaults."""
        response = build_response(200, {}, {'X-Custom': 'value'})
        
        headers = response['headers']
        assert headers['X-Custom'] == 'value'
        assert headers['Access-Control-Allow-Origin'] == '*'  # default preserved


class TestHealthOk:
    """Tests for health_ok response."""

    def test_health_ok_structure(self):
        """health_ok returns correct structure."""
        response = health_ok()
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] == 'ok'
        assert body['service'] == 'invox-api'


class TestExtractSuccess:
    """Tests for extract_success response."""

    def test_extract_success_structure(self):
        """extract_success returns correct structure."""
        extraction = ExtractResponse(
            source='mock',
            customer='Acme',
            location='Pune',
            items=[ExtractionItem(name='Mouse', quantity=50, unit_price=450.0)],
            stated_gst_rate=5.0,
        )
        
        response = extract_success(extraction)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['source'] == 'mock'
        assert body['customer'] == 'Acme'
        assert body['location'] == 'Pune'
        assert len(body['items']) == 1
        assert body['items'][0]['name'] == 'Mouse'
        assert body['items'][0]['quantity'] == 50
        assert body['items'][0]['unitPrice'] == 450.0
        assert body['statedGstRate'] == 5.0


class TestErrorResponses:
    """Tests for error response builders."""

    def test_error_bad_request(self):
        """error_bad_request returns 400."""
        response = error_bad_request('TEST_ERROR', 'Test message')
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'TEST_ERROR'
        assert body['error'] == 'Test message'

    def test_error_bad_request_with_details(self):
        """error_bad_request includes details when provided."""
        response = error_bad_request('TEST_ERROR', 'Test message', {'field': 'value'})
        
        body = json.loads(response['body'])
        assert body['details']['field'] == 'value'

    def test_error_not_found(self):
        """error_not_found returns 404."""
        response = error_not_found('NOT_FOUND', 'Resource not found')
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert body['code'] == 'NOT_FOUND'

    def test_error_method_not_allowed(self):
        """error_method_not_allowed returns 405."""
        response = error_method_not_allowed()
        
        assert response['statusCode'] == 405
        body = json.loads(response['body'])
        assert body['code'] == 'METHOD_NOT_ALLOWED'

    def test_error_internal_server_error(self):
        """error_internal_server_error returns 500."""
        response = error_internal_server_error()
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['code'] == 'INTERNAL_ERROR'
        assert 'internal' in body['error'].lower()

    def test_error_payload_too_large(self):
        """error_payload_too_large returns 413."""
        response = error_payload_too_large({'max': 1000, 'received': 2000})
        
        assert response['statusCode'] == 413
        body = json.loads(response['body'])
        assert body['code'] == 'PAYLOAD_TOO_LARGE'
        assert body['details']['max'] == 1000
        assert body['details']['received'] == 2000


class TestErrorResponseNoStackTraces:
    """Ensure error responses never expose stack traces."""

    def test_error_responses_have_no_trace(self):
        """No error response contains traceback or stack trace keywords."""
        responses = [
            error_bad_request('ERR', 'msg'),
            error_not_found('ERR', 'msg'),
            error_method_not_allowed(),
            error_internal_server_error(),
            error_payload_too_large(),
        ]
        
        for response in responses:
            body = json.dumps(json.loads(response['body']))
            assert 'traceback' not in body.lower()
            assert 'stack trace' not in body.lower()
            assert 'file "' not in body.lower()
            assert 'line ' not in body.lower()