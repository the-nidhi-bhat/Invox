"""
Tests for GST calculation validators.
"""

from src.validators.gst import validate_gst_request


class TestValidateGSTRequest:
    """Tests for GST calculation request validation."""

    def test_valid_request(self):
        """Valid request passes validation."""
        data = {
            'items': [
                {'name': 'mouse', 'quantity': 10, 'unit_price': 100},
            ],
            'customer_state': 'MAHARASHTRA',
        }
        result = validate_gst_request(data)
        assert result.valid is True

    def test_valid_request_without_customer_state(self):
        """Valid request without customer_state passes."""
        data = {
            'items': [
                {'name': 'mouse', 'quantity': 10, 'unit_price': 100},
            ],
        }
        result = validate_gst_request(data)
        assert result.valid is True

    def test_valid_request_with_stated_gst_rate(self):
        """Valid request with stated_gst_rate passes."""
        data = {
            'items': [
                {'name': 'mouse', 'quantity': 10, 'unit_price': 100, 'stated_gst_rate': 5},
            ],
        }
        result = validate_gst_request(data)
        assert result.valid is True

    def test_missing_items(self):
        """Missing items field fails."""
        data = {'customer_state': 'MAHARASHTRA'}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'MISSING_ITEMS'

    def test_items_not_list(self):
        """Items not a list fails."""
        data = {'items': 'not a list'}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_ITEMS_TYPE'

    def test_empty_items(self):
        """Empty items list fails."""
        data = {'items': []}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'EMPTY_ITEMS'

    def test_too_many_items(self):
        """Too many items fails."""
        data = {'items': [{'name': f'item{i}', 'quantity': 1, 'unit_price': 100} for i in range(21)]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'TOO_MANY_ITEMS'
        assert result.details['max_items'] == 20

    def test_item_not_object(self):
        """Item not an object fails."""
        data = {'items': ['not an object']}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_ITEM_TYPE'

    def test_missing_item_name(self):
        """Missing item name fails."""
        data = {'items': [{'quantity': 1, 'unit_price': 100}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'MISSING_ITEM_NAME'

    def test_invalid_item_name_type(self):
        """Item name not string fails."""
        data = {'items': [{'name': 123, 'quantity': 1, 'unit_price': 100}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_ITEM_NAME_TYPE'

    def test_empty_item_name(self):
        """Empty item name fails."""
        data = {'items': [{'name': '', 'quantity': 1, 'unit_price': 100}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'EMPTY_ITEM_NAME'

    def test_missing_quantity(self):
        """Missing quantity fails."""
        data = {'items': [{'name': 'mouse', 'unit_price': 100}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'MISSING_QUANTITY'

    def test_invalid_quantity_type(self):
        """Quantity not a number fails."""
        data = {'items': [{'name': 'mouse', 'quantity': 'abc', 'unit_price': 100}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_QUANTITY_TYPE'

    def test_quantity_not_integer(self):
        """Non-integer quantity fails."""
        data = {'items': [{'name': 'mouse', 'quantity': 1.5, 'unit_price': 100}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_QUANTITY'

    def test_zero_quantity(self):
        """Zero quantity fails."""
        data = {'items': [{'name': 'mouse', 'quantity': 0, 'unit_price': 100}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_QUANTITY'

    def test_negative_quantity(self):
        """Negative quantity fails."""
        data = {'items': [{'name': 'mouse', 'quantity': -1, 'unit_price': 100}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_QUANTITY'

    def test_missing_unit_price(self):
        """Missing unit_price fails."""
        data = {'items': [{'name': 'mouse', 'quantity': 1}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'MISSING_UNIT_PRICE'

    def test_invalid_unit_price_type(self):
        """Unit price not a number fails."""
        data = {'items': [{'name': 'mouse', 'quantity': 1, 'unit_price': 'abc'}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_UNIT_PRICE_TYPE'

    def test_negative_unit_price(self):
        """Negative unit_price fails."""
        data = {'items': [{'name': 'mouse', 'quantity': 1, 'unit_price': -10}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_UNIT_PRICE'

    def test_invalid_stated_gst_type(self):
        """Stated GST rate not a number fails."""
        data = {'items': [{'name': 'mouse', 'quantity': 1, 'unit_price': 100, 'stated_gst_rate': 'abc'}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_STATED_GST_TYPE'

    def test_negative_stated_gst(self):
        """Negative stated GST rate fails."""
        data = {'items': [{'name': 'mouse', 'quantity': 1, 'unit_price': 100, 'stated_gst_rate': -5}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_STATED_GST_RATE'

    def test_stated_gst_over_100(self):
        """Stated GST rate over 100 fails."""
        data = {'items': [{'name': 'mouse', 'quantity': 1, 'unit_price': 100, 'stated_gst_rate': 150}]}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_STATED_GST_RATE'

    def test_invalid_customer_state_type(self):
        """Customer state not a string fails."""
        data = {'items': [{'name': 'mouse', 'quantity': 1, 'unit_price': 100}], 'customer_state': 123}
        result = validate_gst_request(data)
        assert result.valid is False
        assert result.error_code == 'INVALID_CUSTOMER_STATE_TYPE'