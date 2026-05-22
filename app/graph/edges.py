"""Conditional edge logic for LangGraph routing"""

from app.graph.state import GraphState
from app.core.config import settings

def route_after_validation(state: GraphState) -> str:
    """Route based on validation result"""
    status = state.get("status")
    if status == "validated":
        return "brief_analyst"
    else:
        return "error"

def route_after_approval(state: GraphState) -> str:
    """Route based on approval response"""
    response = state.get("approval_response", {})
    approval_status = response.get("status", "")

    if approval_status == "approved":
        return "metrics_fetcher"
    elif approval_status == "revisions_requested":
        max_iterations = state.get("max_iterations", settings.max_revision_iterations)
        iterations = state.get("approval_iterations", 0)
        if iterations < max_iterations:
            return "revision_parser"
        else:
            return "error"
    elif approval_status == "rejected":
        return "error"
    else:
        return "approval_handler"

def should_continue_revision(state: GraphState) -> str:
    """Check if we should continue revision loop"""
    max_iterations = state.get("max_iterations", settings.max_revision_iterations)
    iterations = state.get("revision_count", 0)

    if iterations >= max_iterations:
        return "error"
    else:
        return "campaign_architect"
