"""Model routing hints by task type — configuration only, no vendor calls."""

from auto_client_acquisition.model_router.task_router import list_tasks, route_task

__all__ = ["list_tasks", "route_task"]
