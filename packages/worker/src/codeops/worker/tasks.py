from codeops.core.logging import get_logger
from codeops.worker.celery_app import celery_app
from codeops.worker.crew import CodeAgentsCrew

logger = get_logger(__name__)

@celery_app.task
def run_agent_task(task_id: str, inputs: dict):
    """Run a CrewAI agent task."""
    logger.info("starting_agent_task", task_id=task_id)
    try:
        # Initialize Crew
        crew = CodeAgentsCrew().crew()
        result = crew.kickoff(inputs=inputs)
        logger.info("agent_task_completed", task_id=task_id, result=str(result))
        return str(result)
    except Exception as e:
        logger.error("agent_task_failed", task_id=task_id, error=str(e))
        raise e
