"""
API endpoints for the Antigravity Consultant and Reward System.
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from .consultant import AntigravityConsultant
from .models import Suggestion
from .rewards import AgentPerformance, AgentToken

# Initialize the Consultant
consultant = AntigravityConsultant()

# Create API router
router = APIRouter(prefix="/consultant", tags=["antigravity-consultant"])


# Request/Response Models
class ExamineSuggestionRequest(BaseModel):
    suggestion: Suggestion
    agent_id: Optional[str] = None


class ExamineBatchRequest(BaseModel):
    suggestions: List[Suggestion]
    agent_id: Optional[str] = None


class EvaluateAgentRequest(BaseModel):
    agent_id: str


class AskQuestionRequest(BaseModel):
    question: str


# Endpoints
@router.post("/examine", status_code=status.HTTP_200_OK)
async def examine_suggestion(request: ExamineSuggestionRequest):
    """
    Have the Consultant examine a code suggestion.
    The Consultant will determine if it's truly critical.
    """
    try:
        result = await consultant.examine_suggestion(
            request.suggestion,
            request.agent_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Examination failed: {str(e)}"
        )


@router.post("/examine-batch", status_code=status.HTTP_200_OK)
async def examine_batch(request: ExamineBatchRequest):
    """
    Have the Consultant examine multiple suggestions.
    """
    try:
        results = await consultant.examine_batch(
            request.suggestions,
            request.agent_id
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch examination failed: {str(e)}"
        )


@router.post("/evaluate/{agent_id}", status_code=status.HTTP_200_OK)
async def evaluate_agent(agent_id: str):
    """
    Trigger an evaluation of an agent.
    THE MOMENT OF JUDGMENT.
    """
    try:
        result = await consultant.evaluate_agent(agent_id)
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.post("/start-evaluation-loop", status_code=status.HTTP_200_OK)
async def start_evaluation_loop():
    """
    Start the random evaluation loop (1-3 hours).
    AGENTS WILL LIVE IN FEAR.
    """
    try:
        await consultant.start_evaluation_loop()
        return {
            "status": "started",
            "message": "Evaluation loop started. Agents will be evaluated at random intervals between 1-3 hours.",
            "next_evaluation": consultant.get_next_evaluation_time()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start evaluation loop: {str(e)}"
        )


@router.post("/stop-evaluation-loop", status_code=status.HTTP_200_OK)
async def stop_evaluation_loop():
    """Stop the evaluation loop."""
    consultant.stop_evaluation_loop()
    return {"status": "stopped", "message": "Evaluation loop stopped"}


@router.get("/next-evaluation")
async def get_next_evaluation():
    """Get information about the next evaluation."""
    next_time = consultant.get_next_evaluation_time()
    seconds_until = consultant.get_time_until_evaluation()

    return {
        "next_evaluation": next_time.isoformat() if next_time else None,
        "seconds_until_evaluation": seconds_until,
        "evaluation_loop_running": consultant._evaluation_loop_running
    }


@router.post("/ask", status_code=status.HTTP_200_OK)
async def ask_consultant(request: AskQuestionRequest):
    """
    Ask the Consultant a question about code quality.
    Receive wisdom from Gemini 2.5 Pro Flash.
    """
    try:
        answer = await consultant.ask_question(request.question)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ask Consultant: {str(e)}"
        )


@router.get("/leaderboard")
async def get_leaderboard(top_n: int = 10):
    """Get the leaderboard of top performing agents."""
    leaderboard = consultant.get_leaderboard(top_n)
    return {"leaderboard": [agent.dict() for agent in leaderboard]}


@router.get("/agent/{agent_id}/performance")
async def get_agent_performance(agent_id: str):
    """Get performance metrics for a specific agent."""
    performance = consultant.reward_system.get_agent_performance(agent_id)
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    return performance.dict()


@router.get("/stats")
async def get_consultant_stats():
    """Get overall Consultant and reward system statistics."""
    return consultant.get_system_stats()


@router.post("/register-agent/{agent_id}", status_code=status.HTTP_201_CREATED)
async def register_agent(agent_id: str):
    """Register a new agent in the reward system."""
    performance = consultant.reward_system.register_agent(agent_id)
    return {
        "status": "registered",
        "agent_id": agent_id,
        "performance": performance.dict()
    }


@router.get("/health")
async def health_check():
    """Health check for Consultant system."""
    gemini_available = consultant.gemini is not None
    return {
        "status": "healthy" if gemini_available else "degraded",
        "gemini_available": gemini_available,
        "evaluation_loop_running": consultant._evaluation_loop_running
    }


# Helper function to get the consultant instance
def get_consultant() -> AntigravityConsultant:
    """Get the global consultant instance."""
    return consultant
