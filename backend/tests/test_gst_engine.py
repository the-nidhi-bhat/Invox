"""
Tests for GST Engine.
"""

from decimal import Decimal
from src.services.gst_engine import (
    calculate_gst,
    create_default_config,
    GSTLineItem,
    GSTEngineConfig,
    ProductGSTRule,
    TaxType,
    DEFAULT_SELLER_STATE,
    calculate_gst_for_item,
)


class TestGSTEngineConfig:
    """Tests for GSTEngineConfig."""

    def test_default_config_creation(self):
        """Default config is created with correct defaults."""
        config = create_default_config()
        assert config.seller_state == DEFAULT_SELLER_STATE
        assert config.default_gst_rate == Decimal('18')
        assert len(config.product_rules) > 0

    def test_product_lookup_case_insensitive(self):
        """Product lookup is case-insensitive."""
        config = create_default_config()
        assert config.get_gst_rate('MOUSE') == Decimal('18')
        assert config.get_gst_rate('Mouse') == Decimal('18')
        assert config.get_gst_rate('mouse') == Decimal('18')

    def test_unknown_product_uses_default(self):
        """Unknown products use default GST rate."""
        config = create_default_config()
        assert config.get_gst_rate('unknown_product_xyz') == Decimal('18')


class TestIntraStateCalculation:
    """Tests for intra-state GST calculation (same state)."""

    def test_intra_state_cgst_sgst_split(self):
        """Intra-state splits GST equally into CGST and SGST."""
        config = create_default_config()
        item = GSTLineItem(
            name="mouse",
            quantity=10,
            unit_price=Decimal('100'),
            stated_gst_rate=None,
        )
        
        result = calculate_gst_for_item(item, config, "MAHARASHTRA")
        
        assert result.tax_type == TaxType.INTRA_STATE
        assert result.gst_rate == Decimal('18')
        assert result.cgst_rate == Decimal('9')
        assert result.sgst_rate == Decimal('9')
        assert result.igst_rate == Decimal('0')
        # 10 * 100 = 1000 subtotal
        # 18% of 1000 = 180 GST
        # CGST = 9% of 1000 = 90
        # SGST = 9% of 1000 = 90
        assert result.subtotal == Decimal('1000')
        assert result.gst_amount == Decimal('180')
        assert result.cgst_amount == Decimal('90')
        assert result.sgst_amount == Decimal('90')
        assert result.igst_amount == Decimal('0')

    def test_intra_state_with_quantity(self):
        """Intra-state calculation with quantity > 1."""
        config = create_default_config()
        item = GSTLineItem(
            name="pen",
            quantity=50,
            unit_price=Decimal('10'),
            stated_gst_rate=None,
        )
        
        result = calculate_gst_for_item(item, config, "MAHARASHTRA")
        
        # 50 * 10 = 500 subtotal
        # 12% of 500 = 60 GST
        # CGST = 6% of 500 = 30
        # SGST = 6% of 500 = 30
        assert result.gst_rate == Decimal('12')
        assert result.subtotal == Decimal('500')
        assert result.gst_amount == Decimal('60')
        assert result.cgst_amount == Decimal('30')
        assert result.sgst_amount == Decimal('30')


class TestInterStateCalculation:
    """Tests for inter-state GST calculation (different states)."""

    def test_inter_state_igst_only(self):
        """Inter-state uses only IGST, no CGST/SGST."""
        config = create_default_config()
        item = GSTLineItem(
            name="mouse",
            quantity=10,
            unit_price=Decimal('100'),
            stated_gst_rate=None,
        )
        
        result = calculate_gst_for_item(item, config, "KARNATAKA")
        
        assert result.tax_type == TaxType.INTER_STATE
        assert result.gst_rate == Decimal('18')
        assert result.cgst_rate == Decimal('0')
        assert result.sgst_rate == Decimal('0')
        assert result.igst_rate == Decimal('18')
        # 10 * 100 = 1000 subtotal
        # 18% of 1000 = 180 IGST
        assert result.subtotal == Decimal('1000')
        assert result.gst_amount == Decimal('180')
        assert result.cgst_amount == Decimal('0')
        assert result.sgst_amount == Decimal('0')
        assert result.igst_amount == Decimal('180')

    def test_case_insensitive_state_comparison(self):
        """State comparison is case-insensitive."""
        config = create_default_config()
        item = GSTLineItem(
            name="mouse",
            quantity=1,
            unit_price=Decimal('100'),
        )
        
        result = calculate_gst_for_item(item, config, "maharashtra")
        
        assert result.tax_type == TaxType.INTRA_STATE


