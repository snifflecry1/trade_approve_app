import pytest
from datetime import datetime
from app.entities.action_log_entry import ActionLogEntry, Action, State

class TestActionLogEntry:
    @pytest.fixture
    def log_factory(self):
        def _make_log(**override):
            base_kwargs = dict(
                step=1,
                trade_id=1,
                user_id=123,  # Changed to int for consistency
                action=Action.SUBMIT,
                from_state=State.DRAFT,
                to_state=State.PENDING_APPROVE,
                timestamp=datetime.now(),
                note="Initial submission",
            )
            base_kwargs.update(override)
            return ActionLogEntry(**base_kwargs)  # type: ignore
        return _make_log

    def test_valid_action_log_entry(self, log_factory):
        """Test that a valid action log entry can be created with all required fields."""
        log_entry = log_factory()
        assert log_entry.step == 1
        assert log_entry.trade_id == 1
        assert log_entry.user_id == 123
        assert log_entry.action == Action.SUBMIT
        assert log_entry.from_state == State.DRAFT
        assert log_entry.to_state == State.PENDING_APPROVE
        assert isinstance(log_entry.timestamp, datetime)
        assert log_entry.note == "Initial submission"
    
    def test_action_log_entry_invalid_action(self, log_factory):
        """Test that creating an action log entry with invalid action raises TypeError."""
        with pytest.raises(TypeError):
            log_factory(action="INVALID_ACTION")
    
    def test_action_log_entry_invalid_from_state(self, log_factory):
        """Test that creating an action log entry with invalid from_state raises TypeError."""
        with pytest.raises(TypeError):
            log_factory(from_state="INVALID_STATE")
    
    def test_action_log_entry_invalid_to_state(self, log_factory):
        """Test that creating an action log entry with invalid to_state raises TypeError."""
        with pytest.raises(TypeError):
            log_factory(to_state="INVALID_STATE")
    
    def test_action_log_entry_invalid_timestamp(self, log_factory):
        """Test that creating an action log entry with invalid timestamp raises TypeError."""
        with pytest.raises(TypeError):
            log_factory(timestamp="2023-10-10 10:00:00")
    
    def test_action_log_entry_invalid_step(self, log_factory):
        """Test that creating an action log entry with invalid step raises ValueError."""
        with pytest.raises(ValueError):
            log_factory(step=0)
    
    def test_action_log_entry_invalid_note_type(self, log_factory):
        """Test that creating an action log entry with invalid note type raises TypeError."""
        with pytest.raises(TypeError):
            log_factory(note=12345)
    
    def test_action_log_entry_invalid_user_id(self, log_factory):
        """Test that creating an action log entry with invalid user_id raises ValueError."""
        with pytest.raises(ValueError):
            log_factory(user_id=-1)
    