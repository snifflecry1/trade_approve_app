from app.storage.action_log import ActionLog, Action, State
import pytest

class TestActionLog:
    @pytest.fixture
    def action_log_instance(self):
        return ActionLog()
    
    def test_initialization(self, action_log_instance):
        assert action_log_instance.action_log == {}

    def test_get_logs_non_existent_trade(self, action_log_instance):
        """Test getting logs for a trade ID that doesn't exist."""
        non_existent_id = 9999
        logs = action_log_instance.get_logs(non_existent_id)
        assert logs == []

    def test_record_multiple_trades_separate_logs(self, action_log_instance):
        trade_id_1 = 101
        trade_id_2 = 102
        user_id = 3

        action_log_instance.record(trade_id_1, user_id, Action.SUBMIT, State.DRAFT, "T1 submitted")
        action_log_instance.record(trade_id_2, user_id, Action.SUBMIT, State.DRAFT, "T2 submitted")
        action_log_instance.record(trade_id_1, user_id, Action.APPROVE, State.PENDING_APPROVE, "Approved")

        logs_t1 = action_log_instance.get_logs(trade_id_1)
        logs_t2 = action_log_instance.get_logs(trade_id_2)

        assert len(logs_t1) == 2
        assert len(logs_t2) == 1
    
    def test_record_trade_correct_transition(self, action_log_instance):
        trade_id_1 = 1
        user_id = 3
        action_log_instance.record(trade_id_1, user_id, Action.SUBMIT, State.DRAFT, "T1 submitted")
        logs_t1 = action_log_instance.get_logs(trade_id_1)
        assert len(logs_t1) == 1
        assert logs_t1[0].to_state == State.PENDING_APPROVE

