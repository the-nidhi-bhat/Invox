"""
Tests for Invoice models.
"""

from src.models.invoice import (
    InvoiceStatus,
    TaxType,
    SellerInfo,
    CustomerInfo,
    InvoiceItem,
    InvoiceRequest,
    InvoiceResponse,
)


class TestSellerInfo:
    """Tests for SellerInfo model."""

    def test_seller_info_to_dict(self):
        """Test SellerInfo to_dict conversion."""
        seller = SellerInfo(
            name="Test Seller",
            address="123 Test St",
            state="MAHARASHTRA",
            contact="+91-9999999999",
            gstin="27AAAAA0000A1Z5",
        )
        result = seller.to_dict()
        assert result['name'] == "Test Seller"
        assert result['address'] == "123 Test St"
        assert result['state'] == "MAHARASHTRA"
        assert result['contact'] == "+91-9999999999"
        assert result['gstin'] == "27AAAAA0000A1Z5"

    def test_seller_info_optional_fields(self):
        """Test SellerInfo with optional fields as None."""
        seller = SellerInfo(
            name="Test Seller",
            address="123 Test St",
            state="MAHARASHTRA",
        )
        result = seller.to_dict()
        assert result['contact'] is None
        assert result['gstin'] is None


class TestCustomerInfo:
    """Tests for CustomerInfo model."""

    def test_customer_info_to_dict(self):
        """Test CustomerInfo to_dict conversion."""
        customer = CustomerInfo(
            name="Test Customer",
            location="PUNE",
        )
        result = customer.to_dict()
        assert result['name'] == "Test Customer"
        assert result['location'] == "PUNE"

    def test_customer_info_optional_fields(self):
        """Test CustomerInfo with optional fields as None."""
        customer = CustomerInfo()
        result = customer.to_dict()
        assert result['name'] is None
        assert result['location'] is None


class TestInvoiceItem:
    """Tests for InvoiceItem model."""

    def test_invoice_item_to_dict(self):
        """Test InvoiceItem to_dict conversion."""
        item = InvoiceItem(
            name="Mouse",
            quantity=10,
            unit_price=100.0,
            subtotal=1000.0,
            gst_rate=18.0,
            gst_amount=180.0,
            cgst_rate=9.0,
            cgst_amount=90.0,
            sgst_rate=9.0,
            sgst_amount=90.0,
            igst_rate=0.0,
            igst_amount=0.0,
            stated_gst_rate=18.0,
            gst_mismatch=False,
            tax_type="intra_state",
        )
        result = item.to_dict()
        assert result['name'] == "Mouse"
        assert result['quantity'] == 10
        assert result['unitPrice'] == 100.0
        assert result['subtotal'] == 1000.0
        assert result['gstRate'] == 18.0
        assert result['gstAmount'] == 180.0
        assert result['cgstRate'] == 9.0
        assert result['cgstAmount'] == 90.0
        assert result['sgstRate'] == 9.0
        assert result['sgstAmount'] == 90.0
        assert result['igstRate'] == 0.0
        assert result['igstAmount'] == 0.0
        assert result['statedGstRate'] == 18.0
        assert result['gstMismatch'] is False
        assert result['taxType'] == "intra_state"


class TestInvoiceStatus:
    """Tests for InvoiceStatus enum."""

    def test_invoice_status_values(self):
        """Test InvoiceStatus enum values."""
        assert InvoiceStatus.PENDING.value == "pending"
        assert InvoiceStatus.PAID.value == "paid"
        assert InvoiceStatus.CANCELLED.value == "cancelled"


class TestTaxType:
    """Tests for TaxType enum."""

    def test_tax_type_values(self):
        """Test TaxType enum values."""
        assert TaxType.INTRA_STATE.value == "intra_state"
        assert TaxType.INTER_STATE.value == "inter_state"