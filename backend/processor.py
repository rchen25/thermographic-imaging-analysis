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
        Identifies left and right leg ROIs from the skin mask.
        Returns stats for each leg specifically.
        """
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by area and take the two largest (presumably the legs)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
        
        if len(contours) < 2:
            # Fallback to simple split if segmentation fails to find two distinct legs
            h, w = thermal_data.shape
            return {
                "left": thermal_data[:, :w//2][mask[:, :w//2] > 0],
                "right": thermal_data[:, w//2:][mask[:, w//2:] > 0]
            }

        # Determine which is left and right based on centroid X position
        leg_data = []
        for cnt in contours:
            m = cv2.moments(cnt)
            if m["m00"] == 0: continue
            cx = int(m["m10"] / m["m00"])
            
            # Create a mask for just this contour
            c_mask = np.zeros(mask.shape, np.uint8)
            cv2.drawContours(c_mask, [cnt], -1, 255, -1)
            
            # Extract pixels
            pixels = thermal_data[c_mask > 0]
            leg_data.append({"cx": cx, "pixels": pixels})
            
        leg_data = sorted(leg_data, key=lambda x: x["cx"])
        
        return {
            "left": leg_data[0]["pixels"] if len(leg_data) > 0 else np.array([]),
            "right": leg_data[1]["pixels"] if len(leg_data) > 1 else np.array([])
        }

    def process_frame(self, thermal_data):
        mask = self.create_skin_mask(thermal_data)
        legs = self.get_leg_rois(thermal_data, mask)
        
        stats = {
            "overall_mean": np.mean(thermal_data[mask > 0]) if np.any(mask) else 0,
            "left_mean": np.mean(legs["left"]) if len(legs["left"]) > 0 else 0,
            "right_mean": np.mean(legs["right"]) if len(legs["right"]) > 0 else 0,
            "max_temp": np.max(thermal_data[mask > 0]) if np.any(mask) else 0
        }
        
        stats["asymmetry"] = stats["left_mean"] - stats["right_mean"]
        return stats
