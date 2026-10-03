"""
Tests for DynamoDB Persistence Models.

Tests the PersistedInvoice and related model classes.
"""

import pytest
from datetime import datetime

from src.models.persistence import (
    InvoiceStatus,
    PersistedInvoiceItem,
    PersistedSellerInfo,
    PersistedCustomerInfo,
    PersistedUPIInfo,
    PersistedInvoice,
)


class TestPersistedInvoiceItem:
    """Tests for PersistedInvoiceItem model."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        item = PersistedInvoiceItem(
            name="Test Product",
            quantity=2,
            unit_price=100.0,
            subtotal=200.0,
            gst_rate=18.0,
            gst_amount=36.0,
            cgst_rate=9.0,
            cgst_amount=18.0,
            sgst_rate=9.0,
            sgst_amount=18.0,
            igst_rate=0.0,
            igst_amount=0.0,
            stated_gst_rate=18.0,
            gst_mismatch=False,
            tax_type="intra_state",
        )
        d = item.to_dict()
        assert d['name'] == "Test Product"
        assert d['quantity'] == 2
        assert d['unit_price'] == 100.0
        assert d['tax_type'] == "intra_state"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'name': 'Test Product',
            'quantity': 2,
            'unit_price': 100.0,
            'subtotal': 200.0,
            'gst_rate': 18.0,
            'gst_amount': 36.0,
            'cgst_rate': 9.0,
            'cgst_amount': 18.0,
            'sgst_rate': 9.0,
            'sgst_amount': 18.0,
            'igst_rate': 0.0,
            'igst_amount': 0.0,
            'stated_gst_rate': 18.0,
            'gst_mismatch': False,
            'tax_type': 'intra_state',
        }
        item = PersistedInvoiceItem.from_dict(data)
        assert item.name == "Test Product"
        assert item.quantity == 2
        assert item.unit_price == 100.0
        assert item.tax_type == "intra_state"

    def test_from_dict_with_missing_optional(self):
        """Test creation from dictionary with missing optional fields."""
        data = {
            'name': 'Test Product',
            'quantity': 2,
            'unit_price': 100.0,
            'subtotal': 200.0,
            'gst_rate': 18.0,
            'gst_amount': 36.0,
        }
        item = PersistedInvoiceItem.from_dict(data)
        assert item.name == "Test Product"
        assert item.cgst_rate == 0.0  # default
        assert item.stated_gst_rate is None  # default
        assert item.gst_mismatch is False  # default


class TestPersistedSellerInfo:
    """Tests for PersistedSellerInfo model."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        seller = PersistedSellerInfo(
            name="Test Seller",
            address="123 Test St",
            state="MAHARASHTRA",
            contact="+91-9876543210",
            gstin="27ABCDE1234F1Z5",
        )
        d = seller.to_dict()
        assert d['name'] == "Test Seller"
        assert d['state'] == "MAHARASHTRA"
        assert d['gstin'] == "27ABCDE1234F1Z5"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'name': 'Test Seller',
            'address': '123 Test St',
            'state': 'MAHARASHTRA',
            'contact': '+91-9876543210',
            'gstin': '27ABCDE1234F1Z5',
        }
        seller = PersistedSellerInfo.from_dict(data)
        assert seller.name == "Test Seller"
        assert seller.gstin == "27ABCDE1234F1Z5"


class TestPersistedCustomerInfo:
    """Tests for PersistedCustomerInfo model."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        customer = PersistedCustomerInfo(
            name="Test Customer",
            location="Mumbai, MAHARASHTRA",
        )
        d = customer.to_dict()
        assert d['name'] == "Test Customer"
        assert d['location'] == "Mumbai, MAHARASHTRA"

    def test_from_dict_with_none(self):
        """Test creation from dictionary with None values."""
        data = {'name': None, 'location': None}
        customer = PersistedCustomerInfo.from_dict(data)
        assert customer.name is None
        assert customer.location is None


class TestPersistedUPIInfo:
    """Tests for PersistedUPIInfo model."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        upi = PersistedUPIInfo(
            upi_request_id="UPI-20240115-0001",
            upi_deep_link="upi://pay?pa=merchant@upi&am=100.00",
            qr_code_data="data:image/png;base64,test",
            amount=100.0,
            currency="INR",
            merchant_name="Test Merchant",
            merchant_vpa="merchant@upi",
            transaction_note="Invoice INV-20240115-0001",
            status="pending",
            created_at="2024-01-15T10:00:00",
            expires_at="2024-01-15T10:15:00",
        )
        d = upi.to_dict()
        assert d['upi_request_id'] == "UPI-20240115-0001"
        assert d['amount'] == 100.0
        assert d['status'] == "pending"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'upi_request_id': 'UPI-20240115-0001',
            'upi_deep_link': 'upi://pay?pa=merchant@upi&am=100.00',
            'qr_code_data': 'data:image/png;base64,test',
            'amount': 100.0,
            'currency': 'INR',
            'merchant_name': 'Test Merchant',
            'merchant_vpa': 'merchant@upi',
            'transaction_note': 'Invoice INV-20240115-0001',
            'status': 'pending',
            'created_at': '2024-01-15T10:00:00',
            'expires_at': '2024-01-15T10:15:00',
        }
        upi = PersistedUPIInfo.from_dict(data)
        assert upi.upi_request_id == "UPI-20240115-0001"
        assert upi.amount == 100.0


