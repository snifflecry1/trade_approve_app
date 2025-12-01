# Add config class here ?, how will it be used ?

from app.entities.action_log_entry import ActionLogEntry
from app.storage.action_log import ActionLog, State, Action
from app.entities.trade_detail import TradeDetail
from app.storage.trade_detail_history import TradeDetailHistory
from app.entities.trade_detail import TradeDetail
from app.services.validations import Validator
from app.services.trade_executor import TradeExecutor
from datetime import date, datetime
from app.helper import mappings
from typing import Optional
import logging

logger = logging.getLogger()

class TradeService:
    def __init__(self, trade_history: TradeDetailHistory, action_log: ActionLog, validator=None):
        self.trade_history = trade_history
        self.action_log = action_log
        #self.config = config may need later
        self.validator = Validator()
        self.executor = TradeExecutor()

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
            note: Submission note or comment.

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
            note: Approval note or comment.

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
        Cancel a trade that is past submission. Validates if cancellation is allowed based on trade state.

        Args:
            trade_id: ID of the trade to cancel.
            user_id: User cancelling the trade.
            note: Cancellation note or comment.

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
            note: Update note or comment.
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
    
    def sent_trade_to_counterparty(self, trade_id: int, user_id: int, note: str, strike: Optional[float] = None) -> bool:
        """
        Mark a trade as sent to counterparty. Validates user permissions and trade state before marking.

        Args:
            trade_id: ID of the trade to mark as sent.
            user_id: User marking the trade as sent.
            note: Optional note or comment.
            strike: Actual strike price from execution. If None, simulates one.
        Returns:
            bool: True if marking succeeds, False otherwise.
        """
        if not trade_id in self.trade_history.store:
            logger.error(f"Trade ID {trade_id} not found in trade history.")
            return False
        latest_log = self.action_log.get_latest_log(trade_id)
        if not latest_log:
            logger.error(f"Trade ID {trade_id} has no latest action log entry.")
            return False
        state = latest_log.to_state
        requester_id = self.action_log.action_log[trade_id][0].user_id
        valid = self.validator.validate_send_to_counterparty(trade_id, state=state, requester_id=requester_id, user_id=user_id)
        if not valid:
            logger.error(f"Trade ID {trade_id} failed send to counterparty validation.")
            return False
        self.action_log.record(trade_id=trade_id, user_id=user_id, action=Action.SENDTOEXECUTE, from_state=state, note=note)
        
        trade = self.trade_history.store[trade_id][state]
        sent_trade = TradeDetail(
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
            d_date=trade.d_date
        )
        self.trade_history.add_trade(sent_trade, State.SENT_COUNTERPARTY, trade_id=trade_id)
        logger.info(f"Trade ID {trade_id} marked as sent to counterparty by user {user_id}.")
        
        try:
            executed_trade = self.executor.execute_trade(sent_trade, strike=strike)
        except ValueError as e:
            logger.error(f"Trade execution failed: {e}")
            return False
        self.trade_history.add_trade(executed_trade, State.EXECUTED, trade_id=trade_id)
        logger.info(f"Trade ID {trade_id} executed with strike {executed_trade.strike}.")
        return True

    def book_trade(self, trade_id: int, user_id: int, note: str) -> bool:
        """
        Adds a booking entry for an executed trade. Validates trade state before booking.

        Args:
            trade_id: ID of the trade to book.
            user_id: User booking the trade.
            note: Optional booking note or comment.
            
        Returns:
            bool: True if booking succeeds, False otherwise.
        """ 
        if not trade_id in self.trade_history.store:
            logger.error(f"Trade ID {trade_id} not found in trade history.")
            return False
        latest_log = self.action_log.get_latest_log(trade_id)
        if not latest_log:
            logger.error(f"Trade ID {trade_id} has no latest action log entry.")
            return False
        state = latest_log.to_state
        valid = self.validator.validate_book_trade(trade_id, state=state, trades=self.trade_history.store[trade_id])
        if not valid:
            logger.error(f"Trade ID {trade_id} failed booking validation.")
            return False
                
        self.action_log.record(trade_id=trade_id, user_id=user_id, action=Action.BOOK, from_state=state, note=note)
        logger.info(f"Trade ID {trade_id} booked by user {user_id}.")
        return True
    
    def view_trades(self):
        """
        Returns a pretty printed version of each trade in the action log using the format:
        Trade_ID | Latest_State | Last_Updated_Timestamp
        """
        result = []
        for trade_id, logs in self.action_log.action_log.items():
            latest_log = logs[-1]
            output_line = f"Trade_ID: {trade_id} | Latest_State: {latest_log.to_state.name} | Last_Updated_Timestamp: {latest_log.timestamp}"
            result.append(output_line)
            logger.info(output_line)
        return result
    
    def view_action_log(self, trade_id: int):
        """
        Returns a pretty printed version of the action log for a specific trade using the format:
        Step | Trade_ID | User_ID | Action | From_State | To_State | Timestamp | Note
        """
        result = []
        logs = self.action_log.get_logs(trade_id)
        for log in logs:
            output_line = (f"Step: {log.step} | User_ID: {log.user_id} | "
                           f"Action: {log.action.name} | From_State: {log.from_state.name} | "
                           f"To_State: {log.to_state.name} | Timestamp: {log.timestamp} | Note: {log.note}")
            result.append(output_line)
            logger.info(output_line)
        return result
    
    def view_trade_states(self, trade_id: int):
        """
        Returns all states for a specific trade in the format:
        """
        result = []
        try:
            versions = self.trade_history.get_trade_versions(trade_id)
            result.append(f"| State |")
            for state in versions:
                output_line = f"{mappings.enum_to_state_str[state]}"
                result.append(output_line)
                logger.info(output_line)
            return result
        except KeyError as e:
            logger.error(f"Trade ID {trade_id} not found: {e}")
            return []
    
    def view_trade_details(self, trade_id: int, state: State):
        """
        Returns the details of a specific trade at a specific state.
        """
        try:
            trade_detail = self.trade_history.get_trade_state_version(trade_id, state)
            output_lines = [
                f"Trade ID: {trade_id}",
                f"State: {state.name}",
                f"Entity: {trade_detail.entity}",
                f"Counterparty: {trade_detail.counterparty}",
                f"Direction: {trade_detail.direction.name}",
                f"Style: {trade_detail.style.name}",
                f"Notional Currency: {trade_detail.notion_curr.name}",
                f"Notional Amount: {trade_detail.notion_amount}",
                f"Underlying: {[curr.name for curr in trade_detail.underlying]}",
                f"Trade Date: {trade_detail.t_date}",
                f"Valuation Date: {trade_detail.v_date}",
                f"Delivery Date: {trade_detail.d_date}",
                f"Strike: {trade_detail.strike if trade_detail.strike is not None else 'None'}"
            ]
            return output_lines
        except KeyError as e:
            logger.error(f"Trade ID {trade_id} with state {state.name} not found: {e}")
            return []
    
    def compare_trade_versions(self, trade_id: int, state1: State, state2: State):
        """
        Compares two versions of a trade by their states and returns the differences.

        Args:
            trade_id: ID of the trade to compare.
            state1: First state to compare.
            state2: Second state to compare.
        Returns:
            a dictionary where the keys are the field names that differ and the values are tuples of (value_in_state1, value_in_state2)
        """
        try:
            trade1 = self.trade_history.get_trade_state_version(trade_id, state1)
            trade2 = self.trade_history.get_trade_state_version(trade_id, state2)
            diffs = {}
            for field in trade1.__dataclass_fields__:
                value1 = getattr(trade1, field)
                value2 = getattr(trade2, field)
                if not value2:
                    diffs[field] = (value1, None)
                if value1 != value2:
                    diffs[field] = (value1, value2)
            return diffs
        except KeyError as e:
            logger.error(f"Trade ID {trade_id} with specified states not found: {e}")
            return {}
        
        

    

        

        
        
    
    

