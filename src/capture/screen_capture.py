"""
Screen Capture Module - Cross-platform screen capture functionality
"""

import asyncio
import logging
import platform
from typing import Optional, Tuple
import numpy as np
from PIL import Image
import mss
import cv2

from ..config.settings import Settings

class ScreenCapture:
    """Cross-platform screen capture with chart detection"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.sct = mss.mss()
        
        # Capture region (x, y, width, height)
        self.capture_region = settings.capture_region
        self.logger.info(f"Initialized screen capture with region: {self.capture_region}")
    
    async def capture(self) -> Optional[np.ndarray]:
        """Capture screen region asynchronously"""
        try:
            # Define capture area
            monitor = {
                "top": self.capture_region[1],
                "left": self.capture_region[0],
                "width": self.capture_region[2],
                "height": self.capture_region[3]
            }
            
            # Capture screenshot
            screenshot = self.sct.grab(monitor)
            
            # Convert to numpy array
            img_array = np.array(screenshot)
            
            # Convert BGRA to RGB
            if img_array.shape[2] == 4:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2RGB)
            
            return img_array
            
        except Exception as e:
            self.logger.error(f"Screen capture failed: {e}")
            return None
    
    def set_capture_region(self, x: int, y: int, width: int, height: int):
        """Set new capture region"""
        self.capture_region = (x, y, width, height)
        self.logger.info(f"Updated capture region: {self.capture_region}")
    
    def detect_chart_boundaries(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect chart boundaries in the captured image"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find the largest rectangular contour (likely the chart)
            for contour in sorted(contours, key=cv2.contourArea, reverse=True):
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # If we found a rectangle-like shape
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    return (x, y, w, h)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Chart boundary detection failed: {e}")
            return None
    
    def extract_symbol_timeframe(self, image: np.ndarray) -> dict:
        """Extract symbol and timeframe from chart image (OCR)"""
        # This would use OCR to extract text from the chart
        # For now, return placeholder
        return {
            'symbol': 'UNKNOWN',
            'timeframe': 'UNKNOWN'
        }
    
    async def monitor_changes(self, callback):
        """Monitor for changes in the captured region"""
        previous_image = None
        
        while True:
            current_image = await self.capture()
            
            if current_image is not None and previous_image is not None:
                # Calculate difference
                diff = cv2.absdiff(current_image, previous_image)
                non_zero_count = np.count_nonzero(diff)
                
                # If significant change detected
                if non_zero_count > 1000:  # Threshold for change detection
                    await callback(current_image)
            
            previous_image = current_image
            await asyncio.sleep(1)  # Check every second
