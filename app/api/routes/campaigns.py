"""Campaign management endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.brief import CampaignBriefInput
from app.api.dependencies import (
    get_graph_runner,
    get_websocket_manager,
    get_graph,
)
from app.graph.state import GraphState
import uuid
from datetime import datetime
from app.core.logging import logger

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

# In-memory campaign state store
campaigns = {}

@router.post("/run")
async def run_campaign(
    brief: CampaignBriefInput,
    graph_runner=Depends(get_graph_runner),
    graph=Depends(get_graph),
):
    """Submit campaign brief and start graph execution"""
    try:
        campaign_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())

        initial_state: GraphState = {
            "campaign_brief": brief.model_dump(),
            "campaign_id": campaign_id,
            "session_id": session_id,
            "enriched_brief": None,
            "campaign_plan": {},  # Initialize as empty dict instead of None
            "expanded_tasks": None,
            "assembled_tasks": {},  # Initialize as empty dict
            "asana_project": {},  # Initialize as empty dict
            "proposal": None,
            "approval_response": None,
            "approval_token": None,
            "approval_iterations": 0,
            "max_iterations": 5,
            "metrics": None,
            "performance_report": None,
            "status": "initialized",
            "error_message": None,
            "revision_count": 0,
        }

        campaigns[campaign_id] = {
            "session_id": session_id,
            "brief": brief.model_dump(),
            "created_at": datetime.utcnow().isoformat(),
            "state": initial_state,
        }

        # Run graph in background
        graph_runner.run_graph(session_id, graph, initial_state)

        logger.info(f"Campaign started: {campaign_id}")
        return {
            "campaign_id": campaign_id,
            "session_id": session_id,
            "status": "running",
        }

    except Exception as e:
        logger.error(f"Failed to start campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get current campaign state"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign = campaigns[campaign_id]
    response = {
        "campaign_id": campaign_id,
        "status": campaign["state"].get("status"),
        "created_at": campaign["created_at"],
    }

    # Include error message if present
    error = campaign["state"].get("error_message")
    if error:
        response["error_message"] = error

    return response

@router.get("/{campaign_id}/proposal")
async def get_campaign_proposal(campaign_id: str):
    """Get full campaign proposal details for viewing"""
    if campaign_id not in campaigns:
        logger.error(f"❌ Campaign not found: {campaign_id}")
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign = campaigns[campaign_id]
    state = campaign["state"]
    
    proposal_details = state.get("full_proposal_details", {})
    plan = state.get("campaign_plan", {})
    brief = state.get("campaign_brief", {})

    if not proposal_details and not plan:
        raise HTTPException(status_code=404, detail="Proposal not yet generated")

    return {
        "campaign_id": campaign_id,
        "campaign_name": brief.get("campaign_name", "Campaign"),
        "status": state.get("status"),
        "brief": {
            "objective": brief.get("objective"),
            "target_audience": brief.get("target_audience"),
            "channels": brief.get("channels", []),
            "duration_days": brief.get("duration_days"),
            "budget": brief.get("budget"),
        },
        "proposal": {
            "overview": proposal_details.get("overview", plan.get("overview", "")),
            "content_pieces": proposal_details.get("content_pieces", ""),
            "tasks_summary": proposal_details.get("tasks_summary", ""),
            "asana_project_url": proposal_details.get("asana_project_url", "N/A"),
            "total_tasks_in_asana": proposal_details.get("total_tasks_in_asana", 0),
        },
    }

@router.api_route("/{campaign_id}/approve", methods=["GET", "POST"])
async def submit_approval(
    campaign_id: str,
    action: str = "approve",
    feedback: str = None,
    token: str = None,
):
    """Submit approval/revision response from Slack"""
    if campaign_id not in campaigns:
        logger.error(f"❌ Campaign not found: {campaign_id}")
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign = campaigns[campaign_id]
    state = campaign["state"]

    # Validate token if provided
    if token:
        stored_token = state.get("approval_token")
        
        # If token is not yet set in state, wait for it (with timeout)
        if not stored_token:
            logger.warning(f"⏳ Token not yet set in state for campaign {campaign_id}, waiting...")
            max_wait = 30  # Wait up to 30 seconds for state to be ready
            wait_interval = 0.5
            elapsed = 0
            
            while elapsed < max_wait:
                import time
                time.sleep(wait_interval)
                stored_token = state.get("approval_token")
                elapsed += wait_interval
                
                if stored_token:
                    logger.info(f"✅ Token appeared in state after {elapsed:.1f}s")
                    break
            
            if not stored_token:
                logger.error(f"❌ Approval token never appeared in state for campaign {campaign_id}")
                logger.error(f"   Provided token: {token[:16]}...")
                logger.error(f"   Stored token: None (state not ready)")
                raise HTTPException(status_code=503, detail="Campaign approval state not ready - try again in a moment")
        
        # Compare tokens
        if stored_token != token:
            logger.error(f"❌ Invalid token for campaign {campaign_id}")
            logger.error(f"   Provided token: {token[:16]}...")
            logger.error(f"   Stored token:   {stored_token[:16]}...")
            logger.error(f"   Status: {state.get('status')}")
            logger.error(f"   Campaign state: {list(state.keys())}")
            raise HTTPException(status_code=403, detail="Invalid approval token")

    # Map action to approval status
    if action == "approve":
        approval_status = "approved"
        logger.info(f"✅ Campaign {campaign_id} APPROVED via Slack")
    elif action in ["reject", "revisions", "request_revisions"]:
        approval_status = "rejected"
        logger.info(f"🔄 Campaign {campaign_id} REJECTED - revisions requested via Slack")
    else:
        approval_status = "unknown"
        logger.warning(f"⚠️ Unknown action '{action}' for campaign {campaign_id}")

    # Record the approval response in state
    state["approval_response"] = {
        "campaign_id": campaign_id,
        "status": approval_status,
        "feedback": feedback or "",
        "timestamp": datetime.utcnow().isoformat(),
    }

    logger.info(f"📝 Approval response recorded for campaign {campaign_id}: {approval_status}")
    logger.debug(f"   Token: {token[:8]}..." if token else "   No token provided")
    logger.debug(f"   Feedback: {feedback[:100]}..." if feedback else "   No feedback")

    return {
        "campaign_id": campaign_id,
        "status": approval_status,
        "message": "✅ Response recorded - graph will continue processing",
        "timestamp": datetime.utcnow().isoformat(),
    }

@router.post("/{campaign_id}/resume")
async def resume_campaign(campaign_id: str, approval_response: dict):
    """Resume graph execution after HITL approval"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")

    logger.info(f"Campaign resumed: {campaign_id}")
    return {"campaign_id": campaign_id, "status": "resumed"}

