"""
Invoice Persistence Service for INVOX.

Bridges the invoice generation flow with DynamoDB persistence.
Handles saving invoices after generation and retrieving them.
"""

import uuid
from typing import Optional, Dict, Any, List
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
    PersistedUPIInfo,
    InvoiceStatus as PersistedInvoiceStatus,
)
from src.services.dynamodb_repository import (
    InvoiceRepository,
    get_repository,
    set_repository,
    reset_repository,
)


def _invoice_response_to_persisted(
    invoice_response: InvoiceResponse,
    idempotency_key: Optional[str] = None,
) -> PersistedInvoice:
    """Convert InvoiceResponse to PersistedInvoice for storage."""
    # Build items
    items = []
    for item in invoice_response.items:
        persisted_item = PersistedInvoiceItem(
            name=item.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
            gst_rate=item.gst_rate,
            gst_amount=item.gst_amount,
            cgst_rate=item.cgst_rate,
            cgst_amount=item.cgst_amount,
            sgst_rate=item.sgst_rate,
            sgst_amount=item.sgst_amount,
            igst_rate=item.igst_rate,
            igst_amount=item.igst_amount,
            stated_gst_rate=item.stated_gst_rate,
            gst_mismatch=item.gst_mismatch,
            tax_type=item.tax_type,
        )
        items.append(persisted_item)
    
    # Build seller
    seller = PersistedSellerInfo(
        name=invoice_response.seller.name,
        address=invoice_response.seller.address,
        state=invoice_response.seller.state,
        contact=invoice_response.seller.contact,
        gstin=invoice_response.seller.gstin,
    )
    
    # Build customer
    customer = PersistedCustomerInfo(
        name=invoice_response.customer.name,
        location=invoice_response.customer.location,
    )
    
    # Build UPI info if present
    upi_info = None
    if hasattr(invoice_response, 'upi_info') and invoice_response.upi_info:
        upi = invoice_response.upi_info
        upi_info = PersistedUPIInfo(
            upi_request_id=upi.get('upi_request_id', ''),
            upi_deep_link=upi.get('upi_deep_link', ''),
            qr_code_data=upi.get('qr_code_data', ''),
            amount=upi.get('amount', 0),
            currency=upi.get('currency', 'INR'),
            merchant_name=upi.get('merchant_name', ''),
            merchant_vpa=upi.get('merchant_vpa', ''),
            transaction_note=upi.get('transaction_note'),
            status=upi.get('status', 'pending'),
            created_at=upi.get('created_at'),
            expires_at=upi.get('expires_at'),
        )
    
    # Generate invoice_id if not present (use invoice_number as base)
    invoice_id = invoice_response.invoice_number
    
    return PersistedInvoice(
        invoice_id=invoice_id,
        invoice_number=invoice_response.invoice_number,
        invoice_date=invoice_response.invoice_date,
        status=invoice_response.status,
        seller=seller,
        customer=customer,
        items=items,
        subtotal=invoice_response.subtotal,
        total_gst_amount=invoice_response.total_gst_amount,
        total_cgst=invoice_response.total_cgst,
        total_sgst=invoice_response.total_sgst,
        total_igst=invoice_response.total_igst,
        grand_total=invoice_response.grand_total,
        tax_type=invoice_response.tax_type,
        seller_state=invoice_response.seller_state,
        customer_state=invoice_response.customer_state,
        stated_gst_rate=invoice_response.stated_gst_rate,
        determined_gst_rate=invoice_response.determined_gst_rate,
        gst_mismatch=invoice_response.gst_mismatch,
        mismatch_details=invoice_response.mismatch_details,
        upi_info=upi_info,
        idempotency_key=idempotency_key,
    )


def _persisted_to_invoice_response(persisted: PersistedInvoice) -> InvoiceResponse:
    """Convert PersistedInvoice back to InvoiceResponse."""
    # Build items
    items = []
    for item in persisted.items:
        invoice_item = InvoiceItem(
            name=item.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
            gst_rate=item.gst_rate,
            gst_amount=item.gst_amount,
            cgst_rate=item.cgst_rate,
            cgst_amount=item.cgst_amount,
            sgst_rate=item.sgst_rate,
            sgst_amount=item.sgst_amount,
            igst_rate=item.igst_rate,
            igst_amount=item.igst_amount,
            stated_gst_rate=item.stated_gst_rate,
            gst_mismatch=item.gst_mismatch,
            tax_type=item.tax_type,
        )
        items.append(invoice_item)
    
    # Build seller
    seller = SellerInfo(
        name=persisted.seller.name,
        address=persisted.seller.address,
        state=persisted.seller.state,
        contact=persisted.seller.contact,
        gstin=persisted.seller.gstin,
    )
    
    # Build customer
    customer = CustomerInfo(
        name=persisted.customer.name,
        location=persisted.customer.location,
    )
    
    # Build response
    response = InvoiceResponse(
        invoice_number=persisted.invoice_number,
        invoice_date=persisted.invoice_date,
        status=persisted.status,
        seller=seller,
        customer=customer,
        items=items,
        subtotal=persisted.subtotal,
        total_gst_amount=persisted.total_gst_amount,
        total_cgst=persisted.total_cgst,
        total_sgst=persisted.total_sgst,
        total_igst=persisted.total_igst,
        grand_total=persisted.grand_total,
        tax_type=persisted.tax_type,
        seller_state=persisted.seller_state,
        customer_state=persisted.customer_state,
        stated_gst_rate=persisted.stated_gst_rate,
        determined_gst_rate=persisted.determined_gst_rate,
        gst_mismatch=persisted.gst_mismatch,
        mismatch_details=persisted.mismatch_details,
    )
    
    # Add UPI info if present
    if persisted.upi_info:
        response.upi_info = persisted.upi_info.to_dict()
    
    # Add timestamps
    response.created_at = persisted.created_at
    response.updated_at = persisted.updated_at
    
    return response


