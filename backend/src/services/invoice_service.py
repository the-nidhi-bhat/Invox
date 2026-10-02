"""
Invoice Service for INVOX.

Handles invoice generation using M6 GST calculation results.
Does NOT recalculate GST - uses authoritative M6 calculation.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from decimal import Decimal

from src.models.invoice import (
    InvoiceRequest,
    InvoiceResponse,
    InvoiceItem,
    SellerInfo,
    CustomerInfo,
    InvoiceStatus,
    TaxType,
)
from src.services.gst_engine import (
    calculate_gst,
    create_default_config,
    GSTLineItem,
)


# Default seller configuration for MVP
DEFAULT_SELLER = SellerInfo(
    name="INVOX Demo Seller",
    address="123 Business Street, Mumbai",
    state="MAHARASHTRA",
    contact="+91-9876543210",
    gstin="Demo / Not configured",
)

# Invoice number counter (in production, use DynamoDB or similar)
_invoice_counter = 0


def generate_invoice_number() -> str:
    """
    Generate a deterministic, collision-resistant invoice number.
    
    Format: INV-YYYYMMDD-XXXX
    Uses date + counter for uniqueness within the day.
    """
    global _invoice_counter
    _invoice_counter += 1
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"INV-{date_str}-{_invoice_counter:04d}"


def get_current_ist_datetime() -> datetime:
    """Get current datetime in IST (UTC+5:30)."""
    # IST is UTC+5:30
    ist_offset = timezone(offset=timedelta(hours=5, minutes=30))
    return datetime.now(ist_offset)


def _gst_line_item_from_gst_result(item: dict) -> dict:
    """Convert M6 GST calculation item to invoice item format."""
    return {
        'name': item['name'],
        'quantity': item['quantity'],
        'unit_price': item['unit_price'],
        'subtotal': item['subtotal'],
        'gst_rate': item['gst_rate'],
        'gst_amount': item['gst_amount'],
        'cgst_rate': item['cgst_rate'],
        'cgst_amount': item['cgst_amount'],
        'sgst_rate': item['sgst_rate'],
        'sgst_amount': item['sgst_amount'],
        'igst_rate': item['igst_rate'],
        'igst_amount': item['igst_amount'],
        'stated_gst_rate': item.get('stated_gst_rate'),
        'gst_mismatch': item.get('gst_mismatch', False),
        'tax_type': item['tax_type'],
    }


def _to_float(value) -> float:
    """Safely convert value to float."""
    if value is None:
        return 0.0
    return float(value)


def _to_optional_float(value) -> Optional[float]:
    """Safely convert value to optional float."""
    if value is None:
        return None
    return float(value)


def create_invoice_from_gst_calculation(
    request: dict,
    seller: Optional[SellerInfo] = None,
) -> dict:
    """
    Create an invoice from M6 GST calculation result.
    
    This function:
    1. Validates the M6 GST calculation result exists
    2. Uses the authoritative M6 calculation (does NOT recalculate)
    3. Generates invoice with proper formatting
    4. Returns structured invoice response
    
    Args:
        request: InvoiceRequest with gst_calculation from M6
        seller: Optional seller info (uses default if not provided)
    
    Returns:
        InvoiceResponse as dict
    
    Raises:
        ValueError: If gst_calculation is missing or invalid
    """
    if not request.get('gst_calculation'):
        raise ValueError("GST calculation result is required for invoice generation")
    
    gst_calc = request['gst_calculation']
    
    # Validate required fields from M6 calculation
    required_fields = [
        'items', 'total_subtotal', 'total_gst_amount', 
        'grand_total', 'tax_type', 'seller_state',
        'determined_gst_rate', 'gst_mismatch', 'mismatch_details'
    ]
    for field in required_fields:
        if field not in gst_calc:
            raise ValueError(f"Missing required field in GST calculation: {field}")
    
    # Use default seller if not provided
    if seller is None:
        seller = DEFAULT_SELLER
    
    # Generate invoice number
    invoice_number = generate_invoice_number()
    
    # Generate invoice date (IST)
    invoice_date = get_current_ist_datetime().isoformat()
    
    # Build customer info from request
    customer = CustomerInfo(
        name=request.get('customer_name'),
        location=request.get('customer_location'),
    )
    
    # Build items from M6 calculation result (authoritative)
    invoice_items = []
    for item in gst_calc['items']:
        invoice_item = InvoiceItem(
            name=item['name'],
            quantity=item['quantity'],
            unit_price=item['unit_price'],
            subtotal=item['subtotal'],
            gst_rate=item['gst_rate'],
            gst_amount=item['gst_amount'],
            cgst_rate=item['cgst_rate'],
            cgst_amount=item['cgst_amount'],
            sgst_rate=item['sgst_rate'],
            sgst_amount=item['sgst_amount'],
            igst_rate=item['igst_rate'],
            igst_amount=item['igst_amount'],
            stated_gst_rate=item.get('stated_gst_rate'),
            gst_mismatch=item.get('gst_mismatch', False),
            tax_type=item['tax_type'],
        )
        invoice_items.append(invoice_item)
    
    # Determine tax type
    tax_type = gst_calc['tax_type']
    if tax_type not in ['intra_state', 'inter_state']:
        tax_type = 'intra_state'
    
    # Build response
    response = InvoiceResponse(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        status=InvoiceStatus.PENDING.value,
        seller=seller,
        customer=customer,
        items=invoice_items,
        subtotal=_to_float(gst_calc.get('total_subtotal')),
        total_gst_amount=_to_float(gst_calc.get('total_gst_amount')),
        total_cgst=_to_float(gst_calc.get('total_cgst', 0)),
        total_sgst=_to_float(gst_calc.get('total_sgst', 0)),
        total_igst=_to_float(gst_calc.get('total_igst', 0)),
        grand_total=_to_float(gst_calc.get('grand_total')),
        tax_type=tax_type,
        seller_state=gst_calc.get('seller_state', ''),
        customer_state=gst_calc.get('customer_state'),
        stated_gst_rate=_to_optional_float(gst_calc.get('stated_gst_rate')),
        determined_gst_rate=_to_float(gst_calc.get('determined_gst_rate')),
        gst_mismatch=gst_calc.get('gst_mismatch', False),
        mismatch_details=gst_calc.get('mismatch_details', []),
    )
    
    return response.to_dict()


def validate_invoice_request(request: dict) -> List[str]:
    """
    Validate invoice generation request.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    if not request.get('gst_calculation'):
        errors.append("GST calculation result is required")
        return errors
    
    gst_calc = request.get('gst_calculation', {})
    
    if not gst_calc.get('items') or len(gst_calc['items']) == 0:
        errors.append("At least one item is required")
    
    required_fields = [
        'total_subtotal', 'total_gst_amount', 'grand_total',
        'tax_type', 'seller_state', 'determined_gst_rate'
    ]
    for field in required_fields:
        if field not in gst_calc:
            errors.append(f"Missing required GST calculation field: {field}")
    
    # Validate items
    items = gst_calc.get('items', [])
    if not isinstance(items, list):
        errors.append("Items must be a list")
    else:
        for idx, item in enumerate(items):
            if not item.get('name'):
                errors.append(f"Item {idx}: name is required")
            if item.get('quantity', 0) <= 0:
                errors.append(f"Item {idx}: quantity must be positive")
            if item.get('unit_price', 0) < 0:
                errors.append(f"Item {idx}: unit_price cannot be negative")
            if 'stated_gst_rate' in item and item['stated_gst_rate'] is not None:
                gst_rate = item['stated_gst_rate']
                if not isinstance(gst_rate, (int, float)):
                    errors.append(f"Item {idx}: stated_gst_rate must be a number")
                elif gst_rate < 0 or gst_rate > 100:
                    errors.append(f"Item {idx}: stated_gst_rate must be between 0 and 100")
    
    return errors