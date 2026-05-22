"""LangGraph graph construction - Simplified 3-node workflow"""

from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes import (
    validate_input,
    planner,
    handle_approval,
    analytics,
)
from app.core.config import settings


def _sync_wrapper(async_fn):
    """Wrap async function for sync graph execution"""
    def sync_wrapper(state: GraphState):
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(async_fn(state))
    return sync_wrapper


def build_graph():
    """Build simplified 3-node campaign workflow"""

    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("input_validator", validate_input)
    workflow.add_node("planner", _sync_wrapper(planner))  # Unified: validate + analyze + plan + assemble + asana
    workflow.add_node("approval", _sync_wrapper(handle_approval))  # Slack approval
    workflow.add_node("analytics", _sync_wrapper(analytics))  # Mock GA data + report

    # Linear flow
    workflow.add_edge("input_validator", "planner")
    workflow.add_edge("planner", "approval")
    workflow.add_edge("approval", "analytics")
    workflow.add_edge("analytics", END)

    # Set entry point
    workflow.set_entry_point("input_validator")

    # Compile graph
    graph = workflow.compile()

    return graph


# Initialize graph
graph = build_graph()
