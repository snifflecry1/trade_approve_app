from datetime import date

import pytest

from app.entities.action_log_entry import State
from app.entities.trade_detail import (Currency, Direction, InstrumentStyle,
                                       TradeDetail)


class TestTradeDetail:

    @pytest.fixture
    def detail_factory(self):
        def _make_detail(**override):
            today = date.today()
            base_kwargs = dict(
                state_validator="DRAFT",
                entity="EntityA",
                counterparty="CounterpartyB",
                direction=Direction.BUY,
                style=InstrumentStyle.FORWARD,
                notion_curr=Currency.DOLLAR,
                notion_amount=10000.0,
                underlying=[Currency.DOLLAR, Currency.EURO],
                t_date=today,
                v_date=today,
                d_date=today,
            )
            base_kwargs.update(override)
            return TradeDetail(**base_kwargs)  # type: ignore

        return _make_detail

    def test_valid_trade_detail(self, detail_factory):
        """Test that a valid trade detail can be created with all required fields."""
        detail = detail_factory()
        assert detail.state_validator == "DRAFT"
        assert detail.entity == "EntityA"
        assert detail.counterparty == "CounterpartyB"
        assert detail.direction == Direction.BUY
        assert detail.style == InstrumentStyle.FORWARD
        assert detail.notion_curr == Currency.DOLLAR
        assert detail.notion_amount == 10000.0
        assert detail.underlying == [Currency.DOLLAR, Currency.EURO]
        assert detail.t_date == date.today()
        assert detail.v_date == date.today()
        assert detail.d_date == date.today()

    def test_trade_detail_invalid_amount(self, detail_factory):
        """Test that creating a trade detail with negative amount raises ValueError."""
        with pytest.raises(ValueError):
            detail_factory(notion_amount=-1)

    def test_trade_detail_strike_set_invalid_state(self, detail_factory):
        """Test that setting strike price in non-executed state raises ValueError."""
        with pytest.raises(ValueError):
            detail_factory(strike=100.0, state_validator=State.DRAFT)

    def test_trade_detail_compare(self, detail_factory):
        """Test that comparing two trade details returns correct field differences."""
        detail1 = detail_factory(notion_amount=10000.0)
        detail2 = detail_factory(notion_amount=15000.0)
        diffs = detail1.compare_trade(detail2)
        assert "notion_amount" in diffs
        assert diffs["notion_amount"] == (10000.0, 15000.0)

        detail3 = detail_factory(direction=Direction.SELL)
        diffs2 = detail1.compare_trade(detail3)
        assert "direction" in diffs2
        assert diffs2["direction"] == (Direction.BUY, Direction.SELL)
