from typing import Dict, Any, List, Optional, Protocol, runtime_checkable

@runtime_checkable
class SharedMemoryInterface(Protocol):
    def store(self, category: str, key: str, value: Any) -> None:
        ...

    def retrieve(self, category: str, query: str) -> Any:
        ...

    def get_preference(self, key: str, default: Any = None) -> Any:
        ...

    def store_preference(self, key: str, value: Any) -> None:
        ...

    def add_history_event(self, event: str) -> None:
        ...

    def update_context(self, updates: Dict[str, Any]) -> None:
        ...


@runtime_checkable
class WorkspaceManagerInterface(Protocol):
    def create_workspace(self, mission_id: int) -> Dict[str, Any]:
        ...

    def get_workspace_details(self, mission_id: int) -> Optional[Dict[str, Any]]:
        ...

    def add_note(self, mission_id: int, title: str, content: str) -> str:
        ...

    def add_document(self, mission_id: int, filename: str, content: str) -> str:
        ...

    def add_conversation(self, mission_id: int, conversation_id: str, messages: List[Dict[str, Any]]) -> str:
        ...

    def add_task(self, mission_id: int, task_id: str, task_data: Dict[str, Any]) -> str:
        ...

    def add_architecture(self, mission_id: int, arch_id: str, content: str) -> str:
        ...

    def add_source_code_reference(self, mission_id: int, ref_id: str, data: Dict[str, Any]) -> str:
        ...

    def add_timeline(self, mission_id: int, timeline_data: List[Dict[str, Any]]) -> str:
        ...

    def update_project_memory(self, mission_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def get_project_memory(self, mission_id: int) -> Optional[Dict[str, Any]]:
        ...

    def update_progress(self, mission_id: int, progress_percentage: int, status_notes: str) -> Optional[Dict[str, Any]]:
        ...


@runtime_checkable
class GoalManagerInterface(Protocol):
    def get_mission(self, mission_id: int) -> Optional[Dict[str, Any]]:
        ...

    def create_mission(
        self, 
        title: str, 
        description: str, 
        priority: int = 1,
        dependencies: Optional[List[int]] = None,
        milestones: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        ...

    def list_missions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        ...


@runtime_checkable
class KnowledgeEngineInterface(Protocol):
    async def generate_roadmap(self, topic: str, user_id: str = "default_user") -> Dict[str, Any]:
        ...


@runtime_checkable
class InnovationEngineInterface(Protocol):
    async def brainstorm(self, challenge: str) -> Dict[str, Any]:
        ...


@runtime_checkable
class GenesisEngineInterface(Protocol):
    async def generate_blueprint(self, goal: str) -> Dict[str, Any]:
        ...


@runtime_checkable
class ReflectionEngineInterface(Protocol):
    async def analyze_performance(self, execution_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        ...


@runtime_checkable
class EvolutionEngineInterface(Protocol):
    async def evolve_system(self, reflection_report: Dict[str, Any], user_feedback: Optional[str] = None) -> Dict[str, Any]:
        ...
