from pydantic._internal import _internal_dataclass
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable

# Import default engines
from aether.engines.goal_manager import GoalManager
from aether.engines.workspace_manager import WorkspaceManager
from aether.engines.shared_memory import SharedMemory
from aether.engines.knowledge_engine import KnowledgeEngine
from aether.engines.innovation_engine import InnovationEngine
from aether.engines.genesis_engine import GenesisEngine
from aether.engines.reflection_engine import ReflectionEngine
from aether.engines.evolution_engine import EvolutionEngine

# Import integrations
from aether.integrations import IntegrationManager

logger = logging.getLogger("aether.core.brain")


class WorkflowState:
    """
    Manages the active state, steps, and history of a cognitive workflow.
    """
    def __init__(self, stimulus: Dict[str, Any]):
        self.stimulus = stimulus
        self.intents: List[str] = []
        self.plan: List[Dict[str, Any]] = []
        self.execution_history: List[Dict[str, Any]] = []
        self.results: Dict[str, Any] = {}
        self.errors: Dict[str, Any] = {}
        self.status = "initialized"  # initialized, planning, executing, reflecting, completed, failed
        self.metadata: Dict[str, Any] = {}

    def add_step(self, step_id: str, engine_name: str, action: str, args: Dict[str, Any]):
        self.plan.append({
            "step_id": step_id,
            "engine_name": engine_name,
            "action": action,
            "args": args,
            "status": "pending",
            "result": None,
            "error": None
        })

    def update_step(self, step_id: str, status: str, result: Any = None, error: Any = None):
        for step in self.plan:
            if step["step_id"] == step_id:
                step["status"] = status
                if result is not None:
                    step["result"] = result
                if error is not None:
                    step["error"] = error
                
                # Log to execution history
                self.execution_history.append({
                    "step_id": step_id,
                    "engine_name": step["engine_name"],
                    "action": step["action"],
                    "status": status,
                })
                break


