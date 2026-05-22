"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.routes import campaigns, websocket

# Initialize FastAPI app
app = FastAPI(
    title="MARA - Marketing Agentic Resource Assistant",
    description="Multi-agent AI system for marketing campaign planning and analytics",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaigns.router)
app.include_router(websocket.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MARA",
        "environment": settings.app_env,
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info(f"Starting MARA in {settings.app_env} mode")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Shutting down MARA")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.app_env == "development",
    )
