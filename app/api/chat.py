from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.gemini_service import GeminiService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
gemini_service = GeminiService()

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send message to AI assistant"""
    try:
        # Generate response with Gemini
        response = await gemini_service.generate_response(
            message=request.message,
            context=[],  # We'll add RAG context later
            analysis_type=request.analysis_type
        )
        
        return ChatResponse(
            message=response,
            timestamp=datetime.utcnow().isoformat(),
            context_used=0,
            analysis_type=request.analysis_type
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_gemini():
    """Test endpoint to verify Gemini is working"""
    try:
        response = await gemini_service.generate_response(
            message="Hello! Are you working correctly?",
            analysis_type="general"
        )
        
        return {
            "status": "success",
            "gemini_response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }