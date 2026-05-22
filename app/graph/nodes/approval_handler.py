from app.services.slack_service import slack_service
from app.graph.state import GraphState
from app.core.logging import logger
import uuid
import time
import json

async def handle_approval(state: GraphState) -> GraphState:
    """Send full campaign plan to Slack and wait for approval"""
    try:
        brief = state.get("campaign_brief", {})
        plan = state.get("campaign_plan")
        assembled_tasks = state.get("assembled_tasks", {})
        asana_project = state.get("asana_project", {})
        campaign_id = state.get("campaign_id")

        # Validate that planner ran successfully
        if not plan:
            raise ValueError("Campaign plan is empty - planner node may have failed")

        # Reset approval response for new cycle
        state["approval_response"] = None

        approval_token = str(uuid.uuid4())
        state["approval_token"] = approval_token
        state["approval_iterations"] = state.get("approval_iterations", 0) + 1

        # Build comprehensive campaign proposal with FULL campaign details
        revision_info = f"\n🔄 *Revision #{state.get('revision_count', 0)}*" if state.get('revision_count', 0) > 0 else ""

        # Extract all tasks grouped by channel
        all_tasks_list = assembled_tasks.get("all_tasks", []) if assembled_tasks else []
        tasks_by_channel = {}
        for task in all_tasks_list:
            channel = task.get("channel", "General")
            if channel not in tasks_by_channel:
                tasks_by_channel[channel] = []
            tasks_by_channel[channel].append({
                "title": task.get("title", ""),
                "step": task.get("step", ""),
            })

        # Build task summary
        tasks_summary = ""
        for channel in sorted(tasks_by_channel.keys()):
            tasks_summary += f"\n*{channel.upper()}:*\n"
            for task in tasks_by_channel[channel]:
                tasks_summary += f"  • {task['title']}\n"

        # Build content pieces summary
        content_summary = ""
        content_pieces = plan.get("content_pieces", []) if isinstance(plan.get("content_pieces"), list) else []
        for piece in content_pieces:
            content_summary += f"\n📄 *{piece.get('title', 'Content Piece')}*\n"
            content_summary += f"   Channels: {', '.join(piece.get('channels', []))}\n"
            if piece.get('description'):
                content_summary += f"   Description: {piece.get('description')[:200]}\n"

        # Build clean summary for Slack (avoiding blocks validation errors)
        proposal = f"""🎯 Campaign Approval Required{revision_info}

Campaign: {brief.get('campaign_name', 'Campaign')}
Objective: {brief.get('objective', 'No objective')}
Audience: {brief.get('target_audience', 'Not specified')}
Duration: {brief.get('duration_days', 'N/A')} days
Budget: ${brief.get('budget', 'Not specified')}
Channels: {', '.join(brief.get('channels', []))}

Content Pieces: {len(content_pieces)} pieces
Tasks: {len(all_tasks_list)} total tasks

Click the 'View Full Proposal' button to see complete details.

Token: {approval_token}"""
        
        # Store full proposal details in state for API retrieval
        full_proposal_details = {
            "campaign_id": campaign_id,
            "overview": plan.get('overview', 'No overview')[:2000],
            "content_pieces": content_summary[:2000] if content_summary else "No content pieces defined",
            "tasks_summary": tasks_summary[:2500] if tasks_summary else "No tasks assigned",
            "asana_project_url": asana_project.get('project_url', 'N/A'),
            "total_tasks_in_asana": asana_project.get('total_tasks_created', 0),
        }
        state["full_proposal_details"] = full_proposal_details

        success = await slack_service.send_approval_request(
            campaign_id=campaign_id,
            campaign_name=brief.get("campaign_name", ""),
            proposal_content=proposal,
            approval_token=approval_token,
        )

        if success:
            state["status"] = "awaiting_approval"
            state["proposal"] = proposal
            logger.info(f"✋ Approval request sent for campaign {campaign_id}")
            logger.info(f"📲 Slack approval token: {approval_token}")
            logger.info(f"⏳ Waiting for human approval response from Slack...")

            # Wait for Slack approval response with timeout
            timeout = 3600  # 1 hour timeout
            start_time = time.time()
            poll_interval = 2  # Check every 2 seconds
            checked_count = 0
            last_log_time = start_time

            while time.time() - start_time < timeout:
                approval_response = state.get("approval_response")

                if approval_response:
                    elapsed = time.time() - start_time
                    
                    if approval_response.get("status") == "approved":
                        state["status"] = "approved"
                        logger.info(f"✅ Campaign {campaign_id} APPROVED by Slack")
                        logger.info(f"   Response time: {elapsed:.1f}s")
                        logger.info(f"   Token used: {approval_token[:8]}...")
                        return state
                    
                    elif approval_response.get("status") == "rejected":
                        state["status"] = "revision_requested"
                        feedback = approval_response.get("feedback", "No feedback provided")
                        logger.info(f"🔄 Campaign {campaign_id} REJECTED - revisions requested")
                        logger.info(f"   Response time: {elapsed:.1f}s")
                        logger.info(f"   Feedback: {feedback}")
                        return state

                current_time = time.time()
                elapsed = current_time - start_time
                
                # Log progress every 30 seconds
                if current_time - last_log_time >= 30:
                    logger.debug(f"⏳ Waiting for approval ({elapsed:.1f}s elapsed)...")
                    logger.debug(f"   Campaign: {campaign_id}")
                    logger.debug(f"   Token: {approval_token[:8]}...")
                    last_log_time = current_time

                checked_count += 1
                time.sleep(poll_interval)

            # Timeout reached
            state["status"] = "approval_timeout"
            state["error_message"] = f"Approval timeout after {timeout}s - no response received from Slack"
            logger.error(f"❌ Approval timeout for campaign {campaign_id}")
            logger.error(f"   Expected approval response within {timeout}s")
            logger.error(f"   Check Slack for the approval message with token: {approval_token}")
        else:
            state["status"] = "approval_send_failed"
            state["error_message"] = "Failed to send Slack message - check webhook configuration"
            logger.error(f"❌ Failed to send Slack approval request for campaign {campaign_id}")
            logger.error(f"   Check SLACK_WEBHOOK_URL configuration in environment variables")

    except Exception as e:
        state["status"] = "approval_failed"
        state["error_message"] = str(e)
        logger.error(f"❌ Approval handling failed: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

    return state
