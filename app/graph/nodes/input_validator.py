from app.schemas.brief import CampaignBriefInput
from app.graph.state import GraphState
from app.core.logging import logger

def validate_input(state: GraphState) -> GraphState:
    """Validate input campaign brief"""
    try:
        brief_data = state.get("campaign_brief", {})
        validated_brief = CampaignBriefInput(**brief_data)
        state["status"] = "validated"
        logger.info(f"Input validated for campaign: {validated_brief.campaign_name}")
    except Exception as e:
        state["status"] = "validation_failed"
        state["error_message"] = str(e)
        logger.error(f"Input validation failed: {e}")

    return state
