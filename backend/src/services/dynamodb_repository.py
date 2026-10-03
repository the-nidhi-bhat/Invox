"""
DynamoDB Repository for INVOX Invoice Persistence.

Provides data access layer for invoice persistence using DynamoDB.
Uses a simple interface that can be mocked for testing.
"""

import os
import json
import hashlib
import boto3
from datetime import datetime
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError

from src.models.persistence import (
    PersistedInvoice,
    PersistedInvoiceItem,
    PersistedSellerInfo,
    PersistedCustomerInfo,
    PersistedUPIInfo,
    InvoiceStatus,
)


class InvoiceRepository:
    """
    DynamoDB repository for invoice persistence.
    
    Table Schema:
    - Primary Key: invoice_id (String)
    - GSI: invoice_number-index (for lookup by invoice_number)
    
    All operations use the invoice_id as the primary key.
    """
    
    def __init__(
        self,
        table_name: Optional[str] = None,
        dynamodb_client: Optional[Any] = None,
        region: Optional[str] = None,
    ):
        """
        Initialize the repository.
        
        Args:
            table_name: DynamoDB table name (from env if not provided)
            dynamodb_client: Pre-configured boto3 DynamoDB client (for testing)
            region: AWS region (for creating client if not provided)
        """
        self.table_name = table_name or os.environ.get('INVOICE_TABLE_NAME', 'invox-invoices')
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        
        if dynamodb_client:
            self.client = dynamodb_client
        else:
            self.client = boto3.client('dynamodb', region_name=self.region)
        
        self._table_verified = False
    
    def _verify_table(self) -> None:
        """Verify table exists (lazy initialization)."""
        if self._table_verified:
            return
        try:
            self.client.describe_table(TableName=self.table_name)
            self._table_verified = True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise RuntimeError(f"DynamoDB table '{self.table_name}' does not exist")
            raise
    
    def _generate_idempotency_key(self, invoice_data: dict) -> str:
        """
        Generate a deterministic idempotency key from invoice data.
        
        Uses a hash of the key invoice fields to detect duplicates.
        """
        # Create a normalized representation of the invoice data
        key_data = {
            'invoice_number': invoice_data.get('invoice_number'),
            'seller': invoice_data.get('seller'),
            'customer': invoice_data.get('customer'),
            'items': invoice_data.get('items'),
            'subtotal': invoice_data.get('subtotal'),
            'grand_total': invoice_data.get('grand_total'),
            'tax_type': invoice_data.get('tax_type'),
        }
        # Sort keys for deterministic hashing
        json_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()[:32]
    
    def _check_idempotency(self, idempotency_key: str) -> Optional[PersistedInvoice]:
        """
        Check legacy invoices written before transactional idempotency records.
        """
        if not idempotency_key:
            return None

        record = self._get_idempotency_record(idempotency_key)
        if record:
            invoice_id = record.get('target_invoice_id', {}).get('S')
            invoice = self.get_invoice(invoice_id) if invoice_id else None
            if invoice:
                return invoice
            raise RuntimeError('Idempotency record exists without its invoice')

        scan_kwargs = {
            'TableName': self.table_name,
            'ConsistentRead': True,
            'FilterExpression': (
                'idempotency_key = :key AND attribute_not_exists(record_type)'
            ),
            'ExpressionAttributeValues': {':key': {'S': idempotency_key}},
        }
        while True:
            response = self.client.scan(**scan_kwargs)
            items = response.get('Items', [])
            if items:
                return PersistedInvoice.from_dynamodb_item(items[0])

            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                return None
            scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

    def _get_idempotency_record(self, idempotency_key: str) -> Optional[dict]:
        response = self.client.get_item(
            TableName=self.table_name,
            Key={'invoice_id': {'S': f'IDEMPOTENCY#{idempotency_key}'}},
            ConsistentRead=True,
        )
        return response.get('Item')

    def _write_invoice_idempotently(
        self,
        invoice: PersistedInvoice,
        item: dict,
    ) -> PersistedInvoice:
        idempotency_key = invoice.idempotency_key
        if not idempotency_key:
            raise RuntimeError('Invoice idempotency key is required')

        idempotency_record = {
            'invoice_id': {'S': f'IDEMPOTENCY#{idempotency_key}'},
            'record_type': {'S': 'idempotency'},
            'idempotency_key': {'S': idempotency_key},
            'target_invoice_id': {'S': invoice.invoice_id},
        }
        transaction = [
            {
                'Put': {
                    'TableName': self.table_name,
                    'Item': item,
                    'ConditionExpression': 'attribute_not_exists(invoice_id)',
                }
            },
            {
                'Put': {
                    'TableName': self.table_name,
                    'Item': idempotency_record,
                    'ConditionExpression': 'attribute_not_exists(invoice_id)',
                }
            },
        ]
        for attempt in range(3):
            try:
                self.client.transact_write_items(TransactItems=transaction)
                return invoice
            except ClientError as error:
                error_code = error.response.get('Error', {}).get('Code')
                if error_code != 'TransactionCanceledException':
                    raise RuntimeError(f"Failed to save invoice: {error_code}") from error

                existing_record = self._get_idempotency_record(idempotency_key)
                if existing_record:
                    existing_invoice_id = existing_record.get('target_invoice_id', {}).get('S')
                    existing_invoice = (
                        self.get_invoice(existing_invoice_id) if existing_invoice_id else None
                    )
                    if existing_invoice:
                        return existing_invoice

                cancellation_reasons = error.response.get('CancellationReasons', [])
                has_transaction_conflict = any(
                    reason.get('Code') == 'TransactionConflict'
                    for reason in cancellation_reasons
                )
                if not has_transaction_conflict or attempt == 2:
                    break

        existing_invoice = self.get_invoice(invoice.invoice_id)
        if existing_invoice and existing_invoice.idempotency_key == idempotency_key:
            return existing_invoice
        raise RuntimeError('Invoice creation conflict - please retry')

    def save_invoice(self, invoice: PersistedInvoice) -> PersistedInvoice:
        """
        Save an invoice with its idempotency claim in one atomic transaction.
        """
        self._verify_table()

        if not invoice.idempotency_key:
            invoice.idempotency_key = self._generate_idempotency_key(invoice.to_dynamodb_item())

        existing = self._check_idempotency(invoice.idempotency_key)
        if existing:
            return existing

        invoice.updated_at = datetime.utcnow().isoformat()
        return self._write_invoice_idempotently(invoice, invoice.to_dynamodb_item())
    
    def get_invoice(self, invoice_id: str) -> Optional[PersistedInvoice]:
        """
        Retrieve an invoice by its ID.
        
        Args:
            invoice_id: The invoice UUID
            
        Returns:
            PersistedInvoice if found, None otherwise
        """
        self._verify_table()
        
        try:
            response = self.client.get_item(
                TableName=self.table_name,
                Key={'invoice_id': {'S': invoice_id}},
            )
            item = response.get('Item')
            if item:
                return PersistedInvoice.from_dynamodb_item(item)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                return None
            raise RuntimeError(f"Failed to retrieve invoice: {error_code}")
        return None
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[PersistedInvoice]:
        """
        Retrieve an invoice by its business invoice number.
        
        Note: This requires a GSI on invoice_number for efficient lookup.
        For MVP, we'll do a scan (acceptable for low volume).
        In production, add a GSI on invoice_number.
        
        Args:
            invoice_number: The human-readable invoice number (e.g., INV-20240115-0001)
            
        Returns:
            PersistedInvoice if found, None otherwise
        """
        self._verify_table()
        
        try:
            response = self.client.scan(
                TableName=self.table_name,
                FilterExpression='invoice_number = :num',
                ExpressionAttributeValues={':num': {'S': invoice_number}},
                Limit=1,
            )
            items = response.get('Items', [])
            if items:
                return PersistedInvoice.from_dynamodb_item(items[0])
        except ClientError:
            pass
        return None
    
    def update_invoice_status(self, invoice_id: str, status: str) -> Optional[PersistedInvoice]:
        """
        Update invoice status (e.g., PENDING -> PAID).
        
        Args:
            invoice_id: The invoice UUID
            status: New status value
            
        Returns:
            Updated invoice if found, None otherwise
        """
        self._verify_table()
        
        try:
            response = self.client.update_item(
                TableName=self.table_name,
                Key={'invoice_id': {'S': invoice_id}},
                UpdateExpression='SET #status = :status, updated_at = :updated',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': {'S': status},
                    ':updated': {'S': datetime.utcnow().isoformat()},
                },
                ReturnValues='ALL_NEW',
            )
            item = response.get('Attributes')
            if item:
                return PersistedInvoice.from_dynamodb_item(item)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                return None
            raise RuntimeError(f"Failed to update invoice status: {error_code}")
        return None
    
    def add_upi_info(self, invoice_id: str, upi_info: PersistedUPIInfo) -> Optional[PersistedInvoice]:
        """
        Add UPI payment information to an existing invoice.
        
        Args:
            invoice_id: The invoice UUID
            upi_info: UPI payment information
            
        Returns:
            Updated invoice if found, None otherwise
        """
        self._verify_table()
        
        try:
            upi_dict = upi_info.to_dict()
            upi_m = {k: self._to_dynamodb_value(v) for k, v in upi_dict.items()}
            
            response = self.client.update_item(
                TableName=self.table_name,
                Key={'invoice_id': {'S': invoice_id}},
                UpdateExpression='SET upi_info = :upi, updated_at = :updated',
                ExpressionAttributeValues={
                    ':upi': {'M': upi_m},
                    ':updated': {'S': datetime.utcnow().isoformat()},
                },
                ReturnValues='ALL_NEW',
            )
            item = response.get('Attributes')
            if item:
                return PersistedInvoice.from_dynamodb_item(item)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                return None
            raise RuntimeError(f"Failed to add UPI info: {error_code}")
        return None
    
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


# Global repository instance (initialized lazily)
_repository: Optional[InvoiceRepository] = None


def get_repository() -> InvoiceRepository:
    """Get or create the global repository instance."""
    global _repository
    if _repository is None:
        _repository = InvoiceRepository()
    return _repository


def set_repository(repo: InvoiceRepository) -> None:
    """Set the global repository instance (for testing)."""
    global _repository
    _repository = repo


def reset_repository() -> None:
    """Reset the global repository instance."""
    global _repository
    _repository = None


__all__ = [
    'InvoiceRepository',
    'get_repository',
    'set_repository',
    'reset_repository',
]