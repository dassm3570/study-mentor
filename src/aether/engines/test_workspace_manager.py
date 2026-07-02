import unittest
import os
import shutil
import json
from aether.engines.workspace_manager import WorkspaceManager


class TestWorkspaceManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = "data_test"
        os.makedirs(self.test_dir, exist_ok=True)
        self.workspaces_dir = os.path.join(self.test_dir, "workspaces")
        # Initialize WorkspaceManager with a test path
        self.workspace_manager = WorkspaceManager(base_path=self.workspaces_dir)
        
        # Properly override the global memory with a test provider
        from aether.engines.shared_memory import JSONMemoryStorageProvider, SharedMemory
        provider = JSONMemoryStorageProvider(storage_path=os.path.join(self.test_dir, "shared_memory_test.json"))
        self.workspace_manager.global_memory = SharedMemory(provider=provider)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_workspace(self):
        """Verify that a workspace has the complete directory structure and links to global memory."""
        mission_id = 42
        res = self.workspace_manager.create_workspace(mission_id)
        
        # Verify directories exist
        ws_dir = res["workspace_directory"]
        expected_dirs = [
            "conversations", "generated_files", "documents", 
            "tasks", "notes", "architecture", "source_code_references", 
            "timelines", "memory"
        ]
        for d in expected_dirs:
            self.assertTrue(os.path.exists(os.path.join(ws_dir, d)))

        # Verify progress file
        self.assertTrue(os.path.exists(os.path.join(ws_dir, "progress.json")))

        # Verify project memory file
        self.assertTrue(os.path.exists(os.path.join(ws_dir, "memory", "project_memory.json")))

        # Verify linking in global Shared Memory
        workspace_links = self.workspace_manager.global_memory.retrieve("project_workspaces", "mission_42")
        self.assertIsNotNone(workspace_links)
        self.assertEqual(workspace_links["workspace_directory"], ws_dir)

    def test_add_resources(self):
        """Verify that various resource types can be added to the workspace."""
        mission_id = 7
        self.workspace_manager.create_workspace(mission_id)

        # 1. Add conversation
        conv_path = self.workspace_manager.add_conversation(
            mission_id, 
            "conv_abc", 
            [{"sender": "user", "text": "hello"}]
        )
        self.assertTrue(os.path.exists(conv_path))
        with open(conv_path, "r") as f:
            data = json.load(f)
            self.assertEqual(data["conversation_id"], "conv_abc")

        # 2. Add task
        task_path = self.workspace_manager.add_task(
            mission_id, 
            "task_1", 
            {"title": "Task 1", "status": "todo"}
        )
        self.assertTrue(os.path.exists(task_path))

        # 3. Add architecture
        arch_path = self.workspace_manager.add_architecture(
            mission_id, 
            "arch_design", 
            "# Design Document"
        )
        self.assertTrue(os.path.exists(arch_path))

    def test_project_memory_sync(self):
        """Verify project memory updates write locally and sync indices to global Shared Memory."""
        mission_id = 9
        self.workspace_manager.create_workspace(mission_id)

        updates = {
            "context": {"current_focus": "testing"},
            "key_values": {"api_key_set": True}
        }
        self.workspace_manager.update_project_memory(mission_id, updates)

        # Check local memory file
        local_mem = self.workspace_manager.get_project_memory(mission_id)
        self.assertEqual(local_mem["context"]["current_focus"], "testing")
        self.assertEqual(local_mem["key_values"]["api_key_set"], True)

        # Check global memory index
        global_indices = self.workspace_manager.global_memory.retrieve("project_memory_indices", "mission_9")
        self.assertIsNotNone(global_indices)
        self.assertIn("current_focus", global_indices["context_keys"])
        self.assertIn("api_key_set", global_indices["value_keys"])


if __name__ == "__main__":
    unittest.main()