class CoreBrain:
    """
    The Core Brain of AETHER 2.0.
    Acts as the central orchestrator of the AI Operating System.
    It understands user intent, reasons about goals, creates execution plans,
    coordinates specialized modules, manages workflow state, synthesizes outputs,
    and handles errors.
    
    Designed with an extensible engine registry so new modules can be integrated
    later without changing the Core Brain interface.
    """
    def __init__(self):
        self.active = False
        self._engines: Dict[str, Any] = {}
        self.integrations = IntegrationManager()
        
        logger.info("Initializing AETHER 2.0 Core Brain...")
        self._register_default_engines()

    def _register_default_engines(self):
        """Register the core set of cognitive engines with dependency injection."""
        logger.info("Registering engines with explicit dependency injection...")
        
        shared_memory = SharedMemory()
        workspace_manager = WorkspaceManager(global_memory=shared_memory)
        goal_manager = GoalManager(workspace_manager=workspace_manager)
        knowledge_engine = KnowledgeEngine(shared_memory=shared_memory)
        innovation_engine = InnovationEngine()
        genesis_engine = GenesisEngine()
        reflection_engine = ReflectionEngine()
        evolution_engine = EvolutionEngine(shared_memory=shared_memory)

        self.register_engine("shared_memory", shared_memory)
        self.register_engine("workspace_manager", workspace_manager)
        self.register_engine("goal_manager", goal_manager)
        self.register_engine("knowledge_engine", knowledge_engine)
        self.register_engine("innovation_engine", innovation_engine)
        self.register_engine("genesis_engine", genesis_engine)
        self.register_engine("reflection_engine", reflection_engine)
        self.register_engine("evolution_engine", evolution_engine)
        logger.info("All engines registered successfully.")

    def register_engine(self, name: str, engine: Any):
        """
        Dynamically register an engine/module with the Core Brain.
        Allows future engines to be integrated without changing the Core Brain interface.
        """
        self._engines[name] = engine
        logger.info(f"Engine '{name}' successfully registered.")

    def unregister_engine(self, name: str):
        """Remove an engine from the registry."""
        if name in self._engines:
            del self._engines[name]
            logger.info(f"Engine '{name}' unregistered.")

    def get_engine(self, name: str) -> Optional[Any]:
        """Retrieve a registered engine by name."""
        return self._engines.get(name)

    @property
    def registered_engines(self) -> List[str]:
        """List all currently registered engine names."""
        return list(self._engines.keys())

    # Maintain attribute access for backward compatibility with existing endpoints
    def __getattr__(self, name: str) -> Any:
        if name in self._engines:
            return self._engines[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    async def startup(self):
        self.active = True
        logger.info("AETHER 2.0 Core Brain is ONLINE.")

    async def shutdown(self):
        self.active = False
        logger.info("AETHER 2.0 Core Brain is OFFLINE.")

    async def process_thought(self, stimulus: Dict[str, Any]) -> Dict[str, Any]:
        """
        The cognitive orchestrator loop:
        1. Understand Intent & Reason
        2. Create Execution Plan
        3. Coordinate & Execute Steps
        4. Reflect & Self-Correct
        5. Synthesize Output & Sync Memory
        """
        if not self.active:
            await self.startup()

        text = str(stimulus.get("value", "")).lower()
        logger.info(f"[CoreBrain] Starting cognitive loop for stimulus: '{text}'")

        # Initialize workflow state
        state = WorkflowState(stimulus)

        try:
            # Step 1: Understand Intent & Reason
            state.status = "planning"
            state.intents = self._classify_intents(text)
            logger.info(f"[CoreBrain] Step 1: Classified intents: {state.intents}")
            
            # Step 2: Create Execution Plan
            self._generate_plan(state, text)
            logger.info(f"[CoreBrain] Step 2: Generated plan with {len(state.plan)} steps.")
            for step in state.plan:
                logger.debug(f"  Plan Step: {step['step_id']} -> {step['engine_name']}.{step['action']}")
            
            # Step 3: Coordinate & Execute Plan
            state.status = "executing"
            logger.info("[CoreBrain] Step 3: Coordinating & executing plan steps...")
            await self._execute_plan(state)
            logger.info("[CoreBrain] Step 3: Plan execution finished.")

            # Step 4: Reflect & Self-Correct
            state.status = "reflecting"
            logger.info("[CoreBrain] Step 4: Commencing self-reflection & critique...")
            await self._reflect_and_correct(state)
            logger.info("[CoreBrain] Step 4: Reflection phase completed.")

            # Step 5: Synthesize Output
            state.status = "completed"
            logger.info("[CoreBrain] Step 5: Synthesizing final response and updating Shared Memory...")
            output = self._synthesize_output(state)
            
            # Update Shared Memory with the transaction/event
            memory = self.get_engine("shared_memory")
            if memory:
                memory.add_history_event(f"Processed thought: {text}. Status: {state.status}")
                memory.update_context({"last_thought_status": state.status})
                logger.debug("[CoreBrain] Shared Memory updated with transaction event.")

            logger.info(f"[CoreBrain] Cognitive loop completed successfully. Status: {state.status}")
            return output

        except Exception as e:
            logger.error(f"[CoreBrain] Error in Core Brain cognitive loop: {e}", exc_info=True)
            state.status = "failed"
            
            # Synthesize failure output
            return {
                "thought_process": "Cognitive loop failed during execution.",
                "status": "failed",
                "error": str(e),
                "intents": state.intents,
                "engine_responses": state.results
            }

    def _classify_intents(self, text: str) -> List[str]:
        """Classify incoming stimulus into target engine intents."""
        intents = []
        if any(w in text for w in ["goal", "plan", "todo", "task", "mission", "project"]):
            intents.append("goal_management")
        if any(w in text for w in ["file", "workspace", "dir", "folder", "run"]):
            intents.append("workspace_management")
        if any(w in text for w in ["remember", "memorize", "recall", "memory"]):
            intents.append("memory_access")
        if any(w in text for w in ["know", "search", "document", "find", "query", "summary", "notes"]):
            intents.append("knowledge_query")
        if any(w in text for w in ["creative", "brainstorm", "innovate", "strategy"]):
            intents.append("innovation_brainstorm")
        if any(w in text.lower() for w in ["create", "build", "develop", "generate", "make", "application", "app", "website", "system", "management system", "software", "project", "blueprint", "genesis", "agent", "create agent", "spawn"]):
            intents.append("agent_genesis")
        if any(w in text for w in ["reflect", "critique", "review"]):
            intents.append("self_reflection")
        if any(w in text for w in ["evolve", "optimize", "improve"]):
            intents.append("system_evolution")
        
        if not intents:
            intents.append("general_cognition")
        return intents

    def _generate_plan(self, state: WorkflowState, text: str):
        """Reason about the goal and construct a list of execution steps."""
        raw_text = str(state.stimulus.get("value", ""))
        # Dynamic planning based on detected intents
        step_counter = 1

        # If it's a genesis or project goal, we need to orchestrate multiple engines
        if "agent_genesis" in state.intents or "project" in text or "architecture" in text:
            state.add_step(
                f"step_{step_counter}", 
                "genesis_engine", 
                "generate_blueprint", 
                {"goal": raw_text}
            )
            step_counter += 1
            state.add_step(
                f"step_{step_counter}", 
                "workspace_manager", 
                "prepare_workspace", 
                {"session_id": "session-genesis"}
            )
            step_counter += 1

        # Goal management
        if "goal_management" in state.intents:
            state.add_step(
                f"step_{step_counter}", 
                "goal_manager", 
                "create_goal", 
                {"title": "Automated Goal", "description": f"Handle task: {raw_text}"}
            )
            step_counter += 1

        # Memory access
        if "memory_access" in state.intents:
            state.add_step(
                f"step_{step_counter}", 
                "shared_memory", 
                "store", 
                {"category": "context", "key": "last_stimulus", "value": raw_text}
            )
            step_counter += 1

        # Knowledge query
        if "knowledge_query" in state.intents:
            state.add_step(
                f"step_{step_counter}", 
                "knowledge_engine", 
                "query_knowledge", 
                {"query": raw_text}
            )
            step_counter += 1

        # Innovation brainstorm
        if "innovation_brainstorm" in state.intents:
            state.add_step(
                f"step_{step_counter}", 
                "innovation_engine", 
                "brainstorm", 
                {"challenge": raw_text}
            )
            step_counter += 1

        # Self-reflection
        if "self_reflection" in state.intents:
            state.add_step(
                f"step_{step_counter}", 
                "reflection_engine", 
                "analyze_performance", 
                {"execution_history": []}
            )
            step_counter += 1

        # System evolution
        if "system_evolution" in state.intents:
            state.add_step(
                f"step_{step_counter}", 
                "evolution_engine", 
                "evolve_system", 
                {"reflection_report": {}}
            )
            step_counter += 1

        # General fallbacks if no plan steps generated
        if not state.plan:
            state.add_step(
                f"step_{step_counter}", 
                "shared_memory", 
                "store", 
                {"category": "context", "key": "general_thought", "value": raw_text}
            )

    async def _execute_plan(self, state: WorkflowState):
        """Execute plan steps, handling errors and coordinating engine calls."""
        for step in state.plan:
            step_id = step["step_id"]
            engine_name = step["engine_name"]
            action = step["action"]
            args = step["args"]

            engine = self.get_engine(engine_name)
            if not engine:
                error_msg = f"Engine '{engine_name}' is not registered."
                state.update_step(step_id, "failed", error=error_msg)
                state.errors[engine_name] = error_msg
                continue

            state.update_step(step_id, "running")
            try:
                # Retrieve the method
                method = getattr(engine, action, None)
                if not method or not callable(method):
                    # Check for alternative methods or legacy naming compatibility
                    # e.g., create_goal -> create_mission
                    alt_action = self._resolve_legacy_action(engine_name, action)
                    method = getattr(engine, alt_action, None) if alt_action else None
                    
                    if not method or not callable(method):
                        raise AttributeError(f"Engine '{engine_name}' has no callable method '{action}' or '{alt_action}'")
                
                # Invoke method (handling both async and sync methods)
                if asyncio.iscoroutinefunction(method):
                    result = await method(**args)
                else:
                    result = method(**args)

                state.update_step(step_id, "completed", result=result)
                state.results[engine_name] = {
                    "action": action,
                    "result": result
                }

            except Exception as e:
                logger.warning(f"Step {step_id} failed on engine '{engine_name}': {e}")
                state.update_step(step_id, "failed", error=str(e))
                state.errors[engine_name] = str(e)
                
                # Trigger Innovation Engine for alternative strategy
                await self._handle_step_failure(state, step, e)

    def _resolve_legacy_action(self, engine_name: str, action: str) -> Optional[str]:
        """Map generic actions to legacy engine methods if needed."""
        mappings = {
            "goal_manager": {
                "create_goal": "create_mission",
                "prepare_workspace": "create_workspace"
            },
            "workspace_manager": {
                "prepare_workspace": "create_workspace"
            }
        }
        return mappings.get(engine_name, {}).get(action)

    async def _handle_step_failure(self, state: WorkflowState, step: Dict[str, Any], exception: Exception):
        """Leverage the Innovation Engine to find a workaround if a step fails."""
        innovation = self.get_engine("innovation_engine")
        if innovation and step["engine_name"] != "innovation_engine":
            try:
                challenge = f"Step '{step['action']}' failed on engine '{step['engine_name']}' with error: {exception}"
                logger.info(f"Invoking Innovation Engine for fallback strategies: {challenge}")
                
                if asyncio.iscoroutinefunction(innovation.brainstorm):
                    workarounds = await innovation.brainstorm(challenge=challenge)
                else:
                    workarounds = innovation.brainstorm(challenge=challenge)
                
                state.results["innovation_recovery"] = {
                    "failed_step": step["step_id"],
                    "workarounds": workarounds
                }
            except Exception as ie:
                logger.error(f"Failed to run innovation recovery: {ie}")

    async def _reflect_and_correct(self, state: WorkflowState):
        """Pass the execution history to the ReflectionEngine to evaluate outcomes."""
        reflection = self.get_engine("reflection_engine")
        if reflection:
            try:
                # Prepare execution summary for critique
                history_summary = [
                    {
                        "step_id": s["step_id"],
                        "engine": s["engine_name"],
                        "action": s["action"],
                        "status": s["status"],
                        "has_error": s["error"] is not None
                    }
                    for s in state.plan
                ]
                
                if asyncio.iscoroutinefunction(reflection.analyze_performance):
                    report = await reflection.analyze_performance(execution_history=history_summary)
                else:
                    report = reflection.analyze_performance(execution_history=history_summary)
                
                state.results["reflection_engine"] = {
                    "action": "analyze_performance",
                    "result": report
                }

                # If reflection suggests optimization, trigger Evolution Engine
                if report.get("rating") != "optimal":
                    evolution = self.get_engine("evolution_engine")
                    if evolution:
                        if asyncio.iscoroutinefunction(evolution.evolve_system):
                            evo_res = await evolution.evolve_system(reflection_report=report)
                        else:
                            evo_res = evolution.evolve_system(reflection_report=report)
                        state.results["evolution_engine"] = {
                            "action": "evolve_system",
                            "result": evo_res
                        }

            except Exception as re:
                logger.error(f"Error during self-reflection phase: {re}")

    def _synthesize_output(self, state: WorkflowState) -> Dict[str, Any]:
        """Synthesize final output response from all step results."""
        intents_str = ", ".join(state.intents)
        
        # Build a thought process monologue
        thought_monologue = f"Identified intents: {intents_str}. "
        if state.errors:
            thought_monologue += f"Encountered errors in: {', '.join(state.errors.keys())}. "
            if "innovation_recovery" in state.results:
                thought_monologue += "Formulated alternative recovery strategies. "
        else:
            thought_monologue += "Successfully executed all cognitive plan steps. "

        if "reflection_engine" in state.results:
            critique = state.results["reflection_engine"]["result"].get("critique", "")
            thought_monologue += f"Reflection Critique: {critique}"

        return {
            "thought_process": thought_monologue,
            "intents": state.intents,
            "engine_responses": state.results,
            "status": "completed" if not state.errors else "completed_with_warnings",
            "errors": state.errors if state.errors else None
        }
