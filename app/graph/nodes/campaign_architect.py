from app.services.llm_service import llm_service
from app.graph.state import GraphState
from app.core.logging import logger
from app.prompts.campaign_architect import (
    CAMPAIGN_ARCHITECT_SYSTEM,
    CAMPAIGN_ARCHITECT_PROMPT,
)
from app.utils.json_utils import extract_json


async def architect_campaign(state: GraphState) -> GraphState:
    """Create campaign plan from enriched brief"""
    try:
        brief = state.get("campaign_brief", {})
        enriched = state.get("enriched_brief", {})

        prompt = CAMPAIGN_ARCHITECT_PROMPT.format(
            campaign_name=brief.get("campaign_name", ""),
            objective=brief.get("objective", ""),
            inferred_goals=enriched.get("inferred_goals", []),
            duration_days=brief.get("duration_days", 0),
            channels=brief.get("channels", []),
        )

        response = await llm_service.generate(
            prompt=prompt,
            system=CAMPAIGN_ARCHITECT_SYSTEM,
        )

        plan = extract_json(response)
        state["campaign_plan"] = plan
        state["status"] = "campaign_planned"
        logger.info(f"Campaign plan created: {plan}")
        logger.info(f"Campaign plan created with {len(plan.get('content_pieces', []))} pieces")

    except Exception as e:
        state["status"] = "campaign_planning_failed"
        state["error_message"] = str(e)
        logger.error(f"Campaign planning failed: {e}")

    return state
