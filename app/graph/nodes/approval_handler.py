from app.services.slack_service import slack_service
from app.graph.state import GraphState
from app.core.logging import logger
import uuid

async def handle_approval(state: GraphState) -> GraphState:
    """Send campaign plan to Slack for human approval (HITL - Human-In-The-Loop)"""
    try:
        brief = state.get("campaign_brief", {})
        plan = state.get("campaign_plan", {})
        asana_project = state.get("asana_project", {})
        campaign_id = state.get("campaign_id")

        approval_token = str(uuid.uuid4())

        # Create approval summary
        summary = f"""
Campaign: {brief.get('campaign_name', 'Campaign')}
Objective: {brief.get('objective', 'No objective')}
Duration: {brief.get('duration_days', 'N/A')} days
Budget: {brief.get('budget', 'Not specified')}
Channels: {', '.join(brief.get('channels', []))}

Campaign Overview:
{plan.get('overview', 'N/A')[:500]}...

Tasks Created: {asana_project.get('total_tasks_created', 0)}
Asana Project: {asana_project.get('project_url', 'N/A')}

👉 Approve or request revisions in Slack
"""

        success = await slack_service.send_approval_request(
            campaign_id=campaign_id,
            campaign_name=brief.get("campaign_name", ""),
            proposal_content=summary,
            approval_token=approval_token,
        )

        if success:
            state["status"] = "awaiting_approval"
            state["approval_iterations"] = state.get("approval_iterations", 0) + 1
            logger.info(f"Approval request sent for campaign {campaign_id} via Slack")
        else:
            state["status"] = "approval_send_failed"
            state["error_message"] = "Failed to send Slack message"

    except Exception as e:
        state["status"] = "approval_failed"
        state["error_message"] = str(e)
        logger.error(f"Approval handling failed: {e}")

    return state
