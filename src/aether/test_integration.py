import unittest
import os
import shutil
from aether.core.brain import CoreBrain


class TestEndToEndWorkflow(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_dir = "data_test"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Instantiate CoreBrain
        self.brain = CoreBrain()
        
        # Override storage paths of all engines to use the test directory to avoid side effects
        self.brain.shared_memory.provider.storage_path = os.path.join(self.test_dir, "shared_memory.json")
        self.brain.shared_memory.provider.memory = self.brain.shared_memory.provider._default_memory()
        
        self.brain.goal_manager.storage_path = os.path.join(self.test_dir, "missions.json")
        self.brain.goal_manager.missions = []
        
        self.brain.workspace_manager.base_path = os.path.join(self.test_dir, "workspaces")
        self.brain.goal_manager.workspace_manager = self.brain.workspace_manager

    def tearDown(self):
        # Clean up all generated files
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    async def test_complete_project_generation_workflow(self):
        """
        Integration Test: Verify the complete workflow from a natural language goal
        to the creation of a structured mission, workspace, and blueprint files.
        """
        # 1. User submits a request to generate a project
        stimulus = {
            "value": "Create a new Python Web API project with a Relational SQLite database"
        }

        # 2. Process thought through the central Core Brain
        response = await self.brain.process_thought(stimulus)

        # 3. Verify cognitive loop output structure
        self.assertEqual(response["status"], "completed")
        self.assertIn("agent_genesis", response["intents"])
        self.assertIn("goal_management", response["intents"])
        
        engine_responses = response["engine_responses"]
        self.assertIn("genesis_engine", engine_responses)
        self.assertIn("workspace_manager", engine_responses)
        self.assertIn("goal_manager", engine_responses)
        self.assertIn("reflection_engine", engine_responses)

        # 4. Verify that the Goal Manager successfully created a mission
        missions = self.brain.goal_manager.list_missions()
        self.assertEqual(len(missions), 1)
        mission = missions[0]
        self.assertEqual(mission["title"], "Automated Goal")
        self.assertEqual(mission["status"], "pending")

        # 5. Verify that the Genesis Engine generated the blueprint
        blueprint_data = engine_responses["genesis_engine"]["result"]
        self.assertEqual(blueprint_data["goal"], stimulus["value"])
        self.assertIn("System Architecture", blueprint_data["blueprint"])
        self.assertIn("Database Schema", blueprint_data["blueprint"])

        # 6. Verify that the Workspace Manager created the isolated workspace
        workspace_dir = mission["workspace_path"]
        self.assertTrue(os.path.exists(workspace_dir))
        
        # Check that the directory structure is fully created
        expected_subdirs = ["notes", "tasks", "documents", "architecture", "memory"]
        for subdir in expected_subdirs:
            self.assertTrue(os.path.exists(os.path.join(workspace_dir, subdir)))

        # 7. Verify that Shared Memory has recorded the workflow event
        history = self.brain.shared_memory.get_history()
        self.assertTrue(len(history) > 0)
        self.assertIn("Processed thought", history[-1]["event"])


if __name__ == "__main__":
    unittest.main()
