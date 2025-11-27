from dataclasses import dataclass
from enum import Enum
from datetime import date
from typing import Optional, List


# Helper classes for a trade
# Is this correct layout ?
class InstrumentStyle(Enum):
    FORWARD = "Forward Contract"


class Currency(Enum):
    EURO = "€"
    POUND = "£"
    DOLLAR = "$"


class Direction(Enum):
    BUY = "Buy"
    SELL = "Sell"


# strike is None by default until trade is booked
@dataclass
class TradeDetail:
    trade_id: int
    entity: str
    counterparty: str
    direction: Direction
    style: InstrumentStyle
    notion_curr: Currency
    notion_amount: float
    underlying: List[Currency]
    t_date: date
    v_date: date
    d_date: date
    strike: Optional[float] = None
    # would it be worth storing the state of the trade here ?
    # like some list that is at a specific index pointing to a specific state
    # This seems outside of the specifics of this file representing trade data

    # implement for diff functionality
    # def compare_trade:
