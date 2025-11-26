from dataclasses import dataclass
from enum import Enum


class Role(Enum):
    REQUESTER = "Requester"
    APPROVER = "Approver"

@dataclass
class User:
    id: int
    name: str
    role: Role