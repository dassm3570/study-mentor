import logging
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger("aether.engines.innovation_engine")

class InnovationEngine:
    """
    Formulates novel problem-solving strategies, explores alternative solutions,
    and handles creative tasks. Generates product ideas, startup concepts,
    feature suggestions, research directions, design alternatives, and future improvements.
    
    Evaluates multiple options and returns structured recommendations rather than a single idea.
    """
    def __init__(self):
        logger.info("InnovationEngine initialized.")

    def brainstorm(self, challenge: str) -> list[str]:
        logger.info(f"Brainstorming solutions for: {challenge}")
        package = self.generate_innovation_package(challenge)
        return [idea["title"] for idea in package["product_ideas"]]

    def generate_innovation_package(self, goal: str, industry: str = None, focus_area: str = None) -> Dict[str, Any]:
        logger.info(f"Generating innovation package for goal: '{goal}' | Industry: {industry} | Focus: {focus_area}")
        
        goal_lower = goal.lower()
        
        # 1. Detect Domain/Industry
        detected_industry = industry or "General Technology"
        if not industry:
            if any(w in goal_lower for w in ["food", "delivery", "restaurant", "eat", "meal"]):
                detected_industry = "FoodTech"
            elif any(w in goal_lower for w in ["health", "medical", "fit", "doctor", "patient", "wellness", "therapy"]):
                detected_industry = "HealthTech"
            elif any(w in goal_lower for w in ["learn", "school", "teach", "edu", "student", "course", "study"]):
                detected_industry = "EdTech"
            elif any(w in goal_lower for w in ["finance", "money", "pay", "bank", "crypto", "blockchain", "wallet", "lend"]):
                detected_industry = "FinTech"
            elif any(w in goal_lower for w in ["green", "sustain", "environment", "eco", "climate", "carbon", "recycle"]):
                detected_industry = "CleanTech"
            elif any(w in goal_lower for w in ["social", "chat", "community", "friend", "network", "share", "connect"]):
                detected_industry = "SocialTech"
            elif any(w in goal_lower for w in ["ai", "ml", "intelligence", "agent", "llm", "deep", "model"]):
                detected_industry = "Artificial Intelligence"
            elif any(w in goal_lower for w in ["work", "remote", "team", "manage", "collaborate", "office", "task"]):
                detected_industry = "SaaS & Productivity"

        detected_focus = focus_area or "Innovation & Growth"
        if not focus_area:
            if "sustain" in goal_lower or "eco" in goal_lower or "green" in goal_lower:
                detected_focus = "Sustainability"
            elif "ai" in goal_lower or "smart" in goal_lower or "auto" in goal_lower:
                detected_focus = "Automation & Intelligence"
            elif "decentral" in goal_lower or "crypto" in goal_lower or "web3" in goal_lower:
                detected_focus = "Decentralization"
            elif "remote" in goal_lower or "collaborate" in goal_lower:
                detected_focus = "User Collaboration"

        # 2. Generate Options
        products = self._get_products(goal, detected_industry, detected_focus)
        startups = self._get_startup_concepts(goal, detected_industry)
        features = self._get_features(goal, detected_industry, detected_focus)
        research = self._get_research(goal, detected_industry, detected_focus)
        designs = self._get_design_alternatives(goal)
        improvements = self._get_future_improvements(goal)

        # 3. Evaluate Options (Products & Startups combined)
        options_to_evaluate = []
        for p in products:
            options_to_evaluate.append({"type": "product", "title": p["title"], "description": p["description"]})
        for s in startups:
            options_to_evaluate.append({"type": "startup", "title": s["title"], "description": s["description"]})

        evaluation_results = self.evaluate_options(options_to_evaluate)

        return {
            "goal": goal,
            "industry": detected_industry,
            "focus_area": detected_focus,
            "product_ideas": products,
            "startup_concepts": startups,
            "feature_ideas": features,
            "research_suggestions": research,
            "design_alternatives": designs,
            "future_improvements": improvements,
            "evaluations": evaluation_results
        }

    def evaluate_options(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates multiple options based on Feasibility, Impact, Cost, and Risk.
        Scores each dimension from 1-10 and ranks the options.
        """
        evaluated_options = []
        
        for option in options:
            title = option["title"]
            # Mock scoring algorithm based on string hashes/heuristics for predictable outputs
            title_len = len(title)
            
            feasibility = 5 + (title_len % 5)  # 5 to 9
            impact = 4 + ((title_len * 2) % 6)  # 4 to 9
            cost = 3 + ((title_len * 3) % 7)      # 3 to 9 (lower is better, but here we score it)
            risk = 2 + ((title_len * 4) % 6)      # 2 to 7 (lower is better)

            # Score formula: (Feasibility * 0.3) + (Impact * 0.4) - (Cost * 0.15) - (Risk * 0.15)
            # Re-scale Cost & Risk so higher is better for the formula (10 - score)
            score = round(
                (feasibility * 0.35) + 
                (impact * 0.35) + 
                ((10 - cost) * 0.15) + 
                ((10 - risk) * 0.15), 
                2
            )

            evaluated_options.append({
                "title": title,
                "type": option["type"],
                "description": option["description"],
                "metrics": {
                    "feasibility": feasibility,
                    "impact": impact,
                    "cost": cost,
                    "risk": risk
                },
                "score": score
            })

        # Rank options by score descending
        evaluated_options.sort(key=lambda x: x["score"], reverse=True)

        recommendations = {
            "ranked_options": evaluated_options,
            "recommended_option": evaluated_options[0] if evaluated_options else None,
            "quick_win": next((o for o in evaluated_options if o["metrics"]["feasibility"] >= 8 and o["metrics"]["cost"] <= 5), None),
            "long_term_bet": next((o for o in evaluated_options if o["metrics"]["impact"] >= 8 and o["metrics"]["feasibility"] < 7), None)
        }

        # Fallback if no matching quick win / long term bet found
        if not recommendations["quick_win"] and len(evaluated_options) > 1:
            recommendations["quick_win"] = evaluated_options[1]
        if not recommendations["long_term_bet"] and len(evaluated_options) > 0:
            recommendations["long_term_bet"] = evaluated_options[-1]

        return recommendations

    def _get_products(self, goal: str, industry: str, focus: str) -> List[Dict[str, Any]]:
        # Pre-defined templates for industries
        templates = {
            "FoodTech": [
                {
                    "title": "EcoBite Marketplace",
                    "description": f"Connecting local zero-waste food suppliers directly with eco-conscious consumers for: {goal}.",
                    "tech_stack": "React Native, FastAPI, PostgreSQL"
                },
                {
                    "title": "NutriRoute Planner",
                    "description": f"AI-driven meal planning and delivery service to achieve: {goal}.",
                    "tech_stack": "Flutter, Python, MongoDB"
                }
            ],
            "HealthTech": [
                {
                    "title": "AetherCare Companion",
                    "description": f"AI companion offering personalized mental health exercises to support: {goal}.",
                    "tech_stack": "Next.js, FastAPI, Llama-3"
                }
            ],
            "Artificial Intelligence": [
                {
                    "title": "Aether Agent Swarm",
                    "description": f"An orchestration platform that spawns autonomous agent swarms to achieve: {goal}.",
                    "tech_stack": "Python, CrewAI, LangGraph"
                }
            ]
        }
        return templates.get(industry, [
            {
                "title": f"Aether {focus} Platform",
                "description": f"A modular enterprise platform to solve: {goal}.",
                "tech_stack": "Next.js, FastAPI, PostgreSQL"
            }
        ])

    def _get_startup_concepts(self, goal: str, industry: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"{industry.replace(' ', '')} Go-To-Market",
                "description": f"A venture-backed business model offering automated B2B services solving: {goal}.",
                "revenue_model": "Usage-based APIs and enterprise licensing",
                "target_market": "Early-stage startups and SMEs"
            },
            {
                "title": "Decentralized Action Network",
                "description": f"A community-driven DAO built to incentivize public coordination around: {goal}.",
                "revenue_model": "Protocol transaction fees and treasury yield",
                "target_market": "Open-source developers and web3 communities"
            }
        ]

    def _get_features(self, goal: str, industry: str, focus: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Dynamic Goal Decomposer",
                "description": f"Breaks down '{goal}' into atomic sub-tasks.",
                "impact": "High",
                "complexity": "Medium"
            },
            {
                "title": "Context-Aware Smart Prompter",
                "description": f"Suggestions panel based on semantic similarity to help with: {goal}.",
                "impact": "High",
                "complexity": "High"
            }
        ]

    def _get_research(self, goal: str, industry: str, focus: str) -> List[Dict[str, Any]]:
        return [
            {
                "topic": f"Evaluating Multi-Agent Orchestration in {industry}",
                "hypothesis": f"Multi-agent systems execute '{goal}' with 30% fewer errors.",
                "methodology": "Run 100 test iterations and compare task success rates."
            }
        ]

    def _get_design_alternatives(self, goal: str) -> List[Dict[str, Any]]:
        return [
            {
                "design_id": "alternative_1_minimalist",
                "title": "Minimalist HUD Interface",
                "description": "A dark-mode, single-page dashboard with collapsed sidebar controls, focusing attention entirely on active workflows.",
                "pros": ["Low cognitive load", "Fast render times"],
                "cons": ["Lacks discoverability for advanced tools"]
            },
            {
                "design_id": "alternative_2_conversational",
                "title": "Conversational Canvas Interface",
                "description": "An open canvas where the user interacts via an AI chat thread, and code/diagrams appear as interactive nodes.",
                "pros": ["Highly natural interaction", "Flexible layout"],
                "cons": ["Requires higher screen real estate", "Higher latency"]
            }
        ]

    def _get_future_improvements(self, goal: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Self-Repairing Workspaces",
                "description": "Integrate the Reflection Engine directly with the file writer to automatically patch syntax errors without user intervention.",
                "timeline": "Phase 2"
            },
            {
                "title": "Predictive Resource Allocation",
                "description": "Analyze history logs to pre-fetch documents and cache API responses before the user requests them.",
                "timeline": "Phase 3"
            }
        ]
