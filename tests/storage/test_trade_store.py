import pytest 
from app.storage.trade_detail_history import TradeDetailHistory
from app.entities.trade_detail import TradeDetail, Direction, InstrumentStyle, Currency
from datetime import date

class ConfigMock:
    def __init__(self, store):
        self.store = store

#Probably want to make this generic to make a factory for test data
# class TestConfig:
#     test_t_date=test_v_date=test_d_date= date.today()
#     test_detail = TradeDetail(5, "test_entity", "test_counter", Direction.BUY, InstrumentStyle.FORWARD, Currency.EURO, 5000.00, [Currency.EURO, Currency.DOLLAR], test_t_date, test_v_date, test_d_date)
#     store = {
#         1:{
#             1: test_detail
#         }
#     }
test_t_date=test_v_date=test_d_date= date.today()
test_detail_one = TradeDetail(5, "test_entity", "test_counter", Direction.BUY, InstrumentStyle.FORWARD, Currency.EURO, 5000.00, [Currency.EURO, Currency.DOLLAR], test_t_date, test_v_date, test_d_date)
# test_detail_two = TradeDetail(5, "test_entity", "test_counter", Direction.BUY, InstrumentStyle.FORWARD, Currency.EURO, 10000.00, [Currency.EURO, Currency.POUND], test_t_date, test_v_date, test_d_date)

@pytest.mark.parametrize("config,expected", [
    (None, {}),
    (ConfigMock({1: {1: test_detail_one} }), {1: {1: test_detail_one} })
])
def test_trade_detail_history_init(config, expected):
    history = TradeDetailHistory(config=config)
    assert history.store == expected

# def test_add_trade_detail.py