"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yaml

from src.utils.logger import setup_logging, get_logger
from src.web_app.routes import chat, market, user, news

# Setup logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)

# Load config
with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)

# Create FastAPI app
app = FastAPI(
    title=config['app']['name'],
    version=config['app']['version'],
    description="AI-powered financial education assistant with multi-agent system"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(news.router, prefix="/api/news", tags=["news"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    from src.rag.vector_store import get_vector_store
    
    try:
        vector_store = get_vector_store()
        stats = vector_store.get_stats()
        
        return {
            "status": "healthy",
            "version": config['app']['version'],
            "vector_store_loaded": stats['num_documents'] > 0,
            "num_documents": stats['num_documents']
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "version": config['app']['version'],
            "error": str(e)
        }

# ── Static File Serving (for all-in-one deployment) ──────────────────────────
frontend_path = os.path.join(os.getcwd(), "frontend", "dist")

if os.path.exists(frontend_path):
    logger.info(f"Serving static files from {frontend_path}")
    # Mount the dist folder for static assets (js, css, images)
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

    # Main entry point for the frontend
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # If the path starts with api, don't handle it here (though routers should catch it first)
        if full_path.startswith("api"):
             return {"error": "Not Found"}
             
        # Check if the requested file exists in dist
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Otherwise serve index.html (SPA routing fallback)
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    logger.warning(f"Frontend dist folder not found at {frontend_path}. Static serving disabled.")
    @app.get("/")
    async def root():
        """Root endpoint fallback"""
        return {
            "name": config['app']['name'],
            "version": config['app']['version'],
            "status": "running",
            "frontend": "not_found"
        }

logger.info(f"FastAPI application initialized: {config['app']['name']} v{config['app']['version']}")

