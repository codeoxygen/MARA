from app.services.llm_service import llm_service
from app.graph.state import GraphState
from app.core.logging import logger
from app.prompts.revision_parser import REVISION_PARSER_SYSTEM, REVISION_PARSER_PROMPT
import json

async def parse_revisions(state: GraphState) -> GraphState:
    """Parse human feedback into structured revision requests"""
    try:
        response = state.get("approval_response", {})
        feedback = response.get("feedback", "")
        campaign_id = state.get("campaign_id")
        plan = state.get("campaign_plan", {})

        prompt = REVISION_PARSER_PROMPT.format(
            campaign_id=campaign_id,
            feedback=feedback,
            current_plan=json.dumps(plan, indent=2),
        )

        parsed = await llm_service.generate(
            prompt=prompt,
            system=REVISION_PARSER_SYSTEM,
            max_tokens=2000,
        )

        revisions = json.loads(parsed)
        state["approval_response"] = revisions
        state["revision_count"] = state.get("revision_count", 0) + 1
        state["status"] = revisions.get("status", "revisions_requested")
        logger.info(f"Revisions parsed for campaign {campaign_id}")

    except Exception as e:
        state["status"] = "revision_parsing_failed"
        state["error_message"] = str(e)
        logger.error(f"Revision parsing failed: {e}")

    return state
