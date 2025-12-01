from datetime import date

import pytest

from app.entities.trade_detail import (Currency, Direction, InstrumentStyle,
                                       TradeDetail)
from app.helper import mappings
from app.services.validations import Validator


class TestValidator:
    @pytest.fixture
    def setup_detail(self):
        return TradeDetail(
            state_validator="DRAFT",
            entity="EntityA",
            counterparty="CounterpartyB",
            direction=Direction.BUY,
            style=InstrumentStyle.FORWARD,
            notion_curr=Currency.DOLLAR,
            notion_amount=10000.0,
            underlying=[Currency.DOLLAR, Currency.EURO],
            t_date=date.today(),
            v_date=date.today(),
            d_date=date.today(),
        )

    @pytest.mark.parametrize(
        "invalid_param, mapping",
        [
            ("INVALID_DIRECTION", mappings.direction_stubs),
            ("INVALID_STYLE", mappings.style_stubs),
            ("INVALID_CURRENCY", mappings.currency_stubs),
        ],
    )
    def test_parse_enum_field_invalid_raises_value_error(self, invalid_param, mapping):
        """Test that parsing an invalid enum field raises KeyError."""
        validator = Validator()
        invalid_direction = "UPWARDS"
        try:
            validator.parse_enum_field(
                "test", invalid_direction, mappings.direction_stubs
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
        """Test that parsing a valid enum field returns the correct enum value."""
        validator = Validator()
        result = validator.parse_enum_field("test", valid_param, mapping)
        assert result == mapping[valid_param]

    def test_parse_draft_inputs_valid(self):
        """Test that valid draft inputs are correctly parsed into enum types."""
        validator = Validator()
        direction_str = "BUY"
        style_str = "FORWARD"
        notion_curr_str = "USD"
        underlying_strs = ["USD", "EUR"]

        direction, style, notion_curr, underlying = validator.parse_draft_inputs(
            direction_str, style_str, notion_curr_str, underlying_strs
        )

        assert direction == mappings.direction_stubs[direction_str]
        assert style == mappings.style_stubs[style_str]
        assert notion_curr == mappings.currency_stubs[notion_curr_str]
        assert underlying == [
            mappings.currency_stubs[currency_str] for currency_str in underlying_strs
        ]

    def test_parse_draft_inputs_invalid_raises_value_error(self):
        """Test that invalid draft inputs raise KeyError."""
        validator = Validator()
        direction_str = "INVALID_DIRECTION"
        style_str = "FORWARD"
        notion_curr_str = "USD"
        underlying_strs = ["USD", "EUR"]

        try:
            validator.parse_draft_inputs(
                direction_str, style_str, notion_curr_str, underlying_strs
            )
            assert False, "Expected KeyError was not raised"
        except KeyError as e:
            assert str(e) == f"'Invalid direction: {direction_str}'"

    def test_validate_submit_trade_invalid_cancelled(self, setup_detail):
        """Test that validating submission for a cancelled trade fails."""
        validator = Validator()
        trades = {mappings.State.CANCELLED: setup_detail}
        trade_id = 1

        is_valid = validator.validate_submit_trade(trades, trade_id)
        assert not is_valid

    def validate_submit_trade_valid(self, setup_detail):
        """Test that validating submission for a valid draft trade succeeds."""
        validator = Validator()
        trades = {mappings.State.DRAFT: setup_detail}
        trade_id = 1

        is_valid = validator.validate_submit_trade(trades, trade_id)
        assert is_valid

    def test_validate_approve_trade_invalid_cancelled(self, setup_detail):
        """Test that validating approval for a cancelled trade fails."""
        validator = Validator()
        trades = {mappings.State.CANCELLED: setup_detail}
        trade_id = 1

        is_valid = validator.validate_approve_trade(
            trades, trade_id, user_id=123, request_id=1, state=mappings.State.CANCELLED
        )
        assert not is_valid

    def test_validate_approve_trade_valid(self, setup_detail):
        """Test that validating approval for a pending trade succeeds."""
        validator = Validator()
        setup_detail.state_validator = "PENDING_APPROVAL"
        trades = {mappings.State.PENDING_APPROVE: setup_detail}
        trade_id = 1

        is_valid = validator.validate_approve_trade(
            trades,
            trade_id,
            user_id=123,
            request_id=1,
            state=mappings.State.PENDING_APPROVE,
        )
        assert is_valid

    def test_validate_cancel_trade_invalid_cancelled(self, setup_detail):
        validator = Validator()
        trades = {mappings.State.CANCELLED: setup_detail}
        trade_id = 1

        is_valid = validator.validate_cancel_trade(
            trades, trade_id, state=mappings.State.CANCELLED
        )
        assert not is_valid

    def test_validate_cancel_trade_valid(self, setup_detail):
        """Test that validating cancellation for a valid state succeeds."""
        validator = Validator()
        trades = {mappings.State.DRAFT: setup_detail}
        trade_id = 1

        is_valid = validator.validate_cancel_trade(
            trades, trade_id, state=mappings.State.PENDING_APPROVE
        )
        assert is_valid

    def test_validate_update_trade_invalid_state(self, setup_detail):
        """Test that validating update for an approved trade fails."""
        validator = Validator()
        trades = {mappings.State.APPROVED: setup_detail}
        trade_id = 1

        is_valid = validator.validate_update_trade(
            trades,
            trade_id,
            requester_id=1,
            user_id=2,
            updates={},
            state=mappings.State.APPROVED,
        )
        assert not is_valid

    def test_validate_update_trade_valid(self, setup_detail):
        """Test that validating update for a pending trade succeeds."""
        validator = Validator()
        trades = {mappings.State.PENDING_APPROVE: setup_detail}
        trade_id = 1

        is_valid = validator.validate_update_trade(
            trades,
            trade_id,
            requester_id=1,
            user_id=2,
            updates={},
            state=mappings.State.PENDING_APPROVE,
        )
        assert is_valid

    def test_validate_send_to_counterparty_invalid_state(self, setup_detail):
        """Test that validating send to counterparty for a draft trade fails."""
        validator = Validator()
        trades = {mappings.State.DRAFT: setup_detail}
        trade_id = 1

        is_valid = validator.validate_send_to_counterparty(
            trade_id, state=mappings.State.DRAFT, requester_id=1, user_id=2
        )
        assert not is_valid

    def test_validate_send_to_counterparty_valid(self, setup_detail):
        """Test that validating send to counterparty for an approved trade succeeds."""
        validator = Validator()
        trades = {mappings.State.APPROVED: setup_detail}
        trade_id = 1

        is_valid = validator.validate_send_to_counterparty(
            trade_id, state=mappings.State.APPROVED, requester_id=1, user_id=2
        )
        assert is_valid

    def test_validate_book_trade_invalid_state(self, setup_detail):
        """Test that validating booking for a non-executed trade fails."""
        validator = Validator()
        trades = {mappings.State.APPROVED: setup_detail}
        trade_id = 1

        is_valid = validator.validate_book_trade(
            trade_id, state=mappings.State.APPROVED, trades=trades
        )
        assert not is_valid

    def test_validate_book_trade_valid(self, setup_detail):
        """Test that validating booking for an executed trade succeeds."""
        validator = Validator()
        trades = {mappings.State.EXECUTED: setup_detail}
        trade_id = 1

        is_valid = validator.validate_book_trade(
            trade_id, state=mappings.State.SENT_COUNTERPARTY, trades=trades
        )
        assert is_valid
