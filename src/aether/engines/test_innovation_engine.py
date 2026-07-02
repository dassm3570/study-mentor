import unittest
from aether.engines.innovation_engine import InnovationEngine


class TestInnovationEngine(unittest.TestCase):
    def setUp(self):
        self.innovation_engine = InnovationEngine()

    def test_generate_innovation_package(self):
        """Verify that the engine generates all structured sections and evaluates options."""
        goal = "Build a sustainable smart food delivery service"
        package = self.innovation_engine.generate_innovation_package(goal)

        # Check industry auto-detection
        self.assertEqual(package["industry"], "FoodTech")

        # Verify all required categories exist
        self.assertTrue(len(package["product_ideas"]) > 0)
        self.assertTrue(len(package["startup_concepts"]) > 0)
        self.assertTrue(len(package["feature_ideas"]) > 0)
        self.assertTrue(len(package["research_suggestions"]) > 0)
        self.assertTrue(len(package["design_alternatives"]) > 0)
        self.assertTrue(len(package["future_improvements"]) > 0)

        # Verify evaluations and recommendations
        evals = package["evaluations"]
        self.assertIsNotNone(evals["recommended_option"])
        self.assertIsNotNone(evals["quick_win"])
        self.assertIsNotNone(evals["long_term_bet"])
        
        # Verify options are ranked by score descending
        ranked = evals["ranked_options"]
        self.assertTrue(len(ranked) >= 2)
        for i in range(len(ranked) - 1):
            self.assertTrue(ranked[i]["score"] >= ranked[i+1]["score"])

    def test_evaluate_options_ranking(self):
        """Verify the option scoring and ranking logic directly."""
        options = [
            {"type": "product", "title": "A very short title", "description": "Desc"},
            {"type": "product", "title": "A significantly longer title that will produce different metrics", "description": "Desc"}
        ]
        
        results = self.innovation_engine.evaluate_options(options)
        ranked = results["ranked_options"]
        
        self.assertEqual(len(ranked), 2)
        self.assertTrue(ranked[0]["score"] >= ranked[1]["score"])
        self.assertIn("score", ranked[0])
        self.assertIn("feasibility", ranked[0]["metrics"])


if __name__ == "__main__":
    unittest.main()
