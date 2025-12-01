from app.entities.trade_detail import Currency, InstrumentStyle, Direction
from app.entities.action_log_entry import State
from app.helper import mappings
from app.entities.trade_detail import TradeDetail
from typing import Tuple, Optional, TypeVar, Mapping, List, Dict
import logging

logger = logging.getLogger(__name__)

class Validator:
    T = TypeVar("T") 

    @staticmethod
    def parse_from_mapping(
        value: str,
        mapping: Mapping[str, T],
        field_name: str,
    ) -> Tuple[bool, Optional[T]]:
        """
        Try to map a string to a typed enum/value using a mapping.

        Returns (True, mapped_value) on success,
                (False, None) on failure (and logs an error).
        """
        try:
            return True, mapping[value]
        except KeyError:
            logger.error(f"Unsupported {field_name}: {value}")
            return False, None 

    @staticmethod  
    def parse_enum_field(
        field_name: str,
        raw_value: str,
        mapping: Mapping[str, T],

    ) -> T:
        ok, value = Validator.parse_from_mapping(raw_value, mapping, field_name)
        if not ok or value is None:
            raise KeyError(f"Invalid {field_name}: {raw_value}")
        return value
    
    def parse_draft_inputs(
        self,
        direction_str: str,
        style_str: str,
        notion_curr_str: str,
        underlying_strs: list[str],
    ) -> tuple[Direction, InstrumentStyle, Currency, List[Currency]]:
        direction = self.parse_enum_field("direction", direction_str, mappings.direction_stubs)
        style = self.parse_enum_field("style", style_str, mappings.style_stubs)
        notional_currency = self.parse_enum_field("currency", notion_curr_str, mappings.currency_stubs)

        underlying_currencies = [
            self.parse_enum_field("underlying currency", u, mappings.currency_stubs)
            for u in underlying_strs
        ]

        return direction, style, notional_currency, underlying_currencies
    
    # deeper validation for submitting trade
    def validate_submit_trade(self, trades: Dict[State,TradeDetail], trade_id:int) -> bool:
        if len(trades) > 1:
            logger.error(f"Trade ID {trade_id} has multiple versions; cannot submit.")
            return False
        if State.DRAFT not in trades:
            logger.error(f"Trade ID {trade_id} is not in DRAFT state.")
            return False
        trade = trades[State.DRAFT]
        if trade.notion_curr not in trade.underlying:
            logger.error("Notional currency must be one of the underlying currencies.")
            return False
        elif len(trade.underlying) != 2:
            logger.error("There must be exactly two underlying currencies.")
            return False
        elif trade.t_date > trade.v_date or trade.v_date > trade.d_date:
            logger.error("Date sequence is invalid: t_date <= v_date <= d_date must hold.")
            return False
        elif trade.strike:
            logger.error("Strike price should not be set for draft trades.")
            return False
        return True
    
    def validate_approve_trade(self, trades: Dict[State,TradeDetail], trade_id:int, user_id:int, request_id: int, state: State) -> bool:
        if state != State.PENDING_APPROVE and state != State.NEEDS_REAPPROVAL:
            logger.error(f"Trade ID {trade_id} is not in Pending Approval or Needs Reapproval state.")
            return False
        if state == State.PENDING_APPROVE and user_id == request_id:
            logger.error("Approver cannot be the same as the submitter.")
            return False
        if state == State.NEEDS_REAPPROVAL and user_id != request_id:
            logger.error("Re-approver has to be the original requester.")
            return False
        trade = trades[state]
        if trade.strike:
            logger.error("Trade Strike price can only be set for executed trades.")
            return False
        # Return the used state string to correctly log the from_state
        return True
    
    def validate_cancel_trade(self, trades: Dict[State,TradeDetail], trade_id:int, state: State) -> bool:
        if state == State.CANCELLED or state == State.EXECUTED or state == State.DRAFT:
            logger.error(f"Trade ID {trade_id} in invalid state to be cancelled.")
            return False
        return True
    
    def validate_update_trade(self, trades: Dict[State,TradeDetail], trade_id:int, requester_id:int, user_id:int, updates:dict, state: State) -> bool:
        if state != State.PENDING_APPROVE:
            logger.error(f"Trade ID {trade_id} is not in PENDING_APPROVE state and cannot be updated.")
            return False
        if requester_id == user_id:
            logger.error("Updater cannot be the same as the original requester.")
            return False
        trade = trades[state]
        for key, value in updates.items():
            if hasattr(trade, key):
                if not isinstance(value, type(getattr(trade, key))):
                    logger.error(f"Update for '{key}' has incorrect type. Expected {type(getattr(trade, key)).__name__}, got {type(value).__name__}.")
                    return False
                if key == "notion_amount" and value <= 1.00:
                    logger.error("Notional amount must be positive.")
                    return False
                if key == "strike":
                    logger.error("Strike price can only be set for executed trades.")
                    return False
                if key == "underlying":
                    if len(value) != 2 and trade.notion_curr not in value:
                        logger.error("Underlying must be a list of exactly two currencies and contain notional currency.")
                        return False
                if key == "notion_curr":
                    if value not in trade.underlying:
                        logger.error("Notional currency must be one of the underlying currencies.")
                        return False
                if key in ["t_date", "v_date", "d_date"]:
                    t_date = updates.get("t_date", trade.t_date)
                    v_date = updates.get("v_date", trade.v_date)
                    d_date = updates.get("d_date", trade.d_date)
                    if t_date > v_date or v_date > d_date:
                        logger.error("Date sequence is invalid: t_date <= v_date <= d_date must hold.")
                        return False
            else:
                logger.error(f"TradeDetail has no attribute '{key}' to update.")
                return False
        return True


    
    