@router.get("/test/slack")
async def test_slack_diagnostics():
    """Comprehensive Slack connectivity and configuration diagnostics"""
    from app.core.config import settings

    logger.info("🔍 Running Slack diagnostics...")
    
    diagnostics = {
        "timestamp": datetime.utcnow().isoformat(),
        "configuration": {},
        "connectivity_test": None,
        "webhook_test": None,
        "issues": [],
        "recommendations": [],
    }

    # Check configuration
    webhook_url = settings.slack_webhook_url
    bot_token = settings.slack_bot_token
    base_url = settings.base_url

    diagnostics["configuration"] = {
        "webhook_url_configured": bool(webhook_url),
        "webhook_url_preview": webhook_url[:50] + "..." if webhook_url else "NOT CONFIGURED",
        "bot_token_configured": bool(bot_token),
        "bot_token_preview": bot_token[:20] + "..." if bot_token else "NOT CONFIGURED",
        "base_url": base_url,
        "base_url_valid": base_url.startswith(("http://", "https://")),
    }

    # Check for issues
    if not webhook_url:
        diagnostics["issues"].append("❌ SLACK_WEBHOOK_URL not configured in environment")
        diagnostics["recommendations"].append(
            "Set SLACK_WEBHOOK_URL in .env file. Get it from https://api.slack.com/apps -> Your App -> Incoming Webhooks"
        )
    elif not webhook_url.startswith("https://hooks.slack.com"):
        diagnostics["issues"].append("⚠️  SLACK_WEBHOOK_URL doesn't match expected Slack webhook pattern")

    if not base_url.startswith(("http://", "https://")):
        diagnostics["issues"].append("❌ BASE_URL is not a valid URL")
        diagnostics["recommendations"].append("Set BASE_URL to a valid public URL (e.g., https://your-ngrok-url.ngrok.io)")

    if "example.ngrok.io" in base_url:
        diagnostics["issues"].append("⚠️  BASE_URL appears to be a placeholder")
        diagnostics["recommendations"].append(
            "Update BASE_URL in .env to your actual ngrok URL or production domain"
        )

    # Run connectivity test
    if webhook_url:
        test_message = {
            "text": "🧪 MARA Slack Diagnostics Test",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🧪 MARA Slack Webhook Test",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ Webhook connectivity is working!\n\nThis is a test message from the MARA diagnostics endpoint.",
                    },
                },
            ]
        }

        try:
            import httpx
            async with httpx.AsyncClient() as client:
                logger.info(f"📤 Testing Slack webhook connection...")
                response = await client.post(
                    webhook_url,
                    json=test_message,
                    timeout=10,
                )

                diagnostics["webhook_test"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "http_status_code": response.status_code,
                    "http_reason": response.reason_phrase,
                }

                if response.status_code == 200:
                    logger.info("✅ Slack webhook connection successful")
                    diagnostics["connectivity_test"] = {
                        "status": "success",
                        "message": "✅ Slack webhook is working!",
                        "next_step": "Submit a campaign for approval and you will receive a Slack message",
                    }
                else:
                    logger.error(f"❌ Slack webhook test failed: HTTP {response.status_code}")
                    diagnostics["connectivity_test"] = {
                        "status": "failed",
                        "message": f"❌ Slack webhook returned HTTP {response.status_code}",
                        "response_text": response.text,
                    }
                    diagnostics["issues"].append(f"❌ Slack webhook test failed with HTTP {response.status_code}")
                    diagnostics["recommendations"].append(
                        f"Response: {response.text}. Check that the webhook URL is correct and the channel exists."
                    )

        except Exception as e:
            logger.error(f"❌ Error testing Slack connection: {e}")
            diagnostics["connectivity_test"] = {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
            }
            diagnostics["issues"].append(f"❌ Connection error: {e}")
            diagnostics["recommendations"].append(
                "Check your network connectivity and firewall rules. Slack webhook URL should be accessible from your network."
            )
    else:
        diagnostics["connectivity_test"] = {
            "status": "skipped",
            "reason": "SLACK_WEBHOOK_URL not configured",
        }

    # Add approval flow info
    diagnostics["approval_flow"] = {
        "description": "When a campaign is submitted for approval:",
        "steps": [
            "1. Campaign plan is generated",
            "2. Proposal is formatted",
            "3. Slack approval request is sent to the configured webhook",
            f"4. Approval links point to: {base_url}/api/campaigns/{{campaign_id}}/approve",
            "5. User clicks 'Approve' or 'Request Revisions' in Slack",
            "6. System receives response and continues or revises the plan",
        ],
        "test_campaign_url": "POST /api/campaigns/run with a campaign brief to test the full flow",
    }

    # Summary
    if diagnostics["issues"]:
        diagnostics["summary"] = "⚠️  Issues found - see issues and recommendations above"
    elif diagnostics["connectivity_test"] and diagnostics["connectivity_test"]["status"] == "success":
        diagnostics["summary"] = "✅ Slack is properly configured and connected!"
    else:
        diagnostics["summary"] = "⚠️  Check configuration above"

    logger.info(f"Slack diagnostics complete. Summary: {diagnostics['summary']}")
    
    return diagnostics
