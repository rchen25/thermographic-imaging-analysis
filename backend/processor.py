import numpy as np
import cv2

class ThermalImageProcessor:
    """
    Handles segmentation of skin from background and ROI extraction
    using raw temperature data.
    """
    
    @staticmethod
    def create_skin_mask(thermal_data, min_temp=26.0, max_temp=38.0):
        """
        Creates a binary mask where 1 is skin and 0 is background.
        Default range for human skin in room temp is ~26-38C.
        """
        mask = ((thermal_data >= min_temp) & (thermal_data <= max_temp)).astype(np.uint8) * 255
        
        # Morphological operations to clean up noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask

    @staticmethod
    def get_leg_rois(thermal_data, mask):
        """
        Identifies left and right leg ROIs, then segments them into Upper/Lower regions.
        """
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
        
        if len(contours) < 2:
            return None

        leg_data = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            m = cv2.moments(cnt)
            cx = int(m["m10"] / m["m00"])
            
            c_mask = np.zeros(mask.shape, np.uint8)
            cv2.drawContours(c_mask, [cnt], -1, 255, -1)
            
            # Vertical Split (Knee level approx at 50% height of the bounding box)
            mid_y = y + (h // 2)
            
            upper_mask = c_mask.copy()
            upper_mask[mid_y:, :] = 0
            
            lower_mask = c_mask.copy()
            lower_mask[:mid_y, :] = 0
            
            leg_data.append({
                "cx": cx,
                "upper": thermal_data[upper_mask > 0],
                "lower": thermal_data[lower_mask > 0]
            })
            
        leg_data = sorted(leg_data, key=lambda x: x["cx"])
        
        return {
            "left": {"upper": leg_data[0]["upper"], "lower": leg_data[0]["lower"]},
            "right": {"upper": leg_data[1]["upper"], "lower": leg_data[1]["lower"]}
        }

    def process_frame(self, thermal_data):
        mask = self.create_skin_mask(thermal_data)
        legs = self.get_leg_rois(thermal_data, mask)
        
        # Calculate background stats (ambient environment)
        bg_mask = cv2.bitwise_not(mask)
        bg_mean = np.mean(thermal_data[bg_mask > 0]) if np.any(bg_mask) else 0
        
        # Default stats if no legs detected
        if not legs:
            return {
                "background_mean": bg_mean,
                "overall_mean": 0,
                "relative_temp": 0,
                "max_temp": 0,
                "asymmetry": 0,
                "regions": {}
            }

        skin_pixels = thermal_data[mask > 0]
        skin_mean = np.mean(skin_pixels) if len(skin_pixels) > 0 else 0
        
        stats = {
            "background_mean": bg_mean,
            "overall_mean": skin_mean,
            "relative_temp": skin_mean - bg_mean,
            "max_temp": np.max(skin_pixels) if len(skin_pixels) > 0 else 0,
            "regions": {
                "upper": {
                    "left_mean": np.mean(legs["left"]["upper"]) if len(legs["left"]["upper"]) > 0 else 0,
                    "right_mean": np.mean(legs["right"]["upper"]) if len(legs["right"]["upper"]) > 0 else 0,
                },
                "lower": {
                    "left_mean": np.mean(legs["left"]["lower"]) if len(legs["left"]["lower"]) > 0 else 0,
                    "right_mean": np.mean(legs["right"]["lower"]) if len(legs["right"]["lower"]) > 0 else 0,
                }
            }
        }
        
        stats["regions"]["upper"]["asymmetry"] = stats["regions"]["upper"]["left_mean"] - stats["regions"]["upper"]["right_mean"]
        stats["regions"]["lower"]["asymmetry"] = stats["regions"]["lower"]["left_mean"] - stats["regions"]["lower"]["right_mean"]
        
        # Overall asymmetry is the average of regional asymmetries
        stats["asymmetry"] = (stats["regions"]["upper"]["asymmetry"] + stats["regions"]["lower"]["asymmetry"]) / 2
        return stats
