# AETHER 2.0

**AETHER 2.0** is an Advanced Agentic AI Operating System built with Python and FastAPI. It integrates multiple specialized cognitive engines working in harmony to handle tasks, manage environments, think, reflect, and evolve.

## Directory Structure
- **Core Brain**: `src/aether/core/`
- **Goal Manager**: `src/aether/engines/goal_manager.py`
- **Workspace Manager**: `src/aether/engines/workspace_manager.py`
- **Shared Memory**: `src/aether/engines/shared_memory.py`
- **Knowledge Engine**: `src/aether/engines/knowledge_engine.py`
- **Innovation Engine**: `src/aether/engines/innovation_engine.py`
- **Genesis Engine**: `src/aether/engines/genesis_engine.py`
- **Reflection Engine**: `src/aether/engines/reflection_engine.py`
- **Evolution Engine**: `src/aether/engines/evolution_engine.py`
- **API**: `src/aether/api/`
- **Database**: `src/aether/database/`
- **Config**: `config/`
- **Prompts**: `prompts/`
- **Frontend**: `frontend/`
- **Documentation**: `docs/`

## Getting Started

### Prerequisites
- Python 3.10+

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application using Uvicorn:
   ```bash
   uvicorn aether.main:app --reload --app-dir src
   ```

3. Open your browser and navigate to `http://127.0.0.1:8000` to view the **AETHER 2.0 Dashboard**.
