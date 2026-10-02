"""
Tests for GST calculation endpoint handler.
"""

import json
from unittest.mock import patch, Mock
from src.handlers.gst import handle_gst_calculate


class TestGSTCalculateEndpoint:
    """Tests for the /gst/calculate endpoint handler."""

    def test_valid_gst_calculation(self):
        """Valid request returns correct calculation."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({
                'items': [
                    {'name': 'mouse', 'quantity': 10, 'unit_price': 100},
                ],
                'customer_state': 'MAHARASHTRA',
            }),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['totalSubtotal'] == 1000.0
        assert body['totalGstAmount'] == 180.0
        assert body['totalCgst'] == 90.0
        assert body['totalSgst'] == 90.0
        assert body['totalIgst'] == 0.0
        assert body['grandTotal'] == 1180.0
        assert body['taxType'] == 'intra_state'
        assert body['sellerState'] == 'MAHARASHTRA'
        assert body['customerState'] == 'MAHARASHTRA'
        assert body['gstMismatch'] is False
        assert len(body['items']) == 1
        item = body['items'][0]
        assert item['name'] == 'mouse'
        assert item['quantity'] == 10
        assert item['unitPrice'] == 100.0
        assert item['gstRate'] == 18.0
        assert item['gstAmount'] == 180.0
        assert item['cgstAmount'] == 90.0
        assert item['sgstAmount'] == 90.0
        assert item['igstAmount'] == 0.0
        assert item['gstMismatch'] is False
        assert item['taxType'] == 'intra_state'

    def test_inter_state_calculation(self):
        """Inter-state calculation uses IGST."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({
                'items': [
                    {'name': 'mouse', 'quantity': 10, 'unit_price': 100},
                ],
                'customer_state': 'KARNATAKA',
            }),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['taxType'] == 'inter_state'
        assert body['totalIgst'] == 180.0
        assert body['totalCgst'] == 0.0
        assert body['totalSgst'] == 0.0
        assert body['customerState'] == 'KARNATAKA'

    def test_multiple_items_calculation(self):
        """Multiple items are calculated correctly."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({
                'items': [
                    {'name': 'mouse', 'quantity': 10, 'unit_price': 100},
                    {'name': 'keyboard', 'quantity': 5, 'unit_price': 200},
                ],
                'customer_state': 'MAHARASHTRA',
            }),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert len(body['items']) == 2
        assert body['totalSubtotal'] == 2000.0
        assert body['totalGstAmount'] == 360.0
        assert body['grandTotal'] == 2360.0
        assert len(body['items']) == 2

    def test_gst_mismatch_detection(self):
        """Mismatch between stated and determined GST rate is detected."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({
                'items': [
                    {'name': 'mouse', 'quantity': 1, 'unit_price': 100, 'stated_gst_rate': 5},
                ],
                'customer_state': 'MAHARASHTRA',
            }),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['gstMismatch'] is True
        assert body['statedGstRate'] == 5.0
        assert body['determinedGstRate'] == 18.0
        assert len(body['mismatchDetails']) == 1
        assert 'mouse' in body['mismatchDetails'][0]
        assert '5' in body['mismatchDetails'][0]
        assert '18' in body['mismatchDetails'][0]

    def test_no_mismatch_when_equal(self):
        """No mismatch when stated equals determined."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({
                'items': [
                    {'name': 'mouse', 'quantity': 1, 'unit_price': 100, 'stated_gst_rate': 18},
                ],
                'customer_state': 'MAHARASHTRA',
            }),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['gstMismatch'] is False

    def test_no_stated_gst_rate(self):
        """No mismatch when no stated rate provided."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({
                'items': [
                    {'name': 'mouse', 'quantity': 1, 'unit_price': 100},
                ],
                'customer_state': 'MAHARASHTRA',
            }),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['gstMismatch'] is False
        assert body['statedGstRate'] is None

    def test_unknown_product_uses_default_rate(self):
        """Unknown product uses default 18% rate."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({
                'items': [
                    {'name': 'unknown_product_xyz', 'quantity': 1, 'unit_price': 100},
                ],
                'customer_state': 'MAHARASHTRA',
            }),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['determinedGstRate'] == 18.0

    def test_missing_items_returns_400(self):
        """Missing items field returns 400."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({'customer_state': 'MAHARASHTRA'}),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'MISSING_ITEMS'

    def test_empty_items_returns_400(self):
        """Empty items list returns 400."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({'items': []}),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'EMPTY_ITEMS'

    def test_missing_item_name_returns_400(self):
        """Missing item name returns 400."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({'items': [{'quantity': 1, 'unit_price': 100}]}),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'MISSING_ITEM_NAME'

    def test_zero_quantity_returns_400(self):
        """Zero quantity returns 400."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({'items': [{'name': 'mouse', 'quantity': 0, 'unit_price': 100}]}),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_QUANTITY'

    def test_negative_quantity_returns_400(self):
        """Negative quantity returns 400."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({'items': [{'name': 'mouse', 'quantity': -1, 'unit_price': 100}]}),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_QUANTITY'

    def test_non_integer_quantity_returns_400(self):
        """Non-integer quantity returns 400."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({'items': [{'name': 'mouse', 'quantity': 1.5, 'unit_price': 100}]}),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_QUANTITY'

    def test_negative_unit_price_returns_400(self):
        """Negative unit price returns 400."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({'items': [{'name': 'mouse', 'quantity': 1, 'unit_price': -100}]}),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_UNIT_PRICE'

    def test_invalid_stated_gst_rate_returns_400(self):
        """Invalid stated GST rate returns 400."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({'items': [{'name': 'mouse', 'quantity': 1, 'unit_price': 100, 'stated_gst_rate': 150}]}),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_STATED_GST_RATE'

    def test_get_method_returns_405(self):
        """GET method returns 405."""
        event = {
            'httpMethod': 'GET',
            'path': '/gst/calculate',
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        assert response['statusCode'] == 405
        body = json.loads(response['body'])
        assert body['code'] == 'METHOD_NOT_ALLOWED'

    def test_cors_headers_present(self):
        """Response includes CORS headers."""
        event = {
            'httpMethod': 'POST',
            'path': '/gst/calculate',
            'body': json.dumps({
                'items': [{'name': 'mouse', 'quantity': 1, 'unit_price': 100}],
                'customer_state': 'MAHARASHTRA',
            }),
        }
        context = {}
        
        response = handle_gst_calculate(event, context)
        
        headers = response['headers']
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Content-Type'] == 'application/json'