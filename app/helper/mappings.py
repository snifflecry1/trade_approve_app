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
state_str_to_enum = {
    "DRAFT": State.DRAFT,
    "PENDING_APPROVAL": State.PENDING_APPROVE,
    "NEEDS_REAPPROVAL": State.NEEDS_REAPPROVAL,
    "APPROVED": State.APPROVED,
    "SENT_COUNTERPARTY": State.SENT_COUNTERPARTY,
    "EXECUTED": State.EXECUTED,
    "CANCELLED": State.CANCELLED,
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