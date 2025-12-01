import pytest
from datetime import date, datetime
from app.entities.trade_detail import Direction, InstrumentStyle, Currency
from app.services.api import TradeService
from app.storage.trade_detail_history import TradeDetailHistory
from app.storage.action_log import ActionLog, Action, State

class TestTradeService:
    @pytest.fixture
    def setup_details(self):
        return dict(
            state_validator="DRAFT",
            trade_id=1,
            entity="EntityA",
            counterparty="CounterpartyB",
            direction=Direction.BUY,
            style=InstrumentStyle.FORWARD,
            notion_curr=Currency.DOLLAR,
            notion_amount=10000.0,
            underlying=[Currency.DOLLAR, Currency.EURO],
            t_date=date.today(),
            v_date=date.today(),
            d_date=date.today(),
        )
    
    @pytest.fixture
    def setup_service(self):
        service = TradeService(trade_history=TradeDetailHistory(), action_log=ActionLog())
        return service
    
    @pytest.fixture()
    def setup_service_with_trade(self):
        service = TradeService(trade_history=TradeDetailHistory(), action_log=ActionLog())
        trade_id = service.save_draft(
            entity="EntityA",
            counterparty="CounterpartyB",
            direction="BUY",
            style="FORWARD",
            notion_curr="USD",
            notion_amount=10000.0,
            underlying=["USD", "EUR"],
            t_date=date.today(),
            v_date=date.today(),
            d_date=date.today(),
        )
        return service, trade_id
    
    def test_save_draft_valid(self, setup_details, setup_service):
        trade_id = setup_service.save_draft(
            entity=setup_details["entity"],
            counterparty=setup_details["counterparty"],
            direction="BUY",
            style="FORWARD",
            notion_curr="USD",
            notion_amount=setup_details["notion_amount"],
            underlying=["USD", "EUR"],
            t_date=setup_details["t_date"],
            v_date=setup_details["v_date"],
            d_date=setup_details["d_date"],
        )
        assert trade_id == 1
    
    def test_save_draft_invalid_enum(self, setup_details, setup_service):
        with pytest.raises(KeyError):
            setup_service.save_draft(
                entity=setup_details["entity"],
                counterparty=setup_details["counterparty"],
                direction="INVALID_DIRECTION",
                style="FORWARD",
                notion_curr="USD",
                notion_amount=setup_details["notion_amount"],
                underlying=["USD", "EUR"],
                t_date=setup_details["t_date"],
                v_date=setup_details["v_date"],
                d_date=setup_details["d_date"],
            )
        
    def test_submit_trade_for_approval_valid(self, setup_service_with_trade):
        setup_service, trade_id = setup_service_with_trade
        
        result = setup_service.submit_trade_for_approval(trade_id=trade_id, user_id=123, note="Submitting for approval")
        assert result is True
        log_entry = setup_service.action_log.action_log[trade_id][0]
        assert log_entry.trade_id == trade_id
        assert log_entry.user_id == 123
        assert log_entry.action == Action.SUBMIT
        assert log_entry.from_state == State.DRAFT
        assert log_entry.to_state == State.PENDING_APPROVE
        assert log_entry.note == "Submitting for approval"
        assert isinstance(log_entry.timestamp, datetime)
        assert log_entry.step == 1
    
    def test_submit_trade_for_approval_invalid_id(self, setup_service):
        result = setup_service.submit_trade_for_approval(trade_id=999, user_id=123, note="Submitting for approval")
        assert result is False
    
    def test_approve_trade_valid(self, setup_service_with_trade):
        setup_service, trade_id = setup_service_with_trade
    
        setup_service.submit_trade_for_approval(trade_id=trade_id, user_id=123, note="Submitting for approval")
        result = setup_service.approve_trade(trade_id=trade_id, user_id=456, note="Approving trade")
        assert result is True
        log_entry = setup_service.action_log.action_log[trade_id][1]
        assert log_entry.trade_id == trade_id
        assert log_entry.user_id == 456
        assert log_entry.action == Action.APPROVE
        assert log_entry.from_state == State.PENDING_APPROVE
        assert log_entry.to_state == State.APPROVED
        assert log_entry.note == "Approving trade"
        assert isinstance(log_entry.timestamp, datetime)
        assert log_entry.step == 2
    
    def test_approve_trade_incorrect_user_id(self, setup_service_with_trade):
        setup_service, trade_id = setup_service_with_trade
    
        setup_service.submit_trade_for_approval(trade_id=trade_id, user_id=123, note="Submitting for approval")
        result = setup_service.approve_trade(trade_id=trade_id, user_id=123, note="Approving trade")
        assert result is False
    
    def test_cancel_trade_valid(self, setup_service_with_trade):
        setup_service, trade_id = setup_service_with_trade
    
        setup_service.submit_trade_for_approval(trade_id=trade_id, user_id=123, note="Submitting for approval")
        result = setup_service.cancel_trade(trade_id=trade_id, user_id=789, note="Cancelling trade")
        assert result is True
        log_entry = setup_service.action_log.action_log[trade_id][1]
        assert log_entry.trade_id == trade_id
        assert log_entry.user_id == 789
        assert log_entry.action == Action.CANCEL
        assert log_entry.from_state == State.PENDING_APPROVE
        assert log_entry.to_state == State.CANCELLED
        assert log_entry.note == "Cancelling trade"
        assert isinstance(log_entry.timestamp, datetime)
        assert log_entry.step == 2
    
    def test_cancel_trade_invalid_id(self, setup_service):
        result = setup_service.cancel_trade(trade_id=999, user_id=789, note="Cancelling trade")
        assert result is False
    
    def test_cancel_trade_already_cancelled(self, setup_service_with_trade):
        setup_service, trade_id = setup_service_with_trade
    
        setup_service.submit_trade_for_approval(trade_id=trade_id, user_id=123, note="Submitting for approval")
        setup_service.cancel_trade(trade_id=trade_id, user_id=789, note="Cancelling trade")
        result = setup_service.cancel_trade(trade_id=trade_id, user_id=789, note="Cancelling trade again")
        assert result is False
    
    def test_update_trade_valid(self, setup_service_with_trade):
        setup_service, trade_id = setup_service_with_trade
    
        setup_service.submit_trade_for_approval(trade_id=trade_id, user_id=123, note="Submitting for approval")
        updates = {
            "notion_amount": 20000.0
        }
        result = setup_service.update_trade(trade_id=trade_id, user_id=456, note="Updating trade", **updates)
        assert result is True
        trade = setup_service.trade_history.store[trade_id][State.NEEDS_REAPPROVAL]
        assert trade.notion_amount == 20000.0
        log_entry = setup_service.action_log.get_latest_log(trade_id)
        assert log_entry.trade_id == trade_id
        assert log_entry.user_id == 456
        assert log_entry.action == Action.UPDATE
        assert log_entry.from_state == State.PENDING_APPROVE
        assert log_entry.to_state == State.NEEDS_REAPPROVAL
        assert log_entry.note == "Updating trade"
        assert isinstance(log_entry.timestamp, datetime)
        assert log_entry.step == 2
    
    def test_update_trade_invalid_updater(self, setup_service_with_trade):
        setup_service, trade_id = setup_service_with_trade
    
        setup_service.submit_trade_for_approval(trade_id=trade_id, user_id=123, note="Submitting for approval")
        updates = {
            "notion_amount": 20000.0
        }
        result = setup_service.update_trade(trade_id=trade_id, user_id=123, note="Updating trade", **updates)
        assert result is False
    
    def test_update_trade_invalid_key(self, setup_service_with_trade):
        setup_service, trade_id = setup_service_with_trade
    
        setup_service.submit_trade_for_approval(trade_id=trade_id, user_id=123, note="Submitting for approval")
        updates = {
            "invalid_key": 20000.0
        }
        result = setup_service.update_trade(trade_id=trade_id, user_id=456, note="Updating trade", **updates)
        assert result is False
    
        
        