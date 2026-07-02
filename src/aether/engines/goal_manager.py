import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from aether.core.interfaces import WorkspaceManagerInterface

logger = logging.getLogger("aether.engines.goal_manager")

class GoalManager:
    """
    Manages long-term, medium-term, and short-term goals (Missions).
    Supports creating, listing, updating, completing, and archiving missions,
    as well as milestones, dependencies, and automatic progress tracking.
    Stores data locally in a JSON file.
    """
    def __init__(self, storage_path: str = "data/missions.json", workspace_manager: Optional[WorkspaceManagerInterface] = None):
        self.storage_path = storage_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        if workspace_manager is None:
            from aether.engines.workspace_manager import WorkspaceManager
            self.workspace_manager = WorkspaceManager()
        else:
            self.workspace_manager = workspace_manager
            
        self.missions: List[Dict[str, Any]] = self._load_missions()

    def _load_missions(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading missions from local file: {e}")
                return []
        return []

    def _save_missions(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.missions, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving missions to local file: {e}")

    def get_mission(self, mission_id: int) -> Optional[Dict[str, Any]]:
        for mission in self.missions:
            if mission["id"] == mission_id:
                return mission
        return None

    def create_mission(
        self, 
        title: str, 
        description: str, 
        priority: int = 1,
        dependencies: Optional[List[int]] = None,
        milestones: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        mission_id = len(self.missions) + 1
        
        # Automatically create workspace for the new mission
        workspace_details = self.workspace_manager.create_workspace(mission_id)

        deps = dependencies or []
        
        # Format milestones if provided
        formatted_milestones = []
        if milestones:
            for i, m in enumerate(milestones):
                formatted_milestones.append({
                    "id": i + 1,
                    "title": m.get("title", f"Milestone {i + 1}"),
                    "description": m.get("description", ""),
                    "status": m.get("status", "pending")  # pending, completed
                })

        mission = {
            "id": mission_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending",  # pending, active, paused, completed, archived
            "dependencies": deps,
            "milestones": formatted_milestones,
            "progress_percentage": 0,
            "workspace_path": workspace_details["workspace_directory"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Check if initial dependencies would cause a cycle
        if deps and self._would_cause_cycle(mission_id, deps):
            raise ValueError("Setting these dependencies would cause a circular dependency loop.")

        self.missions.append(mission)
        self._recalculate_progress(mission)
        self._save_missions()
        logger.info(f"Mission created: '{title}' (ID: {mission['id']}) and workspace initialized.")
        return mission

    def list_missions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            return [m for m in self.missions if m["status"] == status]
        return self.missions

    def update_mission(self, mission_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        mission = self.get_mission(mission_id)
        if not mission:
            logger.warning(f"Mission with ID {mission_id} not found for update.")
            return None

        # Handle dependencies change
        if "dependencies" in updates:
            new_deps = updates["dependencies"]
            if self._would_cause_cycle(mission_id, new_deps):
                raise ValueError("Setting these dependencies would cause a circular dependency loop.")
            mission["dependencies"] = new_deps

        # Handle status change validation
        if "status" in updates:
            new_status = updates["status"]
            if new_status == "active":
                can_act, reason = self._can_activate(mission)
                if not can_act:
                    raise ValueError(f"Cannot activate mission: {reason}")
            elif new_status == "completed":
                # Ensure all milestones are completed
                for m in mission.get("milestones", []):
                    if m["status"] != "completed":
                        raise ValueError(f"Cannot complete mission: Milestone '{m['title']}' is not completed.")
            mission["status"] = new_status

        # Standard field updates
        for key in ["title", "description", "priority"]:
            if key in updates:
                mission[key] = updates[key]

        mission["updated_at"] = datetime.utcnow().isoformat()
        self._recalculate_progress(mission)
        self._save_missions()
        logger.info(f"Mission {mission_id} updated.")
        return mission

    def activate_mission(self, mission_id: int) -> Dict[str, Any]:
        updated = self.update_mission(mission_id, {"status": "active"})
        if not updated:
            raise ValueError(f"Mission with ID {mission_id} not found.")
        return updated

    def pause_mission(self, mission_id: int) -> Dict[str, Any]:
        updated = self.update_mission(mission_id, {"status": "paused"})
        if not updated:
            raise ValueError(f"Mission with ID {mission_id} not found.")
        return updated

    def complete_mission(self, mission_id: int) -> Dict[str, Any]:
        # Force all milestones to be completed if completed from this method
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Mission with ID {mission_id} not found.")
        
        for m in mission.get("milestones", []):
            m["status"] = "completed"
        
        updated = self.update_mission(mission_id, {"status": "completed"})
        return updated

    def archive_mission(self, mission_id: int) -> Dict[str, Any]:
        updated = self.update_mission(mission_id, {"status": "archived"})
        if not updated:
            raise ValueError(f"Mission with ID {mission_id} not found.")
        return updated

    # --- Milestone Management ---

    def add_milestone(self, mission_id: int, title: str, description: str = "") -> Dict[str, Any]:
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Mission with ID {mission_id} not found.")

        milestones = mission.setdefault("milestones", [])
        milestone_id = len(milestones) + 1
        milestone = {
            "id": milestone_id,
            "title": title,
            "description": description,
            "status": "pending"
        }
        milestones.append(milestone)
        self._recalculate_progress(mission)
        mission["updated_at"] = datetime.utcnow().isoformat()
        self._save_missions()
        logger.info(f"Milestone '{title}' added to Mission {mission_id}.")
        return milestone

    def update_milestone(self, mission_id: int, milestone_id: int, status: str) -> Dict[str, Any]:
        if status not in ["pending", "completed"]:
            raise ValueError("Milestone status must be 'pending' or 'completed'.")

        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Mission with ID {mission_id} not found.")

        milestone_found = False
        target_milestone = None
        for m in mission.get("milestones", []):
            if m["id"] == milestone_id:
                m["status"] = status
                target_milestone = m
                milestone_found = True
                break

        if not milestone_found:
            raise ValueError(f"Milestone with ID {milestone_id} not found in Mission {mission_id}.")

        self._recalculate_progress(mission)
        mission["updated_at"] = datetime.utcnow().isoformat()
        self._save_missions()
        logger.info(f"Milestone {milestone_id} in Mission {mission_id} updated to '{status}'.")
        return target_milestone

    # --- Dependency Management & Helpers ---

    def set_dependencies(self, mission_id: int, dependency_ids: List[int]) -> Dict[str, Any]:
        updated = self.update_mission(mission_id, {"dependencies": dependency_ids})
        if not updated:
            raise ValueError(f"Mission with ID {mission_id} not found.")
        return updated

    def _recalculate_progress(self, mission: Dict[str, Any]):
        milestones = mission.get("milestones", [])
        if not milestones:
            if mission["status"] == "completed":
                mission["progress_percentage"] = 100
            else:
                mission["progress_percentage"] = 0
            return
        
        completed_count = sum(1 for m in milestones if m["status"] == "completed")
        mission["progress_percentage"] = int((completed_count / len(milestones)) * 100)

    def _would_cause_cycle(self, mission_id: int, new_dependencies: List[int]) -> bool:
        # Build adjacency list representation of the dependency graph
        # using existing missions but substituting the new dependencies for mission_id
        graph = {}
        for m in self.missions:
            m_id = m["id"]
            if m_id == mission_id:
                graph[m_id] = new_dependencies
            else:
                graph[m_id] = m.get("dependencies", [])
        
        # Also ensure mission_id is in the graph even if self.missions doesn't have it yet
        if mission_id not in graph:
            graph[mission_id] = new_dependencies

        # Add any dependency IDs that might not exist in the graph yet
        for dep_list in graph.values():
            for dep_id in dep_list:
                if dep_id not in graph:
                    graph[dep_id] = []
                    
        visited = {} # 0 = unvisited, 1 = visiting, 2 = visited
        
        def dfs(node):
            visited[node] = 1
            for neighbor in graph.get(node, []):
                if visited.get(neighbor, 0) == 1:
                    return True
                if visited.get(neighbor, 0) == 0:
                    if dfs(neighbor):
                        return True
            visited[node] = 2
            return False

        for node in graph:
            if visited.get(node, 0) == 0:
                if dfs(node):
                    return True
        return False

    def _can_activate(self, mission: Dict[str, Any]) -> tuple[bool, str]:
        for dep_id in mission.get("dependencies", []):
            dep_mission = self.get_mission(dep_id)
            if not dep_mission:
                return False, f"Dependency mission ID {dep_id} does not exist."
            if dep_mission["status"] != "completed":
                return False, f"Dependency mission ID {dep_id} ('{dep_mission['title']}') is not completed (current status: {dep_mission['status']})."
        return True, ""
