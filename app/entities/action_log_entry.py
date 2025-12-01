from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from app.entities.trade_detail import TradeDetail


class State(Enum):
    DRAFT = "Draft"
    PENDING_APPROVE = "Pending Approval"
    NEEDS_REAPPROVAL = "Needs Reapproval"
    APPROVED = "Approved"
    SENT_COUNTERPARTY = "Sent to Counterparty"
    EXECUTED = "Executed"
    CANCELLED = "Cancelled"


class Action(Enum):
    SUBMIT = "Submit"
    APPROVE = "Approve"
    UPDATE = "Update"
    SENDTOEXECUTE = "Send to execute"
    BOOK = "Book"
    CANCEL = "Cancel"


@dataclass
class ActionLogEntry:
    step: int
    trade_id: int
    user_id: int
    action: Action
    from_state: State
    to_state: State
    timestamp: datetime
    note: str = ""

    def __post_init__(self):
        if not isinstance(self.action, Action):
            raise TypeError(f"Invalid action: {self.action}")
        if not isinstance(self.from_state, State):
            raise TypeError(f"Invalid from_state: {self.from_state}")
        if not isinstance(self.to_state, State):
            raise TypeError(f"Invalid to_state: {self.to_state}")
        if not isinstance(self.timestamp, datetime):
            raise TypeError(f"Invalid timestamp: {self.timestamp}")
        if self.step < 1:
            raise ValueError(f"Step must be positive integer, got: {self.step}")
        if not isinstance(self.note, str):
            raise TypeError(f"Note must be a string, got: {type(self.note)}")
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError(f"User ID must be a positive integer, got: {self.user_id}")
