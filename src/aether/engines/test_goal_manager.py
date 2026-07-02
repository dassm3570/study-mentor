import unittest
import os
import shutil
from aether.engines.goal_manager import GoalManager


class TestGoalManager(unittest.TestCase):
    def setUp(self):
        # Use a temporary storage path for testing
        self.test_dir = "data_test"
        self.storage_path = os.path.join(self.test_dir, "missions_test.json")
        self.goal_manager = GoalManager(storage_path=self.storage_path)
        
        # Override workspace manager base path to avoid polluting real workspaces
        self.goal_manager.workspace_manager.base_path = os.path.join(self.test_dir, "workspaces")

    def tearDown(self):
        # Clean up temporary test directories
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_mission(self):
        """Test creating a mission with milestones and verifying its initial state."""
        milestones = [
            {"title": "Setup repository", "description": "Initialize git"},
            {"title": "Write code", "description": "Implement feature"}
        ]
        mission = self.goal_manager.create_mission(
            title="Test Project",
            description="A test project mission",
            priority=2,
            milestones=milestones
        )

        self.assertEqual(mission["id"], 1)
        self.assertEqual(mission["title"], "Test Project")
        self.assertEqual(mission["priority"], 2)
        self.assertEqual(mission["status"], "pending")
        self.assertEqual(mission["progress_percentage"], 0)
        self.assertEqual(len(mission["milestones"]), 2)
        self.assertEqual(mission["milestones"][0]["title"], "Setup repository")
        self.assertEqual(mission["milestones"][0]["status"], "pending")

    def test_activate_mission_with_no_dependencies(self):
        """Test activating a mission that has no dependencies."""
        mission = self.goal_manager.create_mission("Mission 1", "No deps")
        self.assertEqual(mission["status"], "pending")
        
        updated = self.goal_manager.activate_mission(mission["id"])
        self.assertEqual(updated["status"], "active")

    def test_activate_mission_with_dependencies(self):
        """Test dependency validation: cannot activate if dependencies are not completed."""
        dep_mission = self.goal_manager.create_mission("Dependency Mission", "Must complete first")
        main_mission = self.goal_manager.create_mission(
            "Main Mission", 
            "Depends on the first one",
            dependencies=[dep_mission["id"]]
        )

        # Attempt to activate main_mission should fail because dependency is 'pending'
        with self.assertRaises(ValueError) as context:
            self.goal_manager.activate_mission(main_mission["id"])
        self.assertIn("is not completed", str(context.exception))

        # Complete the dependency mission
        self.goal_manager.complete_mission(dep_mission["id"])
        
        # Now activation should succeed
        updated = self.goal_manager.activate_mission(main_mission["id"])
        self.assertEqual(updated["status"], "active")

    def test_circular_dependency_detection(self):
        """Test that setting circular dependencies throws a ValueError."""
        m1 = self.goal_manager.create_mission("M1", "Mission 1")
        m2 = self.goal_manager.create_mission("M2", "Mission 2", dependencies=[m1["id"]])
        
        # Adding a dependency from m1 to m2 would create a cycle: m1 -> m2 -> m1
        with self.assertRaises(ValueError) as context:
            self.goal_manager.set_dependencies(m1["id"], [m2["id"]])
        self.assertIn("circular dependency loop", str(context.exception))

    def test_milestone_progress_tracking(self):
        """Test that completing milestones recalculates the progress percentage."""
        milestones = [
            {"title": "M1"},
            {"title": "M2"},
            {"title": "M3"},
            {"title": "M4"}
        ]
        mission = self.goal_manager.create_mission("Progress Mission", "Test progress", milestones=milestones)
        self.assertEqual(mission["progress_percentage"], 0)

        # Complete 1 milestone (25%)
        self.goal_manager.update_milestone(mission["id"], milestone_id=1, status="completed")
        updated = self.goal_manager.get_mission(mission["id"])
        self.assertEqual(updated["progress_percentage"], 25)

        # Complete another milestone (50%)
        self.goal_manager.update_milestone(mission["id"], milestone_id=2, status="completed")
        updated = self.goal_manager.get_mission(mission["id"])
        self.assertEqual(updated["progress_percentage"], 50)

    def test_lifecycle_transitions(self):
        """Test complete lifecycle: pending -> active -> paused -> active -> completed -> archived."""
        mission = self.goal_manager.create_mission("Lifecycle", "Test")
        self.assertEqual(mission["status"], "pending")

        # Activate
        mission = self.goal_manager.activate_mission(mission["id"])
        self.assertEqual(mission["status"], "active")

        # Pause
        mission = self.goal_manager.pause_mission(mission["id"])
        self.assertEqual(mission["status"], "paused")

        # Reactivate
        mission = self.goal_manager.activate_mission(mission["id"])
        self.assertEqual(mission["status"], "active")

        # Complete
        mission = self.goal_manager.complete_mission(mission["id"])
        self.assertEqual(mission["status"], "completed")
        self.assertEqual(mission["progress_percentage"], 100)

        # Archive
        mission = self.goal_manager.archive_mission(mission["id"])
        self.assertEqual(mission["status"], "archived")


if __name__ == "__main__":
    unittest.main()
