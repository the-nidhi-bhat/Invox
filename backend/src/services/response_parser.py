"""
Bedrock Response Parser for INVOX.

Parses and validates raw Bedrock model output into structured extraction.
Handles malformed responses, missing fields, and invalid data safely.
"""

import json
import logging
from typing import Optional, List
from dataclasses import dataclass

from src.models.extraction import ExtractionItem, BedrockExtraction

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """Result of parsing Bedrock response."""
    success: bool
    extraction: Optional[BedrockExtraction] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    raw_content: Optional[str] = None


def parse_bedrock_response(content: str) -> ParseResult:
    """
    Parse raw Bedrock model output into structured extraction.
    
    Args:
        content: Raw text content from Bedrock response
        
    Returns:
        ParseResult with success status and extraction or error details
    """
    if not content or not content.strip():
        return ParseResult(
            success=False,
            error_code='EMPTY_MODEL_OUTPUT',
            error_message='Bedrock returned empty response',
            raw_content=content,
        )
    
    # Try to extract JSON from the response
    # Model might wrap JSON in markdown code blocks or include extra text
    json_str = _extract_json(content)
    if not json_str:
        return ParseResult(
            success=False,
            error_code='NO_JSON_FOUND',
            error_message='Could not find valid JSON in Bedrock response',
            raw_content=content,
        )
    
    # Parse JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Bedrock JSON: {e}")
        return ParseResult(
            success=False,
            error_code='INVALID_MODEL_JSON',
            error_message='Bedrock returned invalid JSON',
            raw_content=content,
        )
    
    # Validate and convert to BedrockExtraction
    extraction = _convert_to_extraction(data)
    if extraction is None:
        return ParseResult(
            success=False,
            error_code='INVALID_EXTRACTION_STRUCTURE',
            error_message='Bedrock response missing required fields or has invalid structure',
            raw_content=content,
        )
    
    # Store raw model output for debugging
    extraction.raw_model_output = content
    
    return ParseResult(
        success=True,
        extraction=extraction,
        raw_content=content,
    )


def _extract_json(text: str) -> Optional[str]:
    """
    Extract JSON string from text that might contain markdown or extra content.
    
    Handles:
    - Plain JSON
    - JSON in markdown code blocks (```json ... ```)
    - JSON with leading/trailing text
    """
    text = text.strip()
    
    # Try direct JSON first
    if text.startswith('{') and text.endswith('}'):
        return text
    
    # Try markdown code block
    import re
    code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if code_block_match:
        return code_block_match.group(1)
    
    # Try to find JSON-like structure
    json_match = re.search(r'(\{.*\})', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    return None


def _convert_to_extraction(data: dict) -> Optional[BedrockExtraction]:
    """
    Convert parsed JSON dict to BedrockExtraction with validation.
    
    Returns None if required structure is missing or invalid.
    """
    if not isinstance(data, dict):
        return None
    
    # Parse customer
    customer = data.get('customer')
    if customer is not None and not isinstance(customer, str):
        customer = str(customer)
    
    # Parse location
    location = data.get('location')
    if location is not None and not isinstance(location, str):
        location = str(location)
    
    # Parse items
    items = []
    raw_items = data.get('items', [])
    if isinstance(raw_items, list):
        for item_data in raw_items:
            item = _parse_item(item_data)
            if item:
                items.append(item)
    
    # Parse stated_gst_rate
    stated_gst_rate = data.get('stated_gst_rate')
    if stated_gst_rate is not None:
        try:
            stated_gst_rate = float(stated_gst_rate)
        except (ValueError, TypeError):
            stated_gst_rate = None
    
    return BedrockExtraction(
        customer=customer,
        location=location,
        items=items,
        stated_gst_rate=stated_gst_rate,
    )


def _parse_item(item_data: dict) -> Optional[ExtractionItem]:
    """Parse a single item from dict, with validation."""
    if not isinstance(item_data, dict):
        return None
    
    name = item_data.get('name')
    if name is not None and not isinstance(name, str):
        name = str(name)
    
    quantity = item_data.get('quantity')
    if quantity is not None:
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = None
    
    unit_price = item_data.get('unit_price')
    if unit_price is not None:
        try:
            unit_price = float(unit_price)
        except (ValueError, TypeError):
            unit_price = None
    
    # Only create item if we have at least a name
    if name and name.strip():
        return ExtractionItem(
            name=name.strip(),
            quantity=quantity if quantity is not None and quantity > 0 else 1,
            unit_price=unit_price if unit_price is not None and unit_price >= 0 else 0.0,
        )
    
    return None


def validate_extraction(extraction: BedrockExtraction) -> List[str]:
    """
    Validate a parsed extraction for business rules.
    
    Returns list of validation errors (empty if valid).
    """
    errors = []
    
    # Check completeness
    missing = extraction.get_missing_fields()
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")
    
    # Validate individual fields
    errors.extend(extraction.validate())
    
    return errors