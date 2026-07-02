import unittest
import os
import shutil
from aether.engines.evolution_engine import EvolutionEngine


class TestEvolutionEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = "data_test"
        os.makedirs(self.test_dir, exist_ok=True)
        self.evolution_engine = EvolutionEngine()
        
        # Override shared memory storage path to avoid writing to real data files
        self.evolution_engine.shared_memory.provider.storage_path = os.path.join(self.test_dir, "shared_memory_test.json")
        self.evolution_engine.shared_memory.provider.memory = self.evolution_engine.shared_memory.provider._default_memory()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_evolve_system_low_risk(self):
        """Verify that low-risk feedback and recommendations are applied immediately."""
        reflection_report = {
            "recommendations": ["Cache database queries for speed"]
        }
        user_feedback = "I prefer postgresql database"

        result = self.evolution_engine.evolve_system(reflection_report, user_feedback)
        
        self.assertTrue(result["updates_applied"])
        self.assertIn("preferred_database", result["applied_updates"])
        self.assertEqual(result["applied_updates"]["preferred_database"], "PostgreSQL")
        self.assertEqual(len(result["proposed_updates"]), 0)
        
        # Verify it was stored in Shared Memory
        self.assertEqual(self.evolution_engine.shared_memory.get_preference("preferred_database"), "PostgreSQL")

    def test_evolve_system_high_risk_staging(self):
        """Verify that high-risk recommendations are staged as proposals and not applied immediately."""
        reflection_report = {
            "recommendations": ["Refine the Core Brain routing thresholds to avoid mismatches"]
        }

        result = self.evolution_engine.evolve_system(reflection_report)
        
        self.assertTrue(result["updates_applied"])
        self.assertEqual(len(result["applied_updates"]), 0)
        self.assertEqual(len(result["proposed_updates"]), 1)
        self.assertEqual(result["proposed_updates"][0]["risk_level"], "high")

        # Verify staged in Shared Memory
        proposals = self.evolution_engine.shared_memory.retrieve("context", "pending_evolution_proposals")
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0]["proposal_id"], "evo_prop_1")

    def test_proposal_approval_and_rejection_workflow(self):
        """Verify the user lifecycle of approving or rejecting staged proposals."""
        reflection_report = {
            "recommendations": ["Refine routing thresholds"]
        }
        self.evolution_engine.evolve_system(reflection_report)

        # 1. Reject proposal
        rejected = self.evolution_engine.reject_proposal("evo_prop_1")
        self.assertTrue(rejected)
        
        # Verify list is empty
        proposals = self.evolution_engine.shared_memory.retrieve("context", "pending_evolution_proposals")
        self.assertEqual(len(proposals), 0)

        # 2. Stage another and approve it
        self.evolution_engine.evolve_system(reflection_report)
        approved = self.evolution_engine.approve_proposal("evo_prop_1")
        self.assertTrue(approved)

        # Verify applied in preferences
        pref = self.evolution_engine.shared_memory.retrieve("preferences", "approved_evo_prop_1")
        self.assertIsNotNone(pref)
        self.assertIn("Refine routing thresholds", pref["description"])

        # Verify list is empty again
        proposals = self.evolution_engine.shared_memory.retrieve("context", "pending_evolution_proposals")
        self.assertEqual(len(proposals), 0)


if __name__ == "__main__":
    unittest.main()
