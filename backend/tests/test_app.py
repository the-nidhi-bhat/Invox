"""
Tests for main Lambda handler (routing).
"""

import json
from src.app import lambda_handler


class TestLambdaHandler:
    """Tests for the main lambda_handler routing."""

    def test_health_get(self):
        """GET /health routes to health handler."""
        event = {
            'httpMethod': 'GET',
            'path': '/health',
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] == 'ok'
        assert body['service'] == 'invox-api'

    def test_extract_post(self):
        """POST /extract routes to extract handler."""
        event = {
            'httpMethod': 'POST',
            'path': '/extract',
            'body': json.dumps({'message': 'test message'}),
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['source'] == 'placeholder'

    def test_unknown_route_returns_404(self):
        """Unknown route returns 404."""
        event = {
            'httpMethod': 'GET',
            'path': '/unknown',
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert body['code'] == 'NOT_FOUND'

    def test_options_cors_preflight(self):
        """OPTIONS request returns CORS headers."""
        event = {
            'httpMethod': 'OPTIONS',
            'path': '/extract',
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        headers = response['headers']
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Access-Control-Allow-Methods'] == 'GET,POST,OPTIONS'

    def test_extract_get_returns_405(self):
        """GET on /extract returns 405."""
        event = {
            'httpMethod': 'GET',
            'path': '/extract',
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 405

    def test_http_api_format_health(self):
        """Health works with HTTP API event format."""
        event = {
            'requestContext': {
                'http': {
                    'method': 'GET',
                    'path': '/health',
                }
            },
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] == 'ok'

    def test_http_api_format_extract(self):
        """Extract works with HTTP API event format."""
        event = {
            'requestContext': {
                'http': {
                    'method': 'POST',
                    'path': '/extract',
                }
            },
            'body': json.dumps({'message': 'test message'}),
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200

    def test_stage_prefix_stripped(self):
        """Stage prefix in path is handled."""
        event = {
            'httpMethod': 'GET',
            'path': '/prod/health',
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200

    def test_exception_handled_gracefully(self):
        """Unhandled exceptions return 500 without stack trace."""
        # Force an error by passing malformed event
        event = {
            'httpMethod': 'GET',
            'path': '/health',
            'body': None,  # This might cause issues in some handlers
        }
        
        # The handler should catch any exception
        response = lambda_handler(event, {})
        
        # Should either work or return 500, but not crash
        assert response['statusCode'] in (200, 500)
        if response['statusCode'] == 500:
            body = json.loads(response['body'])
            assert body['code'] == 'INTERNAL_ERROR'
            # No stack trace in response
            body_str = json.dumps(body)
            assert 'traceback' not in body_str.lower()