def persist_invoice(
    invoice_response: InvoiceResponse,
    idempotency_key: Optional[str] = None,
    repository: Optional[InvoiceRepository] = None,
) -> InvoiceResponse:
    """
    Persist an invoice to DynamoDB.
    
    Args:
        invoice_response: The invoice to persist
        idempotency_key: Optional idempotency key for duplicate detection
        repository: Optional repository instance (uses global if not provided)
        
    Returns:
        The persisted invoice response (with timestamps)
        
    Raises:
        RuntimeError: If persistence fails
    """
    repo = repository or get_repository()
    
    # Convert to persisted format
    persisted = _invoice_response_to_persisted(invoice_response, idempotency_key)
    
    # Save to DynamoDB
    saved = repo.save_invoice(persisted)
    
    # Convert back to response format
    return _persisted_to_invoice_response(saved)


def retrieve_invoice(
    invoice_id: str,
    repository: Optional[InvoiceRepository] = None,
) -> Optional[InvoiceResponse]:
    """
    Retrieve an invoice from DynamoDB by ID.
    
    Args:
        invoice_id: The invoice UUID/number
        repository: Optional repository instance (uses global if not provided)
        
    Returns:
        InvoiceResponse if found, None otherwise
    """
    repo = repository or get_repository()
    persisted = repo.get_invoice(invoice_id)
    if persisted:
        return _persisted_to_invoice_response(persisted)
    return None


def retrieve_invoice_by_number(
    invoice_number: str,
    repository: Optional[InvoiceRepository] = None,
) -> Optional[InvoiceResponse]:
    """
    Retrieve an invoice from DynamoDB by invoice number.
    
    Args:
        invoice_number: The human-readable invoice number
        repository: Optional repository instance (uses global if not provided)
        
    Returns:
        InvoiceResponse if found, None otherwise
    """
    repo = repository or get_repository()
    persisted = repo.get_invoice_by_number(invoice_number)
    if persisted:
        return _persisted_to_invoice_response(persisted)
    return None


def update_invoice_payment_status(
    invoice_id: str,
    status: str,
    repository: Optional[InvoiceRepository] = None,
) -> Optional[InvoiceResponse]:
    """
    Update invoice payment status.
    
    Args:
        invoice_id: The invoice UUID
        status: New status (e.g., 'paid', 'cancelled')
        repository: Optional repository instance (uses global if not provided)
        
    Returns:
        Updated InvoiceResponse if found, None otherwise
    """
    repo = repository or get_repository()
    persisted = repo.update_invoice_status(invoice_id, status)
    if persisted:
        return _persisted_to_invoice_response(persisted)
    return None


def add_upi_payment_info(
    invoice_id: str,
    upi_info: Dict[str, Any],
    repository: Optional[InvoiceRepository] = None,
) -> Optional[InvoiceResponse]:
    """
    Add UPI payment information to an existing invoice.
    
    Args:
        invoice_id: The invoice UUID
        upi_info: UPI payment information dict
        repository: Optional repository instance (uses global if not provided)
        
    Returns:
        Updated InvoiceResponse if found, None otherwise
    """
    repo = repository or get_repository()
    
    persisted_upi = PersistedUPIInfo(
        upi_request_id=upi_info.get('upi_request_id', ''),
        upi_deep_link=upi_info.get('upi_deep_link', ''),
        qr_code_data=upi_info.get('qr_code_data', ''),
        amount=upi_info.get('amount', 0),
        currency=upi_info.get('currency', 'INR'),
        merchant_name=upi_info.get('merchant_name', ''),
        merchant_vpa=upi_info.get('merchant_vpa', ''),
        transaction_note=upi_info.get('transaction_note'),
        status=upi_info.get('status', 'pending'),
        created_at=upi_info.get('created_at'),
        expires_at=upi_info.get('expires_at'),
    )
    
    persisted = repo.add_upi_info(invoice_id, persisted_upi)
    if persisted:
        return _persisted_to_invoice_response(persisted)
    return None


__all__ = [
    'persist_invoice',
    'retrieve_invoice',
    'retrieve_invoice_by_number',
    'update_invoice_payment_status',
    'add_upi_payment_info',
    'get_repository',
    'set_repository',
    'reset_repository',
]