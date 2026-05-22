from app.services.llm_service import llm_service
from app.graph.state import GraphState
from app.core.logging import logger
from app.prompts.channel_expander import CHANNEL_EXPANDER_SYSTEM, CHANNEL_EXPANDER_PROMPT
from app.utils.json_utils import extract_json
import json

async def expand_channels(state: GraphState) -> GraphState:
    """Expand content pieces into channel-specific tasks"""
    try:
        logger.info("Channel expander: Starting")
        brief = state.get("campaign_brief", {})
        plan = state.get("campaign_plan", {})

        logger.info(f"Channel expander: Formatting prompt with {len(plan.get('content_pieces', []))} content pieces")
        prompt = CHANNEL_EXPANDER_PROMPT.format(
            campaign_name=brief.get("campaign_name", ""),
            content_pieces=json.dumps(plan.get("content_pieces", []), indent=2),
            channels=brief.get("channels", []),
        )

        logger.info("Channel expander: Calling LLM")
        response = await llm_service.generate(
            prompt=prompt,
            system=CHANNEL_EXPANDER_SYSTEM,
        )

        logger.info(f"Channel expander: Received response, length: {len(response) if response else 0}")
        expanded = extract_json(response)
        state["expanded_tasks"] = expanded.get("expanded_tasks", [])
        state["status"] = "channels_expanded"
        logger.info(f"Expanded to {len(state.get('expanded_tasks', []))} channel task groups")

    except Exception as e:
        state["status"] = "channel_expansion_failed"
        state["error_message"] = str(e)
        logger.error(f"Channel expansion failed: {e}")

    return state
