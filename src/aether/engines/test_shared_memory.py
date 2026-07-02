import unittest
import os
import shutil
from aether.engines.shared_memory import SharedMemory, JSONMemoryStorageProvider


class TestSharedMemory(unittest.TestCase):
    def setUp(self):
        self.test_dir = "data_test"
        self.storage_path = os.path.join(self.test_dir, "shared_memory_test.json")
        self.provider = JSONMemoryStorageProvider(storage_path=self.storage_path)
        self.shared_memory = SharedMemory(provider=self.provider)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_preferences_storage(self):
        """Verify storing and retrieving preferences."""
        self.shared_memory.store_preference("theme", "dark")
        self.assertEqual(self.shared_memory.get_preference("theme"), "dark")

    def test_skills_registration(self):
        """Verify registering and retrieving skills."""
        self.shared_memory.register_skill(
            name="file_parsing",
            description="Extracts data from text files",
            metadata={"version": "1.0"}
        )
        skill = self.shared_memory.get_skill("file_parsing")
        self.assertIsNotNone(skill)
        self.assertEqual(skill["description"], "Extracts data from text files")
        self.assertEqual(skill["metadata"]["version"], "1.0")

    def test_knowledge_and_context(self):
        """Verify generated knowledge storage and global context updates."""
        # Test Knowledge
        self.shared_memory.store_knowledge("database_choices", "sqlite vs postgres")
        knowledge = self.shared_memory.retrieve_knowledge("database_choices")
        self.assertEqual(knowledge["content"], "sqlite vs postgres")

        # Test Context
        self.shared_memory.update_context({"current_action": "running_tests"})
        context = self.shared_memory.get_context()
        self.assertEqual(context["current_action"], "running_tests")

    def test_entity_relationships(self):
        """Verify adding and querying semantic relationships between entities."""
        self.shared_memory.add_relationship(
            source="UserMission",
            relation="requires",
            target="DatabaseSetup",
            metadata={"priority": "high"}
        )
        self.shared_memory.add_relationship(
            source="DatabaseSetup",
            relation="uses",
            target="PostgreSQL"
        )

        # Retrieve relationships for "DatabaseSetup"
        rels = self.shared_memory.get_relationships_for_entity("DatabaseSetup")
        self.assertEqual(len(rels), 2)
        
        # Check source/target matching
        targets = [r["target"] for r in rels]
        sources = [r["source"] for r in rels]
        self.assertIn("PostgreSQL", targets)
        self.assertIn("UserMission", sources)

    def test_search_memory(self):
        """Verify keyword search across memory categories."""
        self.shared_memory.store_preference("editor", "VS Code")
        self.shared_memory.store_knowledge("editor_shortcuts", "VS Code shortcuts list")
        
        results = self.shared_memory.search_memory("VS Code")
        self.assertTrue(len(results) >= 2)


if __name__ == "__main__":
    unittest.main()
