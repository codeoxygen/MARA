from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime

class WSNodeStatus(str, Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"
    WAITING = "waiting"

class WSDomain(str, Enum):
    PLANNER = "planner"
    COMMS = "comms"
    ANALYTICS = "analytics"
    PRE_GRAPH = "pre_graph"

class WSEvent(BaseModel):
    """WebSocket event for real-time graph execution streaming"""
    session_id: str
    node: str
    status: WSNodeStatus
    domain: WSDomain
    payload: Dict[str, Any] = {}
    iteration: int = 1
    timestamp: datetime
    error_message: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
