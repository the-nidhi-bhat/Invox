"""
Tests for Invoice Handlers (M9 persistence endpoints).

Tests the GET /invoice/{invoice_id} endpoint and updated POST /invoice/generate.
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch

from src.handlers.invoice import (
    handle_invoice_generate,
    handle_invoice_get,
    _generate_idempotency_key,
)
from src.services.persistence_service import reset_repository


class MockRepository:
    """Mock repository for testing handlers."""
    
    def __init__(self):
        self.invoices = {}
        self.save_called = False
        self.retrieve_called = False
    
    def save_invoice(self, invoice):
        self.save_called = True
        self.invoices[invoice.invoice_id] = invoice
        return invoice
    
    def get_invoice(self, invoice_id):
        self.retrieve_called = True
        return self.invoices.get(invoice_id)


@pytest.fixture(autouse=True)
def reset_repo():
    """Reset repository before each test."""
    reset_repository()
    yield
    reset_repository()


@pytest.fixture
def mock_repo():
    """Create a mock repository."""
    return MockRepository()


@pytest.fixture
def sample_invoice_request():
    """Create a sample invoice generation request."""
    return {
        "customer_name": "Test Customer",
        "customer_location": "Mumbai, MAHARASHTRA",
        "items": [
            {
                "name": "Product 1",
                "quantity": 1,
                "unit_price": 100.0,
            }
        ],
        "gst_calculation": {
            "items": [
                {
                    "name": "Product 1",
                    "quantity": 1,
                    "unit_price": 100.0,
                    "subtotal": 100.0,
                    "gst_rate": 18.0,
                    "gst_amount": 18.0,
                    "cgst_rate": 9.0,
                    "cgst_amount": 9.0,
                    "sgst_rate": 9.0,
                    "sgst_amount": 9.0,
                    "igst_rate": 0.0,
                    "igst_amount": 0.0,
                    "tax_type": "intra_state",
                }
            ],
            "total_subtotal": 100.0,
            "total_gst_amount": 18.0,
            "total_cgst": 9.0,
            "total_sgst": 9.0,
            "total_igst": 0.0,
            "grand_total": 118.0,
            "tax_type": "intra_state",
            "seller_state": "MAHARASHTRA",
            "customer_state": "MAHARASHTRA",
            "determined_gst_rate": 18.0,
            "gst_mismatch": False,
            "mismatch_details": [],
        },
    }


class TestGenerateIdempotencyKey:
    """Tests for _generate_idempotency_key function."""

    def test_same_data_produces_same_key(self):
        """Test that identical data produces identical key."""
        data1 = {"invoice_number": "INV-001", "grand_total": 100.0}
        data2 = {"invoice_number": "INV-001", "grand_total": 100.0}
        
        key1 = _generate_idempotency_key(data1)
        key2 = _generate_idempotency_key(data2)
        
        assert key1 == key2
        assert len(key1) == 32  # SHA256 truncated

    def test_different_data_produces_different_key(self):
        """Test that different data produces different key."""
        data1 = {
            "customer_name": "Customer 1",
            "customer_location": "Mumbai",
            "items": [{"name": "Item 1", "quantity": 1, "unit_price": 100}],
            "gst_calculation": {"items": [], "total_subtotal": 100, "total_gst_amount": 18, "grand_total": 118, "tax_type": "intra_state", "seller_state": "MH", "determined_gst_rate": 18, "gst_mismatch": False, "mismatch_details": []}
        }
        data2 = {
            "customer_name": "Customer 2",
            "customer_location": "Delhi",
            "items": [{"name": "Item 1", "quantity": 1, "unit_price": 100}],
            "gst_calculation": {"items": [], "total_subtotal": 100, "total_gst_amount": 18, "grand_total": 118, "tax_type": "intra_state", "seller_state": "MH", "determined_gst_rate": 18, "gst_mismatch": False, "mismatch_details": []}
        }
        
        key1 = _generate_idempotency_key(data1)
        key2 = _generate_idempotency_key(data2)
        
        assert key1 != key2


class TestHandleInvoiceGenerate:
    """Tests for handle_invoice_generate."""

    def test_invoice_generate_with_persistence(self, sample_invoice_request):
        """Test invoice generation with persistence."""
        with patch('src.handlers.invoice.persist_invoice') as mock_persist:
            from src.models.invoice import InvoiceResponse, InvoiceItem, SellerInfo, CustomerInfo, InvoiceStatus
            
            mock_response = InvoiceResponse(
                invoice_number="INV-20240115-0001",
                invoice_date="2024-01-15T10:00:00",
                status=InvoiceStatus.PENDING.value,
                seller=SellerInfo(name="Test Seller", address="123 Test St", state="MAHARASHTRA"),
                customer=CustomerInfo(name="Test Customer", location="Mumbai, MAHARASHTRA"),
                items=[
                    InvoiceItem(
                        name="Product 1", quantity=1, unit_price=100.0, subtotal=100.0,
                        gst_rate=18.0, gst_amount=18.0, cgst_rate=9.0, cgst_amount=9.0,
                        sgst_rate=9.0, sgst_amount=9.0, igst_rate=0.0, igst_amount=0.0,
                    )
                ],
                subtotal=100.0,
                total_gst_amount=18.0,
                total_cgst=9.0,
                total_sgst=9.0,
                total_igst=0.0,
                grand_total=118.0,
                tax_type="intra_state",
                seller_state="MAHARASHTRA",
                customer_state="MAHARASHTRA",
                stated_gst_rate=18.0,
                determined_gst_rate=18.0,
                gst_mismatch=False,
                mismatch_details=[],
            )
            mock_persist.return_value = mock_response
            
            event = {
                'httpMethod': 'POST',
                'body': json.dumps(sample_invoice_request),
            }
            
            response = handle_invoice_generate(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'invoiceNumber' in body
            assert body['grandTotal'] == 118.0
            assert body['status'] == 'pending'
            
            # Verify persistence was called
            mock_persist.assert_called_once()

    def test_invoice_generate_invalid_method(self, sample_invoice_request):
        """Test invoice generation with invalid HTTP method."""
        event = {
            'httpMethod': 'GET',
            'body': json.dumps(sample_invoice_request),
        }
        
        response = handle_invoice_generate(event, None)
        
        assert response['statusCode'] == 405

    def test_invoice_generate_invalid_json(self):
        """Test invoice generation with invalid JSON."""
        event = {
            'httpMethod': 'POST',
            'body': 'not valid json',
        }
        
        response = handle_invoice_generate(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'MALFORMED_JSON'

    def test_invoice_generate_missing_gst_calculation(self):
        """Test invoice generation with missing GST calculation."""
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'customer_name': 'Test',
                'items': [{'name': 'Item', 'quantity': 1, 'unit_price': 100}],
            }),
        }
        
        response = handle_invoice_generate(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'MISSING_GST_CALCULATION'

    def test_invoice_generate_persistence_failure_graceful(self, sample_invoice_request):
        """Test that persistence failure doesn't fail the request."""
        with patch('src.handlers.invoice.persist_invoice') as mock_persist:
            mock_persist.side_effect = RuntimeError("DynamoDB unavailable")
            
            event = {
                'httpMethod': 'POST',
                'body': json.dumps(sample_invoice_request),
            }
            
            response = handle_invoice_generate(event, None)
            
            # Should still succeed (graceful degradation)
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'invoiceNumber' in body
            assert body['grandTotal'] == 118.0


