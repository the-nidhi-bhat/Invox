"""
UPI Service for INVOX.

Generates UPI payment requests with deep links and QR codes.
Honest/simulated payment status only - no real payment verification.
"""

import uuid
import base64
import io
from datetime import datetime, timedelta, timezone
from typing import Optional
from decimal import Decimal

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

from src.models.upi import (
    UPIRequest,
    UPIResponse,
    UPIStatus,
)


# Default merchant configuration for MVP
DEFAULT_MERCHANT_VPA = "invoxdemo@upi"
DEFAULT_MERCHANT_NAME = "INVOX Demo Seller"

# UPI Request ID counter (in production, use DynamoDB or similar)
_upi_request_counter = 0


def generate_upi_request_id() -> str:
    """
    Generate a deterministic, collision-resistant UPI request ID.
    
    Format: UPI-YYYYMMDD-XXXX
    Uses date + counter for uniqueness within the day.
    """
    global _upi_request_counter
    _upi_request_counter += 1
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"UPI-{date_str}-{_upi_request_counter:04d}"


def get_current_ist_datetime() -> datetime:
    """Get current datetime in IST (UTC+5:30)."""
    ist_offset = timezone(offset=timedelta(hours=5, minutes=30))
    return datetime.now(ist_offset)


def build_upi_deep_link(
    amount: float,
    merchant_vpa: str,
    merchant_name: str,
    transaction_note: Optional[str] = None,
    customer_name: Optional[str] = None,
    customer_vpa: Optional[str] = None,
    currency: str = "INR",
) -> str:
    """
    Build a UPI deep link for payment.
    
    UPI deep link format:
    upi://pay?pa=<merchant_vpa>&pn=<merchant_name>&am=<amount>&cu=<currency>&tn=<note>&cu=<currency>
    """
    from urllib.parse import quote_plus
    
    params = {
        'pa': merchant_vpa,
        'pn': merchant_name,
        'am': f"{amount:.2f}",
        'cu': currency,
    }
    
    if transaction_note:
        params['tn'] = transaction_note
    if customer_name:
        params['pn'] = customer_name  # Note: pn is used for both merchant and payer name
    if customer_vpa:
        params['pa'] = customer_vpa  # Override with payer VPA if provided
    
    # Build query string
    query_parts = [f"{k}={quote_plus(str(v))}" for k, v in params.items()]
    query_string = "&".join(query_parts)
    
    return f"upi://pay?{query_string}"


def generate_qr_code_base64(data: str) -> str:
    """
    Generate a QR code as base64 encoded PNG.
    
    Returns base64 encoded PNG data URI.
    """
    if not QRCODE_AVAILABLE:
        # Fallback: return a simple placeholder
        # In production, you'd want qrcode library installed
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{img_base64}"


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


def create_upi_payment_request(
    request: dict,
    merchant_vpa: Optional[str] = None,
    merchant_name: Optional[str] = None,
) -> dict:
    """
    Create a UPI payment request from an invoice.
    
    Args:
        request: UPIRequest with invoice info
        merchant_vpa: Optional merchant VPA (uses default if not provided)
        merchant_name: Optional merchant name (uses default if not provided)
    
    Returns:
        UPIResponse as dict
    
    Raises:
        ValueError: If required fields are missing
    """
    if not request.get('invoice_number'):
        raise ValueError("Invoice number is required for UPI payment request")
    
    if not request.get('invoice_amount') or request['invoice_amount'] <= 0:
        raise ValueError("Valid invoice amount is required")
    
    # Use defaults if not provided
    if merchant_vpa is None:
        merchant_vpa = DEFAULT_MERCHANT_VPA
    if merchant_name is None:
        merchant_name = DEFAULT_MERCHANT_NAME
    
    # Generate UPI request ID
    upi_request_id = generate_upi_request_id()
    
    # Get current time in IST
    created_at = get_current_ist_datetime()
    expires_at = created_at + timedelta(minutes=15)  # 15 minute expiry
    
    # Build transaction note
    transaction_note = request.get('transaction_note') or f"Invoice {request['invoice_number']}"
    
    # Build UPI deep link
    upi_deep_link = build_upi_deep_link(
        amount=request['invoice_amount'],
        merchant_vpa=merchant_vpa,
        merchant_name=merchant_name,
        transaction_note=transaction_note,
        customer_name=request.get('customer_name'),
        customer_vpa=request.get('customer_vpa'),
        currency=request.get('currency', 'INR'),
    )
    
    # Generate QR code
    qr_code_data = generate_qr_code_base64(upi_deep_link)
    
    # Build response
    response = UPIResponse(
        upi_request_id=generate_upi_request_id(),
        upi_deep_link=upi_deep_link,
        qr_code_data=qr_code_data,
        amount=_to_float(request['invoice_amount']),
        currency=request.get('currency', 'INR'),
        merchant_name=merchant_name,
        merchant_vpa=merchant_vpa,
        transaction_note=transaction_note,
        status=UPIStatus.PENDING.value,
        created_at=datetime.now(timezone.utc).isoformat(),
        expires_at=(datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat(),
    )
    
    return response.to_dict()


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


def validate_upi_request(data: dict) -> list[str]:
    """
    Validate UPI payment request.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    if not data.get('invoice_number'):
        errors.append("Invoice number is required")
    
    amount = data.get('invoice_amount')
    if amount is None or float(amount) <= 0:
        errors.append("Valid invoice amount is required")
    
    currency = data.get('currency', 'INR')
    if currency != 'INR':
        errors.append("Only INR currency is supported in MVP")
    
    return errors