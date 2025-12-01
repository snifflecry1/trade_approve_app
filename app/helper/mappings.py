from app.entities.action_log_entry import Action, State
from app.entities.trade_detail import Currency, InstrumentStyle, Direction

# lists available actions from a current state
state_available_actions = {
    State.DRAFT: (Action.SUBMIT),
    State.PENDING_APPROVE: (Action.APPROVE, Action.CANCEL),
    State.APPROVED: (Action.SENDTOEXECUTE, Action.CANCEL),
    State.NEEDS_REAPPROVAL: (Action.APPROVE, Action.CANCEL),
    State.SENT_COUNTERPARTY: (Action.BOOK, Action.CANCEL),
    State.EXECUTED: (),
    State.CANCELLED: (),
}

enum_to_state_str = {
    State.DRAFT: "DRAFT",
    State.PENDING_APPROVE: "PENDING_APPROVAL",
    State.NEEDS_REAPPROVAL: "NEEDS_REAPPROVAL",
    State.APPROVED: "APPROVED",
    State.SENT_COUNTERPARTY: "SENT_COUNTERPARTY",
    State.EXECUTED: "EXECUTED",
    State.CANCELLED: "CANCELLED",
}

# shows what state an action transitions a trade to
action_to_state = {
    Action.SUBMIT: State.PENDING_APPROVE,
    Action.APPROVE: State.APPROVED,
    Action.BOOK: State.EXECUTED,
    Action.UPDATE: State.NEEDS_REAPPROVAL,
    Action.SENDTOEXECUTE: State.SENT_COUNTERPARTY,
    Action.CANCEL: State.CANCELLED,
}

currency_stubs = {
    "EUR": Currency.EURO,
    "GBP": Currency.POUND,
    "USD": Currency.DOLLAR,
}

currency_stub_sign = {
    Currency.DOLLAR: "$",
    Currency.EURO: "€",
    Currency.POUND: "£",
}

style_stubs = {
    "FORWARD": InstrumentStyle.FORWARD,
}

direction_stubs = {
    "BUY": Direction.BUY,
    "SELL": Direction.SELL,
}