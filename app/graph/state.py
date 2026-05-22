from typing import TypedDict, List, Dict, Any, Optional

class GraphState(TypedDict):
    """State passed through the LangGraph"""

    # Input
    campaign_brief: Dict[str, Any]
    campaign_id: str
    session_id: str

    # Planner outputs
    enriched_brief: Optional[Dict[str, Any]]
    campaign_plan: Optional[Dict[str, Any]]
    expanded_tasks: Optional[List[Dict[str, Any]]]
    assembled_tasks: Optional[Dict[str, Any]]

    # Comms outputs
    proposal: Optional[str]
    approval_response: Optional[Dict[str, Any]]
    approval_iterations: int
    max_iterations: int

    # Analytics outputs
    metrics: Optional[Dict[str, List[Any]]]
    performance_report: Optional[Dict[str, Any]]

    # State tracking
    status: str
    error_message: Optional[str]
    revision_count: int
