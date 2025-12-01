from datetime import datetime
from typing import Dict, List, Optional

from app.entities.action_log_entry import Action, ActionLogEntry, State
from app.helper import mappings


class ActionLog:
    # Assuming all data has been validated from here
    def __init__(self):
        self.action_log: Dict[int, List[ActionLogEntry]] = {}

    def record(
        self, trade_id: int, user_id: int, action: Action, from_state: State, note: str
    ):
        """Record a new action log entry for a trade."""
        entries = self.action_log.setdefault(trade_id, [])
        step = len(entries) + 1
        to_state = mappings.action_to_state[action]
        entry = ActionLogEntry(
            step=step,
            trade_id=trade_id,
            user_id=user_id,
            action=action,
            from_state=from_state,
            to_state=to_state,
            timestamp=datetime.now(),
            note=note,
        )
        entries.append(entry)

    def get_latest_log(self, trade_id: int) -> Optional[ActionLogEntry]:
        """Get the most recent action log entry for a trade."""
        logs = list(self.action_log.get(trade_id, []))
        return logs[-1] if logs else None

    def get_logs(self, trade_id: int) -> List[ActionLogEntry]:
        """Get all action log entries for a trade."""
        return list(self.action_log.get(trade_id, []))
