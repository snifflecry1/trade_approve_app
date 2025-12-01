#!/usr/bin/env python3
"""
Trade Approval CLI - Command-line interface for the trade approval system.
"""
import argparse
import shlex
import sys
from datetime import date

from app.services.api import TradeService
from app.storage.action_log import ActionLog
from app.storage.trade_detail_history import TradeDetailHistory

# Global service instance (maintains state across commands in same process)
_service = None


def get_service():
    """Get or create the TradeService singleton."""
    global _service
    if _service is None:
        _service = TradeService(
            trade_history=TradeDetailHistory(), action_log=ActionLog()
        )
    return _service


def cmd_save_draft(args):
    """Save a new trade draft."""
    service = get_service()
    trade_id = service.save_draft(
        entity=args.entity,
        counterparty=args.counterparty,
        direction=args.direction,
        style=args.style,
        notion_curr=args.notion_curr,
        notion_amount=args.notion_amount,
        underlying=args.underlying,
        t_date=date.fromisoformat(args.t_date),
        v_date=date.fromisoformat(args.v_date),
        d_date=date.fromisoformat(args.d_date),
    )
    print(f"✓ Draft saved with Trade ID: {trade_id}")
    return trade_id


def cmd_submit(args):
    """Submit a trade for approval."""
    service = get_service()
    success = service.submit_trade_for_approval(
        trade_id=args.trade_id, user_id=args.user_id, note=args.note or ""
    )
    if success:
        print(f"✓ Trade {args.trade_id} submitted for approval")
    else:
        print(f"✗ Failed to submit trade {args.trade_id}")
        sys.exit(1)


def cmd_approve(args):
    """Approve a pending trade."""
    service = get_service()
    success = service.approve_trade(
        trade_id=args.trade_id, user_id=args.user_id, note=args.note or ""
    )
    if success:
        print(f"✓ Trade {args.trade_id} approved")
    else:
        print(f"✗ Failed to approve trade {args.trade_id}")
        sys.exit(1)


def cmd_cancel(args):
    """Cancel a trade."""
    service = get_service()
    success = service.cancel_trade(
        trade_id=args.trade_id, user_id=args.user_id, note=args.note or ""
    )
    if success:
        print(f"✓ Trade {args.trade_id} cancelled")
    else:
        print(f"✗ Failed to cancel trade {args.trade_id}")
        sys.exit(1)


def cmd_update(args):
    """Update a trade."""
    service = get_service()

    # Build updates dict from provided arguments
    updates = {}
    if args.notion_amount is not None:
        updates["notion_amount"] = args.notion_amount
    if args.entity is not None:
        updates["entity"] = args.entity
    if args.counterparty is not None:
        updates["counterparty"] = args.counterparty
    # Add more fields as needed

    success = service.update_trade(
        trade_id=args.trade_id, user_id=args.user_id, note=args.note or "", **updates
    )
    if success:
        print(f"✓ Trade {args.trade_id} updated")
    else:
        print(f"✗ Failed to update trade {args.trade_id}")
        sys.exit(1)


def cmd_send_to_counterparty(args):
    """Send a trade to counterparty for execution."""
    service = get_service()
    success = service.sent_trade_to_counterparty(
        trade_id=args.trade_id,
        user_id=args.user_id,
        note=args.note or "",
        strike=args.strike,
    )
    if success:
        latest_log = service.action_log.get_latest_log(args.trade_id)
        if latest_log:
            trade = service.trade_history.store[args.trade_id][latest_log.to_state]
            print(
                f"✓ Trade {args.trade_id} sent to counterparty and executed at strike {trade.strike}"
            )
        else:
            print(f"✓ Trade {args.trade_id} sent to counterparty")
    else:
        print(f"✗ Failed to send trade {args.trade_id} to counterparty")
        sys.exit(1)


def cmd_book(args):
    """Book an executed trade."""
    service = get_service()
    success = service.book_trade(
        trade_id=args.trade_id, user_id=args.user_id, note=args.note or ""
    )
    if success:
        print(f"✓ Trade {args.trade_id} booked")
    else:
        print(f"✗ Failed to book trade {args.trade_id}")
        sys.exit(1)


def cmd_view_trades(args):
    """View all trades and their current states."""
    service = get_service()
    trades = service.view_trades()
    if trades:
        print("\nCurrent Trades:")
        print("=" * 80)
        for trade_info in trades:
            print(trade_info)
        print("=" * 80)
    else:
        print("No trades found.")


def cmd_view_action_log(args):
    """View the action log for a specific trade."""
    service = get_service()
    logs = service.view_action_log(trade_id=args.trade_id)
    if logs:
        print(f"\nAction Log for Trade {args.trade_id}:")
        print("=" * 120)
        for log_entry in logs:
            print(log_entry)
        print("=" * 120)
    else:
        print(f"No action log found for trade {args.trade_id}.")


def cmd_view_trade_states(args):
    """View all states for a specific trade."""
    service = get_service()
    states = service.view_trade_states(trade_id=args.trade_id)
    if states:
        print(f"\nAll States for Trade {args.trade_id}:")
        print("=" * 80)
        for state_info in states:
            print(state_info)
        print("=" * 80)
    else:
        print(f"No states found for trade {args.trade_id}.")


