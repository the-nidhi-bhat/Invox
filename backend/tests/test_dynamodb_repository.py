"""
Tests for DynamoDB Repository.

Tests the InvoiceRepository with mocked DynamoDB client.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from threading import Lock
from botocore.exceptions import ClientError

from src.services.dynamodb_repository import (
    InvoiceRepository,
    get_repository,
    set_repository,
    reset_repository,
)
from src.models.persistence import (
    PersistedInvoice,
    PersistedInvoiceItem,
    PersistedSellerInfo,
    PersistedCustomerInfo,
    PersistedUPIInfo,
    InvoiceStatus,
)


def make_client_error(code: str, message: str = ""):
    """Create a mock ClientError."""
    return ClientError(
        {'Error': {'Code': code, 'Message': message}},
        'operation_name'
    )


class MockDynamoDBClient:
    """Mock DynamoDB client for testing."""
    
    def __init__(self):
        self.items = {}
        self.table_exists = True
        self.transaction_lock = Lock()
    
    def describe_table(self, TableName):
        if not self.table_exists:
            raise make_client_error('ResourceNotFoundException', 'Table not found')
        return {'Table': {'TableName': TableName}}
    
    def put_item(self, TableName, Item, ConditionExpression=None, ExpressionAttributeValues=None):
        invoice_id = Item['invoice_id']['S']
        
        # Check condition expression
        if ConditionExpression and 'attribute_not_exists' in ConditionExpression:
            if invoice_id in self.items:
                raise make_client_error('ConditionalCheckFailedException', 'Condition check failed')
        
        self.items[invoice_id] = Item
        return {}
    
    def get_item(self, TableName, Key, ConsistentRead=False):
        invoice_id = Key['invoice_id']['S']
        if invoice_id in self.items:
            return {'Item': self.items[invoice_id]}
        return {}

    def transact_write_items(self, TransactItems):
        with self.transaction_lock:
            for transaction in TransactItems:
                put = transaction['Put']
                item = put['Item']
                invoice_id = item['invoice_id']['S']
                if (
                    put.get('ConditionExpression') == 'attribute_not_exists(invoice_id)'
                    and invoice_id in self.items
                ):
                    raise make_client_error(
                        'TransactionCanceledException',
                        'Conditional request failed',
                    )
            for transaction in TransactItems:
                item = transaction['Put']['Item']
                self.items[item['invoice_id']['S']] = item
        return {}

    def update_item(self, TableName, Key, UpdateExpression, ExpressionAttributeNames=None, ExpressionAttributeValues=None, ReturnValues=None, **kwargs):
        invoice_id = Key['invoice_id']['S']
        if invoice_id not in self.items:
            raise make_client_error('ResourceNotFoundException', 'Item not found')
        
        # Simple update simulation
        item = self.items[invoice_id]
        if 'status' in UpdateExpression:
            status_val = ExpressionAttributeValues[':status']['S']
            item['status'] = {'S': status_val}
        if 'upi_info' in UpdateExpression:
            upi_val = ExpressionAttributeValues[':upi']['M']
            item['upi_info'] = {'M': upi_val}
        item['updated_at'] = {'S': ExpressionAttributeValues[':updated']['S']}
        
        if ReturnValues == 'ALL_NEW':
            return {'Attributes': item}
        return {}
    
    def scan(
        self,
        TableName,
        FilterExpression=None,
        ExpressionAttributeValues=None,
        Limit=None,
        **kwargs,
    ):
        results = []
        # Extract attribute name from FilterExpression (e.g., "invoice_number = :num" -> "invoice_number")
        attr_name = None
        if FilterExpression:
            # Simple parsing: get the part before the operator
            parts = FilterExpression.split()
            if parts:
                attr_name = parts[0]
        
        for item in self.items.values():
            if FilterExpression and ExpressionAttributeValues:
                match = True
                # Use the actual attribute name from FilterExpression
                if attr_name and attr_name in item:
                    # Get the expected value from ExpressionAttributeValues (first one)
                    for val in ExpressionAttributeValues.values():
                        expected_val = val.get('S')
                        actual_val = item.get(attr_name, {}).get('S')
                        if actual_val != expected_val:
                            match = False
                            break
                if 'attribute_not_exists(record_type)' in FilterExpression and 'record_type' in item:
                    match = False
                else:
                    if not attr_name or attr_name not in item:
                        # Fallback: check all expression attribute values
                        for key, val in ExpressionAttributeValues.items():
                            aname = key.replace(':', '')
                            expected_val = val.get('S')
                            actual_val = item.get(aname, {}).get('S')
                            if actual_val != expected_val:
                                match = False
                                break
                if match:
                    results.append(item)
            else:
                results.append(item)
            
            if Limit and len(results) >= Limit:
                break
        return {'Items': results}


@pytest.fixture
def mock_client():
    """Create a mock DynamoDB client."""
    return MockDynamoDBClient()


@pytest.fixture
def repository(mock_client):
    """Create an InvoiceRepository with mocked client."""
    repo = InvoiceRepository(
        table_name="test-invoices",
        dynamodb_client=mock_client,
        region="us-east-1",
    )
    return repo


@pytest.fixture
def sample_invoice():
    """Create a sample persisted invoice."""
    return PersistedInvoice(
        invoice_id="INV-20240115-0001",
        invoice_number="INV-20240115-0001",
        invoice_date="2024-01-15T10:00:00",
        status=InvoiceStatus.PENDING.value,
        seller=PersistedSellerInfo(
            name="Test Seller",
            address="123 Test St",
            state="MAHARASHTRA",
        ),
        customer=PersistedCustomerInfo(
            name="Test Customer",
            location="Mumbai, MAHARASHTRA",
        ),
        items=[
            PersistedInvoiceItem(
                name="Product 1",
                quantity=1,
                unit_price=100.0,
                subtotal=100.0,
                gst_rate=18.0,
                gst_amount=18.0,
                cgst_rate=9.0,
                cgst_amount=9.0,
                sgst_rate=9.0,
                sgst_amount=9.0,
                igst_rate=0.0,
                igst_amount=0.0,
            )
        ],
        subtotal=100.0,
        total_gst_amount=18.0,
        total_cgst=9.0,
        total_sgst=9.0,
        total_igst=0.0,
        grand_total=118.0,
        tax_type="intra_state",
        seller_state="MAHARASHTRA",
        customer_state="MAHARASHTRA",
        determined_gst_rate=18.0,
    )


class TestInvoiceRepository:
    """Tests for InvoiceRepository."""

    def test_save_invoice(self, repository, sample_invoice):
        """Test saving an invoice."""
        saved = repository.save_invoice(sample_invoice)
        
        assert saved.invoice_id == sample_invoice.invoice_id
        assert saved.invoice_number == sample_invoice.invoice_number
        assert saved.grand_total == sample_invoice.grand_total
        
        # Verify it was stored
        retrieved = repository.get_invoice(sample_invoice.invoice_id)
        assert retrieved is not None
        assert retrieved.invoice_id == sample_invoice.invoice_id

    def test_get_invoice(self, repository, sample_invoice):
        """Test retrieving an invoice by ID."""
        repository.save_invoice(sample_invoice)
        
        retrieved = repository.get_invoice(sample_invoice.invoice_id)
        
        assert retrieved is not None
        assert retrieved.invoice_id == sample_invoice.invoice_id
        assert retrieved.grand_total == sample_invoice.grand_total

    def test_get_nonexistent_invoice(self, repository):
        """Test retrieving a non-existent invoice returns None."""
        retrieved = repository.get_invoice("NONEXISTENT")
        assert retrieved is None

    def test_get_invoice_by_number(self, repository, sample_invoice):
        """Test retrieving an invoice by invoice number."""
        repository.save_invoice(sample_invoice)
        
        retrieved = repository.get_invoice_by_number(sample_invoice.invoice_number)
        
        assert retrieved is not None
        assert retrieved.invoice_number == sample_invoice.invoice_number

    def test_update_invoice_status(self, repository, sample_invoice):
        """Test updating invoice status."""
        repository.save_invoice(sample_invoice)
        
        updated = repository.update_invoice_status(sample_invoice.invoice_id, "paid")
        
        assert updated is not None
        assert updated.status == "paid"
        
        # Verify persisted
        retrieved = repository.get_invoice(sample_invoice.invoice_id)
        assert retrieved.status == "paid"

    def test_add_upi_info(self, repository, sample_invoice):
        """Test adding UPI info to an invoice."""
        repository.save_invoice(sample_invoice)
        
        upi_info = PersistedUPIInfo(
            upi_request_id="UPI-20240115-0001",
            upi_deep_link="upi://pay?pa=merchant@upi&am=118.00",
            qr_code_data="data:image/png;base64,test",
            amount=118.0,
            currency="INR",
            merchant_name="Test Merchant",
            merchant_vpa="merchant@upi",
            transaction_note="Invoice INV-20240115-0001",
            status="pending",
            created_at="2024-01-15T10:00:00",
            expires_at="2024-01-15T10:15:00",
        )
        
        updated = repository.add_upi_info(sample_invoice.invoice_id, upi_info)
        
        assert updated is not None
        assert updated.upi_info is not None
        assert updated.upi_info.upi_request_id == "UPI-20240115-0001"
        
        # Verify persisted
        retrieved = repository.get_invoice(sample_invoice.invoice_id)
        assert retrieved.upi_info is not None
        assert retrieved.upi_info.amount == 118.0

    def test_idempotency_same_invoice(self, repository, sample_invoice):
        """Test that saving the same invoice twice returns the same invoice."""
        saved1 = repository.save_invoice(sample_invoice)
        saved2 = repository.save_invoice(sample_invoice)
        
        # Should return the same invoice (idempotent)
        assert saved1.invoice_id == saved2.invoice_id

    def test_idempotency_different_invoice_same_key(self, repository, sample_invoice):
        """Test idempotency with different invoice but same idempotency key."""
        # Save first invoice
        saved1 = repository.save_invoice(sample_invoice)
        
        # Create second invoice with same idempotency key
        invoice2 = PersistedInvoice(
            invoice_id="INV-20240115-0002",
            invoice_number="INV-20240115-0002",
            invoice_date="2024-01-15T11:00:00",
            status=InvoiceStatus.PENDING.value,
            seller=sample_invoice.seller,
            customer=sample_invoice.customer,
            items=sample_invoice.items,
            subtotal=sample_invoice.subtotal,
            total_gst_amount=sample_invoice.total_gst_amount,
            total_cgst=sample_invoice.total_cgst,
            total_sgst=sample_invoice.total_sgst,
            total_igst=sample_invoice.total_igst,
            grand_total=sample_invoice.grand_total,
            tax_type=sample_invoice.tax_type,
            seller_state=sample_invoice.seller_state,
            customer_state=sample_invoice.customer_state,
            determined_gst_rate=sample_invoice.determined_gst_rate,
            idempotency_key=saved1.idempotency_key,  # Same idempotency key
        )
        
        # Should return the first invoice (idempotent)
        saved2 = repository.save_invoice(invoice2)
        assert saved2.invoice_id == saved1.invoice_id

    def test_idempotency_claim_and_invoice_are_written_together(
        self,
        repository,
        sample_invoice,
        mock_client,
    ):
        repository.save_invoice(sample_invoice)

        record_id = f'IDEMPOTENCY#{sample_invoice.idempotency_key}'
        assert mock_client.items[sample_invoice.invoice_id]['idempotency_key']['S'] == (
            sample_invoice.idempotency_key
        )
        assert mock_client.items[record_id]['target_invoice_id']['S'] == sample_invoice.invoice_id

    def test_transaction_conflict_returns_existing_invoice(
        self,
        repository,
        sample_invoice,
    ):
        first = repository.save_invoice(sample_invoice)
        second_invoice = PersistedInvoice.from_dynamodb_item(
            sample_invoice.to_dynamodb_item()
        )
        second_invoice.invoice_id = 'INV-20240115-0002'
        second_invoice.invoice_number = 'INV-20240115-0002'

        existing = repository._write_invoice_idempotently(
            second_invoice,
            second_invoice.to_dynamodb_item(),
        )

        assert existing.invoice_id == first.invoice_id
        assert second_invoice.invoice_id not in repository.client.items

    def test_generate_idempotency_key(self, repository):
        """Test idempotency key generation."""
        data1 = {'invoice_number': 'INV-001', 'grand_total': 100.0}
        data2 = {'invoice_number': 'INV-001', 'grand_total': 100.0}
        data3 = {'invoice_number': 'INV-002', 'grand_total': 100.0}
        
        key1 = repository._generate_idempotency_key(data1)
        key2 = repository._generate_idempotency_key(data2)
        key3 = repository._generate_idempotency_key(data3)
        
        # Same data should produce same key
        assert key1 == key2
        # Different data should produce different key
        assert key1 != key3
        # Key should be 32 chars (SHA256 truncated)
        assert len(key1) == 32


class TestRepositoryGlobalFunctions:
    """Tests for global repository functions."""

    def test_get_repository(self):
        """Test getting the global repository."""
        reset_repository()
        repo = get_repository()
        assert isinstance(repo, InvoiceRepository)
        reset_repository()

    def test_set_repository(self, repository):
        """Test setting the global repository."""
        reset_repository()
        set_repository(repository)
        assert get_repository() is repository
        reset_repository()

    def test_reset_repository(self, repository):
        """Test resetting the global repository."""
        set_repository(repository)
        assert get_repository() is repository
        reset_repository()
        # After reset, get_repository should create a new one
        new_repo = get_repository()
        assert new_repo is not repository
        reset_repository()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])