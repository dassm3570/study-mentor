import unittest
import asyncio
from typing import Dict, Any
from aether.core.brain import CoreBrain, WorkflowState


class MockCustomEngine:
    """A mock engine representing a dynamically integrated module."""
    def __init__(self):
        self.called = False
        self.last_arg = None

    async def execute_custom_task(self, data: str) -> Dict[str, Any]:
        self.called = True
        self.last_arg = data
        return {"status": "success", "data_processed": data.upper()}


class TestCoreBrain(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.brain = CoreBrain()
        await self.brain.startup()

    async def asyncTearDown(self):
        await self.brain.shutdown()

    def test_engine_registration(self):
        """Test that engines can be dynamically registered, retrieved, and unregistered."""
        custom_engine = MockCustomEngine()
        
        # Check initial engines
        self.assertIn("goal_manager", self.brain.registered_engines)
        self.assertIn("workspace_manager", self.brain.registered_engines)
        
        # Register new engine
        self.brain.register_engine("custom_engine", custom_engine)
        self.assertIn("custom_engine", self.brain.registered_engines)
        self.assertEqual(self.brain.get_engine("custom_engine"), custom_engine)
        
        # Check backward compatibility attribute access
        self.assertEqual(self.brain.custom_engine, custom_engine)
        
        # Unregister engine
        self.brain.unregister_engine("custom_engine")
        self.assertNotIn("custom_engine", self.brain.registered_engines)
        with self.assertRaises(AttributeError):
            _ = self.brain.custom_engine

    async def test_process_thought_default_flow(self):
        """Test a default cognitive loop where intents are matched and executed."""
        stimulus = {"value": "Please remember this and create a goal"}
        response = await self.brain.process_thought(stimulus)
        
        self.assertEqual(response["status"], "completed")
        self.assertIn("goal_management", response["intents"])
        self.assertIn("memory_access", response["intents"])
        
        # Verify engines were called
        self.assertIn("goal_manager", response["engine_responses"])
        self.assertIn("shared_memory", response["engine_responses"])

    async def test_dynamic_execution_with_custom_engine(self):
        """Test that a dynamically registered engine can be targeted in the workflow."""
        custom_engine = MockCustomEngine()
        self.brain.register_engine("custom_engine", custom_engine)
        
        # We subclass or override the intent/planning method to include our custom engine
        # simulating how a new module would hook into the planning phase.
        original_generate_plan = self.brain._generate_plan
        
        def custom_generate_plan(state: WorkflowState, text: str):
            original_generate_plan(state, text)
            if "custom" in text:
                state.add_step(
                    "custom_step", 
                    "custom_engine", 
                    "execute_custom_task", 
                    {"data": text}
                )
                
        self.brain._generate_plan = custom_generate_plan
        
        # Process thought matching custom keyword
        stimulus = {"value": "run custom workflow"}
        response = await self.brain.process_thought(stimulus)
        
        self.assertEqual(response["status"], "completed")
        self.assertTrue(custom_engine.called)
        self.assertEqual(custom_engine.last_arg, "run custom workflow")
        self.assertIn("custom_engine", response["engine_responses"])
        self.assertEqual(
            response["engine_responses"]["custom_engine"]["result"]["data_processed"], 
            "RUN CUSTOM WORKFLOW"
        )

    async def test_error_handling_and_innovation_recovery(self):
        """Test that engine failures trigger self-correction via the Innovation Engine."""
        # Register a failing mock engine
        class FailingEngine:
            def do_something(self):
                raise ValueError("Simulated Engine Failure")
                
        self.brain.register_engine("failing_engine", FailingEngine())
        
        # Force plan to include the failing engine
        def force_failing_plan(state: WorkflowState, text: str):
            state.add_step("failing_step", "failing_engine", "do_something", {})
            
        self.brain._generate_plan = force_failing_plan
        
        stimulus = {"value": "trigger failure"}
        response = await self.brain.process_thought(stimulus)
        
        # It should complete with warnings because the step failed but recovery was triggered
        self.assertEqual(response["status"], "completed_with_warnings")
        self.assertIn("failing_engine", response["errors"])
        self.assertEqual(response["errors"]["failing_engine"], "Simulated Engine Failure")
        
        # Verify that innovation recovery got triggered
        self.assertIn("innovation_recovery", response["engine_responses"])
        self.assertEqual(
            response["engine_responses"]["innovation_recovery"]["failed_step"], 
            "failing_step"
        )


if __name__ == "__main__":
    unittest.main()
