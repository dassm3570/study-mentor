from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from aether.core.brain import CoreBrain
from aether.engines.goal_manager import GoalManager

router = APIRouter()
brain = CoreBrain()
goal_manager = GoalManager()

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
    return {
        "brain_online": brain.active,
        "active_threads": 0,
        "cognitive_load": "0%"
    }

@router.post("/think")
async def process_thought(payload: Dict[str, Any]):
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
    return goal_manager.list_missions(status=status)

@router.patch("/missions/{mission_id}", response_model=Dict[str, Any])
async def update_mission(mission_id: int, updates: MissionUpdate):
    try:
        updated = goal_manager.update_mission(mission_id, updates.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Mission not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/missions/{mission_id}/activate", response_model=Dict[str, Any])
async def activate_mission(mission_id: int):
    try:
        return goal_manager.activate_mission(mission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/missions/{mission_id}/pause", response_model=Dict[str, Any])
async def pause_mission(mission_id: int):
    try:
        return goal_manager.pause_mission(mission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/missions/{mission_id}/complete", response_model=Dict[str, Any])
async def complete_mission(mission_id: int):
    try:
        return goal_manager.complete_mission(mission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/missions/{mission_id}/archive", response_model=Dict[str, Any])
async def archive_mission(mission_id: int):
    try:
        return goal_manager.archive_mission(mission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Milestone & Dependency Management ---

@router.post("/missions/{mission_id}/milestones", response_model=Dict[str, Any])
async def add_milestone(mission_id: int, milestone: MilestoneCreate):
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
    details = goal_manager.workspace_manager.get_workspace_details(mission_id)
    if not details:
        raise HTTPException(status_code=404, detail="Workspace or mission not found")
    return details

@router.post("/missions/{mission_id}/workspace/notes", response_model=Dict[str, Any])
async def add_note(mission_id: int, note: NoteCreate):
    filepath = goal_manager.workspace_manager.add_note(mission_id, note.title, note.content)
    return {"status": "success", "filepath": filepath}

@router.post("/missions/{mission_id}/workspace/documents", response_model=Dict[str, Any])
async def add_document(mission_id: int, doc: DocumentCreate):
    filepath = goal_manager.workspace_manager.add_document(mission_id, doc.filename, doc.content)
    return {"status": "success", "filepath": filepath}

@router.post("/missions/{mission_id}/workspace/progress", response_model=Dict[str, Any])
async def update_progress(mission_id: int, progress: ProgressUpdate):
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
shared_memory = SharedMemory()

class PreferenceStore(BaseModel):
    key: str
    value: Any

class ContextUpdate(BaseModel):
    updates: Dict[str, Any]

class HistoryEventCreate(BaseModel):
    event: str

@router.get("/memory/preferences", response_model=Dict[str, Any])
async def get_preferences():
    return shared_memory.memory.get("preferences", {})

@router.post("/memory/preferences", response_model=Dict[str, Any])
async def store_preference(pref: PreferenceStore):
    shared_memory.store_preference(pref.key, pref.value)
    return {"status": "success", "key": pref.key, "value": pref.value}

@router.get("/memory/context", response_model=Dict[str, Any])
async def get_context():
    return shared_memory.get_context()

@router.post("/memory/context", response_model=Dict[str, Any])
async def update_context(ctx: ContextUpdate):
    shared_memory.update_context(ctx.updates)
    return {"status": "success", "context": shared_memory.get_context()}

@router.get("/memory/history", response_model=List[Dict[str, Any]])
async def get_history():
    return shared_memory.get_history()

@router.post("/memory/history", response_model=Dict[str, Any])
async def add_history_event(event: HistoryEventCreate):
    shared_memory.add_history_event(event.event)
    return {"status": "success", "event": event.event}

# --- Knowledge Engine Endpoints ---

from aether.engines.knowledge_engine import KnowledgeEngine
knowledge_engine = KnowledgeEngine()

class RoadmapRequest(BaseModel):
    topic: str

class StudyNotesRequest(BaseModel):
    topic: str

class SummaryRequest(BaseModel):
    content: str

@router.post("/knowledge/roadmap", response_model=Dict[str, Any])
async def generate_roadmap(req: RoadmapRequest):
    return await knowledge_engine.generate_roadmap(req.topic)

@router.post("/knowledge/notes", response_model=Dict[str, Any])
async def generate_study_notes(req: StudyNotesRequest):
    notes = await knowledge_engine.generate_study_notes(req.topic)
    return {"topic": req.topic, "notes": notes}

@router.post("/knowledge/summary", response_model=Dict[str, Any])
async def generate_summary(req: SummaryRequest):
    summary = await knowledge_engine.generate_summary(req.content)
    return {"summary": summary}


# --- Innovation Engine Endpoints ---

from aether.engines.innovation_engine import InnovationEngine
innovation_engine = InnovationEngine()

class InnovationRequest(BaseModel):
    goal: str
    industry: Optional[str] = None
    focus_area: Optional[str] = None

@router.post("/innovation/generate", response_model=Dict[str, Any])
async def generate_innovation(req: InnovationRequest):
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
genesis_engine = GenesisEngine()

class GenesisRequest(BaseModel):
    goal: str
    modules: Optional[List[str]] = None
    tech_stack: Optional[str] = None
    db_type: Optional[str] = None

@router.post("/genesis/generate", response_model=Dict[str, Any])
async def generate_genesis(req: GenesisRequest):
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







