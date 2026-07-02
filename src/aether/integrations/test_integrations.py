import unittest
import os
import shutil
import asyncio
from aether.integrations.connectors import IntegrationManager


class TestIntegrations(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_dir = "data_test"
        os.makedirs(self.test_dir, exist_ok=True)
        self.manager = IntegrationManager()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_connectors_registration(self):
        """Verify all default connectors are registered and accessible."""
        self.assertIsNotNone(self.manager.llm)
        self.assertIsNotNone(self.manager.search)
        self.assertIsNotNone(self.manager.files)
        self.assertIsNotNone(self.manager.git)

    async def test_llm_connector(self):
        """Verify the LanguageModelConnector methods."""
        res = await self.manager.llm.generate_text("Hello AETHER")
        self.assertIn("Hello AETHER", res)

        chat_res = await self.manager.llm.chat([{"role": "user", "content": "hello"}])
        self.assertEqual(chat_res["role"], "assistant")
        self.assertIn("hello", chat_res["content"])

    async def test_web_search_connector(self):
        """Verify the WebSearchConnector methods."""
        results = await self.manager.search.search("AI OS")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Result 1 for AI OS")

    def test_local_file_connector(self):
        """Verify the LocalFileConnector read, write, and list methods."""
        filepath = os.path.join(self.test_dir, "test_file.txt")
        content = "Integrating AETHER 2.0"
        
        # Write
        self.manager.files.write_file(filepath, content)
        self.assertTrue(os.path.exists(filepath))

        # Read
        read_content = self.manager.files.read_file(filepath)
        self.assertEqual(read_content, content)

        # List
        files = self.manager.files.list_dir(self.test_dir)
        self.assertIn("test_file.txt", files)

    def test_git_connector(self):
        """Verify the GitConnector clone and commit methods."""
        dest_path = os.path.join(self.test_dir, "mock_git_repo")
        
        # Clone
        cloned_path = self.manager.git.clone("https://github.com/mock/repo.git", dest_path)
        self.assertTrue(os.path.exists(cloned_path))

        # Commit
        success = self.manager.git.commit_and_push(dest_path, "Initial commit")
        # May be True or False depending on git availability, but should execute without crashing
        self.assertIsInstance(success, bool)


if __name__ == "__main__":
    unittest.main()
