"""Mock Asana API service for creating campaign tasks"""
import uuid
from app.core.logging import logger


class AsanaService:
    """Mock Asana integration for task creation"""

    def __init__(self):
        self.tasks = {}

    async def create_tasks(self, campaign_id: str, tasks_list: list) -> dict:
        """Create tasks in Asana (mock implementation)"""
        try:
            logger.info(f"Asana: Creating {len(tasks_list)} tasks for campaign {campaign_id}")

            asana_tasks = []
            for task in tasks_list:
                asana_task_id = f"asana-{uuid.uuid4().hex[:8]}"
                asana_task = {
                    "id": asana_task_id,
                    "name": task.get("title", "Untitled Task"),
                    "description": task.get("description", ""),
                    "assignee": task.get("owner", "unassigned"),
                    "due_date": None,
                    "status": "not_started",
                    "channel": task.get("channel", "general"),
                    "dependencies": task.get("dependencies", []),
                    "metadata": task.get("metadata", {}),
                }
                asana_tasks.append(asana_task)
                self.tasks[asana_task_id] = asana_task

            logger.info(f"Asana: Successfully created {len(asana_tasks)} tasks")
            return {
                "campaign_id": campaign_id,
                "total_tasks_created": len(asana_tasks),
                "tasks": asana_tasks,
                "project_url": f"https://app.asana.com/0/campaigns/{campaign_id}/list",
            }
        except Exception as e:
            logger.error(f"Asana task creation failed: {e}")
            raise


asana_service = AsanaService()
