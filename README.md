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

## Contact

Zach Hyland
