from app.graph.state import GraphState
from app.core.logging import logger
import uuid
import asyncio

async def assemble_tasks(state: GraphState) -> GraphState:
    """Assemble all tasks into a unified task list with dependencies"""
    try:
        expanded = state.get("expanded_tasks", [])

        all_tasks = []
        channel_groups = []
        dependency_graph = {}
        team_assignments = {}

        for group in expanded:
            channel = group.get("channel", "unknown")
            tasks = group.get("task_sequence", [])

            task_objects = []
            prev_task_id = None

            for idx, task_def in enumerate(tasks):
                task_id = f"{channel}-{idx}-{uuid.uuid4().hex[:8]}"
                task_obj = {
                    "id": task_id,
                    "title": task_def.get("task_name", ""),
                    "description": task_def.get("description", ""),
                    "channel": channel,
                    "status": "pending",
                    "priority": "medium",
                    "owner": task_def.get("owner_role"),
                    "dependencies": [prev_task_id] if prev_task_id else [],
                    "metadata": {
                        "estimated_hours": task_def.get("estimated_hours", 1),
                        "step": task_def.get("step", idx),
                    },
                }
                all_tasks.append(task_obj)
                task_objects.append(task_obj)
                dependency_graph[task_id] = task_obj.get("dependencies", [])

                if task_def.get("owner_role"):
                    if task_def["owner_role"] not in team_assignments:
                        team_assignments[task_def["owner_role"]] = []
                    team_assignments[task_def["owner_role"]].append(task_id)

                prev_task_id = task_id

            channel_groups.append({
                "channel": channel,
                "task_sequence": task_objects,
            })

        state["assembled_tasks"] = {
            "campaign_id": state.get("campaign_id"),
            "all_tasks": all_tasks,
            "channel_groups": channel_groups,
            "dependency_graph": dependency_graph,
            "team_assignments": team_assignments,
        }
        state["status"] = "tasks_assembled"
        logger.info(f"Assembled {len(all_tasks)} total tasks")

    except Exception as e:
        state["status"] = "task_assembly_failed"
        state["error_message"] = str(e)
        logger.error(f"Task assembly failed: {e}")

    return state
