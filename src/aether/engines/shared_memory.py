import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("aether.engines.shared_memory")


class MemoryStorageProvider(ABC):
    """
    Abstract interface for Shared Memory storage.
    Allows the underlying storage mechanism to evolve from JSON files to
    relational databases, semantic graphs, or vector-based databases.
    """
    @abstractmethod
    def store(self, category: str, key: str, value: Any):
        pass

    @abstractmethod
    def retrieve(self, category: str, key: str, default: Any = None) -> Any:
        pass

    @abstractmethod
    def delete(self, category: str, key: str) -> bool:
        pass

    @abstractmethod
    def list_keys(self, category: str) -> List[str]:
        pass

    @abstractmethod
    def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """For future semantic/vector search capabilities."""
        pass

    @abstractmethod
    def store_relationship(self, source: str, relation: str, target: str, metadata: Optional[Dict[str, Any]] = None):
        pass

    @abstractmethod
    def get_relationships(self, entity: str) -> List[Dict[str, Any]]:
        pass


class JSONMemoryStorageProvider(MemoryStorageProvider):
    """
    JSON file-based implementation of the MemoryStorageProvider.
    Acts as the default, lightweight storage mechanism.
    """
    def __init__(self, storage_path: str = "data/shared_memory.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.memory: Dict[str, Any] = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading shared memory file: {e}")
                return self._default_memory()
        return self._default_memory()

    def _default_memory(self) -> Dict[str, Any]:
        return {
            "preferences": {},
            "skills": {},
            "long_term_goals": {},
            "projects": {},
            "learning_history": [],
            "context": {},
            "generated_knowledge": {},
            "relationships": [],
            "history": []
        }

    def _save_memory(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving shared memory file: {e}")

    def store(self, category: str, key: str, value: Any):
        if category not in self.memory:
            self.memory[category] = {}
        
        # If it's a list category, append or handle accordingly
        if isinstance(self.memory[category], list):
            self.memory[category].append({"key": key, "value": value, "timestamp": datetime.utcnow().isoformat()})
        else:
            self.memory[category][key] = value
            
        self._save_memory()

    def retrieve(self, category: str, key: str, default: Any = None) -> Any:
        cat_data = self.memory.get(category)
        if cat_data is None:
            return default
        if isinstance(cat_data, list):
            # For lists, search for key
            for item in cat_data:
                if isinstance(item, dict) and item.get("key") == key:
                    return item.get("value")
            return default
        return cat_data.get(key, default)

    def delete(self, category: str, key: str) -> bool:
        if category in self.memory:
            cat_data = self.memory[category]
            if isinstance(cat_data, dict) and key in cat_data:
                del cat_data[key]
                self._save_memory()
                return True
            elif isinstance(cat_data, list):
                # Filter out items matching key
                new_list = [item for item in cat_data if not (isinstance(item, dict) and item.get("key") == key)]
                if len(new_list) != len(cat_data):
                    self.memory[category] = new_list
                    self._save_memory()
                    return True
        return False

    def list_keys(self, category: str) -> List[str]:
        cat_data = self.memory.get(category, {})
        if isinstance(cat_data, dict):
            return list(cat_data.keys())
        elif isinstance(cat_data, list):
            return [item.get("key") for item in cat_data if isinstance(item, dict) and "key" in item]
        return []

    def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Simple text-based keyword search across categories."""
        results = []
        categories_to_search = [category] if category else self.memory.keys()
        query_lower = query.lower()

        for cat in categories_to_search:
            cat_data = self.memory.get(cat)
            if isinstance(cat_data, dict):
                for k, v in cat_data.items():
                    if query_lower in str(k).lower() or query_lower in str(v).lower():
                        results.append({"category": cat, "key": k, "value": v, "type": "exact_match"})
            elif isinstance(cat_data, list):
                for item in cat_data:
                    if query_lower in str(item).lower():
                        results.append({"category": cat, "value": item, "type": "exact_match"})
        return results

    def store_relationship(self, source: str, relation: str, target: str, metadata: Optional[Dict[str, Any]] = None):
        relationship = {
            "source": source,
            "relation": relation,
            "target": target,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        if "relationships" not in self.memory:
            self.memory["relationships"] = []
        self.memory["relationships"].append(relationship)
        self._save_memory()

    def get_relationships(self, entity: str) -> List[Dict[str, Any]]:
        rels = self.memory.get("relationships", [])
        entity_lower = entity.lower()
        return [
            r for r in rels
            if r["source"].lower() == entity_lower or r["target"].lower() == entity_lower
        ]


class SharedMemory:
    """
    Provides persistent global Shared Memory for AETHER 2.0.
    Acts as the global knowledge layer, delegating to an underlying MemoryStorageProvider.
    Stores:
      - User Preferences
      - Skills / Capabilities
      - Long-term goals & Missions
      - Projects & Context
      - Learning history
      - Generated knowledge
      - Entity relationships
    """
    def __init__(self, provider: Optional[MemoryStorageProvider] = None):
        # Default to JSONMemoryStorageProvider if none supplied
        self.provider = provider or JSONMemoryStorageProvider()
        # Maintain public self.memory dictionary reference for backward compatibility with API endpoints
        # delegating back to the JSONMemoryStorageProvider's internal memory dict if possible
        if hasattr(self.provider, "memory"):
            self.memory = getattr(self.provider, "memory")
        else:
            self.memory = {}

    def store(self, category: str, key: str, value: Any):
        self.provider.store(category, key, value)
        logger.info(f"Stored item in category '{category}': '{key}'")

    def retrieve(self, category: str, key: str, default: Any = None) -> Any:
        return self.provider.retrieve(category, key, default)

    def list_keys(self, category: str) -> List[str]:
        return self.provider.list_keys(category)

    # --- Preferences ---
    def store_preference(self, key: str, value: Any):
        self.store("preferences", key, value)

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self.retrieve("preferences", key, default)

    # --- Skills ---
    def register_skill(self, name: str, description: str, metadata: Optional[Dict[str, Any]] = None):
        self.store("skills", name, {"description": description, "metadata": metadata or {}})

    def get_skill(self, name: str) -> Optional[Dict[str, Any]]:
        return self.retrieve("skills", name)

    # --- Long-term Goals & Projects ---
    def record_project(self, project_id: str, details: Dict[str, Any]):
        self.store("projects", project_id, details)

    # --- History & Learning ---
    def add_history_event(self, description: str):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": description
        }
        # Backwards compatible history list handling
        if hasattr(self.provider, "memory") and "history" in self.provider.memory:
            self.provider.memory["history"].append(event)
            if hasattr(self.provider, "_save_memory"):
                self.provider._save_memory()
        else:
            self.store("history", datetime.utcnow().isoformat(), description)
        logger.info(f"Recorded history event: {description}")

    def get_history(self) -> List[Dict[str, Any]]:
        if hasattr(self.provider, "memory"):
            return self.provider.memory.get("history", [])
        return []

    # --- Context ---
    def update_context(self, context_updates: Dict[str, Any]):
        current_context = self.retrieve("context", "global_context", {})
        current_context.update(context_updates)
        self.store("context", "global_context", current_context)
        logger.info("Global cognitive context updated.")

    def get_context(self) -> Dict[str, Any]:
        return self.retrieve("context", "global_context", {})

    # --- Generated Knowledge ---
    def store_knowledge(self, topic: str, content: Any):
        self.store("generated_knowledge", topic, {
            "content": content,
            "synthesized_at": datetime.utcnow().isoformat()
        })

    def retrieve_knowledge(self, topic: str) -> Optional[Dict[str, Any]]:
        return self.retrieve("generated_knowledge", topic)

    # --- Semantic Entity Relationships ---
    def add_relationship(self, source: str, relation: str, target: str, metadata: Optional[Dict[str, Any]] = None):
        self.provider.store_relationship(source, relation, target, metadata)
        logger.info(f"Recorded relationship: {source} --({relation})--> {target}")

    def get_relationships_for_entity(self, entity: str) -> List[Dict[str, Any]]:
        return self.provider.get_relationships(entity)

    # --- Search ---
    def search_memory(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.provider.search(query, category)
