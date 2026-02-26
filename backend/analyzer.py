import pandas as pd
import numpy as np
import os
import glob
import json

class ThermographicAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.results = {}

    def clean_temp_string(self, val):
        if isinstance(val, str):
            return float(val.replace('℃', '').strip())
        return float(val)

    def load_excel(self, file_path):
        df = pd.read_excel(file_path, header=None)
        # Apply cleaning to all elements
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
                report = self.generate_agent_report(view, view_data)
                # Add image URLs
                report["images"] = {
                    "pre": f"http://localhost:8000/images/{session_id}/PREWORKOUT_{view}.png",
                    "post": f"http://localhost:8000/images/{session_id}/POSTWORKOUT_{view}.png",
                    "recovery": f"http://localhost:8000/images/{session_id}/RECOVERY48HR_{view}.png"
                }
                full_report["analyses"][view] = report

        return full_report

    def generate_agent_report(self, view, data):
        pre = data["pre"]
        post = data["post"]
        recovery = data["recovery"]

        report = {}

        # 1. Baseline Assessment
        mid = pre.shape[1] // 2
        l_pre, r_pre = pre[:, :mid], pre[:, mid:]
        avg_l_pre, avg_r_pre = np.mean(l_pre), np.mean(r_pre)
        asym_pre = avg_l_pre - avg_r_pre
        
        report["visual_summary"] = f"Initial thermographic scan of {view} shows a mean temperature of {np.mean(pre):.2f}°C. "
        if abs(asym_pre) > 0.5:
            report["visual_summary"] += f"Significant baseline heat concentration detected in the {'left' if asym_pre > 0 else 'right'} side."
        else:
            report["visual_summary"] += "Heat distribution is relatively uniform across both limbs."

        report["asymmetry_report"] = {
            "baseline_asymmetry": f"{abs(asym_pre):.2f}°C deviation",
            "primary_side": "Left" if asym_pre > 0 else "Right",
            "classification": "Pathological" if abs(asym_pre) > 1.2 else ("Subtle" if abs(asym_pre) > 0.3 else "Negligible")
        }

        # 2. Immediate Response
        if post is not None:
            diff_post = post - pre
            max_inc = np.max(diff_post)
            avg_inc = np.mean(diff_post)
            l_post, r_post = post[:, :mid], post[:, mid:]
            asym_post = np.mean(l_post) - np.mean(r_post)
            
            report["inflammation_trend"] = {
                "acute_response": f"Mean temperature increased by {avg_inc:.2f}°C post-workout.",
                "peak_intensity": f"Maximum localized increase of {max_inc:.2f}°C detected.",
                "new_asymmetries": "Observed" if abs(asym_post - asym_pre) > 0.5 else "Stable"
            }

        # 3. Recovery Evaluation
        if recovery is not None:
            diff_rec = recovery - pre
            avg_rec_delta = np.mean(diff_rec)
            recovery_pct = (1 - (avg_rec_delta / avg_inc)) * 100 if 'avg_inc' in locals() and avg_inc != 0 else 0
            
            report["recovery_status"] = {
                "recovery_percentage": f"{recovery_pct:.1f}%",
                "lingering_hotspots": "Present" if np.max(diff_rec) > 1.5 else "Resolved",
                "recommendation": self.get_recommendation(recovery_pct, np.max(diff_rec))
            }

        return report

    def get_recommendation(self, recovery_pct, max_lingering):
        if recovery_pct < 50 or max_lingering > 2.0:
            return "High Risk: Implement immediate cryotherapy and 24hr complete rest. Possible localized strain."
        elif recovery_pct < 80:
            return "Moderate: Targeted active recovery (swimming/cycling) and contrast baths recommended."
        else:
            return "Optimal: Recovery on track. Resume standard training intensity."

if __name__ == "__main__":
    analyzer = ThermographicAnalyzer("images")
    report = analyzer.analyze_session("001")
    print(json.dumps(report, indent=2))
    with open("report.json", "w") as f:
        json.dump(report, f, indent=2)
