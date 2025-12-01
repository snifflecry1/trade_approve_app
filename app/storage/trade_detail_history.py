import logging
from typing import Dict, Optional

from app.entities.action_log_entry import State
from app.entities.trade_detail import TradeDetail

logger = logging.getLogger()


# For each trade_id, maps to a dictionary of trade_details
# with state as a key
class TradeDetailHistory:
    store: Dict[int, Dict[State, TradeDetail]]

    def __init__(self, config=None):
        if config and config.store and isinstance(config.store, dict) and config.id:
            self.store = config.store
            self.current_unused_id = config.id
        else:
            self.store = {}
            self.current_unused_id = 1

    # from here were assuming details have been validated
    def add_trade(
        self, details: TradeDetail, state: State, trade_id: Optional[int] = None
    ) -> int:
        """Add a new trade detail version to the store."""
        if not trade_id:
            version_init = {state: details}
            self.store[self.current_unused_id] = version_init
            self.current_unused_id += 1
            return 1
        # This shouldn't occur but wrapping in try in case for some reason
        # a validated id doesn't exist in the store
        else:
            try:
                self.store[trade_id][state] = details
                return 1
            except KeyError as e:
                logger.error(
                    f"missing key: {e.args[0]}, current keys :{list(self.store.keys())}"
                )
                # may need to revise this
                raise KeyError(
                    f"missing key: {e.args[0]}, current keys :{list(self.store.keys())}"
                )
            except Exception as e:
                logger.error(f"error: {e}")
                return 0

    # retrieve all versions for a trade id
    def get_trade_versions(self, trade_id: int) -> dict[State, TradeDetail]:
        """Get all versions of a trade by trade ID."""
        try:
            versions = self.store[trade_id]
            return versions
        except KeyError as e:
            logger.error(
                f"missing key: {e.args[0]}, current keys :{list(self.store.keys())}"
            )
            # may need to revise this
            raise KeyError(
                f"missing key: {e.args[0]}, current keys :{list(self.store.keys())}"
            )

    # for retrieving a specific version of a trade by state
    def get_trade_state_version(self, trade_id: int, state: State) -> TradeDetail:
        """Get a specific version of a trade by trade ID and state."""
        try:
            version = self.store[trade_id][state]
            return version
        except KeyError as e:
            logger.error(
                f"missing key: {e.args[0]}, current keys :{list(self.store.keys())}"
            )
            # may need to revise this
            raise KeyError(
                f"missing key: {e.args[0]}, current keys :{list(self.store.keys())}"
            )
