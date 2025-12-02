### API Methods

#### 1. `save_draft()`

Create a new trade draft.

**Parameters:**
- `entity` (str): Trading entity name
- `counterparty` (str): Counterparty identifier
- `direction` (str): Trade direction ("BUY" or "SELL")
- `style` (str): Instrument style ("FORWARD", "OPTION", etc.)
- `notion_curr` (str): Notional currency ("USD", "EUR", etc.)
- `notion_amount` (float): Notional amount
- `underlying` (list): List of two underlying currencies
- `t_date` (date): Trade date
- `v_date` (date): Valuation date
- `d_date` (date): Delivery date

**Returns:** `int` - Trade ID

**Example:**
```python
from datetime import date

trade_id = service.save_draft(
    entity="EntityA",
    counterparty="CounterpartyB",
    direction="BUY",
    style="FORWARD",
    notion_curr="USD",
    notion_amount=10000.0,
    underlying=["USD", "EUR"],
    t_date=date(2025, 12, 1),
    v_date=date(2025, 12, 15),
    d_date=date(2025, 12, 30)
)
# Returns: 1
```

---

#### 2. `submit_trade_for_approval()`

Submit a draft trade for approval.

**Parameters:**
- `trade_id` (int): ID of the trade to submit
- `user_id` (int): User submitting the trade
- `note` (str): Submission note

**Returns:** `bool` - True if successful

**Example:**
```python
success = service.submit_trade_for_approval(
    trade_id=1,
    user_id=123,
    note="Ready for approval"
)
# Returns: True
```

---

#### 3. `approve_trade()`

Approve a pending trade. The approver must be different from the submitter.

**Parameters:**
- `trade_id` (int): ID of the trade to approve
- `user_id` (int): User approving (must differ from submitter)
- `note` (str): Approval note

**Returns:** `bool` - True if successful

**Example:**
```python
success = service.approve_trade(
    trade_id=1,
    user_id=456,
    note="Approved for execution"
)
# Returns: True
```

---

#### 4. `update_trade()`

Update a pending trade. Moves the trade to NEEDS_REAPPROVAL state.

**Parameters:**
- `trade_id` (int): ID of the trade to update
- `user_id` (int): User updating (must differ from submitter)
- `note` (str): Update note
- `**updates` (dict): Key-value pairs of fields to update

**Returns:** `bool` - True if successful

**Example:**
```python
success = service.update_trade(
    trade_id=1,
    user_id=456,
    note="Updated notional amount",
    notion_amount=20000.0,
    entity="EntityB"
)
# Returns: True
```

---

#### 5. `cancel_trade()`

Cancel a trade that is not yet executed or already cancelled.

**Parameters:**
- `trade_id` (int): ID of the trade to cancel
- `user_id` (int): User cancelling
- `note` (str): Cancellation note

**Returns:** `bool` - True if successful

**Example:**
```python
success = service.cancel_trade(
    trade_id=1,
    user_id=789,
    note="Client request"
)
# Returns: True
```

---

#### 6. `sent_trade_to_counterparty()`

Send an approved trade to counterparty for execution and simulate execution.

**Parameters:**
- `trade_id` (int): ID of the trade to send
- `user_id` (int): User sending the trade
- `note` (str): Execution note
- `strike` (float, optional): Execution strike price (simulated if not provided)

**Returns:** `bool` - True if successful

**Example:**
```python
# With specific strike
success = service.sent_trade_to_counterparty(
    trade_id=1,
    user_id=123,
    note="Sent for execution",
    strike=1.0534
)

# With simulated strike
success = service.sent_trade_to_counterparty(
    trade_id=1,
    user_id=123,
    note="Sent for execution"
)
# Returns: True
```

---

#### 7. `book_trade()`

Book an executed trade (adds audit entry).

**Parameters:**
- `trade_id` (int): ID of the trade to book
- `user_id` (int): User booking
- `note` (str): Booking note

**Returns:** `bool` - True if successful

**Example:**
```python
success = service.book_trade(
    trade_id=1,
    user_id=456,
    note="Booked to system"
)
# Returns: True
```

---

#### 8. `view_trades()`

View all trades with their latest states.

**Returns:** `list[str]` - List of trade summaries

**Example:**
```python
trades = service.view_trades()
# Returns: [
#   "Trade_ID: 1 | Latest_State: EXECUTED | Last_Updated_Timestamp: 2025-12-01 10:30:00"
# ]
```

---

#### 9. `view_action_log()`

View complete action log for a specific trade.

**Parameters:**
- `trade_id` (int): Trade ID to view

**Returns:** `list[str]` - List of action log entries

**Example:**
```python
logs = service.view_action_log(trade_id=1)
# Returns: [
#   "Step: 1 | User_ID: 123 | Action: SUBMIT | From_State: DRAFT | To_State: PENDING_APPROVE | ...",
#   "Step: 2 | User_ID: 456 | Action: APPROVE | From_State: PENDING_APPROVE | To_State: APPROVED | ..."
# ]
```

---

#### 10. `view_trade_states()`

View all states a trade has been through.

**Parameters:**
- `trade_id` (int): Trade ID to view

**Returns:** `list[str]` - List of states

**Example:**
```python
states = service.view_trade_states(trade_id=1)
# Returns: ["| State |", "DRAFT", "PENDING_APPROVE", "APPROVED", "EXECUTED"]
```

---

#### 11. `view_trade_details()`

View detailed information about a trade at a specific state.

**Parameters:**
- `trade_id` (int): Trade ID to view
- `state` (State): State to view

**Returns:** `list[str]` - List of trade details

**Example:**
```python
from app.storage.action_log import State

details = service.view_trade_details(trade_id=1, state=State.APPROVED)
# Returns: [
#   "Trade ID: 1",
#   "State: APPROVED",
#   "Entity: EntityA",
#   "Counterparty: CounterpartyB",
#   ...
# ]
```

---

#### 12. `compare_trade_versions()`

Compare two versions of a trade to see what changed.

**Parameters:**
- `trade_id` (int): Trade ID to compare
- `state1` (State): First state
- `state2` (State): Second state

**Returns:** `dict` - Dictionary of differences

**Example:**
```python
from app.storage.action_log import State

diffs = service.compare_trade_versions(
    trade_id=1,
    state1=State.PENDING_APPROVE,
    state2=State.NEEDS_REAPPROVAL
)
# Returns: {"notion_amount": (10000.0, 20000.0)}
```