from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from aether.core.brain import CoreBrain
from aether.engines.goal_manager import GoalManager

router = APIRouter()

# Lazy initialization for serverless compatibility
_brain = None
_goal_manager = None

def get_brain():
    global _brain
    if _brain is None:
        try:
            _brain = CoreBrain()
        except Exception as e:
            print(f"Warning: CoreBrain initialization failed: {e}")
            _brain = None
    return _brain

def get_goal_manager():
    global _goal_manager
    if _goal_manager is None:
        try:
            _goal_manager = GoalManager()
        except Exception as e:
            print(f"Warning: GoalManager initialization failed: {e}")
            _goal_manager = None
    return _goal_manager

class MissionCreate(BaseModel):
    title: str
    description: str
    priority: Optional[int] = 1

class MissionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None

@router.get("/status")
async def get_system_status():
    brain = get_brain()
    return {
        "brain_online": brain.active if brain else False,
        "active_threads": 0,
        "cognitive_load": "0%"
    }

@router.post("/think")
async def process_thought(payload: Dict[str, Any]):
    brain = get_brain()
    if brain is None:
        raise HTTPException(status_code=503, detail="System not available")
    if not brain.active:
        await brain.startup()
    result = await brain.process_thought(payload)
    return result

# --- Goal Manager (Missions) Endpoints ---

class MilestoneCreate(BaseModel):
    title: str
    description: Optional[str] = ""

class MilestoneUpdate(BaseModel):
    status: str

class DependencyUpdate(BaseModel):
    dependency_ids: List[int]

