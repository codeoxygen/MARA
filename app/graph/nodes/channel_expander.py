from app.services.llm_service import llm_service
from app.graph.state import GraphState
from app.core.logging import logger
from app.prompts.channel_expander import CHANNEL_EXPANDER_SYSTEM, CHANNEL_EXPANDER_PROMPT
import json

async def expand_channels(state: GraphState) -> GraphState:
    """Expand content pieces into channel-specific tasks"""
    try:
        brief = state.get("campaign_brief", {})
        plan = state.get("campaign_plan", {})

        prompt = CHANNEL_EXPANDER_PROMPT.format(
            campaign_name=brief.get("campaign_name", ""),
            content_pieces=json.dumps(plan.get("content_pieces", []), indent=2),
            channels=brief.get("channels", []),
        )

        response = await llm_service.generate(
            prompt=prompt,
            system=CHANNEL_EXPANDER_SYSTEM,
            max_tokens=4000,
        )

        expanded = json.loads(response)
        state["expanded_tasks"] = expanded.get("expanded_tasks", [])
        state["status"] = "channels_expanded"
        logger.info(f"Expanded to {len(state.get('expanded_tasks', []))} channel task groups")

    except Exception as e:
        state["status"] = "channel_expansion_failed"
        state["error_message"] = str(e)
        logger.error(f"Channel expansion failed: {e}")

    return state