class TestPersistedInvoice:
    """Tests for PersistedInvoice model."""

    def _create_sample_invoice(self) -> PersistedInvoice:
        """Create a sample invoice for testing."""
        return PersistedInvoice(
            invoice_id="INV-20240115-0001",
            invoice_number="INV-20240115-0001",
            invoice_date="2024-01-15T10:00:00",
            status=InvoiceStatus.PENDING.value,
            seller=PersistedSellerInfo(
                name="Test Seller",
                address="123 Test St",
                state="MAHARASHTRA",
            ),
            customer=PersistedCustomerInfo(
                name="Test Customer",
                location="Mumbai, MAHARASHTRA",
            ),
            items=[
                PersistedInvoiceItem(
                    name="Product 1",
                    quantity=1,
                    unit_price=100.0,
                    subtotal=100.0,
                    gst_rate=18.0,
                    gst_amount=18.0,
                    cgst_rate=9.0,
                    cgst_amount=9.0,
                    sgst_rate=9.0,
                    sgst_amount=9.0,
                    igst_rate=0.0,
                    igst_amount=0.0,
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

    def test_to_dynamodb_item(self):
        """Test conversion to DynamoDB item format."""
        invoice = self._create_sample_invoice()
        item = invoice.to_dynamodb_item()
        
        # Check primary key
        assert 'invoice_id' in item
        assert item['invoice_id']['S'] == "INV-20240115-0001"
        
        # Check required fields
        assert item['invoice_number']['S'] == "INV-20240115-0001"
        assert item['status']['S'] == "pending"
        assert item['grand_total']['N'] == "118.0"
        assert item['tax_type']['S'] == "intra_state"
        
        # Check nested objects
        assert 'seller' in item
        assert item['seller']['M']['name']['S'] == "Test Seller"
        
        assert 'customer' in item
        assert item['customer']['M']['name']['S'] == "Test Customer"
        
        # Check items list
        assert 'items' in item
        assert item['items']['L'][0]['M']['name']['S'] == "Product 1"

    def test_from_dynamodb_item(self):
        """Test creation from DynamoDB item format."""
        invoice = self._create_sample_invoice()
        dynamodb_item = invoice.to_dynamodb_item()
        
        restored = PersistedInvoice.from_dynamodb_item(dynamodb_item)
        
        assert restored.invoice_id == invoice.invoice_id
        assert restored.invoice_number == invoice.invoice_number
        assert restored.status == invoice.status
        assert restored.grand_total == invoice.grand_total
        assert restored.tax_type == invoice.tax_type
        assert restored.seller.name == invoice.seller.name
        assert restored.customer.name == invoice.customer.name
        assert len(restored.items) == 1
        assert restored.items[0].name == "Product 1"

    def test_to_response_dict(self):
        """Test conversion to API response format."""
        invoice = self._create_sample_invoice()
        response = invoice.to_response_dict()
        
        assert response['invoiceNumber'] == "INV-20240115-0001"
        assert response['status'] == "pending"
        assert response['grandTotal'] == 118.0
        assert response['taxType'] == "intra_state"
        assert response['seller']['name'] == "Test Seller"
        assert response['customer']['name'] == "Test Customer"
        assert len(response['items']) == 1
        assert 'createdAt' in response
        assert 'updatedAt' in response

    def test_to_response_dict_with_upi(self):
        """Test conversion to API response format with UPI info."""
        invoice = self._create_sample_invoice()
        invoice.upi_info = PersistedUPIInfo(
            upi_request_id="UPI-20240115-0001",
            upi_deep_link="upi://pay?pa=merchant@upi&am=118.00",
            qr_code_data="data:image/png;base64,test",
            amount=118.0,
            currency="INR",
            merchant_name="Test Merchant",
            merchant_vpa="merchant@upi",
            transaction_note="Invoice INV-20240115-0001",
            status="pending",
            created_at="2024-01-15T10:00:00",
            expires_at="2024-01-15T10:15:00",
        )
        response = invoice.to_response_dict()
        
        assert 'upiInfo' in response
        assert response['upiInfo']['upi_request_id'] == "UPI-20240115-0001"
        assert response['upiInfo']['amount'] == 118.0


class TestInvoiceStatus:
    """Tests for InvoiceStatus enum."""

    def test_values(self):
        """Test enum values."""
        assert InvoiceStatus.PENDING == "pending"
        assert InvoiceStatus.PAID == "paid"
        assert InvoiceStatus.CANCELLED == "cancelled"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])