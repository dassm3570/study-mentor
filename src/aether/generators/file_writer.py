import logging
from pathlib import Path os

logger = logging.getLogger("aether.generators.file_writer")


class FileWriter:
    def __init__(self, base_path="generated_projects"):

self.base_path = Path(os.getenv("OUTPUT_DIR", "/tmp/generated_projects"))
self.base_path.mkdir(parents=True, exist_ok=True)
    def write_files(self, project_name, files):
        project_dir = self.base_path / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            file_path = project_dir / file["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file["content"])

            logger.info("Generated file: %s", file_path)

        return project_dir
