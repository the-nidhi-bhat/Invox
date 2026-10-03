"""
UPI Models for INVOX.

Defines the request/response contracts for UPI payment request generation.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UPIStatus(str, Enum):
    """UPI payment request status."""
    PENDING = "pending"
    SIMULATED_SUCCESS = "simulated_success"
    SIMULATED_FAILED = "simulated_failed"
    EXPIRED = "expired"


@dataclass
class UPIRequest:
    """Request payload for POST /upi/generate endpoint."""
    # Invoice reference
    invoice_number: str
    invoice_amount: float
    # Payer info
    customer_name: Optional[str] = None
    customer_vpa: Optional[str] = None  # Payer's UPI ID
    # Payment details
    merchant_name: Optional[str] = None
    merchant_vpa: Optional[str] = None  # Merchant's UPI ID
    transaction_note: Optional[str] = None
    # Optional: currency (default INR)
    currency: str = "INR"


@dataclass
class UPIResponse:
    """Response for POST /upi/generate endpoint."""
    upi_request_id: str
    upi_deep_link: str
    qr_code_data: str  # Base64 encoded PNG or SVG data
    amount: float
    currency: str
    merchant_name: str
    merchant_vpa: str
    transaction_note: Optional[str]
    status: str  # UPIStatus.PENDING
    created_at: str  # ISO format
    expires_at: str  # ISO format (e.g., 15 minutes)

    def to_dict(self) -> dict:
        return {
            'upiRequestId': self.upi_request_id,
            'upiDeepLink': self.upi_deep_link,
            'qrCodeData': self.qr_code_data,
            'amount': self.amount,
            'currency': self.currency,
            'merchantName': self.merchant_name,
            'merchantVpa': self.merchant_vpa,
            'transactionNote': self.transaction_note,
            'status': self.status,
            'createdAt': self.created_at,
            'expiresAt': self.expires_at,
        }


# Export for convenience
__all__ = [
    'UPIStatus',
    'UPIRequest',
    'UPIResponse',
]