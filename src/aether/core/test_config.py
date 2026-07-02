import unittest
import os
from pydantic import SecretStr
from aether.core.config import AetherSettings


class TestConfig(unittest.TestCase):
    def setUp(self):
        # Backup existing environment variables to avoid polluting
        self.old_env = dict(os.environ)

    def tearDown(self):
        # Restore environment variables
        os.environ.clear()
        os.environ.update(self.old_env)

    def test_default_settings_loading(self):
        """Verify that settings load defaults or values from settings.yaml correctly."""
        settings = AetherSettings.load_settings()
        
        # Verify database url (should load from settings.yaml if present, or default)
        self.assertIsInstance(settings.database_url, SecretStr)
        
        # Verify feature flags default
        self.assertTrue(settings.enable_evolution)

    def test_environment_variable_override(self):
        """Verify that environment variables override configuration files."""
        os.environ["GEMINI_API_KEY"] = "super-secret-gemini-key"
        os.environ["AETHER_ENV"] = "production"
        os.environ["AETHER_ENABLE_EVOLUTION"] = "false"

        settings = AetherSettings.load_settings()

        # Check environment override
        self.assertEqual(settings.environment, "production")
        self.assertFalse(settings.enable_evolution)

        # Check secret handling
        self.assertIsInstance(settings.gemini_api_key, SecretStr)
        self.assertEqual(settings.gemini_api_key.get_secret_value(), "super-secret-gemini-key")
        
        # Verify SecretStr does not expose plaintext in str representation
        self.assertNotIn("super-secret-gemini-key", str(settings.gemini_api_key))

    def test_dot_env_loading(self):
        """Verify that settings can load from a temporary .env file."""
        env_path = ".env"
        
        # Write temporary .env
        with open(env_path, "w") as f:
            f.write("OPENAI_API_KEY=openai-secret-key\n")
            f.write("AETHER_LOG_LEVEL=DEBUG\n")

        try:
            settings = AetherSettings.load_settings()
            self.assertEqual(settings.log_level, "DEBUG")
            self.assertEqual(settings.openai_api_key.get_secret_value(), "openai-secret-key")
        finally:
            # Clean up .env
            if os.path.exists(env_path):
                os.remove(env_path)


if __name__ == "__main__":
    unittest.main()
