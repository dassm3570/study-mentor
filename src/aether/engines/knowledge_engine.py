import logging
from typing import Dict, Any, List, Optional
from aether.core.interfaces import SharedMemoryInterface

logger = logging.getLogger("aether.engines.knowledge_engine")

class KnowledgeEngine:
    """
    Manages semantic indexing, RAG, and cognitive synthesis.
    Produces personalized learning roadmaps, study notes, quizzes, summaries,
    concept maps, prerequisite analysis, and progress tracking using Shared Memory
    to personalize recommendations.
    """
    def __init__(self, shared_memory: Optional[SharedMemoryInterface] = None):
        if shared_memory is None:
            from aether.engines.shared_memory import SharedMemory
            self.shared_memory = SharedMemory()
        else:
            self.shared_memory = shared_memory
        logger.info("KnowledgeEngine initialized.")

    async def generate_roadmap(self, topic: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Generates a personalized learning roadmap for a given topic,
        tailored using user preferences and existing skills from Shared Memory.
        """
        logger.info(f"Generating personalized learning roadmap for: {topic}")
        
        # 1. Retrieve user preferences & skills from Shared Memory to personalize
        difficulty = self.shared_memory.get_preference("difficulty_level", "Beginner")
        learning_style = self.shared_memory.get_preference("learning_style", "visual")
        existing_skills = self.shared_memory.retrieve("skills", "") or {}
        
        # Adjust phases based on difficulty
        estimated_time = "6 Weeks" if difficulty.lower() == "advanced" else "4 Weeks"
        
        # Basic personalization logic
        phases = [
            {
                "phase": 1,
                "title": f"Fundamentals of {topic}",
                "topics": [f"Introduction to {topic}", f"Core concepts of {topic}"],
                "resources": ["Visual diagrams" if learning_style == "visual" else "Hands-on tutorials"]
            },
            {
                "phase": 2,
                "title": f"Intermediate {topic}",
                "topics": [f"Standard design patterns in {topic}", f"Error handling in {topic}"],
                "resources": ["Interactive coding sandboxes"]
            }
        ]

        if difficulty.lower() == "advanced":
            phases.append({
                "phase": 3,
                "title": f"Advanced {topic}",
                "topics": [f"Performance tuning for {topic}", f"Scaling {topic} architectures"],
                "resources": ["In-depth case studies", "Whitepapers"]
            })

        # Filter out topics where user already has a registered skill
        for phase in phases:
            phase["topics"] = [t for t in phase["topics"] if t.lower() not in existing_skills]

        return {
            "topic": topic,
            "personalized_for": user_id,
            "difficulty": difficulty,
            "learning_style": learning_style,
            "estimated_time": estimated_time,
            "phases": phases
        }

    async def generate_study_notes(self, topic: str) -> str:
        """Generates comprehensive study notes for a topic."""
        logger.info(f"Generating study notes for: {topic}")
        return (
            f"# Study Notes: {topic}\n\n"
            f"## Overview\n"
            f"Essential takeaways and reference guide for **{topic}**.\n\n"
            f"## Core Concepts\n"
            f"1. **Syntax & Paradigm**: Understand the structural and execution model.\n"
            f"2. **State & Control**: Managing lifecycle and data flow.\n"
            f"3. **Testing & Performance**: How to write robust, scalable code.\n"
        )

    async def generate_quiz(self, topic: str) -> List[Dict[str, Any]]:
        """Generates a quiz to test user understanding of a topic."""
        logger.info(f"Generating quiz for: {topic}")
        return [
            {
                "question_id": 1,
                "question": f"What is the primary design philosophy of {topic}?",
                "options": ["Modularity & Decoupling", "Monolithic structure", "Manual memory management", "No abstraction"],
                "correct_option": "Modularity & Decoupling"
            },
            {
                "question_id": 2,
                "question": f"Which component in {topic} handles central coordination?",
                "options": ["Core Brain", "Shared Memory", "Workspace Manager", "API Gateway"],
                "correct_option": "Core Brain"
            }
        ]

    async def generate_summary(self, content: str) -> str:
        """Generates a concise summary of the provided text."""
        logger.info("Generating summary for provided content...")
        words = content.split()
        preview = " ".join(words[:8]) + "..." if len(words) > 8 else content
        return (
            f"### Executive Summary\n"
            f"- **Source**: {preview}\n"
            f"- **Takeaway**: Decoupled modules increase agility and speed up development."
        )

    async def generate_concept_map(self, topic: str) -> Dict[str, Any]:
        """Generates a concept map (nodes and connections) representing the topic structure."""
        logger.info(f"Generating concept map for: {topic}")
        return {
            "topic": topic,
            "nodes": [
                {"id": "A", "label": topic},
                {"id": "B", "label": "Fundamentals"},
                {"id": "C", "label": "Advanced Optimization"}
            ],
            "edges": [
                {"source": "A", "target": "B", "relationship": "has_base"},
                {"source": "A", "target": "C", "relationship": "leads_to"}
            ]
        }

    async def analyze_prerequisites(self, topic: str) -> Dict[str, Any]:
        """
        Analyzes the prerequisites for a topic and checks Shared Memory
        to determine which prerequisites the user already meets.
        """
        logger.info(f"Analyzing prerequisites for: {topic}")
        
        # Hardcoded prerequisite map for demonstration
        prereqs = ["basic_programming", "system_architecture"]
        if "ai" in topic.lower() or "brain" in topic.lower():
            prereqs.append("machine_learning")

        existing_skills = self.shared_memory.list_keys("skills")
        
        analysis = []
        all_met = True
        for p in prereqs:
            met = p in existing_skills
            if not met:
                all_met = False
            analysis.append({
                "prerequisite": p,
                "status": "met" if met else "missing"
            })

        return {
            "topic": topic,
            "all_prerequisites_met": all_met,
            "prerequisites_status": analysis
        }

    def track_learning_progress(self, topic: str, completed_subtopics: List[str]):
        """Records completed topics in the global Shared Memory learning history."""
        logger.info(f"Tracking learning progress for: {topic}")
        
        learning_record = {
            "topic": topic,
            "completed_subtopics": completed_subtopics,
            "timestamp": self.shared_memory.provider.retrieve("context", "dummy") or ""
        }
        
        # Log to shared memory learning history
        self.shared_memory.add_history_event(f"Completed subtopics {completed_subtopics} in {topic}")
        
        # Update specific learning history category
        history = self.shared_memory.retrieve("learning_history", topic) or []
        history.extend(completed_subtopics)
        # Remove duplicates
        history = list(set(history))
        self.shared_memory.store("learning_history", topic, history)
