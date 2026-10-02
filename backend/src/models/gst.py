"""
GST Calculation Models for INVOX.

Defines the request/response contracts for GST calculation.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from enum import Enum


class TaxType(str, Enum):
    """Type of tax applicable based on jurisdiction."""
    INTRA_STATE = "intra_state"  # CGST + SGST
    INTER_STATE = "inter_state"  # IGST


@dataclass
class GSTCalculationItemRequest:
    """Input item for GST calculation request."""
    name: str
    quantity: int
    unit_price: float  # Will be converted to Decimal
    stated_gst_rate: Optional[float] = None  # Optional, from AI extraction


@dataclass
class GSTCalculationRequest:
    """Request payload for POST /gst/calculate endpoint."""
    customer_state: Optional[str] = None
    items: List[GSTCalculationItemRequest] = field(default_factory=list)


@dataclass
class CalculatedItemResponse:
    """Item with calculated GST breakdown."""
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
    stated_gst_rate: Optional[float]
    gst_mismatch: bool
    tax_type: str  # 'intra_state' or 'inter_state'


@dataclass
class GSTCalculationResponse:
    """Response for POST /gst/calculate endpoint."""
    items: List[CalculatedItemResponse]
    total_subtotal: float
    total_gst_amount: float
    total_cgst: float
    total_sgst: float
    total_igst: float
    grand_total: float
    tax_type: str
    seller_state: str
    customer_state: Optional[str]
    stated_gst_rate: Optional[float]
    determined_gst_rate: float
    gst_mismatch: bool
    mismatch_details: List[str]

    def to_dict(self) -> dict:
        return {
            'items': [
                {
                    'name': item.name,
                    'quantity': item.quantity,
                    'unitPrice': item.unit_price,
                    'subtotal': item.subtotal,
                    'gstRate': item.gst_rate,
                    'gstAmount': item.gst_amount,
                    'cgstRate': item.cgst_rate,
                    'cgstAmount': item.cgst_amount,
                    'sgstRate': item.sgst_rate,
                    'sgstAmount': item.sgst_amount,
                    'igstRate': item.igst_rate,
                    'igstAmount': item.igst_amount,
                    'statedGstRate': item.stated_gst_rate,
                    'gstMismatch': item.gst_mismatch,
                    'taxType': item.tax_type,
                }
                for item in self.items
            ],
            'totalSubtotal': self.total_subtotal,
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


# Export for convenience
__all__ = [
    'TaxType',
    'GSTCalculationItemRequest',
    'GSTCalculationRequest',
    'CalculatedItemResponse',
    'GSTCalculationResponse',
]