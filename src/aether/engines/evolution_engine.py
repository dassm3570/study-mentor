import logging
from typing import Dict, Any, List, Optional
from aether.core.interfaces import SharedMemoryInterface

logger = logging.getLogger("aether.engines.evolution_engine")

class EvolutionEngine:
    """
    Continuously improves AETHER by learning user preferences, workflow patterns,
    successful strategies, and feedback.
    Updates Shared Memory responsibly while preserving user control and project integrity
    by staging high-risk updates for user review.
    """
    def __init__(self, shared_memory: Optional[SharedMemoryInterface] = None):
        if shared_memory is None:
            from aether.engines.shared_memory import SharedMemory
            self.shared_memory = SharedMemory()
        else:
            self.shared_memory = shared_memory
        logger.info("EvolutionEngine initialized.")

    def evolve_system(
        self, 
        reflection_report: Dict[str, Any], 
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes performance metrics, feedback, and reflection reports to evolve
        the system. Applies low-risk improvements immediately and stages high-risk
        proposals for user confirmation.
        """
        logger.info("Running system evolution analysis...")

        applied_updates = {}
        proposed_updates = []
        learned_patterns = []

        # 1. Process User Feedback & learn preferences (Low Risk)
        if user_feedback:
            feedback_lower = user_feedback.lower()
            if "prefer" in feedback_lower or "use" in feedback_lower:
                # E.g. "I prefer dark mode" or "I prefer PostgreSQL"
                # Extract potential preference key-value pairs (mock heuristic)
                if "postgres" in feedback_lower:
                    self.shared_memory.store_preference("preferred_database", "PostgreSQL")
                    applied_updates["preferred_database"] = "PostgreSQL"
                    learned_patterns.append("Learned preference: PostgreSQL database.")
                elif "dark" in feedback_lower:
                    self.shared_memory.store_preference("theme", "dark")
                    applied_updates["theme"] = "dark"
                    learned_patterns.append("Learned preference: Dark theme.")

        # 2. Process Reflection Report recommendations
        recommendations = reflection_report.get("recommendations", [])
        for rec in recommendations:
            rec_lower = rec.lower()
            
            # Classify risk: If it suggests changing core parameters or routing, it's High Risk
            if "refine" in rec_lower or "parameter" in rec_lower or "routing" in rec_lower:
                proposal = {
                    "proposal_id": f"evo_prop_{len(proposed_updates) + 1}",
                    "description": f"Update system routing/parameters: {rec}",
                    "target_engine": "core_brain",
                    "impact": "Modifies cognitive intent routing thresholds.",
                    "risk_level": "high"
                }
                proposed_updates.append(proposal)
            else:
                # Low risk optimization - e.g. register a successful strategy
                strategy_key = "successful_strategy_" + str(len(applied_updates) + 1)
                self.shared_memory.store("learning_history", strategy_key, rec)
                applied_updates[strategy_key] = rec
                learned_patterns.append(f"Recorded successful strategy: {rec}")

        # 3. Save pending proposals to Shared Memory to preserve user control
        if proposed_updates:
            existing_proposals = self.shared_memory.retrieve("context", "pending_evolution_proposals", [])
            existing_proposals.extend(proposed_updates)
            self.shared_memory.store("context", "pending_evolution_proposals", existing_proposals)
            logger.info(f"Staged {len(proposed_updates)} high-risk evolution proposals for user review.")

        # 4. Record evolution event in history
        if applied_updates or proposed_updates:
            self.shared_memory.add_history_event(
                f"Evolved system. Applied: {len(applied_updates)} updates. Staged: {len(proposed_updates)} proposals."
            )

        return {
            "updates_applied": len(applied_updates) > 0 or len(proposed_updates) > 0,
            "applied_updates": applied_updates,
            "proposed_updates": proposed_updates,
            "learned_patterns": learned_patterns
        }

    def approve_proposal(self, proposal_id: str) -> bool:
        """Allows the user to explicitly approve and apply a staged high-risk proposal."""
        proposals = self.shared_memory.retrieve("context", "pending_evolution_proposals", [])
        target_proposal = None
        
        for prop in proposals:
            if prop["proposal_id"] == proposal_id:
                target_proposal = prop
                break

        if not target_proposal:
            logger.warning(f"Evolution proposal '{proposal_id}' not found.")
            return False

        # Apply the proposal (mock action applying to system preferences/config)
        self.shared_memory.store("preferences", f"approved_{proposal_id}", {
            "applied_at": self.shared_memory.provider.retrieve("context", "dummy") or "",
            "description": target_proposal["description"]
        })

        # Remove from pending proposals list
        remaining_proposals = [p for p in proposals if p["proposal_id"] != proposal_id]
        self.shared_memory.store("context", "pending_evolution_proposals", remaining_proposals)
        
        self.shared_memory.add_history_event(f"User approved evolution proposal: {proposal_id}")
        logger.info(f"Evolution proposal '{proposal_id}' approved and applied.")
        return True

    def reject_proposal(self, proposal_id: str) -> bool:
        """Allows the user to reject a staged proposal, preserving control."""
        proposals = self.shared_memory.retrieve("context", "pending_evolution_proposals", [])
        
        # Filter out the rejected proposal
        remaining_proposals = [p for p in proposals if p["proposal_id"] != proposal_id]
        if len(remaining_proposals) == len(proposals):
            return False

        self.shared_memory.store("context", "pending_evolution_proposals", remaining_proposals)
        self.shared_memory.add_history_event(f"User rejected evolution proposal: {proposal_id}")
        logger.info(f"Evolution proposal '{proposal_id}' rejected by user.")
        return True
