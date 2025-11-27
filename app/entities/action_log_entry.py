from dataclasses import dataclass
from app.entities.trade_detail import TradeDetail
from enum import Enum
from datetime import datetime
from typing import Optional


class State(Enum):
    DRAFT = "Draft"
    PENDING_APPROVE = "Pending Approval"
    NEEDS_REAPPROVAL = "Needs Reapproval"
    APPROVED = "Approved"
    SENT_COUNTERPARTY = "Sent to Counterparty"
    EXECUTED = "Executed"
    CANCELLED = "Cancelled"


# May need to map these to actual api methods
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
    user_id: str
    action: Action
    from_state: State
    to_state: State
    timestamp: datetime
    note: str = ""
