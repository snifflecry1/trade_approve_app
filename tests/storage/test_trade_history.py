import pytest
from app.storage.trade_detail_history import TradeDetailHistory
from app.entities.trade_detail import TradeDetail, Direction, InstrumentStyle, Currency
from app.entities.action_log_entry import State
from datetime import date


class ConfigMock:
    def __init__(self, store, id):
        self.store = store
        self.id = id


# Probably want to make this generic to make a factory for test data
# class TestConfig:
#     test_t_date=test_v_date=test_d_date= date.today()
#     test_detail = TradeDetail(5, "test_entity", "test_counter", Direction.BUY, InstrumentStyle.FORWARD, Currency.EURO, 5000.00, [Currency.EURO, Currency.DOLLAR], test_t_date, test_v_date, test_d_date)
#     store = {
#         1:{
#             1: test_detail
#         }
#     }
test_t_date = test_v_date = test_d_date = date.today()
test_detail_one = TradeDetail(
    state_validator="DRAFT",
    entity="test_entity",
    counterparty="test_counter",
    direction=Direction.BUY,
    style=InstrumentStyle.FORWARD,
    notion_curr=Currency.EURO,
    notion_amount=5000.00,
    underlying=[Currency.EURO, Currency.DOLLAR],
    t_date=test_t_date,
    v_date=test_v_date,
    d_date=test_d_date,
)
test_detail_two = TradeDetail(
    "NEEDS_REAPPROVAL",
    "test_entity",
    "test_counter",
    Direction.SELL,
    InstrumentStyle.FORWARD,
    Currency.EURO,
    5000.00,
    [Currency.EURO, Currency.DOLLAR],
    test_t_date,
    test_v_date,
    test_d_date,
)
test_detail_three = TradeDetail(
    "EXECUTED",
    "test_entity",
    "test_counter",
    Direction.BUY,
    InstrumentStyle.FORWARD,
    Currency.EURO,
    10000.00,
    [Currency.EURO, Currency.POUND],
    test_t_date,
    test_v_date,
    test_d_date,
)


class TestTradeHistory:
    @pytest.mark.parametrize(
        "config,expected_store, expected_id",
        [
            (None, {}, 1),
            (ConfigMock({1: {1: test_detail_one}}, 1), {1: {1: test_detail_one}}, 1),
        ],
    )
    def test_trade_detail_history_init(self, config, expected_store, expected_id):
        history = TradeDetailHistory(config=config)
        assert history.store == expected_store
        assert history.current_unused_id == expected_id

    # Case 1, empty dictionary -> outer and inner key 1
    # Case 2, verison for trade exists, inner key incremented
    # Case 3, dictionary not empty but new trade, outer key incremented, inner key 1
    @pytest.mark.parametrize(
        "initial_store, initial_id, trade_id, state, trade_detail, expected_store",
        [
            (
                {},
                1,
                None,
                State.DRAFT,
                test_detail_one,
                {1: {State.DRAFT: test_detail_one}},
            ),
            (
                {1: {State.DRAFT: test_detail_one}},
                1,
                1,
                State.NEEDS_REAPPROVAL,
                test_detail_two,
                {
                    1: {
                        State.DRAFT: test_detail_one,
                        State.NEEDS_REAPPROVAL: test_detail_two,
                    }
                },
            ),
            (
                {5: {State.DRAFT: test_detail_one}},
                6,
                None,
                State.DRAFT,
                test_detail_two,
                {
                    5: {State.DRAFT: test_detail_one},
                    6: {State.DRAFT: test_detail_two},
                },
            ),
        ],
    )
    def test_add_trade_detail(
        self, initial_store, initial_id, trade_id, state, trade_detail, expected_store
    ):
        config = ConfigMock(initial_store, initial_id)
        history = TradeDetailHistory(config=config)

        resp = history.add_trade(details=trade_detail, state=state, trade_id=trade_id)

        assert history.store == expected_store

    def test_add_trade_details_failure_key_error(self):
        history = TradeDetailHistory()
        with pytest.raises(KeyError):
            history.add_trade(details=test_detail_one, state=State.DRAFT, trade_id=5)

    def test_get_trade_versions(self):
        expected = {State.DRAFT: test_detail_one}
        config = ConfigMock({1: {State.DRAFT: test_detail_one}}, 2)
        history = TradeDetailHistory(config)
        versions = history.get_trade_versions(1)
        assert expected == versions

    def test_get_trade_versions_key_error(self):
        history = TradeDetailHistory()
        with pytest.raises(KeyError):
            versions = history.get_trade_versions(1)
    
    def test_get_trade_state_version(self):
        expected = test_detail_one
        config = ConfigMock({1: {State.DRAFT: test_detail_one}}, 2)
        history = TradeDetailHistory(config)
        version = history.get_trade_state_version(1, State.DRAFT)
        assert expected == version
    
    def test_get_trade_state_version_key_error(self):
        history = TradeDetailHistory()
        with pytest.raises(KeyError):
            version = history.get_trade_state_version(1, State.DRAFT)
    