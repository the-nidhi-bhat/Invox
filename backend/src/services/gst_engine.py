"""
Deterministic GST Engine for INVOX.

This module provides deterministic GST calculation based on explicit rules.
It does NOT rely on AI output for financial calculations.

Core principle: AI proposes. Rules decide. You stay in control.

MVP Ruleset:
- This is a minimal demonstration ruleset, not a complete Indian GST database.
- Not authoritative legal/tax advice.
- Product categories map to standard GST rates for demonstration.
"""

from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum


class TaxType(Enum):
    """Type of tax applicable based on jurisdiction."""
    INTRA_STATE = "intra_state"  # CGST + SGST
    INTER_STATE = "inter_state"  # IGST


@dataclass
class ProductGSTRule:
    """GST rule for a product/category."""
    product_name: str
    category: str
    gst_rate: Decimal  # e.g., Decimal('18') for 18%


@dataclass
class GSTEngineConfig:
    """Configuration for the GST engine."""
    seller_state: str
    product_rules: List[ProductGSTRule] = field(default_factory=list)
    default_gst_rate: Decimal = Decimal('18')  # Fallback for unknown products
    
    # Build lookup dict for O(1) access
    def __post_init__(self):
        self._product_lookup: Dict[str, ProductGSTRule] = {}
        for rule in self.product_rules:
            key = rule.product_name.lower().strip()
            self._product_lookup[key] = rule
    
    def get_gst_rate(self, product_name: str) -> Decimal:
        """Get GST rate for a product, with fallback to default."""
        key = product_name.lower().strip()
        if key in self._product_lookup:
            return self._product_lookup[key].gst_rate
        return self.default_gst_rate


# MVP Product GST Rules (demonstration ruleset)
# This is a minimal ruleset for demonstration, not a complete GST database.
DEFAULT_PRODUCT_RULES = [
    ProductGSTRule(product_name="mouse", category="electronics", gst_rate=Decimal('18')),
    ProductGSTRule(product_name="keyboard", category="electronics", gst_rate=Decimal('18')),
    ProductGSTRule(product_name="monitor", category="electronics", gst_rate=Decimal('18')),
    ProductGSTRule(product_name="laptop", category="electronics", gst_rate=Decimal('18')),
    ProductGSTRule(product_name="mobile", category="electronics", gst_rate=Decimal('18')),
    ProductGSTRule(product_name="phone", category="electronics", gst_rate=Decimal('18')),
    ProductGSTRule(product_name="headphones", category="electronics", gst_rate=Decimal('18')),
    ProductGSTRule(product_name="charger", category="electronics", gst_rate=Decimal('18')),
    ProductGSTRule(product_name="cable", category="electronics", gst_rate=Decimal('18')),
    ProductGSTRule(product_name="pen", category="stationery", gst_rate=Decimal('12')),
    ProductGSTRule(product_name="notebook", category="stationery", gst_rate=Decimal('12')),
    ProductGSTRule(product_name="paper", category="stationery", gst_rate=Decimal('12')),
    ProductGSTRule(product_name="pencil", category="stationery", gst_rate=Decimal('12')),
    ProductGSTRule(product_name="eraser", category="stationery", gst_rate=Decimal('12')),
    ProductGSTRule(product_name="rice", category="food", gst_rate=Decimal('5')),
    ProductGSTRule(product_name="wheat", category="food", gst_rate=Decimal('5')),
    ProductGSTRule(product_name="sugar", category="food", gst_rate=Decimal('5')),
    ProductGSTRule(product_name="salt", category="food", gst_rate=Decimal('0')),
    ProductGSTRule(product_name="milk", category="food", gst_rate=Decimal('5')),
]


# Default seller state for MVP
DEFAULT_SELLER_STATE = "MAHARASHTRA"


def create_default_config() -> GSTEngineConfig:
    """Create GST engine config with default MVP rules."""
    return GSTEngineConfig(
        seller_state=DEFAULT_SELLER_STATE,
        product_rules=DEFAULT_PRODUCT_RULES,
        default_gst_rate=Decimal('18')
    )


@dataclass
class GSTLineItem:
    """Input item for GST calculation."""
    name: str
    quantity: int
    unit_price: Decimal
    stated_gst_rate: Optional[Decimal] = None


@dataclass
class CalculatedItem:
    """Item with calculated GST breakdown."""
    name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    gst_rate: Decimal
    gst_amount: Decimal
    cgst_rate: Decimal
    cgst_amount: Decimal
    sgst_rate: Decimal
    sgst_amount: Decimal
    igst_rate: Decimal
    igst_amount: Decimal
    stated_gst_rate: Optional[Decimal]
    gst_mismatch: bool
    tax_type: TaxType


@dataclass
class GSTCalculationResult:
    """Complete GST calculation result."""
    items: List[CalculatedItem]
    total_subtotal: Decimal
    total_gst_amount: Decimal
    total_cgst: Decimal
    total_sgst: Decimal
    total_igst: Decimal
    grand_total: Decimal
    tax_type: TaxType
    seller_state: str
    customer_state: Optional[str]
    stated_gst_rate: Optional[Decimal]
    determined_gst_rate: Decimal  # Primary rate used (if uniform)
    gst_mismatch: bool
    mismatch_details: List[str]


# Quantization for currency (2 decimal places)
CURRENCY_QUANTUM = Decimal('0.01')


def quantize_currency(value: Decimal) -> Decimal:
    """Quantize to 2 decimal places using banker's rounding (ROUND_HALF_UP)."""
    return value.quantize(CURRENCY_QUANTUM, rounding=ROUND_HALF_UP)


