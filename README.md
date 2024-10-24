**Honesty** -- This is mostly written by Claude Sonnet 3.5, though I have gone in and changed a few things to suite my needs better. I would not have understood the uses of opencv enough (yet) to create this on my own. 

---
# MotionRecorder
A python program that uses the webcam to watch for motion then records it to an MP4 video

# Summary
This python program uses the webcam to watch for motion, and then records the motion to an MP4 file. It will continue to record for 3 seconds after motion is no longer detected, to see if motion might resume. (This gives a smoother video in the cases where motion *does* resume.) The current version is set to run between specified hours (as I'm trying to take video of a bird that sometimes appears near by window).

# Requirements
The program requires the module `opencv-python` OR `opencv-contrib-python` (Warning: Do not install both. You'll likely get conflict errors.)

Install using `pip3 install opencv-python` OR `pip3 install opencv-contrib-python`

# Configuration
* `camera_index`    -- which camera to use (typically 0)
* `camera_exposure` -- camera exposure to use (typically -4 for indoors, -12 or -11 for bright outdoors)
* `camera_width`    -- camera resolution width
* `camera_height`   -- camera resolution height
* `start_time`      --  time to start recording (hh,mm)
* `end_time`        -- time to stop recording (hh, mm)
  
# Sensitivity
Motion detection sensitivity seems to be based on `min_area`, which I believe is the size of area to watch for changes.

My experiments are not very conclusive yet, and this might not be the only setting that needs changed.
* 500 -- picks up branches moving gently in the breeze
* 1500 -- catches some big cloud movement
* 2000 -- maybe catches birds (the author's goal)


# Screenshot
![スクリーンショット 2024-10-24 午後4 54 26](https://github.com/user-attachments/assets/f9c29198-3eb2-45bd-b3e4-a641bc0f682f)


