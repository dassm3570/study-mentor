import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="AETHER 2.0 AI Operating System",
    description="The Core API and Orchestration engine for the AETHER 2.0 Agentic AI OS.",
    version="2.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from aether.api.v1.router import api_router
    # Include API Router
    app.include_router(api_router, prefix="/api/v1")
except Exception as e:
    print(f"[WARNING] Failed to load API router: {e}")

@app.get("/")
async def root():
    return {
        "status": "running",
        "system": "AETHER 2.0",
        "version": "2.0.0",
        "api": "/api/v1"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "system": "AETHER 2.0",
        "version": "2.0.0"
    }

# Mount frontend static files if directory exists (not in serverless)
try:
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
    if os.path.exists(frontend_path) and os.path.isdir(frontend_path):
        app.mount("/static", StaticFiles(directory=frontend_path, html=True), name="frontend")
except Exception as e:
    print(f"[INFO] Frontend static files not mounted: {e}")
