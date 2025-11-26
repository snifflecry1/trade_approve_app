from typing import Dict
from app.entities.trade_detail import TradeDetail

# For each trade_id, maps to a dictionary of trade_details
# with version_id as a key
class TradeDetailHistory:
    store: Dict[int, Dict[int, TradeDetail]]
    def __init__(self, config=None):
        if config and config.store:
            self.store = config.store
        else:
            self.store = {}
    
    def add_trade(self, trade_id: int, details: TradeDetail):
        pass

        

