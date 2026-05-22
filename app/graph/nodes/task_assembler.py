from app.graph.state import GraphState
from app.core.logging import logger
import uuid
import asyncio

async def assemble_tasks(state: GraphState) -> GraphState:
    """Assemble content pieces into executable tasks with channel-specific production steps"""
    try:
        plan = state.get("campaign_plan", {})
        content_pieces = plan.get("content_pieces", [])

        all_tasks = []
        channel_groups = {}
        dependency_graph = {}
        team_assignments = {}

        for piece_idx, piece in enumerate(content_pieces):
            piece_title = piece.get("title", f"Content Piece {piece_idx}")
            channels = piece.get("channels", [])

            for channel in channels:
                if channel not in channel_groups:
                    channel_groups[channel] = []

                # Get channel-specific tasks from the content piece
                channel_key = f"{channel}_tasks"
                channel_tasks = piece.get(channel_key, []) or piece.get("production_tasks", {}).get(channel, [])

                # If no explicit tasks, create a generic task
                if not channel_tasks:
                    channel_tasks = ["Create content", "Review", "Publish"]

                # Create task objects for each step in the channel workflow
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
                    dependency_graph[task_id] = task_obj.get("dependencies", [])

                    owner = piece.get("owner_role", "content_team")
                    if owner:
                        if owner not in team_assignments:
                            team_assignments[owner] = []
                        team_assignments[owner].append(task_id)

                    prev_task_id = task_id

        state["assembled_tasks"] = {
            "campaign_id": state.get("campaign_id"),
            "all_tasks": all_tasks,
            "channel_groups": {k: v for k, v in sorted(channel_groups.items())},
            "dependency_graph": dependency_graph,
            "team_assignments": team_assignments,
        }
        state["status"] = "tasks_assembled"
        logger.info(f"Assembled {len(all_tasks)} total tasks across {len(channel_groups)} channels")

    except Exception as e:
        state["status"] = "task_assembly_failed"
        state["error_message"] = str(e)
        logger.error(f"Task assembly failed: {e}")

    return state
