import pandas as pd
import numpy as np
import os
import glob
import json
from processor import ThermalImageProcessor
from graph import ThermographicGraph

class ThermographicAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.processor = ThermalImageProcessor()
        self.graph = ThermographicGraph()

    def clean_temp_string(self, val):
        if isinstance(val, str):
            return float(val.replace('℃', '').strip())
        return float(val)

    def load_excel(self, file_path):
        df = pd.read_excel(file_path, header=None)
        data = df.applymap(self.clean_temp_string).values
        return data

    def analyze_session(self, session_id):
        session_path = os.path.join(self.data_dir, session_id)
        files = glob.glob(os.path.join(session_path, "*.xlsx"))
        
        data_map = {}
        for f in files:
            name = os.path.basename(f).replace(".xlsx", "")
            data_map[name] = self.load_excel(f)

        views = ["LEG_FRONT", "LEG_BACK"]
        full_report = {
            "session_id": session_id,
            "analyses": {}
        }

        for view in views:
            view_data = {
                "pre": data_map.get(f"PREWORKOUT_{view}"),
                "post": data_map.get(f"POSTWORKOUT_{view}"),
                "recovery": data_map.get(f"RECOVERY48HR_{view}")
            }
            
            if view_data["pre"] is not None:
                # 1. Run Advanced Vision Pipeline on Pre-workout (Baseline)
                stats = self.processor.process_frame(view_data["pre"])
                
                # 2. Run LangGraph Pipeline for interpretation
                graph_result = self.graph.run(view, stats)
                
                # Format report for UI
                report = {
                    "visual_summary": graph_result["interpretation"],
                    "asymmetry_report": {
                        "baseline_asymmetry": f"{abs(stats['asymmetry']):.2f}°C",
                        "primary_side": "Left" if stats['asymmetry'] > 0 else "Right",
                        "classification": graph_result["risk_level"] + " Risk"
                    },
                    "recovery_status": {
                        "recommendation": " | ".join(graph_result["recommendations"])
                    },
                    "images": {
                        "pre": f"/images/{session_id}/PREWORKOUT_{view}.png",
                        "post": f"/images/{session_id}/POSTWORKOUT_{view}.png",
                        "recovery": f"/images/{session_id}/RECOVERY48HR_{view}.png"
                    }
                }
                
                # Optional: Add acute trend if post exists
                if view_data["post"] is not None:
                    post_stats = self.processor.process_frame(view_data["post"])
                    report["inflammation_trend"] = {
                        "acute_response": f"Temp increased to {post_stats['overall_mean']:.1f}°C",
                        "peak_intensity": f"Peak: {post_stats['max_temp']:.1f}°C",
                        "new_asymmetries": "Stable" if abs(post_stats['asymmetry'] - stats['asymmetry']) < 0.5 else "Elevated"
                    }

                full_report["analyses"][view] = report

        return full_report