class TestHandleInvoiceGet:
    """Tests for handle_invoice_get."""

    def test_invoice_get_success(self):
        """Test successful invoice retrieval."""
        from src.models.invoice import InvoiceResponse, InvoiceItem, SellerInfo, CustomerInfo, InvoiceStatus
        
        mock_response = InvoiceResponse(
            invoice_number="INV-20240115-0001",
            invoice_date="2024-01-15T10:00:00",
            status=InvoiceStatus.PENDING.value,
            seller=SellerInfo(name="Seller", address="Addr", state="STATE"),
            customer=CustomerInfo(name="Customer", location="Loc"),
            items=[
                InvoiceItem(
                    name="Product 1", quantity=1, unit_price=100.0, subtotal=100.0,
                    gst_rate=18.0, gst_amount=18.0, cgst_rate=9.0, cgst_amount=9.0,
                    sgst_rate=9.0, sgst_amount=9.0, igst_rate=0.0, igst_amount=0.0,
                )
            ],
            subtotal=100.0,
            total_gst_amount=18.0,
            total_cgst=9.0,
            total_sgst=9.0,
            total_igst=0.0,
            grand_total=118.0,
            tax_type="intra_state",
            seller_state="STATE",
            customer_state="STATE",
            determined_gst_rate=18.0,
            gst_mismatch=False,
            mismatch_details=[],
        )
        
        with patch('src.handlers.invoice.retrieve_invoice', return_value=mock_response):
            event = {
                'httpMethod': 'GET',
                'pathParameters': {'invoice_id': 'INV-20240115-0001'},
            }
            
            response = handle_invoice_get(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['invoiceNumber'] == 'INV-20240115-0001'
            assert body['grandTotal'] == 118.0

    def test_invoice_get_not_found(self):
        """Test invoice retrieval for non-existent invoice."""
        with patch('src.handlers.invoice.retrieve_invoice', return_value=None):
            event = {
                'httpMethod': 'GET',
                'pathParameters': {'invoice_id': 'NONEXISTENT'},
            }
            
            response = handle_invoice_get(event, None)
            
            assert response['statusCode'] == 404
            body = json.loads(response['body'])
            assert body['code'] == 'INVOICE_NOT_FOUND'

    def test_invoice_get_missing_id(self):
        """Test invoice retrieval with missing invoice_id."""
        event = {
            'httpMethod': 'GET',
            'pathParameters': {},
        }
        
        response = handle_invoice_get(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'MISSING_INVOICE_ID'

    def test_invoice_get_invalid_method(self):
        """Test invoice retrieval with invalid HTTP method."""
        event = {
            'httpMethod': 'POST',
            'pathParameters': {'invoice_id': 'INV-001'},
        }
        
        response = handle_invoice_get(event, None)
        
        assert response['statusCode'] == 405

    def test_invoice_get_repository_error(self):
        """Test invoice retrieval with repository error."""
        with patch('src.handlers.invoice.retrieve_invoice', side_effect=Exception("DynamoDB error")):
            event = {
                'httpMethod': 'GET',
                'pathParameters': {'invoice_id': 'INV-001'},
            }
            
            response = handle_invoice_get(event, None)
            
            assert response['statusCode'] == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])