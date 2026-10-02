"""
Extraction schema for INVOX.

Defines the structured contract between Bedrock and INVOX.
This is the normalized form that the frontend expects.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal


@dataclass
class ExtractionItem:
    """Individual line item in an extracted order."""
    name: str
    quantity: int
    unit_price: float  # Using float for JSON serialization, validated as positive

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'quantity': self.quantity,
            'unitPrice': self.unit_price,
        }

    def validate(self) -> List[str]:
        """Validate item fields. Returns list of error messages (empty if valid)."""
        errors = []
        if not self.name or not self.name.strip():
            errors.append("Item name is required")
        if self.quantity <= 0:
            errors.append("Quantity must be positive")
        if self.unit_price < 0:
            errors.append("Unit price cannot be negative")
        return errors


@dataclass
class BedrockExtraction:
    """
    Structured extraction result from Bedrock.
    
    This is the normalized form after parsing and validation.
    All fields are optional in the raw Bedrock response but
    required for a complete extraction.
    """
    customer: Optional[str] = None
    location: Optional[str] = None
    items: List[ExtractionItem] = field(default_factory=list)
    stated_gst_rate: Optional[float] = None
    
    # Metadata
    raw_model_output: Optional[str] = None  # For debugging
    
    def to_dict(self) -> dict:
        """Convert to dict matching frontend ExtractionResult contract."""
        return {
            'source': 'bedrock',
            'customer': self.customer or '',
            'location': self.location or '',
            'items': [item.to_dict() for item in self.items],
            'statedGstRate': self.stated_gst_rate if self.stated_gst_rate is not None else 0.0,
        }
    
    def is_complete(self) -> bool:
        """Check if all required fields are present."""
        return (
            bool(self.customer and self.customer.strip()) and
            bool(self.location and self.location.strip()) and
            len(self.items) > 0 and
            self.stated_gst_rate is not None
        )
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields."""
        missing = []
        if not self.customer or not self.customer.strip():
            missing.append('customer')
        if not self.location or not self.location.strip():
            missing.append('location')
        if len(self.items) == 0:
            missing.append('items')
        if self.stated_gst_rate is None:
            missing.append('statedGstRate')
        return missing
    
    def validate(self) -> List[str]:
        """Validate all fields. Returns list of error messages."""
        errors = []
        for item in self.items:
            errors.extend(item.validate())
        if self.stated_gst_rate is not None and (self.stated_gst_rate < 0 or self.stated_gst_rate > 100):
            errors.append("Stated GST rate must be between 0 and 100")
        return errors