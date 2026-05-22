from app.services.slack_service import slack_service
from app.graph.state import GraphState
from app.core.logging import logger
import uuid

async def handle_approval(state: GraphState) -> GraphState:
    """Send proposal to Slack for human approval (HITL - Human-In-The-Loop)"""
    try:
        brief = state.get("campaign_brief", {})
        proposal = state.get("proposal", "")
        campaign_id = state.get("campaign_id")

        approval_token = str(uuid.uuid4())

        success = await slack_service.send_approval_request(
            campaign_id=campaign_id,
            campaign_name=brief.get("campaign_name", ""),
            proposal_content=proposal[:2000],
            approval_token=approval_token,
        )

        if success:
            state["status"] = "awaiting_approval"
            state["approval_iterations"] = state.get("approval_iterations", 0) + 1
            logger.info(f"Approval request sent for campaign {campaign_id}")
        else:
            state["status"] = "approval_send_failed"
            state["error_message"] = "Failed to send Slack message"

    except Exception as e:
        state["status"] = "approval_failed"
        state["error_message"] = str(e)
        logger.error(f"Approval handling failed: {e}")

    return state
