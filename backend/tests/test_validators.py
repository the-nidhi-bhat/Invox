"""
Tests for input validators.
"""

from src.validators.extract import (
    validate_extract_request,
    validate_json_body,
    validate_request_size,
    MAX_REQUEST_SIZE,
    MAX_MESSAGE_LENGTH,
)


class TestValidateJsonBody:
    """Tests for JSON body validation."""

    def test_valid_json(self):
        """Valid JSON passes validation."""
        result = validate_json_body('{"message": "test"}')
        assert result.valid is True

    def test_valid_json_empty_object(self):
        """Empty JSON object passes validation."""
        result = validate_json_body('{}')
        assert result.valid is True

    def test_invalid_json(self):
        """Invalid JSON fails validation."""
        result = validate_json_body('{not valid}')
        assert result.valid is False
        assert result.error_code == 'MALFORMED_JSON'

    def test_invalid_json_unterminated_string(self):
        """Unterminated string fails validation."""
        result = validate_json_body('{"message": "test}')
        assert result.valid is False
        assert result.error_code == 'MALFORMED_JSON'

    def test_invalid_json_trailing_comma(self):
        """Trailing comma fails validation."""
        result = validate_json_body('{"message": "test",}')
        assert result.valid is False
        assert result.error_code == 'MALFORMED_JSON'


class TestValidateRequestSize:
    """Tests for request size validation."""

    def test_small_request_passes(self):
        """Small request passes size validation."""
        body = '{"message": "short"}'
        result = validate_request_size(body)
        assert result.valid is True

    def test_exact_limit_passes(self):
        """Request at exact size limit passes."""
        body = 'x' * MAX_REQUEST_SIZE
        result = validate_request_size(body)
        assert result.valid is True

    def test_over_limit_fails(self):
        """Request over size limit fails."""
        body = 'x' * (MAX_REQUEST_SIZE + 1)
        result = validate_request_size(body)
        assert result.valid is False
        assert result.error_code == 'REQUEST_TOO_LARGE'
        assert result.details['max_size_bytes'] == MAX_REQUEST_SIZE
        assert result.details['received_size_bytes'] == MAX_REQUEST_SIZE + 1

    def test_unicode_characters_counted_correctly(self):
        """Unicode characters counted as UTF-8 bytes."""
        # Each emoji is 4 bytes in UTF-8, need enough to exceed 10KB limit
        # 10KB = 10240 bytes, JSON overhead ~20 bytes, so need ~2560 emojis
        body = '{"message": "' + '🎉' * 3000 + '"}'
        result = validate_request_size(body)
        assert result.valid is False  # 3000 * 4 = 12000 bytes + overhead > 10KB
        assert result.error_code == 'REQUEST_TOO_LARGE'


class TestValidateExtractRequest:
    """Tests for extract request validation."""

    def test_valid_request(self):
        """Valid request passes all checks."""
        result = validate_extract_request({'message': 'valid message'})
        assert result.valid is True

    def test_missing_message(self):
        """Missing message field fails."""
        result = validate_extract_request({})
        assert result.valid is False
        assert result.error_code == 'MISSING_MESSAGE'

    def test_message_none(self):
        """None message fails."""
        result = validate_extract_request({'message': None})
        assert result.valid is False
        assert result.error_code == 'INVALID_MESSAGE_TYPE'

    def test_message_integer(self):
        """Integer message fails."""
        result = validate_extract_request({'message': 123})
        assert result.valid is False
        assert result.error_code == 'INVALID_MESSAGE_TYPE'
        assert result.details['received_type'] == 'int'

    def test_message_list(self):
        """List message fails."""
        result = validate_extract_request({'message': ['item1', 'item2']})
        assert result.valid is False
        assert result.error_code == 'INVALID_MESSAGE_TYPE'
        assert result.details['received_type'] == 'list'

    def test_empty_string(self):
        """Empty string fails."""
        result = validate_extract_request({'message': ''})
        assert result.valid is False
        assert result.error_code == 'EMPTY_MESSAGE'

    def test_whitespace_only(self):
        """Whitespace-only string fails."""
        result = validate_extract_request({'message': '   \n\t  '})
        assert result.valid is False
        assert result.error_code == 'EMPTY_MESSAGE'

    def test_max_length_passes(self):
        """Message at max length passes."""
        message = 'x' * MAX_MESSAGE_LENGTH
        result = validate_extract_request({'message': message})
        assert result.valid is True

    def test_over_max_length_fails(self):
        """Message over max length fails."""
        message = 'x' * (MAX_MESSAGE_LENGTH + 1)
        result = validate_extract_request({'message': message})
        assert result.valid is False
        assert result.error_code == 'MESSAGE_TOO_LONG'
        assert result.details['max_length'] == MAX_MESSAGE_LENGTH
        assert result.details['received_length'] == MAX_MESSAGE_LENGTH + 1

    def test_message_with_extra_fields_passes(self):
        """Extra fields in request are ignored (not rejected)."""
        result = validate_extract_request({
            'message': 'valid',
            'extra_field': 'ignored',
        })
        assert result.valid is True