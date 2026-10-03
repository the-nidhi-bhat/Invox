"""
DynamoDB Persistence Models for INVOX.

Defines the data models for invoice persistence in DynamoDB.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice status in persistence layer."""
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass
class PersistedInvoiceItem:
    """Persisted invoice line item."""
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
            'unit_price': self.unit_price,
            'subtotal': self.subtotal,
            'gst_rate': self.gst_rate,
            'gst_amount': self.gst_amount,
            'cgst_rate': self.cgst_rate,
            'cgst_amount': self.cgst_amount,
            'sgst_rate': self.sgst_rate,
            'sgst_amount': self.sgst_amount,
            'igst_rate': self.igst_rate,
            'igst_amount': self.igst_amount,
            'stated_gst_rate': self.stated_gst_rate,
            'gst_mismatch': self.gst_mismatch,
            'tax_type': self.tax_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PersistedInvoiceItem':
        return cls(
            name=data.get('name', ''),
            quantity=int(data.get('quantity', 0)),
            unit_price=float(data.get('unit_price', 0)),
            subtotal=float(data.get('subtotal', 0)),
            gst_rate=float(data.get('gst_rate', 0)),
            gst_amount=float(data.get('gst_amount', 0)),
            cgst_rate=float(data.get('cgst_rate', 0)),
            cgst_amount=float(data.get('cgst_amount', 0)),
            sgst_rate=float(data.get('sgst_rate', 0)),
            sgst_amount=float(data.get('sgst_amount', 0)),
            igst_rate=float(data.get('igst_rate', 0)),
            igst_amount=float(data.get('igst_amount', 0)),
            stated_gst_rate=data.get('stated_gst_rate'),
            gst_mismatch=bool(data.get('gst_mismatch', False)),
            tax_type=data.get('tax_type', 'intra_state'),
        )


@dataclass
class PersistedSellerInfo:
    """Persisted seller information."""
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

    @classmethod
    def from_dict(cls, data: dict) -> 'PersistedSellerInfo':
        return cls(
            name=data.get('name', ''),
            address=data.get('address', ''),
            state=data.get('state', ''),
            contact=data.get('contact'),
            gstin=data.get('gstin'),
        )


@dataclass
class PersistedCustomerInfo:
    """Persisted customer information."""
    name: Optional[str] = None
    location: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'location': self.location,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PersistedCustomerInfo':
        return cls(
            name=data.get('name'),
            location=data.get('location'),
        )


@dataclass
class PersistedUPIInfo:
    """Persisted UPI payment information."""
    upi_request_id: str
    upi_deep_link: str
    qr_code_data: str
    amount: float
    currency: str
    merchant_name: str
    merchant_vpa: str
    transaction_note: Optional[str] = None
    status: str = "pending"
    created_at: Optional[str] = None
    expires_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'upi_request_id': self.upi_request_id,
            'upi_deep_link': self.upi_deep_link,
            'qr_code_data': self.qr_code_data,
            'amount': self.amount,
            'currency': self.currency,
            'merchant_name': self.merchant_name,
            'merchant_vpa': self.merchant_vpa,
            'transaction_note': self.transaction_note,
            'status': self.status,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PersistedUPIInfo':
        return cls(
            upi_request_id=data.get('upi_request_id', ''),
            upi_deep_link=data.get('upi_deep_link', ''),
            qr_code_data=data.get('qr_code_data', ''),
            amount=float(data.get('amount', 0)),
            currency=data.get('currency', 'INR'),
            merchant_name=data.get('merchant_name', ''),
            merchant_vpa=data.get('merchant_vpa', ''),
            transaction_note=data.get('transaction_note'),
            status=data.get('status', 'pending'),
            created_at=data.get('created_at'),
            expires_at=data.get('expires_at'),
        )