class TestGSTMismatchDetection:
    """Tests for GST mismatch detection between stated and determined rates."""

    def test_mismatch_detected(self):
        """Mismatch detected when stated != determined."""
        config = create_default_config()
        item = GSTLineItem(
            name="mouse",
            quantity=1,
            unit_price=Decimal('100'),
            stated_gst_rate=Decimal('5'),
        )
        
        result = calculate_gst_for_item(item, config, "MAHARASHTRA")
        
        assert result.gst_mismatch is True
        assert result.stated_gst_rate == Decimal('5')
        assert result.gst_rate == Decimal('18')

    def test_no_mismatch_when_equal(self):
        """No mismatch when stated == determined."""
        config = create_default_config()
        item = GSTLineItem(
            name="mouse",
            quantity=1,
            unit_price=Decimal('100'),
            stated_gst_rate=Decimal('18'),
        )
        
        result = calculate_gst_for_item(item, config, "MAHARASHTRA")
        
        assert result.gst_mismatch is False
        assert result.stated_gst_rate == Decimal('18')
        assert result.gst_rate == Decimal('18')

    def test_no_mismatch_when_no_stated_rate(self):
        """No mismatch when stated rate is None."""
        config = create_default_config()
        item = GSTLineItem(
            name="mouse",
            quantity=1,
            unit_price=Decimal('100'),
            stated_gst_rate=None,
        )
        
        result = calculate_gst_for_item(item, config, "MAHARASHTRA")
        
        assert result.gst_mismatch is False
        assert result.stated_gst_rate is None


class TestMultipleItems:
    """Tests for multiple items calculation."""

    def test_multiple_items_same_state(self):
        """Multiple items with same tax type."""
        config = create_default_config()
        items = [
            GSTLineItem(name="mouse", quantity=10, unit_price=Decimal('100')),
            GSTLineItem(name="keyboard", quantity=5, unit_price=Decimal('200')),
        ]
        
        result = calculate_gst(items, "MAHARASHTRA", config)
        
        assert len(result.items) == 2
        assert result.tax_type == TaxType.INTRA_STATE
        # mouse: 10*100=1000, keyboard: 5*200=1000
        # total = 2000
        # GST = 18% of 2000 = 360
        assert result.total_subtotal == Decimal('2000')
        assert result.total_gst_amount == Decimal('360')
        assert result.grand_total == Decimal('2360')

    def test_multiple_items_different_categories(self):
        """Multiple items with different GST rates."""
        config = create_default_config()
        items = [
            GSTLineItem(name="mouse", quantity=10, unit_price=Decimal('100')),  # 18%
            GSTLineItem(name="pen", quantity=100, unit_price=Decimal('10')),     # 12%
        ]
        
        result = calculate_gst(items, "MAHARASHTRA", config)
        
        assert len(result.items) == 2
        # mouse: 10*100=1000 @ 18% = 180
        # pen: 100*10=1000 @ 12% = 120
        # total = 2000
        # GST = 180 + 120 = 300
        assert result.total_subtotal == Decimal('2000')
        assert result.total_gst_amount == Decimal('300')
        assert result.grand_total == Decimal('2300')


class TestCalculationPrecision:
    """Tests for Decimal precision and rounding."""

    def test_decimal_precision_no_float_errors(self):
        """Calculations use Decimal to avoid floating-point errors."""
        config = create_default_config()
        item = GSTLineItem(
            name="mouse",
            quantity=3,
            unit_price=Decimal('33.33'),
        )
        
        result = calculate_gst_for_item(item, config, "MAHARASHTRA")
        
        # 3 * 33.33 = 99.99
        # 18% of 99.99 = 17.9982 -> rounded to 18.00
        assert result.subtotal == Decimal('99.99')
        assert result.gst_amount == Decimal('18.00')

    def test_rounding_half_up(self):
        """Rounding uses ROUND_HALF_UP for currency."""
        from src.services.gst_engine import quantize_currency
        from decimal import Decimal, ROUND_HALF_UP
        
        # 0.005 should round to 0.01 (half up)
        assert quantize_currency(Decimal('0.005')) == Decimal('0.01')
        # 0.004 should round to 0.00
        assert quantize_currency(Decimal('0.004')) == Decimal('0.00')
        # 10.005 should round to 10.01
        assert quantize_currency(Decimal('10.005')) == Decimal('10.01')


