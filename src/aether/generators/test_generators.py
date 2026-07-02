import unittest
from typing import Dict, Any
from aether.generators.react_generator import ReactGenerator
from aether.generators.fastapi_generator import FastAPIGenerator
from aether.generators.code_generator import CodeGenerator


class TestGenerators(unittest.TestCase):
    def setUp(self) -> None:
        self.blueprint: Dict[str, Any] = {
            "Executive Summary": "AETHER E-Commerce Platform\nAn automated storefront generator.",
            "System Architecture": "Frontend React SPA calling a FastAPI backend.",
            "Folder Structure": "Root\n-- frontend/\n-- backend/",
        }

    def test_react_generator(self) -> None:
        generator = ReactGenerator()
        files = generator.generate(self.blueprint)

        # React requirements:
        # package.json, vite.config.js, src/main.jsx, src/App.jsx, src/index.css, index.html
        expected_paths = {
            "package.json",
            "vite.config.js",
            "index.html",
            "src/main.jsx",
            "src/index.css",
            "src/App.jsx",
        }

        paths = {f["path"] for f in files}
        self.assertEqual(paths, expected_paths)

        # Verify that blueprint data is serialized inside App.jsx
        app_file = next(f for f in files if f["path"] == "src/App.jsx")
        self.assertIn("AETHER E-Commerce Platform", app_file["content"])

    def test_fastapi_generator(self) -> None:
        generator = FastAPIGenerator()
        files = generator.generate(self.blueprint)

        # FastAPI requirements:
        # backend/main.py, backend/api/routes.py, backend/models.py, backend/config.py, backend/requirements.txt
        expected_paths = {
            "backend/main.py",
            "backend/api/routes.py",
            "backend/models.py",
            "backend/config.py",
            "backend/requirements.txt",
        }

        paths = {f["path"] for f in files}
        self.assertEqual(paths, expected_paths)

        # Verify that project title is embedded in config
        config_file = next(f for f in files if f["path"] == "backend/config.py")
        self.assertIn("AETHER E-Commerce Platform", config_file["content"])

    def test_code_generator_integration(self) -> None:
        generator = CodeGenerator()
        files = generator.generate(self.blueprint)

        # 1 README.md + 5 backend files + 6 frontend files = 12 files
        self.assertEqual(len(files), 12)

        paths = {f["path"] for f in files}
        self.assertIn("README.md", paths)
        
        # Verify backend files exist
        self.assertIn("backend/main.py", paths)
        self.assertIn("backend/api/routes.py", paths)

        # Verify frontend files exist (prefixed with frontend/)
        self.assertIn("frontend/package.json", paths)
        self.assertIn("frontend/vite.config.js", paths)
        self.assertIn("frontend/src/App.jsx", paths)


if __name__ == "__main__":
    unittest.main()
