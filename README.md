# Trade Approval System API

A Python-based trade approval system that manages the lifecycle of financial trades from draft creation through execution and booking.

## Overview

The Trade Approval System provides a comprehensive API for managing trade workflows with built-in validation, state management, and audit logging. The system enforces business rules and tracks all trade modifications through a multi-step approval process.

## Features

- **Draft Management**: Create and save trade drafts with validation
- **Multi-Step Approval**: Submit trades for approval with user authorization checks
- **State Tracking**: Maintain complete trade history across all states
- **Audit Logging**: Track all actions with timestamps and user attribution
- **Trade Updates**: Modify pending trades with automatic reapproval workflows
- **Execution Simulation**: Simulate counterparty execution with strike price updates
- **Version Comparison**: Compare trade details across different states

## Installation

```bash
cd trade_approve_app

# Build Docker containers
docker-compose build

# To run cli session
docker compose run --rm cli

# To run tests
docker compose run --rm tests
```

## API Documentation

### Core Classes

#### `TradeService`

The main API class that orchestrates all trade operations.

**Initialization:**
```python
from app.services.api import TradeService
from app.storage.trade_detail_history import TradeDetailHistory
from app.storage.action_log import ActionLog

service = TradeService(
    trade_history=TradeDetailHistory(),
    action_log=ActionLog()
)
```

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

---

## Complete Usage Scenario
### Note
This usage would be running from a python terminal, trades and logs would be stored in memory as defined in the spec for the case study
Further down this README as an extra I set up a cli client tool where a user can interactively go through the trade process more visually
On another note this api could easily be wrapped in gRPC and be portable across different client languages if we were to persist the action log and trade details for each trade on a database 
(more on potential architecture in DESIGN_NOTES.md)

### Scenario: Creating and Approving a Trade

```python
from datetime import date
from app.services.api import TradeService
from app.storage.trade_detail_history import TradeDetailHistory
from app.storage.action_log import ActionLog

# Initialize service
service = TradeService(
    trade_history=TradeDetailHistory(),
    action_log=ActionLog()
)

# Step 1: User 123 creates a draft trade
trade_id = service.save_draft(
    entity="BankA",
    counterparty="BankB",
    direction="BUY",
    style="FORWARD",
    notion_curr="USD",
    notion_amount=1000000.0,
    underlying=["USD", "EUR"],
    t_date=date(2025, 12, 1),
    v_date=date(2025, 12, 15),
    d_date=date(2025, 12, 30)
)
print(f"Draft created: {trade_id}")  # Output: Draft created: 1

# Step 2: User 123 submits for approval
service.submit_trade_for_approval(
    trade_id=trade_id,
    user_id=123,
    note="Please review this forward contract"
)

# Step 3: User 456 (different user) approves the trade
service.approve_trade(
    trade_id=trade_id,
    user_id=456,
    note="Terms look good"
)

# Step 4: User 123 sends trade to counterparty for execution
service.sent_trade_to_counterparty(
    trade_id=trade_id,
    user_id=123,
    note="Executing trade",
    strike=1.0850  # EUR/USD rate
)

# Step 5: User 456 books the executed trade
service.book_trade(
    trade_id=trade_id,
    user_id=456,
    note="Trade confirmed and booked"
)

# View the complete audit trail
logs = service.view_action_log(trade_id)
for log in logs:
    print(log)
```

---

### Scenario: Updating a Pending Trade

```python
# User 123 submits a trade
trade_id = service.save_draft(
    entity="BankA",
    counterparty="BankB",
    direction="BUY",
    style="FORWARD",
    notion_curr="USD",
    notion_amount=500000.0,
    underlying=["USD", "EUR"],
    t_date=date(2025, 12, 1),
    v_date=date(2025, 12, 15),
    d_date=date(2025, 12, 30)
)
service.submit_trade_for_approval(trade_id=trade_id, user_id=123, note="Initial submission")

# User 456 notices an issue and updates the notional
service.update_trade(
    trade_id=trade_id,
    user_id=456,
    note="Corrected notional amount",
    notion_amount=750000.0
)

# Compare versions to see what changed
from app.storage.action_log import State
diffs = service.compare_trade_versions(
    trade_id=trade_id,
    state1=State.PENDING_APPROVE,
    state2=State.NEEDS_REAPPROVAL
)
print(diffs)  # Output: {"notion_amount": (500000.0, 750000.0)}

# User 123 (original submitter) must re-approve
service.approve_trade(
    trade_id=trade_id,
    user_id=123,
    note="Approved corrected amount"
)
```

---

## Command Line Interface

The system includes a CLI for interactive usage:

### Interactive Mode
```bash
# Run the interactive CLI in Docker
docker-compose run --rm cli
```

### Single Commands
```bash
# Create a draft
save-draft --entity BankA --counterparty BankB --direction BUY --style FORWARD --notion-curr USD --notion-amount 1000000 --underlying USD EUR --t-date 2025-12-01 --v-date 2025-12-15 --d-date 2025-12-30

save-draft --entity BankC --counterparty BankD --direction SELL --style FORWARD --notion-curr USD --notion-amount 50000 --underlying USD EUR --t-date 2025-12-01 --v-date 2025-12-15 --d-date 2025-12-30

# Submit for approval
submit 1 --user-id 123 --note "Ready for review"
submit 2 --user-id 123 --note "Ready for review"

# Update a trade by approver
update 1 --user-id 456 --note "Updated amount" --notion-amount 20000

# Approve trade by user who submitted the trade
approve 1 --user-id 123 --note "Approved"

# Send to counterparty
send-to-counterparty 1 --user-id 456 --note "Executing with counterparty" --strike 1.0850
send-to-counterparty 2 --user-id 123 --note "Executing with counterparty"

# Book trade
book 1 --user-id 456 --note "Trade booked"
book 2 --user-id 456 --note "Trade booked"

# View all trades
view-trades

# View action log
view-action-log 1

# View all states of a trade
view-trade-states 1

# View trade detail for a specific state
view-trade-details 1 NEEDS_REAPPROVAL

# Compare versions
compare-trade-versions 1 PENDING_APPROVE NEEDS_REAPPROVAL
```

---

## Trade States

The system manages trades through the following states:

1. **DRAFT**: Initial state when trade is created
2. **PENDING_APPROVE**: Trade submitted and awaiting approval
3. **NEEDS_REAPPROVAL**: Trade was updated and needs re-approval
4. **APPROVED**: Trade approved and ready for execution
5. **SENT_COUNTERPARTY**: Trade sent to counterparty
6. **EXECUTED**: Trade executed with strike price
7. **CANCELLED**: Trade cancelled by user

---

## Testing

```bash
# Run all tests in Docker
docker-compose run --rm test

# Run specific test file
docker-compose run --rm test pytest tests/services/test_api.py -v

# Run with verbose output
docker-compose run --rm test pytest -v

# Run with coverage report
docker-compose run --rm test pytest --cov=app --cov-report=term-missing
```

---

## Project Structure

```
trade_approve_app/
├── app/
│   ├── entities/          # Domain models (TradeDetail, ActionLogEntry, User)
│   ├── services/          # Business logic (TradeService, Validator, TradeExecutor)
│   ├── storage/           # Data storage (TradeDetailHistory, ActionLog)
│   ├── helper/            # Utilities (mappings)
│   └── main.py            # CLI interface
├── tests/                 # Unit tests
└── README.md             # This file
```


---

## Contact

Zach Hyland
