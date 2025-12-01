from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class InstrumentStyle(Enum):
    FORWARD = "Forward Contract"


class Currency(Enum):
    EURO = "EUR"
    POUND = "GBP"
    DOLLAR = "USD"


class Direction(Enum):
    BUY = "Buy"
    SELL = "Sell"


# strike is None by default until trade is booked
@dataclass
class TradeDetail:
    state_validator: str
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

    # Checking for valid notional amount and strike price
    def __post_init__(self):
        if self.notion_amount <= 1.00:
            raise ValueError("Notional amount must be positive")
        if self.strike and self.state_validator != "EXECUTED":
            raise ValueError("Strike price can only be set for executed trades")

    def compare_trade(self, other_trade: "TradeDetail") -> Dict[str, Tuple[Any, Any]]:
        differences = {}
        for field in self.__dataclass_fields__:
            if getattr(self, field) != getattr(other_trade, field):
                differences[field] = (getattr(self, field), getattr(other_trade, field))
        return differences
