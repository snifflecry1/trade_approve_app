from app.helper import mappings
from app.services.validations import Validator
import pytest


class TestValidator:
    @pytest.mark.parametrize(
        "invalid_param, mapping",
        [
            ("INVALID_DIRECTION", mappings.direction_stubs),
            ("INVALID_STYLE", mappings.style_stubs),
            ("INVALID_CURRENCY", mappings.currency_stubs),
        ],
    )
    def test_parse_enum_field_invalid_raises_value_error(self, invalid_param, mapping):
        validator = Validator()
        invalid_direction = "UPWARDS"
        try:
            validator.parse_enum_field(
                "test",
                invalid_direction,
                mappings.direction_stubs
            )
            assert False, "Expected ValueError was not raised"
        except KeyError as e:
            assert str(e) == f"'Invalid test: {invalid_direction}'"

    @pytest.mark.parametrize(
        "valid_param, mapping",
        [
            ("BUY", mappings.direction_stubs),
            ("FORWARD", mappings.style_stubs),
            ("EUR", mappings.currency_stubs),
        ],
    )    
    def test_parse_enum_field_valid(self, valid_param, mapping):
        validator = Validator()
        result = validator.parse_enum_field(
            "test",
            valid_param,
            mapping
        )
        assert result == mapping[valid_param]
    
    def test_parse_draft_inputs_valid(self):
        validator = Validator()
        direction_str = "BUY"
        style_str = "FORWARD"
        notion_curr_str = "USD"
        underlying_strs = ["USD", "EUR"]

        direction, style, notion_curr, underlying = validator.parse_draft_inputs(
            direction_str,
            style_str,
            notion_curr_str,
            underlying_strs
        )

        assert direction == mappings.direction_stubs[direction_str]
        assert style == mappings.style_stubs[style_str]
        assert notion_curr == mappings.currency_stubs[notion_curr_str]
        assert underlying == [
            mappings.currency_stubs[currency_str] for currency_str in underlying_strs
        ]

    def test_parse_draft_inputs_invalid_raises_value_error(self):
        validator = Validator()
        direction_str = "INVALID_DIRECTION"
        style_str = "FORWARD"
        notion_curr_str = "USD"
        underlying_strs = ["USD", "EUR"]

        try:
            validator.parse_draft_inputs(
                direction_str,
                style_str,
                notion_curr_str,
                underlying_strs
            )
            assert False, "Expected KeyError was not raised"
        except KeyError as e:
            assert str(e) == f"'Invalid direction: {direction_str}'"
    