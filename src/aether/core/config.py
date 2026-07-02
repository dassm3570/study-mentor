import os
import yaml
import logging
from typing import Dict, Any, List, Optional
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("aether.core.config")


class AetherSettings(BaseSettings):
    """
    AETHER 2.0 Global Configuration & Settings.
    Loads values from:
      1. Environment variables (prefixed with AETHER_)
      2. A local .env file
      3. Fallbacks to config/settings.yaml or default values
    """
    # Environment & Debugging
    environment: str = Field(default="development", validation_alias="AETHER_ENV")
    debug: bool = Field(default=False, validation_alias="AETHER_DEBUG")
    log_level: str = Field(default="INFO", validation_alias="AETHER_LOG_LEVEL")

    # API Keys & Secrets (Protected using SecretStr)
    gemini_api_key: Optional[SecretStr] = Field(default=None, validation_alias="GEMINI_API_KEY")
    openai_api_key: Optional[SecretStr] = Field(default=None, validation_alias="OPENAI_API_KEY")
    database_url: SecretStr = Field(
        default=SecretStr("sqlite+aiosqlite:///./aether.db"),
        validation_alias="DATABASE_URL"
    )

    # Feature Flags
    enable_evolution: bool = Field(default=True, validation_alias="AETHER_ENABLE_EVOLUTION")
    enable_innovation_recovery: bool = Field(default=True, validation_alias="AETHER_ENABLE_INNOVATION_RECOVERY")
    enable_self_reflection: bool = Field(default=True, validation_alias="AETHER_ENABLE_SELF_REFLECTION")

    # Engine Configurations
    workspace_base_path: str = Field(default="workspaces", validation_alias="AETHER_WORKSPACE_PATH")
    max_subtasks_per_goal: int = Field(default=10, validation_alias="AETHER_MAX_SUBTASKS")
    shared_memory_ttl: int = Field(default=3600, validation_alias="AETHER_MEMORY_TTL")

    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @classmethod
    def load_settings(cls) -> "AetherSettings":
        """
        Loads settings starting with defaults from config/settings.yaml,
        overridden by .env and environment variables.
        """
        yaml_data = {}
        yaml_path = os.path.join("config", "settings.yaml")
        
        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, "r") as f:
                    yaml_content = yaml.safe_load(f)
                    if yaml_content:
                        # Flatten YAML structure for Pydantic input
                        yaml_data = cls._flatten_yaml(yaml_content)
            except Exception as e:
                logger.warning(f"Failed to load settings.yaml: {e}")

        # Instantiate settings, passing YAML data as initial defaults
        # Environment variables and .env will override these.
        return cls(**yaml_data)

    @staticmethod
    def _flatten_yaml(content: Dict[str, Any]) -> Dict[str, Any]:
        """Flattens nested YAML configuration structures."""
        flat = {}
        # Parse system section
        system = content.get("system", {})
        if "environment" in system:
            flat["environment"] = system["environment"]
        if "log_level" in system:
            flat["log_level"] = system["log_level"]

        # Parse database section
        database = content.get("database", {})
        if "url" in database:
            flat["database_url"] = database["url"]

        # Parse engines section
        engines = content.get("engines", {})
        goal_mgr = engines.get("goal_manager", {})
        if "max_subtasks" in goal_mgr:
            flat["max_subtasks_per_goal"] = goal_mgr["max_subtasks"]

        memory = engines.get("shared_memory", {})
        if "ttl_seconds" in memory:
            flat["shared_memory_ttl"] = memory["ttl_seconds"]

        workspace = engines.get("workspace_manager", {})
        if "base_path" in workspace:
            flat["workspace_base_path"] = workspace["base_path"]

        return flat


# Global Settings Instance
settings = AetherSettings.load_settings()


def configure_logging():
    """Configures application-wide logging based on settings."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
