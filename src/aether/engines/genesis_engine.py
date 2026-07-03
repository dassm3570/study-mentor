import logging
import json
import asyncio
from pathlib import Path import os
from typing import Dict, Any, List, Optional
from aether.generators.code_generator import CodeGenerator
from aether.generators.project_builder import ProjectBuilder
from aether.integrations.llm_providers import LLMProvider, get_llm_provider, MockLLMProvider

logger = logging.getLogger("aether.engines.genesis_engine")

class GenesisComponent:
    """Base interface for all Genesis specialist components."""
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        raise NotImplementedError


class RequirementsGenerator(GenesisComponent):
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        prompt = f"Generate a detailed Requirements Specification for a project with the goal: '{goal}'."
        return await llm_provider.generate_text(prompt, "You are an expert product manager. Output in clean Markdown.")


# Keeping other specialists for backward compatibility
class ResearchAnalyst(GenesisComponent):
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        prompt = f"Generate a Market and Technical Research report for: '{goal}'."
        return await llm_provider.generate_text(prompt, "You are an expert technical research analyst.")

class SystemArchitect(GenesisComponent):
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        prompt = f"Design the Software Architecture for: '{goal}'."
        return await llm_provider.generate_text(prompt, "You are a Principal Software Architect.")

class UiUxDesigner(GenesisComponent):
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        prompt = f"Design the UI/UX System for: '{goal}'."
        return await llm_provider.generate_text(prompt, "You are a Lead UI/UX Designer.")

class DatabaseDesigner(GenesisComponent):
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        prompt = f"Create a Database Schema for: '{goal}'."
        return await llm_provider.generate_text(prompt, "You are a Senior Database Administrator.")

class BackendPlanner(GenesisComponent):
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        prompt = f"Formulate a Backend Engineering Plan for: '{goal}'."
        return await llm_provider.generate_text(prompt, "You are a Backend Engineering Lead.")

class FrontendPlanner(GenesisComponent):
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        prompt = f"Formulate a Frontend Engineering Plan for: '{goal}'."
        return await llm_provider.generate_text(prompt, "You are a Frontend Engineering Lead.")

class AiIntegrationSpecialist(GenesisComponent):
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        prompt = f"Design the AI Integration Strategy for: '{goal}'."
        return await llm_provider.generate_text(prompt, "You are an AI Integration Specialist.")

class TestingStrategist(GenesisComponent):
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        prompt = f"Design a Verification and Testing Strategy for: '{goal}'."
        return await llm_provider.generate_text(prompt, "You are a QA and Testing Architect.")

class DocumentationGenerator(GenesisComponent):
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        prompt = f"Create Developer Documentation for: '{goal}'."
        return await llm_provider.generate_text(prompt, "You are a Technical Writer.")

class DeploymentPlanner(GenesisComponent):
    async def generate(self, goal: str, context: Dict[str, Any], llm_provider: LLMProvider) -> str:
        prompt = f"Create a Deployment Plan for: '{goal}'."
        return await llm_provider.generate_text(prompt, "You are a DevOps Engineer.")


