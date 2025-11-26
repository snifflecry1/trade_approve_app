from dataclasses import dataclass
from trade_detail import TradeDetail
from enum import Enum

class Action(Enum):
    DRAFT = "Draft"
    PENDING_APPROVE = "Pending Approval"
    NEEDS_REAPPROVAL = "Needs Reapproval"
    APPROVED = "Approved"
    SENT_COUNTERPARTY = "Sent to Counterparty"
    EXECUTED = "Executed"
    CANCELLED = "Cancelled"

@dataclass
class Trade:
    id: str
    requester_id: str
    state: Action
    details: TradeDetail
    current_version: int = 1