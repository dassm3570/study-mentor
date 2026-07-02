# pyrefly: ignore [missing-import]
import logging
from typing import Dict, Any, List

logger = logging.getLogger("aether.generators.fastapi_generator")


class FastAPIGenerator:
    """
    Generates a FastAPI project structure based on an AI blueprint.
    """

    def __init__(self) -> None:
        pass

    def generate(self, blueprint: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Returns a list of FastAPI files dynamically populated with the blueprint metadata.
        """
        logger.info("Generating FastAPI backend files from blueprint.")

        # Extract information from blueprint to customize files
        project_title = blueprint.get("Executive Summary", "AETHER Generated API").split("\n")[0]
        # Clean title to fit Pydantic string defaults safely
        project_title = project_title.replace('"', '\\"').strip("# ")

        # 1. backend/config.py
        config_content = f"""from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "{project_title}"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite+aiosqlite:///./aether.db"
    
    class Config:
        case_sensitive = True

settings = Settings()
"""

        # 2. backend/models.py
        models_content = """from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Boolean

class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "items"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
"""

        # 3. backend/api/routes.py
        routes_content = """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select
from typing import List
from pydantic import BaseModel
from backend.config import settings
from backend.models import Base, Item

router = APIRouter()

# Async Database Engine and Session
engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Pydantic schemas
class ItemBase(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    
    class Config:
        from_attributes = True

# Dependency to get async DB session
async def get_db():
    async with async_session() as session:
        yield session

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Check database connectivity
        await db.execute(select(1))
        return {
            "status": "healthy",
            "database": "connected",
            "project": settings.PROJECT_NAME
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

@router.get("/items", response_model=List[ItemResponse])
async def read_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).offset(skip).limit(limit))
    items = result.scalars().all()
    return items

@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = Item(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item
"""

        # 4. backend/main.py
        main_content = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.config import settings
from backend.api.routes import router as api_router, engine
from backend.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up / close engine on shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}!",
        "docs_url": "/docs",
        "api_health_url": f"{settings.API_V1_STR}/health"
    }
"""

        # 5. backend/requirements.txt
        requirements_content = """fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
pydantic-settings>=2.2.0
sqlalchemy>=2.0.0
aiosqlite>=0.20.0
"""

        logger.info("FastAPI backend files successfully prepared.")

        return [
            {"path": "backend/main.py", "content": main_content},
            {"path": "backend/api/routes.py", "content": routes_content},
            {"path": "backend/models.py", "content": models_content},
            {"path": "backend/config.py", "content": config_content},
            {"path": "backend/requirements.txt", "content": requirements_content},
        ]
