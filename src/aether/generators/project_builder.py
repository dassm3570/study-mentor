import logging
import re
from .file_writer import FileWriter

logger = logging.getLogger("aether.generators.project_builder")


class ProjectBuilder:
    """
    Builds a software project from AI generated files.
    """

    def __init__(self, base_path=""):
        self.writer = FileWriter(base_path=base_path)

    @staticmethod
    def _normalize_project_name(project_name: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", project_name).strip("-").lower()
        return normalized or "generated-project"

    def build_project(self, project_name: str, files: list):
        """
        Creates a complete project directory.
        """
        normalized_name = self._normalize_project_name(project_name)
        output_directory = self.writer.write_files(normalized_name, files)

        logger.info("Project build completed for %s at %s", normalized_name, output_directory)
        return {
            "success": True,
            "project_name": normalized_name,
            "output_directory": str(output_directory),
            "files_created": len(files)
        }