@router.post("/missions", response_model=Dict[str, Any])
async def create_mission(mission: MissionCreate):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    try:
        return goal_manager.create_mission(
            title=mission.title,
            description=mission.description,
            priority=mission.priority
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/missions", response_model=List[Dict[str, Any]])
async def list_missions(status: Optional[str] = Query(None, description="Filter by status (pending, active, paused, completed, archived)")):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    return goal_manager.list_missions(status=status)

@router.patch("/missions/{mission_id}", response_model=Dict[str, Any])
async def update_mission(mission_id: int, updates: MissionUpdate):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    try:
        updated = goal_manager.update_mission(mission_id, updates.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Mission not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/missions/{mission_id}/activate", response_model=Dict[str, Any])
async def activate_mission(mission_id: int):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    try:
        return goal_manager.activate_mission(mission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/missions/{mission_id}/pause", response_model=Dict[str, Any])
async def pause_mission(mission_id: int):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    try:
        return goal_manager.pause_mission(mission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/missions/{mission_id}/complete", response_model=Dict[str, Any])
async def complete_mission(mission_id: int):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    try:
        return goal_manager.complete_mission(mission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/missions/{mission_id}/archive", response_model=Dict[str, Any])
async def archive_mission(mission_id: int):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    try:
        return goal_manager.archive_mission(mission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Milestone & Dependency Management ---

@router.post("/missions/{mission_id}/milestones", response_model=Dict[str, Any])
async def add_milestone(mission_id: int, milestone: MilestoneCreate):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    try:
        return goal_manager.add_milestone(
            mission_id=mission_id,
            title=milestone.title,
            description=milestone.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/missions/{mission_id}/milestones/{milestone_id}", response_model=Dict[str, Any])
async def update_milestone(mission_id: int, milestone_id: int, milestone_update: MilestoneUpdate):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    try:
        return goal_manager.update_milestone(
            mission_id=mission_id,
            milestone_id=milestone_id,
            status=milestone_update.status
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/missions/{mission_id}/dependencies", response_model=Dict[str, Any])
async def set_dependencies(mission_id: int, dep: DependencyUpdate):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    try:
        return goal_manager.set_dependencies(
            mission_id=mission_id,
            dependency_ids=dep.dependency_ids
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Workspace Manager Endpoints ---

class NoteCreate(BaseModel):
    title: str
    content: str

class DocumentCreate(BaseModel):
    filename: str
    content: str

class ProgressUpdate(BaseModel):
    progress_percentage: int
    status_notes: str

@router.get("/missions/{mission_id}/workspace", response_model=Dict[str, Any])
async def get_workspace_details(mission_id: int):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    details = goal_manager.workspace_manager.get_workspace_details(mission_id)
    if not details:
        raise HTTPException(status_code=404, detail="Workspace or mission not found")
    return details

@router.post("/missions/{mission_id}/workspace/notes", response_model=Dict[str, Any])
async def add_note(mission_id: int, note: NoteCreate):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    filepath = goal_manager.workspace_manager.add_note(mission_id, note.title, note.content)
    return {"status": "success", "filepath": filepath}

@router.post("/missions/{mission_id}/workspace/documents", response_model=Dict[str, Any])
async def add_document(mission_id: int, doc: DocumentCreate):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    filepath = goal_manager.workspace_manager.add_document(mission_id, doc.filename, doc.content)
    return {"status": "success", "filepath": filepath}

@router.post("/missions/{mission_id}/workspace/progress", response_model=Dict[str, Any])
async def update_progress(mission_id: int, progress: ProgressUpdate):
    goal_manager = get_goal_manager()
    if goal_manager is None:
        raise HTTPException(status_code=503, detail="System not available")
    updated = goal_manager.workspace_manager.update_progress(
        mission_id, 
        progress.progress_percentage, 
        progress.status_notes
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return updated

# --- Shared Memory Endpoints ---

from aether.engines.shared_memory import SharedMemory
_shared_memory = None

def get_shared_memory():
    global _shared_memory
    if _shared_memory is None:
        try:
            _shared_memory = SharedMemory()
        except Exception as e:
            print(f"Warning: SharedMemory initialization failed: {e}")
            _shared_memory = None
    return _shared_memory

class PreferenceStore(BaseModel):
    key: str
    value: Any

class ContextUpdate(BaseModel):
    updates: Dict[str, Any]

class HistoryEventCreate(BaseModel):
    event: str

@router.get("/memory/preferences", response_model=Dict[str, Any])
async def get_preferences():
    shared_memory = get_shared_memory()
    if shared_memory is None:
        raise HTTPException(status_code=503, detail="System not available")
    return shared_memory.memory.get("preferences", {})

@router.post("/memory/preferences", response_model=Dict[str, Any])
async def store_preference(pref: PreferenceStore):
    shared_memory = get_shared_memory()
    if shared_memory is None:
        raise HTTPException(status_code=503, detail="System not available")
    shared_memory.store_preference(pref.key, pref.value)
    return {"status": "success", "key": pref.key, "value": pref.value}

@router.get("/memory/context", response_model=Dict[str, Any])
async def get_context():
    shared_memory = get_shared_memory()
    if shared_memory is None:
        raise HTTPException(status_code=503, detail="System not available")
    return shared_memory.get_context()

@router.post("/memory/context", response_model=Dict[str, Any])
async def update_context(ctx: ContextUpdate):
    shared_memory = get_shared_memory()
    if shared_memory is None:
        raise HTTPException(status_code=503, detail="System not available")
    shared_memory.update_context(ctx.updates)
    return {"status": "success", "context": shared_memory.get_context()}

@router.get("/memory/history", response_model=List[Dict[str, Any]])
async def get_history():
    shared_memory = get_shared_memory()
    if shared_memory is None:
        raise HTTPException(status_code=503, detail="System not available")
    return shared_memory.get_history()

@router.post("/memory/history", response_model=Dict[str, Any])
async def add_history_event(event: HistoryEventCreate):
    shared_memory = get_shared_memory()
    if shared_memory is None:
        raise HTTPException(status_code=503, detail="System not available")
    shared_memory.add_history_event(event.event)
    return {"status": "success", "event": event.event}

# --- Knowledge Engine Endpoints ---

from aether.engines.knowledge_engine import KnowledgeEngine
_knowledge_engine = None

def get_knowledge_engine():
    global _knowledge_engine
    if _knowledge_engine is None:
        try:
            _knowledge_engine = KnowledgeEngine()
        except Exception as e:
            print(f"Warning: KnowledgeEngine initialization failed: {e}")
            _knowledge_engine = None
    return _knowledge_engine

class RoadmapRequest(BaseModel):
    topic: str

class StudyNotesRequest(BaseModel):
    topic: str

class SummaryRequest(BaseModel):
    content: str

@router.post("/knowledge/roadmap", response_model=Dict[str, Any])
async def generate_roadmap(req: RoadmapRequest):
    knowledge_engine = get_knowledge_engine()
    if knowledge_engine is None:
        raise HTTPException(status_code=503, detail="System not available")
    return await knowledge_engine.generate_roadmap(req.topic)

@router.post("/knowledge/notes", response_model=Dict[str, Any])
async def generate_study_notes(req: StudyNotesRequest):
    knowledge_engine = get_knowledge_engine()
    if knowledge_engine is None:
        raise HTTPException(status_code=503, detail="System not available")
    notes = await knowledge_engine.generate_study_notes(req.topic)
    return {"topic": req.topic, "notes": notes}

@router.post("/knowledge/summary", response_model=Dict[str, Any])
async def generate_summary(req: SummaryRequest):
    knowledge_engine = get_knowledge_engine()
    if knowledge_engine is None:
        raise HTTPException(status_code=503, detail="System not available")
    summary = await knowledge_engine.generate_summary(req.content)
    return {"summary": summary}


# --- Innovation Engine Endpoints ---

from aether.engines.innovation_engine import InnovationEngine
_innovation_engine = None

def get_innovation_engine():
    global _innovation_engine
    if _innovation_engine is None:
        try:
            _innovation_engine = InnovationEngine()
        except Exception as e:
            print(f"Warning: InnovationEngine initialization failed: {e}")
            _innovation_engine = None
    return _innovation_engine

class InnovationRequest(BaseModel):
    goal: str
    industry: Optional[str] = None
    focus_area: Optional[str] = None

@router.post("/innovation/generate", response_model=Dict[str, Any])
async def generate_innovation(req: InnovationRequest):
    innovation_engine = get_innovation_engine()
    if innovation_engine is None:
        raise HTTPException(status_code=503, detail="System not available")
    try:
        result = innovation_engine.generate_innovation_package(
            goal=req.goal,
            industry=req.industry,
            focus_area=req.focus_area
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Genesis Engine Endpoints ---

from aether.engines.genesis_engine import GenesisEngine
_genesis_engine = None

def get_genesis_engine():
    global _genesis_engine
    if _genesis_engine is None:
        try:
            _genesis_engine = GenesisEngine()
        except Exception as e:
            print(f"Warning: GenesisEngine initialization failed: {e}")
            _genesis_engine = None
    return _genesis_engine

class GenesisRequest(BaseModel):
    goal: str
    modules: Optional[List[str]] = None
    tech_stack: Optional[str] = None
    db_type: Optional[str] = None

@router.post("/genesis/generate", response_model=Dict[str, Any])
async def generate_genesis(req: GenesisRequest):
    genesis_engine = get_genesis_engine()
    if genesis_engine is None:
        raise HTTPException(status_code=503, detail="System not available")
    try:
        options = {}
        if req.modules:
            options["modules"] = req.modules
        if req.tech_stack:
            options["tech_stack"] = req.tech_stack
        if req.db_type:
            options["db_type"] = req.db_type

        result = await genesis_engine.generate_blueprint(
            goal=req.goal,
            options=options
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







