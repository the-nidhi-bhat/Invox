"""
Tests for GET /health endpoint.
"""

import json
from src.handlers.health import handle_health


def test_health_endpoint_returns_ok():
    """Health endpoint returns status ok with service name."""
    event = {
        'httpMethod': 'GET',
        'path': '/health',
    }
    context = {}
    
    response = handle_health(event, context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['status'] == 'ok'
    assert body['service'] == 'invox-api'


def test_health_endpoint_has_cors_headers():
    """Health response includes CORS headers."""
    event = {'httpMethod': 'GET', 'path': '/health'}
    context = {}
    
    response = handle_health(event, context)
    
    headers = response['headers']
    assert headers['Access-Control-Allow-Origin'] == '*'
    assert 'Content-Type' in headers
    assert headers['Content-Type'] == 'application/json'