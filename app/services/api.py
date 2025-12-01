# Add config class here ?, how will it be used ?

from app.entities.action_log_entry import ActionLogEntry
from app.storage.action_log import ActionLog, State, Action
from app.entities.trade_detail import TradeDetail
from app.storage.trade_detail_history import TradeDetailHistory
from app.entities.trade_detail import TradeDetail
from app.services.validations import Validator
from datetime import date, datetime
from app.helper import mappings
import logging

logger = logging.getLogger()

class TradeService:
    def __init__(self, trade_history: TradeDetailHistory, action_log: ActionLog, validator=None):
        self.trade_history = trade_history
        self.action_log = action_log
        #self.config = config may need later
        self.validator = Validator()

    def save_draft(self, entity: str, counterparty: str, direction: str,
                   style: str, notion_curr: str, notion_amount: float,
                   underlying: list, t_date: date, v_date: date, d_date: date
        ) -> int:
        """
        Save a trade draft with validation and audit logging.

        Args:
            entity: Trading entity name.
            counterparty: Counterparty identifier.
            direction: Trade direction string ("BUY"/"SELL").
            style: Instrument style string ("FORWARD"/"OPTION"/etc).
            notion_curr: Notional currency string ("USD"/"EUR"/etc).
            notion_amount: Notional amount for the trade.
            underlying: List of underlying currency strings.
            t_date: Trade date.
            v_date: Valuation date.
            d_date: Delivery date.

        Returns:
            int: Trade ID of the saved draft.
        """
        id = self.trade_history.current_unused_id
        parsed_direction, parsed_style, parsed_curr, parsed_underlying = self.validator.parse_draft_inputs(direction_str=direction,
            style_str=style,
            notion_curr_str=notion_curr,
            underlying_strs=underlying)
        try:
            trade_detail = TradeDetail(
                state_validator="DRAFT",
                entity=entity, 
                counterparty=counterparty,
                direction=parsed_direction, 
                style=parsed_style,                                      
                notion_curr=parsed_curr, 
                notion_amount=notion_amount,
                underlying=parsed_underlying,
                t_date=t_date,
                v_date=v_date, d_date=d_date
            )
            self.trade_history.add_trade(trade_detail, State.DRAFT)
            logger.info(f"Draft trade saved with ID {id}")
        except (ValueError, TypeError) as e:
            logger.error(f"Validation error while creating TradeDetail: {e}")
            return 0
        return id


    def submit_trade_for_approval(self, trade_id: int, user_id: int, note: str) -> bool:
        """
        Submit a draft trade for approval with validation.

        Args:
            trade_id: ID of the trade to submit.
            user_id: User submitting the trade.
            note: Optional submission note or comment.

        Returns:
            bool: True if submission succeeds, False otherwise.
        """
        if not trade_id in self.trade_history.store:
            logger.error(f"Trade ID {trade_id} not found in trade history.")
            return False
        valid = self.validator.validate_submit_trade(self.trade_history.store[trade_id], trade_id)
        if not valid:
            logger.error(f"Trade ID {trade_id} failed submission validation.")
            return False
        self.action_log.record(trade_id=trade_id, user_id=user_id, action=Action.SUBMIT, from_state=State.DRAFT, note=note)
        trade = self.trade_history.store[trade_id][State.DRAFT]
        trade.state_validator = "PENDING_APPROVAL"
        self.trade_history.add_trade(trade, State.PENDING_APPROVE, trade_id=trade_id)
        logger.info(f"Trade ID {trade_id} submitted for approval by user {user_id}.")
        return True
    
    def approve_trade(self, trade_id: int, user_id: int, note: str) -> bool:
        """
        Approve a trade that is pending approval. Validates who can approve based on user_id

        Args:
            trade_id: ID of the trade to approve.
            user_id: User approving the trade.
            note: Optional approval note or comment.

        Returns:
            bool: True if approval succeeds, False otherwise.
        """
        if not trade_id in self.trade_history.store:
            logger.error(f"Trade ID {trade_id} not found in trade history.")
            return False
        trades = self.trade_history.store[trade_id]
        if not trade_id in self.action_log.action_log:
            logger.error(f"Trade ID {trade_id} has no action log entries.")
            return False
        request_user_id = self.action_log.action_log[trade_id][0].user_id
        latest_log = self.action_log.get_latest_log(trade_id)
        if not latest_log:
            logger.error(f"Trade ID {trade_id} has no latest action log entry.")
            return False
        state = latest_log.to_state
        valid = self.validator.validate_approve_trade(trades, trade_id, user_id, request_user_id, state=state)
        if not valid:
            logger.error(f"Trade ID {trade_id} failed approval validation.")
            return False
        self.action_log.record(trade_id=trade_id, user_id=user_id, action=Action.APPROVE, from_state=state, note=note)
        trade = self.trade_history.store[trade_id][state]
        self.trade_history.add_trade(trade, State.APPROVED, trade_id=trade_id)
        logger.info(f"Trade ID {trade_id} approved by user {user_id}.")
        return True
    
    def cancel_trade(self, trade_id: int, user_id: int, note: str) -> bool:
        """
        Cancel a trade that is pending approval.

        Args:
            trade_id: ID of the trade to cancel.
            user_id: User cancelling the trade.
            note: Optional cancellation note or comment.

        Returns:
            bool: True if cancellation succeeds, False otherwise.
        """
        if not trade_id in self.trade_history.store:
            logger.error(f"Trade ID {trade_id} not found in trade history.")
            return False
        trades = self.trade_history.store[trade_id]
        latest_log = self.action_log.get_latest_log(trade_id)
        if not latest_log:
            logger.error(f"Trade ID {trade_id} has no latest action log entry.")
            return False
        state = latest_log.to_state
        valid = self.validator.validate_cancel_trade(trades, trade_id, state=state)
        if not valid:
            logger.error(f"Trade ID {trade_id} failed cancellation validation.")
            return False
        self.action_log.record(trade_id=trade_id, user_id=user_id, action=Action.CANCEL, from_state=state, note=note)
        trade = self.trade_history.store[trade_id][state]
        self.trade_history.add_trade(trade, State.CANCELLED, trade_id=trade_id)
        logger.info(f"Trade ID {trade_id} cancelled by user {user_id}.")
        return True
    
    def update_trade(self, trade_id: int, user_id: int, note: str, **updates) -> bool:
        """
        Update a trade that is pending approval with new details. Validates updates dict and user permissions  before applying.

        Args:
            trade_id: ID of the trade to update.
            user_id: User updating the trade.
            note: Optional update note or comment.
            updates: Key-value pairs of fields to update in the trade.

        Returns:
            bool: True if update succeeds, False otherwise.
        """
        if not trade_id in self.trade_history.store:
            logger.error(f"Trade ID {trade_id} not found in trade history.")
            return False
        trades = self.trade_history.store[trade_id]
        latest_log = self.action_log.get_latest_log(trade_id)
        if not latest_log:
            logger.error(f"Trade ID {trade_id} has no latest action log entry.")
            return False
        state = latest_log.to_state
        request_user_id = self.action_log.action_log[trade_id][0].user_id
        valid = self.validator.validate_update_trade(trades=trades, trade_id=trade_id, updates=updates, state=state, requester_id=request_user_id, user_id=user_id)
        if not valid:
            logger.error(f"Trade ID {trade_id} failed update validation.")
            return False
        trade = self.trade_history.store[trade_id][state]
        copy_of_trade = TradeDetail(
            state_validator=trade.state_validator,
            entity=trade.entity,
            counterparty=trade.counterparty,
            direction=trade.direction,
            style=trade.style,
            notion_curr=trade.notion_curr,
            notion_amount=trade.notion_amount,
            underlying=trade.underlying,
            t_date=trade.t_date,
            v_date=trade.v_date,
            d_date=trade.d_date,
        )
        for key, value in updates.items():
            setattr(copy_of_trade, key, value)
        self.trade_history.add_trade(copy_of_trade, State.NEEDS_REAPPROVAL, trade_id=trade_id)
        self.action_log.record(trade_id=trade_id, user_id=user_id, action=Action.UPDATE, from_state=state, note=note)
        logger.info(f"Trade ID {trade_id} updated by user {user_id}.")
        return True
        

        
        
    
    

