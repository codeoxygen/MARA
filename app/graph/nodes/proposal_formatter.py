from app.services.llm_service import llm_service
from app.graph.state import GraphState
from app.core.logging import logger
from app.prompts.proposal_formatter import (
    PROPOSAL_FORMATTER_SYSTEM,
    PROPOSAL_FORMATTER_PROMPT,
)
import json

async def format_proposal(state: GraphState) -> GraphState:
    """Format campaign plan into human-readable proposal"""
    try:
        brief = state.get("campaign_brief", {})
        plan = state.get("campaign_plan", {})
        tasks = state.get("assembled_tasks", {})

        prompt = PROPOSAL_FORMATTER_PROMPT.format(
            campaign_name=brief.get("campaign_name", ""),
            campaign_plan=json.dumps(plan, indent=2),
            task_list=json.dumps(tasks, indent=2),
        )

        proposal = await llm_service.generate(
            prompt=prompt,
            system=PROPOSAL_FORMATTER_SYSTEM,
            max_tokens=3000,
        )

        state["proposal"] = proposal
        state["status"] = "proposal_formatted"
        logger.info("Proposal formatted for approval")

    except Exception as e:
        state["status"] = "proposal_formatting_failed"
        state["error_message"] = str(e)
        logger.error(f"Proposal formatting failed: {e}")

    return state
