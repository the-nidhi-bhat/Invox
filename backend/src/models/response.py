"""
Response models for INVOX API.

Defines the structure of successful and error responses.
"""

from dataclasses import dataclass, asdict
from typing import Any, Optional, List
import json


@dataclass
class ExtractionItem:
    """Individual line item in an extracted order."""
    name: str
    quantity: int
    unit_price: float

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'quantity': self.quantity,
            'unitPrice': self.unit_price,
        }


@dataclass
class ExtractResponse:
    """Successful response for POST /extract endpoint."""
    source: str  # 'mock' | 'bedrock' | 'placeholder'
    customer: str
    location: str
    items: List[ExtractionItem]
    stated_gst_rate: float

    def to_dict(self) -> dict:
        return {
            'source': self.source,
            'customer': self.customer,
            'location': self.location,
            'items': [item.to_dict() for item in self.items],
            'statedGstRate': self.stated_gst_rate,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class HealthResponse:
    """Successful response for GET /health endpoint."""
    status: str
    service: str

    def to_dict(self) -> dict:
        return {'status': self.status, 'service': self.service}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class ErrorResponse:
    """Standard error response structure."""
    error: str
    code: str
    details: Optional[dict] = None

    def to_dict(self) -> dict:
        result = {'error': self.error, 'code': self.code}
        if self.details:
            result['details'] = self.details
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())