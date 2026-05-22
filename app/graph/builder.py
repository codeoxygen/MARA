"""LangGraph graph construction - 4-node workflow with approval loop"""

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


def _route_after_planner(state: GraphState) -> str:
    """Route based on planner status"""
    status = state.get("status")

    # If planner failed, end the graph
    if "failed" in status.lower() or "error" in status.lower():
        return END
    # If planning succeeded, proceed to approval
    elif status == "plan_complete":
        return "approval"
    # Default: continue to approval
    else:
        return "approval"


def _route_after_approval(state: GraphState) -> str:
    """Route based on approval status"""
    status = state.get("status")
    iterations = state.get("approval_iterations", 0)
    max_iterations = state.get("max_iterations", 5)

    # Check if revisions requested and within iteration limit
    if status == "revision_requested" and iterations < max_iterations:
        return "planner"
    # If approved or max iterations reached, proceed to analytics
    elif status == "approved":
        return "analytics"
    # Otherwise end the graph
    else:
        return END


def build_graph():
    """Build 4-node campaign workflow with approval loop"""

    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("input_validator", validate_input)
    workflow.add_node("planner", _sync_wrapper(planner))  # Unified: validate + analyze + plan + assemble + asana
    workflow.add_node("approval", _sync_wrapper(handle_approval))  # Slack approval with wait
    workflow.add_node("analytics", _sync_wrapper(analytics))  # Mock GA data + report

    # Flow with conditional routing
    workflow.add_edge("input_validator", "planner")

    # Conditional routing after planner - stop if planning failed
    workflow.add_conditional_edges(
        "planner",
        _route_after_planner,
        {
            "approval": "approval",
            END: END,
        }
    )

    # Conditional routing from approval
    workflow.add_conditional_edges(
        "approval",
        _route_after_approval,
        {
            "planner": "planner",
            "analytics": "analytics",
            END: END,
        }
    )

    workflow.add_edge("analytics", END)

    # Set entry point
    workflow.set_entry_point("input_validator")

    # Compile graph
    graph = workflow.compile()

    return graph


# Initialize graph
graph = build_graph()
