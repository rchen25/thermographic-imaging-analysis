from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
import numpy as np

# Define the state of our analysis
class AnalysisState(TypedDict):
    view: str
    stats: dict
    interpretation: str
    recommendations: List[str]
    risk_level: str # Low, Medium, High

class ThermographicGraph:
    def __init__(self):
        self.workflow = StateGraph(AnalysisState)
        
        # Add Nodes
        self.workflow.add_node("interpreter", self.clinical_interpreter_node)
        self.workflow.add_node("planner", self.recovery_planner_node)
        self.workflow.add_node("risk_assessor", self.risk_assessment_node)
        
        # Set Entry Point
        self.workflow.set_entry_point("interpreter")
        
        # Define Edges
        self.workflow.add_edge("interpreter", "risk_assessor")
        self.workflow.add_edge("risk_assessor", "planner")
        self.workflow.add_edge("planner", END)
        
        self.app = self.workflow.compile()

    def clinical_interpreter_node(self, state: AnalysisState):
        """
        Mock LLM node for interpreting thermal stats.
        """
        stats = state.get("stats", {})
        asym = abs(stats.get("asymmetry", 0))
        mean = stats.get("overall_mean", 0)
        
        interpretation = f"Analysis of {state['view']} reveals a mean temperature of {mean:.1f}°C. "
        if not stats or mean == 0:
             interpretation = f"Insufficient thermal data detected in {state['view']} to perform anatomical segmentation."
        elif asym > 1.0:
            interpretation += f"Critical asymmetry of {asym:.2f}°C detected. "
        elif asym > 0.4:
            interpretation += f"Moderate asymmetry of {asym:.2f}°C detected. "
        else:
            interpretation += "Thermal distribution is within normal physiological limits. "
            
        return {"interpretation": interpretation}

    def risk_assessment_node(self, state: AnalysisState):
        """
        Logic-based or LLM-based risk classification.
        """
        stats = state.get("stats", {})
        asym = abs(stats.get("asymmetry", 0))
        max_temp = stats.get("max_temp", 0)
        
        risk = "Low"
        if not stats or max_temp == 0:
            risk = "Unknown"
        elif asym > 1.2 or max_temp > 36.5:
            risk = "High"
        elif asym > 0.6:
            risk = "Medium"
            
        return {"risk_level": risk}

    def recovery_planner_node(self, state: AnalysisState):
        """
        Generates recommendations based on the risk level.
        """
        risk = state["risk_level"]
        recommendations = []
        
        if risk == "High":
            recommendations = [
                "Immediate cessation of high-impact activity.",
                "Clinical consultation for possible tissue damage.",
                "Acute cryotherapy protocol (15 min every 2 hours)."
            ]
        elif risk == "Medium":
            recommendations = [
                "Focus on active recovery and mobility work.",
                "Contrast baths (3 min hot / 1 min cold).",
                "Reduce training volume by 30% for the next 48h."
            ]
        else:
            recommendations = [
                "Resume standard training protocol.",
                "Standard post-workout hydration and nutrition.",
                "Routine stretching focusing on major muscle groups."
            ]
            
        return {"recommendations": recommendations}

    def run(self, view: str, stats: dict):
        inputs = {"view": view, "stats": stats}
        return self.app.invoke(inputs)
