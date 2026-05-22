from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Task(BaseModel):
    """Individual task in the campaign execution plan"""
    id: str
    title: str
    description: str
    channel: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    owner: Optional[str] = None
    due_date: Optional[str] = None
    dependencies: List[str] = []
    subtasks: List[str] = []
    metadata: Dict = {}

class ChannelTaskGroup(BaseModel):
    """Tasks grouped by channel with sequence"""
    channel: str
    task_sequence: List[Task]
    parallel_groups: Optional[List[List[str]]] = None

class TaskList(BaseModel):
    """Complete task list with dependencies and assignments"""
    campaign_id: str
    all_tasks: List[Task]
    channel_groups: List[ChannelTaskGroup]
    dependency_graph: Dict[str, List[str]]
    team_assignments: Dict[str, List[str]]
