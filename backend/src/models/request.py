"""
Request models for INVOX API.

Defines the expected request payloads for each endpoint.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtractRequest:
    """Request payload for POST /extract endpoint."""
    message: str

    @classmethod
    def from_dict(cls, data: dict) -> 'ExtractRequest':
        """Create ExtractRequest from dictionary (e.g., parsed JSON)."""
        return cls(message=data.get('message', ''))


@dataclass
class HealthRequest:
    """Request payload for GET /health endpoint (empty)."""
    pass