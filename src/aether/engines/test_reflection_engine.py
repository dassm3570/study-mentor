import unittest
from aether.engines.reflection_engine import ReflectionEngine


class TestReflectionEngine(unittest.TestCase):
    def setUp(self):
        self.reflection_engine = ReflectionEngine()

    def test_analyze_optimal_performance(self):
        """Verify reflection results when all steps succeed and align with the mission."""
        active_mission = {
            "title": "Setup database",
            "milestones": [
                {"id": 1, "title": "Install PostgreSQL", "status": "completed"}
            ]
        }
        execution_history = [
            {"step_id": "step_1", "engine": "database_designer", "action": "setup_db", "status": "completed", "has_error": False}
        ]

        report = self.reflection_engine.analyze_performance(execution_history, active_mission)
        
        self.assertEqual(report["rating"], "optimal")
        self.assertEqual(report["alignment"]["score"], 100)
        self.assertEqual(len(report["missing_deliverables"]), 0)
        self.assertEqual(len(report["risks"]), 0)
        self.assertEqual(len(report["recommendations"]), 0)

    def test_analyze_suboptimal_performance_with_failures(self):
        """Verify reflection results when there are failed steps and uncompleted milestones."""
        active_mission = {
            "title": "Deploy website",
            "priority": 3,
            "milestones": [
                {"id": 1, "title": "Run tests", "status": "completed"},
                {"id": 2, "title": "Build Docker image", "status": "pending"}
            ]
        }
        execution_history = [
            {"step_id": "step_1", "engine": "testing_strategist", "action": "run_tests", "status": "completed", "has_error": False},
            {"step_id": "step_2", "engine": "deployment_planner", "action": "build_docker", "status": "failed", "has_error": True}
        ]

        report = self.reflection_engine.analyze_performance(execution_history, active_mission)

        self.assertEqual(report["rating"], "suboptimal")
        self.assertEqual(report["quality_assessment"]["failed_steps"], 1)
        self.assertEqual(report["quality_assessment"]["error_rate"], "50.0%")
        
        # Verify missing deliverables
        self.assertEqual(len(report["missing_deliverables"]), 1)
        self.assertIn("Milestone 2: Build Docker image", report["missing_deliverables"])

        # Verify risks and recommendations are generated
        self.assertTrue(len(report["risks"]) > 0)
        self.assertTrue(len(report["recommendations"]) > 0)
        self.assertIn("Invoke the Innovation Engine to seek alternative strategies for failed steps.", report["recommendations"])


if __name__ == "__main__":
    unittest.main()
