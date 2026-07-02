import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("aether.engines.reflection_engine")

class ReflectionEngine:
    """
    Reviews completed work, checks alignment with the active mission,
    identifies missing deliverables, evaluates quality, highlights risks,
    and generates actionable recommendations before updating the Evolution Engine.
    """
    def __init__(self):
        logger.info("ReflectionEngine initialized.")

    def analyze_performance(
        self, 
        execution_history: List[Dict[str, Any]], 
        active_mission: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Reviews completed work and generates a detailed critique, risk assessment,
        and recommendations.
        """
        logger.info("Reflecting on recent execution history and mission alignment...")

        # 1. Evaluate alignment with active mission
        alignment_score = 100
        alignment_notes = "Execution perfectly aligned with the active mission."
        
        if active_mission:
            mission_title = active_mission.get("title", "")
            # Check if any step relates to the mission title keywords (basic heuristic)
            keywords = [w.lower() for w in mission_title.split()]
            matched_keywords = 0
            for step in execution_history:
                action_str = str(step.get("action", "")).lower() + " " + str(step.get("engine", "")).lower()
                if any(k in action_str for k in keywords):
                    matched_keywords += 1
            
            if len(keywords) > 0 and matched_keywords == 0:
                alignment_score = 60
                alignment_notes = f"Warning: No executed steps explicitly matched keywords from the mission title '{mission_title}'."

        # 2. Identify missing deliverables
        missing_deliverables = []
        if active_mission:
            # Check for uncompleted milestones
            for milestone in active_mission.get("milestones", []):
                if milestone.get("status") != "completed":
                    missing_deliverables.append(f"Milestone {milestone.get('id')}: {milestone.get('title')}")

        # 3. Evaluate quality & detect errors
        failed_steps = [s for s in execution_history if s.get("has_error") or s.get("status") == "failed"]
        error_count = len(failed_steps)
        total_steps = len(execution_history)
        
        quality_rating = "optimal"
        if error_count > 0:
            quality_rating = "critical_issues" if error_count == total_steps else "suboptimal"

        # 4. Highlight risks
        risks = []
        if error_count > 0:
            risks.append(f"Technical Debt: {error_count} failed step(s) in the current run.")
        if active_mission and active_mission.get("priority", 1) > 2:
            risks.append("High Priority: This is a critical mission; failures have elevated impact.")
        if len(missing_deliverables) > 2:
            risks.append("Scope Creep: Multiple milestones remain uncompleted.")

        # 5. Generate actionable recommendations
        recommendations = []
        if error_count > 0:
            recommendations.append("Invoke the Innovation Engine to seek alternative strategies for failed steps.")
        if len(missing_deliverables) > 0:
            recommendations.append("Prioritize pending milestones before executing final deployment tasks.")
        if alignment_score < 80:
            recommendations.append("Refine the Core Brain intent classification mapping to improve mission routing.")

        return {
            "rating": quality_rating,
            "alignment": {
                "score": alignment_score,
                "notes": alignment_notes
            },
            "missing_deliverables": missing_deliverables,
            "quality_assessment": {
                "total_steps": total_steps,
                "failed_steps": len(failed_steps),
                "error_rate": f"{round((error_count / total_steps) * 100, 2)}%" if total_steps > 0 else "0%"
            },
            "risks": risks,
            "recommendations": recommendations
        }
