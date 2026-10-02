"""
Tests for POST /extract endpoint with Bedrock integration.
"""

import json
from unittest.mock import Mock, patch
from src.handlers.extract import handle_extract
from src.models.response import ExtractionItem
from src.services.bedrock_client import BedrockResponse
from src.services.response_parser import ParseResult
from src.models.extraction import BedrockExtraction, ExtractionItem as ModelExtractionItem


class TestExtractEndpoint:
    """Tests for the /extract endpoint handler."""

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
        
        # Should not crash - validation happens before Bedrock call
        assert response['statusCode'] in (200, 500)


class TestExtractWithMockedBedrock:
    """Tests for /extract endpoint with mocked Bedrock client."""

    @patch('src.handlers.extract._get_bedrock_client')
    def test_valid_extract_returns_bedrock_response(self, mock_get_client):
        """Valid request with successful Bedrock call returns extraction."""
        # Setup mock Bedrock client
        mock_client = Mock()
        mock_client.invoke_model.return_value = BedrockResponse(
            success=True,
            content='{"customer": "Acme", "location": "Pune", "items": [{"name": "mouse", "quantity": 50, "unit_price": 450}], "stated_gst_rate": 5}',
        )
        mock_get_client.return_value = mock_client
        
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': 'bhaiya 50 mouse 450 wala, Acme Pune ko, 5% gst laga dena'}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['source'] == 'bedrock'
        assert body['customer'] == 'Acme'
        assert body['location'] == 'Pune'
        assert len(body['items']) == 1
        assert body['items'][0]['name'] == 'mouse'
        assert body['items'][0]['quantity'] == 50
        assert body['items'][0]['unitPrice'] == 450
        assert body['statedGstRate'] == 5

    @patch('src.handlers.extract._get_bedrock_client')
    def test_bedrock_throttled_returns_500(self, mock_get_client):
        """Bedrock throttling returns 500 without exposing details."""
        mock_client = Mock()
        mock_client.invoke_model.return_value = BedrockResponse(
            success=False,
            error_code='BEDROCK_THROTTLED',
            error_message='Bedrock request was throttled',
        )
        mock_get_client.return_value = mock_client
        
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': 'test message'}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['code'] == 'INTERNAL_ERROR'
        # No internal details exposed
        assert 'throttled' not in body['error'].lower()

    @patch('src.handlers.extract._get_bedrock_client')
    def test_bedrock_access_denied_returns_500(self, mock_get_client):
        """Bedrock access denied returns 500."""
        mock_client = Mock()
        mock_client.invoke_model.return_value = BedrockResponse(
            success=False,
            error_code='BEDROCK_ACCESS_DENIED',
            error_message='Access denied to Bedrock model',
        )
        mock_get_client.return_value = mock_client
        
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': 'test message'}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['code'] == 'INTERNAL_ERROR'

    @patch('src.handlers.extract._get_bedrock_client')
    def test_bedrock_invalid_json_returns_500(self, mock_get_client):
        """Bedrock returning invalid JSON returns 500."""
        mock_client = Mock()
        mock_client.invoke_model.return_value = BedrockResponse(
            success=True,
            content='not valid json at all',
        )
        mock_get_client.return_value = mock_client
        
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': 'test message'}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 500

    @patch('src.handlers.extract._get_bedrock_client')
    def test_bedrock_missing_fields_returns_500(self, mock_get_client):
        """Bedrock response missing required fields returns 500."""
        mock_client = Mock()
        mock_client.invoke_model.return_value = BedrockResponse(
            success=True,
            content='{"customer": "Acme"}',  # missing location, items, gst
        )
        mock_get_client.return_value = mock_client
        
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': 'test message'}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 500

    @patch('src.handlers.extract._get_bedrock_client')
    def test_bedrock_negative_quantity_returns_500(self, mock_get_client):
        """Bedrock response with negative quantity returns 500."""
        mock_client = Mock()
        mock_client.invoke_model.return_value = BedrockResponse(
            success=True,
            content='{"customer": "Acme", "location": "Pune", "items": [{"name": "mouse", "quantity": -5, "unit_price": 450}], "stated_gst_rate": 5}',
        )
        mock_get_client.return_value = mock_client
        
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': 'test message'}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 500

    @patch('src.handlers.extract._get_bedrock_client')
    def test_bedrock_invalid_gst_rate_returns_500(self, mock_get_client):
        """Bedrock response with invalid GST rate returns 500."""
        mock_client = Mock()
        mock_client.invoke_model.return_value = BedrockResponse(
            success=True,
            content='{"customer": "Acme", "location": "Pune", "items": [{"name": "mouse", "quantity": 10, "unit_price": 450}], "stated_gst_rate": 150}',
        )
        mock_get_client.return_value = mock_client
        
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': 'test message'}),
        }
        context = {}
        
        response = handle_extract(event, context)
        
        assert response['statusCode'] == 500

    @patch('src.handlers.extract._get_bedrock_client')
    def test_extract_response_has_cors_headers(self, mock_get_client):
        """Extract response includes CORS headers."""
        mock_client = Mock()
        mock_client.invoke_model.return_value = BedrockResponse(
            success=True,
            content='{"customer": "Acme", "location": "Pune", "items": [{"name": "mouse", "quantity": 10, "unit_price": 450}], "stated_gst_rate": 5}',
        )
        mock_get_client.return_value = mock_client
        
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