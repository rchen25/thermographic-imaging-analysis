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
        # Fix FutureWarning: Use map instead of applymap
        data = df.map(self.clean_temp_string).values
        return data

    def get_muscle_group(self, view, region):
        mapping = {
            "LEG_FRONT": {"upper": "Quadriceps", "lower": "Tibialis Anterior / Shins"},
            "LEG_BACK": {"upper": "Hamstrings / Gluteal fold", "lower": "Gastrocnemius / Soleus (Calves)"}
        }
        return mapping.get(view, {}).get(region, "Unknown")

    def get_max_asymmetry_info(self, view, regions_stats):
        if not regions_stats:
            return "Unknown", "N/A", 0.0
            
        upper_asym = abs(regions_stats.get("upper", {}).get("asymmetry", 0))
        lower_asym = abs(regions_stats.get("lower", {}).get("asymmetry", 0))
        
        if upper_asym >= lower_asym:
            return "Upper Leg", self.get_muscle_group(view, "upper"), upper_asym
        else:
            return "Lower Leg", self.get_muscle_group(view, "lower"), lower_asym

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
                baseline_stats = self.processor.process_frame(view_data["pre"])
                reg_name, muscle, val = self.get_max_asymmetry_info(view, baseline_stats["regions"])
                
                graph_result = self.graph.run(view, baseline_stats)
                
                report = {
                    "visual_summary": graph_result["interpretation"],
                    "asymmetry_report": {
                        "baseline_asymmetry": f"{abs(baseline_stats['asymmetry']):.2f}°C",
                        "hotter_side": "Left" if baseline_stats['asymmetry'] > 0 else "Right",
                        "peak_region": f"{reg_name} ({muscle})",
                        "peak_value": f"{val:.2f}°C",
                        "classification": graph_result["risk_level"] + " Risk"
                    },
                    "ambient_stats": {
                        "background_temp": f"{baseline_stats['background_mean']:.2f}°C",
                        "relative_skin_temp": f"{baseline_stats['relative_temp']:.2f}°C"
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
                
                for phase in ["post", "recovery"]:
                    if view_data[phase] is not None:
                        phase_stats = self.processor.process_frame(view_data[phase])
                        p_reg, p_muscle, p_val = self.get_max_asymmetry_info(view, phase_stats["regions"])
                        
                        asym_delta = abs(phase_stats['asymmetry']) - abs(baseline_stats['asymmetry'])
                        temp_delta = phase_stats['relative_temp'] - baseline_stats['relative_temp']
                        hot_side = "Left" if phase_stats['asymmetry'] > 0 else "Right"
                        
                        if phase == "post":
                            report["inflammation_trend"] = {
                                "asymmetry_change": f"{asym_delta:+.2f}°C",
                                "hotter_side": hot_side,
                                "peak_asymmetry_node": f"{p_reg} ({p_muscle})",
                                "relative_temp_shift": f"{temp_delta:+.2f}°C (vs ambient)",
                                "peak_intensity": f"{phase_stats['max_temp']:.1f}°C"
                            }
                        else:
                            report["recovery_delta"] = {
                                "asymmetry_recovery": f"{asym_delta:+.2f}°C",
                                "hotter_side": hot_side,
                                "peak_recovery_node": f"{p_reg} ({p_muscle})",
                                "relative_temp_recovery": f"{temp_delta:+.2f}°C (vs ambient)"
                            }

                full_report["analyses"][view] = report

        return full_report
