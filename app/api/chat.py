from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.gemini_service import GeminiService
from app.services.rag_service import LocalRAGService
from app.services.prompt_optimizer import PromptOptimizer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
gemini_service = GeminiService()
rag_service = LocalRAGService()
prompt_optimizer = PromptOptimizer()

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send message to AI assistant with auto-detection and optimization"""
    try:
        # 1. Optimize query with auto-detection if needed
        optimization = await prompt_optimizer.optimize_query(
            request.message, 
            context_type=request.analysis_type or "auto"
        )
        
        # 2. Search RAG with optimized query
        rag_results = await rag_service.search_tickets(
            query=optimization["optimized_prompt"],
            max_results=5
        )
        
        # 3. Generate response with Gemini using detected intent
        response = await gemini_service.generate_response(
            message=optimization["optimized_prompt"],
            context=rag_results,
            analysis_type=optimization["detected_intent"]
        )
        
        return ChatResponse(
            message=response,
            timestamp=datetime.utcnow().isoformat(),
            context_used=len(rag_results),
            analysis_type=optimization["detected_intent"]  # Return auto-detected type
        )
        
    except Exception as e:
        logger.error(f"Error in enhanced chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-analysis-type")
async def detect_analysis_type(request: ChatRequest):
    """Test endpoint to see auto-detection in action"""
    try:
        detected_type = prompt_optimizer.auto_detect_analysis_type(request.message)
        optimization = await prompt_optimizer.optimize_query(request.message, "auto")
        
        return {
            "original_message": request.message,
            "detected_analysis_type": detected_type,
            "optimization_details": optimization,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in analysis type detection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Mantener endpoints existentes...