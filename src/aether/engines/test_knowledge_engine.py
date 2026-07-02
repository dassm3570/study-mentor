import unittest
import os
import shutil
from aether.engines.knowledge_engine import KnowledgeEngine


class TestKnowledgeEngine(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_dir = "data_test"
        os.makedirs(self.test_dir, exist_ok=True)
        self.knowledge_engine = KnowledgeEngine()
        from aether.engines.shared_memory import JSONMemoryStorageProvider, SharedMemory
        provider = JSONMemoryStorageProvider(storage_path=os.path.join(self.test_dir, "shared_memory_test.json"))
        self.knowledge_engine.shared_memory = SharedMemory(provider=provider)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    async def test_generate_personalized_roadmap_beginner(self):
        """Verify that a beginner visual roadmap generates correctly."""
        self.knowledge_engine.shared_memory.store_preference("difficulty_level", "Beginner")
        self.knowledge_engine.shared_memory.store_preference("learning_style", "visual")

        roadmap = await self.knowledge_engine.generate_roadmap("Python")
        self.assertEqual(roadmap["difficulty"], "Beginner")
        self.assertEqual(roadmap["learning_style"], "visual")
        self.assertEqual(len(roadmap["phases"]), 2)
        self.assertIn("Visual diagrams", roadmap["phases"][0]["resources"][0])

    async def test_generate_personalized_roadmap_advanced(self):
        """Verify that an advanced roadmap generates with extra phases and resources."""
        self.knowledge_engine.shared_memory.store_preference("difficulty_level", "Advanced")
        self.knowledge_engine.shared_memory.store_preference("learning_style", "auditory")

        roadmap = await self.knowledge_engine.generate_roadmap("Python")
        self.assertEqual(roadmap["difficulty"], "Advanced")
        self.assertEqual(len(roadmap["phases"]), 3)

    async def test_quiz_and_concept_map(self):
        """Verify quiz and concept map generation."""
        quiz = await self.knowledge_engine.generate_quiz("AetherOS")
        self.assertEqual(len(quiz), 2)
        self.assertEqual(quiz[0]["correct_option"], "Modularity & Decoupling")

        cmap = await self.knowledge_engine.generate_concept_map("Python")
        self.assertEqual(cmap["topic"], "Python")
        self.assertEqual(len(cmap["nodes"]), 3)

    async def test_prerequisite_analysis(self):
        """Verify prerequisite analysis checks registered skills."""
        # Setup skills
        self.knowledge_engine.shared_memory.register_skill("basic_programming", "Python coding")
        
        # Analyze a topic that requires basic_programming and machine_learning
        analysis = await self.knowledge_engine.analyze_prerequisites("AI Brain")
        self.assertFalse(analysis["all_prerequisites_met"])
        
        prereqs = {p["prerequisite"]: p["status"] for p in analysis["prerequisites_status"]}
        self.assertEqual(prereqs["basic_programming"], "met")
        self.assertEqual(prereqs["machine_learning"], "missing")

    def test_track_learning_progress(self):
        """Verify tracking learning progress updates history in Shared Memory."""
        self.knowledge_engine.track_learning_progress("FastAPI", ["routing", "dependencies"])
        
        history = self.knowledge_engine.shared_memory.retrieve("learning_history", "FastAPI")
        self.assertIn("routing", history)
        self.assertIn("dependencies", history)


if __name__ == "__main__":
    unittest.main()
