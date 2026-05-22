"""Campaign management endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.brief import CampaignBriefInput
from app.schemas.approval import ApprovalResponse, ApprovalStatus
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

        initial_state = GraphState(
            campaign_brief=brief.model_dump(),
            campaign_id=campaign_id,
            session_id=session_id,
            enriched_brief=None,
            campaign_plan=None,
            expanded_tasks=None,
            assembled_tasks=None,
            proposal=None,
            approval_response=None,
            approval_iterations=0,
            max_iterations=5,
            metrics=None,
            performance_report=None,
            status="initialized",
            error_message=None,
            revision_count=0,
        )

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
    return {
        "campaign_id": campaign_id,
        "status": campaign["state"].get("status"),
        "created_at": campaign["created_at"],
    }

@router.post("/{campaign_id}/approve")
async def submit_approval(
    campaign_id: str,
    action: str = "approve",
    feedback: str = None,
):
    """Submit approval/revision response"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign = campaigns[campaign_id]
    state = campaign["state"]

    approval_status = ApprovalStatus.APPROVED if action == "approve" else ApprovalStatus.REVISIONS_REQUESTED

    state["approval_response"] = {
        "campaign_id": campaign_id,
        "status": approval_status.value,
        "feedback": feedback or "",
        "timestamp": datetime.utcnow().isoformat(),
    }

    logger.info(f"Approval response recorded for campaign {campaign_id}: {approval_status}")

    return {
        "campaign_id": campaign_id,
        "status": approval_status.value,
        "message": "Response recorded",
    }

@router.post("/{campaign_id}/resume")
async def resume_campaign(campaign_id: str, approval_response: dict):
    """Resume graph execution after HITL approval"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")

    logger.info(f"Campaign resumed: {campaign_id}")
    return {"campaign_id": campaign_id, "status": "resumed"}
