from app.entities.action_log_entry import Action, State, ActionLogEntry
from app.helper import mappings
from typing import List, Dict
from datetime import datetime


class ActionLog:
    # Assuming all data has been validated from here
    def __init__(self):
        self.action_log: Dict[int, List[ActionLogEntry]] = {}

    def record(
        self, trade_id: int, user_id: str, action: Action, from_state: State, note: str
    ):
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

    def get_logs(self, trade_id:int) -> List[ActionLogEntry]:
        return list(self.action_log.get(trade_id, []))

