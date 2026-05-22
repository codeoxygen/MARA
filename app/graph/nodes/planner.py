"""Single unified planner node: Input validation → Brief analysis → Campaign planning → Task assembly → Asana sync"""
from app.services.llm_service import llm_service
from app.services.asana_service import asana_service
from app.graph.state import GraphState
from app.core.logging import logger
from app.prompts.planner import PLANNER_SYSTEM, PLANNER_PROMPT
from app.utils.json_utils import extract_json
import json
import uuid


async def planner(state: GraphState) -> GraphState:
    """
    Unified planner node:
    1. Validate input brief
    2. Analyze brief with LLM
    3. Generate campaign plan with channel-specific tasks
    4. Assemble tasks
    5. Send to Asana
    """
    try:
        # Step 1: Validate input
        logger.info("Planner: Validating campaign brief")
        brief = state.get("campaign_brief", {})
        approval_response = state.get("approval_response")
        revision_count = state.get("revision_count", 0)

        if not brief.get("campaign_name"):
            raise ValueError("Campaign name is required")
        if not brief.get("objective"):
            raise ValueError("Campaign objective is required")
        if not brief.get("channels"):
            raise ValueError("At least one channel is required")

        # Determine if this is a revision or initial planning
        if approval_response and approval_response.get("status") == "rejected":
            logger.info(f"Planner: Revision #{revision_count + 1} - Incorporating feedback")
            revision_feedback = approval_response.get("feedback", "Please improve the campaign plan")
            additional_context = brief.get("additional_context", "")
            additional_context = f"{additional_context}\n\nREVISION FEEDBACK:\n{revision_feedback}"
            state["revision_count"] = revision_count + 1
        else:
            additional_context = brief.get("additional_context", "")
            logger.info(f"Planner: Generating initial campaign plan for '{brief.get('campaign_name')}'")

        # Step 2: Call unified LLM prompt for full planning
        prompt = PLANNER_PROMPT.format(
            campaign_name=brief.get("campaign_name", ""),
            objective=brief.get("objective", ""),
            target_audience=brief.get("target_audience", ""),
            channels=json.dumps(brief.get("channels", [])),
            duration_days=brief.get("duration_days", 0),
            budget=brief.get("budget", "Not specified"),
            key_messages=json.dumps(brief.get("key_messages", [])),
            success_metrics=json.dumps(brief.get("success_metrics", [])),
            additional_context=additional_context,
        )

        response = await llm_service.generate(
            prompt=prompt,
            system=PLANNER_SYSTEM,
        )

        if not response or not response.strip():
            raise ValueError("Empty response from LLM")

        # Step 3: Parse response
        logger.debug(f"Planner: Parsing LLM response")
        plan_data = extract_json(response)

        if not plan_data:
            logger.error(f"Planner: Failed to extract JSON from LLM response")
            logger.error(f"Response preview: {response[:200]}")
            raise ValueError("Failed to parse campaign plan from LLM response")

        # Step 4: Extract and assemble tasks
        logger.info("Planner: Assembling tasks from campaign plan")
        all_tasks = []
        channel_groups = {}

        content_pieces = plan_data.get("content_pieces", [])
        for piece_idx, piece in enumerate(content_pieces):
            piece_title = piece.get("title", f"Content Piece {piece_idx}")
            channels = piece.get("channels", [])

            for channel in channels:
                if channel not in channel_groups:
                    channel_groups[channel] = []

                # Get channel-specific tasks
                channel_key = f"{channel}_tasks"
                channel_tasks = piece.get(channel_key, []) or ["Create content", "Review", "Publish"]

                prev_task_id = None
                for step_idx, task_name in enumerate(channel_tasks):
                    task_id = f"{channel}-{piece_idx}-{step_idx}-{uuid.uuid4().hex[:8]}"

                    task_obj = {
                        "id": task_id,
                        "title": f"{piece_title} - {task_name}",
                        "description": f"{task_name} for {piece_title} on {channel.capitalize()}",
                        "content_piece": piece_title,
                        "channel": channel,
                        "step": task_name,
                        "status": "pending",
                        "priority": "medium",
                        "owner": piece.get("owner_role", "content_team"),
                        "dependencies": [prev_task_id] if prev_task_id else [],
                        "metadata": {
                            "estimated_hours": piece.get("estimated_effort", {}).get(channel, 2),
                            "sequence_order": step_idx,
                        },
                    }

                    all_tasks.append(task_obj)
                    channel_groups[channel].append(task_obj)
                    prev_task_id = task_id

        # Step 5: Send tasks to Asana
        logger.info("Planner: Sending tasks to Asana")
        asana_result = await asana_service.create_tasks(state.get("campaign_id"), all_tasks)

        # Step 6: Update state
        state["campaign_plan"] = plan_data
        state["assembled_tasks"] = {
            "campaign_id": state.get("campaign_id"),
            "all_tasks": all_tasks,
            "channel_groups": {k: v for k, v in sorted(channel_groups.items())},
        }
        state["asana_project"] = asana_result
        state["status"] = "plan_complete"

        logger.info(f"Planner: ✅ Complete - {len(all_tasks)} tasks created in Asana")

    except json.JSONDecodeError as e:
        state["status"] = "planning_failed"
        state["error_message"] = f"Invalid JSON response from LLM: {str(e)}"
        logger.error(f"Planner: JSON decode error: {e}")
    except Exception as e:
        state["status"] = "planning_failed"
        state["error_message"] = str(e)
        logger.error(f"Planner: Failed: {e}")

    return state
