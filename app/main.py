from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.chat import router as chat_router
from app.api.chat import router as chat_router
from app.api.rag import router as rag_router
from app.api.visualizations import router as viz_router
from app.api.reports import router as reports_router



# Initialize FastAPI
app = FastAPI(
    title="PM AI Assistant",
    description="AI Assistant for Project Managers and Scrum Masters",
    version="1.0.0",
    debug=settings.debug
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers

app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
app.include_router(viz_router, prefix="/api/visualizations", tags=["visualizations"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(rag_router, prefix="/api/rag", tags=["rag"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
from app.api.analytics import router as analytics_router

# Include routers
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(rag_router, prefix="/api/rag", tags=["rag"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {
        "message": "PM AI Assistant API", 
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "debug": settings.debug}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host=settings.host, 
        port=settings.port, 
        reload=settings.debug
    )