def cmd_view_trade_details(args):
    """View details of a trade at a specific state."""
    from app.storage.action_log import State

    service = get_service()
    try:
        state = State[args.state.upper()]
    except KeyError:
        print(
            f"✗ Invalid state: {args.state}. Valid states: {', '.join([s.name for s in State])}"
        )
        sys.exit(1)

    details = service.view_trade_details(trade_id=args.trade_id, state=state)
    if details:
        print(f"\nTrade Details for Trade {args.trade_id} at State {state.name}:")
        print("=" * 80)
        for detail_line in details:
            print(detail_line)
        print("=" * 80)
    else:
        print(f"No details found for trade {args.trade_id} at state {state.name}.")


def cmd_compare_trade_versions(args):
    """Compare two versions of a trade by their states."""
    from app.storage.action_log import State

    service = get_service()
    try:
        state1 = State[args.state1.upper()]
        state2 = State[args.state2.upper()]
    except KeyError as e:
        print(
            f"✗ Invalid state: {e}. Valid states: {', '.join([s.name for s in State])}"
        )
        sys.exit(1)

    diffs = service.compare_trade_versions(
        trade_id=args.trade_id, state1=state1, state2=state2
    )
    if diffs:
        print(
            f"\nDifferences between Trade {args.trade_id} at {state1.name} vs {state2.name}:"
        )
        print("=" * 100)
        for field, (val1, val2) in diffs.items():
            print(f"{field}: '{val1}' , '{val2}'")
        print("=" * 100)
    else:
        print(
            f"No differences found between states {state1.name} and {state2.name} for trade {args.trade_id}."
        )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Trade Approval System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Start interactive REPL mode"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # save-draft command
    draft_parser = subparsers.add_parser(
        "save-draft",
        help="Save a new trade draft",
        usage="save-draft --entity EntityA --counterparty CounterpartyB --direction BUY --style FORWARD --notion-curr USD --notion-amount 10000 --underlying USD EUR --t-date 2025-12-01 --v-date 2025-12-15 --d-date 2025-12-30",
    )
    draft_parser.add_argument("--entity", required=True, help="Trading entity")
    draft_parser.add_argument("--counterparty", required=True, help="Counterparty name")
    draft_parser.add_argument(
        "--direction", required=True, choices=["BUY", "SELL"], help="Trade direction"
    )
    draft_parser.add_argument(
        "--style", required=True, help="Instrument style (e.g., FORWARD, OPTION)"
    )
    draft_parser.add_argument(
        "--notion-curr", required=True, help="Notional currency (e.g., USD, EUR)"
    )
    draft_parser.add_argument(
        "--notion-amount", type=float, required=True, help="Notional amount"
    )
    draft_parser.add_argument(
        "--underlying", nargs=2, required=True, help="Two underlying currencies"
    )
    draft_parser.add_argument("--t-date", required=True, help="Trade date (YYYY-MM-DD)")
    draft_parser.add_argument(
        "--v-date", required=True, help="Valuation date (YYYY-MM-DD)"
    )
    draft_parser.add_argument(
        "--d-date", required=True, help="Delivery date (YYYY-MM-DD)"
    )
    draft_parser.set_defaults(func=cmd_save_draft)

    # submit command
    submit_parser = subparsers.add_parser(
        "submit",
        help="Submit a trade for approval",
        usage='submit 1 --user-id 123 --note "Ready for review"',
    )
    submit_parser.add_argument("trade_id", type=int, help="Trade ID to submit")
    submit_parser.add_argument(
        "--user-id", type=int, required=True, help="User ID submitting"
    )
    submit_parser.add_argument("--note", help="Optional note")
    submit_parser.set_defaults(func=cmd_submit)

    # approve command
    approve_parser = subparsers.add_parser(
        "approve",
        help="Approve a pending trade",
        usage='approve 1 --user-id 456 --note "Approved"',
    )
    approve_parser.add_argument("trade_id", type=int, help="Trade ID to approve")
    approve_parser.add_argument(
        "--user-id", type=int, required=True, help="User ID approving"
    )
    approve_parser.add_argument("--note", help="Optional note")
    approve_parser.set_defaults(func=cmd_approve)

    # cancel command
    cancel_parser = subparsers.add_parser(
        "cancel",
        help="Cancel a trade",
        usage='cancel 1 --user-id 789 --note "Client request"',
    )
    cancel_parser.add_argument("trade_id", type=int, help="Trade ID to cancel")
    cancel_parser.add_argument(
        "--user-id", type=int, required=True, help="User ID cancelling"
    )
    cancel_parser.add_argument("--note", help="Optional note")
    cancel_parser.set_defaults(func=cmd_cancel)

    # update command
    update_parser = subparsers.add_parser(
        "update",
        help="Update a trade",
        usage='update 1 --user-id 456 --note "Updated amount" --notion-amount 20000',
    )
    update_parser.add_argument("trade_id", type=int, help="Trade ID to update")
    update_parser.add_argument(
        "--user-id", type=int, required=True, help="User ID updating"
    )
    update_parser.add_argument("--note", help="Optional note")
    update_parser.add_argument(
        "--notion-amount", type=float, help="New notional amount"
    )
    update_parser.add_argument("--entity", help="New entity")
    update_parser.add_argument("--counterparty", help="New counterparty")
    update_parser.set_defaults(func=cmd_update)

    # send-to-counterparty command
    send_parser = subparsers.add_parser(
        "send-to-counterparty",
        help="Send trade to counterparty for execution",
        usage='send-to-counterparty 1 --user-id 123 --note "Executing" --strike 1.0850',
    )
    send_parser.add_argument("trade_id", type=int, help="Trade ID to send")
    send_parser.add_argument(
        "--user-id", type=int, required=True, help="User ID sending"
    )
    send_parser.add_argument("--note", help="Optional note")
    send_parser.add_argument(
        "--strike",
        type=float,
        help="Execution strike price (optional, will simulate if not provided)",
    )
    send_parser.set_defaults(func=cmd_send_to_counterparty)

    # book command
    book_parser = subparsers.add_parser(
        "book",
        help="Book an executed trade",
        usage='book 1 --user-id 456 --note "Trade booked"',
    )
    book_parser.add_argument("trade_id", type=int, help="Trade ID to book")
    book_parser.add_argument(
        "--user-id", type=int, required=True, help="User ID booking"
    )
    book_parser.add_argument("--note", help="Optional note")
    book_parser.set_defaults(func=cmd_book)

    # view-trades command
    view_parser = subparsers.add_parser(
        "view-trades", help="View all trades and their states", usage="view-trades"
    )
    view_parser.set_defaults(func=cmd_view_trades)

    # view-action-log command
    log_parser = subparsers.add_parser(
        "view-action-log",
        help="View action log for a specific trade",
        usage="view-action-log 1",
    )
    log_parser.add_argument(
        "trade_id", type=int, help="Trade ID to view action log for"
    )
    log_parser.set_defaults(func=cmd_view_action_log)

    # view-trade-states command
    states_parser = subparsers.add_parser(
        "view-trade-states",
        help="View all states for a specific trade",
        usage="view-trade-states 1",
    )
    states_parser.add_argument("trade_id", type=int, help="Trade ID to view states for")
    states_parser.set_defaults(func=cmd_view_trade_states)

    # view-trade-details command
    details_parser = subparsers.add_parser(
        "view-trade-details",
        help="View trade details at a specific state",
        usage="view-trade-details 1 APPROVED",
    )
    details_parser.add_argument("trade_id", type=int, help="Trade ID to view")
    details_parser.add_argument(
        "state", help="State to view (e.g., DRAFT, PENDING_APPROVE, APPROVED, EXECUTED)"
    )
    details_parser.set_defaults(func=cmd_view_trade_details)

    # compare-trade-versions command
    compare_parser = subparsers.add_parser(
        "compare-trade-versions",
        help="Compare two versions of a trade",
        usage="compare-trade-versions 1 PENDING_APPROVE NEEDS_REAPPROVAL",
    )
    compare_parser.add_argument("trade_id", type=int, help="Trade ID to compare")
    compare_parser.add_argument("state1", help="First state to compare")
    compare_parser.add_argument("state2", help="Second state to compare")
    compare_parser.set_defaults(func=cmd_compare_trade_versions)

    args = parser.parse_args()

    # Start interactive mode if requested
    if args.interactive:
        interactive_mode(parser, subparsers)
        return

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute the command
    args.func(args)


