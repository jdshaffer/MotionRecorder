##################################################################################
# Use the webcam to watch for motion then record to an MP4 video
# Continues recording an extra 3 seconds (to see if motion resumes)
# Current version runs between specified hours
# (Final Version)
# 2024-10-24
#
# Requires the module opencv-python  OR  opencv-contrib-python
#    pip3 install opencv-contrib-python
#
# Be sure to change the Configuration Settings to match your needs
#
# min_area = the minimal size area (width x height) needed to trigger detection 
#   3000 = 55x55 pixels (roughly)
#   4200 = 65x65
#
# sensitivity = threshold for detecting changes between frames
#    Lower  (~10) make the detector more sensitive to small changes
#    Higher (~50) mean only more significant changes will be detected
#
# min_area and sensitivity are set near the top of the MotionDetector class
#
##################################################################################

import cv2
import numpy as np
from datetime import datetime, time
import os
import time as time_module


# Configuration Settings
camera_index = 0           # Maybe change to 1 on OSX
camera_exposure = -4       # (-4 for indoors, -12 or -11 for bright outdoors)
camera_width = 1280        # Camera resolution width
camera_height = 960        # Camera resolution height
start_time = time(12, 0)   # 12:00 PM
end_time   = time(15, 0)   #  3:00 PM


class MotionDetector:
    # Set min_area in the next line...
    def __init__(self, sensitivity=20, min_area=2000, start_time=start_time, end_time=end_time):
        self.sensitivity = sensitivity
        self.min_area = min_area
        self.start_time = start_time
        self.end_time = end_time
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=16, detectShadows=True)
        self.recording = False
        self.video_writer = None
        self.last_motion_time  = 0
        self.post_motion_delay = 3   # Number of seconds to continue recording after motion stops
        
        # Create output directory if it doesn't exist
        if not os.path.exists('recorded_motion'):
            os.makedirs('recorded_motion')

    def is_active_hours(self):
        current_time = datetime.now().time()
        return self.start_time <= current_time <= self.end_time

    def start(self, camera_source=camera_index): 
        cap = cv2.VideoCapture(camera_source)
        
        # Set camera resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)
        
        # Set camera exposure
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)           # Disable auto-exposure
        cap.set(cv2.CAP_PROP_EXPOSURE, camera_exposure)  # Set manual exposure
        
        # Get actual resolution (might be different from requested)
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera resolution: {actual_width}x{actual_height}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Create a copy for drawing
            display_frame = frame.copy()
            
            # Check if we're within active hours
            if self.is_active_hours():
                # Apply background subtraction
                fg_mask = self.background_subtractor.apply(frame)
                
                # Threshold to binary
                _, thresh = cv2.threshold(fg_mask, 244, 255, cv2.THRESH_BINARY)
                
                # Find contours
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 
                                             cv2.CHAIN_APPROX_SIMPLE)
                
                motion_detected = False
                
                # Process each contour
                for contour in contours:
                    if cv2.contourArea(contour) > self.min_area:
                        motion_detected = True
                        (x, y, w, h) = cv2.boundingRect(contour)
                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), 
                                    (0, 255, 0), 2)

                # Update last motion time if motion is detected
                if motion_detected:
                    self.last_motion_time = time_module.time()

                # Handle recording state
                if motion_detected and not self.recording:
                    self.start_recording(frame)
                elif not motion_detected and self.recording:
                    # Only stop recording if enough time has passed since last motion
                    if time_module.time() - self.last_motion_time > self.post_motion_delay:
                        self.stop_recording()
                
                if self.recording:
                    self.video_writer.write(frame)
                    # Calculate remaining delay time
                    remaining_delay = max(0, self.post_motion_delay - 
                                       (time_module.time() - self.last_motion_time))
                    if remaining_delay > 0:
                        cv2.putText(display_frame, f"Recording... ({remaining_delay:.1f}s)", 
                                  (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    else:
                        cv2.putText(display_frame, "Recording...", (10, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Display status
                status = "Motion Detected" if motion_detected else "No Motion"
            else:
                # Outside active hours
                status = "Outside Active Hours"
                # Stop recording if it was in progress
                if self.recording:
                    self.stop_recording()

            # Display current time and status
            current_time = datetime.now().strftime("%H:%M:%S")
            cv2.putText(display_frame, f"Time: {current_time}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(display_frame, f"Status: {status}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(display_frame, f"Active: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(display_frame, f"Exposure: {camera_exposure}", (10, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(display_frame, f"Resolution: {actual_width}x{actual_height}", (10, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # Show the frame
            cv2.imshow("Motion Detector", display_frame)

            # Break loop with 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup(cap)

    def start_recording(self, frame):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recorded_motion/motion_{timestamp}.mp4"
        height, width = frame.shape[:2]
        self.video_writer = cv2.VideoWriter(
            filename,
            cv2.VideoWriter_fourcc(*'mp4v'),
            20.0,
            (width, height)
        )    
        self.recording = True

    def stop_recording(self):
        if self.video_writer:
            self.video_writer.release()
        self.recording = False

    def cleanup(self, cap):
        if self.video_writer:
            self.video_writer.release()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = MotionDetector(sensitivity=20, min_area=500)
    detector.start()
    
