"""
Tests for UPI Handler (M9 persistence integration).

Tests the POST /upi/generate endpoint with invoice persistence.
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch

from src.handlers.upi import handle_upi_generate
from src.services.persistence_service import reset_repository


class MockRepository:
    """Mock repository for testing UPI handler."""
    
    def __init__(self):
        self.invoices = {}
        self.add_upi_called = False
    
    def get_invoice(self, invoice_id):
        return self.invoices.get(invoice_id)
    
    def add_upi_info(self, invoice_id, upi_info):
        self.add_upi_called = True
        if invoice_id in self.invoices:
            self.invoices[invoice_id].upi_info = upi_info
            return self.invoices[invoice_id]
        return None


@pytest.fixture(autouse=True)
def reset_repo():
    """Reset repository before each test."""
    reset_repository()
    yield
    reset_repository()


@pytest.fixture
def mock_repo():
    """Create a mock repository with a sample invoice."""
    repo = MockRepository()
    
    # Add a sample invoice
    from src.models.persistence import (
        PersistedInvoice, PersistedInvoiceItem, PersistedSellerInfo,
        PersistedCustomerInfo, InvoiceStatus
    )
    
    invoice = PersistedInvoice(
        invoice_id="INV-20240115-0001",
        invoice_number="INV-20240115-0001",
        invoice_date="2024-01-15T10:00:00",
        status=InvoiceStatus.PENDING.value,
        seller=PersistedSellerInfo(name="Seller", address="Addr", state="MAHARASHTRA"),
        customer=PersistedCustomerInfo(name="Customer", location="Mumbai"),
        items=[
            PersistedInvoiceItem(
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
        determined_gst_rate=18.0,
    )
    repo.invoices["INV-20240115-0001"] = invoice
    
    return repo


@pytest.fixture
def sample_upi_request():
    """Create a sample UPI generation request."""
    return {
        "invoice_number": "INV-20240115-0001",
        "invoice_amount": 118.0,
        "customer_name": "Test Customer",
        "currency": "INR",
    }


class TestHandleUpiGenerate:
    """Tests for handle_upi_generate."""

    def test_upi_generate_with_persistence(self, mock_repo, sample_upi_request):
        """Test UPI generation with persistence to invoice."""
        with patch('src.handlers.upi.retrieve_invoice', return_value=Mock(invoice_number="INV-20240115-0001")):
            with patch('src.handlers.upi.add_upi_payment_info') as mock_add_upi:
                event = {
                    'httpMethod': 'POST',
                    'body': json.dumps(sample_upi_request),
                }
                
                response = handle_upi_generate(event, None)
                
                assert response['statusCode'] == 200
                body = json.loads(response['body'])
                assert 'upiRequestId' in body
                assert body['amount'] == 118.0
                assert body['status'] == 'pending'
                assert 'upiDeepLink' in body
                assert 'qrCodeData' in body
                
                # Verify UPI info was added to invoice
                mock_add_upi.assert_called_once()

    def test_upi_generate_invalid_method(self, sample_upi_request):
        """Test UPI generation with invalid HTTP method."""
        event = {
            'httpMethod': 'GET',
            'body': json.dumps(sample_upi_request),
        }
        
        response = handle_upi_generate(event, None)
        
        assert response['statusCode'] == 405

    def test_upi_generate_invalid_json(self):
        """Test UPI generation with invalid JSON."""
        event = {
            'httpMethod': 'POST',
            'body': 'not valid json',
        }
        
        response = handle_upi_generate(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'MALFORMED_JSON'

    def test_upi_generate_missing_invoice_number(self):
        """Test UPI generation with missing invoice number."""
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'invoice_amount': 100.0,
            }),
        }
        
        response = handle_upi_generate(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_INPUT'

    def test_upi_generate_invalid_amount(self):
        """Test UPI generation with invalid amount."""
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'invoice_number': 'INV-001',
                'invoice_amount': -10.0,
            }),
        }
        
        response = handle_upi_generate(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['code'] == 'INVALID_INPUT'

    def test_upi_generate_invoice_not_found(self, sample_upi_request):
        """Test UPI generation for non-existent invoice (should still succeed)."""
        request = sample_upi_request.copy()
        request['invoice_number'] = 'NONEXISTENT'
        
        with patch('src.handlers.upi.retrieve_invoice', return_value=None):
            event = {
                'httpMethod': 'POST',
                'body': json.dumps(request),
            }
            
            # Should still succeed - UPI generation doesn't require invoice to exist
            response = handle_upi_generate(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'upiRequestId' in body

    def test_upi_generate_persistence_failure_graceful(self, sample_upi_request):
        """Test that UPI persistence failure doesn't fail the request."""
        with patch('src.handlers.upi.retrieve_invoice', return_value=Mock(invoice_number="INV-20240115-0001")):
            with patch('src.handlers.upi.add_upi_payment_info', side_effect=Exception("DynamoDB error")):
                event = {
                    'httpMethod': 'POST',
                    'body': json.dumps(sample_upi_request),
                }
                
                response = handle_upi_generate(event, None)
                
                # Should still succeed (graceful degradation)
                assert response['statusCode'] == 200
                body = json.loads(response['body'])
                assert 'upiRequestId' in body


if __name__ == "__main__":
    pytest.main([__file__, "-v"])