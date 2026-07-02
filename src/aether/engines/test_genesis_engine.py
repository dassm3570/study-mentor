import unittest
import asyncio
import tempfile
from pathlib import Path
from aether.engines.genesis_engine import GenesisEngine
from aether.generators.fastapi_generator import FastAPIGenerator
from aether.generators.react_generator import ReactGenerator


class TestGenesisEngine(unittest.TestCase):
    def setUp(self):
        self.genesis_engine = GenesisEngine()

    def test_specialists_registration(self):
        """Verify all 11 AI software engineering specialists are registered for backward compatibility."""
        expected_specialists = [
            "requirements", "research", "architecture", "ui_ux", 
            "database", "backend", "frontend", "ai_integration", 
            "testing", "documentation", "deployment"
        ]
        for specialist in expected_specialists:
            self.assertIn(specialist, self.genesis_engine.specialists)

    def test_generate_full_blueprint(self):
        """Verify that the engine generates a complete 14-section blueprint."""
        goal = "Build a secure decentralized chatting platform"
        result = asyncio.run(self.genesis_engine.generate_blueprint(goal))

        self.assertEqual(result["goal"], goal)
        blueprint = result["blueprint"]
        
        # Ensure all 14 sections are present
        self.assertEqual(len(blueprint), 14)
        self.assertIn("Executive Summary", blueprint)
        self.assertIn("System Architecture", blueprint)
        self.assertIn("Folder Structure", blueprint)
        self.assertIn("Backend Components", blueprint)
        self.assertIn("Frontend Components", blueprint)
        self.assertIn("Database Schema", blueprint)
        self.assertIn("API Endpoints", blueprint)
        self.assertIn("Agent Workflow", blueprint)
        self.assertIn("Shared Memory Design", blueprint)
        self.assertIn("Core Brain Flow", blueprint)
        self.assertIn("Development Phases", blueprint)
        self.assertIn("Testing Strategy", blueprint)
        self.assertIn("Deployment Plan", blueprint)
        self.assertIn("Future Improvements", blueprint)

        # Check a sample content
        self.assertIn("decentralized chatting platform", blueprint["Executive Summary"])

    def test_generate_blueprint_builds_placeholder_project_files(self):
        """Blueprint generation should also materialize a simple starter project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = GenesisEngine(output_dir=temp_dir)
            result = asyncio.run(engine.generate_blueprint("Build a task manager"))

            self.assertEqual(result["goal"], "Build a task manager")
            root = Path(temp_dir)
            generated_files = {
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
                if path.is_file()
            }

            self.assertTrue(any(path.endswith("README.md") for path in generated_files))
            self.assertTrue(any(path.endswith("backend/main.py") for path in generated_files))
            self.assertTrue(any(path.endswith("frontend/index.html") for path in generated_files))

    def test_specialized_generators_return_file_lists(self):
        """The specialized generators should return placeholder file descriptors without writing files."""
        blueprint = {
            "Executive Summary": "A task planner",
            "System Architecture": "A modular service",
        }

        fastapi_files = FastAPIGenerator().generate(blueprint)
        react_files = ReactGenerator().generate(blueprint)

        self.assertEqual(fastapi_files[0]["path"], "backend/main.py")
        self.assertIn("FastAPI", fastapi_files[0]["content"])
        self.assertEqual(react_files[0]["path"], "frontend/index.html")
        self.assertIn("AETHER Project", react_files[0]["content"])


if __name__ == "__main__":
    unittest.main()
