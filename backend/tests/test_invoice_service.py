"""
Tests for Invoice Service.
"""

from datetime import datetime
from decimal import Decimal
from src.services.invoice_service import (
    create_invoice_from_gst_calculation,
    validate_invoice_request,
    generate_invoice_number,
    _gst_line_item_from_gst_result,
    DEFAULT_SELLER,
)
from src.models.invoice import SellerInfo


class TestInvoiceService:
    """Tests for invoice service functions."""

    def test_generate_invoice_number_format(self):
        """Test invoice number generation format."""
        # Generate a few invoice numbers to check format
        num1 = generate_invoice_number()
        num2 = generate_invoice_number()
        
        # Should match INV-YYYYMMDD-XXXX format
        assert num1.startswith("INV-")
        assert num2.startswith("INV-")
        
        # Counter should increment
        parts1 = num1.split("-")
        parts2 = num2.split("-")
        assert len(parts1) == 3
        assert len(parts2) == 3
        assert parts1[0] == "INV"
        assert parts2[0] == "INV"
        assert len(parts1[1]) == 8  # YYYYMMDD
        assert len(parts1[2]) == 4  # XXXX

    def test_gst_line_item_from_gst_result(self):
        """Test conversion from M6 GST result to invoice item format."""
        gst_item = {
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
        
        result = _gst_line_item_from_gst_result(gst_item)
        
        assert result['name'] == 'Mouse'
        assert result['quantity'] == 10
        assert result['unit_price'] == 100.0
        assert result['subtotal'] == 1000.0
        assert result['gst_rate'] == 18.0
        assert result['gst_amount'] == 180.0
        assert result['cgst_rate'] == 9.0
        assert result['cgst_amount'] == 90.0
        assert result['sgst_rate'] == 9.0
        assert result['sgst_amount'] == 90.0
        assert result['igst_rate'] == 0.0
        assert result['igst_amount'] == 0.0
        assert result['stated_gst_rate'] == 5.0
        assert result['gst_mismatch'] is True
        assert result['tax_type'] == 'intra_state'

    def test_gst_line_item_from_gst_result_inter_state(self):
        """Test conversion for inter-state GST."""
        gst_item = {
            'name': 'Keyboard',
            'quantity': 5,
            'unit_price': 500.0,
            'subtotal': 2500.0,
            'gst_rate': 18.0,
            'gst_amount': 450.0,
            'cgst_rate': 0.0,
            'cgst_amount': 0.0,
            'sgst_rate': 0.0,
            'sgst_amount': 0.0,
            'igst_rate': 18.0,
            'igst_amount': 450.0,
            'stated_gst_rate': None,
            'gst_mismatch': False,
            'tax_type': 'inter_state',
        }
        
        result = _gst_line_item_from_gst_result(gst_item)
        
        assert result['tax_type'] == 'inter_state'
        assert result['igst_rate'] == 18.0
        assert result['cgst_rate'] == 0.0
        assert result['sgst_rate'] == 0.0


class TestValidateInvoiceRequest:
    """Tests for validate_invoice_request function."""

    def test_valid_request(self):
        """Test valid invoice request passes validation."""
        from src.services.invoice_service import validate_invoice_request
        
        request = {
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
        
        errors = validate_invoice_request(request)
        assert len(errors) == 0

    def test_missing_gst_calculation(self):
        """Test missing gst_calculation fails validation."""
        from src.services.invoice_service import validate_invoice_request
        
        request = {
            'customer_name': 'Acme Corp',
            'items': [{'name': 'Mouse', 'quantity': 10, 'unit_price': 100.0}],
        }
        
        errors = validate_invoice_request(request)
        assert len(errors) == 1
        assert "GST calculation result is required" in errors[0]

    def test_missing_items_in_gst_calculation(self):
        """Test missing items in gst_calculation fails validation."""
        from src.services.invoice_service import validate_invoice_request
        
        request = {
            'gst_calculation': {
                'total_subtotal': 1000.0,
                'total_gst_amount': 180.0,
                'grand_total': 1180.0,
                'tax_type': 'intra_state',
                'seller_state': 'MAHARASHTRA',
                'determined_gst_rate': 18.0,
            }
        }
        
        errors = validate_invoice_request(request)
        assert any("At least one item is required" in e for e in errors)

    def test_empty_items_in_gst_calculation(self):
        """Test empty items list in gst_calculation fails validation."""
        from src.services.invoice_service import validate_invoice_request
        
        request = {
            'gst_calculation': {
                'items': [],
                'total_subtotal': 1000.0,
                'total_gst_amount': 180.0,
                'grand_total': 1180.0,
                'tax_type': 'intra_state',
                'seller_state': 'MAHARASHTRA',
                'determined_gst_rate': 18.0,
            }
        }
        
        errors = validate_invoice_request(request)
        assert any("At least one item is required" in e for e in errors)

    def test_missing_item_name(self):
        """Test missing item name fails validation."""
        from src.services.invoice_service import validate_invoice_request
        
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
        
        errors = validate_invoice_request(request)
        assert any("name is required" in e for e in errors)

    def test_invalid_quantity(self):
        """Test invalid quantity fails validation."""
        from src.services.invoice_service import validate_invoice_request
        
        request = {
            'gst_calculation': {
                'items': [{'name': 'Mouse', 'quantity': 0, 'unit_price': 100.0}],
                'total_subtotal': 1000.0,
                'total_gst_amount': 180.0,
                'grand_total': 1180.0,
                'tax_type': 'intra_state',
                'seller_state': 'MAHARASHTRA',
                'determined_gst_rate': 18.0,
            }
        }
        
        errors = validate_invoice_request(request)
        assert any("quantity must be positive" in e for e in errors)

    def test_negative_unit_price(self):
        """Test negative unit price fails validation."""
        from src.services.invoice_service import validate_invoice_request
        
        request = {
            'gst_calculation': {
                'items': [{'name': 'Mouse', 'quantity': 10, 'unit_price': -100.0}],
                'total_subtotal': 1000.0,
                'total_gst_amount': 180.0,
                'grand_total': 1180.0,
                'tax_type': 'intra_state',
                'seller_state': 'MAHARASHTRA',
                'determined_gst_rate': 18.0,
            }
        }
        
        errors = validate_invoice_request(request)
        assert any("unit_price cannot be negative" in e for e in errors)