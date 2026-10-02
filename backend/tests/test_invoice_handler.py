"""
Tests for Invoice Generation endpoint handler.
"""

import json
from src.handlers.invoice import handle_invoice_generate
from src.services.invoice_service import DEFAULT_SELLER


class TestInvoiceGenerateEndpoint:
    """Tests for the /invoice/generate endpoint handler."""

    def _create_valid_request(self, overrides=None):
        """Create a valid invoice generation request."""
        base = {
            'customer_name': 'Acme Corp',
            'customer_location': 'PUNE',
            'items': [
                {'name': 'Mouse', 'quantity': 10, 'unit_price': 100.0},
            ],
            'stated_gst_rate': 5.0,
            'gst_calculation': {
                'items': [
                    {
                        'name': 'Mouse',
                        'quantity': 10,
                        'unit_price': 100.0,
                        'subtotal': 1000.0,
                        'gst_rate': 18.0,
                        'gst_amount': 180.0,
                        'cgst_rate': 9.0,
                        'cgst_amount': 90.0,
                        'sgst_rate': 9.0,
                        'sgst_amount': 90.0,
                        'igst_rate': 0.0,
                        'igst_amount': 0.0,
                        'stated_gst_rate': 5.0,
                        'gst_mismatch': True,
                        'tax_type': 'intra_state',
                    }
                ],
                'total_subtotal': 1000.0,
                'total_gst_amount': 180.0,
                'total_cgst': 90.0,
                'total_sgst': 90.0,
                'total_igst': 0.0,
                'grand_total': 1180.0,
                'tax_type': 'intra_state',
                'seller_state': 'MAHARASHTRA',
                'customer_state': 'PUNE',
                'determined_gst_rate': 18.0,
                'stated_gst_rate': 5.0,
                'gst_mismatch': True,
                'mismatch_details': ['Item Mouse: stated 5%, rules determine 18%'],
            }
        }
        if overrides:
            # Deep merge overrides
            import copy
            request = json.loads(json.dumps(overrides))
            return request
        return base

    def test_valid_invoice_generation(self):
        """Valid request returns correct invoice."""
        event = {
            'httpMethod': 'POST',
            'path': '/invoice/generate',
            'body': json.dumps(self._create_valid_request()),
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] == 'pending'
        assert body['invoiceNumber'].startswith('INV-')
        assert body['seller']['name'] == 'INVOX Demo Seller'
        assert body['customer']['name'] == 'Acme Corp'
        assert body['customer']['location'] == 'PUNE'
        assert len(body['items']) == 1
        item = body['items'][0]
        assert item['name'] == 'Mouse'
        assert item['quantity'] == 10
        assert item['unitPrice'] == 100.0
        assert item['subtotal'] == 1000.0
        assert item['gstRate'] == 18.0
        assert item['gstAmount'] == 180.0
        assert item['cgstAmount'] == 90.0
        assert item['sgstAmount'] == 90.0
        assert item['igstAmount'] == 0.0
        assert item['gstMismatch'] is True
        assert item['taxType'] == 'intra_state'
        assert body['totalSubtotal'] == 1000.0
        assert body['totalGstAmount'] == 180.0
        assert body['totalCgst'] == 90.0
        assert body['totalSgst'] == 90.0
        assert body['totalIgst'] == 0.0
        assert body['grandTotal'] == 1180.0
        assert body['taxType'] == 'intra_state'
        assert body['sellerState'] == 'MAHARASHTRA'
        assert body['customerState'] == 'PUNE'
        assert body['statedGstRate'] == 5.0
        assert body['determinedGstRate'] == 18.0
        assert body['gstMismatch'] is True
        assert len(body['mismatchDetails']) == 1
        assert 'Mouse' in body['mismatchDetails'][0]
        assert '5' in body['mismatchDetails'][0]
        assert '18' in body['mismatchDetails'][0]

    def test_inter_state_invoice_generation(self):
        """Inter-state invoice uses IGST."""
        request = self._create_valid_request()
        request['gst_calculation']['tax_type'] = 'inter_state'
        request['gst_calculation']['customer_state'] = 'KARNATAKA'
        request['gst_calculation']['items'][0]['tax_type'] = 'inter_state'
        request['gst_calculation']['items'][0]['cgst_rate'] = 0.0
        request['gst_calculation']['items'][0]['cgst_amount'] = 0.0
        request['gst_calculation']['items'][0]['sgst_rate'] = 0.0
        request['gst_calculation']['items'][0]['sgst_amount'] = 0.0
        request['gst_calculation']['items'][0]['igst_rate'] = 18.0
        request['gst_calculation']['items'][0]['igst_amount'] = 180.0
        request['gst_calculation']['total_cgst'] = 0.0
        request['gst_calculation']['total_sgst'] = 0.0
        request['gst_calculation']['total_igst'] = 180.0
        request['gst_calculation']['customer_state'] = 'KARNATAKA'
        
        event = {
            'httpMethod': 'POST',
            'path': '/invoice/generate',
            'body': json.dumps(request),
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['taxType'] == 'inter_state'
        assert body['totalIgst'] == 180.0
        assert body['totalCgst'] == 0.0
        assert body['totalSgst'] == 0.0
        assert body['items'][0]['taxType'] == 'inter_state'
        assert body['items'][0]['igstAmount'] == 180.0
        assert body['items'][0]['cgstAmount'] == 0.0
        assert body['items'][0]['sgstAmount'] == 0.0

    def test_multiple_items_invoice(self):
        """Multiple items invoice is generated correctly."""
        request = self._create_valid_request()
        request['gst_calculation']['items'] = [
            {
                'name': 'Mouse',
                'quantity': 10,
                'unit_price': 100.0,
                'subtotal': 1000.0,
                'gst_rate': 18.0,
                'gst_amount': 180.0,
                'cgst_rate': 9.0,
                'cgst_amount': 90.0,
                'sgst_rate': 9.0,
                'sgst_amount': 90.0,
                'igst_rate': 0.0,
                'igst_amount': 0.0,
                'stated_gst_rate': 5.0,
                'gst_mismatch': True,
                'tax_type': 'intra_state',
            },
            {
                'name': 'Keyboard',
                'quantity': 5,
                'unit_price': 200.0,
                'subtotal': 1000.0,
                'gst_rate': 18.0,
                'gst_amount': 180.0,
                'cgst_rate': 9.0,
                'cgst_amount': 90.0,
                'sgst_rate': 9.0,
                'sgst_amount': 90.0,
                'igst_rate': 0.0,
                'igst_amount': 0.0,
                'stated_gst_rate': 18.0,
                'gst_mismatch': False,
                'tax_type': 'intra_state',
            },
        ]
        request['gst_calculation']['total_subtotal'] = 2000.0
        request['gst_calculation']['total_gst_amount'] = 360.0
        request['gst_calculation']['total_cgst'] = 180.0
        request['gst_calculation']['total_sgst'] = 180.0
        request['gst_calculation']['total_igst'] = 0.0
        request['gst_calculation']['grand_total'] = 2360.0
        request['gst_calculation']['items'][1]['cgst_rate'] = 9.0
        request['gst_calculation']['items'][1]['cgst_amount'] = 90.0
        request['gst_calculation']['items'][1]['sgst_rate'] = 9.0
        request['gst_calculation']['items'][1]['sgst_amount'] = 90.0
        request['gst_calculation']['items'][1]['igst_rate'] = 0.0
        request['gst_calculation']['items'][1]['igst_amount'] = 0.0
        
        event = {
            'httpMethod': 'POST',
            'path': '/invoice/generate',
            'body': json.dumps(request),
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert len(body['items']) == 2
        assert body['totalSubtotal'] == 2000.0
        assert body['totalGstAmount'] == 360.0
        assert body['grandTotal'] == 2360.0

    def test_missing_gst_calculation_returns_400(self):
        """Missing gst_calculation returns 400."""
        event = {
            'httpMethod': 'POST',
            'path': '/invoice/generate',
            'body': json.dumps({'customer_name': 'Acme Corp'}),
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_INPUT'
        assert 'GST calculation result is required' in body['error']

    def test_missing_items_in_gst_calculation_returns_400(self):
        """Missing items in gst_calculation returns 400."""
        event = {
            'httpMethod': 'POST',
            'path': '/invoice/generate',
            'body': json.dumps({
                'gst_calculation': {
                    'total_subtotal': 1000.0,
                    'total_gst_amount': 180.0,
                    'grand_total': 1180.0,
                    'tax_type': 'intra_state',
                    'seller_state': 'MAHARASHTRA',
                    'determined_gst_rate': 18.0,
                }
            }),
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_INPUT'
        assert 'At least one item is required' in body['details']['errors'][0]

    def test_missing_item_name_returns_400(self):
        """Missing item name returns 400."""
        request = {
            'gst_calculation': {
                'items': [{'quantity': 10, 'unit_price': 100.0}],
                'total_subtotal': 1000.0,
                'total_gst_amount': 180.0,
                'grand_total': 1180.0,
                'tax_type': 'intra_state',
                'seller_state': 'MAHARASHTRA',
                'determined_gst_rate': 18.0,
            }
        }
        event = {
            'httpMethod': 'POST',
            'path': '/invoice/generate',
            'body': json.dumps(request),
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_INPUT'
        assert 'name is required' in body['details']['errors'][0]

    def test_zero_quantity_returns_400(self):
        """Zero quantity returns 400."""
        request = self._create_valid_request()
        request['gst_calculation']['items'][0]['quantity'] = 0
        
        event = {
            'httpMethod': 'POST',
            'path': '/invoice/generate',
            'body': json.dumps(request),
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_INPUT'

    def test_negative_quantity_returns_400(self):
        """Negative quantity returns 400."""
        request = self._create_valid_request()
        request['gst_calculation']['items'][0]['quantity'] = -1
        
        event = {
            'httpMethod': 'POST',
            'path': '/invoice/generate',
            'body': json.dumps(request),
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_INPUT'

    def test_negative_unit_price_returns_400(self):
        """Negative unit price returns 400."""
        request = self._create_valid_request()
        request['gst_calculation']['items'][0]['unit_price'] = -100.0
        
        event = {
            'httpMethod': 'POST',
            'path': '/invoice/generate',
            'body': json.dumps(request),
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_INPUT'

    def test_invalid_stated_gst_rate_returns_400(self):
        """Invalid stated GST rate returns 400."""
        request = self._create_valid_request()
        request['gst_calculation']['items'][0]['stated_gst_rate'] = 150
        
        event = {
            'httpMethod': 'POST',
            'path': '/invoice/generate',
            'body': json.dumps(request),
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_INPUT'

    def test_get_method_returns_405(self):
        """GET method returns 405."""
        event = {
            'httpMethod': 'GET',
            'path': '/invoice/generate',
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        assert response['statusCode'] == 405
        body = json.loads(response['body'])
        assert body['code'] == 'METHOD_NOT_ALLOWED'

    def test_cors_headers_present(self):
        """Response includes CORS headers."""
        event = {
            'httpMethod': 'POST',
            'path': '/invoice/generate',
            'body': json.dumps(self._create_valid_request()),
        }
        context = {}
        
        response = handle_invoice_generate(event, context)
        
        headers = response['headers']
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Content-Type'] == 'application/json'