def interactive_mode(parser, subparsers):
    """Run interactive REPL mode."""
    print("=" * 60)
    print("Trade Approval System - Interactive Mode")
    print("=" * 60)
    print("State is preserved between commands in this session.")
    print("Type 'help' for available commands or 'exit' to quit.\n")

    # Initialize service once for the entire session
    get_service()

    while True:
        try:
            # Get user input
            user_input = input("trade> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting interactive mode.")
                break

            # Handle help command
            if user_input.lower() in ["help", "?"]:
                parser.print_help()
                continue

            # Handle "help <command>" to show specific command help
            if user_input.lower().startswith("help "):
                command_name = user_input.split(maxsplit=1)[1].strip()
                if command_name in subparsers.choices:
                    subparsers.choices[command_name].print_help()
                else:
                    print(f"Unknown command: {command_name}")
                    print(f"Available commands: {', '.join(subparsers.choices.keys())}")
                continue

            # Parse the command
            try:
                args = shlex.split(user_input)
                parsed_args = parser.parse_args(args)

                if hasattr(parsed_args, "func"):
                    parsed_args.func(parsed_args)
                else:
                    print("Unknown command. Type 'help' for available commands.")

            except SystemExit:
                # argparse calls sys.exit on error, catch it to keep REPL alive
                continue
            except Exception as e:
                print(f"Error: {e}")

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
            continue
        except EOFError:
            print("\nExiting interactive mode.")
            break


if __name__ == "__main__":
    main()
