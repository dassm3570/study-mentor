import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from aether.core.interfaces import SharedMemoryInterface

logger = logging.getLogger("aether.engines.workspace_manager")

class WorkspaceManager:
    """
    Manages isolated workspace directories for AETHER 2.0 missions.
    Each workspace stores:
      - Conversations
      - Generated files
      - Documents
      - Tasks
      - Notes
      - Architecture
      - Source code references
      - Timelines
      - Project-specific memory (linked to global Shared Memory)
    """
    def __init__(self, base_path: str = "workspaces", global_memory: Optional[SharedMemoryInterface] = None):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        
        # Instantiate global shared memory link if not injected
        if global_memory is None:
            from aether.engines.shared_memory import SharedMemory
            self.global_memory = SharedMemory()
        else:
            self.global_memory = global_memory

    def _get_workspace_dir(self, mission_id: Any) -> str:
        return os.path.join(self.base_path, f"mission_{mission_id}")

    def create_workspace(self, mission_id: Optional[int] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a dedicated, isolated workspace directory structure for a mission or session.
        """
        target_id = mission_id if mission_id is not None else (session_id if session_id is not None else 0)
        ws_dir = self._get_workspace_dir(target_id)
        
        # Define isolated subdirectories
        subdirs = [
            "conversations",
            "generated_files",
            "documents",
            "tasks",
            "notes",
            "architecture",
            "source_code_references",
            "timelines",
            "memory"
        ]
        for subdir in subdirs:
            os.makedirs(os.path.join(ws_dir, subdir), exist_ok=True)

        # Initialize progress file
        progress_path = os.path.join(ws_dir, "progress.json")
        initial_progress = {
            "mission_id": target_id,
            "progress_percentage": 0,
            "last_updated": datetime.utcnow().isoformat(),
            "status_notes": "Workspace initialized with full module structure."
        }
        with open(progress_path, "w") as f:
            json.dump(initial_progress, f, indent=4)

        # Initialize local project-specific memory
        local_mem_path = os.path.join(ws_dir, "memory", "project_memory.json")
        initial_mem = {
            "mission_id": target_id,
            "created_at": datetime.utcnow().isoformat(),
            "context": {},
            "key_values": {}
        }
        with open(local_mem_path, "w") as f:
            json.dump(initial_mem, f, indent=4)

        # Link project-specific memory metadata to the global Shared Memory
        self.global_memory.store(
            category="project_workspaces",
            key=f"mission_{target_id}",
            value={
                "workspace_directory": ws_dir,
                "initialized_at": datetime.utcnow().isoformat(),
                "local_memory_path": local_mem_path
            }
        )

        logger.info(f"Isolated workspace created for mission {target_id} at {ws_dir}")
        
        return {
            "workspace_directory": ws_dir,
            "structure": subdirs,
            "progress": initial_progress
        }

    def get_workspace_details(self, mission_id: int) -> Optional[Dict[str, Any]]:
        ws_dir = self._get_workspace_dir(mission_id)
        if not os.path.exists(ws_dir):
            return None
        
        progress_path = os.path.join(ws_dir, "progress.json")
        progress = {}
        if os.path.exists(progress_path):
            with open(progress_path, "r") as f:
                progress = json.load(f)

        details = {
            "workspace_directory": ws_dir,
            "progress": progress
        }

        # Collect counts of files in each category
        subdirs = [
            "conversations", "generated_files", "documents", 
            "tasks", "notes", "architecture", "source_code_references", "timelines"
        ]
        for subdir in subdirs:
            path = os.path.join(ws_dir, subdir)
            details[f"{subdir}_count"] = len(os.listdir(path)) if os.path.exists(path) else 0

        return details

    def add_note(self, mission_id: int, title: str, content: str) -> str:
        ws_dir = self._get_workspace_dir(mission_id)
        notes_dir = os.path.join(ws_dir, "notes")
        os.makedirs(notes_dir, exist_ok=True)
        
        filename = f"{title.lower().replace(' ', '_')}.txt"
        filepath = os.path.join(notes_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def add_document(self, mission_id: int, filename: str, content: str) -> str:
        ws_dir = self._get_workspace_dir(mission_id)
        docs_dir = os.path.join(ws_dir, "documents")
        os.makedirs(docs_dir, exist_ok=True)
        
        filepath = os.path.join(docs_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def add_conversation(self, mission_id: int, conversation_id: str, messages: List[Dict[str, Any]]) -> str:
        ws_dir = self._get_workspace_dir(mission_id)
        conv_dir = os.path.join(ws_dir, "conversations")
        os.makedirs(conv_dir, exist_ok=True)
        
        filepath = os.path.join(conv_dir, f"{conversation_id}.json")
        with open(filepath, "w") as f:
            json.dump({"conversation_id": conversation_id, "messages": messages, "updated_at": datetime.utcnow().isoformat()}, f, indent=4)
        return filepath

    def add_task(self, mission_id: int, task_id: str, task_data: Dict[str, Any]) -> str:
        ws_dir = self._get_workspace_dir(mission_id)
        tasks_dir = os.path.join(ws_dir, "tasks")
        os.makedirs(tasks_dir, exist_ok=True)
        
        filepath = os.path.join(tasks_dir, f"{task_id}.json")
        with open(filepath, "w") as f:
            json.dump(task_data, f, indent=4)
        return filepath

    def add_architecture(self, mission_id: int, arch_id: str, content: str) -> str:
        ws_dir = self._get_workspace_dir(mission_id)
        arch_dir = os.path.join(ws_dir, "architecture")
        os.makedirs(arch_dir, exist_ok=True)
        
        filepath = os.path.join(arch_dir, f"{arch_id}.md")
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def add_source_code_reference(self, mission_id: int, ref_id: str, data: Dict[str, Any]) -> str:
        ws_dir = self._get_workspace_dir(mission_id)
        ref_dir = os.path.join(ws_dir, "source_code_references")
        os.makedirs(ref_dir, exist_ok=True)
        
        filepath = os.path.join(ref_dir, f"{ref_id}.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        return filepath

    def add_timeline(self, mission_id: int, timeline_data: List[Dict[str, Any]]) -> str:
        ws_dir = self._get_workspace_dir(mission_id)
        timeline_dir = os.path.join(ws_dir, "timelines")
        os.makedirs(timeline_dir, exist_ok=True)
        
        filepath = os.path.join(timeline_dir, "timeline.json")
        with open(filepath, "w") as f:
            json.dump(timeline_data, f, indent=4)
        return filepath

    # --- Project-specific Memory Management ---

    def update_project_memory(self, mission_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the project-specific memory located inside the workspace
        and syncs key metadata/context with the global Shared Memory.
        """
        ws_dir = self._get_workspace_dir(mission_id)
        mem_path = os.path.join(ws_dir, "memory", "project_memory.json")
        
        if not os.path.exists(mem_path):
            raise ValueError(f"Project memory file does not exist for mission {mission_id}")

        with open(mem_path, "r") as f:
            local_mem = json.load(f)

        # Merge updates into context or key_values
        local_mem["context"].update(updates.get("context", {}))
        local_mem["key_values"].update(updates.get("key_values", {}))
        local_mem["updated_at"] = datetime.utcnow().isoformat()

        with open(mem_path, "w") as f:
            json.dump(local_mem, f, indent=4)

        # Sync key details to the global Shared Memory for discovery/cross-reference
        self.global_memory.store(
            category="project_memory_indices",
            key=f"mission_{mission_id}",
            value={
                "last_updated": local_mem["updated_at"],
                "context_keys": list(local_mem["context"].keys()),
                "value_keys": list(local_mem["key_values"].keys())
            }
        )

        logger.info(f"Updated project memory for mission {mission_id} and synced to global memory.")
        return local_mem

    def get_project_memory(self, mission_id: int) -> Optional[Dict[str, Any]]:
        ws_dir = self._get_workspace_dir(mission_id)
        mem_path = os.path.join(ws_dir, "memory", "project_memory.json")
        if not os.path.exists(mem_path):
            return None
        with open(mem_path, "r") as f:
            return json.load(f)

    def update_progress(self, mission_id: int, progress_percentage: int, status_notes: str) -> Optional[Dict[str, Any]]:
        ws_dir = self._get_workspace_dir(mission_id)
        progress_path = os.path.join(ws_dir, "progress.json")
        if not os.path.exists(progress_path):
            return None

        updated_progress = {
            "mission_id": mission_id,
            "progress_percentage": progress_percentage,
            "last_updated": datetime.utcnow().isoformat(),
            "status_notes": status_notes
        }
        with open(progress_path, "w") as f:
            json.dump(updated_progress, f, indent=4)

        logger.info(f"Progress updated for mission {mission_id}: {progress_percentage}%")
        return updated_progress
