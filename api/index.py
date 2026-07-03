import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.aether.main import app
except ImportError as e:
    # Fallback: create minimal app if imports fail
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(title="AETHER 2.0 - Error Mode")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"error": f"Failed to initialize main app: {str(e)}"}
    
    @app.get("/health")
    async def health():
        return {"status": "degraded", "error": str(e)}
    
    print(f"[STARTUP ERROR] Failed to import app from src.aether.main: {e}")

# For Vercel's serverless handler
__all__ = ["app"]