class TestGSTCalculationResult:
    """Tests for complete GST calculation result."""

    def test_complete_result_structure(self):
        """Result contains all required fields."""
        config = create_default_config()
        items = [
            GSTLineItem(name="mouse", quantity=10, unit_price=Decimal('100')),
        ]
        
        result = calculate_gst(items, "MAHARASHTRA", config)
        
        assert result.items is not None
        assert len(result.items) == 1
        assert result.total_subtotal == Decimal('1000')
        assert result.total_gst_amount == Decimal('180')
        assert result.total_cgst == Decimal('90')
        assert result.total_sgst == Decimal('90')
        assert result.total_igst == Decimal('0')
        assert result.grand_total == Decimal('1180')
        assert result.tax_type == TaxType.INTRA_STATE
        assert result.seller_state == DEFAULT_SELLER_STATE
        assert result.customer_state == "MAHARASHTRA"
        assert result.gst_mismatch is False
        assert result.mismatch_details == []

    def test_inter_state_result(self):
        """Result for inter-state order."""
        config = create_default_config()
        items = [
            GSTLineItem(name="mouse", quantity=10, unit_price=Decimal('100')),
        ]
        
        result = calculate_gst(items, "KARNATAKA", config)
        
        assert result.tax_type == TaxType.INTER_STATE
        assert result.total_cgst == Decimal('0')
        assert result.total_sgst == Decimal('0')
        assert result.total_igst == Decimal('180')

    def test_mismatch_details_in_result(self):
        """Mismatch details are included in result."""
        config = create_default_config()
        items = [
            GSTLineItem(name="mouse", quantity=1, unit_price=Decimal('100'), stated_gst_rate=Decimal('5')),
        ]
        
        result = calculate_gst(items, "MAHARASHTRA", config)
        
        assert result.gst_mismatch is True
        assert len(result.mismatch_details) == 1
        assert "mouse" in result.mismatch_details[0]
        assert "5" in result.mismatch_details[0]
        assert "18" in result.mismatch_details[0]

    def test_determined_gst_rate_in_result(self):
        """Determined GST rate is included in result."""
        config = create_default_config()
        items = [
            GSTLineItem(name="mouse", quantity=1, unit_price=Decimal('100')),
        ]
        
        result = calculate_gst(items, "MAHARASHTRA", config)
        
        assert result.determined_gst_rate == Decimal('18')

    def test_stated_gst_rate_in_result(self):
        """Stated GST rate is included when uniform."""
        config = create_default_config()
        items = [
            GSTLineItem(name="mouse", quantity=1, unit_price=Decimal('100'), stated_gst_rate=Decimal('5')),
        ]
        
        result = calculate_gst(items, "MAHARASHTRA", config)
        
        assert result.stated_gst_rate == Decimal('5')


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_items_raises_error(self):
        """Empty items list raises ValueError."""
        config = create_default_config()
        items = []
        
        try:
            calculate_gst(items, "MAHARASHTRA", config)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "at least one item" in str(e).lower()

    def test_unknown_product_uses_default_rate(self):
        """Unknown product uses default GST rate."""
        config = create_default_config()
        item = GSTLineItem(
            name="unknown_product_xyz",
            quantity=1,
            unit_price=Decimal('100'),
        )
        
        result = calculate_gst_for_item(item, config, "MAHARASHTRA")
        
        assert result.gst_rate == Decimal('18')

    def test_zero_quantity_not_allowed(self):
        """Zero quantity should be caught by validation (not tested here as it's a validator concern)."""
        # This is handled by the validator, not the engine
        pass

    def test_different_state_case_variations(self):
        """Various state name formats work."""
        config = create_default_config()
        item = GSTLineItem(name="mouse", quantity=1, unit_price=Decimal('100'))
        
        # All these should be intra-state
        for state in ["MAHARASHTRA", "maharashtra", "Maharashtra", "MaHaRaShTrA"]:
            result = calculate_gst_for_item(item, config, state)
            assert result.tax_type == TaxType.INTRA_STATE, f"Failed for {state}"


class TestTaxTypeEnum:
    """Tests for TaxType enum."""

    def test_tax_type_values(self):
        assert TaxType.INTRA_STATE.value == "intra_state"
        assert TaxType.INTER_STATE.value == "inter_state"

    def test_tax_type_in_calculated_item(self):
        """CalculatedItem has correct tax_type."""
        config = create_default_config()
        item = GSTLineItem(name="mouse", quantity=1, unit_price=Decimal('100'))
        
        intra = calculate_gst_for_item(item, config, "MAHARASHTRA")
        inter = calculate_gst_for_item(item, config, "KARNATAKA")
        
        assert intra.tax_type == TaxType.INTRA_STATE
        assert inter.tax_type == TaxType.INTER_STATE