def calculate_gst_for_item(
    item: GSTLineItem,
    config: GSTEngineConfig,
    customer_state: Optional[str]
) -> CalculatedItem:
    """
    Calculate GST for a single line item.
    
    Args:
        item: The line item to calculate GST for
        config: GST engine configuration
        customer_state: Customer's state for intra/inter-state determination
    
    Returns:
        CalculatedItem with full GST breakdown
    """
    # Get determined GST rate from rules (NOT from AI)
    determined_rate = config.get_gst_rate(item.name)
    
    # Determine tax type based on states
    is_intra_state = False
    if customer_state:
        is_intra_state = customer_state.strip().upper() == config.seller_state.strip().upper()
    
    tax_type = TaxType.INTRA_STATE if is_intra_state else TaxType.INTER_STATE
    
    # Calculate subtotal
    subtotal = quantize_currency(item.quantity * item.unit_price)
    
    # Calculate GST amount based on determined rate
    gst_rate = determined_rate
    gst_amount = quantize_currency(subtotal * (gst_rate / Decimal('100')))
    
    # Split CGST/SGST or IGST based on tax type
    if tax_type == TaxType.INTRA_STATE:
        cgst_rate = quantize_currency(gst_rate / Decimal('2'))
        sgst_rate = quantize_currency(gst_rate / Decimal('2'))
        cgst_amount = quantize_currency(subtotal * (cgst_rate / Decimal('100')))
        sgst_amount = quantize_currency(subtotal * (sgst_rate / Decimal('100')))
        igst_rate = Decimal('0')
        igst_amount = Decimal('0')
    else:  # INTER_STATE
        cgst_rate = Decimal('0')
        sgst_rate = Decimal('0')
        cgst_amount = Decimal('0')
        sgst_amount = Decimal('0')
        igst_rate = gst_rate
        igst_amount = gst_amount
    
    # Check for mismatch with stated GST rate
    stated_rate = item.stated_gst_rate
    gst_mismatch = False
    if stated_rate is not None and stated_rate != determined_rate:
        gst_mismatch = True
    
    return CalculatedItem(
        name=item.name,
        quantity=item.quantity,
        unit_price=item.unit_price,
        subtotal=subtotal,
        gst_rate=gst_rate,
        gst_amount=gst_amount,
        cgst_rate=cgst_rate,
        cgst_amount=cgst_amount,
        sgst_rate=sgst_rate,
        sgst_amount=sgst_amount,
        igst_rate=igst_rate,
        igst_amount=igst_amount,
        stated_gst_rate=stated_rate,
        gst_mismatch=gst_mismatch,
        tax_type=tax_type,
    )


def calculate_gst(
    items: List[GSTLineItem],
    customer_state: Optional[str],
    config: Optional[GSTEngineConfig] = None
) -> GSTCalculationResult:
    """
    Calculate GST for a complete order.
    
    Args:
        items: List of line items
        customer_state: Customer's state for intra/inter-state determination
        config: GST engine configuration (uses default if not provided)
    
    Returns:
        Complete GST calculation result
    """
    if config is None:
        config = create_default_config()
    
    if not items:
        raise ValueError("At least one item is required for GST calculation")
    
    calculated_items = []
    mismatch_details = []
    all_match = True
    
    for item in items:
        calculated = calculate_gst_for_item(item, config, customer_state)
        calculated_items.append(calculated)
        
        if calculated.gst_mismatch:
            all_match = False
            stated = calculated.stated_gst_rate
            determined = calculated.gst_rate
            mismatch_details.append(
                f"Item '{item.name}': stated {stated}%, rules determine {determined}%"
            )
    
    # Calculate totals
    total_subtotal = sum((item.subtotal for item in calculated_items), Decimal('0'))
    total_gst_amount = sum((item.gst_amount for item in calculated_items), Decimal('0'))
    total_cgst = sum((item.cgst_amount for item in calculated_items), Decimal('0'))
    total_sgst = sum((item.sgst_amount for item in calculated_items), Decimal('0'))
    total_igst = sum((item.igst_amount for item in calculated_items), Decimal('0'))
    grand_total = quantize_currency(total_subtotal + total_gst_amount)
    
    # Determine overall tax type (use first item's type as reference)
    tax_type = calculated_items[0].tax_type if calculated_items else TaxType.INTRA_STATE
    
    # Check if all items have same tax type
    for item in calculated_items:
        if item.tax_type != tax_type:
            # Mixed scenario - this shouldn't happen in normal use but handle gracefully
            pass
    
    # Determine stated GST rate (use first item's stated rate if all same, else None)
    stated_rates = [item.stated_gst_rate for item in calculated_items if item.stated_gst_rate is not None]
    stated_gst_rate = stated_rates[0] if stated_rates and len(set(stated_rates)) == 1 else None
    
    # Primary determined rate (use first item's rate if all same)
    determined_rates = [item.gst_rate for item in calculated_items]
    determined_gst_rate = determined_rates[0] if len(set(determined_rates)) == 1 else determined_rates[0]
    
    gst_mismatch = not all_match
    
    return GSTCalculationResult(
        items=calculated_items,
        total_subtotal=quantize_currency(total_subtotal),
        total_gst_amount=quantize_currency(total_gst_amount),
        total_cgst=quantize_currency(total_cgst),
        total_sgst=quantize_currency(total_sgst),
        total_igst=quantize_currency(total_igst),
        grand_total=grand_total,
        tax_type=tax_type,
        seller_state=config.seller_state,
        customer_state=customer_state,
        stated_gst_rate=stated_gst_rate,
        determined_gst_rate=determined_gst_rate,
        gst_mismatch=gst_mismatch,
        mismatch_details=mismatch_details,
    )