@dataclass
class PersistedInvoice:
    """
    Complete persisted invoice record for DynamoDB.
    
    Primary Key: invoice_id (string)
    """
    # Primary key
    invoice_id: str
    # Business identifier (human-readable)
    invoice_number: str
    invoice_date: str  # ISO format
    status: str  # InvoiceStatus.PENDING, PAID, CANCELLED
    
    # Seller info
    seller: PersistedSellerInfo
    
    # Customer info
    customer: PersistedCustomerInfo
    
    # Line items
    items: List[PersistedInvoiceItem] = field(default_factory=list)
    
    # Totals
    subtotal: float = 0.0
    total_gst_amount: float = 0.0
    total_cgst: float = 0.0
    total_sgst: float = 0.0
    total_igst: float = 0.0
    grand_total: float = 0.0
    
    # Tax classification
    tax_type: str = "intra_state"
    seller_state: str = ""
    customer_state: Optional[str] = None
    
    # GST mismatch tracking
    stated_gst_rate: Optional[float] = None
    determined_gst_rate: float = 0.0
    gst_mismatch: bool = False
    mismatch_details: List[str] = field(default_factory=list)
    
    # UPI payment info (optional)
    upi_info: Optional[PersistedUPIInfo] = None
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Idempotency key (hash of request data for duplicate detection)
    idempotency_key: Optional[str] = None

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert to DynamoDB item format (with type annotations)."""
        item = {
            'invoice_id': {'S': self.invoice_id},
            'invoice_number': {'S': self.invoice_number},
            'invoice_date': {'S': self.invoice_date},
            'status': {'S': self.status},
            'seller': {'M': {k: self._to_dynamodb_value(v) for k, v in self.seller.to_dict().items()}},
            'customer': {'M': {k: self._to_dynamodb_value(v) for k, v in self.customer.to_dict().items()}},
            'items': {'L': [{'M': {k: self._to_dynamodb_value(v) for k, v in item.to_dict().items()}} for item in self.items]},
            'subtotal': {'N': str(self.subtotal)},
            'total_gst_amount': {'N': str(self.total_gst_amount)},
            'total_cgst': {'N': str(self.total_cgst)},
            'total_sgst': {'N': str(self.total_sgst)},
            'total_igst': {'N': str(self.total_igst)},
            'grand_total': {'N': str(self.grand_total)},
            'tax_type': {'S': self.tax_type},
            'seller_state': {'S': self.seller_state},
            'customer_state': {'S': self.customer_state} if self.customer_state else {'NULL': True},
            'stated_gst_rate': {'N': str(self.stated_gst_rate)} if self.stated_gst_rate is not None else {'NULL': True},
            'determined_gst_rate': {'N': str(self.determined_gst_rate)},
            'gst_mismatch': {'BOOL': self.gst_mismatch},
            'mismatch_details': {'L': [{'S': d} for d in self.mismatch_details]},
            'created_at': {'S': self.created_at},
            'updated_at': {'S': self.updated_at},
        }
        if self.idempotency_key:
            item['idempotency_key'] = {'S': self.idempotency_key}
        if self.upi_info:
            item['upi_info'] = {'M': {k: self._to_dynamodb_value(v) for k, v in self.upi_info.to_dict().items()}}
        return item

    def _to_dynamodb_value(self, value: Any) -> Dict[str, Any]:
        """Convert Python value to DynamoDB attribute value."""
        if value is None:
            return {'NULL': True}
        elif isinstance(value, bool):
            return {'BOOL': value}
        elif isinstance(value, (int, float)):
            return {'N': str(value)}
        elif isinstance(value, str):
            return {'S': value}
        elif isinstance(value, list):
            return {'L': [self._to_dynamodb_value(v) for v in value]}
        elif isinstance(value, dict):
            return {'M': {k: self._to_dynamodb_value(v) for k, v in value.items()}}
        else:
            return {'S': str(value)}

    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]) -> 'PersistedInvoice':
        """Create PersistedInvoice from DynamoDB item."""
        def from_dynamodb_value(val: Dict[str, Any]) -> Any:
            if 'S' in val:
                return val['S']
            elif 'N' in val:
                # Try to parse as int first, then float
                try:
                    return int(val['N'])
                except ValueError:
                    return float(val['N'])
            elif 'BOOL' in val:
                return val['BOOL']
            elif 'NULL' in val and val['NULL']:
                return None
            elif 'L' in val:
                return [from_dynamodb_value(v) for v in val['L']]
            elif 'M' in val:
                return {k: from_dynamodb_value(v) for k, v in val['M'].items()}
            return None

        data = {k: from_dynamodb_value(v) for k, v in item.items()}
        
        # Parse nested objects
        seller_data = data.get('seller', {})
        customer_data = data.get('customer', {})
        items_data = data.get('items', [])
        upi_info_data = data.get('upi_info')
        
        return cls(
            invoice_id=data.get('invoice_id', ''),
            invoice_number=data.get('invoice_number', ''),
            invoice_date=data.get('invoice_date', ''),
            status=data.get('status', 'pending'),
            seller=PersistedSellerInfo.from_dict(seller_data),
            customer=PersistedCustomerInfo.from_dict(customer_data),
            items=[PersistedInvoiceItem.from_dict(i) for i in items_data],
            subtotal=float(data.get('subtotal', 0)),
            total_gst_amount=float(data.get('total_gst_amount', 0)),
            total_cgst=float(data.get('total_cgst', 0)),
            total_sgst=float(data.get('total_sgst', 0)),
            total_igst=float(data.get('total_igst', 0)),
            grand_total=float(data.get('grand_total', 0)),
            tax_type=data.get('tax_type', 'intra_state'),
            seller_state=data.get('seller_state', ''),
            customer_state=data.get('customer_state'),
            stated_gst_rate=data.get('stated_gst_rate'),
            determined_gst_rate=float(data.get('determined_gst_rate', 0)),
            gst_mismatch=bool(data.get('gst_mismatch', False)),
            mismatch_details=data.get('mismatch_details', []),
            upi_info=PersistedUPIInfo.from_dict(upi_info_data) if upi_info_data else None,
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            idempotency_key=data.get('idempotency_key'),
        )

    def to_response_dict(self) -> dict:
        """Convert to API response format (compatible with InvoiceResponse)."""
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
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
        if self.upi_info:
            result['upiInfo'] = self.upi_info.to_dict()
        return result


__all__ = [
    'InvoiceStatus',
    'PersistedInvoiceItem',
    'PersistedSellerInfo',
    'PersistedCustomerInfo',
    'PersistedUPIInfo',
    'PersistedInvoice',
]