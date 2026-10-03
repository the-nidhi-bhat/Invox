"""
Tests for Invoice Persistence Service.

Tests the persistence service functions with mocked repository.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.models.invoice import (
    InvoiceResponse,
    InvoiceItem,
    SellerInfo,
    CustomerInfo,
    InvoiceStatus,
)
from src.models.persistence import (
    PersistedInvoice,
    PersistedInvoiceItem,
    PersistedSellerInfo,
    PersistedCustomerInfo,
    InvoiceStatus as PersistedInvoiceStatus,
)
from src.services.persistence_service import (
    persist_invoice,
    retrieve_invoice,
    retrieve_invoice_by_number,
    update_invoice_payment_status,
    add_upi_payment_info,
    get_repository,
    set_repository,
    reset_repository,
)
from src.services.dynamodb_repository import InvoiceRepository


class MockRepository:
    """Mock repository for testing."""
    
    def __init__(self):
        self.invoices = {}
        self.upi_infos = {}
    
    def save_invoice(self, invoice):
        self.invoices[invoice.invoice_id] = invoice
        return invoice
    
    def get_invoice(self, invoice_id):
        return self.invoices.get(invoice_id)
    
    def get_invoice_by_number(self, invoice_number):
        for inv in self.invoices.values():
            if inv.invoice_number == invoice_number:
                return inv
        return None
    
    def update_invoice_status(self, invoice_id, status):
        if invoice_id in self.invoices:
            self.invoices[invoice_id].status = status
            self.invoices[invoice_id].updated_at = datetime.utcnow().isoformat()
            return self.invoices[invoice_id]
        return None
    
    def add_upi_info(self, invoice_id, upi_info):
        if invoice_id in self.invoices:
            self.invoices[invoice_id].upi_info = upi_info
            self.invoices[invoice_id].updated_at = datetime.utcnow().isoformat()
            return self.invoices[invoice_id]
        return None


@pytest.fixture
def mock_repo():
    """Create a mock repository."""
    return MockRepository()


@pytest.fixture
def sample_invoice_response():
    """Create a sample InvoiceResponse."""
    return InvoiceResponse(
        invoice_number="INV-20240115-0001",
        invoice_date="2024-01-15T10:00:00",
        status=InvoiceStatus.PENDING.value,
        seller=SellerInfo(
            name="Test Seller",
            address="123 Test St",
            state="MAHARASHTRA",
        ),
        customer=CustomerInfo(
            name="Test Customer",
            location="Mumbai, MAHARASHTRA",
        ),
        items=[
            InvoiceItem(
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
        stated_gst_rate=18.0,
        determined_gst_rate=18.0,
        gst_mismatch=False,
        mismatch_details=[],
    )


class TestPersistInvoice:
    """Tests for persist_invoice function."""

    def test_persist_invoice_success(self, mock_repo, sample_invoice_response):
        """Test successful invoice persistence."""
        result = persist_invoice(sample_invoice_response, repository=mock_repo)
        
        assert result.invoice_number == sample_invoice_response.invoice_number
        assert result.grand_total == sample_invoice_response.grand_total
        assert result.created_at is not None
        assert result.updated_at is not None
        
        # Verify it was stored in repository
        stored = mock_repo.get_invoice(sample_invoice_response.invoice_number)
        assert stored is not None
        assert stored.grand_total == 118.0

    def test_persist_invoice_with_idempotency_key(self, mock_repo, sample_invoice_response):
        """Test persistence with idempotency key."""
        idempotency_key = "test-key-123"
        result = persist_invoice(sample_invoice_response, idempotency_key=idempotency_key, repository=mock_repo)
        
        assert result.invoice_number == sample_invoice_response.invoice_number
        stored = mock_repo.get_invoice(sample_invoice_response.invoice_number)
        assert stored.idempotency_key == idempotency_key

    def test_persist_invoice_preserves_gst_totals(self, mock_repo, sample_invoice_response):
        """Test that GST totals are preserved exactly."""
        result = persist_invoice(sample_invoice_response, repository=mock_repo)
        
        assert result.total_gst_amount == 18.0
        assert result.total_cgst == 9.0
        assert result.total_sgst == 9.0
        assert result.total_igst == 0.0
        assert result.grand_total == 118.0
        assert result.determined_gst_rate == 18.0
        assert result.gst_mismatch is False

    def test_persist_invoice_preserves_customer_data(self, mock_repo, sample_invoice_response):
        """Test that customer data is preserved."""
        result = persist_invoice(sample_invoice_response, repository=mock_repo)
        
        assert result.customer.name == "Test Customer"
        assert result.customer.location == "Mumbai, MAHARASHTRA"
        assert result.seller.name == "Test Seller"

    def test_persist_invoice_multiple_items(self, mock_repo):
        """Test persistence with multiple line items."""
        invoice = InvoiceResponse(
            invoice_number="INV-20240115-0002",
            invoice_date="2024-01-15T10:00:00",
            status=InvoiceStatus.PENDING.value,
            seller=SellerInfo(name="Seller", address="Addr", state="STATE"),
            customer=CustomerInfo(name="Customer", location="Loc"),
            items=[
                InvoiceItem(
                    name="Item 1", quantity=1, unit_price=100.0, subtotal=100.0,
                    gst_rate=18.0, gst_amount=18.0, cgst_rate=9.0, cgst_amount=9.0,
                    sgst_rate=9.0, sgst_amount=9.0, igst_rate=0.0, igst_amount=0.0,
                ),
                InvoiceItem(
                    name="Item 2", quantity=2, unit_price=50.0, subtotal=100.0,
                    gst_rate=12.0, gst_amount=12.0, cgst_rate=6.0, cgst_amount=6.0,
                    sgst_rate=6.0, sgst_amount=6.0, igst_rate=0.0, igst_amount=0.0,
                ),
            ],
            subtotal=200.0,
            total_gst_amount=30.0,
            total_cgst=15.0,
            total_sgst=15.0,
            total_igst=0.0,
            grand_total=230.0,
            tax_type="intra_state",
            seller_state="STATE",
            customer_state="STATE",
            determined_gst_rate=15.0,
            gst_mismatch=False,
            mismatch_details=[],
        )
        
        result = persist_invoice(invoice, repository=mock_repo)
        
        assert len(result.items) == 2
        assert result.items[0].name == "Item 1"
        assert result.items[1].name == "Item 2"
        assert result.grand_total == 230.0


class TestRetrieveInvoice:
    """Tests for retrieve_invoice function."""

    def test_retrieve_invoice_success(self, mock_repo, sample_invoice_response):
        """Test successful invoice retrieval."""
        # First persist
        persist_invoice(sample_invoice_response, repository=mock_repo)
        
        # Then retrieve
        result = retrieve_invoice(sample_invoice_response.invoice_number, repository=mock_repo)
        
        assert result is not None
        assert result.invoice_number == sample_invoice_response.invoice_number
        assert result.grand_total == sample_invoice_response.grand_total

    def test_retrieve_invoice_not_found(self, mock_repo):
        """Test retrieval of non-existent invoice."""
        result = retrieve_invoice("NONEXISTENT", repository=mock_repo)
        assert result is None

    def test_retrieve_invoice_by_number(self, mock_repo, sample_invoice_response):
        """Test retrieval by invoice number."""
        persist_invoice(sample_invoice_response, repository=mock_repo)
        
        result = retrieve_invoice_by_number(sample_invoice_response.invoice_number, repository=mock_repo)
        
        assert result is not None
        assert result.invoice_number == sample_invoice_response.invoice_number


class TestUpdateInvoicePaymentStatus:
    """Tests for update_invoice_payment_status function."""

    def test_update_status_to_paid(self, mock_repo, sample_invoice_response):
        """Test updating invoice status to paid."""
        persist_invoice(sample_invoice_response, repository=mock_repo)
        
        result = update_invoice_payment_status(
            sample_invoice_response.invoice_number,
            "paid",
            repository=mock_repo
        )
        
        assert result is not None
        assert result.status == "paid"

    def test_update_status_not_found(self, mock_repo):
        """Test updating status of non-existent invoice."""
        result = update_invoice_payment_status("NONEXISTENT", "paid", repository=mock_repo)
        assert result is None


class TestAddUPIPaymentInfo:
    """Tests for add_upi_payment_info function."""

    def test_add_upi_info(self, mock_repo, sample_invoice_response):
        """Test adding UPI payment info to invoice."""
        persist_invoice(sample_invoice_response, repository=mock_repo)
        
        upi_info = {
            'upi_request_id': 'UPI-20240115-0001',
            'upi_deep_link': 'upi://pay?pa=merchant@upi&am=118.00',
            'qr_code_data': 'data:image/png;base64,test',
            'amount': 118.0,
            'currency': 'INR',
            'merchant_name': 'Test Merchant',
            'merchant_vpa': 'merchant@upi',
            'transaction_note': 'Invoice INV-20240115-0001',
            'status': 'pending',
            'created_at': '2024-01-15T10:00:00',
            'expires_at': '2024-01-15T10:15:00',
        }
        
        result = add_upi_payment_info(
            sample_invoice_response.invoice_number,
            upi_info,
            repository=mock_repo
        )
        
        assert result is not None
        assert result.upi_info is not None
        assert result.upi_info['upi_request_id'] == 'UPI-20240115-0001'
        assert result.upi_info['amount'] == 118.0

    def test_add_upi_info_not_found(self, mock_repo):
        """Test adding UPI info to non-existent invoice."""
        upi_info = {'upi_request_id': 'UPI-001', 'amount': 100.0}
        result = add_upi_payment_info("NONEXISTENT", upi_info, repository=mock_repo)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])