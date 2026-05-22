"""LangGraph graph construction"""

from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes import (
    validate_input,
    analyze_brief,
    architect_campaign,
    expand_channels,
    assemble_tasks,
    format_proposal,
    handle_approval,
    parse_revisions,
    fetch_metrics,
    synthesize_insights,
)
from app.graph.edges import (
    route_after_validation,
    route_after_approval,
    should_continue_revision,
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
    """Build and compile the LangGraph"""

    workflow = StateGraph(GraphState)

    # Add nodes (wrap async functions for sync execution)
    workflow.add_node("input_validator", validate_input)
    workflow.add_node("brief_analyst", _sync_wrapper(analyze_brief))
    workflow.add_node("campaign_architect", _sync_wrapper(architect_campaign))
    workflow.add_node("channel_expander", _sync_wrapper(expand_channels))
    workflow.add_node("task_assembler", _sync_wrapper(assemble_tasks))
    workflow.add_node("proposal_formatter", _sync_wrapper(format_proposal))
    workflow.add_node("approval_handler", _sync_wrapper(handle_approval))
    workflow.add_node("revision_parser", _sync_wrapper(parse_revisions))
    workflow.add_node("metrics_fetcher", _sync_wrapper(fetch_metrics))
    workflow.add_node("insights_synthesizer", _sync_wrapper(synthesize_insights))

    # Add edges
    workflow.add_edge("input_validator", "brief_analyst")
    workflow.add_edge("brief_analyst", "campaign_architect")
    workflow.add_edge("campaign_architect", "channel_expander")
    workflow.add_edge("channel_expander", "task_assembler")
    workflow.add_edge("task_assembler", "proposal_formatter")
    workflow.add_edge("proposal_formatter", "approval_handler")
    workflow.add_edge("metrics_fetcher", "insights_synthesizer")
    workflow.add_edge("insights_synthesizer", END)

    # Conditional edges
    workflow.add_conditional_edges(
        "approval_handler",
        route_after_approval,
        {
            "metrics_fetcher": "metrics_fetcher",
            "revision_parser": "revision_parser",
            "error": END,
        },
    )

    workflow.add_conditional_edges(
        "revision_parser",
        should_continue_revision,
        {
            "campaign_architect": "campaign_architect",
            "error": END,
        },
    )

    # Set entry point
    workflow.set_entry_point("input_validator")

    # Compile graph
    graph = workflow.compile()

    return graph

# Initialize graph
graph = build_graph()