class GenesisEngine:
    """
    Coordinates a team of 11 specialist AI software engineering components
    to compile a complete, highly structured project blueprint.
    Uses a modular LLM provider interface.
    """
    def __init__(self, llm_provider: Optional[LLMProvider] = None, output_dir: Optional[Path | str] = None):
        logger.info("GenesisEngine initialized.")
        self.llm_provider = llm_provider or get_llm_provider()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "/tmp/generated_projects"))
        self.code_generator = CodeGenerator()
        self.project_builder = ProjectBuilder(base_path=self.output_dir)
        self.specialists: Dict[str, GenesisComponent] = {
            "requirements": RequirementsGenerator(),
            "research": ResearchAnalyst(),
            "architecture": SystemArchitect(),
            "ui_ux": UiUxDesigner(),
            "database": DatabaseDesigner(),
            "backend": BackendPlanner(),
            "frontend": FrontendPlanner(),
            "ai_integration": AiIntegrationSpecialist(),
            "testing": TestingStrategist(),
            "documentation": DocumentationGenerator(),
            "deployment": DeploymentPlanner()
        }

    def spawn_agent(self, agent_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Spawning agent of type: {agent_type}")
        return {
            "agent_id": f"agent-{agent_type}-001",
            "status": "initialized",
            "capabilities": config.get("capabilities", [])
        } 
    def _generate_fallback_blueprint(self, goal: str, tech_stack: str, db_type: str) -> Dict[str, Any]:
        """Generates a highly detailed structured blueprint programmatically as a fallback."""
        return {
            "Executive Summary": (
                f"This blueprint outlines the development of a state-of-the-art solution for: '{goal}'. "
                f"Designed with modern scalability, security, and modularity in mind, the system leverages "
                f"{tech_stack} and a {db_type} database to deliver a seamless user experience."
            ),
            "System Architecture": (
                f"The application is structured as a decoupled client-server architecture. "
                f"The frontend communicates with the backend via RESTful APIs. It includes an API Gateway, "
                f"an Application Server running on {tech_stack}, and a {db_type} database instance."
            ),
            "Folder Structure": (
                "project-root/\n"
                "├── backend/\n"
                "│   ├── app/\n"
                "│   │   ├── api/\n"
                "│   │   ├── core/\n"
                "│   │   ├── models/\n"
                "│   │   └── main.py\n"
                "│   └── Dockerfile\n"
                "├── frontend/\n"
                "│   ├── src/\n"
                "│   │   ├── components/\n"
                "│   │   └── pages/\n"
                "│   └── package.json\n"
                "└── docker-compose.yml"
            ),
            "Backend Components": (
                f"Built using {tech_stack}. Key modules include: Authentication & Authorization (JWT), "
                f"Core Controller, Database Connector, and external service integrations."
            ),
            "Frontend Components": (
                f"Interactive UI components built to support '{goal}'. Includes: Dashboard, User Settings, "
                f"Goal Management Panel, and real-time visualization widgets."
            ),
            "Database Schema": (
                f"Configured for a {db_type} database. Includes 'users', 'sessions', 'tasks', "
                f"and 'history' tables with foreign key constraints."
            ),
            "API Endpoints": (
                "POST /api/v1/auth/login - User authentication\n"
                "GET /api/v1/tasks - Retrieve active tasks\n"
                "POST /api/v1/tasks - Create a new task\n"
                "GET /api/v1/health - Service health status"
            ),
            "Agent Workflow": (
                "1. User submits stimulus -> 2. Agent classifies intent -> 3. Agent creates plan -> "
                "4. Executed by specialized engines -> 5. Output returned to user."
            ),
            "Shared Memory Design": (
                "Uses Redis for fast short-term memory / session caching, and the primary SQL database "
                "for long-term audit logs and persistent history."
            ),
            "Core Brain Flow": (
                "The Core Brain orchestrates requests through: Intent Classifier -> Plan Generator -> "
                "Step Executor -> Reflection Engine -> Evolution Engine."
            ),
            "Development Phases": (
                "Phase 1: Requirements & Architecture (Week 1)\n"
                "Phase 2: Backend & Database Setup (Weeks 2-3)\n"
                "Phase 3: Frontend Development (Weeks 4-5)\n"
                "Phase 4: Integration & Testing (Week 6)"
            ),
            "Testing Strategy": (
                "Unit tests using standard test frameworks (70% coverage), Integration tests for API endpoints "
                "(20% coverage), and End-to-End user flow tests (10% coverage)."
            ),
            "Deployment Plan": (
                "Containerized using Docker and Docker Compose. Configured for automated CI/CD deployment "
                "to cloud environments (e.g., AWS, GCP) using GitHub Actions."
            ),
            "Future Improvements": (
                "1. Multi-region database replication\n"
                "2. Real-time WebSocket notifications\n"
                "3. Advanced analytics dashboard\n"
                "4. Automatic system-wide self-healing and scaling."
            )
        }

    def _generate_project_files(self, goal: str, blueprint: Dict[str, Any]) -> None:
        """Materialize a starter project from the generated blueprint."""
        try:
            files = self.code_generator.generate(blueprint)
            build_result = self.project_builder.build_project(goal, files)
            logger.info(
                "Generated starter project for '%s' at %s",
                goal,
                build_result["output_directory"],
            )
        except Exception as exc:
            logger.error("Failed to build starter project files: %s", exc, exc_info=True)

    async def generate_blueprint(self, goal: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generates a complete, structured software blueprint.
        Queries the LLM provider for a valid JSON response or falls back to a programmatically
        customized blueprint if the LLM is not available.
        """
        logger.info(f"Generating blueprint for goal: '{goal}'")
        options = options or {}
        tech_stack = options.get("tech_stack", "FastAPI, React, TailwindCSS")
        db_type = options.get("db_type", "PostgreSQL")

        if isinstance(self.llm_provider, MockLLMProvider):
            logger.info("LLM provider is Mock. Using programmatic blueprint generator.")
            blueprint = self._generate_fallback_blueprint(goal, tech_stack, db_type)
            logger.info(f"Returning mock/programmatic blueprint. Keys: {list(blueprint.keys())}")
            self._generate_project_files(goal, blueprint)
            return {
                "goal": goal,
                "blueprint": blueprint
            }

        # Query the LLM
        prompt = f"""
Generate a detailed, structured software blueprint for a project.
Project Goal: {goal}
Target Tech Stack: {tech_stack}
Database Type: {db_type}

The output MUST be a valid JSON object with the following keys. Do not include any markdown formatting (like ```json or ```) in the response, just the raw JSON:
{{
  "Executive Summary": "...",
  "System Architecture": "...",
  "Folder Structure": "...",
  "Backend Components": "...",
  "Frontend Components": "...",
  "Database Schema": "...",
  "API Endpoints": "...",
  "Agent Workflow": "...",
  "Shared Memory Design": "...",
  "Core Brain Flow": "...",
  "Development Phases": "...",
  "Testing Strategy": "...",
  "Deployment Plan": "...",
  "Future Improvements": "..."
}}
"""
        system_instruction = "You are a Principal Software Architect and DevOps expert. You only output valid JSON matching the requested schema."
        
        try:
            response_text = await self.llm_provider.generate_text(prompt, system_instruction)
            
            # Clean up potential markdown wrapper
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()

            blueprint = json.loads(cleaned_text)
            logger.info(f"Successfully generated and parsed blueprint from LLM. Keys: {list(blueprint.keys())}")
            self._generate_project_files(goal, blueprint)
            return {
                "goal": goal,
                "blueprint": blueprint
            }
        except Exception as e:
            logger.error(f"Failed to generate or parse blueprint from LLM: {e}. Falling back.", exc_info=True)
            blueprint = self._generate_fallback_blueprint(goal, tech_stack, db_type)
            logger.info(f"Returning fallback blueprint. Keys: {list(blueprint.keys())}")
            self._generate_project_files(goal, blueprint)
            return {
                "goal": goal,
                "blueprint": blueprint
            }
