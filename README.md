# StudyMentor

StudyMentor is a modular AI-powered learning and project-generation platform built with Python, FastAPI, and a lightweight frontend. It combines planning, memory, reflection, and generation engines to help users create structured learning experiences and software projects.

## Overview

StudyMentor is designed around a loop of:
1. Receiving a goal or mission
2. Planning the work
3. Generating artifacts, code, or content
4. Storing shared memory and progress
5. Reflecting and improving the next cycle

## Architecture at a Glance

```text
User / Mission
   |
   v
Goal Manager --> Workspace Manager --> Shared Memory
   |                  |
   v                  v
Knowledge Engine   Reflection Engine
   |                  |
   +----> Innovation Engine ---->
                 |
                 v
            Genesis / Code Generation
                 |
                 v
              Output Files / API / Frontend
```

## Core Workflow

### 1. Mission Intake
- A user or system submits a goal, request, or mission.
- The goal manager transforms it into actionable tasks.

### 2. Planning and Workspace Setup
- A workspace is created for the mission.
- Documents, notes, tasks, and generated files are organized.

### 3. Memory and Knowledge Use
- Shared memory stores important context.
- Knowledge and reflection engines help reuse prior insights.

### 4. Generation
- The system generates code, documentation, backend/frontend scaffolding, or other deliverables.
- Outputs are written into the workspace and exposed through the application.

### 5. Reflection and Evolution
- The system evaluates outputs and improves future generation cycles.
- This creates a feedback loop for more robust results over time.

## Project Structure

- src/aether/core/: core reasoning and configuration components
- src/aether/engines/: mission planning, reflection, memory, and generation engines
- src/aether/generators/: code and project scaffolding generators
- src/aether/api/: FastAPI endpoints
- src/aether/database/: persistence layer
- frontend/: simple web interface
- prompts/: prompt templates for brain and reflection workflows
- docs/: architecture and developer notes

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
uvicorn aether.main:app --reload --app-dir src
```

Then open:

```text
http://127.0.0.1:8000
```

## Development Guide

### 1. Understand the main entrypoint
The FastAPI app is launched from src/aether/main.py.

### 2. Explore the engine layer
The core behavior is implemented in:
- src/aether/engines/goal_manager.py
- src/aether/engines/workspace_manager.py
- src/aether/engines/shared_memory.py
- src/aether/engines/reflection_engine.py
- src/aether/engines/innovation_engine.py

### 3. Extend generators
New project or file generation workflows can be added in:
- src/aether/generators/

### 4. Add or update prompts
Prompt templates live in the prompts/ directory and can be tuned to improve behavior.

## Example Flow

```text
User asks: "Build a study app"
   |
   v
Goal Manager creates tasks
   |
   v
Workspace is prepared
   |
   v
Knowledge and memory are consulted
   |
   v
Code and project files are generated
   |
   v
Reflection improves the next run
```

## Notes

This repository is intended as a study and experimentation platform for building agentic workflows, memory-driven generation, and modular AI systems.

## License

This project is provided as-is for educational and experimental use.
