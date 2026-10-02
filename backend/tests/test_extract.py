"""
Tests for POST /extract endpoint.
"""

import json
from src.handlers.extract import handle_extract, PLACEHOLDER_EXTRACTION
from src.models.response import ExtractionItem


class TestExtractEndpoint:
    """Tests for the /extract endpoint handler."""

    def test_valid_extract_request_returns_placeholder(self):
        """Valid request returns deterministic placeholder response."""
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': 'bhaiya 50 mouse 450 wala, Acme Pune ko, 5% gst laga dena'}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['source'] == 'placeholder'
        assert 'not yet implemented' in body['customer'].lower()
        assert 'not yet implemented' in body['location'].lower()
        assert len(body['items']) == 1
        assert body['items'][0]['name'] == '[Extraction not yet implemented]'
        assert body['items'][0]['quantity'] == 1
        assert body['items'][0]['unitPrice'] == 0.0
        assert body['statedGstRate'] == 0.0

    def test_valid_extract_request_has_cors_headers(self):
        """Extract response includes CORS headers."""
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': 'test message'}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        headers = response['headers']
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Content-Type'] == 'application/json'

    def test_missing_message_returns_400(self):
        """Request without message field returns 400 with MISSING_MESSAGE code."""
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'MISSING_MESSAGE'
        assert 'message' in body['error'].lower()

    def test_empty_message_returns_400(self):
        """Request with empty message returns 400 with EMPTY_MESSAGE code."""
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': ''}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'EMPTY_MESSAGE'

    def test_whitespace_only_message_returns_400(self):
        """Request with whitespace-only message returns 400."""
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': '   \n\t  '}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'EMPTY_MESSAGE'

    def test_invalid_message_type_returns_400(self):
        """Request with non-string message returns 400 with INVALID_MESSAGE_TYPE code."""
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': 123}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_MESSAGE_TYPE'
        assert body['details']['received_type'] == 'int'

    def test_message_too_long_returns_400(self):
        """Request with message exceeding max length returns 400."""
        long_message = 'x' * 5001
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': long_message}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'MESSAGE_TOO_LONG'
        assert body['details']['max_length'] == 5000
        assert body['details']['received_length'] == 5001

    def test_malformed_json_returns_400(self):
        """Request with invalid JSON returns 400 with MALFORMED_JSON code."""
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': '{not valid json}',
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'MALFORMED_JSON'

    def test_oversized_request_returns_413(self):
        """Request exceeding size limit returns 413."""
        # Create a body larger than 10KB
        large_message = 'x' * 15000
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': large_message}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 413
        body = json.loads(response['body'])
        assert body['code'] == 'PAYLOAD_TOO_LARGE'

    def test_get_method_returns_405(self):
        """GET request to /extract returns 405 METHOD_NOT_ALLOWED."""
        event = {
            'httpMethod': 'GET',
            'path': '/extract',
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 405
        body = json.loads(response['body'])
        assert body['code'] == 'METHOD_NOT_ALLOWED'

    def test_put_method_returns_405(self):
        """PUT request to /extract returns 405."""
        event = {
            'httpMethod': 'PUT',
            'path': '/extract',
            'body': json.dumps({'message': 'test'}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 405

    def test_delete_method_returns_405(self):
        """DELETE request to /extract returns 405."""
        event = {
            'httpMethod': 'DELETE',
            'path': '/extract',
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 405

    def test_placeholder_response_is_deterministic(self):
        """Placeholder response is identical for all valid inputs."""
        messages = [
            'bhaiya 50 mouse 450 wala',
            'hello world',
            'different message entirely',
        ]
        
        responses = []
        for msg in messages:
            event = {
                'httpMethod': 'POST',
                'path': '/extract',
                'body': json.dumps({'message': msg}),
            }
            response = handle_extract(event, {})
            responses.append(json.loads(response['body']))
        
        # All responses should be identical
        assert responses[0] == responses[1] == responses[2]
        assert responses[0]['source'] == 'placeholder'

    def test_extract_via_http_api_format(self):
        """Extract works with HTTP API event format (requestContext.http)."""
        event = {
            'requestContext': {
                'http': {
                    'method': 'POST',
                    'path': '/extract',
                }
            },
            'body': json.dumps({'message': 'test message'}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 200