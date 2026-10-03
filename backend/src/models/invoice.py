"""
Invoice Models for INVOX.

Defines the request/response contracts for invoice generation.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice status."""
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class TaxType(str, Enum):
    """Type of tax applicable based on jurisdiction."""
    INTRA_STATE = "intra_state"  # CGST + SGST
    INTER_STATE = "inter_state"  # IGST


@dataclass
class SellerInfo:
    """Seller/business information."""
    name: str
    address: str
    state: str
    contact: Optional[str] = None
    gstin: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'address': self.address,
            'state': self.state,
            'contact': self.contact,
            'gstin': self.gstin,
        }


@dataclass
class CustomerInfo:
    """Customer information."""
    name: Optional[str] = None
    location: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'location': self.location,
        }


@dataclass
class InvoiceItem:
    """Invoice line item with GST breakdown."""
    name: str
    quantity: int
    unit_price: float
    subtotal: float
    gst_rate: float
    gst_amount: float
    cgst_rate: float
    cgst_amount: float
    sgst_rate: float
    sgst_amount: float
    igst_rate: float
    igst_amount: float
    stated_gst_rate: Optional[float] = None
    gst_mismatch: bool = False
    tax_type: str = "intra_state"

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'quantity': self.quantity,
            'unitPrice': self.unit_price,
            'subtotal': self.subtotal,
            'gstRate': self.gst_rate,
            'gstAmount': self.gst_amount,
            'cgstRate': self.cgst_rate,
            'cgstAmount': self.cgst_amount,
            'sgstRate': self.sgst_rate,
            'sgstAmount': self.sgst_amount,
            'igstRate': self.igst_rate,
            'igstAmount': self.igst_amount,
            'statedGstRate': self.stated_gst_rate,
            'gstMismatch': self.gst_mismatch,
            'taxType': self.tax_type,
        }


@dataclass
class InvoiceRequest:
    """Request payload for POST /invoice/generate endpoint."""
    # The confirmed order from M5 review
    customer_name: Optional[str] = None
    customer_location: Optional[str] = None
    items: List[dict] = field(default_factory=list)
    stated_gst_rate: Optional[float] = None
    # M6 GST calculation result
    gst_calculation: Optional[dict] = None


@dataclass
class InvoiceResponse:
    """Response for POST /invoice/generate endpoint."""
    invoice_number: str
    invoice_date: str  # ISO format
    status: str  # InvoiceStatus.PENDING
    seller: SellerInfo
    customer: CustomerInfo
    items: List[InvoiceItem]
    subtotal: float
    total_gst_amount: float
    total_cgst: float
    total_sgst: float
    total_igst: float
    grand_total: float
    tax_type: str
    seller_state: str
    customer_state: Optional[str]
    stated_gst_rate: Optional[float] = None
    determined_gst_rate: float = 0.0
    gst_mismatch: bool = False
    mismatch_details: List[str] = field(default_factory=list)
    # Persistence timestamps (added by M9)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # UPI payment info (optional)
    upi_info: Optional[dict] = None

    def to_dict(self) -> dict:
        result = {
            'invoiceNumber': self.invoice_number,
            'invoiceDate': self.invoice_date,
            'status': self.status,
            'seller': self.seller.to_dict(),
            'customer': self.customer.to_dict(),
            'items': [item.to_dict() for item in self.items],
            'totalSubtotal': self.subtotal,
            'totalGstAmount': self.total_gst_amount,
            'totalCgst': self.total_cgst,
            'totalSgst': self.total_sgst,
            'totalIgst': self.total_igst,
            'grandTotal': self.grand_total,
            'taxType': self.tax_type,
            'sellerState': self.seller_state,
            'customerState': self.customer_state,
            'statedGstRate': self.stated_gst_rate,
            'determinedGstRate': self.determined_gst_rate,
            'gstMismatch': self.gst_mismatch,
            'mismatchDetails': self.mismatch_details,
        }
        if self.created_at:
            result['createdAt'] = self.created_at
        if self.updated_at:
            result['updatedAt'] = self.updated_at
        if self.upi_info:
            result['upiInfo'] = self.upi_info
        return result


# Export for convenience
__all__ = [
    'InvoiceStatus',
    'TaxType',
    'SellerInfo',
    'CustomerInfo',
    'InvoiceItem',
    'InvoiceRequest',
    'InvoiceResponse',
]