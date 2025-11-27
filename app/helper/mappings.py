from app.entities.action_log_entry import Action, State

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

# shows what state an action transitions a trade to
action_to_state = {
    Action.SUBMIT: State.PENDING_APPROVE,
    Action.APPROVE: State.APPROVED,
    Action.BOOK: State.EXECUTED,
    Action.UPDATE: State.NEEDS_REAPPROVAL,
    Action.SENDTOEXECUTE: State.SENT_COUNTERPARTY,
}
